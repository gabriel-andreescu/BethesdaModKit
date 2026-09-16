import os


def test_payload_reuse_and_input_changes(payload_module):
    stage, invoke = payload_module
    sources = stage / "source"
    sources.mkdir()
    script = sources / "test.psc"
    script.write_bytes(b"original")
    first = invoke()
    payload = first["output"]
    archive = payload / "TestMod.bsa"
    modified = archive.stat().st_mtime_ns
    assert len(first["calls"]) == 1

    unchanged = invoke()
    assert not unchanged["calls"]
    assert archive.stat().st_mtime_ns == modified

    (stage / "plugin.dll").write_bytes(b"native output")
    assert not invoke()["calls"]
    assert (payload / "plugin.dll").read_bytes() == b"native output"

    # XMake compares modification times in whole seconds.
    changed = script.stat().st_mtime + 2
    script.write_bytes(b"modified")
    os.utime(script, (changed, changed))
    assert len(invoke()["calls"]) == 1

    script.unlink()
    assert not invoke()["calls"]
    assert not archive.exists()
    assert not (payload / "TestMod.esp").exists()


def test_archive_options_replace_payload(payload_module):
    stage, invoke = payload_module
    sources = stage / "source"
    sources.mkdir()
    (sources / "test.psc").write_bytes(b"source")
    textures = stage / "textures"
    textures.mkdir()
    (textures / "test.dds").write_bytes(b"texture")
    payload = invoke()["output"]
    assert (payload / "TestMod - Textures.bsa").is_file()

    invoke(options={"files": ["source/**"]})
    assert not (payload / "TestMod - Textures.bsa").exists()
    assert (payload / "textures/test.dds").read_bytes() == b"texture"

    invoke(options={"files": []})
    assert not (payload / "TestMod.bsa").exists()
    assert not (payload / "TestMod.esp").exists()
    assert (payload / "source/test.psc").read_bytes() == b"source"


def test_failed_archive_preserves_payload_and_sources(payload_module):
    stage, invoke = payload_module
    sources = stage / "source"
    sources.mkdir()
    script = sources / "test.psc"
    script.write_bytes(b"source")
    payload = invoke()["output"]
    archive = payload / "TestMod.bsa"
    previous = archive.read_bytes()
    collision = stage / "TestMod.bsa"
    collision.write_bytes(b"existing archive")

    invoke(error="conflicts")
    assert archive.read_bytes() == previous
    assert script.read_bytes() == b"source"
    assert collision.read_bytes() == b"existing archive"

    collision.unlink()
    invoke(options={"split_size": 1}, fail=True, error="BSArch failed")
    assert archive.read_bytes() == previous
    assert script.read_bytes() == b"source"


def test_asset_overrides_and_removed_override(payload_module):
    stage, invoke = payload_module
    (stage / "config.ini").write_text("base")
    override = stage.parent / "Overrides"
    override.mkdir(parents=True)
    (override / "config.ini").write_text("override")
    script = stage.parent / "xmake.lua"
    script.write_text(
        script.read_text() + '\nadd_installfiles("Missing/(**)", "Overrides/(**)")\n'
    )
    payload = invoke(options=False)["output"]
    assert (payload / "config.ini").read_text() == "override"
    (override / "config.ini").unlink()
    invoke(options=False)
    assert (payload / "config.ini").read_text() == "base"
