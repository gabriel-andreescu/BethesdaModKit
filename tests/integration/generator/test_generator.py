import json

import pytest
import yaml
from copier import run_copy
from tests.support import ROOT, archive_files, deployment_config, run


def generate(destination, **answers):
    run_copy(
        str(ROOT),
        destination,
        vcs_ref="HEAD",
        data={"bmk_repository": ROOT.as_posix(), **answers},
        defaults=True,
        quiet=True,
    )


@pytest.mark.parametrize("game", ["skyrim", "fallout4"])
def test_component_layout(tmp_path, game):
    generate(
        tmp_path,
        game=game,
        components=[
            "native",
            "papyrus",
            "interface",
            "plugin_generation",
            "plugin_patching",
        ],
        native_settings=True,
        mcm=True,
        clib_util=False,
    )
    assert {
        p.relative_to(tmp_path).as_posix() for p in (tmp_path / "src").rglob("*.csproj")
    } == {
        "src/mutagen/MyMod/MyMod.csproj",
        "src/synthesis/MyModPatch/MyModPatch.csproj",
    }
    native = (tmp_path / "xmake.lua").read_text()
    assert f"@addon/bmk/{game}.plugin" in native
    assert "$(projectdir)/src/native/**.cpp" in native
    assert (tmp_path / "src/native/Plugin.cpp").is_file()
    assert (tmp_path / "src/papyrus/MyMod.psc").is_file()
    script = "frame_1/DoAction.as" if game == "skyrim" else ".gitkeep"
    assert (tmp_path / "src/interface/actionscript" / script).is_file()
    assert (tmp_path / "MyMod.slnx").is_file()
    assert (tmp_path / ".clangd").is_file()
    assert (tmp_path / "src/native/Settings.cpp").is_file()
    assert (tmp_path / "src/papyrus/mcm/MyModMCM.psc").is_file()
    assert (tmp_path / "src/mutagen/MyMod/Mcm.cs").is_file()
    assert (tmp_path / "src/mutagen/MyMod/FormIDs.txt").read_bytes() == b""
    assert (tmp_path / "assets/MCM/Config/MyMod/settings.ini").is_file()
    assert (tmp_path / "assets/optional/mcm/MCM/Config/MyMod/config.json").is_file()
    assert (
        'add_packages("'
        + ("commonlibsse-ng" if game == "skyrim" else "commonlibf4")
        + '", "clib-util", "bmk")'
        in native
    )


def test_native_source_choice(tmp_path):
    generate(
        tmp_path,
        project_name="My-Mod",
        components=["native", "papyrus"],
        native_source="code",
        native_settings=True,
    )
    assert (tmp_path / "code/Plugin.cpp").is_file()
    assert (tmp_path / "assets/MCM/Config/My-Mod/settings.ini").is_file()
    assert "$(projectdir)/code/**.cpp" in (tmp_path / "xmake.lua").read_text()
    answers = yaml.safe_load((tmp_path / ".copier-answers.yml").read_text())
    assert answers["native_source"] == "code"
    assert (
        tmp_path / "src/papyrus/My_Mod.psc"
    ).read_text().strip() == "Scriptname My_Mod Hidden"


def test_asset_package(tmp_path, bmk_addon):
    project = tmp_path / "project"
    destination = tmp_path / "deployed"
    generate(project, deploy=str(destination))
    assert not (project / "src").exists()
    assert not (project / ".clangd").exists()
    answers = yaml.safe_load((project / ".copier-answers.yml").read_text())
    assert "deploy" not in answers
    (project / "assets/config.ini").write_text("configuration")
    run(project, bmk_addon, "package", "-y")
    assert archive_files(project / "build/dist/MyMod/MyMod-0.1.0.zip") == {
        "config.ini": b"configuration"
    }
    assert (destination / "config.ini").read_text() == "configuration"


def test_package_composition(tmp_path, bmk_addon):
    project = tmp_path / "project"
    generate(project)
    (project / "assets/base.txt").write_text("base")
    (project / "private.txt").write_text("private")
    (project / "output.txt").write_text("compiled")
    (project / "override.txt").write_text("override")
    (project / "xmake.lua").write_text(
        f"add_repositories({json.dumps('bmk ' + ROOT.as_posix())})\n"
        'add_addons("bmk 0.1.0")\nincludes("@addon/bmk/project")\n'
        'target("Private")\n set_kind("phony")\n set_default(false)\n add_installfiles("private.txt")\n'
        'target("Compiler")\n set_kind("phony")\n set_default(false)\n'
        ' add_deps("Private")\n add_installfiles("output.txt")\n'
        'target("Skyrim::MyMod")\n set_version("1.0.0")\n'
        ' add_rules("@addon/bmk/skyrim.package", {targets = {"Compiler"}})\n'
        ' add_installfiles("assets/(**)")\n'
        'target("Fallout4::MyMod")\n set_version("2.0.0")\n'
        ' add_rules("@addon/bmk/fallout4.package", {targets = {"Compiler"}})\n'
        ' add_installfiles("override.txt", {filename = "output.txt"})\n'
    )
    deployment_config(project, {"Skyrim::MyMod": [str(tmp_path / "deployed")]})
    run(project, bmk_addon, "package", "-y")
    assert archive_files(project / "build/dist/Skyrim/MyMod/MyMod-1.0.0.zip") == {
        "base.txt": b"base",
        "output.txt": b"compiled",
    }
    assert archive_files(project / "build/dist/Fallout4/MyMod/MyMod-2.0.0.zip") == {
        "output.txt": b"override"
    }
    assert not (tmp_path / "deployed/private.txt").exists()
