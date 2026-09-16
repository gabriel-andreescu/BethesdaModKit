local modules = path.join(os.scriptdir(), "../../../xmake/modules")
local selection = import("archives.selection", { rootdir = modules })
local archive = import("archives.archive", { rootdir = modules })

local function stage(name, files)
    local directory = path.join(os.curdir(), name)
    os.mkdir(directory)
    for _, file in ipairs(files) do
        io.writefile(path.join(directory, file), "fixture")
    end
    return directory
end

local function pack(directory, name, options, parts)
    local game = import("archives." .. name .. ".settings", { rootdir = modules }).get()
    local calls = {}
    os.vrunv = function(program, arguments)
        assert(path.filename(program) == "BSArch.exe")
        assert(arguments[1] == "pack")
        local files = {}
        for _, file in ipairs(os.files(path.join(arguments[2], "**"))) do
            local relative = path.relative(file, arguments[2]):gsub("\\", "/")
            table.insert(files, relative)
        end
        table.sort(files)
        table.insert(calls, { files = files, arguments = arguments })
        for _, part in ipairs(parts or { "" }) do
            io.writefile(path.join(path.directory(arguments[3]), "part" .. part .. game.extension), "fixture")
        end
    end
    archive.pack(directory, { game = name, options = { [game.extension:sub(2)] = options } }, "TestMod")
    return calls
end

local function check_files(directory, expected)
    local actual = {}
    for _, file in ipairs(os.files(path.join(directory, "**"))) do
        local relative = path.relative(file, directory):gsub("\\", "/")
        table.insert(actual, relative)
    end
    table.sort(actual)
    table.sort(expected)
    assert(
        table.concat(actual, "\n") == table.concat(expected, "\n"),
        "%s: expected %s, got %s",
        directory,
        table.concat(expected, ", "),
        table.concat(actual, ", ")
    )
end

function main()
    local included = {
        "materials/test.bgsm",
        "meshes/test.nif",
        "textures/test.dds",
        "interface/test.swf",
        "scripts/test.pex",
        "source/scripts/test.psc",
        "sound/test.wav",
        "sound/voice/test.fuz",
        "sound/voice/test.hkx",
        "music/test.xwm",
        "strings/test.strings",
        "shadersfx/test.fxp",
        "grass/test.gid",
        "lodsettings/test.lod",
        "seq/test.seq",
        "Scripts\\TEST.PEX",
    }
    local excluded = {
        "README.txt",
        "meshes/readme.txt",
        "meshes/.gitkeep",
        "SKSE/Plugins/test.dll",
        "F4SE/Plugins/test.dll",
        "textures/source.psd",
        "CalienteTools/test.nif",
        "dialogueviews/test.xml",
        "unknown/file.bin",
    }
    local fallout_only = {
        "meshes/actors/character/animations/test.hkx",
        "meshes/actors/character/behaviors/test.hkx",
        "meshes/actors/character/_1stperson/animations/test.hkx",
        "meshes/actors/character/_1stperson/behaviors/test.hkx",
        "meshes/animationdatasinglefile.txt",
        "meshes/animationsetdatasinglefile.txt",
        "vis/test.uvd",
        "programs/test.swf",
    }
    for _, name in ipairs({ "skyrim", "fallout4" }) do
        local game = import("archives." .. name .. ".settings", { rootdir = modules }).get()
        for _, file in ipairs(included) do
            assert(selection.selected(file, game), name .. ": " .. file)
        end
        for _, file in ipairs(excluded) do
            assert(not selection.selected(file, game), name .. ": " .. file)
        end
        for _, file in ipairs(fallout_only) do
            assert(selection.selected(file, game) == (name == "fallout4"), name .. ": " .. file)
        end

        local directory = stage(name, { "scripts/test.pex", "textures/test.dds", "textures/test.png" })
        local calls = pack(directory, name, { split_size = 1 }, { "", "1" })
        assert(#calls == 2)
        local main = name == "skyrim" and "scripts/test.pex" or "scripts/test.pex,textures/test.png"
        local textures = name == "skyrim" and "textures/test.dds,textures/test.png" or "textures/test.dds"
        assert(table.concat(calls[1].files, ",") == main)
        assert(table.concat(calls[2].files, ",") == textures)
        local formats = name == "skyrim" and { "-sse", "-sse" } or { "-fo4", "-fo4dds" }
        for index, call in ipairs(calls) do
            assert(call.arguments[4] == formats[index])
            assert(call.arguments[5] == "-z")
            assert(tonumber(call.arguments[6]:match("^-split:(.+)$")) == 1)
        end
        local suffixes = name == "skyrim" and { ".esp", ".bsa", " - Textures.bsa" }
            or { ".esp", " - Main.ba2", " - Textures.ba2" }
        local expected = {}
        for _, part in ipairs({ "", "1" }) do
            for _, suffix in ipairs(suffixes) do
                table.insert(expected, "TestMod" .. part .. suffix)
            end
        end
        check_files(directory, expected)
    end

    for index, patterns in ipairs({ { "source/**" }, {} }) do
        local directory = stage("patterns" .. index, { "source/test.psc", "scripts/test.pex", "source/.gitkeep" })
        local calls = pack(directory, "skyrim", { files = patterns })
        assert(#calls == (index == 1 and 1 or 0))
        if index == 1 then
            assert(table.concat(calls[1].files, ",") == "source/test.psc")
        end
        assert(os.isfile(path.join(directory, "scripts/test.pex")))
        assert(os.isfile(path.join(directory, "source/test.psc")) == (index == 2))
        assert(os.isfile(path.join(directory, "TestMod.esp")) == (index == 1))
    end

    local owners = {
        { plugins = {}, owner = "TestMod" },
        { plugins = { "Existing.esp" }, owner = "Existing" },
        { plugins = { "TestMod.esl", "Other.esp" }, owner = "TestMod" },
        { plugins = { "Existing.esm", "Other.esp" }, option = "existing.esm", owner = "Existing" },
    }
    for index, case in ipairs(owners) do
        local directory = stage("owner" .. index, table.join({ "scripts/test.pex" }, case.plugins))
        pack(directory, "skyrim", case.option and { plugin = case.option } or true)
        local expected = table.join(case.plugins, { case.owner .. ".bsa" })
        if #case.plugins == 0 then
            table.insert(expected, "TestMod.esp")
        end
        check_files(directory, expected)
    end

    local nested = stage("nested", { "Data/scripts/test.pex", "README.txt" })
    local calls = pack(nested, "skyrim", { root = "Data" })
    assert(table.concat(calls[1].files, ",") == "scripts/test.pex")
    check_files(nested, { "Data/TestMod.bsa", "Data/TestMod.esp", "README.txt" })

    local invalid = {
        { { "scripts/test.pex", "One.esp", "Two.esp" }, true, "Multiple plugins" },
        { { "scripts/test.pex" }, { plugin = "Missing.esp" }, "not present" },
        { { "scripts/test.pex", "TestMod.bsa" }, true, "conflicts" },
        { { "scripts/test.pex", "TestMod1.esm", "TestMod.esp" }, true, "loader conflicts" },
        { { "SKSE/Plugins/test.dll" }, { files = { "SKSE/**" } }, "cannot pack selected file" },
        { { "root.txt" }, { files = { "*.txt" } }, "must have a directory" },
        { { "scripts/test.pex" }, { files = { "../outside/**" } }, "must stay inside Data" },
        { { "scripts/test.pex" }, { split_size = 0.5 }, "whole number" },
    }
    for index, case in ipairs(invalid) do
        local directory = stage("invalid" .. index, case[1])
        local failure
        try({
            function()
                pack(directory, "skyrim", case[2], { "", "1" })
            end,
            catch({
                function(error)
                    failure = tostring(error)
                end,
            }),
        })
        assert(failure and failure:find(case[3], 1, true), "Expected %s, got %s", case[3], failure)
    end
end
