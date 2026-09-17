#include <F4SE/F4SE.h>

#if defined(_MSC_VER)
static_assert(_MSVC_LANG >= 202302L);
#else
static_assert(__cplusplus >= 202302L);
#endif

F4SE_PLUGIN_LOAD(const F4SE::LoadInterface* f4se) {
    F4SE::Init(f4se);
    return true;
}
