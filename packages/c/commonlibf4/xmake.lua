package("commonlibf4")
set_homepage("https://github.com/libxse/commonlibf4")
set_description("CommonLibF4 for Fallout 4 F4SE plugins")
set_license("GPL-3.0")
add_urls("https://github.com/libxse/commonlibf4/archive/8e645d4a5b556701fd6936df99e40aa1d783600d.tar.gz")
add_versions("2026.09.13", "c9f233abbf76d1aaeea5612ecbf5b0cdae73d06978598c37dedaf34a916d5270")
add_resources(
    "2026.09.13",
    "commonlib-shared",
    "https://github.com/libxse/commonlib-shared/archive/29fbdb0e2dc548c9ab22f6964981d75090dc9094.tar.gz",
    "03b50bfb92c9e5fe0ec4fa0ba751883fe14ec3222b2cf56e89d27dce27c33fd3"
)
for _, feature in ipairs({ "ini", "json", "toml", "xbyak", "random" }) do
    add_configs(
        feature,
        { description = "Enable commonlib-shared " .. feature .. " support", default = false, type = "boolean" }
    )
end
add_deps("spdlog v1.16.0", { configs = { header_only = false, wchar = true, std_format = true } })
add_links("commonlibf4", "commonlib-shared")
add_syslinks(
    "advapi32",
    "bcrypt",
    "d3d11",
    "d3dcompiler",
    "dbghelp",
    "dxgi",
    "ole32",
    "shell32",
    "user32",
    "version",
    "ws2_32"
)
on_load(function(package)
    for feature, dependency in pairs({
        ini = "simpleini v4.25",
        json = "glaze v7.0.0",
        toml = "toml11 v4.4.0",
        xbyak = "xbyak v7.06",
        random = "xoshiro-cpp 2021.08.04",
    }) do
        if package:config(feature) then
            package:add("deps", dependency)
            package:add("defines", "COMMONLIB_OPTION_" .. feature:upper() .. "=1")
        end
    end
    package:add("cxxflags", "/EHsc", "/permissive-")
    if package:has_tool("cxx", "cl") then
        package:add(
            "cxxflags",
            "/bigobj",
            "/cgthreads8",
            "/diagnostics:caret",
            "/external:W0",
            "/fp:contract",
            "/fp:except-",
            "/guard:cf-",
            "/Zc:enumTypes",
            "/Zc:preprocessor",
            "/Zc:templateScope",
            "/wd4200",
            "/wd4201",
            "/wd4324",
            "/we4715"
        )
    elseif package:has_tool("cxx", "clang_cl") then
        package:add(
            "cxxflags",
            "-fms-compatibility",
            "-fms-extensions",
            "-Wno-delete-non-abstract-non-virtual-dtor",
            "-Wno-deprecated-volatile",
            "-Wno-ignored-qualifiers",
            "-Wno-inconsistent-missing-override",
            "-Wno-invalid-offsetof",
            "-Wno-microsoft-include",
            "-Wno-overloaded-virtual",
            "-Wno-pragma-system-header-outside-header",
            "-Wno-reinterpret-base-class",
            "-Wno-switch",
            "-Wno-unused-local-typedef",
            "-Wno-unused-private-field"
        )
    end
end)
on_install("windows|x64", function(package)
    local shared =
        path.join(package:resourcedir("commonlib-shared"), "commonlib-shared-29fbdb0e2dc548c9ab22f6964981d75090dc9094")
    os.mkdir("lib/commonlib-shared")
    os.cp(path.join(shared, "*"), "lib/commonlib-shared")
    local configs = { mode = package:is_debug() and "debug" or "releasedbg" }
    for _, feature in ipairs({ "ini", "json", "toml", "xbyak", "random" }) do
        configs["commonlib_" .. feature] = package:config(feature)
    end
    import("package.tools.xmake").install(package, configs, { targets = { "commonlibf4", "commonlib-shared" } })
    os.cp("res/commonlibf4-plugin.cpp.in", package:installdir("share"))
    os.cp("lib/commonlib-shared/res/commonlib-plugin.rc.in", package:installdir("share"))
    os.cp("LICENSE", package:installdir("share/licenses/commonlibf4"))
    os.cp("EXCEPTIONS", package:installdir("share/licenses/commonlibf4"))
    os.cp("res/license/MIT", package:installdir("share/licenses/commonlibf4"))
    os.cp("lib/commonlib-shared/LICENSE", package:installdir("share/licenses/commonlib-shared"))
    os.cp("lib/commonlib-shared/EXCEPTIONS", package:installdir("share/licenses/commonlib-shared"))
    os.cp(path.join(package:scriptdir(), "licenses"), package:installdir())
end)
