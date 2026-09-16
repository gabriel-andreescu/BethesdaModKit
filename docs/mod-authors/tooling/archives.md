# BSA and BA2 archives

Enable `bsa` or `ba2` on a package:

```lua
add_rules("@addon/bmk/skyrim.package", {bsa = true})
add_rules("@addon/bmk/fallout4.package", {ba2 = true})
```

Selected files from the prepared package are packed for
[deployment and ZIP packaging](packaging.md).

| Game      | Main archive          | Texture archive           |
| --------- | --------------------- | ------------------------- |
| Skyrim    | `<plugin>.bsa`        | `<plugin> - Textures.bsa` |
| Fallout 4 | `<plugin> - Main.ba2` | `<plugin> - Textures.ba2` |

BMK uses the plugin matching the target name, or the only plugin in the package.
If there is no plugin, it supplies an empty ESL-flagged `<target>.esp`. Activate
that plugin to load the archives. For multiple plugins, select which one the
archives belong to:

```lua
add_rules("@addon/bmk/skyrim.package", {bsa = {plugin = "MyMod.esp"}})
```

## File selection

Defaults select these extensions recursively and case-insensitively:

| Directory               | Extensions                                                                                                             |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `meshes/`               | `.bto`, `.btr`, `.btt`, `.dtl`, `.egm`, `.hkb`, `.hkx`, `.lst`, `.nif`, `.tri`, `.hkc`, `.hkt`, `.hkp`, `.ini`, `.txt` |
| `textures/`             | `.dds`, `.png`, `.tga`                                                                                                 |
| `materials/`            | `.bgem`, `.bgsm`                                                                                                       |
| `interface/`            | `.dds`, `.gfx`, `.swf`, `.txt`, `.png`                                                                                 |
| `scripts/`              | `.psc`, `.pex`, `.txt`                                                                                                 |
| `source/`               | `.psc`                                                                                                                 |
| `sound/`                | `.fuz`, `.lip`, `.ogg`, `.wav`, `.xwm`                                                                                 |
| `sound/voice/`          | Also `.hkx`, `.mp3`                                                                                                    |
| `music/`                | `.xwm`, `.mp3`                                                                                                         |
| `strings/`              | `.dlstrings`, `.ilstrings`, `.strings`                                                                                 |
| `shadersfx/`            | `.fxp`                                                                                                                 |
| `grass/`                | `.cgid`, `.gid`, `.lnk`                                                                                                |
| `lodsettings/`          | `.dlodsettings`, `.lod`, `.lodsettings`                                                                                |
| `seq/`                  | `.seq`                                                                                                                 |
| `vis/` (Fallout 4)      | `.uvd`                                                                                                                 |
| `programs/` (Fallout 4) | `.swf`                                                                                                                 |

Skyrim character animations and behaviors, including their `_1stperson`
variants, stay loose for animation generators.
`meshes/animationdatasinglefile.txt`, `meshes/animationsetdatasinglefile.txt`
and files named `readme.txt` also stay loose. BodySlide files and
`dialogueviews/` are outside the default selection.

Override the defaults with XMake file patterns relative to the archive input
root:

```lua
add_rules("@addon/bmk/skyrim.package", {bsa = {
    files = {"meshes/**|actors/character/animations/**", "scripts/**", "source/**"}
}})
```

`files` replaces the entire automatic selection, including its exclusions.
`files = {}` packs nothing. Missing directories are skipped. Selecting files
BSArch cannot pack, such as DLLs or plugin files, fails the build.

The archive input root defaults to the package root. For a package containing a
`Data/` directory, set `root = "Data"` in the archive options.

## Compression and splitting

BSArch compresses archive entries while leaving audio and strings uncompressed,
except FUZ voice files and voice-line HKX files. Fallout 4 DDS archives use the
required texture compression. Assets are not optimized or converted to other
texture formats.

Archives split at 2 GiB for Skyrim and 4 GiB for Fallout 4. Set `split_size` in
GiB to a whole number from 1 to 2 for Skyrim or 1 to 8 for Fallout 4. Additional
parts receive matching numbered loader plugins, which must also be activated.

BMK bundles BSArch and empty loader plugins. See
[Bundled resources](../../../xmake/modules/archives/resources/README.md) for
attribution and licensing.
