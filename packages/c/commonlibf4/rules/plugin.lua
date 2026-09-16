-- Adapted from CommonLibF4 and commonlib-shared. See ../licenses/NOTICE.md for licensing and changes.
rule("plugin")
add_deps("win.sdk.resource")
on_config(function(target)
    import("core.project.project")
    import("core.base.semver")

    local share = path.join(target:pkg("commonlibf4"):installdir(), "share")
    local data = target:extraconf("rules", "@commonlibf4/plugin") or {}
    local version = target:version() or "0.0.0"
    local project_version = project.version() or version
    local xse_version = data.xse_minimum or "0.0.0"

    target:set("arch", "x64")
    target:set("kind", "shared")
    target:set("configdir", target:autogendir())
    target:add("configfiles", path.join(share, "commonlib-plugin.rc.in"))
    target:add("configfiles", path.join(share, "commonlibf4-plugin.cpp.in"))
    target:add("files", path.join(target:configdir(), "commonlib-plugin.rc"), { always_added = true })
    target:add("files", path.join(target:configdir(), "commonlibf4-plugin.cpp"), { always_added = true })

    target:set("configvar", "COMMONLIB_PLUGIN_AUTHOR", data.author or "")
    target:set("configvar", "COMMONLIB_PLUGIN_CONTACT", data.contact or "")
    target:set("configvar", "COMMONLIB_PLUGIN_DESCRIPTION", data.description or "")
    target:set("configvar", "COMMONLIB_PLUGIN_LICENSE", (target:license() or "Unknown") .. " License")
    target:set("configvar", "COMMONLIB_PLUGIN_NAME", data.name or target:basename())
    target:set("configvar", "COMMONLIB_PLUGIN_VERSION", version)
    target:set("configvar", "COMMONLIB_PLUGIN_VERSION_MAJOR", semver.new(version):major())
    target:set("configvar", "COMMONLIB_PLUGIN_VERSION_MINOR", semver.new(version):minor())
    target:set("configvar", "COMMONLIB_PLUGIN_VERSION_PATCH", semver.new(version):patch())
    target:set("configvar", "COMMONLIB_PLUGIN_XSE_VERSION_MAJOR", semver.new(xse_version):major())
    target:set("configvar", "COMMONLIB_PLUGIN_XSE_VERSION_MINOR", semver.new(xse_version):minor())
    target:set("configvar", "COMMONLIB_PLUGIN_XSE_VERSION_PATCH", semver.new(xse_version):patch())
    target:set("configvar", "COMMONLIB_PROJECT_NAME", project.name() or "")
    target:set("configvar", "COMMONLIB_PROJECT_VERSION", project_version)
    target:set("configvar", "COMMONLIB_PROJECT_VERSION_MAJOR", semver.new(project_version):major())
    target:set("configvar", "COMMONLIB_PROJECT_VERSION_MINOR", semver.new(project_version):minor())
    target:set("configvar", "COMMONLIB_PROJECT_VERSION_PATCH", semver.new(project_version):patch())

    local options = data.options or {}
    target:set("configvar", "COMMONLIBF4_OPTION_SIG_SCANNING", tostring(options.sig_scanning or false))
    target:set(
        "configvar",
        "COMMONLIBF4_OPTION_ADDRESS_LIBRARY",
        tostring(not options.sig_scanning and options.address_library ~= false)
    )
    target:set("configvar", "COMMONLIBF4_OPTION_NO_STRUCT_USE", tostring(options.no_struct_use or false))
    target:set(
        "configvar",
        "COMMONLIBF4_OPTION_LAYOUT_DEPENDENT",
        tostring(not options.no_struct_use and options.layout_dependent ~= false)
    )
end)
