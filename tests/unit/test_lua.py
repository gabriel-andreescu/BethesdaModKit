import shutil

import pytest
from tests.support import ROOT, run


@pytest.mark.parametrize("module", ["archives", "components"])
def test_lua_rules(tmp_path, module):
    xmake = shutil.which("xmake")
    assert xmake, "Install XMake to run Lua tests."
    run(tmp_path, xmake, "lua", str(ROOT / f"tests/unit/lua/{module}.lua"))
