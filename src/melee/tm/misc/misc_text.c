/**
 * @file
 * Ports of TM-CE's Misc text changes:
 *
 * - Text Modifications/Add Symbols to ASCII-Menu Text Lookup Table.asm
 * - Text Modifications/Make Spaces Store 0x1A.asm
 * - Text Modifications/Make Spaces Not Store 00s.asm
 * - Text Modifications/Parse Numbers Correctly.asm
 * - Text - Increment Max Size.asm
 *
 * All five patch HSD_SisLib_803A67EC, the ASCII to SIS text encoder used by
 * HSD_SisLib_803A6B98 and friends (Text_AddSubtext in MexTK), so they are
 * one edited copy of it behind a `function` hook. Plus the SIS text heap
 * sizes (Increase CSS / In-Game SIS Text Heap.asm).
 */
#include "misc.h"

#include <sysdolphin/baselib/sislib.h>

/// sysdolphin/baselib (statics with unique names): the SJIS -> font glyph
/// lookup HSD_SisLib_803A67EC searches.
typedef struct TmMiscSjis {
    u8 lead;
    u8 trail;
} TmMiscSjis;
typedef struct TmMiscGlyph {
    u8 hi;
    u8 lo;
} TmMiscGlyph;
extern TmMiscSjis lbl_8040C8C0[];
extern TmMiscGlyph HSD_SisLib_8040C680[];

/// Entries in the lookup above (ARRAY_SIZE(HSD_SisLib_FontAtlas) in
/// hsd_3A64.c; the loop count in the vanilla code is 287).
#define TM_MISC_GLYPHS 287

/// SIS opcode that starts a new line.
#define SIS_NEWLINE 0x03

/// Add Symbols: ASCII characters TM-CE maps to full-width SJIS glyphs
/// without touching the kerning state. A trail of 0 marks "\n".
static const u8 tm_misc_symbols[][3] = {
    { '!', 0x81, 0x49 }, { '/', 0x81, 0x5E }, { '.', 0x81, 0x44 },
    { '=', 0x81, 0x81 }, { '+', 0x81, 0x7B }, { '%', 0x81, 0x93 },
    { '\n', 0x03, 0x00 }, { '\'', 0x81, 0x66 }, { '>', 0x81, 0x84 },
    { '<', 0x81, 0x83 }, { '_', 0x81, 0x51 }, { '^', 0x81, 0x4F },
    { '?', 0x81, 0x48 }, { '|', 0x81, 0x62 }, { '(', 0x81, 0x69 },
    { ')', 0x81, 0x6A },
};

/// Same as sisBeginLine in hsd_3A64.c: start a kerned run.
static void beginKerning(u8* data, s32* out_idx, s32* has_kerning)
{
    s32 idx = *out_idx;
    if (*has_kerning == 0) {
        data[idx++] = 0xA;
        data[idx++] = 0xF4;
        data[idx++] = 0x0;
        data[idx++] = 0x0;
        data[idx++] = 0x0;
        *has_kerning += 1;
    }
    *out_idx = idx;
}

/// Same as sisEndKerning in hsd_3A64.c (writes the end code whether or
/// not a kerned run is open).
static void endKerning(u8* data, s32* out_idx, s32* has_kerning)
{
    data[(*out_idx)++] = 0xB;
    *has_kerning = 0;
}

/// Replaces HSD_SisLib_803A67EC (`function` hook). Differences from
/// vanilla, all from TM-CE:
///
/// - Add Symbols: the characters in #tm_misc_symbols are looked up first
///   and emitted as their full-width glyph, with no kerning change; '\n'
///   emits the SIS newline code. (Vanilla has no glyph for most of them;
///   it did handle '.' and '\'' but toggled kerning.)
/// - Make Spaces Store 0x1A / Not Store 00s: a space never starts a kerned
///   run. (The two patches together leave only the glyph.)
/// - Parse Numbers Correctly: neither does a digit.
/// - Text - Increment Max Size: no 128-character limit; the input is read
///   up to its terminator.
s32 tm_misc_SisEncode(u8* data, u8* string)
{
    u8* str_cursor;
    s32 lut_idx;
    s32 in_idx;
    s32 out_idx;
    s32 has_kerning[1];
    u8 cur_char;
    u8 sjis_hi;
    u8 sjis_lo;
    int k;

    has_kerning[0] = 0;
    str_cursor = string;
    out_idx = 0;
    for (in_idx = 0;; in_idx++, str_cursor++) {
        cur_char = string[in_idx];
        if (cur_char == '\0') {
            if (has_kerning[0] != 0) {
                data[out_idx++] = 0xB;
            }
            break;
        }

        for (k = 0; k < (int) ARRAY_SIZE(tm_misc_symbols); k++) {
            if (tm_misc_symbols[k][0] == cur_char) {
                break;
            }
        }
        if (k < (int) ARRAY_SIZE(tm_misc_symbols)) {
            if (cur_char == '\n') {
                data[out_idx++] = SIS_NEWLINE;
                continue;
            }
            sjis_hi = tm_misc_symbols[k][1];
            sjis_lo = tm_misc_symbols[k][2];
        } else if (cur_char == ' ') {
            sjis_hi = 0x81;
            sjis_lo = 0x40;
        } else if (cur_char == '"') {
            endKerning(data, &out_idx, has_kerning);
            sjis_hi = 0x81;
            sjis_lo = 0x68;
        } else if (cur_char == ',') {
            endKerning(data, &out_idx, has_kerning);
            sjis_hi = 0x81;
            sjis_lo = 0x43;
        } else if (cur_char == '-') {
            endKerning(data, &out_idx, has_kerning);
            sjis_hi = 0x81;
            sjis_lo = 0x7C;
        } else if ((cur_char >= '0') && (cur_char <= '9')) {
            sjis_hi = 0x82;
            sjis_lo = string[in_idx] + 0x1F;
        } else if (cur_char == ':') {
            beginKerning(data, &out_idx, has_kerning);
            sjis_hi = 0x81;
            sjis_lo = 0x46;
        } else if ((cur_char >= 'A') && (cur_char <= 'Z')) {
            endKerning(data, &out_idx, has_kerning);
            sjis_hi = 0x82;
            sjis_lo = string[in_idx] + 0x1F;
        } else if ((cur_char >= 'a') && (cur_char <= 'z')) {
            endKerning(data, &out_idx, has_kerning);
            sjis_hi = 0x82;
            sjis_lo = string[in_idx] + 0x20;
        } else {
            endKerning(data, &out_idx, has_kerning);
            sjis_hi = string[in_idx++];
            sjis_lo = str_cursor[1];
            str_cursor += 1;
        }
        for (lut_idx = 0; lut_idx < TM_MISC_GLYPHS; lut_idx++) {
            if ((sjis_hi == lbl_8040C8C0[lut_idx].lead) &&
                (sjis_lo == lbl_8040C8C0[lut_idx].trail))
            {
                data[out_idx++] = HSD_SisLib_8040C680[lut_idx].hi;
                data[out_idx++] = HSD_SisLib_8040C680[lut_idx].lo;
                break;
            }
        }
    }
    data[out_idx] = 0;
    return out_idx;
}

/// Wraps the `HSD_SisLib_803A6048` call in preloadState for the CSS
/// (+0x58).
///
/// Port of Increase CSS SIS Text Heap.asm, which patches the `li r3,0x2400`
/// before this call to 0x4800. That instruction (0x801A3F9C) is a Slippi
/// injection site, so the size is raised here instead, never lowered.
void tm_misc_CssTextHeap(size_t size)
{
    if (size < 0x4800) {
        size = 0x4800;
    }
    HSD_SisLib_803A6048(size);
}
