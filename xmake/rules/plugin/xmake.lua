rule("plugin")
add_deps("@self/native.compiler")
on_load(function(target)
    target:set("kind", "shared")
end)
after_config(function(target)
    local config = target:data("bmk.plugin")
    target:add("installfiles", target:targetfile(), { prefixdir = config.plugins })
    if target:symbolfile() then
        target:add("installfiles", target:symbolfile(), { prefixdir = config.plugins })
    end
end)
