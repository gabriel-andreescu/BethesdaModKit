# Documentation

## Mod authors

Start with [the project template](mod-authors/template/projects.md) for a
generated build setup, or
[use BMK in an existing mod](mod-authors/tooling/building.md) to add individual
build rules or helpers.

### Project template

| Guide                                                 | Covers                                                              |
| ----------------------------------------------------- | ------------------------------------------------------------------- |
| [Projects](mod-authors/template/projects.md)          | Copier options, adding components and updating customized projects. |
| [Template defaults](mod-authors/template/defaults.md) | Generated configuration and component defaults.                     |
| [Settings and MCM](mod-authors/template/settings.md)  | Generated native settings and the optional MCM addon.               |

### Build tools and helpers

| Guide                                                             | Covers                                                            |
| ----------------------------------------------------------------- | ----------------------------------------------------------------- |
| [Use BMK in an existing project](mod-authors/tooling/building.md) | Integrating build rules and helpers without the template.         |
| [SKSE and F4SE plugins](mod-authors/tooling/native-plugins.md)    | CommonLib, DLL metadata and shared sources.                       |
| [Dependencies and runtimes](mod-authors/tooling/dependencies.md)  | Dependency sources, runtime requirements and library adaptations. |
| [Papyrus](mod-authors/tooling/papyrus.md)                         | Caprica, imports and packaged script sources.                     |
| [Scaleform UI](mod-authors/tooling/interface.md)                  | SWF builds with FFDec and ActionScript.                           |
| [C# generators and patchers](mod-authors/tooling/dotnet.md)       | Mutagen and Synthesis projects.                                   |
| [Deployment and packaging](mod-authors/tooling/packaging.md)      | Package contents, local deployment and ZIPs.                      |
| [BSA and BA2 archives](mod-authors/tooling/archives.md)           | File selection, compression and loader plugins.                   |
| [Clang tooling](mod-authors/tooling/clang.md)                     | Compilation databases, formatting and lint commands.              |
| [GitHub Actions](mod-authors/tooling/github-actions.md)           | Mod builds and releases.                                          |
| [Updating](mod-authors/tooling/updating.md)                       | Addon, dependency, Python and workflow updates.                   |
| [Skyrim DevBench](mod-authors/tooling/skyrim/devbench.md)         | Python helpers, pytest fixtures and native API integration.       |

## BMK maintainers

- [Development](maintainers/development.md): environment, formatting and tests.
- [Contributing](../CONTRIBUTING.md): repository layout, dependency maintenance
  and BMK releases.
