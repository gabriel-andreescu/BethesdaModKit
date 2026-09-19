# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
