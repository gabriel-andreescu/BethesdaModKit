local extensions = {
    materials = { "bgem", "bgsm" },
    meshes = { "bto", "btr", "btt", "dtl", "egm", "hkb", "hkx", "lst", "nif", "tri", "hkc", "hkt", "hkp", "ini", "txt" },
    textures = { "dds", "png", "tga" },
    interface = { "dds", "gfx", "swf", "txt", "png" },
    scripts = { "psc", "pex", "txt" },
    source = { "psc" },
    sound = { "fuz", "lip", "ogg", "wav", "xwm" },
    music = { "xwm", "mp3" },
    strings = { "dlstrings", "ilstrings", "strings" },
    shadersfx = { "fxp" },
    grass = { "cgid", "gid", "lnk" },
    lodsettings = { "dlodsettings", "lod", "lodsettings" },
    seq = { "seq" },
}

function selected(file, game)
    local relative = file:gsub("\\", "/"):lower()
    if path.filename(relative) == "readme.txt" then
        return false
    end
    if game.exclude and game.exclude(relative) then
        return false
    end
    local directory = relative:match("^([^/]+)/")
    local extension = path.extension(relative):sub(2)
    if relative:startswith("sound/voice/") and (extension == "hkx" or extension == "mp3") then
        return true
    end
    return table.contains(game.extensions[directory] or extensions[directory] or {}, extension)
end
