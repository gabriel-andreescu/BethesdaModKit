# SKSE and F4SE plugins

BMK's native rules build DLLs using CommonLib. See
[runtime requirements and dependency sources](dependencies.md) before choosing a
game target.

## Target configuration

With [BMK configured](building.md#setup), include the native defaults and the
matching CommonLib package:

```lua
includes("@addon/bmk/native")
add_requires("commonlibsse-ng X.Y.Z", {system = false})

target("Native")
    set_default(false)
    set_basename("MyMod")
    set_version("1.2.0")
    add_rules("@commonlibsse-ng/plugin", {author = "Author", description = "My plugin"})
    add_rules("@addon/bmk/skyrim.plugin")
    add_files("src/**.cpp")
    add_packages("commonlibsse-ng")

target("MyMod")
    set_version("1.2.0")
    add_rules("@addon/bmk/skyrim.package", {targets = {"Native"}})
    add_installfiles("assets/(**)")
```

For Fallout 4, use `commonlibf4 2026.09.13`, `@commonlibf4/plugin`,
`@addon/bmk/fallout4.plugin` and `@addon/bmk/fallout4.package`.

The native defaults select x64, `releasedbg`, the dynamic MSVC runtime and
C++23. They enable extra warnings as errors, UTF-8 source encoding and
compilation database generation. Select another mode with `xmake f -m`.

Use `set_warnings("allextra")` on a target to retain extra warnings without
treating them as errors. An explicit `set_languages` also overrides C++23.

Use the same compiler defaults for native test and utility targets:

```lua
add_rules("@addon/bmk/native.compiler")
```

CommonLib's rule generates the DLL's SKSE/F4SE metadata and Windows version
resource from target metadata. Native and package versions are independent. Use
a shared Lua variable when they should match.

`set_basename` sets the DLL filename and the default embedded plugin name. The
CommonLib rule's `name` argument overrides only the embedded name.

Packages include native targets' DLLs and available debug symbols under
`SKSE/Plugins/` or `F4SE/Plugins/`. Building the native target alone does not
deploy or package it.

### Shared native sources

For manually composed multi-game projects, shared code can remain under `src/`,
with game-specific code in `src/Skyrim/` and `src/Fallout4/`:

```lua
target("Native::Skyrim")
    add_files("src/**.cpp|Fallout4/**.cpp")
    add_includedirs("src")

target("Native::Fallout4")
    add_files("src/**.cpp|Skyrim/**.cpp")
    add_includedirs("src")
```

Each target compiles shared files with its own dependencies and definitions. In
included Lua files, use `$(projectdir)/src/...` for paths relative to the
project root.

## Local dependency builds

To build against a local CommonLibSSE-NG, CommonLibF4, CLibUtil or DevBench
checkout, reinstall its package from it with the requires lock disabled. With
the lock enabled, reinstalling one package rewrites `xmake-requires.lock` down
to that package:

```powershell
xmake f -y --policies=package.requires_lock:n
xmake require -f -y --debugdir=C:/path/to/CommonLibSSE-NG "commonlibsse-ng X.Y.Z"
xmake
```

Use the version the project's `xmake.lua` requires. The package builds a copy of
the checkout and leaves it unchanged. The CommonLibSSE-NG copy also receives
BMK's [VR override](dependencies.md#library-sources).

To return to the pinned source, reinstall the package, then enable the lock:

```powershell
xmake require -f -y "commonlibsse-ng X.Y.Z"
xmake f -y --policies=package.requires_lock:y
```

## Settings files

The settings helper requires C++23 and Windows. Add the `bmk` and `clib-util`
header packages to the target. CommonLib provides spdlog:

```lua
add_requires("bmk X.Y.Z", "clib-util X.Y.Z")

target("Native", function()
    add_packages("bmk", "clib-util")
end)
```

Include CommonLib before `BMK/Settings.h` because SimpleIni includes the Windows
API. `BMK/Settings.h` loads the packaged and user INIs, then passes both files
and the supplied initial values to the reader callback. By default, the helper
saves the updated user INI after the reader returns. File errors and reader
exceptions return a failure. A save failure is reported separately so valid
values can still be applied.

The reader callback owns each setting, its validation, and any repair written to
the user INI. Pass CommonLib's default level to `ApplyLogLevel` to apply the
shared debug setting and debugger behavior.

Pass `BMK::Settings::SaveUserFile::kNo` to read settings without saving the user
INI.

```cpp
auto loaded = BMK::Settings::Load(paths, Values {}, ReadValues);
if (!loaded) {
    spdlog::warn("Cannot load settings: {}", loaded.error().message);
    return;
}
if (loaded->saveFailure) {
    spdlog::warn("Cannot save settings: {}", loaded->saveFailure->message);
}
current = std::move(loaded->values);
BMK::Settings::ApplyLogLevel(current.debugLogging, commonLibDefaultLevel);
```
