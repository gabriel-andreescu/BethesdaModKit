# Settings and MCM

In the [Copier options](projects.md#options), enable `native_settings` for
[CLibUtil](https://github.com/powerof3/CLibUtil)-based INI settings and `mcm`
for an optional MCM addon.

Adding `mcm` later is backward-compatible with existing user settings.

## Native settings

The native plugin reads `MCM/Config/<name>/settings.ini` from the main package,
overlays the user file `MCM/Settings/<name>.ini` and saves it with missing
settings filled in.

Users edit the generated INI. Changes take effect after a game restart. Existing
user values take precedence over changes to packaged defaults.

`bDebugLogging` switches the CommonLib logger to debug level. When it is
disabled, the logger uses CommonLib's build-dependent default. An attached
debugger also enables debug logging.

## MCM addon

When the MCM menu closes, the generated handler calls `Settings::Reload()` to
reload the INI and apply `bDebugLogging`. Extend it to apply your mod's other
settings.

The optional `<name>MCM` package contains:

- `<name>.esp`, containing the MCM quest and records built by the same Mutagen
  generator.
- The quest script and native Papyrus declarations, including sources.
- `MCM/Config/<name>/config.json`.

The settings identifier matches `<name>.esp`, as required by Skyrim's MCM
Helper.

| Game      | MCM dependencies                                                                                                                               | Reload event    |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| Skyrim    | [SkyUI](https://www.nexusmods.com/skyrimspecialedition/mods/12604) and [MCM Helper](https://www.nexusmods.com/skyrimspecialedition/mods/53000) | `OnConfigClose` |
| Fallout 4 | [Mod Configuration Menu](https://www.nexusmods.com/fallout4/mods/21497)                                                                        | `OnMCMClose`    |

Set [Papyrus imports](defaults.md#papyrus) to the game's source scripts. The
Skyrim template includes the
[MCM Helper SDK](https://github.com/Exit-9B/MCM-Helper/wiki/Creating-a-Config-Script)
as an XMake dependency. Fallout 4 also needs the matching F4SE sources for
`RegisterForExternalEvent`.

### ESP variants

With `plugin_generation` selected, one Mutagen target generates both ESP
variants with a shared [FormID mapping](defaults.md#persistent-formids). The
optional ESP replaces the main ESP and retains the records created by
`BuildPlugin(mod)` before adding the MCM quest.

The generator does not import an ESP from `assets/`. An independently authored
`assets/<name>.esp` conflicts with the generated MCM variant, so the build
rejects it. Add those records to the generator, or configure a separate MCM
plugin instead of using the replacement layout.

Without `plugin_generation`, the Mutagen-generated ESP goes only in the optional
MCM package. [Archive packing](../tooling/archives.md) can still add an empty
loader ESP to the main package.

Both packages use the `version` declared in `xmake.lua`. Publish them together,
including for MCM-only changes, so the replacement ESP matches the main release.

For a project with main records, the ZIP contents include:

```text
MyMod-0.1.0.zip
  MyMod.esp
  SKSE/Plugins/MyMod.dll
  MCM/Config/MyMod/settings.ini

MyModMCM-0.1.0.zip
  MyMod.esp
  Scripts/MyModMCM.pex
  MCM/Config/MyMod/config.json
```

Install the main mod first, then let the optional MCM addon overwrite
`MyMod.esp`. Keep the main and addon versions together. Fallout 4 uses
`F4SE/Plugins/` for the DLL.

Build the MCM addon with:

```sh
xmake package MyModMCM
```
