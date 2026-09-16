#pragma once

#include <chrono>
#include <functional>
#include <future>
#include <memory>
#include <optional>
#include <string>
#include <utility>

namespace BMK::Skyrim::Detail {
template <class Enqueue>
std::optional<std::string> WaitForInspection(
    std::function<std::string()> a_inspect,
    Enqueue&& a_enqueue,
    std::chrono::milliseconds a_timeout
) {
    // The queue owns the task even if the listener stops waiting during a load.
    auto task = std::make_shared<std::packaged_task<std::string()>>(std::move(a_inspect));
    auto result = task->get_future();
    std::forward<Enqueue>(a_enqueue)([task] { (*task)(); });
    if (result.wait_for(a_timeout) != std::future_status::ready) {
        return std::nullopt;
    }
    return result.get();
}
}
