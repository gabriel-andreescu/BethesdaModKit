# Scaleform UI builds

BMK resolves [FFDec](https://github.com/jindrapetrik/jpexs-decompiler) and Java
through XMake. A target builds one SWF from FFDec XML or an existing SWF,
optionally importing ActionScript.

## `@addon/bmk/ffdec`

```lua
add_requires("ffdec 26.3.0", {host = true})

target("Interface")
    set_default(false)
    add_rules("@addon/bmk/ffdec", {
        xml = "src/interface/swf/MyMod.xml",
        scripts = "src/interface/actionscript",
        output = "MyMod.swf"
    })
    add_packages("ffdec")
```

Select the target in a [package](packaging.md#package-composition) to ship the
SWF under `Interface/`.

| Option         | Default  | Purpose                                           |
| -------------- | -------- | ------------------------------------------------- |
| `xml` or `swf` | Required | Input FFDec XML or SWF. Supply exactly one.       |
| `scripts`      | None     | FFDec ActionScript import directory.              |
| `output`       | Required | Output filename relative to the target directory. |

The target writes its SWF under `build/artifacts/<target>/`, or `set_targetdir`.
The input XML or SWF, imported scripts and `add_extrafiles` inputs determine
when it is rebuilt.

## ActionScript inputs

Keep the directory structure produced by FFDec's script export, such as
`frame_1/DoAction.as` for Skyrim's AS2 scripts or class paths for Fallout 4's
AS3. Script imports replace scripts already present in the input SWF. When
starting from an existing UI, use FFDec to export its structure and scripts. For
configured ActionScript, use XMake's `add_configfiles` and point `scripts` to
the configured output directory. Translations and other ready-to-ship files use
ordinary package mappings.
