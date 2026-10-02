# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/).

## [Unreleased]

### Added

- Generate only tooling configuration for an existing project with
  `tooling_only=true`.
- Add `.luarc.json` to generated projects, with XMake declarations for the Lua
  language server from xmake-luals.
- The build workflow installs npm dependencies for each committed
  `package-lock.json` before it runs pre-commit hooks.

### Changed

- Generated README lists the documentation links and describes CI.
- Generated VS Code settings recommend and configure Prettier, StyLua and the
  Lua language server.
- Require `_camelCase` names for private and protected members in generated
  native projects.
- Require `kCamelCase` enum constants in generated native projects.
- Allow pointer conditions, all-public data structs and internal-linkage
  non-const globals in generated native projects.
- Keep comparisons on one line when clang-format wraps a logical expression in
  generated native projects.
- The build workflow builds with XMake from `gabriel-andreescu/xmake` at a
  pinned commit instead of the XMake 3.1.1 release.

### Removed

- **Breaking:** The template no longer asks for the BMK repository, and
  `copier update` switches projects that answered a local directory back to
  GitHub. To build a project against a local checkout, follow
  [Validate package and rule changes](CONTRIBUTING.md#validate-package-and-rule-changes).

### Fixed

- Report which game rule to use when a target uses `@addon/bmk/package` on its
  own.

## [0.4.0] - 2026-09-29

### Added

- Add CommonLibSSE-NG 9.0.0 and 10.0.0 packages.

### Changed

- Pin generated projects' build workflow to the BMK release tag.
- Enforce Microsoft's `var` convention and braces on every block in generated C#
  projects.

### Fixed

- Use clang-format 23.1.0 in generated projects and their build workflow.

## [0.3.1] - 2026-09-20

### Fixed

- Publish Nexus changelogs under the selected release version.
- Use the project's Ruff executable directly in generated editor settings.

## [0.3.0] - 2026-09-20

### Added

- Nexus Mods uploads from package targets, with file categories and release
  changelogs.

## [0.2.0] - 2026-09-20

### Added

- Add a Nexus description starter and recommend BBCode Editor and Preview.
- Add a NuGet package for creating Skyrim MCM Helper quests with Mutagen.
- Add native settings helpers for layered INI loading and log levels.
- Add a Skyrim DevBench inspection registration helper.
- Add native compiler defaults for plugins, tests, and utilities.
- Format native project sources with clang-format during pre-commit checks.
- Add a Skyrim Papyrus SDK package with optional SKSE, MCM Helper, and
  powerofthree's Papyrus Extender interfaces.
- Add Papyrus source packages for Skyrim, SKSE, and powerofthree's Papyrus
  Extender.

### Changed

- Generate native projects with a precompiled header for CommonLib and the
  script extender.
- Include source locations and thread IDs in generated native plugins' logs, and
  use CommonLib's default log level.

### Fixed

- Require Python 3.11 or newer in generated DevBench test projects.
- Avoid a false positive from LLVM's enum range analyzer in MSVC filesystem
  headers.
- Apply the documented C++23 default when native targets do not set a language.
- Fix Clang tooling for native projects that use precompiled headers.
- Generate dependency lockfiles for new projects.
- Flush debug log messages when debug logging is enabled.

## [0.1.0] - 2026-09-17

### Added

- Initial release.
