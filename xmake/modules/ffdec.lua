import("core.project.depend")
import("lib.detect.find_tool")

function commands(options, intermediate, output)
    assert((options.xml ~= nil) ~= (options.swf ~= nil), "FFDec requires either xml or swf.")
    local commands = {}
    if options.xml then
        table.insert(commands, { "-xml2swf", options.xml, intermediate })
    end
    if options.scripts then
        table.insert(commands, {
            "-config",
            "autoDeobfuscate=false,decompile=false",
            "-onerror",
            "abort",
            "-importScript",
            options.xml and intermediate or options.swf,
            output,
            options.scripts,
        })
    end
    return commands
end

function build(target)
    local options = target:extraconf("rules", "@addon/bmk/ffdec") or {}
    local package = assert(target:pkg("ffdec"), "Add the ffdec package to the interface target.")
    local java = assert(find_tool("java", { envs = target:pkgenvs() }), "FFDec requires Java.")
    local jar = path.join(package:installdir(), "lib", "ffdec.jar")
    local output = path.join(target:targetdir(), options.output)
    local files = { options.xml or options.swf, jar, path.join(os.scriptdir(), "ffdec.lua") }
    if options.scripts then
        table.join2(files, os.files(path.join(options.scripts, "**")))
    end
    table.join2(files, (target:extrafiles()))
    depend.on_changed(function()
        local work = os.tmpfile() .. ".dir"
        os.mkdir(work)
        try({
            function()
                local intermediate = path.join(work, "base.swf")
                local result = path.join(work, "result.swf")
                for _, args in ipairs(commands(options, intermediate, result)) do
                    os.vrunv(java.program, table.join({ "-jar", jar }, args), { envs = target:pkgenvs() })
                end
                if not options.scripts then
                    os.cp(options.xml and intermediate or options.swf, result)
                end
                os.mkdir(path.directory(output))
                os.mv(result, output)
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
        dependfile = target:dependfile("ffdec"),
        files = files,
        values = { string.serialize(options, { orderkeys = true }) },
        changed = target:is_rebuilt() or not os.isfile(output),
    })
end
