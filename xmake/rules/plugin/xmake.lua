rule("plugin")
add_deps("@self/native.compiler")
after_config(function(target)
    local config = target:data("bmk.plugin")
    target:set("kind", "shared")
    target:add("installfiles", target:targetfile(), { prefixdir = config.plugins })
    if target:symbolfile() then
        target:add("installfiles", target:symbolfile(), { prefixdir = config.plugins })
    end
end)
