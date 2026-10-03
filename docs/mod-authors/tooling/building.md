# Using BMK in an existing mod

BMK's build rules require Git and
[XMake 3.1.1](https://github.com/xmake-io/xmake/releases/tag/v3.1.1) or newer.
BSA/BA2 packing requires Windows.

## Setup

| Integration                                            | Requirements                                   | Adds to the project                                                   |
| ------------------------------------------------------ | ---------------------------------------------- | --------------------------------------------------------------------- |
| XMake build rules                                      | XMake and the chosen component's toolchain     | Build targets, packaging and optional deployment.                     |
| [Python helpers](skyrim/devbench.md#python-setup)      | Python 3.11+, DevBench for game operations     | A Python dependency. Native integration is optional.                  |
| [C++ inspection helper](skyrim/devbench.md#native-api) | CommonLibSSE-NG, SKSE and DevBench API headers | Header-only game-thread inspection. Works with existing CMake builds. |

These integrations do not require Copier or its generated project layout.

A complete asset-only `xmake.lua`:

```lua
set_xmakever("3.1.1")
set_project("MyMod")
set_policy("package.requires_lock", true)

add_repositories("bmk https://github.com/gabriel-andreescu/BethesdaModKit.git")
add_addons("bmk X.Y.Z")
includes("@addon/bmk/project")

target("MyMod", function()
    set_version("1.0.0")
    add_rules("@addon/bmk/skyrim.package")
    add_installfiles("assets/(**)")
end)
```

The root policy enables XMake's dependency lockfile. `project` declares the
`deploy` and `distdir` options. Native plugins also include `@addon/bmk/native`
for the compiler defaults.

Place files under `assets/` using the paths you want inside the ZIP. For
example, `assets/textures/MyMod/iron.dds` becomes `textures/MyMod/iron.dds`. Use
`@addon/bmk/fallout4.package` for Fallout 4.

## Build and package

```powershell
xmake
xmake package
```

The example writes `build/dist/MyMod/MyMod-1.0.0.zip`. To add compilation,
declare the component targets and list them in the
[package's `targets` option](packaging.md#package-composition).

Configure asset paths, deployment destinations and ZIP outputs through
[deployment and packaging](packaging.md). For BSA/BA2 settings, see
[archive options](archives.md).

[Papyrus](papyrus.md) requires Windows and the script sources imported by your
mod. [Interface builds](interface.md) resolve FFDec and Java through XMake.
[C# generators](dotnet.md) require a matching .NET SDK.

## SKSE and F4SE plugins

Requires Visual Studio 2022 with the C++ toolset and Windows SDK. For clang-cl
builds, also install LLVM and configure the toolchain:

```powershell
xmake f --toolchain=clang-cl
```

See [native target configuration](native-plugins.md#target-configuration) and
[Clang tooling](clang.md) for compilation databases and linting.
