rule("skyrim.package")
add_deps("@self/package")
on_load(function(target)
    target:data_set("bmk.package", {
        game = "skyrim",
        options = target:extraconf("rules", "@addon/bmk/skyrim.package") or {},
    })
end)

rule("skyrim.plugin")
add_deps("@self/plugin")
on_config(function(target)
    target:data_set("bmk.plugin", { plugins = "SKSE/Plugins" })
end)

rule("skyrim.papyrus")
add_deps("@self/papyrus")
on_load(function(target)
    target:data_set("bmk.papyrus", {
        game = "skyrim",
        options = target:extraconf("rules", "@addon/bmk/skyrim.papyrus") or {},
    })
end)

rule("skyrim.synthesis")
add_deps("@self/synthesis")
on_load(function(target)
    target:data_set("bmk.synthesis", {
        game = "SkyrimSE",
        options = target:extraconf("rules", "@addon/bmk/skyrim.synthesis") or {},
    })
end)
