rule("package")
on_load(function(target)
    target:set("kind", "phony")
end)
after_load(function(target)
    local package = target:data("bmk.package")
    assert(
        package,
        target:name() .. ": use @addon/bmk/skyrim.package or @addon/bmk/fallout4.package instead of @addon/bmk/package."
    )
    for _, name in ipairs(package.options.targets or {}) do
        target:add("deps", name, { inherit = false })
    end
end)
after_build(function(target)
    import("core.project.config")
    local payload = import("@self.payload").prepare(target)
    if config.get("deploy") then
        import("@self.deployment").deploy(target, payload)
    end
end)
on_package(function(target)
    local payload = import("@self.payload").prepare(target)
    import("@self.packaging").package(target, payload, target:data("bmk.package"))
end)
