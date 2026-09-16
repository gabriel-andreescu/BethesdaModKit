# Bundled resources

| Resource            | Source                                                                                                                     | License                |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| `bsarch/BSArch.exe` | [BSArch 1.1](https://www.nexusmods.com/newvegas/mods/64745), [source](https://github.com/TES5Edit/TES5Edit/tree/dev-4.1.6) | [MPL 2.0](MPL-2.0.txt) |

BSArch is by zilav, ElminsterAU and Sheson.

BSArch SHA256:
`4d04a6b85f718a800c1382c05a719184b0b96c582516868e35d3140cc5b7227a`.

Its compression-library notices are included in
[bsarch/licenses](bsarch/licenses):

| Component      | Source                                                                                                               | Notice                                         |
| -------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| lz4-delphi     | [Source](https://github.com/ElminsterAU/lz4-delphi/tree/6d6244eb768797c1a5aa6346848e6ee68d096e0f)                    | [BSD-2-Clause](bsarch/licenses/lz4-delphi.txt) |
| LZ4            | [Source](https://github.com/ElminsterAU/lz4-delphi/tree/6d6244eb768797c1a5aa6346848e6ee68d096e0f/Objects/C)          | [BSD-2-Clause](bsarch/licenses/lz4.txt)        |
| xxHash         | [Source](https://github.com/ElminsterAU/lz4-delphi/blob/6d6244eb768797c1a5aa6346848e6ee68d096e0f/Objects/C/xxhash.c) | [BSD-2-Clause](bsarch/licenses/xxhash.txt)     |
| libdeflate-pas | [Source](https://github.com/ElminsterAU/libdeflate-pas/tree/c044fe1a7b0e2e9930c6a5110c7bd194a4872c91)                | [MIT](bsarch/licenses/libdeflate-pas.txt)      |
| libdeflate     | [Source](https://github.com/ebiggers/libdeflate/tree/v1.24)                                                          | [MIT](bsarch/licenses/libdeflate.txt)          |
| zlib           | [Source](https://github.com/madler/zlib)                                                                             | [zlib](bsarch/licenses/zlib.txt)               |

BMK's empty loader plugins are generated with Mutagen and contain no records or
master dependencies. Both are ESL-flagged. The Skyrim loader uses header version
1.70 and the Fallout 4 loader uses 1.0.
