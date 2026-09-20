import("utils.archive")
import("core.base.json")
import("core.project.config", { alias = "project_config" })

local function filename(name)
    assert(
        type(name) == "string"
            and name ~= ""
            and name ~= "."
            and name ~= ".."
            and not name:find('[<>:"/\\|?*]')
            and not name:find("[. ]$"),
        "Invalid package filename: " .. tostring(name)
    )
    return name
end

function package(target, payload, config)
    local components = target:fullname():split("::", { plain = true })
    for _, component in ipairs(components) do
        filename(component)
    end
    local dist = path.absolute(project_config.get("distdir") or path.join(project_config.builddir(), "dist"))
    local output = path.join(dist, table.concat(components, "/"))
    local manifest =
        path.join(os.projectdir(), ".xmake/bmk/packages", hash.uuid(target:fullname() .. "\n" .. output) .. ".lua")
    local metadata = path.join(os.projectdir(), ".xmake/bmk/packages", hash.uuid(target:fullname()) .. ".json")
    local previous = os.isfile(manifest) and io.load(manifest) or {}
    local version = assert(target:version(), "Set a version for target " .. target:fullname())
    local name = filename((config.options.package_name or target:name()) .. "-" .. version .. ".zip")
    local destination = path.join(output, name)
    local files = os.files(path.join(payload, "**|.gitkeep|**/.gitkeep"))
    local current = {}
    if #files > 0 then
        assert(not os.isdir(destination), "Package output is a directory: " .. destination)
        assert(
            not os.isfile(destination) or previous[name:lower()],
            "Packaging would overwrite an unowned file: " .. destination
        )
        current[name:lower()] = name
    end
    for index, file in ipairs(files) do
        files[index] = path.relative(file, payload)
    end

    local staging = os.tmpfile() .. ".zip"
    try({
        function()
            if #files > 0 then
                archive.archive(staging, files, { curdir = payload, compress = "best" })
            end
            -- Keep ownership of partial output if replacing an archive fails.
            local pending = table.copy(previous)
            for key, file in pairs(current) do
                pending[key] = file
            end
            io.save(manifest, pending)
            if #files > 0 then
                os.mkdir(output)
                os.mv(staging, destination)
            end
            for key, file in pairs(previous) do
                local obsolete = path.join(output, filename(file))
                if not current[key] and os.isfile(obsolete) then
                    os.rm(obsolete)
                end
            end
            io.save(manifest, current)
            if #files > 0 then
                json.savefile(metadata, {
                    target = target:fullname(),
                    name = config.options.package_name or target:name(),
                    version = version,
                    archive = path.relative(destination, dist):gsub("\\", "/"),
                    game = config.game,
                    nexus = config.options.nexus,
                    changelog = config.options.changelog
                        and path.relative(path.absolute(config.options.changelog), os.projectdir()):gsub("\\", "/"),
                })
            elseif os.isfile(metadata) then
                os.rm(metadata)
            end
        end,
        finally({
            function(ok, errors)
                os.tryrm(staging)
                if not ok then
                    raise(errors)
                end
            end,
        }),
    })
end
