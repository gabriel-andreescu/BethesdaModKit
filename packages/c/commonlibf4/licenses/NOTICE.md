# CommonLibF4 adapter

`../rules/plugin.lua` adapts the plugin rules from
[CommonLibF4](https://github.com/libxse/commonlibf4/blob/8e645d4a5b556701fd6936df99e40aa1d783600d/xmake.lua)
and [commonlib-shared](https://github.com/libxse/commonlib-shared/blob/29fbdb0e2dc548c9ab22f6964981d75090dc9094/xmake.lua).
Licensed under [GPL-3.0-or-later](COPYING), with the
[exceptions shared by both projects](EXCEPTIONS).

Modified by gabriel-andreescu, 2026-09-16: use installed metadata templates,
package rule options and the target basename as the default plugin name.
