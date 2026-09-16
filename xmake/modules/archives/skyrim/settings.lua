local loose_paths = {
    "meshes/actors/character/animations/",
    "meshes/actors/character/behaviors/",
    "meshes/actors/character/_1stperson/animations/",
    "meshes/actors/character/_1stperson/behaviors/",
}

function get()
    return {
        extension = ".bsa",
        formats = { main = "-sse", textures = "-sse" },
        suffixes = { main = "", textures = " - Textures" },
        split_size = 2,
        max_split_size = 2,
        extensions = {},
        texture = function(file)
            return path.extension(file) == ".dds" or (file:startswith("textures/") and path.extension(file) == ".png")
        end,
        exclude = function(file)
            for _, prefix in ipairs(loose_paths) do
                if file:startswith(prefix) then
                    return true
                end
            end
            return file == "meshes/animationdatasinglefile.txt" or file == "meshes/animationsetdatasinglefile.txt"
        end,
    }
end
