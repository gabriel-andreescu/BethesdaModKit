import json
import shutil

import pytest
import yaml
from copier import run_copy, run_update
from tests.support import ROOT, VERSION, archive_files, deployment_config, run


def generate(destination, **answers):
    run_copy(
        str(ROOT),
        destination,
        vcs_ref="HEAD",
        data=answers,
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
    project = (tmp_path / "src/mutagen/MyMod/MyMod.csproj").read_text()
    if game == "skyrim":
        assert 'PackageReference Include="BethesdaModKit.Mutagen"' in project
    else:
        assert "BethesdaModKit.Mutagen" not in project
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
    generate(project, deploy=str(destination), bmk_repository=ROOT.as_posix())
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


def test_kit_release_pins(tmp_path):
    generate(tmp_path, components=["native"], native_settings=True, mcm=True)
    workflow = yaml.safe_load((tmp_path / ".github/workflows/build.yml").read_text())
    assert (
        workflow["jobs"]["build"]["uses"]
        == f"gabriel-andreescu/BethesdaModKit/.github/workflows/build.yml@v{VERSION}"
    )
    native = (tmp_path / "xmake.lua").read_text()
    assert f'add_addons("bmk {VERSION}", ' in native
    assert f'add_requires("bmk {VERSION}"' in native
    project = (tmp_path / "src/mutagen/MyMod/MyMod.csproj").read_text()
    assert f'Include="BethesdaModKit.Mutagen" Version="{VERSION}"' in project


def test_package_composition(tmp_path, bmk_addon):
    project = tmp_path / "project"
    generate(project)
    (project / "assets/base.txt").write_text("base")
    (project / "private.txt").write_text("private")
    (project / "output.txt").write_text("compiled")
    (project / "override.txt").write_text("override")
    (project / "xmake.lua").write_text(
        f"add_repositories({json.dumps('bmk ' + ROOT.as_posix())})\n"
        f'add_addons("bmk {VERSION}")\nincludes("@addon/bmk/project")\n'
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


def test_tooling_only_keeps_existing_project(tmp_path):
    existing = {
        "README.md": "# Existing project\n",
        "xmake.lua": 'set_project("Existing")\n',
        "src/Plugin.cpp": "existing source\n",
    }
    for name, contents in existing.items():
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(contents)
    generate(tmp_path, tooling_only=True, components=["native", "plugin_generation"])
    for name, contents in existing.items():
        assert (tmp_path / name).read_text() == contents
    generated = {
        path.relative_to(tmp_path).as_posix()
        for path in tmp_path.rglob("*")
        if path.is_file()
    } - existing.keys()
    assert generated == {
        ".clang-format",
        ".clang-tidy",
        ".clangd",
        ".config/dotnet-tools.json",
        ".copier-answers.yml",
        ".editorconfig",
        ".gitattributes",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".prettierignore",
        ".prettierrc.json",
        ".stylua.toml",
        ".vscode/extensions.json",
        ".vscode/settings.json",
    }


def test_tooling_update_preserves_project_hooks(tmp_path, monkeypatch):
    # Template file names plus pytest's temporary path exceed MAX_PATH on Windows runners.
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.longpaths")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")
    template = tmp_path / "template"
    template.mkdir()
    shutil.copy(ROOT / "copier.yml", template)
    shutil.copytree(ROOT / "templates", template / "templates")
    run(template, "git", "init", "-q")
    run(template, "git", "add", ".")
    commit = (
        "git",
        "-c",
        "user.name=BMK tests",
        "-c",
        "user.email=tests@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "-c",
        "core.hooksPath=NUL",
        "commit",
        "-qm",
    )
    run(template, *commit, "Template")
    consumer = tmp_path / "consumer"
    run_copy(
        str(template),
        consumer,
        vcs_ref="HEAD",
        data={"tooling_only": True, "components": ["native"]},
        defaults=True,
        quiet=True,
    )
    hooks_path = consumer / ".pre-commit-config.yaml"
    hooks = yaml.safe_load(hooks_path.read_text())
    hooks["repos"][0]["hooks"].append(
        {
            "id": "project-check",
            "name": "Project check",
            "entry": "check-project",
            "language": "system",
        }
    )
    hooks_path.write_text(yaml.safe_dump(hooks, sort_keys=False))
    (consumer / "xmake.lua").write_text('set_project("Existing")\n')
    run(consumer, "git", "init", "-q")
    run(consumer, "git", "add", ".")
    run(consumer, *commit, "Project customizations")
    editor = template / "templates/.editorconfig.jinja"
    editor.write_text(editor.read_text().replace("indent_size = 4", "indent_size = 8"))
    run(template, "git", "add", ".")
    run(template, *commit, "Update editor defaults")
    run_update(consumer, vcs_ref="HEAD", defaults=True, overwrite=True, quiet=True)
    updated_hooks = yaml.safe_load(hooks_path.read_text())
    assert updated_hooks["repos"][0]["hooks"][-1]["id"] == "project-check"
    assert "indent_size = 8" in (consumer / ".editorconfig").read_text()
    assert (consumer / "xmake.lua").read_text() == 'set_project("Existing")\n'
    assert not (consumer / "README.md").exists()
