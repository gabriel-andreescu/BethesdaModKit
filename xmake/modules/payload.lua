import("core.project.depend")
import("core.project.config")

function collect(target, output)
    local selected = {}
    local function include(source_target)
        local sources, destinations = source_target:installfiles(output)
        for index, source in ipairs(sources) do
            if path.filename(source):lower() ~= ".gitkeep" then
                local destination = path.relative(destinations[index], output)
                selected[destination:lower()] = { source = source, destination = destination }
            end
        end
    end
    for _, name in ipairs(target:data("bmk.package").options.targets or {}) do
        include(assert(target:dep(name), "Unknown package target: " .. name))
    end
    include(target)
    local inputs = table.values(selected)
    table.sort(inputs, function(left, right)
        return left.destination < right.destination
    end)
    return inputs
end

function prepare(target)
    if target:data("bmk.payload") then
        return target:data("bmk.payload")
    end
    local mod = target:data("bmk.package")
    local directory = path.join(config.builddir(), "bmk", (target:fullname():gsub("::", "/")))
    local output = path.join(directory, "payload")
    local inputs = collect(target, output)
    local files, layout = {}, {}
    for _, input in ipairs(inputs) do
        table.insert(files, input.source)
        table.insert(layout, input.destination)
    end
    local implementation = os.files(path.join(os.scriptdir(), "**"))
    table.sort(implementation)
    table.join2(files, implementation)
    depend.on_changed(function()
        local stage = os.tmpfile() .. ".dir"
        os.mkdir(stage)
        try({
            function()
                for _, input in ipairs(inputs) do
                    if path.filename(input.source):lower() ~= ".gitkeep" then
                        os.cp(input.source, path.join(stage, input.destination))
                    end
                end
                local originals = {}
                for _, input in ipairs(inputs) do
                    originals[input.destination:gsub("\\", "/"):lower()] = input.source
                end
                import("@self.archives.archive").pack(stage, mod, target:name(), {
                    directory = path.join(directory, "archives"),
                    sources = originals,
                })
                if os.exists(output) then
                    os.rm(output)
                end
                os.mv(stage, output)
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
        dependfile = path.join(config.directory(), "bmk", target:fullname():gsub("::", "/"), "payload.d"),
        files = files,
        values = { mod.game, target:name(), output, string.serialize(mod.options, { orderkeys = true }), layout },
        changed = not os.isdir(output),
    })
    target:data_set("bmk.payload", output)
    return output
end
