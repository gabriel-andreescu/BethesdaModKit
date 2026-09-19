# Updating tools and dependencies

| Part                     | Update                                                                | Recorded in                                    |
| ------------------------ | --------------------------------------------------------------------- | ---------------------------------------------- |
| Generated project files  | `copier update`                                                       | `.copier-answers.yml` and the generated files. |
| XMake dependency recipes | `xmake repo --update`                                                 | Local repository checkouts.                    |
| BMK build rules          | Change the `add_addons` version, then configure                       | `xmake.lua` and `xmake-addons.lock`.           |
| XMake dependencies       | `xmake require --upgrade`                                             | `xmake-requires.lock`.                         |
| NuGet helpers            | Change the `PackageReference` version, then `dotnet restore`          | The consuming `.csproj`.                       |
| Python helpers           | `uv lock --upgrade-package bethesda-mod-kit`, then `uv sync --locked` | `uv.lock`.                                     |
| GitHub build workflow    | Change the `uses` revision in the caller                              | `.github/workflows/build.yml`.                 |

Keep `.copier-answers.yml`, `xmake-requires.lock`, `xmake-addons.lock` and
`uv.lock` in Git when the project uses them. Copier merges project files. It
does not reinstall build tools or update Python's environment.

## BMK addon

Select the BMK release in `xmake.lua`:

```lua
add_addons("bmk 0.1.0")
```

The recipe installs the corresponding Git tag. XMake records the selected
version in `xmake-addons.lock` and keeps different versions side by side.

To upgrade, update the repository recipes, change the `add_addons` version and
configure again:

```sh
xmake repo --update
xmake f -y
xmake package
```

For a version range, `xmake addon --upgrade` resolves it again and updates the
lockfile. An exact version remains fixed until its declaration changes.

## Library and compiler packages

`xmake-requires.lock` records resolved package versions, configurations and
repository revisions. Change an explicit `add_requires` version before asking
XMake to resolve a newer version. `xmake require --upgrade` resolves within the
project's current declarations.

BMK recipes can change their pinned source without changing the library's
version label. When adopting such a recipe change, reinstall the affected
package, for example:

```sh
xmake require --upgrade -f -y clib-util
```

Review the lockfile changes and rebuild the affected targets before publishing
the mod. The [dependency reference](dependencies.md) identifies BMK's library
sources and adaptations.

## Workflow revision

Use the BMK commit selected for the project in the reusable workflow's `uses`
reference. This selects CI's build steps, independently of the addon and
dependency installations. See
[workflow setup](github-actions.md#workflow-setup).
