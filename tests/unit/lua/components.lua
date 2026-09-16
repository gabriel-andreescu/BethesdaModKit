local modules = path.join(os.scriptdir(), "../../../xmake/modules")
local papyrus = import("papyrus", { rootdir = modules })
local ffdec = import("ffdec", { rootdir = modules })
local synthesis = import("synthesis", { rootdir = modules })
local generated = import("generated", { rootdir = modules })

function main()
    local args = papyrus.arguments("fallout4", {
        root = "src/papyrus",
        imports = { "game sources", "dependencies" },
        flags = "flags.flg",
        arguments = { "--release" },
    }, { "Selected.psc" }, "compiled")
    assert(args[1] == "Selected.psc")
    assert(table.contains(args, "--game=fallout4"))
    assert(table.contains(args, "--flags=" .. path.absolute("flags.flg")))
    assert(table.contains(args, "--import=" .. table.concat({
        path.absolute("src/papyrus"),
        path.absolute("game sources"),
        path.absolute("dependencies"),
    }, ";")))
    assert(args[#args] == "--release")

    args = papyrus.arguments("skyrim", { root = "src/papyrus" }, { "Selected.psc" }, "compiled")
    assert(table.concat(args, "|") == table.concat({
        "Selected.psc",
        "--game=skyrim",
        "--ignorecwd",
        "--import=" .. path.absolute("src/papyrus"),
        "--output=" .. path.absolute("compiled"),
    }, "|"))

    local commands = ffdec.commands({ xml = "movie.xml", scripts = "actionscript" }, "base.swf", "result.swf")
    assert(table.concat(commands[1], "|") == "-xml2swf|movie.xml|base.swf")
    assert(
        table.concat(commands[2], "|")
            == "-config|autoDeobfuscate=false,decompile=false|-onerror|abort|-importScript|base.swf|result.swf|actionscript"
    )
    commands = ffdec.commands({ swf = "authored.swf", scripts = "actionscript" }, "unused", "result.swf")
    assert(#commands == 1 and commands[1][6] == "authored.swf")

    args = synthesis.arguments("SkyrimSE", {
        output = "Patch.esp",
        load_order = "loadorder.txt",
        arguments = { "--PatcherName", "Compatibility" },
    }, "inputs", "$(outputdir)")
    assert(table.concat(args, "|") == table.concat({
        "run-patcher",
        "--GameRelease",
        "SkyrimSE",
        "--DataFolderPath",
        path.absolute("inputs"),
        "--LoadOrderFilePath",
        path.absolute("loadorder.txt"),
        "--ModKey",
        "Patch.esp",
        "--OutputPath",
        path.join("$(outputdir)", "Patch.esp"),
        "--PatcherName",
        "Compatibility",
    }, "|"))

    io.writefile("stage/Previous.esp", "previous")
    io.writefile("output/sibling.esp", "sibling")
    generated.publish("stage", "output", "outputs.lua")
    os.rm("stage/Previous.esp")
    io.writefile("stage/Current.esp", "current")
    generated.publish("stage", "output", "outputs.lua")
    assert(not os.isfile("output/Previous.esp"))
    assert(io.readfile("output/Current.esp") == "current")
    assert(io.readfile("output/sibling.esp") == "sibling")
    local exported = {}
    local target = {
        add = function(_, _, file)
            table.insert(exported, file)
        end,
    }
    generated.installfiles(target, "output", "outputs.lua", { "*.esp" })
    assert(#exported == 1 and exported[1] == path.join("output", "(Current.esp)"))
end
