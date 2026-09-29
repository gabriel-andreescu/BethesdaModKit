# BMK development

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). From the BMK root:

```powershell
uv sync --locked
uv run pre-commit install
```

## Formatting and lint

The [commit hooks](../../.pre-commit-config.yaml) format staged files with
Prettier, Ruff and StyLua, and apply Ruff lint fixes. Prettier uses
[`proseWrap: "always"`](https://prettier.io/docs/options#prose-wrap). StyLua
uses four-space indentation. Run the hooks on all tracked files with:

```powershell
uv run pre-commit run --all-files
```

Builds enforce the C# code style in `.editorconfig`: `var` only where the type
is apparent, and braces on every block.

CI runs the same checks. Jinja templates and bundled license files are excluded
from formatting.

## XMake

Requires [XMake 3.1.1](https://github.com/xmake-io/xmake/releases/tag/v3.1.1).

## Tests

Run the unit tests:

```powershell
uv run pytest
```

These cover Python helpers, archive rules and compiler arguments. Lua tests use
XMake.

Integration tests require Windows, Git, PowerShell 7 and XMake:

```powershell
uv run pytest tests/integration -n 4
```

These cover generated projects, deployment, packaging, release scripts and the
pytest plugin lifecycle. Use `-n 0` for serial execution.

Set `BMK_TEST_CACHE` to choose the XMake test cache directory.

## Native tests

Requires an x64 C++23 compiler. XMake installs Catch2.

```powershell
xmake -P tests/native
xmake test -P tests/native
```

These tests cover queued inspection results, exceptions, timeouts and captured
data lifetime.

For clangd support in the Skyrim headers, generate the consumer's compilation
database after installing the local addon as described in
[consumer validation](../../CONTRIBUTING.md#validate-package-and-rule-changes):

```powershell
xmake f -P tests/native/plugins -y -a x64 --game=skyrim --deploy=n
xmake project -P tests/native/plugins -k compile_commands --lsp=clangd
```

To build and inspect Skyrim and Fallout 4 plugin packages:

```powershell
$env:BMK_TEST_NATIVE_PLUGINS = "1"
uv run pytest tests/native/test_plugins.py
Remove-Item Env:BMK_TEST_NATIVE_PLUGINS
```

`BMK_TEST_TOOLCHAIN` selects `msvc` (default) or `clang-cl`. These tests check
package installation, DLL exports and ZIP contents.
