import json

import pytest

pytest_plugins = ["pytester"]


def test_game_suite_is_opt_in_before_connection(pytester):
    pytester.makeconftest("""
import pytest
import bmk.skyrim.devbench.pytest_plugin as plugin
pytest_plugins = ["bmk.skyrim.devbench.pytest_plugin"]
def forbidden(*args):
    raise AssertionError("Connection attempted without opt-in")
plugin.Client = forbidden
""")
    pytester.makepyfile("""
import pytest
@pytest.mark.game
def test_game(devbench):
    raise AssertionError("Game test ran without opt-in")
""")
    pytester.runpytest_subprocess("-q").assert_outcomes(skipped=1)


@pytest.mark.parametrize("launch", [False, True])
def test_failed_test_and_teardown_keep_transcript_and_close_session(pytester, launch):
    pytester.makeconftest("""
from pathlib import Path
import json
import pytest
import bmk.skyrim.devbench.pytest_plugin as plugin
pytest_plugins = ["bmk.skyrim.devbench.pytest_plugin"]
class Client:
    def __init__(self, *args, **kwargs): self.transcript = []
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
    def health(self): return {"ok": True}
    def launch(self, command, **kwargs):
        assert not Path("launch.json").exists()
        Path("launch.json").write_text(json.dumps(command))
    def quit(self):
        assert Path("second-test").exists()
        assert not Path("quit").exists()
        Path("quit").touch()
    def close(self): Path("closed").touch()
plugin.Client = Client
@pytest.fixture
def game_state(devbench):
    devbench.transcript.append({"tool": "prepare"})
    yield
    devbench.transcript.append({"tool": "restore"})
    raise RuntimeError("cleanup failed")
""")
    if launch:
        pytester.makepyprojecttoml(r"""
[tool.pytest.ini_options]
devbench_command = ['C:\Mod Manager\manager.exe', '--profile', 'Test profile']
devbench_quit_on_exit = true
""")
    pytester.makepyfile("""
from pathlib import Path

def test_game(game_state):
    assert False, "feature failed"

def test_second(devbench):
    assert not Path("quit").exists()
    assert devbench.transcript == []
    Path("second-test").touch()
""")
    result = pytester.runpytest_subprocess(
        "--game-tests",
        "--devbench-url=http://localhost:8920",
        "-q",
    )
    result.assert_outcomes(failed=1, errors=1, passed=1)
    assert (pytester.path / "closed").is_file()
    assert (pytester.path / "quit").exists() == launch
    if launch:
        assert json.loads((pytester.path / "launch.json").read_text()) == [
            r"C:\Mod Manager\manager.exe",
            "--profile",
            "Test profile",
        ]
    transcripts = list((pytester.path / "test-results/game").rglob("transcript.json"))
    assert len(transcripts) == 2
    game_transcript = next(
        path for path in transcripts if path.parent.name.endswith("test_game")
    )
    assert json.loads(game_transcript.read_text()) == [
        {"tool": "prepare"},
        {"tool": "restore"},
    ]


def test_parallel_game_workers_are_rejected(pytester):
    pytester.makeconftest("""
pytest_plugins = ["bmk.skyrim.devbench.pytest_plugin"]
def pytest_addoption(parser):
    parser.addoption("--workers", dest="numprocesses", type=int, default=0)
""")
    pytester.makepyfile("def test_game(): pass")
    result = pytester.runpytest_subprocess("--game-tests", "--workers=2", "-q")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*Run without pytest-xdist workers*"])
