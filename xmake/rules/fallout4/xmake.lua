rule("fallout4.package")
add_deps("@self/package")
on_load(function(target)
    target:data_set("bmk.package", {
        game = "fallout4",
        options = target:extraconf("rules", "@addon/bmk/fallout4.package") or {},
    })
end)

rule("fallout4.plugin")
add_deps("@self/plugin")
on_config(function(target)
    target:data_set("bmk.plugin", { plugins = "F4SE/Plugins" })
end)

rule("fallout4.papyrus")
add_deps("@self/papyrus")
on_load(function(target)
    target:data_set("bmk.papyrus", {
        game = "fallout4",
        options = target:extraconf("rules", "@addon/bmk/fallout4.papyrus") or {},
    })
end)

rule("fallout4.synthesis")
add_deps("@self/synthesis")
on_load(function(target)
    target:data_set("bmk.synthesis", {
        game = "Fallout4",
        options = target:extraconf("rules", "@addon/bmk/fallout4.synthesis") or {},
    })
end)
