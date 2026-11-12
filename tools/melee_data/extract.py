#!/usr/bin/env python3
"""Extract frame data for every playable fighter from the game's own files.

Reads Pl??.dat / Pl??AJ.dat from an extracted disc (default
build/disc/files, falling back to orig/GALE01/files) and writes one JSON file
per character to data/framedata/<slug>.json. Everything here is read from
the retail data; nothing is typed in by hand except names.

    python tools/melee_data/extract.py [--files DIR] [--out DIR]

Frame convention: 1-indexed. "start 7" means the 7th frame of the move.
Script timing follows ftAction_80073240 / lbcommand.c: an AsynchronousTimer
N runs the following commands on frame N, a SynchronousTimer N waits N
frames from the current frame.
"""

import argparse
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsd_dat import FighterDat  # noqa: E402
from roster import ROSTER, MOVE_NAMES, move_key  # noqa: E402

MOVE_KEYS = {v[0] for v in MOVE_NAMES.values()}

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

# Command lengths in bytes (default 4). Opcode is the top 6 bits of the
# first byte; keys here are that byte with the low 2 bits cleared.
LENGTHS = {
    0x14: 8, 0x1C: 8, 0x28: 0x14, 0x2C: 0x14, 0x44: 0x0C, 0x88: 0x0C,
    0x98: 0x1C, 0x9C: 0x10, 0xD8: 0x0C, 0xDC: 0x0C, 0xE0: 8, 0xE8: 0x10,
}

ELEMENTS = {
    0: "normal", 1: "fire", 2: "electric", 3: "slash", 4: "coin", 5: "ice",
    6: "sleep", 7: "sleep_long", 8: "grab", 9: "bury", 10: "cape",
    11: "inert", 12: "disable", 13: "darkness", 14: "screw_attack",
    15: "flower", 16: "none",
}
BODY_STATES = {0: "normal", 1: "invincible", 2: "intangible"}

# ftCo_DatAttrs fields worth publishing (offset, type, name). Names follow
# src/melee/ft/types.h.
ATTRS = [
    (0x000, "f", "walk_accel_mul"), (0x004, "f", "walk_accel_base"),
    (0x008, "f", "walk_max_vel"), (0x018, "f", "ground_friction"),
    (0x01C, "f", "dash_initial_velocity"), (0x020, "f", "dash_accel_mul"),
    (0x024, "f", "dash_accel_base"), (0x028, "f", "dash_max_velocity"),
    (0x030, "f", "max_run_brake_frames"),
    (0x038, "f", "jump_startup_time"),
    (0x03C, "f", "jump_h_initial_velocity"),
    (0x040, "f", "jump_v_initial_velocity"),
    (0x044, "f", "ground_to_air_jump_momentum_multiplier"),
    (0x048, "f", "jump_h_max_velocity"),
    (0x04C, "f", "hop_v_initial_velocity"),
    (0x050, "f", "air_jump_v_multiplier"),
    (0x054, "f", "air_jump_h_multiplier"), (0x058, "i", "max_jumps"),
    (0x05C, "f", "gravity"), (0x060, "f", "terminal_velocity"),
    (0x064, "f", "air_drift_stick_mul"), (0x068, "f", "aerial_drift_base"),
    (0x06C, "f", "air_drift_max"), (0x070, "f", "aerial_friction"),
    (0x074, "f", "fast_fall_velocity"),
    (0x07C, "f", "jab_2_input_window"), (0x080, "f", "jab_3_input_window"),
    (0x084, "f", "standing_turn_frames"), (0x088, "f", "weight"),
    (0x08C, "f", "model_scaling"), (0x090, "f", "initial_shield_size"),
    (0x0A8, "f", "ledge_jump_horizontal_velocity"),
    (0x0AC, "f", "ledge_jump_vertical_velocity"),
    (0x0E4, "f", "normal_landing_lag"), (0x0E8, "f", "landingairn_lag"),
    (0x0EC, "f", "landingairf_lag"), (0x0F0, "f", "landingairb_lag"),
    (0x0F4, "f", "landingairhi_lag"), (0x0F8, "f", "landingairlw_lag"),
    (0x104, "f", "wall_jump_horizontal_velocity"),
    (0x108, "f", "wall_jump_vertical_velocity"),
]


def num(x):
    """Round float32 noise away; ints stay ints."""
    if isinstance(x, int):
        return x
    r = round(x, 5)
    return int(r) if r == int(r) else r


def bits(word, hi, n):
    """n bits of a 32-bit word, hi = number of bits above the field."""
    return (word >> (32 - hi - n)) & ((1 << n) - 1)


def parse_hitbox(b):
    w0, = struct.unpack_from(">I", b, 0)
    size, z, y, x = struct.unpack_from(">Hhhh", b, 4)
    w3, w4 = struct.unpack_from(">II", b, 12)
    return {
        "id": bits(w0, 6, 3),
        "bone": bits(w0, 14, 7),
        "damage": bits(w0, 23, 9),
        "size": num(size / 256),
        "offset": [num(x / 256), num(y / 256), num(z / 256)],
        "angle": bits(w3, 0, 9),
        "kbg": bits(w3, 9, 9),
        "wdsk": bits(w3, 18, 9),
        "interaction": bits(w3, 30, 2),
        "bkb": bits(w4, 0, 9),
        "element": ELEMENTS.get(bits(w4, 9, 5), bits(w4, 9, 5)),
        "shield_damage": bits(w4, 15, 7),
        "hits_grounded": bool(bits(w4, 30, 1)),
        "hits_airborne": bool(bits(w4, 31, 1)),
    }


def parse_throw(b):
    w0, w1, w2 = struct.unpack_from(">III", b, 0)
    return {
        "type": bits(w0, 6, 3),
        "damage": bits(w0, 23, 9),
        "angle": bits(w1, 0, 9),
        "kbg": bits(w1, 9, 9),
        "wdsk": bits(w1, 18, 9),
        "bkb": bits(w2, 0, 9),
        "element": ELEMENTS.get(bits(w2, 9, 4), bits(w2, 9, 4)),
    }


EFFECT_KEYS = ("damage", "angle", "kbg", "bkb", "wdsk", "element",
               "shield_damage", "hits_grounded", "hits_airborne")


def run_script(data, pc, total_frames, air_normal):
    """Interpret one subaction script frame by frame.

    Returns a list (index 0 = frame 1) of per-frame dicts.
    """
    frames = []
    active = {}        # hitbox id -> (serial, hitbox dict)
    serial = 0
    body = "normal"
    bones = {}         # bone -> state
    lag_flag = False   # landing-lag flag for aerials (False = autocancel)
    iasa = False
    stack = []         # return addresses and loop frames
    wait_until = 0
    done = pc == 0
    limit = total_frames if total_frames else 400
    for frame in range(1, limit + 1):
        info = {"throw": None, "release": False, "charge": False,
                "shoot": False, "self_damage": 0}
        guard = 0
        while not done and frame >= wait_until:
            guard += 1
            if guard > 2000:       # a goto loop without a timer
                done = True
                break
            op = data[pc] & 0xFC
            n = LENGTHS.get(op, 4)
            b = data[pc:pc + n]
            word, = struct.unpack_from(">I", b, 0)
            arg = word & 0x03FFFFFF
            pc += n
            if op == 0x00:
                done = True
            elif op == 0x04:
                wait_until = frame + arg
            elif op == 0x08:
                wait_until = arg
            elif op == 0x0C:
                stack.append(["loop", pc, arg])
            elif op == 0x10:
                if stack and stack[-1][0] == "loop":
                    stack[-1][2] -= 1
                    if stack[-1][2] > 0:
                        pc = stack[-1][1]
                    else:
                        stack.pop()
            elif op == 0x14:   # Subroutine (lbcommand.c Command_05)
                stack.append(["call", pc])
                pc, = struct.unpack_from(">I", b, 4)
            elif op == 0x18:
                while stack and stack[-1][0] == "loop":
                    stack.pop()
                if stack:
                    pc = stack.pop()[1]
            elif op == 0x1C:   # Goto (Command_07)
                pc, = struct.unpack_from(">I", b, 4)
            elif op == 0x20:
                done = True        # timer follows the animation loop
            elif op == 0x2C:
                hb = parse_hitbox(b)
                serial += 1
                active[hb["id"]] = (serial, hb)
            elif op == 0x30:
                hid, dmg = bits(word, 6, 3), bits(word, 9, 23)
                if hid in active:
                    serial += 1
                    active[hid] = (serial, dict(active[hid][1], damage=dmg))
            elif op == 0x34:
                hid, size = bits(word, 6, 3), bits(word, 9, 23)
                if hid in active:
                    active[hid] = (active[hid][0],
                                   dict(active[hid][1], size=num(size / 256)))
            elif op == 0x3C:
                active.pop(arg, None)
            elif op == 0x40:
                active = {}
            elif op == 0x4C:
                lag_flag = bool(arg & 1)
            elif op == 0x50:   # in throws: the victim is released
                info["release"] = True
            elif op == 0x5C:
                iasa = True
            elif op == 0x60:
                info["shoot"] = True
            elif op == 0x68:
                body = BODY_STATES.get(arg & 3, "normal")
            elif op == 0x6C:
                body = "normal"
                bones = {}
            elif op == 0x70:
                bone, state = bits(word, 6, 8), bits(word, 14, 18)
                if state:
                    bones[bone] = BODY_STATES.get(state, "normal")
                else:
                    bones.pop(bone, None)
            elif op == 0x88:
                t = parse_throw(b)
                if t["type"] == 0 and info["throw"] is None:
                    info["throw"] = t
            elif op == 0xCC:
                info["self_damage"] += bits(word, 16, 16)
            elif op == 0xE0:
                info["charge"] = True
        info["hitboxes"] = dict(active)
        info["body"] = body
        info["bones"] = dict(bones)
        info["lag_flag"] = lag_flag if air_normal else None
        info["iasa"] = iasa
        frames.append(info)
        if not total_frames and done:
            break
    return frames


# States whose entry code does not step the script on the frame they are
# entered (no ftAnim_8006EBA4 after Fighter_ChangeMotionState: see
# ftCo_Catch.c, ftCo_Attack1.c, ftCo_Passive*.c, ftCo_DownStand.c ...).
# In game everything in them happens one frame later than the script says
# and the state lasts one frame longer. Confirmed against frame-by-frame
# captures (grab = 30 frames, hitbox on frame 7 for most characters).
ENTRY_DELAY = {
    "jab2", "jab3", "grab", "dash_grab", "pummel", "taunt",
    "tech_in_place", "tech_roll_forward", "tech_roll_backward",
    "wall_tech", "wall_tech_jump", "ceiling_tech",
    "getup_stand_faceup", "getup_stand_facedown",
    "shield_off", "rebound", "landing",
}


# Mr. Game & Watch's neutral, back and up air are his own states
# (ftGw_MS_AttackAirN..., ftgamewatchattackair.c) and land through
# ftCo_LandingAir_EnterWithMsidLag with the full lag: no L-cancel.
NO_LCANCEL = {("mr-game-and-watch", k) for k in ("nair", "bair", "uair")}


def ranges(flags):
    """[(start, end)] 1-indexed inclusive runs where flags[i] is truthy."""
    out, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i + 1
        if not f and start is not None:
            out.append([start, i])
            start = None
    if start is not None:
        out.append([start, len(flags)])
    return out


def summarize(frames, total):
    s = {"total_frames": total}
    iasa = next((i + 1 for i, f in enumerate(frames) if f["iasa"]), None)
    if iasa is not None and (not total or iasa <= total):
        s["iasa"] = iasa
    charge = next((i + 1 for i, f in enumerate(frames) if f["charge"]), None)
    if charge:
        s["charge_frame"] = charge
    shoot = [i + 1 for i, f in enumerate(frames) if f["shoot"]]
    if shoot:
        s["projectile_frames"] = shoot
    dmg = [[i + 1, f["self_damage"]] for i, f in enumerate(frames)
           if f["self_damage"]]
    if dmg:
        s["self_damage"] = dmg
    # hit windows: runs of an unchanged set of hitbox instances
    hits, prev, start = [], None, None
    for i, f in enumerate(frames + [{"hitboxes": {}}]):
        cur = tuple(sorted((v[0] for v in f["hitboxes"].values())))
        if cur != prev:
            if prev:
                boxes = [v[1] for _, v in
                         sorted(frames[i - 1]["hitboxes"].items())]
                hits.append({"start": start, "end": i, "hitboxes": boxes})
            start = i + 1
            prev = cur
    if hits:
        s["hits"] = hits
        s["first_hit_frame"] = hits[0]["start"]
    for state in ("intangible", "invincible"):
        r = ranges([f["body"] == state for f in frames])
        if r:
            s[state] = r
    part = {}
    for bone in sorted({b for f in frames for b in f["bones"]}):
        for state in ("intangible", "invincible"):
            r = ranges([f["bones"].get(bone) == state for f in frames])
            if r:
                part.setdefault(state, []).append(
                    {"bone": bone, "frames": r})
    if part:
        s["partial"] = part
    throw = next((f["throw"] for f in frames if f["throw"]), None)
    if throw:
        t = dict(throw)
        t.pop("type")
        t["release_frame"] = next(
            (i + 1 for i, f in enumerate(frames) if f["release"]), None)
        s["throw"] = t
    return s


def extract_fighter(entry, files):
    dat_path = os.path.join(files, "Pl%s.dat" % entry["dat"])
    aj_path = os.path.join(files, "Pl%sAJ.dat" % entry["dat"])
    with open(dat_path, "rb") as f:
        raw = f.read()
    with open(aj_path, "rb") as f:
        aj = f.read()
    fd = FighterDat(raw, aj)
    d = fd.dat.data
    attrs = {}
    for off, kind, name in ATTRS:
        fmt = ">f" if kind == "f" else ">i"
        attrs[name] = num(struct.unpack_from(fmt, d, fd.attrs_off + off)[0])
    lag = {"nair": "landingairn_lag", "fair": "landingairf_lag",
           "bair": "landingairb_lag", "uair": "landingairhi_lag",
           "dair": "landingairlw_lag"}
    moves, seen = {}, {}
    for s in fd.subactions:
        if not s.name or s.frames is None:
            continue
        key = move_key(s.short)
        if key is None:
            continue
        if key in seen:
            # the table repeats entries (item variants, mirrored copies);
            # keep the first unless the script differs
            if seen[key] == (s.script, s.frames) or not (
                    key.startswith("special") or key.startswith("fsmash")):
                continue
            key = "%s_%d" % (key, s.index)
        seen[key] = (s.script, s.frames)
        total = int(s.frames) - 1
        air = key in lag
        frames = run_script(d, s.script, total, air)
        base = key.rsplit("_", 1)[0] if key not in MOVE_KEYS else key
        delay = base in ENTRY_DELAY
        if delay:
            idle = {"throw": None, "release": False, "charge": False,
                    "shoot": False, "self_damage": 0, "hitboxes": {},
                    "body": "normal", "bones": {}, "lag_flag": None,
                    "iasa": False}
            frames = [idle] + frames
            total += 1
        m = {"subaction": s.short, "index": s.index}
        if delay:
            m["entry_delay"] = 1
        m.update(summarize(frames, total))
        if air:
            flags = [f["lag_flag"] for f in frames]
            # autocancel = landing on a frame where the lag flag is clear
            first_lag = next((i + 1 for i, v in enumerate(flags) if v), None)
            if first_lag is None:
                m["autocancel"] = {"always": True}
            else:
                last_lag = max(i + 1 for i, v in enumerate(flags) if v)
                m["autocancel"] = {"before": first_lag, "after": last_lag}
            ll = int(attrs[lag[key]])
            m["landing_lag"] = ll
            m["landing_lag_lcancel"] = math.floor(ll / 2)
            if (entry["id"], key) in NO_LCANCEL:
                m["landing_lag_lcancel"] = ll
                m["no_lcancel"] = True
        moves[key] = m
    return {
        "schema": "melee-framedata/v1",
        "id": entry["id"],
        "name": entry["name"],
        "dat": "Pl%s.dat" % entry["dat"],
        "ft_data": fd.root_name,
        "attributes": attrs,
        "moves": moves,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--files", help="extracted disc files/ directory")
    ap.add_argument("--out", default=os.path.join(REPO, "data", "framedata"))
    args = ap.parse_args()
    files = args.files
    if files is None:
        for cand in ("build/disc/files", "orig/GALE01/files"):
            p = os.path.join(REPO, cand)
            if os.path.exists(os.path.join(p, "PlFx.dat")):
                files = p
                break
    if files is None:
        sys.exit("no extracted disc found; pass --files")
    os.makedirs(args.out, exist_ok=True)
    for entry in ROSTER:
        out = extract_fighter(entry, files)
        path = os.path.join(args.out, entry["id"] + ".json")
        with open(path, "w") as f:
            json.dump(out, f, indent=1)
            f.write("\n")
        print("%-18s %3d moves -> %s" % (
            entry["id"], len(out["moves"]), os.path.relpath(path, REPO)))


if __name__ == "__main__":
    main()
