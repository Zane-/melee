#!/usr/bin/env python3
"""Build the native (32-bit Linux) headless game: build/native/melee_headless.

The game's own sources are compiled for the host by upstream's CMake preset
(`native`), into libmelee.a, with the generated archive readers. This script
adds what a program needs on top:

- the vanilla files that preset leaves out, compiled unchanged with a shim
  header (src/host/shim.h) for the SDK declarations they need;
- the host platform layer (src/host/): memory, time, disc, pads, and
  graphics and audio as no-ops;
- Aurora's C matrix and vector functions;
- a generated stub, returning 0, for every SDK function still missing.

Needs (see docs/ai/native-port.md): a multilib gcc, the Aurora headers, and
the archive tool and type table built through Nix:

    nix build .#melee-dwarf -o build/nix/dwarf
    nix build .#melee-dat   -o build/nix/melee-dat
    build/nix/melee-dat/bin/melee-dat types export \\
        -o build/GALE01/dat/types.bin --dwarf build/nix/dwarf/melee.elf

Usage: python tools/native_build.py [--opt LEVEL] [--no-cmake]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

if sys.platform == "win32" and not sys.flags.utf8_mode:
    # Sources are UTF-8 (some hold Japanese text); Windows' default codec
    # is not. UTF-8 mode makes every file read and pipe decode use it.
    sys.exit(subprocess.call([sys.executable, "-X", "utf8", *sys.argv]))

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "native"
OBJ = OUT / "host"
AURORA = Path(os.environ.get("AURORA_SRC", ROOT / "build/deps/aurora"))
# Windows (MSYS2's i686 MinGW-w64 gcc on PATH): docs/ai/windows.md. The
# archive tool is built there with cargo, not Nix.
WIN32 = sys.platform == "win32"
MELEE_DAT = Path(os.environ.get(
    "MELEE_DAT",
    ROOT / ("build/cargo/release/melee-dat.exe" if WIN32
            else "build/nix/melee-dat/bin/melee-dat")))
# The POSIX stand-ins the host layer needs on Windows (src/host/win32/).
WIN32_HOST = [f"-I{ROOT}/src/host/win32",
              "-include", str(ROOT / "src/host/win32/posix.h")]

# Floating point is done in SSE, in the precision the source asks for, as
# the console's FPU does; x87 would compute everything in extended precision.
# The console's compiler fuses a multiply and an add into one instruction
# with one rounding (fmadds) wherever the product has no other use, also
# across statements; -mfma with -ffp-contract=fast is gcc's nearest
# equivalent, and only acts when optimising. The two compilers do not always
# choose the same places.
# Optimising, gcc emits a file's globals in an order of its own and drops
# the static ones nothing names; unoptimised it keeps both as in the source,
# and so (in a file's own data) as on the console. Code that reaches a
# global through its neighbour (kind 5 in docs/ai/native-port.md: all of
# Venom's tables, through grVe_803E5348) then reads something else, or
# calls it: Venom crashed at -O2 as it loaded. -fno-toplevel-reorder keeps
# the unoptimised layout at every level.
BASE_FLAGS = [
    "-m32", "-std=gnu2x", "-g", "-fno-pie", "-fno-strict-aliasing",
    "-fwrapv", "-fno-delete-null-pointer-checks", "-fno-omit-frame-pointer",
    "-fno-toplevel-reorder",
    "-msse2", "-mfpmath=sse", "-mfma", "-w",
]
DEFINES = ["-DTARGET_PC", "-Dbool=int"]

# Vanilla files built here, unchanged: the ones upstream's preset excludes,
# and any file one of whose functions the host layer replaces. A
# `-Dname=name_vanilla` renames that function so src/host/ can supply its
# own: the native counterpart of the overlay's `function` hook. (An object
# linked here defines everything its copy in libmelee.a does, so that copy
# is never pulled in.)
VANILLA = {
    # Which music the game last started (audio.c, host_pstream_start): the
    # client puts the stage's back after its menu music. Music the game
    # starts or stops while nobody hears it waits for that to end
    # (host_audio_quiet).
    "melee/lb/lbaudio_ax.c": [
        "-DHSD_AudioPStreamStartChParam=host_pstream_start",
        "-DAXDriverStop=host_axdriver_stop"],
    "melee/gm/gmmain.c": ["-Dmain=game_main"],
    "melee/lb/lb_0195.c": ["-Dlb_80019894=lb_80019894_vanilla"],
    # A frame played ahead (src/host/ahead.c) must not end the scene: the
    # scene loop would return before the lookahead could be undone. A
    # forked game (engine.c, "engine fork") thinks and draws nothing: the
    # scene loop's render calls are the host's, and do nothing there.
    "melee/gm/gmscene.c": ["-Dgm_801A4B60=gm_801A4B60_vanilla",
                           "-Dgm_801A4B74=gm_801A4B74_vanilla",
                           "-DHSD_StartRender=host_scene_start_render",
                           "-DHSD_VICopyXFBAsync=host_scene_copy_xfb",
                           "-DGXInvalidateVtxCache=host_scene_invalidate_vtx",
                           "-DGXInvalidateTexAll=host_scene_invalidate_tex"],
    "melee/lb/lbcardnew.c": [],
    "sysdolphin/baselib/fog.c": [],
    "sysdolphin/baselib/pobj.c": [],
    # Palettes go to the graphics layer through the shim (shim.h).
    "sysdolphin/baselib/tobj.c": [],
    "sysdolphin/baselib/sobjlib.c": [],
    "sysdolphin/baselib/sislib_font.c": [],
    "sysdolphin/baselib/hsd_3915.c": [],
    "sysdolphin/baselib/video.c": [
        "-DHSD_VICopyXFBAsync=HSD_VICopyXFBAsync_vanilla",
        "-DHSD_VIWaitXFBFlush=HSD_VIWaitXFBFlush_vanilla",
    ],
    # The draw pass is optional (--draw): src/host/cuts.c.
    "sysdolphin/baselib/gobj.c": [
        "-DHSD_GObj_80390FC0=HSD_GObj_80390FC0_vanilla",
    ],
    # Relocating a copied archive is loading it again (src/host/archive.c).
    "melee/lb/lbarchive.c": ["-DlbArchiveRelocate=lbArchiveRelocate_vanilla"],
    # It copies a sound header table onto itself, shifted down: the
    # console's memcpy copies forwards, which is what memmove does here.
    "sysdolphin/baselib/synth.c": ["-Dmemcpy=memmove"],
    # Random draws can be logged with their callers (src/host/debug.c).
    "sysdolphin/baselib/random.c": [
        "-DHSD_Rand=HSD_Rand_vanilla", "-DHSD_Randf=HSD_Randf_vanilla",
        "-DHSD_Randi=HSD_Randi_vanilla",
    ],
    # Particle banks are converted first (src/host/particles.c).
    "sysdolphin/baselib/particle.c": [
        "-DpsInitDataBankLocate=psInitDataBankLocate_vanilla",
        "-DpsInitDataBankLoad=psInitDataBankLoad_vanilla",
        "-DpsInitDataBank=psInitDataBank_vanilla",
    ],
    # UCF 0.84 (src/melee/tm/ucf/, src/host/ucf.c): every call and table
    # entry the overlay hooks for it (config/GALE01/tm_hooks/ucf.txt) goes
    # to the C version instead. These files call those functions and do not
    # define them, so a rename reaches exactly those sites; the two calls
    # in Fighter_procInput and the one before the hitlag callback are
    # patches (PATCHES, fighter.c).
    **{rel: ["-D%s=tm_ucf_%s" % (fn, fn.split("_", 1)[1]) for fn in fns]
       for rel, fns in {
        "melee/ft/kinds/ftCommon/ftCo_Wait.c": ["ftCo_80099794"],
        "melee/ft/kinds/ftCommon/ftCo_AppealS.c": ["ftCo_80099794"],
        "melee/ft/kinds/ftSamus/ftsamusspeciallw0.c": ["ftCo_80099794"],
        "melee/ft/kinds/ftYoshi/ftyoshiguard.c": [
            "ftCo_80099794", "ftCo_8009A080"],
        "melee/ft/kinds/ftCommon/ftCo_Guard.c": [
            "ftCo_8009980C", "ftCo_8009A080"],
        "melee/ft/kinds/ftCommon/ftCo_SquatWait.c": [
            "ftCo_SquatRv_CheckInput"],
        "melee/ft/kinds/ftCommon/ftCo_Damage.c": ["ftCo_DamageFall_IASA"],
        "melee/ft/kinds/ftCommon/ftCo_ItemParasolDamageFall.c": [
            "ftCo_DamageFall_IASA"],
        # the Turn and DamageFall states' input callbacks
        "melee/ft/ftmotionstates.c": [
            "ftCo_Turn_IASA", "ftCo_DamageFall_IASA"],
       }.items()},
}

# Source patches: exact text replaced in a copy of a vanilla file before it
# is compiled here (the file in the repository is not touched). For the few
# places where the game's code depends on how the console lays data out in
# memory and no function boundary separates that from the rest. A patch
# whose text is no longer found, or found a different number of times than
# the patch says (once unless given), stops the build.
PATCHES = {
    # The game's audio RAM arena stops at 16 MB, the console's. The host has
    # more (HOST_ARAM_SIZE): what does not fit the preload heap (a drill's
    # many opponents' animations) loads into the rest when a fighter is
    # made (src/host/match.c). Audio RAM is not part of the game's state.
    "melee/lb/lbmemory.c": [
        ("_p(a_arenaHi) = (ARGetSize() > 0x01000000U) ? 0x01000000U : "
         "ARGetSize();",
         "_p(a_arenaHi) = ARGetSize();"),
    ],
    # UCF (see VANILLA): Fighter_procInput's first ftCo_IsCpuControlled
    # (+0xC4 on the console) hands UCF the fighter, its one lb_8000D148
    # (+0x738) is where UCF keeps the stick's history and snaps cardinals,
    # and the hitlag callback is run through UCF's SDI (Fighter_procUpdate,
    # after the call at +0x5D0).
    "melee/ft/fighter.c": [
        ('#include "fighter.h"\n',
         '#include "fighter.h"\n#include "melee/tm/ucf/ucf.h"\n'
         'void host_moves_filter(Fighter* fp);\n'
         'void host_moves_sticks(Fighter* fp);\n'),
        # A Versus mode's moves (src/host/moves.c): the buttons and C-stick
        # a fighter's rule leaves, as soon as they are read, a person's,
        # a model's and the game CPU's alike.
        ("""            if (ftCo_IsCpuControlled(fp)) {
                fp->input.held_buttons[0] = ftCo_GetCpuButtons(fp);
            } else {
                fp->input.held_buttons[0] =
                    HSD_PadGameStatus[fp->pad_port].button;
            }
""",
         """            if (ftCo_IsCpuControlled(fp)) {
                fp->input.held_buttons[0] = ftCo_GetCpuButtons(fp);
            } else {
                fp->input.held_buttons[0] =
                    HSD_PadGameStatus[fp->pad_port].button;
            }
            host_moves_filter(fp);
"""),
        # and the C-stick again once UCF has read the pad (its PadBuffer,
        # in tm_ucf_8000D148 just above, snaps a stick at the rim from the
        # raw pad)
        ("""                fp->activity_timer.lstick.y = 0;
                fp->activity_timer.lstick.x = 0;
            }

            // Fighter_ClampSpecificValue
            fp->active_duration.trigger++;""",
         """                fp->activity_timer.lstick.y = 0;
                fp->activity_timer.lstick.x = 0;
            }
            host_moves_sticks(fp);

            // Fighter_ClampSpecificValue
            fp->active_duration.trigger++;"""),
        ("""            if (ftCo_IsCpuControlled(fp)) {
                SET_STICKS(fp->input.lstick[0].x, fp->input.lstick[0].y,
                           ftCo_GetCpuLStickX(fp), ftCo_GetCpuLStickY(fp));""",
         """            if (tm_ucf_IsCpuControlled(fp)) {
                SET_STICKS(fp->input.lstick[0].x, fp->input.lstick[0].y,
                           ftCo_GetCpuLStickX(fp), ftCo_GetCpuLStickY(fp));"""),
        ("if (lb_8000D148(fp->input.lstick[1].x, fp->input.lstick[1].y,",
         "if (tm_ucf_8000D148(fp->input.lstick[1].x, fp->input.lstick[1].y,"),
        ("""    ftColl_80076528(gobj);

    if (fp->hitlag_cb) {""",
         """    ftColl_80076528(gobj);
    tm_ucf_PreHitlag(gobj);

    if (fp->hitlag_cb) {"""),
    ],
    # A Versus mode's end decided in the game's frame (src/host/rules.c):
    # the match's outcome asks the host's rule after the timer, before the
    # stocks.
    "melee/gm/gmvs.c": [
        ('#include "gmvs.h"\n', '#include "gmvs.h"\nint host_rules_outcome(void);\n'),
        ("""    if (!controller.start.is_teams) {
        ffa_outcome = gm_GetFFAOutcome();""",
         """    {
        MatchOutcome host_outcome = (MatchOutcome) host_rules_outcome();
        if (host_outcome != OUTCOME_NONE) {
            return host_outcome;
        }
    }
    if (!controller.start.is_teams) {
        ffa_outcome = gm_GetFFAOutcome();"""),
    ],
    # The particle interpreter's one multi-byte operand: a float, copied
    # byte by byte from byte code that stays in disc order.
    "sysdolphin/baselib/particle.c": [
        ("""    ((ParticleFloatBytes*) &hsd_804D78D0)->bytes[0] = *p++;
    ((ParticleFloatBytes*) &hsd_804D78D0)->bytes[1] = *p++;
    ((ParticleFloatBytes*) &hsd_804D78D0)->bytes[2] = *p++;
    ((ParticleFloatBytes*) &hsd_804D78D0)->bytes[3] = *p++;
""",
         """    ((ParticleFloatBytes*) &hsd_804D78D0)->bytes[3] = *p++;
    ((ParticleFloatBytes*) &hsd_804D78D0)->bytes[2] = *p++;
    ((ParticleFloatBytes*) &hsd_804D78D0)->bytes[1] = *p++;
    ((ParticleFloatBytes*) &hsd_804D78D0)->bytes[0] = *p++;
"""),
        # Three globals addressed as one struct laid over them.
        ("head = &data->particle[gen->linkNo];",
         "head = &hsd_804D0908[gen->linkNo];"),
        ("if (data->jobj[jidx] != NULL) {",
         "if (psPointJObj[jidx] != NULL) {"),
        ("HSD_JObjUnref(data->jobj[jidx]);",
         "HSD_JObjUnref(psPointJObj[jidx]);"),
        ("data->jobj[jidx] = NULL;", "psPointJObj[jidx] = NULL;"),
        ("HSD_ObjFree(&data->alloc_data, prt);",
         "HSD_ObjFree(&hsd_804D0F60.alloc_data, prt);"),
    ],
    # Two tables addressed as "what follows this other table in memory".
    # Samus's grapple beam, pulling its links in: the first coordinate is
    # read through `dir_ptr` one line before it is pointed at `dir`. The
    # retail code reads `dir` itself there (`lfs f1,40(r1)`, the address it
    # has just passed on); natively it read through whatever the stack
    # held, a wrong number or a crash.
    "melee/it/kinds/itsamusgrapple.c": [
        ("            link->pos.x = (dir_ptr->x * attrs->x38) + head->pos.x;\n"
         "            dir_ptr = &dir;\n",
         "            dir_ptr = &dir;\n"
         "            link->pos.x = (dir_ptr->x * attrs->x38) + head->pos.x;\n"),
    ],
    # A CPU fighter hit with no knockback to speak of: the game sets its
    # stick from two variables it did not assign (upstream marks the bug).
    # On the console they are what two registers hold, one of them the low
    # byte of the fighter's own address, which has no native equivalent.
    # Here: a stick at rest, so that the native game is at least the same
    # game every time.
    "melee/ft/kinds/ftCommon/ftCo_0A01.c": [
        ("    s8 stick_x;\n    s8 stick_y;\n\n    data = &fp->cpu;\n"
         "    if (!fp->x221A_b3) {",
         "    s8 stick_x = 0;\n    s8 stick_y = 0;\n\n"
         "    data = &fp->cpu;\n    if (!fp->x221A_b3) {"),
        # A CPU that has been hit decides whether to go to its "being hit"
        # command (18, which steers against the knockback) by a variable
        # that this branch never assigns. In the retail code it is r31,
        # which the function does not touch before: the caller's. At 33 of
        # the 36 places the function is called from, the caller keeps a
        # pointer there (so: yes); at one it is 0, at two an argument.
        # Natively it was the stack's leftovers. Here: yes, always. This
        # changed matches (the Ice Climbers' partner is such a CPU).
        ("                data2->xFA_b1 = false;\n            }\n        }\n"
         "        if (switch_cmd != 0) {\n            ftCo_800B4A78(fp);\n"
         "            data->x18 = 0x12;",
         "                data2->xFA_b1 = false;\n            }\n"
         "            switch_cmd = 1;\n        }\n"
         "        if (switch_cmd != 0) {\n            ftCo_800B4A78(fp);\n"
         "            data->x18 = 0x12;"),
        # A CPU whose opponent is in the air with no floor below and no
        # platform edge that qualifies: ftCo_800A4768 fills nothing in and
        # the CPU walks towards whatever the stack held. Here: the middle
        # of the stage.
        ("    u8 _[0x18];\n    Vec3 sp18;\n    f32 fx;",
         "    u8 _[0x18];\n    Vec3 sp18 = { 0 };\n    f32 fx;"),
    ],
    # A stock icon's frame: `base` is never assigned for the first twenty
    # characters. The console's code leaves the character's number in the
    # register that holds it (checked in the retail code: `cmpwi r3,19;
    # ble` straight to the sum), so that is its value there; natively it
    # was whatever the stack held, and every icon was Captain Falcon's.
    "melee/gm/gm_1601.c": [
        ("f32 gm_80168B34(CharacterKind ckind, int arg1, int arg2)\n"
         "{\n    int base;",
         "f32 gm_80168B34(CharacterKind ckind, int arg1, int arg2)\n"
         "{\n    int base = ckind;"),
    ],
    # The fighter material class is read as one struct with the two
    # templates defined after it; on the console they follow it in memory.
    "melee/ft/ftmaterial.c": [
        ("info->texp_tmpl", "ftMaterial_803C6A44", 3),
        ("info->tevdesc_tmpl", "ftMaterial_803C69D0", 2),
    ],
    "melee/ft/ftdata.c": [
        ("(ftData_UnkCountStruct*) "
         "&CostumeListsForeachCharacter[Ft_Kind_Max];",
         "ftData_Table_Unk0;"),
        ("(ftData_UnkCountStruct*) "
         "((u8*) CostumeListsForeachCharacter + 5940);",
         "ftData_UnkIntPairs;"),
        ("((ft_8045993C_t*) &list[Ft_Kind_Max])[i]", "ft_8045993C[i]", 3),
    ],
    # The trophy tables, addressed from the struct that precedes them.
    "melee/ty/toy.c": [
        ("    base = (u8*) &_Toy_804A26B8;\n    save_data = "
         "gmMainLib_GetTrophyFlags();",
         "    base = (u8*) Toy_804A284C - 0x194;\n    save_data = "
         "gmMainLib_GetTrophyFlags();"),
        ("memzero(&userData->x194, 0x25A);", "memzero(Toy_804A284C, 0x25A);"),
    ],
    # A sound bank's end address, stored "32 entries past" one table: in
    # the table that follows it.
    "sysdolphin/baselib/synth.c": [
        ("HSD_Synth_804C2AE0[bank_id + 0x80 / 4] = (void*) offset;",
         "hsd_SynthSFXBank[bank_id] = (int) offset;"),
    ],
    # A sound file's load is known by the id its request returns, and the
    # callback that ends it looks the file up by that id to mark it loaded
    # and start the next. On the console the load ends later, after the id
    # has been stored; here a read completes inside the request, before,
    # so the callback found nothing and loaded the same file again: every
    # character's sounds twice, and a few matches with different opponents
    # overflowed the bank (an assertion in synth.c, 2026-11-13). The id is
    # the file's entry number: stored first, the callback finds it.
    "melee/lb/lbaudio_ax.c": [
        ("lbl_80433A64[slot] = HSD_SynthSFXLoad(cur_ssm_file, 2, fn_80026C04, 0);",
         "lbl_80433A64[slot] = DVDConvertPathToEntrynum(cur_ssm_file);\n"
         "        lbl_80433A64[slot] = "
         "HSD_SynthSFXLoad(cur_ssm_file, 2, fn_80026C04, 0);", 2),
    ],
    # The camera's descriptor, addressed from a struct laid over the
    # globals before it.
    "melee/cm/camera.c": [
        ("(struct CameraStaticData*) &cm_803BCB18;",
         "(struct CameraStaticData*) ((u8*) &cm_803BCB64 - "
         "offsetof(struct CameraStaticData, desc));"),
        # the match camera, for the host's "camera" command (src/host/
        # camera.c: a drill's camera, following its player at a distance)
        ("/* 452C68 */ static Camera game_camera;",
         "/* 452C68 */ static Camera game_camera;\n"
         "Camera* host_game_camera(void) { return &game_camera; }\n"
         "void host_camera_subject(Vec3* pos, int slot);"),
        # the free camera's subject (a fighter's bone, followed at half
        # the way each frame) eased by the host when a drill's camera
        # follows its player (src/host/camera.c)
        ("    while (!get_subject_pos(subject_pos, slot_ptr)) {\n"
         "        *slot_ptr = Camera_8002BA00(*slot_ptr, 1);\n"
         "    }\n",
         "    while (!get_subject_pos(subject_pos, slot_ptr)) {\n"
         "        *slot_ptr = Camera_8002BA00(*slot_ptr, 1);\n"
         "    }\n"
         "    host_camera_subject(subject_pos, *slot_ptr);\n"),
    ],
    # An image descriptor, addressed from a struct laid over the globals
    # before it.
    "melee/lb/lbrefract.c": [
        ("data->imagedesc0;", "imagedesc0;"),
    ],
    # A rotation read as four floats into a variable of three.
    "melee/lb/lb_020A.c": [
        ("    Vec3 rot;\n    Quaternion rot2;",
         "    struct { Vec3 v; f32 w; } rot_;\n#define rot rot_.v\n"
         "    Quaternion rot2;"),
    ],
    # Square roots stored to, and read back from, a stack slot outside the
    # function's own variables (where the original's temporary was).
    "melee/ft/ft_0899.c": [
        ("((volatile f32*) &sp1C)[-1]", "host_scratch_f32", 2),
    ],
    "melee/it/kinds/itlinkhookshot.c": [
        ("*(&y + 6)", "y", 2),
    ],
    "melee/lb/lbcollision.c": [
        ("sqrtf_store(n1, sqrt_tmp - 1)", "sqrtf_store(n1, &sqrt_tmp[0])"),
    ],
    # Item script words read through casts: they are in disc order.
    "melee/it/itanimlist.c": [
        ("((u16*) cmd->x8.u)[0]", "host_be_u16(cmd->x8.u, 0)", 2),
        ("((u16*) cmd->x8.u)[1]", "host_be_u16(cmd->x8.u, 1)", 2),
        ("((s16*) cmd->x8.u)[0]", "host_be_s16(cmd->x8.u, 0)", 3),
        ("((s16*) cmd->x8.u)[1]", "host_be_s16(cmd->x8.u, 1)", 3),
        ("*(u32*) cmd->x8.u;", "host_be_u32(cmd->x8.u);"),
    ],
    # Reads through a null pointer, written to pad a stack frame: the
    # console's compiler drops them, an unoptimised build executes them.
    "melee/ft/kinds/ftYoshi/ftyoshispecials.c": [
        ("    GET_FIGHTER(NULL);\n", "", 7),
    ],
    "melee/ft/kinds/ftCommon/ftCo_FlyReflect.c": [
        ("    GET_FIGHTER(0);\n", "", 2),
    ],
    # A script's goto and subroutine targets are offsets in the file.
    "melee/lb/lbcommand.c": [
        ("info->x8.u = info->x8.u->Command_05.ptr;",
         "info->x8.u = host_script_target(info->x8.u);"),
        ("info->x8.u = info->x8.u->Command_07.ptr;",
         "info->x8.u = host_script_target(info->x8.u);"),
        # Execute Loop reads the loop's start as x8.ptr[loop_count], in an
        # array declared with one element (what makes the function match),
        # and the count as event_return[loop_count - 1]. An index past a
        # declared bound is undefined behaviour: gcc, optimising (-O1 and
        # up), takes the index for 0 and drops the jump back as a no-op, so
        # every loop in a fighter's, an item's or a colour animation's
        # script ran its body once. The same words through the plain
        # pointer the function already uses: the console's addresses.
        ("    if ((s32) info->event_return[info->loop_count - 1]) {\n"
         "        info->x8.ptr[0] = &info->x8.ptr[info->loop_count][0];\n",
         "    if ((s32) ptr[info->loop_count + 3]) {\n"
         "        info->x8.u = (union CmdUnion*) ptr[info->loop_count + 2];\n"),
        # The return stack of loops and subroutines is declared with three
        # entries and uses up to five (the two words after it, as on the
        # console): the same words, through a pointer with no bound.
        ("info->event_return[",
         "((union CmdUnion**) ((u32*) info + 4))[", 4),
    ],
    # Brinstar's bubbles, which raise the floor's middle columns: the code
    # reads these three globals as one struct (grZe_BubbleState: four
    # positions, then the bubbles), as they lie on the console, 0x30 bytes
    # apart. Natively the third is aligned to 32 bytes and began 4 bytes
    # later, so every bubble was read 4 bytes off: none active, the middle
    # columns at x 0 (or NaN, optimised), and a fighter could fall through
    # the floor. One struct, laid out as on the console.
    "melee/gr/grzebes.c": [
        ("/* 8049F140 */ static Vec3 grZe_8049F140[2];\n"
         "/* 8049F158 */ static Vec3 grZe_8049F158[2];\n"
         "/* 8049F170 */ static grZe_BubbleEntry grZe_8049F170[20];\n",
         "/* 8049F140 */ static struct {\n"
         "    Vec3 x0[2];\n"
         "    Vec3 x18[2];\n"
         "    grZe_BubbleEntry x30[20];\n"
         "} host_grZe_8049F140;\n"
         "#define grZe_8049F140 (host_grZe_8049F140.x0)\n"
         "#define grZe_8049F158 (host_grZe_8049F140.x18)\n"
         "#define grZe_8049F170 (host_grZe_8049F140.x30)\n"),
    ],
    # The nth animation joint of a stage model: the next n in the file.
    "melee/gr/granime.c": [
        ("aj = &aj[arg2];", "aj = host_dat_element(aj, arg2, 0x14);"),
        ("mj = &mj[arg2];", "mj = host_dat_element(mj, arg2, 0xC);"),
        ("sj = &sj[arg2];", "sj = host_dat_element(sj, arg2, 0xC);"),
    ],
}

# Files that write vertex data straight to the console's command pipe
# (`GXWGFifo.f32 = x;`, an assignment to a hardware address). In a copy of
# each, every such write becomes a call of the function that puts the same
# value in the stream (GXParam1f32(x)): Aurora's in the window build, a stub
# in the headless one.
FIFO_FILES = ["melee/gm/gm_1832.c", "sysdolphin/baselib/hsd_3915.c",
              "sysdolphin/baselib/psdisp.c"]
FIFO_WRITE = re.compile(
    r"\bGXWGFifo\.(u8|s8|u16|s16|u32|s32|f32)\s*=\s*([^;]+);")

AURORA_C = ["mtx.c", "mtx44.c", "mtxvec.c", "quat.c", "vec.c"]

# Stubs that must not simply return 0 in eax: these return a float.
FLOAT_STUBS = set()


def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], cwd=ROOT, **kw)


def includes():
    return [
        f"-I{AURORA}/include", f"-I{ROOT}/src",
        f"-I{ROOT}/libs/doldecomp/include",
        f"-I{OUT}/dat-readers/schema",
        f"-I{ROOT}/tools/dat-cli/native/include",
        f"-I{ROOT}/build/GALE01/include",
    ]


def cmake(flags):
    """libmelee.a and the readers, through upstream's preset."""
    for need in (AURORA / "include/dolphin/os.h", MELEE_DAT,
                 ROOT / "build/GALE01/dat/types.bin"):
        if not need.exists():
            sys.exit(f"missing {need}: see docs/ai/native-port.md")
    cflags = " ".join(flags)
    stamp = OUT / "host_flags.txt"
    if not (OUT / "build.ninja").exists() or not stamp.exists() or \
            stamp.read_text() != cflags:
        env = dict(os.environ, AURORA_SRC=str(AURORA))
        toolchain = ([f"-DCMAKE_TOOLCHAIN_FILE={ROOT}/cmake/i686-mingw.cmake"]
                     if WIN32 else [])
        r = run(["cmake", "--preset", "native", "-B", OUT, *toolchain,
                 "-DMELEE_DAT_READERS=ON",
                 f"-DMELEE_DAT={MELEE_DAT}", f"-DCMAKE_C_FLAGS={cflags}"],
                env=env, capture_output=True, text=True)
        if r.returncode:
            sys.exit(r.stdout + r.stderr)
        OUT.mkdir(parents=True, exist_ok=True)
        stamp.write_text(cflags)
    r = run(["ninja", "-C", OUT, "melee", "dat_melee", "dat_native"],
            capture_output=True, text=True)
    if r.returncode:
        sys.exit("\n".join((r.stdout + r.stderr).splitlines()[-40:]))


def compile_one(job):
    src, obj, extra = job
    obj.parent.mkdir(parents=True, exist_ok=True)
    dep = obj.with_suffix(".d")
    if obj.exists() and dep.exists():
        newest = obj.stat().st_mtime
        deps = dep.read_text().replace("\\\n", " ").split(":", 1)[-1].split()
        key = obj.with_suffix(".cmd")
        if key.exists() and key.read_text() == " ".join(extra) and all(
                Path(d).exists() and Path(d).stat().st_mtime <= newest
                for d in deps):
            return None
    cc = "g++" if str(src).endswith(".cpp") else "gcc"
    cmd = [cc, *extra, "-MMD", "-MF", str(dep), "-c", str(src), "-o",
           str(obj)]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        return f"{src}:\n{r.stderr[-3000:]}"
    obj.with_suffix(".cmd").write_text(" ".join(extra))
    return None


def compile_all(jobs):
    with ThreadPoolExecutor(os.cpu_count()) as pool:
        errors = [e for e in pool.map(compile_one, jobs) if e]
    if errors:
        sys.exit("\n".join(errors))


def symbol_kinds():
    """name -> ('function' | 'object', size) from the matching build."""
    kinds = {}
    pat = re.compile(r"^(\S+) = \.\w+:0x[0-9A-Fa-f]+; // type:(\w+)"
                     r"(?: size:0x([0-9A-Fa-f]+))?")
    for line in (ROOT / "config/GALE01/symbols.txt").read_text().splitlines():
        m = pat.match(line)
        if m:
            kinds[m.group(1)] = (m.group(2), int(m.group(3) or "0", 16))
    return kinds


AURORA32 = ROOT / "build/aurora32/build"   # tools/aurora32/build.sh
WINDOW = False


def aurora_libs():
    """What Aurora's own example links, from its build, without the
    library that only holds a main()."""
    ninja = AURORA32 / "build.ninja"
    if not ninja.exists():
        sys.exit(f"missing {ninja}: run tools/aurora32/build.sh")
    text = ninja.read_text()
    at = text.index("build examples/simple:")
    line = re.search(r"^  LINK_LIBRARIES = (.*)$", text[at:], re.M).group(1)
    libs = []
    for item in line.split():
        if item.endswith("libaurora_main.a"):
            continue
        libs.append(item if item.startswith(("/", "-"))
                    else str(AURORA32 / item))
    return libs


# The game's statics, gathered into one section a rollback snapshot copies
# (src/host/state.c): everything of the game's library, the readers, the
# game files built here, and the host files whose state is the game's
# timeline (emulated time, completions, alarms, the disc's and audio RAM's
# bookkeeping, the AX voices, the archive tables, the game heap's base).
# Not the host's own side: the control protocol, the window, the interface,
# the adapter, the network, the snapshots themselves.
GAME_STATE_HOST = ("archive", "audio", "cuts", "dvd", "gameheap", "hw",
                   "main", "match", "os", "particles", "setup", "ucf")


def game_state_script():
    sections = "(.data .data.* .bss .bss.*)"
    inputs = ["*libmelee.a:*", "*libdat_melee.a:*", "*libdat_native.a:*",
              "*/host/vanilla/*.o", "*/host/patched/*.o", "*/host/tm/*.o",
              "*/host/sdk/*.o", "*/host/stubs_gen.o"] + [
        f"*/host/{name}.o" for name in GAME_STATE_HOST]
    body = "".join(f"    {pattern}{sections}\n" for pattern in inputs)
    script = OUT / "game_state.ld"
    text = ("/* Generated by tools/native_build.py. */\n"
            "SECTIONS\n{\n  .game_state : ALIGN(4096)\n  {\n"
            "    __game_state_start = .;\n" + body +
            "    . = ALIGN(4096);\n    __game_state_end = .;\n  }\n}\n"
            "INSERT AFTER .bss;\n")
    if not script.exists() or script.read_text() != text:
        script.write_text(text)
    return script


def link(objs, out, capture=False):
    libs = [OUT / "libmelee.a", OUT / "dat-readers/libdat_melee.a",
            OUT / "dat-readers/libdat_native.a"]
    if WIN32:
        # The arena sits at the console's addresses, above 2 GB: a 32-bit
        # Windows program reaches them only when large address aware.
        # The game's statics are not gathered into one section there (the
        # linker script is ELF's); see state.c.
        # --disable-dynamicbase: loaded at a fixed address, as -no-pie on
        # Linux (no ASLR), so addresses in a crash report or a snapshot
        # are the same every run.
        # -static: MinGW's runtime (libgcc, winpthread) linked in, so the
        # program runs without MSYS2's directory on PATH (else it stops at
        # once with 0xC0000135, a DLL not found).
        cmd = ["g++" if WINDOW else "gcc", "-m32", "-static", "-o", out,
               *objs, "-Wl,--large-address-aware",
               "-Wl,--disable-dynamicbase", "-Wl,--start-group", *libs]
    else:
        cmd = ["g++" if WINDOW else "gcc", "-m32", "-no-pie", "-rdynamic",
               "-o", out, *objs, f"-Wl,-T,{game_state_script()}",
               "-Wl,--start-group", *libs]
    if WINDOW:
        cmd += aurora_libs() + ["-pthread"]
    cmd += ["-Wl,--end-group", "-lm"]
    if WIN32:
        cmd.append("-lws2_32")  # Winsock (net.c)
    if "native-asan" in str(OUT):
        cmd.append("-fsanitize=address")
    return run(cmd, capture_output=True, text=True)


def write_stubs(names, path):
    kinds = symbol_kinds()
    lines = ['/* Generated by tools/native_build.py: SDK and debug functions',
             '   nothing implements natively. Each returns 0. */',
             'void host_stub_hit(int index);', '']
    funcs, objects = [], []
    for name in sorted(names):
        kind, size = kinds.get(name, ("function", 0))
        (objects if kind == "object" else funcs).append((name, size))
    for name, size in objects:
        lines.append(f"char {name}[{max(size, 4)}] "
                     "__attribute__((aligned(8)));")
    lines.append("")
    for i, (name, _) in enumerate(funcs):
        if name in FLOAT_STUBS:
            lines.append(f"float {name}(void) {{ host_stub_hit({i}); "
                         "return 0.0F; }")
        else:
            lines.append(f"int {name}(void) {{ host_stub_hit({i}); "
                         "return 0; }")
    lines.append("")
    lines.append("const char* const host_stub_names[] = {")
    lines += [f'    "{name}",' for name, _ in funcs]
    lines.append('    "",')
    lines.append("};")
    lines.append(f"unsigned host_stub_hits[{len(funcs) + 1}];")
    lines.append(f"const int host_stub_count = {len(funcs)};")
    text = "\n".join(lines) + "\n"
    if not path.exists() or path.read_text() != text:
        path.write_text(text)
    return funcs, objects


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    # -O2 with multiply-add fusing off (2026-11-15): the same game as -O0
    # bit for bit on all 80 of uninit.py's matches, 17 of 19 of survey.py's
    # against the console's code as -O0, every native test and drill check
    # the same; about twice as fast (the engine's search 25,000 frames a
    # second, 14,300 at -O0). Fusing on drifts from -O0 in the last bit on
    # moving stages and is no nearer the console. The live game and the
    # engine's copies (forks, shadows), and both sides of a netplay
    # session, must be built alike.
    ap.add_argument("--opt", default="2",
                    help="optimisation level (default 2)")
    ap.add_argument("--contract", default="off",
                    choices=["fast", "on", "off"],
                    help="fusing of multiply-add (default off; it only "
                         "happens when optimising)")
    ap.add_argument("--asan", action="store_true",
                    help="build build/native-asan/melee_headless with "
                         "AddressSanitizer: reads past the end of converted "
                         "archive data and of globals are reported "
                         "(tools/native_asan.sh runs it)")
    ap.add_argument("--auto-init", choices=["zero", "pattern"],
                    help="build build/native-init-X/melee_headless, in "
                         "which every local variable the code does not "
                         "assign starts as zero, or as bytes of 0xFE. The "
                         "decompiled code reads some it never assigns; if "
                         "the two builds play differently, one of those "
                         "matters (tests/native/uninit.py)")
    ap.add_argument("--out",
                    help="build into this directory instead (build/native,"
                         " or build/native-window with --window): an "
                         "optimised build to compare beside the shared one")
    ap.add_argument("--no-cmake", action="store_true",
                    help="reuse libmelee.a as it is")
    ap.add_argument("--window", action="store_true",
                    help="build build/native-window/melee_native: the game "
                         "with Aurora under its graphics calls (needs "
                         "tools/aurora32/build.sh first)")
    args = ap.parse_args()

    global OUT, OBJ, WINDOW
    flags = BASE_FLAGS + [f"-O{args.opt}", f"-ffp-contract={args.contract}"]
    if WIN32:
        # Aurora's headers declare OSReport, OSPanic and a few more weak.
        # On ELF the host's definition wins; the PE linker leaves a weak
        # definition's references unresolved, at address 0 (the game called
        # 0 at its first OSReport). Not weak, they link normally, and what is
        # really missing becomes a stub as on Linux.
        flags.append("-DDECL_WEAK=")
    if args.window:
        WINDOW = True
        OUT = ROOT / "build" / "native-window"
        OBJ = OUT / "host"
        DEFINES.append("-DHOST_WINDOW")
    if args.auto_init:
        OUT = ROOT / "build" / f"native-init-{args.auto_init}"
        OBJ = OUT / "host"
        flags.append(f"-ftrivial-auto-var-init={args.auto_init}")
    if args.asan:
        OUT = ROOT / "build" / "native-asan"
        OBJ = OUT / "host"
        flags += ["-fsanitize=address", "-fsanitize-recover=address"]
    if args.out:
        OUT = Path(args.out).resolve()
        OBJ = OUT / "host"
    if args.opt == "1":
        # The pass that fuses multiply-adds is otherwise an -O2 pass.
        flags.append("-fexpensive-optimizations")
    # What allocates for the game allocates from the game heap, which a
    # rollback snapshot covers (src/host/gameheap.c): the game's library and
    # the readers (through cmake), the game files built here, archive.c.
    heap = ["-include", str(ROOT / "src/host/gameheap.h")]
    if not args.no_cmake:
        cmake(flags + heap)

    common = flags + DEFINES + includes()
    jobs = []
    shim = ["-include", str(ROOT / "src/host/shim.h")] + heap
    for rel, extra in VANILLA.items():
        if rel in PATCHES or rel in FIFO_FILES:
            continue  # built once, from its patched copy, below
        jobs.append((ROOT / "src" / rel,
                     OBJ / "vanilla" / (rel.replace("/", "_") + ".o"),
                     common + shim + extra))
    for rel in sorted(set(PATCHES) | set(FIFO_FILES)):
        patches = PATCHES.get(rel, [])
        text = (ROOT / "src" / rel).read_text()
        if rel in FIFO_FILES:
            text, n = FIFO_WRITE.subn(r"GXParam1\1(\2);", text)
            if n == 0:
                sys.exit(f"{rel}: no direct pipe writes found")
        for old, new, *count in patches:
            want = count[0] if count else 1
            if text.count(old) != want:
                sys.exit(f"patch for {rel}: expected {want} of "
                         f"{old!r}, found {text.count(old)}")
            text = text.replace(old, new)
        copy = OBJ / "patched" / rel
        copy.parent.mkdir(parents=True, exist_ok=True)
        if not copy.exists() or copy.read_text() != text:
            copy.write_text(text)
        jobs.append((copy, OBJ / "patched" / (rel.replace("/", "_") + ".o"),
                     common + shim
                     + ["-iquote", str((ROOT / "src" / rel).parent)]
                     + VANILLA.get(rel, [])))
    # UCF in C, the same file the overlay links (src/host/ucf.c).
    jobs.append((ROOT / "src/melee/tm/ucf/ucf.c", OBJ / "tm" / "ucf.o",
                 common + shim))
    # The overlay's character rotation (src/host/match.c): a match loads a
    # drill's other opponents with it and the CPU becomes one at once.
    jobs.append((ROOT / "src/melee/tm/rotation/rotation.c",
                 OBJ / "tm" / "rotation.o", common + shim))
    host_sources = sorted((ROOT / "src/host").glob("*.c"))
    if WIN32:
        host_sources.append(ROOT / "src/host/win32/compat.c")
    for src in host_sources:
        extra = common + (heap if src.name == "archive.c" else [])
        if WIN32:
            extra = extra + WIN32_HOST
        if src.name == "window.c":
            # Aurora's and SDL's headers need the real `bool` (the game's
            # is an int), and the SDL that Aurora was built with.
            extra = [f for f in common if f != "-Dbool=int"] + [
                f"-I{AURORA32}/_deps/sdl-src/include"]
        jobs.append((src, OBJ / (src.stem + ".o"), extra))
    if WINDOW:
        # The client's interface: C++, against RmlUi and the patched Aurora
        # that tools/aurora32/build.sh builds.
        jobs.append((ROOT / "src/host/ui.cpp", OBJ / "ui.o", [
            "-m32", "-std=c++20", "-g", "-O1", "-fno-pie", "-w",
            "-DHOST_WINDOW", "-DAURORA_ENABLE_RMLUI", "-DRMLUI_STATIC_LIB",
            f"-I{AURORA32.parent}/aurora-src/include",
            f"-I{AURORA32}/_deps/rmlui-src/Include",
            f"-I{AURORA32}/_deps/sdl-src/include"]))
    for name in AURORA_C:
        jobs.append((AURORA / "lib/dolphin/mtx" / name,
                     OBJ / "aurora" / (name + ".o"),
                     flags + DEFINES + [f"-I{AURORA}/include"]))
    # The SDK's own heap allocator, as decompiled: the same blocks at the
    # same addresses as on the console.
    jobs.append((ROOT / "libs/dolphin/src/dolphin/os/OSAlloc.c",
                 OBJ / "sdk" / "OSAlloc.o",
                 flags + ["-include", "stdint.h", "-include", "stddef.h",
                          f"-I{ROOT}/libs/dolphin/include", f"-I{ROOT}/src",
                          f"-I{ROOT}/libs/doldecomp/include"]))
    # The types marked PPC_LAYOUT, by name, for src/host/archive.c.
    marked = set()
    for sub in ("melee", "sysdolphin"):
        for header in (ROOT / "src" / sub).rglob("*.h"):
            marked.update(re.findall(
                r"\b(?:union|struct)\s+PPC_LAYOUT\s+(\w+)",
                header.read_text()))
    names_c = OBJ / "ppc_layout_gen.c"
    text = ("/* Generated by tools/native_build.py. */\n"
            "const char* const host_ppc_layout_names[] = {\n"
            + "".join(f'    "{n}",\n' for n in sorted(marked))
            + "    0,\n};\n")
    names_c.parent.mkdir(parents=True, exist_ok=True)
    if not names_c.exists() or names_c.read_text() != text:
        names_c.write_text(text)
    jobs.append((names_c, OBJ / "ppc_layout_gen.o", flags))
    compile_all(jobs)
    objs = [obj for _, obj, _ in jobs]

    # What is still missing becomes a stub.
    stub_c = OBJ / "stubs_gen.c"
    stub_o = OBJ / "stubs_gen.o"
    write_stubs([], stub_c)
    compile_all([(stub_c, stub_o, flags)])
    r = link(objs + [stub_o], OUT / "melee_headless.trial")
    missing = sorted(set(re.findall(r"undefined reference to `([^']+)'",
                                    r.stderr)))
    other = [l for l in r.stderr.splitlines()
             if "undefined reference" not in l and "error" in l.lower()
             and "ld returned" not in l]
    if other:
        sys.exit("\n".join(other[:30]))
    funcs, objects = write_stubs(missing, stub_c)
    compile_all([(stub_c, stub_o, flags)])
    exe = OUT / ("melee_native" if WINDOW else "melee_headless")
    r = link(objs + [stub_o], exe)
    if r.returncode:
        sys.exit("\n".join(r.stderr.splitlines()[-30:]))
    (OUT / "melee_headless.trial").unlink(missing_ok=True)
    (OBJ / "stubs.json").write_text(json.dumps(
        {"functions": [n for n, _ in funcs],
         "objects": [n for n, _ in objects]}, indent=1))
    print(f"OK: {exe.relative_to(ROOT)} "
          f"({len(funcs)} stubbed functions, {len(objects)} stubbed objects)")


if __name__ == "__main__":
    main()
