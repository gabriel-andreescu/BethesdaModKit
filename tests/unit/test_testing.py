import pytest

from bmk.testing import preserved_file, set_ini_values, wait_for


def test_wait_returns_matched_observation():
    states = iter([{"value": 1}, {"value": 7}])
    expected = 7
    assert wait_for(
        lambda: next(states), lambda state: state["value"] == expected, interval=0
    ) == {"value": 7}


def test_wait_keeps_last_observation_and_callback_errors():
    with pytest.raises(AssertionError, match='"value": 9'):
        wait_for(lambda: {"value": 9}, lambda _: False, timeout=0)

    def unavailable():
        raise RuntimeError("inspection unavailable")

    with pytest.raises(RuntimeError, match="inspection unavailable"):
        wait_for(unavailable)


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
def test_ini_edits_are_literal_and_restore_original_bytes(tmp_path, newline):
    path = tmp_path / "settings.ini"
    original = newline.join([b"[Test]", b"value = before", b"untouched = yes", b""])
    path.write_bytes(original)
    with pytest.raises(RuntimeError), preserved_file(path, tmp_path / "backup.ini"):
        set_ini_values(path, {"value": "$1 literal"})
        assert path.read_bytes() == original.replace(b"before", b"$1 literal")
        raise RuntimeError("test failed")
    assert path.read_bytes() == original
    assert (tmp_path / "backup.ini").read_bytes() == original


@pytest.mark.parametrize(
    "original,changes",
    [
        (b"value=before\n", {"value": "after", "missing": 1}),
        (b"[A]\nvalue=1\n[B]\nvalue=2\n", {"value": 3}),
    ],
)
def test_rejected_ini_edits_do_not_partially_write(tmp_path, original, changes):
    path = tmp_path / "settings.ini"
    path.write_bytes(original)
    with pytest.raises(ValueError, match="Expected one setting"):
        set_ini_values(path, changes)
    assert path.read_bytes() == original
