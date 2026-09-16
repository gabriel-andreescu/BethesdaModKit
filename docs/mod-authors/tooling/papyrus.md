# Papyrus

BMK installs a prebuilt [Caprica](https://github.com/gabriel-andreescu/Caprica)
compiler for Windows x64 through XMake. Provide game and dependency script
sources through `imports`.

## Target configuration

```lua
add_requires("caprica", {host = true})

target("Papyrus")
    set_default(false)
    add_rules("@addon/bmk/skyrim.papyrus", {
        root = "src/papyrus",
        imports = {"dependencies/scripts"}
    })
    add_packages("caprica")
    add_files("src/papyrus/**.psc")
```

Use `@addon/bmk/fallout4.papyrus` for Fallout 4. Select the Papyrus target in a
[package](packaging.md#package-composition) to ship its PEX files under
`Scripts/`.

| Option      | Default                       | Purpose                                           |
| ----------- | ----------------------------- | ------------------------------------------------- |
| `root`      | Required                      | Source root used for compilation.                 |
| `imports`   | `{}`                          | Additional import directories, passed to Caprica. |
| `flags`     | Caprica's built-in game flags | Path to a flags file override.                    |
| `arguments` | `{}`                          | Additional Caprica arguments.                     |

## Imports and compiler options

BMK passes the source `root` first, followed by `imports` in the order written.
Papyrus SDK packages added with `add_packages` append their include directories.
Caprica gives earlier imports precedence over later ones.

Change compiler options through `arguments`. See
[Caprica's options](https://github.com/gabriel-andreescu/Caprica/blob/v2026.9.17/Caprica/main_options.cpp)
for the available flags.

## Outputs

Only scripts selected with `add_files` are compiled. PEX files are written to
`build/artifacts/<target>/`, or the target's `set_targetdir`, and exposed to
packages under `Scripts/`. Source and imported PSC files, flags and compiler
arguments determine when scripts are rebuilt.

Include PSC sources with `add_installfiles`:

```lua
add_installfiles("src/papyrus/(**.psc)", {prefixdir = "Source/Scripts"})
```

Use `Scripts/Source/User` for Fallout 4.
