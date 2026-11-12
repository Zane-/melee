"""Minimal reader for Melee fighter data archives (Pl??.dat + Pl??AJ.dat).

Only what the frame data extractor needs: the ftData root, the common
attribute block, the subaction (animation + script) table and the frame
count of each animation. Layout follows `struct ftData` and
`Fighter_WaitAnimData` in src/melee/ft/types.h.
"""

import re
import struct

HEADER_SIZE = 0x20
SUBACTION_SIZE = 0x18


class Dat:
    def __init__(self, raw):
        self.raw = raw
        (self.file_size, self.data_size, self.reloc_count, self.root_count,
         self.ref_count) = struct.unpack_from(">5I", raw, 0)
        self.data = raw[HEADER_SIZE:HEADER_SIZE + self.data_size]
        roots_off = HEADER_SIZE + self.data_size + self.reloc_count * 4
        strings_off = roots_off + (self.root_count + self.ref_count) * 8
        self.roots = {}
        for i in range(self.root_count):
            off, name_off = struct.unpack_from(">2I", raw, roots_off + i * 8)
            start = strings_off + name_off
            name = raw[start:raw.index(b"\0", start)].decode("ascii")
            self.roots[name] = off

    def u32(self, off):
        return struct.unpack_from(">I", self.data, off)[0]

    def f32(self, off):
        return struct.unpack_from(">f", self.data, off)[0]

    def cstr(self, off):
        return self.data[off:self.data.index(b"\0", off)].decode("ascii")


class Subaction:
    __slots__ = ("index", "name", "short", "anim_offset", "anim_size",
                 "script", "flags", "frames")


def short_name(name):
    m = re.match(r".*ACTION_(.*?)_figatree", name)
    return m.group(1) if m else name


def anim_frames(aj, offset, size):
    """Frame count of the figatree stored at offset in the AJ file."""
    if aj is None or size == 0:
        return None
    sub = Dat(aj[offset:offset + size])
    root = next(iter(sub.roots.values()))
    # HSD_FigaTree: s32 type, u32 pad, f32 frames, ...
    return sub.f32(root + 8)


class FighterDat:
    def __init__(self, raw, aj=None):
        self.dat = Dat(raw)
        name = next(n for n in self.dat.roots if n.startswith("ftData"))
        self.root_name = name
        self.root = self.dat.roots[name]
        d = self.dat
        self.attrs_off = d.u32(self.root + 0x00)
        self.ext_attrs_off = d.u32(self.root + 0x04)
        table = d.u32(self.root + 0x0C)
        table_end = d.u32(self.root + 0x14)
        count = (table_end - table) // SUBACTION_SIZE
        self.subactions = []
        for i in range(count):
            o = table + i * SUBACTION_SIZE
            name_off, a_off, a_size, script, flags, _ = struct.unpack_from(
                ">6I", d.data, o)
            s = Subaction()
            s.index = i
            s.name = d.cstr(name_off) if name_off else ""
            s.short = short_name(s.name)
            s.anim_offset, s.anim_size = a_off, a_size
            s.script = script
            s.flags = flags
            s.frames = anim_frames(aj, a_off, a_size) if s.name else None
            self.subactions.append(s)
