#pragma once

#include <CLIBUtil/detail/SimpleIni.h>
#include <spdlog/spdlog.h>

#include <Windows.h>

#include <cstdint>
#include <exception>
#include <expected>
#include <filesystem>
#include <format>
#include <functional>
#include <optional>
#include <string>
#include <system_error>
#include <utility>

namespace BMK::Settings {
struct Paths {
    std::filesystem::path defaults;
    std::filesystem::path user;
};

struct Failure {
    std::string message;
};

enum class SaveUserFile : std::uint8_t {
    kNo,
    kYes,
};

template <class Values>
struct Loaded {
    Values values;
    std::optional<Failure> saveFailure;
};

namespace Detail {
    inline std::optional<Failure> LoadFile(CSimpleIniA& a_ini, const std::filesystem::path& a_path) {
        a_ini.SetUnicode();
        std::error_code error;
        const auto exists = std::filesystem::exists(a_path, error);
        if (error) {
            return Failure {std::format("Cannot inspect {}: {}", a_path.string(), error.message())};
        }
        if (!exists) {
            return std::nullopt;
        }
        if (const auto result = a_ini.LoadFile(a_path.c_str()); result < 0) {
            return Failure {std::format("Cannot read {} (INI error {})", a_path.string(), result)};
        }
        return std::nullopt;
    }

    inline std::optional<Failure> SaveFile(const CSimpleIniA& a_ini, const std::filesystem::path& a_path) {
        std::error_code error;
        const auto parent = a_path.parent_path();
        if (!parent.empty()) {
            std::filesystem::create_directories(parent, error);
            if (error) {
                return Failure {std::format("Cannot create {}: {}", parent.string(), error.message())};
            }
        }
        if (const auto result = a_ini.SaveFile(a_path.c_str()); result < 0) {
            return Failure {std::format("Cannot write {} (INI error {})", a_path.string(), result)};
        }
        return std::nullopt;
    }
}

template <class Values, class Reader>
std::expected<Loaded<Values>, Failure> Load(
    Paths a_paths,
    Values a_values,
    Reader&& a_reader,
    const SaveUserFile a_saveUserFile = SaveUserFile::kYes
) {
    CSimpleIniA defaults;
    if (auto failure = Detail::LoadFile(defaults, a_paths.defaults)) {
        return std::unexpected(std::move(*failure));
    }

    CSimpleIniA user;
    if (auto failure = Detail::LoadFile(user, a_paths.user)) {
        return std::unexpected(std::move(*failure));
    }

    try {
        std::invoke(std::forward<Reader>(a_reader), defaults, user, a_values);
    } catch (const std::exception& error) {
        return std::unexpected(
            Failure {std::format(
                "Cannot process {} and {}: {}",
                a_paths.defaults.string(),
                a_paths.user.string(),
                error.what()
            )}
        );
    }

    return Loaded<Values> {
        .values = std::move(a_values),
        .saveFailure = a_saveUserFile == SaveUserFile::kYes ? Detail::SaveFile(user, a_paths.user) : std::nullopt,
    };
}

inline void ApplyLogLevel(const bool a_debugLogging, const spdlog::level::level_enum a_defaultLevel) {
    const auto level = a_debugLogging || IsDebuggerPresent() != 0 ? spdlog::level::debug : a_defaultLevel;
    spdlog::set_level(level);
    spdlog::flush_on(level);
}
}
