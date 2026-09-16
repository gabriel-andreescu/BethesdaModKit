function main(requestfile)
    local json = import("core.base.json")
    local request = json.loadfile(requestfile)
    local modules = path.join(os.scriptdir(), "../../../xmake/modules")
    local result = { calls = {} }
    os.vrunv = function(program, arguments)
        assert(path.filename(program) == "BSArch.exe")
        local files = {}
        for _, file in ipairs(os.files(path.join(arguments[2], "**"))) do
            local relative = path.relative(file, arguments[2]):gsub("\\", "/")
            table.insert(files, relative)
        end
        table.sort(files)
        table.insert(result.calls, { arguments = arguments, files = files })
        if request.fail then
            raise("BSArch failed")
        end
        io.writefile(arguments[3], table.concat(files, "\n"))
    end
    local target = import("core.project.project").target("TestMod")
    target:data_set("bmk.package", { game = "skyrim", options = { bsa = request.options } })
    result.output = import("payload", { rootdir = modules }).prepare(target)
    json.savefile(requestfile .. ".result", result)
end
