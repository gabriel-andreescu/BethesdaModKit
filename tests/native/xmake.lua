set_project("BMKNativeTests")
set_languages("c++23")
set_defaultmode("releasedbg")
add_rules("mode.releasedbg")
add_rules("plugin.compile_commands.autoupdate", { outputdir = ".", lsp = "clangd" })
add_requires("catch2 3.8.1")

target("InspectionTaskTests", function()
    set_kind("binary")
    add_files("skyrim/InspectionTaskTests.cpp")
    add_includedirs("../../native/include")
    add_packages("catch2")
    add_tests("inspection")
    after_config(function(target)
        if target:has_tool("cxx", "cl") then
            target:add("symbols", "embed")
        end
    end)
end)
