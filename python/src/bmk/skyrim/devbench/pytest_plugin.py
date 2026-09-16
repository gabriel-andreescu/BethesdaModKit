"""Load explicitly with pytest_plugins = ['bmk.skyrim.devbench.pytest_plugin']."""

import json
import re
from functools import partial
from pathlib import Path

import pytest
import requests

from bmk.testing import wait_for

from .client import Client


def pytest_addoption(parser):
    group = parser.getgroup("devbench")
    group.addoption(
        "--game-tests",
        action="store_true",
        help="Enable tests that control a running game",
    )
    group.addoption("--devbench-url", help="HTTP address of the intended DevBench host")
    parser.addini("devbench_url", "DevBench HTTP URL", default="http://127.0.0.1:8920")
    parser.addini("devbench_command", "Launcher executable and arguments", type="args")
    parser.addini("devbench_cwd", "Launcher working directory", default="")
    parser.addini(
        "devbench_launch_timeout",
        "Launch and condition-wait timeout in seconds",
        default="120",
    )
    parser.addini("devbench_timeout", "HTTP request timeout in seconds", default="30")
    parser.addini(
        "devbench_quit_on_exit",
        "Request game exit after the test session",
        type="bool",
        default=False,
    )
    group.addoption(
        "--game-results",
        default="test-results/game",
        help="Directory for test transcripts",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "game: controls a running game and requires --game-tests"
    )
    if config.getoption("game_tests") and getattr(config.option, "numprocesses", 0):
        raise pytest.UsageError(
            "Game tests share one process. Run without pytest-xdist workers"
        )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("game_tests"):
        for item in items:
            if item.get_closest_marker("game"):
                item.add_marker(pytest.mark.skip(reason="Enable with --game-tests"))


@pytest.fixture(scope="session")
def devbench_session(request):
    if not request.config.getoption("game_tests"):
        pytest.skip("Enable with --game-tests")
    config = request.config
    url = config.getoption("devbench_url") or config.getini("devbench_url")
    with Client(url, timeout=float(config.getini("devbench_timeout"))) as client:
        command = config.getini("devbench_command")
        if command:
            client.launch(
                command,
                cwd=config.getini("devbench_cwd") or None,
                timeout=float(config.getini("devbench_launch_timeout")),
            )
        else:
            try:
                client.health()
            except (requests.ConnectionError, requests.Timeout) as error:
                pytest.fail(
                    f"Cannot connect to DevBench at {url}. Start the game with "
                    "DevBench installed, or set devbench_command to launch it. "
                    f"Connection error: {error}",
                    pytrace=False,
                )
        try:
            yield client
        finally:
            if config.getini("devbench_quit_on_exit"):
                client.quit()


@pytest.fixture(name="wait_for", scope="session")
def wait_for_fixture(pytestconfig):
    return partial(
        wait_for, timeout=float(pytestconfig.getini("devbench_launch_timeout"))
    )


@pytest.fixture
def game_artifacts(request):
    root = Path(request.config.getoption("game_results"))
    name = re.sub(r"[^a-zA-Z0-9_.-]", "_", request.node.nodeid)
    directory = root / name
    directory.mkdir(parents=True, exist_ok=True)
    return directory


@pytest.fixture
def devbench(devbench_session, game_artifacts):
    client = devbench_session
    client.transcript.clear()
    try:
        yield client
    finally:
        (game_artifacts / "transcript.json").write_text(
            json.dumps(client.transcript, indent=2), encoding="utf-8"
        )
