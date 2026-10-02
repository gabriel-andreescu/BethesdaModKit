# Clang tooling

Formatting and diagnostics use the project's `.clang-format`, `.clangd` and
`.clang-tidy` configuration.

## Compilation database

Native plugin rules generate `compile_commands.json` at the project root after a
build, with commands exported for clangd.

## Format

```powershell
clang-format -i src/Plugin.cpp
```

## Run clang-tidy

With LLVM on PATH, run from the native project:

```powershell
xmake check clang.tidy
```

This checks every native source the project builds, in parallel. To check
selected files, pass them with `-f`:

```powershell
xmake check clang.tidy -f src/Plugin.cpp
```
