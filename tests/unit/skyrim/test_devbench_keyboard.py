from copy import deepcopy
from unittest.mock import Mock

import pytest

from bmk.skyrim.devbench import DevBenchError, Keyboard

CAPABILITIES = {
    "contract": {"name": "devbench.input", "version": {"major": 2, "minor": 0}},
    "capabilities": {
        "keyboard": {
            "version": 1,
            "encoding": "DirectInputScanCode",
            "available": True,
            "actions": ["down", "up", "tap", "releaseAll"],
        }
    },
}


def test_hold_releases_its_owner_after_assertion_failure():
    client = Mock()
    client.call.side_effect = [
        CAPABILITIES,
        {"ok": True},
        {"released": True},
        {"failed": []},
    ]
    with (
        pytest.raises(AssertionError, match="observed failure"),
        Keyboard(client) as keyboard,
        keyboard.hold(23, max_hold_ms=8000),
    ):
        raise AssertionError("observed failure")
    sent = [call.args[1] for call in client.call.call_args_list][1:]
    assert [args["action"] for args in sent] == ["down", "up", "releaseAll"]
    assert all(args["owner"] == keyboard.owner for args in sent)
    assert sent[0]["maxHoldMs"] == 8000


def test_uncertain_down_failure_still_attempts_release():
    client = Mock()
    client.call.side_effect = [
        CAPABILITIES,
        TimeoutError("lost response"),
        {"released": True},
    ]
    keyboard = Keyboard(client)
    with pytest.raises(TimeoutError), keyboard.hold(23):
        pytest.fail("Failed down must not enter the hold body")
    assert client.call.call_args.args[1]["action"] == "up"


@pytest.mark.parametrize("change", ["version", "encoding", "available", "actions"])
def test_unsupported_keyboard_contract_never_injects(change):
    capabilities = deepcopy(CAPABILITIES)
    capabilities["capabilities"]["keyboard"][change] = {
        "version": 99,
        "encoding": "VirtualKey",
        "available": False,
        "actions": ["tap"],
    }[change]
    client = Mock()
    client.call.return_value = capabilities
    with pytest.raises(DevBenchError, match="Unsupported"):
        Keyboard(client)
    client.call.assert_called_once_with("input", {"action": "capabilities"})


def test_cleanup_failure_is_not_silenced():
    client = Mock()
    client.call.side_effect = [CAPABILITIES, {"failed": ["leftShift"]}]
    with pytest.raises(DevBenchError, match="leftShift"), Keyboard(client):
        pass


def test_unmapped_control_does_not_inject():
    client = Mock()
    client.call.return_value = CAPABILITIES
    client.papyrus.return_value = -1
    keyboard = Keyboard(client)
    with pytest.raises(DevBenchError, match="no keyboard binding"):
        keyboard.mapped_key("Left Attack/Block")
    client.papyrus.assert_called_once_with(
        "Input", "GetMappedKey", ["Left Attack/Block", 0]
    )
    client.call.assert_called_once_with("input", {"action": "capabilities"})
