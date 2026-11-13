/** @file
 * Particle banks, converted for the host.
 *
 * A particle bank is a block the game "locates" itself
 * (psInitDataBankLocate): a header and a table of offsets into the block,
 * which it turns into pointers. The entries of a command bank are command
 * lists, a fixed header of 16-bit fields, words and floats followed by byte
 * code; those of a texture bank are texture groups, words and a table of
 * offsets to pixel data.
 *
 * The generated readers know a bank only as an array of words. So the host
 * goes back to the bank's bytes as they are in the file, puts the headers
 * and tables in the host's byte order where they lie, and hands that to the
 * game's own locate and load functions, which then run unchanged. Byte code
 * and pixel data stay as they are on the disc (the one multi-byte operand
 * the interpreter reads, a float, is read in disc order: see PATCHES in
 * tools/native_build.py).
 *
 * Particles have to run even with nothing drawn: they draw from the game's
 * random number generator every frame.
 */
#include "host.h"

#include <string.h>

void psInitDataBankLocate_vanilla(int* cmd_bank, int* tex_bank,
                                  int* form_bank);
void psInitDataBankLoad_vanilla(int bank, const int* cmd_bank,
                                const int* tex_bank, const unsigned* ref,
                                const int* form_bank);

static uint32_t be32(const uint8_t* p)
{
    return (uint32_t) p[0] << 24 | (uint32_t) p[1] << 16 |
           (uint32_t) p[2] << 8 | p[3];
}

static uint32_t word(uint8_t* p)
{
    uint32_t v = be32(p);
    memcpy(p, &v, 4);
    return v;
}

static uint16_t half(uint8_t* p)
{
    uint16_t v = (uint16_t) (p[0] << 8 | p[1]);
    memcpy(p, &v, 2);
    return v;
}

/* --- which banks are already in host order -------------------------------- */

#define MAX_BANKS 256
static const uint8_t* converted[MAX_BANKS];

static int is_converted(const uint8_t* bank)
{
    for (int i = 0; i < MAX_BANKS; i++) {
        if (converted[i] == bank) {
            return 1;
        }
    }
    return 0;
}

static void set_converted(const uint8_t* bank)
{
    for (int i = 0; i < MAX_BANKS; i++) {
        if (converted[i] == NULL) {
            converted[i] = bank;
            return;
        }
    }
    host_fatal("too many particle banks");
}

void host_particles_forget(const uint8_t* data, uint32_t size)
{
    for (int i = 0; i < MAX_BANKS; i++) {
        if (converted[i] != NULL && converted[i] >= data &&
            converted[i] < data + size)
        {
            converted[i] = NULL;
        }
    }
}

/* --- conversion ------------------------------------------------------------ */

/// Offsets already handled within one bank: several table entries can name
/// the same list or group.
#define MAX_SEEN 4096
static uint32_t seen[MAX_SEEN];
static int nseen;

static int first_time(uint32_t offset)
{
    for (int i = 0; i < nseen; i++) {
        if (seen[i] == offset) {
            return 0;
        }
    }
    if (nseen == MAX_SEEN) {
        host_fatal("particle bank with too many entries");
    }
    seen[nseen++] = offset;
    return 1;
}

static void convert_cmd_bank(uint8_t* bank)
{
    uint16_t version = half(bank);
    uint32_t count, table;

    half(bank + 2);
    nseen = 0;
    switch (version) {
    case 0:
        count = word(bank + 4);
        table = 8;
        break;
    case 0x40:
    case 0x41:
    case 0x42:
    case 0x43:
        word(bank + 4);
        count = word(bank + 8);
        table = 12;
        break;
    default:
        host_fatal("particle command bank of unknown version %x", version);
    }
    for (uint32_t i = 0; i < count; i++) {
        uint32_t offset = word(bank + table + 4 * i);
        uint8_t* list = bank + offset;
        if (offset == 0 || !first_time(offset)) {
            continue;
        }
        /* HSD_PSCmdList: four 16-bit fields, then words and floats up to
           the byte code at 0x3C. */
        for (int at = 0; at < 8; at += 2) {
            half(list + at);
        }
        for (int at = 8; at < 0x3C; at += 4) {
            word(list + at);
        }
    }
}

static void convert_tex_bank(uint8_t* bank)
{
    uint32_t groups = word(bank);

    nseen = 0;
    for (uint32_t i = 1; i <= groups; i++) {
        uint32_t offset = word(bank + 4 * i);
        uint8_t* g = bank + offset;
        uint32_t num, fmt, entries;
        uint16_t palnum, palflag;
        if (offset == 0 || !first_time(offset)) {
            continue;
        }
        /* HSD_PSTexGroup */
        num = word(g);
        fmt = word(g + 4);
        word(g + 8);
        word(g + 0xC);
        word(g + 0x10);
        palnum = half(g + 0x14);
        palflag = half(g + 0x16);
        entries = num;
        /* Colour-indexed formats have palettes after the textures, as
           psInitDataBankLocate counts them. */
        if (fmt == 8 || fmt == 9 || fmt == 10) {
            if (palflag & 1) {
                entries = num + 1;
            } else if (palnum != 0) {
                entries = num + palnum;
            } else {
                entries = num * 2;
            }
        }
        for (uint32_t t = 0; t < entries; t++) {
            word(g + 0x18 + 4 * t);
        }
    }
}

/* --- the game's entry points ------------------------------------------------ */

void psInitDataBankLocate(int* cmd_bank, int* tex_bank, int* form_bank)
{
    uint8_t* cmd = host_dat_raw(cmd_bank);
    uint8_t* tex = host_dat_raw(tex_bank);

    if (form_bank != NULL) {
        host_fatal("particle form banks are not converted");
    }
    if (is_converted(cmd)) {
        return; /* located already, as the game's own callers ensure */
    }
    convert_cmd_bank(cmd);
    convert_tex_bank(tex);
    set_converted(cmd);
    psInitDataBankLocate_vanilla((int*) cmd, (int*) tex, NULL);
}

void psInitDataBankLoad(int bank, const int* cmd_bank, const int* tex_bank,
                        const unsigned* ref, const int* form_bank)
{
    psInitDataBankLoad_vanilla(bank, host_dat_raw(cmd_bank),
                               host_dat_raw(tex_bank), ref, form_bank);
}

void psInitDataBank(int bank, int* cmd_bank, int* tex_bank, unsigned* ref,
                    int* form_bank)
{
    if (bank < 65) {
        psInitDataBankLocate(cmd_bank, tex_bank, form_bank);
        psInitDataBankLoad(bank, cmd_bank, tex_bank, ref, form_bank);
    }
}
