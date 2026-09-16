import("core.project.config")
import("core.project.depend")
import("lib.detect.find_tool")

function run(target, options, arguments)
    local dotnet = assert(find_tool("dotnet"), "Install the project's .NET SDK.")
    local project = path.absolute(assert(options.project, "Set the C# project path."))
    local artifacts =
        path.absolute(path.join(config.builddir(), "intermediates", "dotnet", (target:fullname():gsub("::", "/"))))
    local properties = {
        "--property:Configuration=" .. (options.configuration or "Release"),
        "--property:ArtifactsPath=" .. artifacts,
        "--nologo",
    }
    os.vrunv(dotnet.program, table.join({ "build", project }, properties))
    local assembly = os.iorunv(
        dotnet.program,
        table.join({
            "msbuild",
            project,
            "--getProperty:TargetPath",
        }, properties)
    ):trim()
    assert(os.isfile(assembly), "MSBuild did not return a target assembly: " .. assembly)
    local files = table.join(os.files(path.join(path.directory(assembly), "**")), target:extrafiles(), {
        path.join(os.scriptdir(), "dotnet.lua"),
        path.join(os.scriptdir(), "generated.lua"),
    })
    depend.on_changed(function()
        local stage = os.tmpfile() .. ".dir"
        os.mkdir(stage)
        try({
            function()
                local args = {}
                for _, argument in ipairs(arguments) do
                    table.insert(args, (argument:replace("$(outputdir)", path.absolute(stage), { plain = true })))
                end
                os.vrunv(dotnet.program, table.join({ assembly }, args))
                import("@self.generated").publish(stage, target:targetdir(), target:dependfile("dotnet.outputs"))
            end,
            finally({
                function(ok, errors)
                    os.tryrm(stage)
                    if not ok then
                        raise(errors)
                    end
                end,
            }),
        })
    end, {
        dependfile = target:dependfile("dotnet"),
        files = files,
        values = arguments,
        changed = target:is_rebuilt()
            or import("@self.generated").missing(target:targetdir(), target:dependfile("dotnet.outputs")),
    })
    import("@self.generated").installfiles(
        target,
        target:targetdir(),
        target:dependfile("dotnet.outputs"),
        options.outputs or {}
    )
end
