import hashlib
import json
import os
from pathlib import Path

import pefile
import pytest
from copier import run_copy
from tests.support import ROOT, archive_files, deployment_config, run

pytestmark = pytest.mark.skipif(
    os.environ.get("BMK_TEST_NATIVE_PLUGINS") != "1",
    reason="Set BMK_TEST_NATIVE_PLUGINS=1 to build native plugin consumers.",
)


@pytest.fixture(scope="session")
def compiler_identity(bmk_addon):
    toolchain = os.environ.get("BMK_TEST_TOOLCHAIN", "msvc")
    identity = run(
        ROOT,
        bmk_addon,
        "lua",
        "-c",
        'import("core.tool.toolchain"); import("core.base.json"); '
        f"local tc = toolchain.load({json.dumps(toolchain)}, "
        '{plat = "windows", arch = "x64"}); assert(tc:check()); '
        'print(json.encode({tc:config("vs_toolset"), tc:config("vs_sdkver")}))',
    ).stdout.splitlines()[-1]
    identity += run(ROOT, bmk_addon, "--version").stdout.splitlines()[0]
    identity += toolchain
    if toolchain == "clang-cl":
        identity += run(ROOT, "clang-cl", "--version").stdout
    return identity


@pytest.fixture
def native_xmake(monkeypatch, bmk_addon, compiler_identity, game):
    # XMake's package hash omits recipe contents and compiler versions.
    recipes = (
        ("commonlibsse-ng", "clib-util", "devbench-api")
        if game == "skyrim"
        else ("commonlibf4", "clib-util")
    )
    digest = hashlib.sha256(compiler_identity.encode())
    for name in recipes:
        for source in sorted((ROOT / "packages" / name[0] / name).rglob("*")):
            if source.is_file():
                digest.update(source.relative_to(ROOT).as_posix().encode() + b"\0")
                digest.update(source.read_bytes())
    cache = Path(os.environ["XMAKE_PKG_INSTALLDIR"]) / digest.hexdigest()[:16]
    monkeypatch.setenv("XMAKE_PKG_INSTALLDIR", str(cache))
    return bmk_addon


@pytest.mark.parametrize(
    "game,extender",
    [("skyrim", "SKSE"), ("fallout4", "F4SE")],
)
def test_plugin_package(tmp_path_factory, native_xmake, game, extender):
    project = tmp_path_factory.mktemp("plugin")
    if game == "skyrim":
        project /= "projects/native/skyrim/integrations/consumer"
    run_copy(
        str(ROOT),
        project,
        data={
            "project_name": "TestPlugin",
            "author": "Test Author",
            "description": "Plugin package test",
            "game": game,
            "components": ["native"],
            "native_settings": True,
            "devbench_api": game == "skyrim",
            "bmk_repository": ROOT.as_posix(),
        },
        defaults=True,
        quiet=True,
    )
    configuration = project / "xmake.lua"
    contents = configuration.read_text().replace(
        f'add_rules("@addon/bmk/{game}.package", {{',
        f'add_rules("@addon/bmk/{game}.package", {{package_name = "PublicName",',
    )
    assets = project / "assets/asset.txt"
    assets.write_text("asset")
    if game == "fallout4":
        assets.unlink()
    if game == "skyrim":
        contents = contents.replace(
            'add_requires("commonlibsse-ng 8.0.1", {system = false})',
            'add_requires("commonlibsse-ng 8.0.1", {system = false, configs = {'
            "skyrim_se = false, skyrim_ae = true, skyrim_vr = false, "
            "skse_xbyak = false, skse_patch_safety = false}})",
        )
        source = project / "src/Plugin.cpp"
        source.write_text(
            source.read_text().replace(
                "#include <SKSE/SKSE.h>",
                "#include <ClibUtil/string.hpp>",
            )
        )
    configuration.write_text(contents)
    toolchain = os.environ.get("BMK_TEST_TOOLCHAIN", "msvc")
    run(
        project,
        native_xmake,
        "f",
        "-y",
        f"--toolchain={toolchain}",
        "--deploy=y",
    )
    destination = project / "deployed"
    deployment_config(project, {"TestPlugin": [str(destination)]})
    run(project, native_xmake, "package", "-y")
    files = archive_files(project / "build/dist/TestPlugin/PublicName-0.1.0.zip")
    settings = "MCM/Config/TestPlugin/settings.ini"
    assert files[settings] == (project / "assets" / settings).read_bytes()
    if game == "skyrim":
        assert files["asset.txt"] == b"asset"
    else:
        assert set(files) == {
            "F4SE/Plugins/TestPlugin.dll",
            "F4SE/Plugins/TestPlugin.pdb",
            settings,
        }
    dll = files[f"{extender}/Plugins/TestPlugin.dll"]
    built = project / "build/windows/x64/releasedbg/TestPlugin.dll"
    assert dll == built.read_bytes()
    assert (
        files[f"{extender}/Plugins/TestPlugin.pdb"]
        == built.with_suffix(".pdb").read_bytes()
    )
    assert (destination / f"{extender}/Plugins/TestPlugin.dll").read_bytes() == dll
    assert (
        destination / f"{extender}/Plugins/TestPlugin.pdb"
    ).read_bytes() == built.with_suffix(".pdb").read_bytes()
    with pefile.PE(data=dll) as pe:
        exports = {symbol.name for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols}
        assert f"{extender}Plugin_Load".encode() in exports
        assert f"{extender}Plugin_Version".encode() in exports
        assert pe.FILE_HEADER.Machine == 0x8664
        strings = {
            key: value
            for group in pe.FileInfo
            for info in group
            if hasattr(info, "StringTable")
            for table in info.StringTable
            for key, value in table.entries.items()
        }
        assert strings[b"FileDescription"] == b"Plugin package test"
        assert strings[b"InternalName"] == b"TestPlugin"
        assert strings[b"FileVersion"] == b"0.1.0.0"
        assert strings[b"ProductVersion"] == b"0.1.0.0"
        assert b"Test Author" in dll
    if game == "skyrim":
        objects = list((project / "build/.objs").rglob("DevBenchAPI.cpp.obj"))
        assert len(objects) == 1
        modified = objects[0].stat().st_mtime_ns
        run(project, native_xmake, "build", "-y")
        assert objects[0].stat().st_mtime_ns == modified
