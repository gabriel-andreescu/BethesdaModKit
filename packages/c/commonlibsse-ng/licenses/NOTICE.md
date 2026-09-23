# CommonLibSSE-NG adapter

`../rules/plugin.lua` adapts the plugin rules from
[CommonLibSSE-NG](https://github.com/gabriel-andreescu/CommonLibSSE-NG/blob/e04a2f09fbd6df65ecd24a1abf3e6580fda60411/xmake.lua)
and [commonlib-shared](https://github.com/libxse/commonlib-shared/blob/29fbdb0e2dc548c9ab22f6964981d75090dc9094/xmake.lua).
Licensed under [GPL-3.0-or-later](COPYING), with the
[CommonLibSSE-NG exceptions](EXCEPTIONS.md) and
[commonlib-shared exceptions](commonlib-shared-EXCEPTIONS).

Modified by gabriel-andreescu, 2026-09-16: use installed metadata templates,
package rule options and the target basename as the default plugin name.

`patches/vr-form-factory.patch` in the package recipe modifies
[CommonLibSSE-NG's IFormFactory.cpp](https://github.com/gabriel-andreescu/CommonLibSSE-NG/blob/e04a2f09fbd6df65ecd24a1abf3e6580fda60411/src/RE/I/IFormFactory.cpp)
under the same CommonLibSSE-NG terms. Modified by gabriel-andreescu, 2026-09-16:
use a VR-specific address for the initialization flag.
