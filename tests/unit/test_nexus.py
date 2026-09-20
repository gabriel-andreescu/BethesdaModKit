import io
import json
from pathlib import Path
from unittest.mock import patch

import yaml
from tests.support import ROOT


def step(name):
    workflow = yaml.safe_load((ROOT / ".github/workflows/nexus.yml").read_text())
    return next(
        step["run"]
        for job in workflow["jobs"].values()
        for step in job["steps"]
        if step.get("name") == name
    )


def run_step(name):
    namespace = {"__name__": "test"}
    exec(step(name), namespace)  # noqa: S102
    return namespace


def test_package_destinations_and_shared_changelogs():
    namespace = run_step("Plan Nexus publication")
    mod_id = "7318624464804"
    main = {
        "target": "Main",
        "name": "My Mod",
        "version": "1.1.0",
        "game": "skyrim",
        "archive": "Main/My Mod-1.1.0.zip",
        "nexus": {
            "mod_id": mod_id,
            "file_id": "1",
            "category": "main",
            "primary": True,
        },
    }
    optional = {
        **main,
        "target": "MCM",
        "archive": "MCM/My Mod MCM-1.1.0.zip",
        "nexus": {"mod_id": mod_id, "file_id": "2", "category": "optional"},
    }
    textures = {
        **main,
        "target": "Textures",
        "version": "2.0.0",
        "changelog": "assets/textures/CHANGELOG.md",
        "archive": "Textures/My Mod Textures-2.0.0.zip",
        "nexus": {"mod_id": mod_id, "file_id": "3", "category": "miscellaneous"},
    }
    notes = {
        "0000": {
            "version": "1.1.0",
            "path": "CHANGELOG.md",
            "html": "<h3>Fixed</h3>\n<ul><li>Settings <code>reload</code> &amp; saving.</li></ul>",
        },
        "0001": {
            "version": "2.0.0",
            "path": "assets/textures/CHANGELOG.md",
            "html": '<h3>Added</h3><ul><li>Textures for <a href="https://example.com">My Mod</a>.</li></ul>',
        },
    }
    files, changelogs = namespace["plan"](
        [main, optional, textures, {**main, "target": "Local", "nexus": None}],
        notes,
        ".",
    )
    assert {(file["file_id"], file["category"], file["primary"]) for file in files} == {
        ("1", "main", True),
        ("2", "optional", False),
        ("3", "miscellaneous", False),
    }
    assert {entry["version"]: entry["entries"] for entry in changelogs} == {
        "1.1.0": ["Fixed: Settings reload & saving."],
        "2.0.0": ["Added: Textures for My Mod (https://example.com)."],
    }


def test_retry_skips_uploaded_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    archive = Path("packages/Main/mod.zip")
    archive.parent.mkdir(parents=True)
    archive.write_bytes(b"fixture")
    output = tmp_path / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setenv("NEXUSMODS_API_KEY", "fixture")
    monkeypatch.setenv(
        "NEXUS_FILE",
        json.dumps(
            {
                "file_id": "17",
                "mod_id": "23",
                "version": "1.1.0",
                "archive": "Main/mod.zip",
                "name": "My Mod",
            }
        ),
    )
    responses = [
        {"data": {"mod_files": [{"id": "17"}]}},
        {"data": {"versions": [{"version": "1.0.0"}, {"version": "1.1.0"}]}},
    ]
    with patch(
        "urllib.request.urlopen",
        side_effect=[
            io.BytesIO(json.dumps(response).encode()) for response in responses
        ],
    ) as request:
        run_step("Check Nexus file")
    assert [call.args[0].full_url for call in request.call_args_list] == [
        "https://api.nexusmods.com/v3/mods/23/files",
        "https://api.nexusmods.com/v3/mod-files/17/versions",
    ]
    assert output.read_text().strip() == "exists=true"


def test_changelog_retry_only_posts_missing_entries(monkeypatch):
    monkeypatch.setenv("NEXUSMODS_API_KEY", "fixture")
    monkeypatch.setenv(
        "NEXUS_CHANGELOG",
        json.dumps(
            {
                "mod_id": "7318624464804",
                "page_id": "192420",
                "domain": "skyrimspecialedition",
                "version": "1.1.0",
                "entries": ["Fixed: Saving & loading.", "Added: New menu."],
            }
        ),
    )
    existing = {"1.1.0": ["Fixed: Saving &amp; loading."]}
    with patch(
        "urllib.request.urlopen",
        side_effect=[io.BytesIO(json.dumps(existing).encode()), io.BytesIO(b"{}")],
    ) as request:
        run_step("Publish Nexus changelog")
    assert json.loads(request.call_args.args[0].data) == {
        "version": "1.1.0",
        "changelog": "Added: New menu.",
    }
    existing["1.1.0"].append("Added: New menu.")
    with patch(
        "urllib.request.urlopen", return_value=io.BytesIO(json.dumps(existing).encode())
    ) as request:
        run_step("Publish Nexus changelog")
    assert request.call_count == 1
