#!/usr/bin/env python3
"""Query the Melee character data in data/framedata/*.json.

    query.py list                         characters and key attributes
    query.py fox                          one character: attributes, move keys
    query.py fox usmash [--json]          one move, every hitbox
    query.py oos fox                      out-of-shield options, fastest first
    query.py jump fox                     jump squat, short/full hop timing estimate
    query.py kb fox usmash marth 80       knockback/hitstun at 80% (pre-hit)
        [--cc] [--hit N]                  crouch cancel; pick the Nth hit row
    query.py thresholds fox dthrow marth  percents where tumble / CC-break start
    query.py shield marth fsmash fox      advantage on shield and which of the
                                          defender's OOS options punish it

Character ids are the file names in data/characters/ (fox, captain-falcon,
mr-game-and-watch...). Move keys are the `Key` column of the frame data
tables (usmash, nair, special_lw_start...).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402
from roster import ROSTER, BY_ID  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
DATA = os.environ.get("MELEE_DATA_DIR") or os.path.join(REPO, "data")


def load(cid):
    if cid not in BY_ID:
        close = [e["id"] for e in ROSTER if cid.replace("_", "-") in e["id"]]
        sys.exit("unknown character %r%s" % (
            cid, "; did you mean %s?" % ", ".join(close) if close else
            "; run `query.py list`"))
    with open(os.path.join(DATA, "framedata", cid + ".json")) as f:
        return json.load(f)


def get_move(char, key):
    m = char["moves"].get(key)
    if m is None:
        close = [k for k in char["moves"] if key in k]
        sys.exit("%s has no move %r%s" % (
            char["id"], key,
            "; similar: %s" % ", ".join(close) if close else ""))
    return m


def effects(move):
    """Distinct (window, hitbox effect) rows of a move, strongest first
    within each window."""
    rows = []
    if "throw" in move:
        t = move["throw"]
        rows.append({"start": t.get("release_frame"),
                     "end": t.get("release_frame"), "damage": t["damage"],
                     "angle": t["angle"], "bkb": t["bkb"], "kbg": t["kbg"],
                     "wdsk": t["wdsk"], "element": t["element"],
                     "throw": True})
    for h in move.get("hits", []):
        seen = []
        for b in sorted(h["hitboxes"], key=lambda b: -b["damage"]):
            e = (b["damage"], b["angle"], b["bkb"], b["kbg"], b["wdsk"],
                 b["element"])
            if e not in seen:
                seen.append(e)
                rows.append({"start": h["start"], "end": h["end"],
                             "damage": b["damage"], "angle": b["angle"],
                             "bkb": b["bkb"], "kbg": b["kbg"],
                             "wdsk": b["wdsk"], "element": b["element"]})
    return rows


def cmd_list():
    print("%-18s %6s %7s %6s %5s %5s" % (
        "id", "weight", "gravity", "fall", "ff", "jsq"))
    for e in ROSTER:
        a = load(e["id"])["attributes"]
        print("%-18s %6s %7s %6s %5s %5s" % (
            e["id"], a["weight"], a["gravity"], a["terminal_velocity"],
            a["fast_fall_velocity"], a["jump_startup_time"]))


def cmd_char(cid):
    c = load(cid)
    print("%s (%s)" % (c["name"], c["dat"]))
    for k, v in c["attributes"].items():
        print("  %-40s %s" % (k, v))
    print("moves: " + " ".join(c["moves"]))


def cmd_move(cid, key, as_json):
    c = load(cid)
    m = get_move(c, key)
    if as_json:
        print(json.dumps(m, indent=1))
        return
    print("%s %s (%s)" % (c["name"], key, m["subaction"]))
    print("  total %d, first actionable frame %d%s" % (
        m["total_frames"], calc.faf(m),
        " (IASA)" if m.get("iasa") else ""))
    for k in ("entry_delay", "charge_frame", "intangible", "invincible",
              "partial", "projectile_frames", "self_damage", "autocancel",
              "landing_lag", "landing_lag_lcancel"):
        if k in m:
            print("  %s: %s" % (k, json.dumps(m[k])))
    for i, r in enumerate(effects(m)):
        print("  %s %d: frames %s-%s dmg %d angle %d bkb %d kbg %d wdsk %d "
              "%s shieldstun %d" % (
                  "throw" if r.get("throw") else "hit", i, r["start"], r["end"], r["damage"], r["angle"], r["bkb"],
                  r["kbg"], r["wdsk"], r["element"],
                  calc.shield_stun(r["damage"])))


def cmd_oos(cid):
    c = load(cid)
    for o in calc.oos_options(c):
        print("  frame %2d  %-16s via %-11s (%s)" % (
            o["frame"], o["option"], o["via"], o["move"]))


def cmd_jump(cid):
    c = load(cid)
    a = c["attributes"]
    print("%s: jump squat %d frames (airborne on frame %d after the jump "
          "input)" % (c["name"], a["jump_startup_time"],
                      a["jump_startup_time"] + 1))
    for full in (False, True):
        for ff in (False, True):
            j = calc.jump_arc(a, full, ff)
            print("  %-9s %-14s apex frame %2d (height %5.2f), lands frame "
                  "%2d, %2d airborne frames" % (
                      "full hop" if full else "short hop",
                      "+ fast fall" if ff else "", j["apex_frame"],
                      j["peak_height"], j["landing_frame"],
                      j["airborne_frames"]))
    print("  estimate from attributes (+/-2 frames, flat ground, no aerial "
          "drift effects): tune in game")
    print("  aerial landing lag: " + ", ".join(
        "%s %s/%s" % (k, c["moves"][k]["landing_lag"],
                      c["moves"][k]["landing_lag_lcancel"])
        for k in ("nair", "fair", "bair", "uair", "dair")
        if k in c["moves"]) + " (normal/L-cancelled)")


def pick_hit(rows, idx):
    if not rows:
        sys.exit("move has no hitbox or throw data")
    if idx >= len(rows):
        sys.exit("move has %d hit rows (0..%d)" % (len(rows), len(rows) - 1))
    return rows[idx]


def target_weight(defender, row):
    """Throws ignore the victim's weight for knockback (the formula uses
    100); weight only changes how fast the throw animation plays."""
    return 100 if row.get("throw") else defender["attributes"]["weight"]


def cmd_kb(att, key, dfn, percent, cc, idx):
    a, d = load(att), load(dfn)
    r = pick_hit(effects(get_move(a, key)), idx)
    w = target_weight(d, r)
    kb = calc.knockback(percent + r["damage"], r["damage"], w, r["kbg"],
                        r["bkb"], r["wdsk"], cc)
    print("%s %s (%s %d: %d%%, angle %d) on %s (weight %s) at %d%%%s" % (
        a["name"], key, "throw" if r.get("throw") else "hit", idx,
        r["damage"], r["angle"], d["name"],
        "100, throws ignore weight" if r.get("throw") else w, percent,
        " crouch cancelled" if cc else ""))
    print("  knockback %.1f, hitstun %d frames, hitlag %d frames, %s" % (
        kb, calc.hitstun(kb),
        calc.hitlag(r["damage"], r["element"] == "electric", cc),
        "tumble (knockdown if they land)" if kb >= calc.TUMBLE_KB
        else "no tumble (stays standing if grounded)"))
    print("  launch speed %.2f units/frame, decaying %.3f per frame" % (
        kb * calc.LAUNCH_SPEED_MULT, calc.LAUNCH_DECAY))


def cmd_thresholds(att, key, dfn, idx):
    a, d = load(att), load(dfn)
    r = pick_hit(effects(get_move(a, key)), idx)
    w = target_weight(d, r)
    args = (r["damage"], w, r["kbg"], r["bkb"], r["wdsk"])
    print("%s %s (hit %d) on %s, pre-hit percents:" % (
        a["name"], key, idx, d["name"]))
    if r["wdsk"]:
        kb = calc.knockback(0, *args)
        print("  set knockback %.1f at every percent (%s)" % (
            kb, "tumble" if kb >= calc.TUMBLE_KB else "no tumble"))
        return
    t = calc.percent_for_kb(calc.TUMBLE_KB, *args)
    c = calc.percent_for_kb(calc.TUMBLE_KB, *args, crouch_cancel=True)
    print("  tumble / knockdown from: %s" % ("never" if t is None
                                             else "%d%%" % t))
    print("  crouch cancel stops preventing tumble from: %s" % (
        "never" if c is None else "%d%%" % c))


def cmd_shield(att, key, dfn):
    a, d = load(att), load(dfn)
    m = get_move(a, key)
    if "landing_lag" in m:
        adv = calc.shield_advantage_aerial(m)
        how = "L-cancelled, landing the frame after the hit (best case)"
    else:
        adv = calc.shield_advantage_ground(m)
        how = "first active frame"
    if adv is None:
        sys.exit("no hitbox data for that move")
    print("%s %s on %s's shield: %+d (%s)" % (
        a["name"], key, d["name"], adv, how))
    print("  %s's out-of-shield options (hit frame, guaranteed if <= %d):"
          % (d["name"], -adv))
    for o in calc.oos_options(d):
        ok = o["frame"] <= -adv
        print("    frame %2d  %-16s %s" % (
            o["frame"], o["option"], "PUNISHES" if ok else "too slow"))
    print("  (ignores range, shield pushback and shield DI: check spacing)")


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    idx = 0
    if "--hit" in argv:
        i = argv.index("--hit")
        idx = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    args = [a for a in argv if not a.startswith("--")]
    if not args or "--help" in flags:
        print(__doc__)
    elif args[0] == "list":
        cmd_list()
    elif args[0] == "oos" and len(args) == 2:
        cmd_oos(args[1])
    elif args[0] == "jump" and len(args) == 2:
        cmd_jump(args[1])
    elif args[0] == "kb" and len(args) == 5:
        cmd_kb(args[1], args[2], args[3], int(args[4]), "--cc" in flags, idx)
    elif args[0] == "thresholds" and len(args) == 4:
        cmd_thresholds(args[1], args[2], args[3], idx)
    elif args[0] == "shield" and len(args) == 4:
        cmd_shield(args[1], args[2], args[3])
    elif len(args) == 1:
        cmd_char(args[0])
    elif len(args) == 2:
        cmd_move(args[0], args[1], "--json" in flags)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
