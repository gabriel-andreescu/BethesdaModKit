rule("synthesis")
on_load(function(target)
    target:set("kind", "phony")
end)
after_config(function(target)
    import("core.project.config")
    if not target:get("targetdir") then
        target:set("targetdir", path.join(config.builddir(), "artifacts", (target:fullname():gsub("::", "/"))))
    end
end)
on_build(function(target)
    import("@self.synthesis").build(target)
end)
