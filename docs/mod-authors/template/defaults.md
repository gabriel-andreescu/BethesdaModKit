# Template defaults

See [the template's build choices](projects.md#what-the-template-selects) for
compiler defaults, packaged outputs and optional components.

## Editor and Git settings

Projects include `.editorconfig` and `.gitattributes` for consistent
indentation, LF line endings and binary mod assets. VS Code settings recommend
and configure EditorConfig, XMake, Prettier, StyLua and the Lua language server,
along with the extensions for the selected components. `.luarc.json` loads the
XMake declarations and plugin from
[xmake-luals](https://github.com/gabriel-andreescu/xmake-luals), which `xmake f`
installs into `.xmake/luals`.

## Formatting

Pre-commit formats staged files with:

- **Prettier:** Markdown, YAML and JSON, with `proseWrap: "always"`.
- **StyLua:** Lua, using four-space indentation.
- **Ruff**, when Python tests are included: lint fixes, import sorting and
  formatting.
- **[CSharpier](https://csharpier.com/docs/About)**, when C# is included: C# and
  XML. Run `dotnet tool restore` once per clone to install the pinned tool.
- **clang-format**, when native code is included: C and C++ sources using
  clang-format 23.1.0.

After initializing the project's Git repository, install the hooks with:

```powershell
uv tool install pre-commit
pre-commit install
```

Run formatting and lint fixes on all tracked files with
`pre-commit run --all-files`. CI runs the same hooks and fails if they change
files or report errors.

## DevBench

`devbench_tests` adds Python dependencies and a startup test under
`tests/game/`. Session setup waits for the main menu before any game test. Tests
share that session and can load their own saves without restarting Skyrim.

See
[DevBench setup and pytest options](../tooling/skyrim/devbench.md#python-setup)
for dependencies, launch commands and running the suite.

`devbench_api` adds the
[native API and BMK helpers](../tooling/skyrim/devbench.md#native-api) to the
plugin's dependencies. Both options are independent and can be added through a
Copier update.

## Native plugins

Native projects include `.clang-format`, `.clangd` and `.clang-tidy`. The clangd
configuration uses `clang-cl` for Windows x64 C++23. The clang-tidy header
filter covers `src/`. Adjust it if project headers live elsewhere. Generated
native targets precompile the CommonLib and script extender headers in `PCH.h`.

See [native build rules](../tooling/native-plugins.md) and
[Clang commands](../tooling/clang.md).

## Papyrus

Papyrus targets enable strict checks and
[Caprica's language extensions](https://github.com/gabriel-andreescu/Caprica#language-extensions).
They include PSC sources in packages under `Source/Scripts/` for Skyrim or
`Scripts/Source/User/` for Fallout 4. Remove the target's `add_installfiles`
declaration to omit sources.

Skyrim targets include the
[Papyrus SDK](../tooling/papyrus.md#imports-and-compiler-options) for vanilla
interfaces.

The generated XMake options accept local import paths and an optional flags
file:

```powershell
xmake f --papyrus_imports="C:/Game/Source/Scripts;C:/Dependencies/Scripts"
xmake f --papyrus_flags="path/to/CustomFlags.flg"
```

See the [Papyrus rule](../tooling/papyrus.md) for compiler arguments and
imports.

## C# projects

`plugin_generation`, `plugin_patching` and `mcm` create .NET 10 projects with
`global.json`, `Directory.Build.props` and a root `.slnx` solution.

CSharpier uses its [defaults](https://csharpier.com/docs/Configuration) with the
indentation and line endings in `.editorconfig`. Run it independently of
pre-commit with:

```powershell
dotnet csharpier format .
```

Use `dotnet csharpier check .` to check formatting without editing files. The
generated editor settings select CSharpier for C# and XML and enable formatting
on save.

`Directory.Build.props` enables the SDK's
[recommended analyzers](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview#enable-additional-rules)
and treats warnings as errors. Builds also enforce the `.editorconfig` code
style: `var` only where the type is apparent, following
[Microsoft's conventions](https://learn.microsoft.com/dotnet/csharp/fundamentals/coding-style/coding-conventions#implicitly-typed-local-variables),
and braces on every block. `dotnet format style` and `dotnet format analyzers`
can apply available code fixes. CSharpier owns whitespace formatting.

See [C# build rules](../tooling/dotnet.md) for generator arguments, patcher
inputs and package outputs.

For Synthesis, set the input Data directory and load-order file through the
generated `synthesis_data` and `synthesis_load_order` XMake options:

```powershell
xmake f --synthesis_data="C:/PatchInputs/Data" --synthesis_load_order="patch-loadorder.txt"
```

### Persistent FormIDs

The Mutagen project configures `TextFileFormKeyAllocator` with a `FormIDs.txt`
mapping beside the C# project. Commit this file with the generator. Copier
updates preserve it.

See [persistent FormIDs](../tooling/dotnet.md#persistent-formids) for allocation
names and shared mappings.

## CI workflow

`.github/workflows/build.yml` calls BMK's
[build workflow](../tooling/github-actions.md) at the project's BMK release. It
runs on pushes to `main`, pull requests and manual runs. Version tags also
publish a GitHub release.
