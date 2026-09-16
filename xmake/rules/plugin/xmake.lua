rule("plugin")
add_deps("mode.debug", "mode.releasedbg", "mode.release")
add_deps("plugin.compile_commands.autoupdate")
after_config(function(target)
    local config = target:data("bmk.plugin")
    target:set("kind", "shared")
    if not target:get("languages") then
        target:set("languages", "c++23")
    end
    if not target:get("warnings") then
        target:set("warnings", "allextra", "error")
    end
    target:add("defines", "NOMINMAX")
    target:set("encodings", "utf-8")
    target:extraconf_set("rules", "plugin.compile_commands.autoupdate", "lsp", "clangd")
    if target:has_tool("cxx", "cl") then
        -- MSVC objects must carry their debug information for compiler-cache reuse.
        target:add("symbols", "embed")
    end
    target:add("cxxflags", "/EHsc", "/permissive-")
    target:add("cxxflags", "/Zc:preprocessor", { tools = "cl" })
    target:add("installfiles", target:targetfile(), { prefixdir = config.plugins })
    if target:symbolfile() then
        target:add("installfiles", target:symbolfile(), { prefixdir = config.plugins })
    end
end)
