# GitHub Actions

BMK's reusable [build workflow](../../../.github/workflows/build.yml) builds
`releasedbg` packages and uploads the targets' ZIPs as Actions artifacts. Tag
pushes also publish a GitHub release.

## Workflow setup

Add `.github/workflows/build.yml`:

```yaml
name: Build and release

on:
  push:
    branches: [main]
    tags: ["v[0-9]*", "[0-9]*"]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    permissions:
      contents: write
    uses: gabriel-andreescu/BethesdaModKit/.github/workflows/build.yml@5321e7e3bbb05565a1d0334a88a32152b1445eaf
```

| Input                 | Default      | Purpose                                                            |
| --------------------- | ------------ | ------------------------------------------------------------------ |
| `project-directory`   | `.`          | Directory containing the project's `xmake.lua` and `CHANGELOG.md`. |
| `run-tests`           | `false`      | Run `xmake test` before packaging.                                 |
| `dist-directory`      | `build/dist` | ZIP output directory relative to the project.                      |
| `configure-arguments` | Empty        | Additional XMake configure arguments, one per line.                |

Builds use Windows, MSVC and XMake 3.1.1. Deployment is disabled.

Select the BMK revision used by the project. See [updating](updating.md) for the
separate workflow, addon and dependency pins.

If the repository has a root `.pre-commit-config.yaml`, the workflow runs its
checks before building.

The workflow caches XMake, dependency downloads, installed packages and
compilation results between runs.

For C# projects, `global.json` selects the SDK and NuGet packages are cached.
Supply script sources and patcher inputs through the project's dependencies and
configuration. Pass project-specific XMake options through
`configure-arguments`.

On MSVC targets outside BMK's plugin rules, use `set_symbols("debug", "embed")`
so cached objects retain their debug information.

## Releases

Push an `X.Y.Z` or `vX.Y.Z` tag matching a dated `## [X.Y.Z] - YYYY-MM-DD` entry
in `CHANGELOG.md`. The workflow attaches all built ZIPs and uses that entry as
the release notes. Individual targets retain their declared package versions.

Actions artifacts retain the target folders, including
[namespace directories](packaging.md#zip-packages). In GitHub releases,
duplicate ZIP filenames receive the target path as a prefix, with directory
separators replaced by hyphens. The target name is omitted from the prefix when
the ZIP already starts with `<target>-`. For example,
`Skyrim/MyMod/MyMod-1.0.0.zip` becomes `Skyrim-MyMod-1.0.0.zip`, while
`Skyrim/MyMod/Alternate-1.0.0.zip` becomes `Skyrim-MyMod-Alternate-1.0.0.zip`.
Unique ZIP filenames remain unchanged.

Missing, empty or undated entries block publication. Existing releases are not
overwritten.

### Target changelogs

Targets use the root release entry unless they declare a separate changelog:

```lua
target("Skyrim::MyMod::HighResolutionTextures")
    set_version("1.1.0")
    add_rules("@addon/bmk/skyrim.package", {
        changelog = "assets/optional/HighResolutionTextures/CHANGELOG.md"
    })
    add_installfiles("assets/optional/HighResolutionTextures/Data/(**)")
```

The declared changelog supplies the entry matching the target version. Paths are
relative to the project root. Keep changelogs outside the paths selected by
`add_installfiles` unless they should also ship in the ZIP.

The release body starts with the root entry selected by the tag, followed by the
target entries under package-name and version headings. Targets sharing a
changelog entry share one section. A missing target entry blocks publication.
