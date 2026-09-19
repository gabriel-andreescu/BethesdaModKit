package("skyrim-papyrus-sdk", function()
    set_kind("library", { headeronly = true })
    set_description("Skyrim Papyrus SDK interfaces")

    add_configs("skse", { description = "Include SKSE interfaces", default = false, type = "boolean" })
    add_configs("mcm", { description = "Include MCM Helper interfaces", default = false, type = "boolean" })
    add_configs("papyrus_extender", {
        description = "Include powerofthree's Papyrus Extender interfaces",
        default = false,
        type = "boolean",
    })

    on_load(function(package)
        if package:config("mcm") then
            package:add("deps", "mcm-helper-sdk 1.6.3")
        end
        if package:config("papyrus_extender") then
            package:add("deps", "papyrus-extender-sse-sources 81e4c6b7")
        end
        if package:config("skse") then
            package:add("deps", "skse-papyrus-sources 2.0.20")
        end
        package:add("deps", "skyrim-papyrus-sources ec822650")
    end)

    on_install(function() end)
end)
