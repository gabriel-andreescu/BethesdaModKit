#pragma once

#include "Detail/InspectionTask.h"

#include <DevBenchAPI.h>
#include <SKSE/SKSE.h>

#include <chrono>
#include <exception>
#include <functional>
#include <string>
#include <utility>

namespace BMK::Skyrim::DevBench {
struct Inspection {
    const char* name;
    const char* descriptor;
    std::string (*snapshot)();
    const char* timeoutResponse;
    const char* failureResponse;
};

inline void InspectOnGameThread(
    std::function<std::string()> a_inspect,
    void* a_sink,
    DevBenchAPI::WriteFn a_write,
    const char* a_timeoutResponse,
    const char* a_failureResponse
) {
    try {
        const auto result = Detail::WaitForInspection(
            std::move(a_inspect),
            [](auto a_task) { SKSE::GetTaskInterface()->AddTask(std::move(a_task)); },
            std::chrono::seconds(3)
        );
        a_write(a_sink, result ? result->c_str() : a_timeoutResponse);
    } catch (const std::exception& error) {
        SKSE::log::error("DevBench inspection failed: {}", error.what());
        a_write(a_sink, a_failureResponse);
    }
}

namespace Detail {
template <const Inspection& Definition>
void HandleInspection(
    [[maybe_unused]] void* a_context,
    [[maybe_unused]] const char* a_args,
    void* a_sink,
    DevBenchAPI::WriteFn a_write
) {
    InspectOnGameThread(
        Definition.snapshot,
        a_sink,
        a_write,
        Definition.timeoutResponse,
        Definition.failureResponse
    );
}
}

template <const Inspection& Definition>
void RegisterInspection() {
    auto* api = DevBenchAPI::GetDevBenchInterface001();
    if (api == nullptr) {
        return;
    }
    if (api->GetBuildNumber() < 10500) {
        SKSE::log::warn("DevBench {} inspection requires version 1.5.0 or newer", Definition.name);
        return;
    }
    if (!api->RegisterToolExtension(
            "inspect",
            Definition.name,
            Definition.descriptor,
            Detail::HandleInspection<Definition>,
            nullptr
        )) {
        SKSE::log::warn("DevBench replaced an existing {} inspection extension", Definition.name);
    }
}
}
