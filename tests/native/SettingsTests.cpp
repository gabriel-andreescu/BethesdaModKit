#include <BMK/Settings.h>

#include <catch2/catch_test_macros.hpp>

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <string>

namespace {
struct Values {
    int value {1};
    int packagedOnly {1};
};

class TemporaryDirectory {
public:
    TemporaryDirectory() {
        const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
        path_ = std::filesystem::temp_directory_path() / ("bmk-settings-" + std::to_string(stamp));
        std::filesystem::create_directories(path_);
    }

    ~TemporaryDirectory() {
        std::error_code error;
        std::filesystem::remove_all(path_, error);
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory(TemporaryDirectory&&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(TemporaryDirectory&&) = delete;

    const std::filesystem::path& Get() const {
        return path_;
    }

private:
    std::filesystem::path path_;
};

void Write(const std::filesystem::path& a_path, const std::string& a_contents) {
    std::ofstream stream(a_path);
    stream << a_contents;
    REQUIRE(stream.good());
}

std::string Read(const std::filesystem::path& a_path) {
    std::ifstream stream(a_path);
    return {std::istreambuf_iterator<char> {stream}, {}};
}

void ReadValues(CSimpleIniA& a_defaults, CSimpleIniA& a_user, Values& a_values) {
    a_values.value = static_cast<int>(a_defaults.GetLongValue("General", "iValue", a_values.value));
    a_values.packagedOnly = static_cast<int>(
        a_defaults.GetLongValue("General", "iPackagedOnly", a_values.packagedOnly)
    );
    a_values.value = static_cast<int>(a_user.GetLongValue("General", "iValue", a_values.value));
    a_values.packagedOnly = static_cast<int>(a_user.GetLongValue("General", "iPackagedOnly", a_values.packagedOnly));
    a_user.SetLongValue("General", "iValue", a_values.value);
    a_user.SetLongValue("General", "iPackagedOnly", a_values.packagedOnly);
}
} // namespace

TEST_CASE("Settings pass both INIs to the reader") {
    TemporaryDirectory files;
    const auto defaults = files.Get() / "defaults.ini";
    const auto user = files.Get() / "user.ini";
    const std::string packaged = "[General]\niValue=2\niPackagedOnly=4\n";
    Write(defaults, packaged);
    Write(user, "[General]\niValue=3\n");

    SECTION("Save processed user settings") {
        const auto result = BMK::Settings::Load(BMK::Settings::Paths {defaults, user}, Values {}, ReadValues);

        REQUIRE(result.has_value());
        CHECK(result->values.value == 3);
        CHECK(result->values.packagedOnly == 4);
        CHECK_FALSE(result->saveFailure.has_value());
        CHECK(Read(defaults) == packaged);
        CSimpleIniA saved;
        REQUIRE(saved.LoadFile(user.c_str()) >= 0);
        CHECK(saved.GetLongValue("General", "iValue") == 3);
        CHECK(saved.GetLongValue("General", "iPackagedOnly") == 4);
    }

    SECTION("Skip saving the user INI") {
        const auto original = Read(user);
        const auto result = BMK::Settings::Load(
            BMK::Settings::Paths {defaults, user},
            Values {},
            ReadValues,
            BMK::Settings::SaveUserFile::kNo
        );

        REQUIRE(result.has_value());
        CHECK(result->values.value == 3);
        CHECK(result->values.packagedOnly == 4);
        CHECK_FALSE(result->saveFailure.has_value());
        CHECK(Read(defaults) == packaged);
        CHECK(Read(user) == original);
    }
}

TEST_CASE("Settings reject file read failures") {
    TemporaryDirectory files;
    SECTION("Unreadable INI") {
        const auto defaults = files.Get() / "defaults.ini";
        std::filesystem::create_directory(defaults);

        const auto result = BMK::Settings::Load(
            BMK::Settings::Paths {defaults, files.Get() / "user.ini"},
            Values {},
            ReadValues
        );

        CHECK_FALSE(result.has_value());
    }

    SECTION("Reader failure") {
        const auto user = files.Get() / "user.ini";
        const std::string original = "[General]\niValue=3\n";
        Write(user, original);

        const auto result = BMK::Settings::Load(
            BMK::Settings::Paths {files.Get() / "defaults.ini", user},
            Values {},
            [](CSimpleIniA&, CSimpleIniA&, Values&) { throw std::runtime_error("invalid value"); }
        );

        CHECK_FALSE(result.has_value());
        CHECK(Read(user) == original);
    }
}

TEST_CASE("Settings retain valid values when saving fails") {
    TemporaryDirectory files;
    const auto user = files.Get() / "user.ini";
    const auto result = BMK::Settings::Load(
        BMK::Settings::Paths {files.Get() / "defaults.ini", user},
        Values {},
        [&user](CSimpleIniA& a_defaults, CSimpleIniA& a_user, Values& a_values) {
            ReadValues(a_defaults, a_user, a_values);
            a_values.value = 4;
            std::filesystem::create_directory(user);
        }
    );

    REQUIRE(result.has_value());
    CHECK(result->values.value == 4);
    CHECK(result->saveFailure.has_value());
}
