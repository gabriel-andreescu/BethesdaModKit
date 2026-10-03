# Updating tools and dependencies

| Part                       | Update                                                                | Recorded in                                    |
| -------------------------- | --------------------------------------------------------------------- | ---------------------------------------------- |
| Generated project files    | `copier update`                                                       | `.copier-answers.yml` and the generated files. |
| XMake dependency recipes   | `xmake repo --update`                                                 | Local repository checkouts.                    |
| BMK and xmake-luals addons | Change the `add_addons` version, then configure                       | `xmake.lua` and `xmake-addons.lock`.           |
| XMake dependencies         | `xmake require --upgrade`                                             | `xmake-requires.lock`.                         |
| NuGet helpers              | Change the `PackageReference` version, then `dotnet restore`          | The consuming `.csproj`.                       |
| Python helpers             | `uv lock --upgrade-package bethesda-mod-kit`, then `uv sync --locked` | `uv.lock`.                                     |
| Build workflow             | Change the `uses` release tag in the caller                           | `.github/workflows/build.yml`.                 |

Keep `.copier-answers.yml`, `xmake-requires.lock`, `xmake-addons.lock` and
`uv.lock` in Git when the project uses them. Copier merges project files. It
does not reinstall build tools or update Python's environment.

The same update command applies to tooling-only projects. Copier merges shared
configuration changes with project-specific settings and hooks.

## BMK addon

Select the BMK release in `xmake.lua`:

```lua
add_addons("bmk X.Y.Z")
```

The recipe installs the corresponding Git tag. XMake records the selected
version in `xmake-addons.lock` and keeps different versions side by side.

To upgrade, update the repository recipes, change the `add_addons` version and
configure again:

```powershell
xmake repo --update
xmake f -y
xmake package
```

For a version range, `xmake addon --upgrade` resolves it again and updates the
lockfile. An exact version remains fixed until its declaration changes.

To build against a local BMK checkout, follow the
[consumer setup](../../../CONTRIBUTING.md#validate-package-and-rule-changes).

## Library and compiler packages

`xmake-requires.lock` records resolved package versions, configurations and
repository revisions. Change an explicit `add_requires` version before asking
XMake to resolve a newer version. `xmake require --upgrade` resolves within the
project's current declarations.

BMK recipes can change their pinned source without changing the library's
version label. To adopt such a recipe change, reinstall the affected package
with the requires lock disabled, then configure from scratch so the lock records
the new recipe revision:

```powershell
xmake repo --update
xmake f -y --policies=package.requires_lock:n
xmake require -f -y "clib-util X.Y.Z"
xmake f -c -y
```

With the lock enabled, reinstalling one package rewrites `xmake-requires.lock`
down to that package. To build against a local checkout of a dependency, see
[local dependency builds](native-plugins.md#local-dependency-builds).

Review the lockfile changes and rebuild the affected targets before publishing
the mod. The [dependency reference](dependencies.md) identifies BMK's library
sources and adaptations.

## Workflow release

Use the BMK release selected for the project in the reusable workflow's `uses`
reference. This selects CI's build steps, independently of the addon and
dependency installations. Copier updates that tag for generated projects. See
[workflow setup](github-actions.md#workflow-setup).
