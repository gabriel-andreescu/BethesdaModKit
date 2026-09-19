# Contributing

See [Development](docs/maintainers/development.md) for the Python environment,
formatting and tests.

## Repository layout

| Directory    | Responsibility                                               |
| ------------ | ------------------------------------------------------------ |
| `templates/` | Copier project files.                                        |
| `xmake/`     | Addon rules, deployment and packaging.                       |
| `addons/`    | Addon distribution recipes.                                  |
| `packages/`  | Library and API recipes, patches and package-specific rules. |
| `native/`    | C++ helpers.                                                 |
| `dotnet/`    | .NET helper packages.                                        |
| `python/`    | Python helpers and pytest integration.                       |

Game-specific behavior belongs under its game directory.

Template documentation belongs in `docs/mod-authors/template/` and links to the
independent rule and helper references in `docs/mod-authors/tooling/`.
Contributor setup and checks belong in `docs/maintainers/`.

## .NET package maintenance

`BethesdaModKit.Mutagen` uses the same version as the BMK Python package. Build
and inspect it before release:

```powershell
dotnet pack dotnet/BethesdaModKit.Mutagen/BethesdaModKit.Mutagen.csproj -c Release -o build/nuget
```

Release tags publish the package to NuGet.org through the `ci.yml` trusted
publishing job. Configure its NuGet.org policy for this repository and workflow,
then set the `NUGET_USER` repository secret to the NuGet.org profile name.

## Package maintenance

Update source revisions, package versions and archive hashes together. Review
patches against the new source before retaining them. Preserve upstream license
and exception files in the installed package.

### CommonLibSSE-NG

The [package definition](packages/c/commonlibsse-ng/xmake.lua) also pins OpenVR.
Update that revision alongside CommonLib.

| Patch                                                                             | Purpose                                                  |
| --------------------------------------------------------------------------------- | -------------------------------------------------------- |
| [vr-form-factory.patch](packages/c/commonlibsse-ng/patches/vr-form-factory.patch) | Correct the VR form-factory initialization flag address. |

[rules/plugin.lua](packages/c/commonlibsse-ng/rules/plugin.lua) adapts metadata
generation for installed-package consumers using the unchanged upstream
templates. Compare it with upstream's `commonlib.plugin` and
`commonlibsse-ng.plugin` rules when updating metadata options or template
variables.

Keep the package's exported runtime definitions aligned with its build
configuration.

### CommonLibF4

In the [package definition](packages/c/commonlibf4/xmake.lua), match the
`commonlib-shared` resource to the submodule revision in the selected
CommonLibF4 commit. The package builds both libraries with upstream's XMake
project.

Keep dependencies, feature definitions and public compiler flags aligned with
`commonlib-shared/xmake.lua`. The `ini`, `json`, `toml`, `xbyak` and `random`
package configurations map to its `commonlib_*` options.

Compare [rules/plugin.lua](packages/c/commonlibf4/rules/plugin.lua) with
upstream's `commonlibf4.plugin` and `commonlib.plugin` rules. BMK defaults the
embedded plugin name to the target's basename in both CommonLib adapters.

### Caprica

The [package definition](packages/c/caprica/xmake.lua) downloads Windows x64
binaries from
[gabriel-andreescu/Caprica releases](https://github.com/gabriel-andreescu/Caprica/releases).
Update the release version, ZIP checksum and compiler-options link in
[Papyrus](docs/mod-authors/tooling/papyrus.md) together. Preserve the archive's
license notices in the installed package.

## Validate package and rule changes

Reinstall the changed package in a
[consumer project](docs/mod-authors/tooling/building.md), then build and package
it. For changes to the shared BMK rules, register the local checkout as the
consumer's `bmk` repository and install it with XMake's `--debugdir` option:

```powershell
$env:XMAKE_GLOBALDIR = Join-Path $PWD ".xmake/development"
xmake repo --add --global bmk C:/path/to/BethesdaModKit
xrepo install --addon -y --debugdir=C:/path/to/BethesdaModKit "bmk 0.2.0"
xmake
xmake package
```

Keep that global directory for the development session. The source override
installs uncommitted code under the requested version, so it belongs in an
isolated development cache. Consumer builds install the tagged source instead.

Check generated plugin metadata, deployed files and archive contents as
appropriate to the change. Run the
[tests](docs/maintainers/development.md#tests) when changing the generator or
packaging rules.

## CI and releases

[CI](.github/workflows/ci.yml) runs the development checks. Native consumers
build with MSVC and clang-cl when their dependencies, build rules, headers or
test setup change, and on tags or manual runs.

Keep the XMake version in the CI and consumer workflows aligned with
[the development setup](docs/maintainers/development.md#xmake).

For BMK releases, update `python/pyproject.toml`, the
`BethesdaModKit.Mutagen.csproj` package version, `uv.lock` and the dated
changelog entry. Update the template and documentation PackageReference pins.
Add the release to `addons/b/bmk/xmake.lua` and update the `add_addons` version
in the template, examples and test consumers. Keep existing recipe versions so
consumers can continue installing older releases.

Publish a matching `vX.Y.Z` tag. The addon downloads that tag, and CI publishes
the source release after checks pass. Do not move published release tags.

BMK and [mod releases](docs/mod-authors/tooling/github-actions.md) share
[release.yml](.github/workflows/release.yml), which extracts notes with
[Changelog Reader](https://github.com/mindsers/changelog-reader-action).
