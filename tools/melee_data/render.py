#!/usr/bin/env python3
"""Fill the generated parts of data/characters/<id>.md.

Reads data/framedata/<id>.json (from extract.py) and
data/resources/meleelibrary.json (from library.py) and rewrites, in each
character file:

  * the generated keys at the end of the YAML front matter
  * <!-- GENERATED:attributes --> ... <!-- /GENERATED:attributes -->
  * <!-- GENERATED:framedata -->  ... <!-- /GENERATED:framedata -->
  * <!-- GENERATED:resources -->  ... <!-- /GENERATED:resources -->

Hand-written text outside those markers is never touched. A character file
that does not exist yet is created from a stub.

    python tools/melee_data/render.py [id ...]
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402
from roster import ROSTER, MOVE_NAMES, SPECIAL_DIRS  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
DATA = os.environ.get("MELEE_DATA_DIR") or os.path.join(REPO, "data")

KEY_INFO = {v[0]: (v[1], v[2]) for v in MOVE_NAMES.values()}
GROUPS = [
    ("ground", "Ground attacks"),
    ("air", "Aerials"),
    ("grab", "Grabs and throws"),
    ("special", "Special moves"),
    ("defense", "Dodges and rolls"),
    ("tech", "Techs and getups"),
    ("ledge", "Ledge options"),
]
LIBRARY_TITLES = {"dr-mario": "Doctor Mario",
                  "mr-game-and-watch": "Mr. Game and Watch"}
B_NAMES = ["Neutral B", "Side B", "Up B", "Down B"]


def load_char(cid):
    with open(os.path.join(DATA, "framedata", cid + ".json")) as f:
        return json.load(f)


def frames_str(rs):
    return ", ".join("%d" % a if a == b else "%d-%d" % (a, b) for a, b in rs)


def angle_str(a):
    return "Sakurai" if a == 361 else str(a)


def special_label(entry, key, sub):
    m = re.match(r"Special(Air)?(N|S|Hi|Lw)(.*)", sub)
    if not m:
        return sub
    air, d, rest = m.groups()
    name = "%s: %s" % (B_NAMES[SPECIAL_DIRS[d]],
                       entry["specials"][SPECIAL_DIRS[d]])
    bits = [x for x in ("air" if air else "ground", rest) if x]
    return "%s, %s" % (name, ", ".join(bits))


def move_group(key):
    base = key if key in KEY_INFO else key.rsplit("_", 1)[0]
    if key.startswith("special"):
        return "special"
    if base in KEY_INFO:
        return KEY_INFO[base][1]
    return None


def move_label(entry, key, m):
    if key.startswith("special"):
        return special_label(entry, key, m["subaction"])
    if key in KEY_INFO:
        return KEY_INFO[key][0]
    base = key.rsplit("_", 1)[0]
    return "%s (variant %s)" % (KEY_INFO[base][0], m["subaction"])


def effect_rows(m):
    """Collapse hit windows that share the same set of hitbox effects."""
    rows = []
    for h in m.get("hits", []):
        effs = []
        for b in h["hitboxes"]:
            e = (b["damage"], b["angle"], b["bkb"], b["kbg"], b["wdsk"],
                 b["element"])
            if e not in effs:
                effs.append(e)
        effs = tuple(effs)
        for r in rows:
            if r["effs"] == effs:
                r["frames"].append([h["start"], h["end"]])
                break
        else:
            rows.append({"effs": effs, "frames": [[h["start"], h["end"]]],
                         "hit": h})
    return rows


def notes(m, group):
    n = []
    if m.get("entry_delay"):
        n.append("starts 1 frame late (included)")
    if m.get("no_lcancel"):
        n.append("cannot be L-cancelled")
    if "charge_frame" in m:
        n.append("charge hold frame %d" % m["charge_frame"])
    for state in ("intangible", "invincible"):
        if state in m and group not in ("defense", "tech", "ledge"):
            n.append("%s %s" % (state, frames_str(m[state])))
    for state, parts in m.get("partial", {}).items():
        allf = sorted({tuple(r) for p in parts for r in p["frames"]})
        n.append("partly %s %s (%d bone%s)" % (
            state, frames_str(allf), len(parts),
            "" if len(parts) == 1 else "s"))
    if "projectile_frames" in m:
        n.append("spawns article/projectile on %s" % ", ".join(
            str(x) for x in m["projectile_frames"]))
    if "self_damage" in m:
        n.append("self damage %s" % ", ".join(
            "%d%% on frame %d" % (d, f) for f, d in m["self_damage"]))
    return "; ".join(n)


def cell(x):
    return "-" if x is None else str(x)


def table(header, rows):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("-" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(cell(c) for c in r) + " |")
    return "\n".join(out)


def attack_table(entry, char, keys, air):
    header = ["Move", "Key", "Active", "Dmg", "Angle", "BKB", "KBG",
              "Set KB", "Effect", "Total", "IASA", "Shield stun"]
    header += ["Land lag", "L-cancel", "Autocancel", "On shield (best)"] \
        if air else ["On shield"]
    header.append("Notes")
    rows = []
    for key in keys:
        m = char["moves"][key]
        erows = effect_rows(m)
        common = [m["total_frames"], m.get("iasa")]
        if not erows:
            row = [move_label(entry, key, m), "`%s`" % key, None, None,
                   None, None, None, None, None] + common + [None]
            row += [None] * (4 if air else 1) + [notes(m, None)]
            if air:
                row[12], row[13] = m.get("landing_lag"), \
                    m.get("landing_lag_lcancel")
            rows.append(row)
            continue
        for i, r in enumerate(erows):
            e = r["effs"]

            def col(j):
                vals = []
                for x in e:
                    v = angle_str(x[j]) if j == 1 else str(x[j])
                    if v not in vals:
                        vals.append(v)
                return "/".join(vals)
            dmg = max(x[0] for x in e)
            stun = calc.shield_stun(dmg) if dmg else None
            elems = [x for x in dict.fromkeys(x[5] for x in e)
                     if x != "normal"]
            row = [move_label(entry, key, m) if i == 0 else "",
                   "`%s`" % key if i == 0 else "",
                   frames_str(r["frames"]), col(0), col(1), col(2), col(3),
                   col(4) if any(x[4] for x in e) else None,
                   "/".join(elems)]
            row += common if i == 0 else ["", ""]
            row.append(stun)
            if air:
                ac = m.get("autocancel", {})
                if ac.get("always"):
                    acs = "always"
                else:
                    acs = "<%d, >%d" % (ac.get("before", 0),
                                        ac.get("after", 0))
                adv = calc.shield_advantage_aerial(m, r["hit"])
                row += [m.get("landing_lag") if i == 0 else "",
                        m.get("landing_lag_lcancel") if i == 0 else "",
                        acs if i == 0 else "",
                        "%+d" % adv if adv is not None else None]
            else:
                adv = calc.shield_advantage_ground(m, r["hit"]) \
                    if not key.startswith("special") else None
                row.append("%+d" % adv if adv is not None else None)
            row.append(notes(m, None) if i == 0 else "")
            rows.append(row)
    return table(header, rows)


def grab_table(entry, char, keys):
    out = []
    grabs = [k for k in keys if k in ("grab", "dash_grab")]
    rows = []
    for k in grabs:
        m = char["moves"][k]
        act = [[h["start"], h["end"]] for h in m.get("hits", [])]
        merged = [[act[0][0], act[-1][1]]] if act else []
        rows.append([KEY_INFO[k][0], "`%s`" % k, frames_str(merged),
                     m["total_frames"], notes(m, None)])
    out.append(table(["Move", "Key", "Grab box active", "Total", "Notes"],
                     rows))
    rows = []
    for k in keys:
        if k in grabs:
            continue
        m = char["moves"][k]
        t = m.get("throw")
        hit_dmg = sum(max(b["damage"] for b in h["hitboxes"])
                      for h in m.get("hits", []))
        if t:
            rows.append([KEY_INFO[k][0], "`%s`" % k,
                         t["damage"] + hit_dmg if hit_dmg else t["damage"],
                         t["damage"], angle_str(t["angle"]), t["bkb"],
                         t["kbg"], t["wdsk"] or None,
                         t["element"] if t["element"] != "normal" else None,
                         t.get("release_frame"), m["total_frames"],
                         notes(m, None)])
        else:
            rows.append([KEY_INFO[k][0], "`%s`" % k, hit_dmg or None, None,
                         None, None, None, None, None,
                         m.get("first_hit_frame"), m["total_frames"],
                         notes(m, None)])
    out.append(table(["Move", "Key", "Total dmg", "Throw dmg", "Angle",
                      "BKB", "KBG", "Set KB", "Effect", "Release / hit",
                      "Total", "Notes"], rows))
    return "\n\n".join(out)


def state_table(entry, char, keys, group):
    rows = []
    for k in keys:
        m = char["moves"][k]
        inv = []
        for state in ("intangible", "invincible"):
            if state in m:
                inv.append("%s %s" % (state, frames_str(m[state])))
        hit = None
        if m.get("hits"):
            hs = m["hits"]
            dmg = "/".join(dict.fromkeys(
                str(b["damage"]) for h in hs for b in h["hitboxes"]))
            hit = "%s (%s%%)" % (frames_str(
                [[h["start"], h["end"]] for h in hs]), dmg)
        rows.append([move_label(entry, k, m), "`%s`" % k,
                     "; ".join(inv) or None,
                     hit, m["total_frames"], m.get("iasa"),
                     "starts 1 frame late (included)"
                     if m.get("entry_delay") else ""])
    return table(["Option", "Key", "Intangible / invincible", "Hitbox",
                  "Total", "IASA", "Notes"], rows)


def attributes_block(char):
    a = char["attributes"]
    js = int(a["jump_startup_time"])
    rows = [
        ["Weight", a["weight"]],
        ["Gravity", a["gravity"]],
        ["Terminal fall speed", a["terminal_velocity"]],
        ["Fast-fall speed", a["fast_fall_velocity"]],
        ["Jump squat (frames before airborne)", js],
        ["Full hop / short hop initial Y speed",
         "%s / %s" % (a["jump_v_initial_velocity"],
                      a["hop_v_initial_velocity"])],
        ["Air jump Y multiplier", a["air_jump_v_multiplier"]],
        ["Jumps", a["max_jumps"]],
        ["Walk max speed", a["walk_max_vel"]],
        ["Dash initial speed / run max speed",
         "%s / %s" % (a["dash_initial_velocity"], a["dash_max_velocity"])],
        ["Ground friction (traction)", a["ground_friction"]],
        ["Air max horizontal speed", a["air_drift_max"]],
        ["Air acceleration (base + stick)",
         "%s + %s" % (a["aerial_drift_base"], a["air_drift_stick_mul"])],
        ["Air friction", a["aerial_friction"]],
        ["Normal landing lag", a["normal_landing_lag"]],
        ["Shield size", a["initial_shield_size"]],
    ]
    out = ["## Attributes", "",
           "Read from `%s` (`ftCo_DatAttrs`). Speeds are game units per "
           "frame." % char["dat"], "",
           table(["Attribute", "Value"], rows)]
    return "\n".join(out)


def oos_block(char):
    rows = [[o["option"], o["via"], o["frame"], "`%s`" % o["move"]]
            for o in calc.oos_options(char)]
    m = char["moves"]
    for key in ("spotdodge", "roll_forward", "roll_backward"):
        if key in m and "intangible" in m[key]:
            rows.append([KEY_INFO[key][0], "direct",
                         "intangible %s of %d" % (
                             frames_str(m[key]["intangible"]),
                             m[key]["total_frames"]), "`%s`" % key])
    js = int(char["attributes"]["jump_startup_time"])
    rows.append(["Wavedash", "jump",
                 "actionable on frame %d" % (js + 1 + 10 + 1), "-"])
    return table(["Option", "Via", "Hitbox out on frame", "Key"], rows)


def framedata_block(entry, char):
    out = ["## Frame data", ""]
    out.append(
        "Extracted from the game's own files (`%s`, NTSC 1.02) by "
        "`tools/melee_data/extract.py`; machine-readable copy in "
        "[`../framedata/%s.json`](../framedata/%s.json). Conventions are "
        "in [`../README.md`](../README.md#frame-data-conventions): frames "
        "are 1-indexed, `Active` lists the frames a hitbox is out, `IASA` "
        "is the first frame the move can be interrupted, `Total` is the "
        "animation length (first actionable frame is IASA, or Total + 1), "
        "`Set KB` is weight-dependent set knockback, angle `Sakurai` is "
        "the special angle 361. `On shield` is the frame advantage when "
        "the first active frame hits a full hard shield (negative = the "
        "defender acts first). Projectile and article hitboxes (lasers, "
        "needles, turnips, missiles...) are not in fighter scripts and "
        "are not listed." % (char["dat"], entry["id"], entry["id"]))
    by_group = {}
    for key in char["moves"]:
        g = move_group(key)
        if g:
            by_group.setdefault(g, []).append(key)
    for g, title in GROUPS:
        keys = by_group.get(g)
        if not keys:
            continue
        out += ["", "### " + title, ""]
        if g in ("ground", "special"):
            if g == "special":
                out += ["One row per script (special moves are split into "
                        "several states). Frames count from the start of "
                        "that state; a few specials start one frame later "
                        "in game than the script says, so treat +/-1 as "
                        "unverified until checked in game.", ""]
            out.append(attack_table(entry, char, keys, False))
        elif g == "air":
            out += ["`Autocancel` `<a, >b`: landing before frame a or "
                    "after frame b gives normal landing lag (%s frames) "
                    "instead of the aerial's. `On shield (best)` assumes "
                    "an L-cancelled landing on the frame after the hit."
                    % char["attributes"]["normal_landing_lag"], "",
                    attack_table(entry, char, keys, True)]
        elif g == "grab":
            out.append(grab_table(entry, char, keys))
        else:
            if g == "tech":
                out += ["Tech and getup-stand intangibility is listed as "
                        "the script gives it, shifted by the entry delay "
                        "(so 2-20 where community tables say 1-20).", ""]
            out.append(state_table(entry, char, keys, g))
    out += ["", "### Out of shield options (computed)", "",
            "Frame the hitbox first comes out, counting the first frame "
            "the player acts out of shield as frame 1. Aerials: jump squat "
            "+ aerial startup. Up smash and up B: jump-cancelled, 1 + "
            "startup. Shield release (15 frames of `GuardOff`) is not "
            "needed for any of these.", "", oos_block(char)]
    return "\n".join(out)


def library_cards(entry):
    path = os.path.join(DATA, "resources", "meleelibrary.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        lib = json.load(f)
    title = LIBRARY_TITLES.get(entry["id"], entry["name"])
    for sec in lib:
        if sec["title"] == title:
            return sec["cards"]
    return []


def md_escape(s):
    return s.replace("|", "\\|").replace("\n", " ")


def resources_block(entry):
    cards = library_cards(entry)
    out = ["## Resources", "",
           "Community guides for %s indexed by [The Melee Library]"
           "(https://www.meleelibrary.com/#%s) (snapshot 2026-11-11). "
           "Videos cannot be read by an agent; use titles and descriptions "
           "as pointers to what the community considers important."
           % (entry["name"], re.sub(r"[^a-z]+", "-", LIBRARY_TITLES.get(
               entry["id"], entry["name"]).lower()).strip("-")), ""]
    if not cards:
        out.append("None listed.")
        return "\n".join(out)
    rows = []
    for c in cards:
        t = md_escape(c["title"] or "(untitled)")
        link = "[%s](%s)" % (t, c["url"]) if c["url"] else t
        rows.append([link, md_escape(c["author"]),
                     md_escape(c["description"])])
    out.append(table(["Resource", "Author", "About"], rows))
    return "\n".join(out)


def front_matter_generated(entry, char):
    a = char["attributes"]
    m = char["moves"]
    lines = ["# generated: begin (tools/melee_data/render.py, do not edit)",
             "dat: %s" % char["dat"],
             "framedata: ../framedata/%s.json" % entry["id"],
             "code: src/melee/ft/kinds/%s" % entry["code"],
             "specials:"]
    for d, n in zip(("neutral_b", "side_b", "up_b", "down_b"),
                    entry["specials"]):
        lines.append("  %s: \"%s\"" % (d, n))
    lines.append("attributes:")
    for k, label in (("weight", "weight"), ("gravity", "gravity"),
                     ("terminal_velocity", "fall_speed"),
                     ("fast_fall_velocity", "fast_fall_speed"),
                     ("jump_startup_time", "jump_squat"),
                     ("max_jumps", "jumps"),
                     ("walk_max_vel", "walk_speed"),
                     ("dash_initial_velocity", "dash_speed"),
                     ("dash_max_velocity", "run_speed"),
                     ("ground_friction", "traction"),
                     ("air_drift_max", "air_speed"),
                     ("normal_landing_lag", "landing_lag")):
        lines.append("  %s: %s" % (label, a[k]))
    lines.append("moves:  # key: [first hit frame, first actionable frame, "
                 "max damage]")
    for key, mv in m.items():
        g = move_group(key)
        if g not in ("ground", "air", "grab", "special"):
            continue
        dmg = max([b["damage"] for h in mv.get("hits", [])
                   for b in h["hitboxes"]] + [0])
        if "throw" in mv:
            dmg = mv["throw"]["damage"]
        lines.append("  %s: [%s, %d, %d]" % (
            key, mv.get("first_hit_frame") or "null", calc.faf(mv), dmg))
    lines.append("oos:  # option: frame the hitbox is out")
    for o in calc.oos_options(char):
        lines.append("  %s: %d" % (o["move"], o["frame"]))
    lines.append("resources: %d" % len(library_cards(entry)))
    lines.append("# generated: end")
    return lines


STUB = """---
schema: melee-character/v1
id: {id}
name: {name}
---

# {name}

<!-- GENERATED:attributes -->
<!-- /GENERATED:attributes -->

<!-- GENERATED:framedata -->
<!-- /GENERATED:framedata -->

<!-- GENERATED:resources -->
<!-- /GENERATED:resources -->
"""


def replace_block(text, name, body):
    pat = re.compile(r"<!-- GENERATED:%s -->.*?<!-- /GENERATED:%s -->"
                     % (name, name), re.S)
    new = "<!-- GENERATED:%s -->\n%s\n<!-- /GENERATED:%s -->" % (
        name, body, name)
    if not pat.search(text):
        return text.rstrip("\n") + "\n\n" + new + "\n"
    return pat.sub(lambda _: new, text, count=1)


def render(entry):
    char = load_char(entry["id"])
    path = os.path.join(DATA, "characters", entry["id"] + ".md")
    if os.path.exists(path):
        with open(path) as f:
            text = f.read()
    else:
        text = STUB.format(id=entry["id"], name=entry["name"])
    # front matter
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit("%s: no front matter" % path)
    fm = re.sub(r"# generated: begin.*?# generated: end\n?", "",
                m.group(1) + "\n", flags=re.S).rstrip("\n")
    fm = fm + "\n" + "\n".join(front_matter_generated(entry, char))
    text = "---\n" + fm + "\n---\n" + text[m.end():]
    text = replace_block(text, "attributes", attributes_block(char))
    text = replace_block(text, "framedata", framedata_block(entry, char))
    text = replace_block(text, "resources", resources_block(entry))
    with open(path, "w") as f:
        f.write(text)
    return path


def fm_field(text, key):
    """One scalar/inline-list field from YAML front matter, as text."""
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return ""
    f = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), m.group(1), re.M)
    return f.group(1).strip().strip('"') if f else ""


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text.rstrip("\n") + "\n")


def character_index():
    rows = []
    for e in ROSTER:
        path = os.path.join(DATA, "characters", e["id"] + ".md")
        with open(path) as f:
            text = f.read()
        a = load_char(e["id"])["attributes"]
        rows.append(["[%s](%s.md)" % (e["name"], e["id"]), "`%s`" % e["id"],
                     md_escape(fm_field(text, "tier")), a["weight"],
                     a["terminal_velocity"], a["gravity"],
                     int(a["jump_startup_time"]),
                     md_escape(fm_field(text, "archetype").strip("[]")),
                     md_escape(fm_field(text, "summary"))])
    out = ["# Characters", "",
           "Generated by `tools/melee_data/render.py` from each file's "
           "front matter and `../framedata/*.json`. One file per character: "
           "strategy, character tech, punishes, recovery, drill seeds, "
           "exact frame data and community resources.", "",
           table(["Character", "id", "Tier", "Weight", "Fall speed",
                  "Gravity", "Jump squat", "Archetype", "How they win"],
                 rows)]
    write(os.path.join(DATA, "characters", "README.md"), "\n".join(out))


def technique_index():
    d = os.path.join(DATA, "techniques")
    if not os.path.isdir(d):
        return
    rows = []
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md") or name == "README.md":
            continue
        with open(os.path.join(d, name)) as f:
            text = f.read()
        rows.append(["[%s](%s)" % (fm_field(text, "name") or name[:-3],
                                   name), "`%s`" % name[:-3],
                     fm_field(text, "category"),
                     fm_field(text, "difficulty"),
                     md_escape(fm_field(text, "summary"))])
    out = ["# Techniques and mechanics", "",
           "Generated index. Universal (not character-specific) techniques "
           "and the formulas behind them. Character files link here.", "",
           table(["Technique", "id", "Category", "Difficulty", "Summary"],
                 rows)]
    write(os.path.join(d, "README.md"), "\n".join(out))


def library_pages():
    path = os.path.join(DATA, "resources", "meleelibrary.json")
    if not os.path.exists(path):
        return
    with open(path) as f:
        lib = json.load(f)
    char_titles = {LIBRARY_TITLES.get(e["id"], e["name"]): e for e in ROSTER}
    index, parent = [], ""
    for sec in lib:
        if sec["level"] == 1:
            parent = sec["title"]
        if not sec["cards"]:
            continue
        if sec["title"] in char_titles:
            e = char_titles[sec["title"]]
            index.append(["[%s](../characters/%s.md#resources)" % (
                sec["title"], e["id"]), "Character Guides",
                len(sec["cards"]), "in the character file"])
            continue
        slug = slugify(sec["title"])
        rows = []
        for c in sec["cards"]:
            t = md_escape(c["title"] or "(untitled)")
            rows.append(["[%s](%s)" % (t, c["url"]) if c["url"] else t,
                         md_escape(c["author"]),
                         md_escape(c["description"])])
        desc = sec.get("description") or ""
        out = ["---", "schema: melee-resources/v1", "id: %s" % slug,
               "title: \"%s\"" % sec["title"],
               "section: \"%s\"" % (parent if parent != sec["title"]
                                     else ""),
               "source: https://www.meleelibrary.com/",
               "snapshot: 2026-11-11", "count: %d" % len(sec["cards"]),
               "---", "", "# %s" % sec["title"], ""]
        if desc:
            out += [desc, ""]
        out += ["Links collected by The Melee Library. Titles, authors and "
                "descriptions are theirs; videos and forum threads are "
                "pointers, not content an agent can read here.", "",
                table(["Resource", "Author", "About"], rows)]
        write(os.path.join(DATA, "resources", "library", slug + ".md"),
              "\n".join(out))
        index.append(["[%s](library/%s.md)" % (sec["title"], slug),
                      parent if parent != sec["title"] else "",
                      len(sec["cards"]), md_escape(desc)])
    out = ["# Resources", "",
           "Index of [The Melee Library](https://www.meleelibrary.com/) "
           "(one page of curated links; snapshot 2026-11-11, parsed by "
           "`tools/melee_data/library.py` into `meleelibrary.json`). "
           "Character sections are merged into the character files.", "",
           table(["Section", "Part of", "Links", "About"], index)]
    write(os.path.join(DATA, "resources", "README.md"), "\n".join(out))


def main():
    want = set(sys.argv[1:])
    for entry in ROSTER:
        if want and entry["id"] not in want:
            continue
        p = render(entry)
        print(os.path.relpath(p, REPO))
    character_index()
    technique_index()
    library_pages()


if __name__ == "__main__":
    main()
