import json
import subprocess
from pathlib import Path

import pytest
from tests.support import ROOT


@pytest.fixture
def module_project(tmp_path):
    def create(name="TestMod"):
        project = tmp_path / "mod"
        project.mkdir()
        (project / "payload").mkdir()
        (project / "xmake.lua").write_text(
            'option("distdir")\n'
            f'target({json.dumps(name)})\n    set_version("0.1.0")\n    set_kind("phony")\n'
        )
        return project

    return create


@pytest.fixture
def module_command(xmake):
    def command(operation, target="TestMod", payload="payload", *, config=None):
        return [
            xmake,
            "lua",
            str(ROOT / "tests/integration/packaging/run_module.lua"),
            operation,
            target,
            payload,
            json.dumps(config or {"directory": ".", "options": {}}),
        ]

    return command


@pytest.fixture
def payload_module(tmp_path, xmake):
    project = tmp_path / "archives"
    project.mkdir()
    stage = project / "Data"
    stage.mkdir()
    (project / "xmake.lua").write_text(
        'target("TestMod")\n    set_kind("phony")\n    add_installfiles("Data/(**)")\n'
    )

    def invoke(*, options=True, error=None, fail=False):
        request = project / "request.json"
        request.write_text(json.dumps({"options": options, "fail": fail}))
        completed = subprocess.run(
            [
                xmake,
                "lua",
                str(ROOT / "tests/integration/packaging/run_payload.lua"),
                str(request),
            ],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        output = completed.stdout + completed.stderr
        if error:
            assert completed.returncode != 0 and error in output, output
            return None
        assert completed.returncode == 0, output
        result = json.loads(Path(str(request) + ".result").read_text())
        if "output" in result:
            result["output"] = project / result["output"]
        return result

    return stage, invoke
