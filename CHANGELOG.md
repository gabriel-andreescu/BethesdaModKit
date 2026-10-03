# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/).

## [Unreleased]

## [0.6.0] - 2026-10-03

### Added

- The `devbench_wait_timeout` pytest setting sets the `wait_for` fixture's
  default timeout, 30 seconds.

### Changed

- The `wait_for` fixture no longer takes its default timeout from
  `devbench_launch_timeout`.
- Generated projects pin the `bmk` header package to the BMK release,
  `skyrim-papyrus-sdk 2026.09.20` and `caprica 2026.9.17`. The two recipes now
  declare versions, so `xmake require` rejects unknown ones.
- The generated pre-commit configuration no longer restores .NET tools before
  CSharpier runs. Run `dotnet tool restore` once per clone. The build workflow
  restores them before running the hooks.
- Generated C# projects enable implicit usings and nullable reference types in
  `Directory.Build.props` instead of each project file.
- The generated README links the Papyrus page instead of noting the Caprica
  requirement.

## [0.5.0] - 2026-10-02

### Added

- The template generates only tooling configuration for an existing project with
  `tooling_only=true`.
- Generated projects include `.luarc.json`, with XMake declarations for the Lua
  language server from xmake-luals.
- The build workflow installs npm dependencies for each committed
  `package-lock.json` before it runs pre-commit hooks.

### Changed

- Generated projects pin xmake-luals 0.1.1.
- Native targets compile with `/Zc:__cplusplus`, so `__cplusplus` reports the
  selected standard.
- Generated README lists the documentation links and describes CI.
- Generated VS Code settings recommend and configure Prettier, StyLua and the
  Lua language server.
- Generated native projects require `_camelCase` names for private and protected
  members.
- Generated native projects require `kCamelCase` enum constants.
- Generated native projects allow pointer conditions, all-public data structs
  and internal-linkage non-const globals.
- Generated native projects keep comparisons on one line when clang-format wraps
  a logical expression.
- The build workflow builds with XMake from `gabriel-andreescu/xmake` at a
  pinned commit instead of the XMake 3.1.1 release.

### Removed

- **Breaking:** The template no longer asks for the BMK repository, and
  `copier update` switches projects that answered a local directory back to
  GitHub. To build a project against a local checkout, follow
  [Validate package and rule changes](CONTRIBUTING.md#validate-package-and-rule-changes).

### Fixed

- The build workflow keeps separate compilation caches for different
  `configure-arguments`.
- The generated startup test checks the main menu instead of only starting the
  session.
- The build reports which game rule to use when a target uses
  `@addon/bmk/package` on its own.

## [0.4.0] - 2026-09-29

### Added

- BMK provides CommonLibSSE-NG 9.0.0 and 10.0.0 packages.

### Changed

- Generated projects' build workflow is pinned to the BMK release tag.
- Generated C# projects enforce Microsoft's `var` convention and braces on every
  block.

### Fixed

- Generated projects and their build workflow use clang-format 23.1.0.

## [0.3.1] - 2026-09-20

### Fixed

- Nexus changelogs are published under the selected release version.
- Generated editor settings use the project's Ruff executable directly.

## [0.3.0] - 2026-09-20

### Added

- Nexus Mods uploads from package targets, with file categories and release
  changelogs.

## [0.2.0] - 2026-09-20

### Added

- Generated projects include a Nexus description starter and recommend BBCode
  Editor and Preview.
- The `BethesdaModKit.Mutagen` NuGet package creates Skyrim MCM Helper quests
  with Mutagen.
- Native settings helpers load layered INIs and apply log levels.
- A Skyrim DevBench helper registers inspections.
- Native compiler defaults apply to plugins, tests and utilities.
- Pre-commit checks format native project sources with clang-format.
- The Skyrim Papyrus SDK package provides the vanilla interfaces with optional
  SKSE, MCM Helper and powerofthree's Papyrus Extender interfaces.
- Papyrus source packages provide the Skyrim, SKSE and powerofthree's Papyrus
  Extender interfaces.

### Changed

- Generated native projects precompile the CommonLib and script extender
  headers.
- Generated native plugins log source locations and thread IDs, and use
  CommonLib's default log level.

### Fixed

- Generated DevBench test projects require Python 3.11 or newer.
- LLVM's enum range analyzer no longer reports a false positive in MSVC
  filesystem headers.
- Native targets that set no language use the documented C++23 default.
- Clang tooling works for native projects that use precompiled headers.
- New projects generate dependency lockfiles.
- Debug log messages are flushed when debug logging is enabled.

## [0.1.0] - 2026-09-17

### Added

- Initial release.
