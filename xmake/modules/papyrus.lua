import("core.project.depend")

function arguments(game, options, sources, output)
    local root = path.absolute(assert(options.root, "Papyrus requires a source root."))
    local imports = { root }
    for _, directory in ipairs(options.imports or {}) do
        table.insert(imports, path.absolute(directory))
    end
    local args = table.copy(sources)
    table.join2(args, {
        "--game=" .. game,
        "--ignorecwd",
        "--import=" .. table.concat(imports, ";"),
        "--output=" .. path.absolute(output),
    })
    if options.flags then
        table.insert(args, "--flags=" .. path.absolute(options.flags))
    end
    return table.join(args, options.arguments or {})
end

function build(target)
    local settings = target:data("bmk.papyrus")
    local options = table.copy(settings.options)
    options.imports = table.copy(options.imports or {})
    for _, name in ipairs({ "includedirs", "sysincludedirs" }) do
        for _, directories in ipairs(target:get_from(name, "package::*")) do
            table.join2(options.imports, directories)
        end
    end
    local package = assert(target:pkg("caprica"), "Add the caprica package to the Papyrus target.")
    local compiler = path.join(package:installdir(), "bin", "Caprica.exe")
    local sources = table.copy(target:sourcefiles())
    for index, source in ipairs(sources) do
        sources[index] = path.absolute(source)
    end
    local output = target:targetdir()
    local args = arguments(settings.game, options, sources, output)
    local files = table.join(
        sources,
        { compiler, path.join(os.scriptdir(), "papyrus.lua"), path.join(os.scriptdir(), "generated.lua") },
        os.files(path.join(options.root, "**.psc"))
    )
    if options.flags then
        table.insert(files, options.flags)
    end
    for _, directory in ipairs(options.imports or {}) do
        table.join2(files, os.files(path.join(directory, "**.psc")))
    end
    depend.on_changed(function()
        local stage = os.tmpfile() .. ".dir"
        os.mkdir(stage)
        try({
            function()
                if #sources > 0 then
                    os.vrunv(compiler, arguments(settings.game, options, sources, stage))
                end
                import("@self.generated").publish(stage, output, target:dependfile("papyrus.outputs"))
            end,
            finally({
                function(ok, errors)
                    os.tryrm(stage)
                    if not ok then
                        raise(errors)
                    end
                end,
            }),
        })
    end, {
        dependfile = target:dependfile("papyrus"),
        files = files,
        values = args,
        changed = target:is_rebuilt()
            or import("@self.generated").missing(output, target:dependfile("papyrus.outputs")),
    })
    import("@self.generated").installfiles(
        target,
        output,
        target:dependfile("papyrus.outputs"),
        { "**.pex" },
        "Scripts"
    )
end
