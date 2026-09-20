# Deployment and packaging

## Package composition

Each package selects build targets and files:

```lua
target("MyMod")
    set_version("1.2.0")
    add_rules("@addon/bmk/skyrim.package", {
        targets = {"Native", "Papyrus", "Interface", "Mutagen"}
    })
    add_installfiles("assets/main/(**)")

target("OtherModPatch")
    set_version("1.0.0")
    add_rules("@addon/bmk/skyrim.package", {
        targets = {"Synthesis"},
        changelog = "src/synthesis/OtherModPatch/CHANGELOG.md"
    })
    add_installfiles("assets/optional/othermod/(**)")
```

Use `@addon/bmk/fallout4.package` for Fallout 4.

`targets` adds build dependencies and collects each listed target's installable
outputs. Transitive dependencies and targets added only with `add_deps` do not
ship. Outputs are applied in list order, followed by the package's own
`add_installfiles` mappings. Later mappings replace files at the same
destination.

An asset-only mod needs one package target with `add_installfiles`. A mod ZIP
can combine files from several directories. Several ZIPs can reuse the same
files and compiler outputs.

| Option         | Default                           | Purpose                                                                |
| -------------- | --------------------------------- | ---------------------------------------------------------------------- |
| `targets`      | `{}`                              | Build targets whose installable outputs ship.                          |
| `package_name` | Target name without its namespace | ZIP filename before the version suffix.                                |
| `changelog`    | Root `CHANGELOG.md`               | [Release notes](github-actions.md#target-changelogs) for this package. |
| `nexus`        | Unset                             | [Nexus Mods destination](nexus.md) for release uploads.                |
| `bsa` / `ba2`  | `false`                           | [Archive settings](archives.md).                                       |

Use normal XMake mappings to control paths within the package:

```lua
add_installfiles("assets/main/(**)")
add_installfiles("config/MyMod.ini", {prefixdir = "SKSE/Plugins"})
add_installfiles("src/papyrus/(**.psc)", {prefixdir = "Source/Scripts"})
```

`.gitkeep` files are omitted.

## Deployment

Set package destinations in the ignored `.xmake/bmk/deploy.json` file:

```json
{
  "Skyrim::MyMod": ["C:/Mods/Skyrim/MyMod"],
  "Fallout4::MyMod": ["C:/Games/Fallout4/Data"]
}
```

For packages containing `meshes/`, `textures/` or `SKSE/` at their root, use a
mod manager's mod directory or the game's `Data/` directory. Use the game
installation root only when the package itself includes `Data/` or other
root-level files. Use full target names, including namespaces. Paths are
absolute or relative to the project root. Each package accepts multiple
destinations.

```sh
xmake Skyrim::MyMod
xmake
```

Building a package prepares its current files and deploys it to configured
destinations. Targets without destinations are not deployed. Disable deployment
with `xmake f --deploy=n`.

Rebuilds remove obsolete files previously deployed by that package. Packages
sharing a destination must have non-overlapping output paths. Conflicts with
another package or unowned files fail before deployment changes its
destinations.

Ownership records live in the ignored `.bmk/deployment.lua`, independently of
XMake's cache. After deleting `.xmake/`, restore `deploy.json` to resume
deployment to the same destinations.

Removing a destination leaves its deployed files in place. Keep `.bmk/` while
those files are deployed. If ownership records are lost, remove this project's
previously deployed files or choose an empty destination before deploying again.

## ZIP packages

```sh
xmake package
xmake package OtherModPatch
```

ZIPs contain the same prepared files as deployment, including any BSA/BA2
archives. Versions come from package targets. `package_name` changes the ZIP
name independently of native plugins and game archives.

| Target            | Default ZIP path                                |
| ----------------- | ----------------------------------------------- |
| `MyMod`           | `build/dist/MyMod/MyMod-<version>.zip`          |
| `Skyrim::MyMod`   | `build/dist/Skyrim/MyMod/MyMod-<version>.zip`   |
| `Fallout4::MyMod` | `build/dist/Fallout4/MyMod/MyMod-<version>.zip` |

The default distribution directory follows XMake's build directory. Override it
with `xmake f --distdir=dist`. Changing the distribution directory leaves
earlier output in place.

Packaging replaces a target's ZIP and removes its older versions. Other targets
and unrelated files are preserved. Empty packages produce no ZIP.

Use `set_default(false)` for packages that should build only when selected
explicitly, such as a compatibility patch requiring additional local inputs.
