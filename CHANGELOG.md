# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Format native project sources with clang-format during pre-commit checks.
- Add Papyrus source packages for Skyrim, SKSE, and powerofthree's Papyrus
  Extender.

### Changed

- Include source locations and thread IDs in generated native plugins' logs, and
  use CommonLib's default log level.

### Fixed

- Apply the documented C++23 default when native targets do not set a language.
- Generate dependency lockfiles for new projects.
- Flush debug log messages when debug logging is enabled.

## [0.1.0] - 2026-09-17

### Added

- Initial release.
