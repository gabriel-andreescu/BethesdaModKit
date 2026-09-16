import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from bmk.skyrim.devbench import cli


@pytest.mark.parametrize("failed", [False, True])
def test_scenario_options_and_failure_transcript(tmp_path, monkeypatch, failed):
    source = tmp_path / "scenario.json"
    source.write_text(
        json.dumps({"steps": [{"wait": 10}], "repeat": 3, "continueOnError": True})
    )
    output = tmp_path / "results/transcript.json"
    client = SimpleNamespace(
        scenario=Mock(side_effect=RuntimeError("step failed") if failed else None),
        transcript=[{"tool": "scenario-result", "result": {"ok": not failed}}],
        close=Mock(),
    )
    monkeypatch.setattr(cli, "Client", lambda *args, **kwargs: client)
    monkeypatch.setattr(
        "sys.argv",
        [
            "devbench-scenario",
            str(source),
            "--url",
            "http://localhost:8920",
            "--output",
            str(output),
        ],
    )
    if failed:
        with pytest.raises(RuntimeError, match="step failed"):
            cli.main()
    else:
        cli.main()
    client.scenario.assert_called_once_with(
        [{"wait": 10}], repeat=3, continue_on_error=True
    )
    client.close.assert_called_once()
    assert json.loads(output.read_text()) == client.transcript
