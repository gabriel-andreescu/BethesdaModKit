# Projects

Copier creates a project for Skyrim or Fallout 4. Add components during creation
or through a later update.

## First build

Requires Copier, Git, XMake 3.1.1 or newer and, for this SKSE DLL example,
Windows with an MSVC C++23 toolchain and Windows SDK.

```powershell
copier copy --defaults -d project_name=MyMod -d 'components=[native]' https://github.com/gabriel-andreescu/BethesdaModKit.git MyMod
cd MyMod
xmake f -y
xmake package
```

The ZIP at `build/dist/MyMod/MyMod-0.1.0.zip` contains `SKSE/Plugins/MyMod.dll`
and its PDB. For Fallout 4, add `-d game=fallout4` when creating the project.
Its DLL and PDB go under `F4SE/Plugins/` instead.

To deploy the same files while building, create `.xmake/bmk/deploy.json`:

```json
{
  "MyMod": ["C:/Mods/MyMod - dev"]
}
```

Run `xmake` and check `C:/Mods/MyMod - dev/SKSE/Plugins/MyMod.dll`. Point the
destination at a separate test mod directory, or the game's `Data/` directory
for an unmanaged installation. See
[deployment](../tooling/packaging.md#deployment) for ownership and cleanup
behavior.

With no components selected, Copier creates an asset-only project. Add files
under `assets/` before packaging. An empty project produces no ZIP.

## Build a generated project

The generated `xmake.lua` registers BMK and declares the selected components and
packages. Supply the toolchains and local inputs for those components:

| Component            | Local requirements                                                                                              |
| -------------------- | --------------------------------------------------------------------------------------------------------------- |
| Native               | Windows, an MSVC C++23 toolchain and Windows SDK.                                                               |
| Papyrus or MCM       | Windows and [Papyrus import paths](defaults.md#papyrus). Fallout 4 MCM also needs matching F4SE script sources. |
| Mutagen or Synthesis | The .NET SDK specified in `global.json`.                                                                        |
| Synthesis            | [Input Data directory and load-order file](defaults.md#c-projects).                                             |

From the project root:

```sh
xmake f -y
xmake
xmake package
```

Packages are written to `build/dist/<target>/`. See
[deployment and packaging](../tooling/packaging.md) for local deployment,
package selection and output paths, and [template defaults](defaults.md) for
formatting, tests and compiler settings.

## What the template selects

- Native targets use x64, C++23, `releasedbg`, the dynamic MSVC runtime and
  extra warnings as errors. ZIPs include the DLL and available debug symbols.
- Papyrus targets use Caprica with strict checks and language extensions. ZIPs
  include the compiled scripts and their PSC sources.
- MCM adds Papyrus and a Mutagen/.NET project. With `plugin_generation`, the
  optional ZIP contains a replacement ESP and must be released with the main
  ZIP. Otherwise, the Mutagen-generated ESP goes only in the optional ZIP. See
  [the MCM file layout](settings.md#esp-variants).
- BSA/BA2 packing adds an empty ESL-flagged ESP when the package has no plugin
  to load its archives. That ESP must be activated in the load order.

See [template defaults](defaults.md) for the generated configuration, and
[dependencies and runtimes](../tooling/dependencies.md) for the selected
libraries.

## Options

Pass answers with `-d name=value`, or use the interactive prompts.

| Answer                  | Default                                                   | Purpose                                                                                                                                               |
| ----------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `project_name`          | `MyMod`                                                   | Project name and initial DLL/ESP basenames.                                                                                                           |
| `game`                  | `skyrim`                                                  | `skyrim` or `fallout4`.                                                                                                                               |
| `components`            | `[]`                                                      | Components: SKSE/F4SE DLL (`native`), Papyrus (`papyrus`), SWF (`interface`), Mutagen ESP (`plugin_generation`), Synthesis patch (`plugin_patching`). |
| `description`, `author` | Empty                                                     | Project metadata.                                                                                                                                     |
| `pre_commit`            | `true`                                                    | Include [formatting and lint hooks](defaults.md#formatting).                                                                                          |
| `native_source`         | `src` for native only without MCM, otherwise `src/native` | Native source directory.                                                                                                                              |
| `papyrus_source`        | `src/papyrus`                                             | Papyrus source directory.                                                                                                                             |
| `interface_source`      | `src/interface`                                           | FFDec XML and ActionScript directory.                                                                                                                 |
| `mutagen_source`        | `src/mutagen/<project_name>`                              | Initial Mutagen project directory.                                                                                                                    |
| `synthesis_source`      | `src/synthesis/<project_name>Patch`                       | Initial Synthesis project directory.                                                                                                                  |
| `clib_util`             | `true`                                                    | Include CLibUtil with a native plugin.                                                                                                                |
| `native_settings`       | `false`                                                   | Generate native settings using CLibUtil. Requires `native`.                                                                                           |
| `mcm`                   | `false`                                                   | Add an optional [MCM package](settings.md). Requires native settings.                                                                                 |
| `devbench_tests`        | `false`                                                   | Set up pytest with BMK's DevBench client and fixtures for Skyrim.                                                                                     |
| `devbench_api`          | `false`                                                   | Include the DevBench API and BMK helpers for a Skyrim native plugin.                                                                                  |
| `pack_assets`           | `false`                                                   | Enable BSA/BA2 packing on the initial package.                                                                                                        |
| `deploy`                | Empty                                                     | Initial deployment destinations, separated by `;`. Stored locally.                                                                                    |
| `bmk_repository`        | BMK's GitHub URL                                          | Package repository URL or local directory.                                                                                                            |

Put source files in `src/` and files to include unchanged in `assets/`. BMK
writes build output to `build/`. Source paths are configurable. Selecting native
settings includes CLibUtil regardless of `clib_util`. MCM also generates the
Papyrus scripts and Mutagen project it needs.

Multiple games can coexist through manually composed
[targets](../tooling/native-plugins.md#shared-native-sources) and
[packages](../tooling/packaging.md).

## Adding components and updating

Keep `.copier-answers.yml` in Git. From a clean working tree:

```sh
copier update
```

To add components, supply the complete selection:

```sh
copier update -d 'components=[native, papyrus, interface]'
```

This adds the selected source scaffolding and build declarations while Copier
merges changes with project edits. Review any merge conflicts.

Copier retains the configured source paths. To reorganize existing code, move
the files yourself and pass the new path, such as `-d native_source=src/native`.

Add further build or package targets directly in `xmake.lua`.

Copier updates project files. Use the separate
[tool and dependency update commands](../tooling/updating.md) to update
installed build tools, Python dependencies or the reusable workflow.
