rule("ffdec")
on_load(function(target)
    target:set("kind", "phony")
end)
after_config(function(target)
    import("core.project.config")
    if not target:get("targetdir") then
        target:set("targetdir", path.join(config.builddir(), "artifacts", (target:fullname():gsub("::", "/"))))
    end
    local options = target:extraconf("rules", "@addon/bmk/ffdec") or {}
    local output = assert(options.output, "FFDec requires an output filename.")
    target:add("installfiles", path.join(target:targetdir(), output), { prefixdir = "Interface" })
end)
on_build(function(target)
    import("@self.ffdec").build(target)
end)
