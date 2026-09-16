-- BSArch silently skips these extensions even when explicitly selected.
local skipped_extensions = {
    ".bsa",
    ".ba2",
    ".esm",
    ".esp",
    ".esl",
    ".nam",
    ".sdp",
    ".cdx",
    ".csg",
    ".override",
    ".ghost",
    ".exe",
    ".dll",
    ".pdb",
    ".bak",
    ".db",
    ".psd",
    ".jpg",
    ".jpeg",
    ".3ds",
    ".max",
    ".blend",
    ".obj",
    ".xlsx",
    ".docx",
    ".7z",
    ".zip",
    ".rar",
    ".tmp",
}

local function loader_owner(stage, options, name)
    local plugins = {}
    for _, file in ipairs(os.files(path.join(stage, "*"))) do
        if table.contains({ ".esp", ".esm", ".esl" }, path.extension(file):lower()) then
            table.insert(plugins, path.filename(file))
        end
    end
    if options.plugin then
        for _, plugin in ipairs(plugins) do
            if plugin:lower() == options.plugin:lower() then
                return path.basename(plugin), false
            end
        end
        raise("Archive plugin is not present in the payload: %s", options.plugin)
    end
    for _, plugin in ipairs(plugins) do
        if path.basename(plugin):lower() == name:lower() then
            return path.basename(plugin), false
        end
    end
    assert(#plugins <= 1, "Multiple plugins in the payload. Set the archive 'plugin' option.")
    if #plugins == 1 then
        return path.basename(plugins[1]), false
    end
    return name, true
end

function pack(stage, config, name, cache)
    local game = import("@self.archives." .. config.game .. ".settings").get()
    local resources = path.join(os.scriptdir(), "resources")
    local settings = config.options[game.extension:sub(2)]
    if not settings then
        return
    end
    assert(settings == true or type(settings) == "table", "Archive options must be true or a table.")
    local options = settings == true and {} or settings
    if options.root then
        local relative = path.relative(path.absolute(options.root, stage), path.absolute(stage)):gsub("\\", "/")
        assert(
            not path.is_absolute(options.root) and relative ~= ".." and not relative:startswith("../"),
            "Archive root must stay inside the package."
        )
        stage = path.join(stage, options.root)
    end
    local selected = {}
    if options.files ~= nil then
        assert(type(options.files) == "table", "Archive 'files' must be a list of patterns relative to Data.")
        for _, pattern in ipairs(options.files) do
            assert(
                not path.is_absolute(pattern) and not pattern:gsub("\\", "/"):find("%.%./"),
                "Archive patterns must stay inside Data."
            )
            for _, file in ipairs(os.files(path.join(stage, pattern))) do
                selected[path.relative(file, stage):gsub("\\", "/"):lower()] = true
            end
        end
    end
    local groups = { main = {}, textures = {} }
    for _, file in ipairs(os.files(path.join(stage, "**"))) do
        local relative = path.relative(file, stage)
        local key = relative:gsub("\\", "/"):lower()
        local include = options.files ~= nil and selected[key]
            or (options.files == nil and import("@self.archives.selection").selected(relative, game))
        if include and path.filename(key) ~= ".gitkeep" then
            assert(
                not table.contains(skipped_extensions, path.extension(key)),
                "BSArch cannot pack selected file: " .. relative
            )
            assert(key:find("/", 1, true), "Archive files must have a directory: " .. relative)
            local texture = game.texture(key)
            table.insert(texture and groups.textures or groups.main, relative)
        end
    end
    if #groups.main + #groups.textures == 0 then
        return
    end

    local owner, create_loader = loader_owner(stage, options, name)
    if cache then
        import("core.project.depend")
        local files, layout, occupied = {}, {}, {}
        for _, relative in ipairs(table.join(groups.main, groups.textures)) do
            local key = (options.root and path.join(options.root, relative) or relative):gsub("\\", "/"):lower()
            table.insert(files, cache.sources[key])
            table.insert(layout, relative)
        end
        for _, file in ipairs(os.files(path.join(stage, "*"))) do
            if table.contains({ ".esp", ".esm", ".esl", ".bsa", ".ba2" }, path.extension(file):lower()) then
                table.insert(occupied, path.filename(file):lower())
            end
        end
        table.sort(occupied)
        table.sort(layout)
        local generated = path.join(cache.directory, "output")
        depend.on_changed(function()
            local work = os.tmpfile() .. ".dir"
            os.mkdir(work)
            try({
                function()
                    for _, relative in ipairs(layout) do
                        os.cp(path.join(stage, relative), path.join(work, relative))
                    end
                    for _, filename in ipairs(occupied) do
                        os.cp(path.join(stage, filename), path.join(work, filename))
                    end
                    local nested = { game = config.game, options = table.copy(config.options) }
                    local key = game.extension:sub(2)
                    nested.options[key] = table.copy(options)
                    nested.options[key].root = nil
                    pack(work, nested, name)
                    for _, filename in ipairs(occupied) do
                        os.tryrm(path.join(work, filename))
                    end
                    if os.isdir(generated) then
                        os.rm(generated)
                    end
                    os.mv(work, generated)
                end,
                finally({
                    function(ok, errors)
                        os.tryrm(work)
                        if not ok then
                            raise(errors)
                        end
                    end,
                }),
            })
        end, {
            dependfile = path.join(cache.directory, "archives.d"),
            files = table.join(files, os.files(path.join(os.scriptdir(), "**"))),
            values = { config.game, name, layout, occupied, string.serialize(options, { orderkeys = true }) },
            changed = not os.isdir(generated),
        })
        for _, relative in ipairs(layout) do
            os.rm(path.join(stage, relative))
        end
        for _, file in ipairs(os.files(path.join(generated, "**"))) do
            os.cp(file, path.join(stage, path.relative(file, generated)))
        end
        return
    end
    local split = options.split_size or game.split_size
    assert(
        type(split) == "number" and split % 1 == 0 and split >= 1 and split <= game.max_split_size,
        "Archive split_size must be a whole number of GiB, from 1 to 2 for Skyrim or 1 to 8 for Fallout 4."
    )
    local work = os.tmpfile() .. ".dir"
    os.mkdir(work)
    try({
        function()
            local occupied = {}
            for _, file in ipairs(os.files(path.join(stage, "*"))) do
                occupied[path.filename(file):lower()] = true
            end
            local function add_loader(stem)
                local filename = stem .. ".esp"
                for _, extension in ipairs({ ".esp", ".esm", ".esl" }) do
                    assert(
                        not occupied[(stem .. extension):lower()],
                        "Generated loader conflicts with existing plugin: " .. stem
                    )
                end
                os.cp(path.join(resources, config.game, "archive-loader.esp"), path.join(stage, filename))
                occupied[filename:lower()] = true
            end
            if create_loader then
                add_loader(owner)
            end
            local split_loaders = {}
            for _, group in ipairs({ "main", "textures" }) do
                local files = groups[group]
                if #files > 0 then
                    table.sort(files)
                    local source = path.join(work, group, "Data")
                    local output = path.join(work, group, "output")
                    os.mkdir(output)
                    for _, relative in ipairs(files) do
                        os.cp(path.join(stage, relative), path.join(source, relative))
                    end
                    local extension = game.extension
                    local format = game.formats[group]
                    os.vrunv(path.join(resources, "bsarch", "BSArch.exe"), {
                        "pack",
                        source,
                        path.join(output, "part" .. extension),
                        format,
                        "-z",
                        "-split:" .. tostring(split),
                    })
                    local archives = os.files(path.join(output, "*" .. extension))
                    for _, archive in ipairs(archives) do
                        local part = path.basename(archive):match("^part(%d*)$")
                        local stem = owner .. part
                        local suffix = game.suffixes[group]
                        local filename = stem .. suffix .. extension
                        assert(
                            not occupied[filename:lower()],
                            "Generated archive conflicts with an existing file: " .. filename
                        )
                        if part ~= "" and not split_loaders[stem] then
                            add_loader(stem)
                            split_loaders[stem] = true
                        end
                        os.mv(archive, path.join(stage, filename))
                        occupied[filename:lower()] = true
                    end
                    for _, relative in ipairs(files) do
                        os.rm(path.join(stage, relative))
                    end
                end
            end
        end,
        finally({
            function(ok, errors)
                os.tryrm(work)
                if not ok then
                    raise(errors)
                end
            end,
        }),
    })
end
