# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Add native compiler defaults for plugins, tests, and utilities.
- Format native project sources with clang-format during pre-commit checks.
- Add a Skyrim Papyrus SDK package with optional SKSE, MCM Helper, and
  powerofthree's Papyrus Extender interfaces.
- Add Papyrus source packages for Skyrim, SKSE, and powerofthree's Papyrus
  Extender.

### Changed

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
