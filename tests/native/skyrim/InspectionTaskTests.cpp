#include <BMK/Skyrim/Detail/InspectionTask.h>

#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers.hpp>

#include <chrono>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>

using BMK::Skyrim::Detail::WaitForInspection;

TEST_CASE("An inspection returns the worker's result") {
    std::jthread worker;
    const auto result = WaitForInspection(
        [] { return std::string {R"({"ok":true})"}; },
        [&](auto task) { worker = std::jthread(std::move(task)); },
        std::chrono::seconds(1)
    );
    REQUIRE(result == R"({"ok":true})");
}

TEST_CASE("Inspection exceptions reach the waiting caller") {
    REQUIRE_THROWS_WITH(
        WaitForInspection(
            []() -> std::string { throw std::runtime_error("snapshot failed"); },
            [](auto task) { task(); },
            std::chrono::seconds(1)
        ),
        "snapshot failed"
    );
}

TEST_CASE("A timed-out inspection retains its data until the queue releases it") {
    std::function<void()> queued;
    auto data = std::make_shared<std::string>("snapshot");
    const std::weak_ptr<std::string> lifetime = data;
    bool inspected = false;
    const auto result = WaitForInspection(
        [owned = std::move(data), &inspected] {
            inspected = true;
            return *owned;
        },
        [&](auto task) { queued = std::move(task); },
        std::chrono::milliseconds(0)
    );
    REQUIRE_FALSE(result.has_value());
    REQUIRE_FALSE(inspected);
    REQUIRE_FALSE(lifetime.expired());
    queued();
    REQUIRE(inspected);
    queued = {};
    REQUIRE(lifetime.expired());
}
