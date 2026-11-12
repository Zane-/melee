"""Melee combat formulas (NTSC 1.02) used by the docs and the query tool.

Sources: knockback/hitstun/hitlag are the standard community formulas
(SSBWiki "Knockback", "Hitstun", "Hitlag"); shield stun follows
ftCo_80092ED8 / ftCo_80092F2C in src/melee/ft/kinds/ftCommon/ftCo_Guard.c
with the constants in PlCo.dat (1.5, 2.0, light-shield range 0.3..0.95 and
the 20-frame GuardSetOff animation played at rate 20.1 / stun).
"""

import math

TUMBLE_KB = 80.0          # knockback at which a hit causes tumble/knockdown
CC_MULT = 2.0 / 3.0       # crouch cancel knockback multiplier
HITSTUN_MULT = 0.4
LAUNCH_SPEED_MULT = 0.03
LAUNCH_DECAY = 0.051


def knockback(percent_after, damage, weight, kbg, bkb, wdsk=0,
              crouch_cancel=False):
    """Knockback units. percent_after = target percent after the hit."""
    if wdsk:
        p, d = 10.0, float(wdsk)
    else:
        p, d = float(percent_after), float(damage)
    kb = ((p / 10 + p * d / 20) * (200.0 / (weight + 100)) * 1.4 + 18)
    kb = kb * (kbg / 100.0) + bkb
    if crouch_cancel:
        kb *= CC_MULT
    return min(kb, 2500.0)


def hitstun(kb):
    return int(math.floor(kb * HITSTUN_MULT))


def hitlag(damage, electric=False, crouch_cancel=False):
    h = math.floor(damage / 3.0 + 3)
    if electric:
        h = math.floor(h * 1.5)
    if crouch_cancel:
        h = math.floor(h * CC_MULT)
    return int(min(h, 20))


def shield_stun(damage, light=0.0):
    """Frames of shield stun. light: 0 = full hard shield, 1 = lightest."""
    f = 1.5 * (damage * (0.3 + 0.65 * light)) + 2.0
    return int(math.floor(f * 200.0 / 201.0))


def percent_for_kb(target_kb, damage, weight, kbg, bkb, wdsk=0,
                   crouch_cancel=False):
    """Lowest pre-hit percent at which the hit reaches target_kb.

    Returns None when the knockback does not depend on percent (set
    knockback) or never reaches it below 999%.
    """
    if wdsk:
        return None
    for pre in range(0, 1000):
        if knockback(pre + damage, damage, weight, kbg, bkb,
                     crouch_cancel=crouch_cancel) >= target_kb:
            return pre
    return None


def faf(move):
    """First actionable frame: IASA if the move has one, else total + 1."""
    return move.get("iasa") or move["total_frames"] + 1


def shield_advantage_ground(move, hit=None):
    """Frame advantage on a hard shield for a grounded move, taking the
    first active frame of the given hit window (default: the first)."""
    hits = move.get("hits")
    if not hits:
        return None
    h = hit or hits[0]
    dmg = max(b["damage"] for b in h["hitboxes"])
    if dmg == 0:
        return None
    return shield_stun(dmg) - (faf(move) - 1 - h["start"])


def shield_advantage_aerial(move, hit=None, lcancel=True):
    """Best case: the aerial connects on the frame before landing."""
    hits = move.get("hits")
    if not hits or "landing_lag" not in move:
        return None
    h = hit or hits[0]
    dmg = max(b["damage"] for b in h["hitboxes"])
    lag = move["landing_lag_lcancel"] if lcancel else move["landing_lag"]
    return shield_stun(dmg) - lag


def oos_options(char):
    """Out-of-shield options with the frame their hitbox first comes out,
    counted from the first frame the player acts out of shield."""
    moves = char["moves"]
    js = int(char["attributes"]["jump_startup_time"])
    out = []

    def add(name, via, frame, key):
        out.append({"option": name, "via": via, "frame": frame, "move": key})

    for key, name in (("nair", "Neutral air"), ("fair", "Forward air"),
                      ("bair", "Back air"), ("uair", "Up air"),
                      ("dair", "Down air")):
        m = moves.get(key)
        if m and m.get("first_hit_frame"):
            add(name, "jump", js + m["first_hit_frame"], key)
    m = moves.get("usmash")
    if m and m.get("first_hit_frame"):
        add("Up smash", "jump cancel", 1 + m["first_hit_frame"], "usmash")
    # the first grounded up-B state in table order is the one entered
    for key, m in moves.items():
        if m["subaction"].startswith("SpecialHi"):
            if m.get("first_hit_frame"):
                add("Up B", "jump cancel", 1 + m["first_hit_frame"], key)
            break
    for key in ("special_air_lw_start", "special_air_lw"):
        m = moves.get(key)
        if m and m.get("first_hit_frame") and m["first_hit_frame"] <= 6:
            add("Down B (aerial)", "jump", js + m["first_hit_frame"], key)
            break
    m = moves.get("grab")
    if m and m.get("first_hit_frame"):
        add("Shield grab", "direct", m["first_hit_frame"], "grab")
    out.sort(key=lambda o: o["frame"])
    return out


def jump_arc(attrs, full_hop=False, fast_fall=False):
    """Estimate a grounded jump from the attributes: frame-by-frame
    integration of initial speed, gravity and terminal velocity on flat
    ground with no aerial. Frames count from the jump input (frame 1 = first
    jump squat frame). An estimate (+/-2 frames): verify in game.
    """
    js = int(attrs["jump_startup_time"])
    v = attrs["jump_v_initial_velocity"] if full_hop \
        else attrs["hop_v_initial_velocity"]
    g, term = attrs["gravity"], attrs["terminal_velocity"]
    ff = attrs["fast_fall_velocity"]
    y, peak, apex, n = 0.0, 0.0, 0, 0
    fell = False
    while n < 600:
        n += 1
        if n > 1:
            v = max(v - g, -(ff if fell else term))
            if fast_fall and v < 0 and not fell:
                v, fell = -ff, True
        y += v
        if y > peak:
            peak, apex = y, n
        if y <= 0:
            break
    return {"jump_squat": js, "first_airborne_frame": js + 1,
            "apex_frame": js + apex, "peak_height": round(peak, 2),
            "airborne_frames": n - 1, "landing_frame": js + n}
