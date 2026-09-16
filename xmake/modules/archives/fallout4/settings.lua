function get()
    return {
        extension = ".ba2",
        formats = { main = "-fo4", textures = "-fo4dds" },
        suffixes = { main = " - Main", textures = " - Textures" },
        split_size = 4,
        max_split_size = 8,
        extensions = { vis = { "uvd" }, programs = { "swf" } },
        texture = function(file)
            return path.extension(file) == ".dds"
        end,
    }
end
