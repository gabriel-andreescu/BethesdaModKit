import json
import subprocess

import pytest
from tests.support import archive_files, locked_file, run


def planned_files(path):
    return json.loads(path.read_text())


def test_empty_payload_produces_no_package(module_project, module_command):
    project = module_project()
    nested = project / "payload/nested"
    nested.mkdir()
    (nested / ".gitkeep").touch()
    run(project, *module_command("package"))
    assert not list(project.glob("build/dist/**/*.zip"))


def test_package_contents_omit_placeholders(module_project, module_command):
    project = module_project()
    textures = project / "payload/textures"
    textures.mkdir()
    (textures / "fixture.txt").write_text("original")
    nested = project / "payload/nested"
    nested.mkdir()
    (nested / ".gitkeep").touch()
    nexus = {"mod_id": "7318624464804", "file_id": "7995705", "category": "main"}
    run(
        project,
        *module_command(
            "package",
            config={
                "game": "skyrim",
                "options": {"changelog": "Skyrim/CHANGELOG.md", "nexus": nexus},
            },
        ),
    )
    output = project / "build/dist/TestMod"
    expected = {
        "TestMod-0.1.0.zip": {"textures/fixture.txt": "original"},
    }
    assert {file.name for file in output.iterdir()} == expected.keys()
    for name, contents in expected.items():
        assert planned_files(output / name) == contents
    metadata = next((project / ".xmake/bmk/packages").glob("*.json"))
    assert json.loads(metadata.read_text()) == {
        "target": "TestMod",
        "name": "TestMod",
        "version": "0.1.0",
        "archive": "TestMod/TestMod-0.1.0.zip",
        "changelog": "Skyrim/CHANGELOG.md",
        "game": "skyrim",
        "nexus": nexus,
    }


def test_distribution_directory_has_separate_ownership(
    module_project, module_command, xmake
):
    project = module_project()
    (project / "payload/asset.txt").write_text("asset")
    run(project, *module_command("package"))
    destination = project / "custom/TestMod/TestMod-0.1.0.zip"
    destination.parent.mkdir(parents=True)
    destination.write_text("unowned")
    run(project, xmake, "f", "-y", "--distdir=custom")
    result = subprocess.run(
        module_command("package"),
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0 and "unowned file" in result.stdout + result.stderr
    assert destination.read_text() == "unowned"
    assert (project / "build/dist/TestMod/TestMod-0.1.0.zip").is_file()


@pytest.mark.parametrize("change", ["empty", "renamed", "version"])
def test_obsolete_packages_are_removed(module_project, module_command, change):
    project = module_project()
    asset = project / "payload/asset.txt"
    asset.write_text("main")
    run(project, *module_command("package"))
    output = project / "build/dist/TestMod"
    main_zip = output / "TestMod-0.1.0.zip"
    assert planned_files(main_zip) == {"asset.txt": "main"}
    (output / "unrelated.zip").write_bytes(b"keep")
    (project / "build/dist/unrelated.txt").write_text("keep")

    if change == "empty":
        asset.unlink()
        asset.with_name(".gitkeep").touch()
    elif change == "version":
        script = project / "xmake.lua"
        script.write_text(script.read_text().replace('"0.1.0"', '"0.2.0"'))
    options = {"package_name": "Renamed"} if change == "renamed" else {}
    run(project, *module_command("package", config={"options": options}))

    expected = {"unrelated.zip"}
    if change == "renamed":
        expected.add("Renamed-0.1.0.zip")
    elif change == "version":
        expected.add("TestMod-0.2.0.zip")
    assert {p.name for p in output.iterdir()} == expected
    assert (output / "unrelated.zip").read_bytes() == b"keep"
    assert (project / "build/dist/unrelated.txt").read_text() == "keep"
    records = list((project / ".xmake/bmk/packages").glob("*.json"))
    if change == "empty":
        assert not records
    else:
        record = json.loads(records[0].read_text())
        assert (
            record["archive"] == f"TestMod/{next(iter(expected - {'unrelated.zip'}))}"
        )
        assert "changelog" not in record


@pytest.mark.parametrize("namespaced", [False, True])
def test_game_targets_can_share_package_names(
    module_project, module_command, namespaced
):
    first = "Skyrim::MyMod" if namespaced else "MyModSkyrim"
    second = "Fallout4::MyMod" if namespaced else "MyModFallout4"
    project = module_project(first)
    options = {} if namespaced else {"package_name": "MyMod"}
    script = project / "xmake.lua"
    script.write_text(
        script.read_text()
        + f'\ntarget("{second}")\n    set_kind("phony")\n    set_version("0.1.0")\n'
    )
    for folder in ("Skyrim", "Fallout4"):
        data = project / folder / "Data"
        data.mkdir(parents=True, exist_ok=True)
        (data / "asset.txt").write_text(folder)
    for target, folder in [(first, "Skyrim"), (second, "Fallout4")]:
        run(
            project,
            *module_command(
                "package",
                target,
                f"{folder}/Data",
                config={"directory": folder, "options": options},
            ),
        )
    first_output = project / "build/dist" / first.replace("::", "/")
    second_output = project / "build/dist" / second.replace("::", "/")
    assert planned_files(first_output / "MyMod-0.1.0.zip") == {"asset.txt": "Skyrim"}
    assert planned_files(second_output / "MyMod-0.1.0.zip") == {"asset.txt": "Fallout4"}
    before = {p.name: p.read_bytes() for p in second_output.iterdir()}
    (project / "Skyrim/Data/asset.txt").unlink()
    run(
        project,
        *module_command(
            "package",
            first,
            "Skyrim/Data",
            config={"directory": "Skyrim", "options": options},
        ),
    )
    assert not list(first_output.iterdir())
    assert {p.name: p.read_bytes() for p in second_output.iterdir()} == before


def test_targets_package_independent_versions(module_project, module_command):
    project = module_project("Skyrim::MyMod")
    packages = [
        ("Skyrim::MyMod", "0.1.0", "payload"),
        (
            "Skyrim::MyMod::HighResolutionTextures",
            "1.0.0",
            "Skyrim/Optional/HighResolutionTextures",
        ),
        ("Skyrim::MyMod::AlternateConfig", "1.1.0", "Skyrim/Misc/AlternateConfig"),
    ]
    with (project / "xmake.lua").open("a") as script:
        for target, version, _ in packages[1:]:
            script.write(
                f'\ntarget("{target}")\n    set_kind("phony")\n'
                f'    set_version("{version}")\n'
            )
    for target, _, directory in packages:
        payload = project / directory
        payload.mkdir(parents=True, exist_ok=True)
        (payload / "asset.txt").write_text(target)
        run(project, *module_command("package", target, directory))
    for target, version, _ in packages:
        name = target.split("::")[-1]
        output = project / "build/dist" / target.replace("::", "/")
        assert planned_files(output / f"{name}-{version}.zip") == {"asset.txt": target}


@pytest.mark.parametrize("conflict", ["unowned", "directory"])
def test_package_conflicts_preserve_output(module_project, module_command, conflict):
    project = module_project()
    (project / "payload/asset.txt").write_text("main")
    run(project, *module_command("package"))
    output = project / "build/dist/TestMod"
    old_zip = output / "TestMod-0.1.0.zip"
    previous = old_zip.read_bytes()
    script = project / "xmake.lua"
    script.write_text(script.read_text().replace('"0.1.0"', '"0.2.0"'))
    conflict_path = output / "TestMod-0.2.0.zip"
    if conflict == "directory":
        conflict_path.mkdir()
        (conflict_path / "unrelated.txt").write_text("keep")
    else:
        conflict_path.write_bytes(b"keep")
    result = subprocess.run(
        module_command("package"),
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert old_zip.read_bytes() == previous
    if conflict == "unowned":
        assert conflict_path.read_bytes() == b"keep"
    elif conflict == "directory":
        assert (conflict_path / "unrelated.txt").read_text() == "keep"


@pytest.mark.parametrize("locked", ["source", "output"])
def test_failed_packaging_can_be_retried(module_project, module_command, locked):
    project = module_project()
    source = project / "payload/asset.txt"
    source.write_text("original")
    run(project, *module_command("package-real"))
    output = project / "build/dist/TestMod"
    old_zip = output / "TestMod-0.1.0.zip"
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    script = project / "xmake.lua"
    script.write_text(script.read_text().replace('"0.1.0"', '"0.2.0"'))
    source.write_text("updated")
    with locked_file(source if locked == "source" else old_zip):
        result = subprocess.run(
            module_command("package-real"),
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0
        if locked == "source":
            assert {p.name: p.read_bytes() for p in output.iterdir()} == before
    assert old_zip.read_bytes() == before[old_zip.name]
    run(project, *module_command("package-real"))
    assert not old_zip.exists()
    assert archive_files(output / "TestMod-0.2.0.zip") == {"asset.txt": b"updated"}
