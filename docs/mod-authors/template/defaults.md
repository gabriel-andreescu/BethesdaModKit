# Template defaults

See [the template's build choices](projects.md#what-the-template-selects) for
compiler defaults, packaged outputs and optional components.

## Editor and Git settings

Projects include `.editorconfig` and `.gitattributes` for consistent
indentation, LF line endings and binary mod assets.

## Formatting

Pre-commit formats staged files with:

- **Prettier:** Markdown (`.md`), YAML (`.yaml`, `.yml`) and JSON (`.json`,
  `.jsonc`), using [Prettier's defaults](https://prettier.io/docs/options) with
  `proseWrap: "always"`.
- **StyLua:** Lua (`.lua`), using four-space indentation.
- **Ruff**, when Python is included: lint fixes and formatting for `.py` and
  `.pyi` files. The lint configuration also enables import sorting.
- **[CSharpier](https://csharpier.com/docs/About)**, when C# is included: C# and
  XML (`.cs`, `.csx`, `.csproj`, `.props`, `.targets`, `.slnx`, `.xml`,
  `.config`). The hook restores the pinned .NET tool before formatting.

After initializing the project's Git repository, install the hooks with:

```sh
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

Native projects include `.clang-format`, `.clangd` and `.clang-tidy`. The
formatting configuration requires clang-format 23 or newer. The clangd
configuration uses `clang-cl` for Windows x64 C++23. The clang-tidy header
filter covers `src/`. Adjust it if project headers live elsewhere.

See [native build rules](../tooling/native-plugins.md) and
[Clang commands](../tooling/clang.md).

## Papyrus

Papyrus targets enable strict checks and
[Caprica's language extensions](https://github.com/gabriel-andreescu/Caprica#language-extensions).
They include PSC sources in packages under `Source/Scripts/` for Skyrim or
`Scripts/Source/User/` for Fallout 4. Remove the target's `add_installfiles`
declaration to omit sources.

The generated XMake options accept local import paths and an optional flags
file:

```sh
xmake f --papyrus_imports="C:/Game/Source/Scripts;C:/Dependencies/Scripts"
xmake f --papyrus_flags="path/to/CustomFlags.flg"
```

See the [Papyrus rule](../tooling/papyrus.md) for compiler arguments and
imports.

## C# projects

`plugin_generation`, `plugin_patching` and `mcm` create .NET 10 projects with
`global.json`, `Directory.Build.props` and a root `.slnx` solution.

CSharpier uses its [defaults](https://csharpier.com/docs/Configuration) with the
indentation and line endings in `.editorconfig`. Restore and run it
independently of pre-commit with:

```sh
dotnet tool restore
dotnet csharpier format .
```

Use `dotnet csharpier check .` to check formatting without editing files. The
generated editor settings select CSharpier for C# and XML and enable formatting
on save.

`Directory.Build.props` enables the SDK's
[recommended analyzers](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview#enable-additional-rules)
and treats warnings as errors. `dotnet format style` and
`dotnet format analyzers` can apply available code fixes. CSharpier owns
whitespace formatting.

See [C# build rules](../tooling/dotnet.md) for generator arguments, patcher
inputs and package outputs.

For Synthesis, set the input Data directory and load-order file through the
generated `synthesis_data` and `synthesis_load_order` XMake options:

```sh
xmake f --synthesis_data="C:/PatchInputs/Data" --synthesis_load_order="patch-loadorder.txt"
```

### Persistent FormIDs

The Mutagen project configures `TextFileFormKeyAllocator` with a `FormIDs.txt`
mapping beside the C# project. Commit this file with the generator. Copier
updates preserve it.

See [persistent FormIDs](../tooling/dotnet.md#persistent-formids) for allocation
names and shared mappings.

## GitHub Actions

The generated workflow calls BMK's
[reusable build workflow](../tooling/github-actions.md) on pushes to `main`,
pull requests and manual runs. Version tags also publish a GitHub release.
