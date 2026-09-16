import("core.project.config")

function arguments(game, options, data, output)
    local name = assert(options.output, "Synthesis requires an output plugin filename.")
    return table.join({
        "run-patcher",
        "--GameRelease",
        game,
        "--DataFolderPath",
        path.absolute(data),
        "--LoadOrderFilePath",
        path.absolute(assert(options.load_order, "Synthesis requires a load-order file.")),
        "--ModKey",
        name,
        "--OutputPath",
        path.join(output, name),
    }, options.arguments or {})
end

function build(target)
    local settings = target:data("bmk.synthesis")
    local options = settings.options
    local data = options.data
    assert(options.load_order, "Synthesis requires a load-order file.")
    if not data then
        data = path.join(config.builddir(), "intermediates", (target:fullname():gsub("::", "/")), "Data")
        local sources, destinations = target:extrafiles(data)
        local current = {}
        for index, source in ipairs(sources) do
            current[path.absolute(destinations[index]):lower()] = true
            os.cp(source, destinations[index], { copy_if_different = true })
        end
        for _, file in ipairs(os.files(path.join(data, "**"))) do
            if not current[path.absolute(file):lower()] then
                os.rm(file)
            end
        end
    end
    target:add("extrafiles", options.load_order)
    if options.data then
        for _, extension in ipairs({ "esp", "esm", "esl", "strings", "dlstrings", "ilstrings" }) do
            target:add("extrafiles", path.join(data, "**." .. extension))
        end
    end
    local generator = table.copy(options)
    generator.outputs = { "**" }
    import("@self.dotnet").run(target, generator, arguments(settings.game, options, data, "$(outputdir)"))
end
