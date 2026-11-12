#ifndef MELEE_TM_TEST_TMTEST_H
#define MELEE_TM_TEST_TMTEST_H

/*
 * Agent-first test runner (test builds only: TM_TEST=1, see
 * tools/tmtest.py and docs/ai/testing.md).
 *
 * A test build boots straight into one event's match with the characters,
 * stage and RNG seed in `tm_test_config`, plays a scripted input sequence on
 * port 1 frame-exactly, and reports through OSReport lines starting with
 * "TMTEST " followed by one JSON object. Nothing depends on menus or on
 * wall-clock pad timing, so a run is deterministic and works the same in
 * Dolphin (tools/tmtest.py reads the log) and in tools/melee_sim (which
 * hooks OSReport).
 *
 * `tm_test_config` is a global at a fixed symbol: the runner patches it into
 * the DOL (or writes it into memory) before boot. Shared by native and
 * TM-CE code, so plain C types only.
 */

#define TM_TEST_MAGIC 0x544D5453 /* 'TMTS' */
#define TM_TEST_MAX_INPUTS 128
#define TM_TEST_MAX_OPTIONS 16
#define TM_TEST_NONE 0xFF
/// Option index that, for the "course" event, selects the drill (value =
/// CourseDrillId) instead of a menu option. A spec's "drill" key.
#define TM_TEST_OPT_DRILL 0xFF

/// When an input entry starts.
enum TmTestTrigger {
    TM_TEST_AT_FRAME,      ///< `frame` = match frame (0 = first frame)
    TM_TEST_ON_ENTER,      ///< `frame` frames after `port` enters `state`
    TM_TEST_ON_EXIT,       ///< `frame` frames after `port` leaves `state`
};

/// Pad buttons (PAD_BUTTON_* values).
#define TM_TEST_A 0x0100
#define TM_TEST_B 0x0200
#define TM_TEST_X 0x0400
#define TM_TEST_Y 0x0800
#define TM_TEST_START 0x1000
#define TM_TEST_Z 0x0010
#define TM_TEST_R 0x0020
#define TM_TEST_L 0x0040
#define TM_TEST_DLEFT 0x0001
#define TM_TEST_DRIGHT 0x0002
#define TM_TEST_DDOWN 0x0004
#define TM_TEST_DUP 0x0008

typedef struct TmTestInput {
    unsigned char trigger;  ///< TmTestTrigger
    unsigned char port;     ///< fighter slot watched by ON_ENTER/ON_EXIT
    unsigned short state;   ///< action state for ON_ENTER/ON_EXIT
    unsigned short frame;   ///< frame, or delay after the trigger
    unsigned short hold;    ///< frames held (0 = 1)
    unsigned short buttons; ///< TM_TEST_* buttons
    signed char lx, ly;     ///< main stick, -127..127 (PAD values)
    signed char cx, cy;     ///< C-stick
    unsigned char l, r;     ///< analog triggers 0..255
} TmTestInput;

typedef struct TmTestOption {
    unsigned char index; ///< option index in the event's main menu
    unsigned char pad;
    short value;
} TmTestOption;

typedef struct TmTestConfig {
    unsigned int magic;        ///< TM_TEST_MAGIC when filled in
    char event[16];            ///< EventDesc.eventFile, e.g. "shineoos"
    unsigned char hmn_ckind;   ///< external character id, NONE = event's
    unsigned char hmn_color;
    unsigned char cpu_ckind;   ///< NONE = event's choice
    unsigned char cpu_color;
    unsigned short stage;      ///< external stage id, 0xFFFF = event's
    unsigned short trace;      ///< log fighters every N frames, 0 = never
    unsigned int seed;         ///< RNG seed at match start
    unsigned int max_frames;   ///< match frames before "done"
    unsigned int option_count;
    TmTestOption options[TM_TEST_MAX_OPTIONS];
    unsigned int input_count;
    TmTestInput inputs[TM_TEST_MAX_INPUTS];
} TmTestConfig;

extern TmTestConfig tm_test_config;

/// Match frames since the test match started, -1 before.
int tm_test_Frame(void);

/// @name Called from shared code in test builds (#ifdef TM_TEST)
/// @{
void tm_test_OnEventModeLoad(void); ///< css area: skip the CSS
void tm_test_OnMatchEnter(void);    ///< tm_event_start.c: wait for loads
/// @}

/// @name TM-CE side (src/tmce/test_bridge.c)
/// @{
/// Set option `index` of event `file`'s main menu. 0 if no such option.
int tmce_test_SetOption(const char* file, int index, int value);
/// @}

#endif
