from collections import deque
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import bmk.skyrim.devbench.client as transport
from bmk.skyrim.devbench import Client, DevBenchError


@pytest.fixture
def connection(monkeypatch):
    responses = deque()
    requests = []
    event_responses = deque()
    event_requests = []
    health = {"ok": True}

    def response(value):
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: value)

    def post(url, *, json, timeout):
        requests.append(json)
        return response(responses.popleft())

    def get(url, *, timeout, params=None):
        if url.endswith("/api/events"):
            event_requests.append(params["since"])
            return response(event_responses.popleft())
        return response(health.copy())

    session = SimpleNamespace(
        get=get,
        post=post,
        close=lambda: None,
    )
    monkeypatch.setattr(transport.requests, "Session", lambda: session)
    client = Client("http://127.0.0.1:8920")
    return SimpleNamespace(
        client=client,
        responses=responses,
        requests=requests,
        event_responses=event_responses,
        event_requests=event_requests,
        health=health,
    )


def test_papyrus_preserves_types_and_transcript(connection):
    c = connection
    c.responses.append({"called": True, "returned": False})
    args = [{"form": "0x123"}, 1.5, False]
    c.client.timeout = 90
    c.client.session.post = Mock(wraps=c.client.session.post)
    assert (
        c.client.papyrus("Actor", "IsEquipped", args, "0x14", timeout_ms=60000) is False
    )
    assert c.requests[0]["args"] == args
    assert c.requests[0]["timeoutMs"] == 60000
    assert c.client.session.post.call_args.kwargs["timeout"] == 90
    assert c.client.transcript[0]["args"]["self"] == {"form": "0x14"}
    args[0]["form"] = "changed"
    assert c.client.transcript[0]["args"]["args"][0] == {"form": "0x123"}


def test_failed_calls_keep_response_and_error(connection):
    connection.responses.append({"called": False, "error": "missing function"})
    with pytest.raises(DevBenchError, match="missing function"):
        connection.client.papyrus("Actor", "Missing")
    receipt = connection.client.transcript[-1]
    assert receipt["result"]["error"] == "missing function"
    assert "missing function" in receipt["error"]


@pytest.mark.parametrize("ready", [True, False])
def test_launch_waits_for_health_and_closes_on_failure(connection, monkeypatch, ready):
    launch = Mock()
    monkeypatch.setattr(transport.subprocess, "Popen", launch)
    monkeypatch.setattr(transport.time, "sleep", Mock())
    monkeypatch.setattr(
        transport.time, "monotonic", Mock(side_effect=[0, 0, 0, 1 if ready else 120])
    )
    client = connection.client
    client.health = Mock(
        side_effect=[transport.requests.ConnectionError(), {"ok": True}]
    )
    client.session.close = Mock()
    command = ["C:/Mod Manager/manager.exe", "--profile", "Test profile", "SKSE"]

    def run():
        with client:
            return client.launch(command, cwd="C:/Mod Manager")

    if ready:
        assert run() == {"ok": True}
        assert client.health.call_count == 2
    else:
        with pytest.raises(DevBenchError, match="did not become available"):
            run()
    assert launch.call_args.args == (command,)
    assert launch.call_args.kwargs["cwd"] == "C:/Mod Manager"
    client.session.close.assert_called_once()


@pytest.mark.parametrize(
    "error", [transport.requests.HTTPError("503"), ValueError("bad JSON")]
)
def test_transport_failures_keep_evidence(connection, error):
    connection.client.session.post = Mock(side_effect=error)
    with pytest.raises(type(error), match=str(error)):
        connection.client.call("inspect", {"kind": "scene"}, record=False)
    receipt = connection.client.transcript[-1]
    assert receipt["args"] == {"kind": "scene"}
    assert receipt["error"] == str(error)


def test_http_errors_include_the_server_reason(connection):
    response = transport.requests.Response()
    response.status_code = 404
    response._content = b'{"error":"no capture provider registered"}'
    response.url = "http://127.0.0.1:8920/api/tool/capture"
    connection.client.session.post = Mock(return_value=response)
    with pytest.raises(
        transport.requests.HTTPError, match="no capture provider registered"
    ):
        connection.client.call("capture", {"kind": "auto"}, record=False, timeout=75)
    assert connection.client.session.post.call_args.kwargs["timeout"] == 75
    receipt = connection.client.transcript[-1]
    assert receipt["responseBody"] == response.text
    assert "404" in receipt["error"]


@pytest.mark.parametrize(
    "url", ["http://example.com", "https://localhost", "http://user@localhost"]
)
def test_invalid_endpoint_rejected_before_connecting(monkeypatch, url):
    session = Mock(side_effect=AssertionError("Unexpected HTTP session"))
    monkeypatch.setattr(transport.requests, "Session", session)
    with pytest.raises(ValueError, match="loopback"):
        Client(url)
    session.assert_not_called()


def test_failed_scenario_has_start_and_completed_result(connection):
    connection.responses.extend(
        [
            {"queued": True, "runId": 3},
            {
                "done": True,
                "ok": False,
                "result": {
                    "ok": False,
                    "aborted": True,
                    "stepsRun": 1,
                    "results": [
                        {
                            "index": 0,
                            "kind": "waitFor",
                            "topic": "saveGame",
                            "satisfied": False,
                            "timedOut": True,
                        }
                    ],
                },
            },
        ]
    )
    with pytest.raises(DevBenchError, match="Scenario 3 failed"):
        connection.client.scenario([{"waitFor": "saveGame", "timeoutMs": 1000}])
    assert connection.requests[0]["continueOnError"] is False
    assert len(connection.requests) == 2
    assert [r["tool"] for r in connection.client.transcript] == [
        "scenario",
        "scenario-result",
    ]
    assert connection.client.transcript[-1]["result"]["ok"] is False


def test_scenario_polls_until_completed(connection, monkeypatch):
    monkeypatch.setattr(transport.time, "sleep", Mock())
    result = {"ok": True, "stepsRun": 1}
    connection.responses.extend(
        [
            {"queued": True, "runId": 3},
            {"done": False},
            {"done": True, "ok": True, "result": result},
        ]
    )
    assert connection.client.scenario([{"wait": 1}]) == result
    assert connection.client.transcript[-1]["runId"] == 3


def test_interrupted_wait_identifies_the_pending_run(connection, monkeypatch):
    connection.responses.extend([{"queued": True, "runId": 3}, {"done": False}])
    monkeypatch.setattr(transport.time, "sleep", Mock(side_effect=KeyboardInterrupt))
    with pytest.raises(KeyboardInterrupt) as error:
        connection.client.scenario([{"wait": 1000}])
    assert "DevBench run 3" in error.value.__notes__[0]
    assert "does not cancel" in error.value.__notes__[0]
    assert connection.client.transcript[0]["result"]["runId"] == 3


def test_polling_failure_is_retained(connection):
    connection.responses.append({"ok": False, "error": "run unavailable"})
    with pytest.raises(DevBenchError, match="run unavailable") as error:
        connection.client.wait_run(99)
    assert "DevBench run 99" in error.value.__notes__[0]
    assert connection.client.transcript[-1]["args"]["runId"] == 99
    assert "run unavailable" in connection.client.transcript[-1]["error"]


@pytest.mark.parametrize(
    "action,event_name", [("save", "saveGame"), ("load", "postLoadGame")]
)
@pytest.mark.parametrize("delayed", [False, True])
def test_save_load_observes_events_after_the_operation_cursor(
    connection, monkeypatch, action, event_name, delayed
):
    c = connection
    monkeypatch.setattr(transport.time, "sleep", Mock())
    completed = {"seq": 11, "topic": "lifecycle", "data": {"event": event_name}}
    c.event_responses.append({"headSeq": 10, "events": [dict(completed, seq=10)]})
    if delayed:
        c.event_responses.append({"headSeq": 10, "events": []})
    c.event_responses.append({"headSeq": 11, "events": [completed]})
    post = c.client.session.post

    def submit(url, **kwargs):
        if url.endswith("/game"):
            assert c.event_requests == [0]
        return post(url, **kwargs)

    c.client.session.post = submit
    c.responses.append({"queued": True})
    if action == "load":
        c.responses.extend(
            [
                {"queued": True, "runId": 3},
                {"done": True, "result": {"ok": True}},
                {"cell": {"editorId": "QASmoke"}},
            ]
        )
        c.client.load("fixture", cell="QASmoke", settle_ms=250, timeout=60)
        assert c.requests[1]["steps"] == [
            {"waitUntil": "noBlockingMenu", "timeoutMs": 60000},
            {"wait": 250},
        ]
        assert c.requests[-1] == {"kind": "scene"}
    else:
        c.client.save("fixture")
    assert c.requests[0] == {"action": action, "name": "fixture"}
    assert c.event_requests == ([0, 10, 10] if delayed else [0, 10])
    receipt = next(r for r in c.client.transcript if r["tool"] == "lifecycle")
    assert receipt["result"] == completed


def test_event_poll_does_not_skip_events_beyond_the_snapshot(connection, monkeypatch):
    c = connection
    monkeypatch.setattr(transport.time, "sleep", Mock())
    c.responses.append({"queued": True})
    c.event_responses.extend(
        [
            {"headSeq": 10, "events": []},
            {"headSeq": 11, "events": []},
            {
                "headSeq": 13,
                "events": [
                    {
                        "seq": 11,
                        "topic": "menu",
                        "data": {"name": "Loading Menu", "opening": True},
                    },
                    {"seq": 12, "topic": "lifecycle", "data": {"event": "preLoadGame"}},
                ],
            },
            {
                "headSeq": 13,
                "events": [
                    {"seq": 13, "topic": "lifecycle", "data": {"event": "saveGame"}}
                ],
            },
        ]
    )
    c.client.save("fixture")
    assert c.event_requests == [0, 10, 10, 12]
    assert c.client.transcript[-1]["result"]["seq"] == 13


def test_load_timeout_does_not_proceed_to_readiness_checks(connection, monkeypatch):
    c = connection
    monkeypatch.setattr(transport.time, "monotonic", Mock(side_effect=[0, 60]))
    c.responses.append({"queued": True})
    c.event_responses.extend(
        [{"headSeq": 10, "events": []}, {"headSeq": 10, "events": []}]
    )
    with pytest.raises(DevBenchError, match="postLoadGame after load 'fixture'"):
        c.client.load("fixture", timeout=60)
    assert c.requests == [{"action": "load", "name": "fixture"}]
    assert "Timed out" in c.client.transcript[-1]["error"]


@pytest.mark.parametrize("before_submission", [True, False])
def test_load_event_request_failure_stops_the_operation(connection, before_submission):
    c = connection
    c.responses.append({"queued": True})
    c.event_responses.append({"headSeq": 10, "events": []})
    get = c.client.session.get

    def fetch(url, **kwargs):
        if url.endswith("/api/events") and (before_submission or c.requests):
            raise transport.requests.ConnectionError("connection lost")
        return get(url, **kwargs)

    c.client.session.get = fetch
    with pytest.raises(transport.requests.ConnectionError, match="connection lost"):
        c.client.load("fixture")
    assert c.requests == (
        [] if before_submission else [{"action": "load", "name": "fixture"}]
    )
    assert c.client.transcript[-1]["error"] == "connection lost"


@pytest.mark.parametrize(
    "existing", [[], [{"formId": "0xFF000001", "base": {"formId": "0x00012345"}}]]
)
def test_spawn_identifies_new_reference_without_papyrus_return(connection, existing):
    connection.responses.extend(
        [
            {"truncated": False, "refs": existing},
            {"called": True, "returned": None},
            {
                "truncated": False,
                "refs": existing
                + [{"formId": "0xFF000002", "base": {"formId": "0x00012345"}}],
            },
        ]
    )
    assert (
        connection.client.spawn(0x12345, "ACHR", persistent=True, disabled=True)
        == "0xFF000002"
    )
    assert connection.requests[1]["args"] == [{"form": "0x00012345"}, 1, True, True]


@pytest.mark.parametrize(
    "refs,truncated",
    [
        ([], False),
        ([], True),
        (
            [
                {"formId": "0xFF000001", "base": {"formId": "0x00012345"}},
                {"formId": "0xFF000002", "base": {"formId": "0x00012345"}},
            ],
            False,
        ),
    ],
)
def test_spawn_rejects_missing_truncated_or_ambiguous_observations(
    connection, refs, truncated
):
    connection.responses.extend(
        [
            {"truncated": False, "refs": []},
            {"called": True, "returned": None},
            {"truncated": truncated, "refs": refs},
        ]
    )
    with pytest.raises(DevBenchError, match="uniquely"):
        connection.client.spawn(0x12345, "REFR")


@pytest.mark.parametrize(
    "collection,index,local_id,value,expected",
    [
        ("plugins", 15, 0x9211C7, 0x0F9211C7, 0x0F9211C7),
        ("lightPlugins", 0x45, 0x800, -33269760, 0xFE045800),
    ],
)
def test_form_lookup_handles_scripted_full_and_light_forms(
    connection, collection, index, local_id, value, expected
):
    mods = {"plugins": [], "lightPlugins": []}
    mods[collection] = [{"index": index, "name": "test.esp"}]
    connection.responses.extend([mods, {"called": True, "returned": value}])
    assert connection.client.form_id(local_id, "Test.esp") == expected
    assert connection.requests[-1]["self"] == {"form": f"0x{expected:08X}"}


@pytest.mark.parametrize("value", [None, 0])
def test_form_lookup_rejects_missing_form(connection, value):
    connection.responses.extend(
        [
            {"plugins": [{"index": 1, "name": "Test.esp"}], "lightPlugins": []},
            {"called": True, "returned": value},
        ]
    )
    with pytest.raises(DevBenchError, match="Missing form"):
        connection.client.form_id(0xABC, "Test.esp")


def test_form_lookup_rejects_missing_plugin(connection):
    connection.responses.append({"plugins": [], "lightPlugins": []})
    with pytest.raises(DevBenchError, match="not loaded"):
        connection.client.form_id(0xABC, "Test.esp")


def test_light_form_lookup_rejects_id_overflow(connection):
    connection.responses.append(
        {"plugins": [], "lightPlugins": [{"index": 1, "name": "Test.esp"}]}
    )
    with pytest.raises(ValueError, match="Invalid local form ID"):
        connection.client.form_id(0x1000, "Test.esp")
