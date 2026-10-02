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

Build and package a [consumer project](docs/mod-authors/tooling/building.md)
with the changes. Install the local checkout as the consumer's addon with
XMake's `--debugdir` option in an isolated global directory, and register it as
the consumer's package repository:

```powershell
$env:XMAKE_GLOBALDIR = Join-Path $PWD ".xmake/development"
xmake repo --add --global bmk C:/path/to/BethesdaModKit
xrepo install --addon -y --debugdir=C:/path/to/BethesdaModKit "bmk X.Y.Z"
xmake repo --add bmk C:/path/to/BethesdaModKit
xmake f -y --policies=package.requires_lock:n
xmake
xmake package
```

Keep that global directory for the development session. The source override
installs uncommitted code under the requested version, so it belongs in an
isolated development cache. Consumer builds install the tagged source instead.
The project's repository takes precedence over the one in `xmake.lua`, so
recipes also come from the checkout. Disabling the requires lock keeps
`xmake-requires.lock` from pinning or recording it. Reinstall the addon after
rule changes, and a package after recipe changes with
`xmake require -f -y <package>`.

XMake records the checkout in `xmake-addons.lock` when the lock has no entry for
the requested version. Don't commit that lock. Once the version is released,
return the consumer to it from a new shell:

```powershell
xmake repo --remove bmk
Remove-Item xmake-addons.lock
xmake f -c -y
```

Pack a changed `BethesdaModKit.Mutagen` with a unique prerelease suffix, so it
never shares a version with a release or an earlier local pack that NuGet has
cached:

```powershell
dotnet pack dotnet/BethesdaModKit.Mutagen/BethesdaModKit.Mutagen.csproj -c Release -o build/nuget --version-suffix "dev.$(Get-Date -Format yyyyMMddHHmmss)"
```

Add `build/nuget` as a NuGet source in the consumer and reference the packed
version.

Check generated plugin metadata, deployed files and archive contents as
appropriate to the change. Run the
[tests](docs/maintainers/development.md#tests) when changing the generator or
packaging rules.

## CI and releases

Unreleased work lands on `dev`. `main` tracks the latest release.

[CI](.github/workflows/ci.yml) runs the development checks. Native consumers
build with MSVC and clang-cl when their dependencies, build rules, headers or
test setup change, and on tags or manual runs.

Keep the XMake version in the CI and consumer workflows aligned with
[the development setup](docs/maintainers/development.md#xmake).

For BMK releases, update `python/pyproject.toml`, the `VersionPrefix` in
`BethesdaModKit.Mutagen.csproj`, `uv.lock`, `bmk_version` in `copier.yml` and
the dated changelog entry. Add the release to `addons/b/bmk/xmake.lua` and
update the `add_addons` version in `tests/native/plugins/xmake.lua`. The
template's `add_addons` version, PackageReference pin and build workflow tag
follow `bmk_version`, and CI fails when the package version, `bmk_version` and
the recipe disagree. Keep existing recipe versions so consumers can continue
installing older releases.

Merge `dev` into `main` through a pull request without squashing, then publish a
matching lightweight `vX.Y.Z` tag on `main` with `git tag vX.Y.Z`. Workflows
calling `build.yml` by an annotated tag cannot find its nested release workflow,
so CI rejects annotated release tags. The addon downloads that tag, and CI
publishes the source release after checks pass. Do not move published release
tags.

BMK and [mod releases](docs/mod-authors/tooling/github-actions.md) share
[release.yml](.github/workflows/release.yml), which extracts notes with
[Changelog Reader](https://github.com/mindsers/changelog-reader-action).
