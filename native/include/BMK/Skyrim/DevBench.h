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
}
