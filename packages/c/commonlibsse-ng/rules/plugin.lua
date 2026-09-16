-- Adapted from CommonLibSSE-NG and commonlib-shared. See ../licenses/NOTICE.md for licensing and changes.
rule("plugin")
add_deps("win.sdk.resource")
on_config(function(target)
    import("core.project.project")
    import("core.base.semver")

    local share = path.join(target:pkg("commonlibsse-ng"):installdir(), "share")
    local data = target:extraconf("rules", "@commonlibsse-ng/plugin") or {}
    local version = target:version() or "0.0.0"
    local project_version = project.version() or version

    target:set("arch", "x64")
    target:set("kind", "shared")
    target:set("configdir", target:autogendir())
    target:add("configfiles", path.join(share, "commonlib-plugin.rc.in"))
    target:add("configfiles", path.join(share, "commonlibsse-ng-plugin.cpp.in"))
    target:add("files", path.join(target:configdir(), "commonlib-plugin.rc"), { always_added = true })
    target:add("files", path.join(target:configdir(), "commonlibsse-ng-plugin.cpp"), { always_added = true })

    target:set("configvar", "COMMONLIB_PLUGIN_AUTHOR", data.author or "")
    target:set("configvar", "COMMONLIB_PLUGIN_CONTACT", data.contact or "")
    target:set("configvar", "COMMONLIB_PLUGIN_DESCRIPTION", data.description or "")
    target:set("configvar", "COMMONLIB_PLUGIN_LICENSE", (target:license() or "Unknown") .. " License")
    target:set("configvar", "COMMONLIB_PLUGIN_NAME", data.name or target:basename())
    target:set("configvar", "COMMONLIB_PLUGIN_VERSION", version)
    target:set("configvar", "COMMONLIB_PLUGIN_VERSION_MAJOR", semver.new(version):major())
    target:set("configvar", "COMMONLIB_PLUGIN_VERSION_MINOR", semver.new(version):minor())
    target:set("configvar", "COMMONLIB_PLUGIN_VERSION_PATCH", semver.new(version):patch())
    target:set("configvar", "COMMONLIB_PROJECT_NAME", project.name() or "")
    target:set("configvar", "COMMONLIB_PROJECT_VERSION", project_version)
    target:set("configvar", "COMMONLIB_PROJECT_VERSION_MAJOR", semver.new(project_version):major())
    target:set("configvar", "COMMONLIB_PROJECT_VERSION_MINOR", semver.new(project_version):minor())
    target:set("configvar", "COMMONLIB_PROJECT_VERSION_PATCH", semver.new(project_version):patch())

    local options = data.options or {}
    local struct_compatibility = "SKSE::StructCompatibility::Independent"
    local runtime_compatibility = "SKSE::VersionIndependence::AddressLibrary"
    if options.struct_dependent then
        struct_compatibility = "SKSE::StructCompatibility::Dependent"
    end
    if options.signature_scanning and not options.address_library then
        runtime_compatibility = "SKSE::VersionIndependence::SignatureScanning"
    end
    target:set("configvar", "COMMONLIBSSE_NG_OPTION_STRUCT_COMPATIBILITY", struct_compatibility)
    target:set("configvar", "COMMONLIBSSE_NG_OPTION_RUNTIME_COMPATIBILITY", runtime_compatibility)
end)
