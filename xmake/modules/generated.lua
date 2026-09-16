function publish(stage, destination, manifest)
    local previous = os.isfile(manifest) and io.load(manifest) or {}
    local current = {}
    for _, file in ipairs(os.files(path.join(stage, "**"))) do
        local relative = path.relative(file, stage)
        current[relative:lower()] = relative
        os.cp(file, path.join(destination, relative), { copy_if_different = true })
    end
    for key, relative in pairs(previous) do
        if not current[key] then
            os.tryrm(path.join(destination, relative))
        end
    end
    os.mkdir(destination)
    io.save(manifest, current)
end

function installfiles(target, directory, manifest, patterns, prefix)
    local owned = os.isfile(manifest) and io.load(manifest) or {}
    for _, pattern in ipairs(patterns) do
        for _, file in ipairs(os.files(path.join(directory, pattern))) do
            local relative = path.relative(file, directory)
            if owned[relative:lower()] then
                target:add("installfiles", path.join(directory, "(" .. relative .. ")"), { prefixdir = prefix })
            end
        end
    end
end

function missing(directory, manifest)
    if not os.isfile(manifest) then
        return true
    end
    for _, relative in pairs(io.load(manifest)) do
        if not os.isfile(path.join(directory, relative)) then
            return true
        end
    end
    return false
end
