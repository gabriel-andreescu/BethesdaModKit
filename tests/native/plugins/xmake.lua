set_project("TestPlugin")
set_license("GPL-3.0")

option("game", { default = "skyrim", values = { "skyrim", "fallout4" } })
add_repositories("bmk " .. (os.getenv("BMK_TEST_REPOSITORY") or path.join(os.scriptdir(), "../../..")))
add_addons("bmk 0.3.0")
includes("@addon/bmk/project")
includes("@addon/bmk/native")

if is_config("game", "skyrim") then
    add_requires("commonlibsse-ng 8.0.1", {
        configs = {
            skyrim_se = false,
            skyrim_ae = true,
            skyrim_vr = false,
            skse_xbyak = false,
            skse_patch_safety = false,
        },
    })
    add_requires("bmk", "devbench-api 2026.09.13")
else
    add_requires("commonlibf4 2026.09.13")
end

target("TestPlugin", function()
    set_version("0.1.0")
    if is_config("game", "skyrim") then
        add_rules("@commonlibsse-ng/plugin", { author = "Test Author", description = "Plugin package test" })
        add_rules("@addon/bmk/skyrim.plugin")
        add_rules("@devbench-api/integration")
        add_packages("bmk", "commonlibsse-ng", "devbench-api", { external = true })
        add_files("skyrim.cpp")
    else
        add_rules("@commonlibf4/plugin", { author = "Test Author", description = "Plugin package test" })
        add_rules("@addon/bmk/fallout4.plugin")
        add_packages("commonlibf4", { external = true })
        add_files("fallout4.cpp")
    end
end)
