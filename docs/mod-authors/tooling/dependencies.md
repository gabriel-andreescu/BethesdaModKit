# Dependencies and runtimes

## Native runtimes

| Target    | CommonLib configuration | Runtime requirements                                                                                                                |
| --------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Skyrim SE | `skyrim_se`             | Skyrim 1.5.97, matching SKSE and Address Library.                                                                                   |
| Skyrim AE | `skyrim_ae`             | Steam or GOG runtime supported by SKSE and its matching Address Library. The pinned headers include Steam 1.7.104 and GOG 1.6.1179. |
| Skyrim VR | `skyrim_vr`             | Skyrim VR 1.4.15, SKSEVR and VR Address Library. See the form-factory override below.                                               |
| Fallout 4 | CommonLibF4             | The pinned library's generated metadata declares Fallout 4 1.11.240. Use matching F4SE and Address Library.                         |

The Skyrim package enables SE, AE and VR together. Restrict a build through the
CommonLib package configurations when the mod targets fewer runtimes:

```lua
add_requires("commonlibsse-ng 8.0.1", {system = false, configs = {
    skyrim_se = false,
    skyrim_ae = true,
    skyrim_vr = false
}})
```

Runtime support also depends on the mod's relocations, hooks and structure
access. A successful build does not establish in-game compatibility. Test the
mod on each runtime it supports.

See [SKSE](https://skse.silverlock.org/),
[Skyrim Address Library](https://www.nexusmods.com/skyrimspecialedition/mods/32444),
[VR Address Library](https://www.nexusmods.com/skyrimspecialedition/mods/58101),
[F4SE](https://f4se.silverlock.org/) and
[Fallout 4 Address Library](https://www.nexusmods.com/fallout4/mods/47327).

## Library sources

| Dependency      | Source used by BMK                                                                                                                                                  | BMK changes                                                   |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| CommonLibSSE-NG | [gabriel-andreescu/CommonLibSSE-NG](https://github.com/gabriel-andreescu/CommonLibSSE-NG), pinned in [the recipe](../../../packages/c/commonlibsse-ng/xmake.lua)    | Installed-package metadata rule and VR form-factory override. |
| CommonLibF4     | [libxse/commonlibf4](https://github.com/libxse/commonlibf4), with its matching commonlib-shared revision in [the recipe](../../../packages/c/commonlibf4/xmake.lua) | Installed-package metadata rule.                              |
| CLibUtil        | [gabriel-andreescu/CLibUtil](https://github.com/gabriel-andreescu/CLibUtil), pinned in [the recipe](../../../packages/c/clib-util/xmake.lua)                        | Headers installed unchanged.                                  |
| DevBench API    | [alandtse/devbench](https://github.com/alandtse/devbench), pinned in [the recipe](../../../packages/d/devbench-api/xmake.lua)                                       | Packages the MIT API header and companion source.             |

The CommonLib metadata rules use the libraries' resource templates and default
the embedded DLL name to the target's basename.

The
[VR override](../../../packages/c/commonlibsse-ng/patches/vr-form-factory.patch)
changes the address used to read `IFormFactory`'s initialization flag.

## Build tools

| Component    | Tool                                                                                                                                                                               |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Papyrus      | Windows binaries from [gabriel-andreescu/Caprica](https://github.com/gabriel-andreescu/Caprica/releases), selected by [the Caprica recipe](../../../packages/c/caprica/xmake.lua). |
| Scaleform UI | [FFDec](https://github.com/jindrapetrik/jpexs-decompiler), selected by [the FFDec recipe](../../../packages/f/ffdec/xmake.lua). Java is resolved as a dependency.                  |
| BSA/BA2      | Bundled BSArch and loader plugins. See [bundled resources](../../../xmake/modules/archives/resources/README.md).                                                                   |

XMake resolves the compiler tools automatically. Mutagen and Synthesis projects
use NuGet dependencies and require the .NET SDK selected by `global.json`.
