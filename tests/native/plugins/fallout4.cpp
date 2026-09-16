#include <F4SE/F4SE.h>

F4SE_PLUGIN_LOAD(const F4SE::LoadInterface* f4se) {
    F4SE::Init(f4se);
    return true;
}
