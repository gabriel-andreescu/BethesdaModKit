#include <BMK/Skyrim/DevBench.h>

#if defined(_MSC_VER)
static_assert(_MSVC_LANG >= 202302L);
#else
static_assert(__cplusplus >= 202302L);
#endif

SKSE_PLUGIN_LOAD(const SKSE::LoadInterface* skse) {
    SKSE::Init(skse);
    return true;
}
