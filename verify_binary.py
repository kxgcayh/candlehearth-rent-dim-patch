#!/usr/bin/env python3
"""Inspect the PE export table and SKSE metadata without loading the DLL."""
from pathlib import Path
import struct
import sys


def verify(path):
    data = Path(path).read_bytes()
    u16 = lambda off: struct.unpack_from("<H", data, off)[0]
    u32 = lambda off: struct.unpack_from("<I", data, off)[0]
    pe = u32(0x3C)
    assert data[:2] == b"MZ" and data[pe:pe + 4] == b"PE\0\0"
    assert u16(pe + 4) == 0x8664 and u16(pe + 22) & 0x2000, "not AMD64 DLL"
    opt = pe + 24
    assert u16(opt) == 0x20B, "not PE32+"
    sections = opt + u16(pe + 20)

    def offset(rva):
        for i in range(u16(pe + 6)):
            section = sections + 40 * i
            size, addr, rawsize, raw = struct.unpack_from("<IIII", data, section + 8)
            if addr <= rva < addr + max(size, rawsize):
                result = raw + rva - addr
                assert result < raw + rawsize, "RVA has no file backing"
                return result
        raise AssertionError(f"unmapped RVA {rva:X}")

    directory = offset(u32(opt + 112))
    count = u32(directory + 24)
    functions, names, ordinals = (offset(u32(directory + n)) for n in (28, 32, 36))
    exports = {}
    for i in range(count):
        namepos = offset(u32(names + 4 * i))
        name = data[namepos:data.index(b"\0", namepos)].decode()
        exports[name] = u32(functions + 4 * u16(ordinals + 2 * i))
    assert {"SKSEPlugin_Load", "SKSEPlugin_Query", "SKSEPlugin_Version"} <= exports.keys()
    version = offset(exports["SKSEPlugin_Version"])
    assert u32(version) == 1, "unexpected metadata format"
    assert u32(version + 4) == 0x10020, "expected plugin version 0.1.2"
    assert data[version + 8:version + 8 + 256].split(b"\0", 1)[0] == b"CandlehearthRentDim"
    assert u32(version + 0x304) & 2, "missing Address Library V5 compatibility flag"
    assert not u32(version + 0x304) & 1, "must declare struct dependence"
    runtime = (1 << 24) | (7 << 16) | (104 << 4)
    assert u32(version + 0x30C) == runtime, "wrong supported runtime"
    assert all(u32(version + 0x310 + 4 * i) == 0 for i in range(15)), "unexpected extra runtime"
    print("PASS: AMD64 PE32+ DLL; SKSE Load/Query/Version exports; 0.1.2; struct dependent; V5; AE 1.7.104 only")
    for name, rva in exports.items():
        print(f"  {name}: RVA 0x{rva:X}, file offset 0x{offset(rva):X}")


if __name__ == "__main__":
    verify(sys.argv[1])
