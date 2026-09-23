package("commonlibsse-ng")
set_homepage("https://github.com/alandtse/CommonLibSSE-NG")
set_description("CommonLibSSE-NG for Skyrim SKSE plugins")
set_license("GPL-3.0")
add_urls("https://github.com/gabriel-andreescu/CommonLibSSE-NG/archive/$(version).tar.gz", {
    version = function(version)
        local revisions = {
            ["8.0.1"] = "b3bec7424238c9fee2623f145e2714e7558f18d4",
            ["9.0.0"] = "e04a2f09fbd6df65ecd24a1abf3e6580fda60411",
        }
        return revisions[tostring(version)]
    end,
})
add_versions("8.0.1", "34162b1feaacd66a617e913f3bcf3320722ad9b8728be5c8d3f1c8bbcb07e39c")
add_versions("9.0.0", "406df41ff3c6cd9bc3eb5bb8c5f68e3f4159798452d3b7f3335a23dab8231afd")
add_patches(
    ">=8.0.1",
    path.join(os.scriptdir(), "patches", "vr-form-factory.patch"),
    "d16641d4e41f7a58d8c978fc1d23293b980ee1e9a9ea704a7c008fa301693260"
)
for _, runtime in ipairs({ "skyrim_se", "skyrim_ae", "skyrim_vr" }) do
    add_configs(runtime, { description = "Enable " .. runtime, default = true, type = "boolean" })
end
add_configs("skse_xbyak", { description = "Enable Xbyak support", default = true, type = "boolean" })
add_configs("skse_patch_safety", { description = "Enable patch safety", default = true, type = "boolean" })
add_deps("directxmath 2024.02", "directxtk 24.2.0")
add_deps("spdlog v1.16.0", { configs = { header_only = false, wchar = true, std_format = true } })
add_syslinks("advapi32", "bcrypt", "d3d11", "d3dcompiler", "dbghelp", "dxgi", "ole32", "shell32", "user32", "version")
add_links("commonlibsse-ng")
on_load(function(package)
    if package:config("skse_xbyak") then
        package:add("deps", "xbyak v7.06")
    end
    if package:config("skyrim_vr") then
        package:add("deps", "rapidcsv v8.92")
        package:add(
            "resources",
            ">=8.0.1",
            "openvr",
            "https://github.com/ValveSoftware/openvr/archive/60eb187801956ad277f1cae6680e3a410ee0873b.zip",
            "51b4deef78c10f52e3e41d85bab51a87a55cd4d87b4d6c65c8952c2cbfafb9ae"
        )
        package:add("includedirs", "include/openvr")
    end
    local runtimes = 0
    for _, runtime in ipairs({ "skyrim_se", "skyrim_ae", "skyrim_vr" }) do
        if package:config(runtime) then
            package:add("defines", "ENABLE_" .. runtime:upper() .. "=1")
            runtimes = runtimes + 1
        end
    end
    if runtimes > 1 then
        package:add("defines", "HAS_SKYRIM_MULTI_TARGETING=1")
    end
    if package:config("skse_xbyak") then
        package:add("defines", "SKSE_SUPPORT_XBYAK=1")
    end
    if package:config("skse_patch_safety") then
        package:add("defines", "SKSE_SUPPORT_PATCH_SAFETY=1")
    end
    package:add("includedirs", "include")
end)
on_install("windows|x64", function(package)
    local openvr
    if package:config("skyrim_vr") then
        openvr = path.join(package:resourcedir("openvr"), "openvr-60eb187801956ad277f1cae6680e3a410ee0873b")
        os.cp(path.join(openvr, "headers"), "extern/openvr/headers")
    end
    import("package.tools.xmake").install(package, {
        mode = package:is_debug() and "debug" or "releasedbg",
        skyrim_se = package:config("skyrim_se"),
        skyrim_ae = package:config("skyrim_ae"),
        skyrim_vr = package:config("skyrim_vr"),
        skse_xbyak = package:config("skse_xbyak"),
        skse_patch_safety = package:config("skse_patch_safety"),
        tests = false,
    })
    if package:config("skyrim_vr") then
        os.cp("extern/openvr/headers/*.h", package:installdir("include/openvr"))
        os.cp(path.join(openvr, "LICENSE"), path.join(package:installdir("share/licenses"), "openvr.txt"))
    end
    os.cp("res/commonlib-plugin.rc.in", package:installdir("share"))
    os.cp("res/commonlibsse-ng-plugin.cpp.in", package:installdir("share"))
    os.cp("COPYING.txt", package:installdir("share"))
    os.cp("EXCEPTIONS.md", package:installdir("share"))
    os.cp("licenses/*", package:installdir("share/licenses"))
    os.cp(path.join(package:scriptdir(), "licenses"), package:installdir())
end)
