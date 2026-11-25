"""Where crouch cancel stops, measured in the game.

For an opponent's move from a distance against a character crouching: the
most damage (the character's before the hit) at which the hit leaves it on
its feet. Above it the hit tumbles the character: two thirds of the
knockback is still past the game's 80. Found by a binary search, each
step a play of the drill runtime (the opponent stands, then plays the move
with the engine's `move`; the character holds down from the first frame).

    python tools/melee_drills/cc_limits.py [--opponents a,b] [--moves m,m]
        [--distances 12,18,24,30] [--chars a,b] [--jobs N] [--out FILE]
    python tools/melee_drills/cc_limits.py --table
    python tools/melee_drills/cc_limits.py --asdi [the same options]

Writes data/actor/crouch_cancel.json:
    {"limits": {OPPONENT: {MOVE: {DISTANCE: {CHARACTER: LIMIT}}}}}
LIMIT: the damage; null where the move did not hit the crouching character
from there; -1 where it knocked it down at 0%; 260 where it still held at
260% (the search's top). `least(opponent, move)` gives, per character, the
least over the distances it hit from: what the crouch cancel drill draws a
try's damage under (data/drills/universal-crouch-cancel.json).

--asdi measures where ASDI down stops instead: the character stands and
holds the C-stick down through the hit's freeze (found by a first play);
the limit is the most damage at which it is on the floor when the freeze
ends, neither lifted nor knocked down. Without the crouch's two thirds the
knockback reaches the game's 80 sooner. Written to
data/actor/asdi_down.json, with "hitlag": the freeze of each hit in frames
(the same shape): what universal-asdi's example holds the C-stick for; and
"lifts": whether the hit lifts the character at 0% when it holds nothing
(false: it stays on the floor anyway, and there is nothing to ASDI down).

The whole table (11 opponents, 6 moves, 4 distances, 26 characters) takes
about 2 hours of one core; --jobs divides it by opponent. --table measures
nothing: it writes the table's summary (Fox, the lightest and the heaviest
character) into data/techniques/crouch-cancel.md, between its markers
(with --asdi: ASDI down's, into data/techniques/asdi.md).
"""
import argparse
import copy
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))

OUT = os.path.join(ROOT, "data", "actor", "crouch_cancel.json")
TOP11 = ("fox", "marth", "jigglypuff", "falco", "sheik", "captain-falcon",
         "peach", "ice-climbers", "pikachu", "yoshi", "samus")
MOVES = ("dtilt", "ftilt", "jab", "fsmash", "dsmash", "run_attack")
DISTANCES = (12, 18, 24, 30)
TOP = 260
# knocked off its feet: lying down, the fall of a hit, a tumble
FALLEN = frozenset(range(183, 199)) | {38, 87, 88, 89, 90, 91}
CROUCH = [{"stick": [0, -1], "frame": 1, "hold": 300}]
IDLE = [{"stick": [0, 0], "frame": 1, "hold": 1}]
ASDI_OUT = os.path.join(ROOT, "data", "actor", "asdi_down.json")
ASDI_MOVES = ("dtilt", "ftilt", "jab", "run_attack")
ASDI_DISTANCES = (10, 13, 16, 24, 30)


def characters():
    return sorted(f[:-5] for f in os.listdir(
        os.path.join(ROOT, "data", "framedata")) if f.endswith(".json"))


class Enough(Exception):
    pass


def base():
    """The crouch cancel drill with one scenario to fill in: its words,
    measures and checks are a drill's, as the format wants them."""
    from melee_drills import format as fmt
    spec = copy.deepcopy(fmt.load("universal-crouch-cancel"))
    spec["attempt"] = {"start": "their_attack", "judge": {"frame": 120},
                       "cancel": [], "limit": 140, "within": 300}
    spec.pop("shield", None)
    first = spec["scenarios"][0]
    for p in spec["parts"]:
        p.pop("attempt", None)
        p["scenario"] = 0
    spec["tutorial"]["lessons"] = spec["tutorial"]["lessons"][:1]
    for les in spec["tutorial"]["lessons"]:
        les.pop("scenario", None)
    spec["scenarios"] = [{"name": "x", "stage": "final-destination",
                          "player": {"x": -20, "percent": 0},
                          "opponent": {}, "camera": "normal",
                          "numbers": dict(first["numbers"])}]
    return spec


def played(game, spec, opponent, move, distance, ch, percent, inputs,
           frames=110):
    """The character's frames against the move: [(damage, state,
    airborne, hitlag)], and the index of the hit (None: not hit)."""
    from melee_course import engine
    from melee_drills.drill import JsonDrill, inputs_to_refs
    sc = spec["scenarios"][0]
    sc["player"]["percent"] = percent
    sc["opponent"] = {
        "character": opponent, "x": -20 + distance, "facing": "player",
        "script": [{"do": "hold", "pad": "stand", "for": 30},
                   {"do": "move", "name": move},
                   {"do": "hold", "pad": "shield"}]}
    drill = JsonDrill(spec)
    s = engine.Session(drill, game, character=ch, live=False, seed=1,
                       dpad=False)
    drill.build_reference = lambda c: inputs_to_refs(
        inputs, drill.nums(c), drill.ref_start)
    lead = drill.ref_lead + drill.ref_start - 1
    seen = []

    def each(g, frame):
        if s.demo_pass != 2 or frame <= lead + 1:
            return
        me = g.fighter(s.person)
        seen.append((me.percent, me.state, bool(me.airborne), me.hitlag))
        if len(seen) >= frames:
            raise Enough()
    try:
        s.run(demo=True, each_frame=each)
    except Enough:
        pass
    hit = next((k for k, row in enumerate(seen)
                if row[0] > percent + 0.01), None)
    return seen, hit


def held(game, spec, opponent, move, distance, ch, percent, frames=110):
    """True: hit, and on its feet; False: knocked down; None: not hit."""
    seen, hit = played(game, spec, opponent, move, distance, ch, percent,
                       CROUCH, frames)
    if hit is None:
        return None
    return not any(row[1] in FALLEN for row in seen[hit:])


def freeze(game, spec, opponent, move, distance, ch):
    """(the example frame the hit lands on, its freeze in frames, whether
    it lifts the character off the floor) for the character standing at
    0%, holding nothing; None: not hit."""
    seen, hit = played(game, spec, opponent, move, distance, ch, 0, IDLE)
    if hit is None:
        return None
    n = 0
    while hit + n < len(seen) and seen[hit + n][3] > 0:
        n += 1
    return hit + 1, n, any(row[2] for row in seen[hit + n:hit + n + 10])


def landed(game, spec, opponent, move, distance, ch, percent, at, n):
    """ASDI down: the C-stick down from the frame after the hit (example
    frame `at`) through its freeze of `n` frames. True: on the floor when
    the freeze ends, and not knocked down."""
    seen, hit = played(game, spec, opponent, move, distance, ch, percent,
                       [{"cstick": [0, -1], "frame": at + 1, "hold": n}])
    if hit is None:
        return None
    after = seen[hit + n:hit + n + 40]
    return not any(row[2] or row[1] in FALLEN for row in after)


def search(ok):
    """The most damage `ok` holds at: -1 not even at 0, TOP still there."""
    first = ok(0)
    if first is None:
        return None
    if not first:
        return -1
    if ok(TOP):
        return TOP
    lo, hi = 0, TOP
    while hi - lo > 1:
        mid = (lo + hi) // 2
        got = ok(mid)
        if got is None:
            return None
        if got:
            lo = mid
        else:
            hi = mid
    return lo


def limit(game, spec, opponent, move, distance, ch):
    first = held(game, spec, opponent, move, distance, ch, 0)
    if first is None:
        return None
    if not first:
        return -1
    if held(game, spec, opponent, move, distance, ch, TOP):
        return TOP
    lo, hi = 0, TOP
    while hi - lo > 1:
        mid = (lo + hi) // 2
        got = held(game, spec, opponent, move, distance, ch, mid)
        if got is None:
            return None
        if got:
            lo = mid
        else:
            hi = mid
    return lo


def measure(job):
    """One opponent's table: {move: {distance: {character: limit}}}; with
    ASDI down, each hit's freeze too, in the same shape."""
    opponent, moves, distances, chars, asdi = job
    from native import Native
    spec = base()
    out = {m: {str(d): {} for d in distances} for m in moves}
    lag = {m: {str(d): {} for d in distances} for m in moves}
    lift = {m: {str(d): {} for d in distances} for m in moves}
    for ch in chars:
        with Native() as game:
            for m in moves:
                for d in distances:
                    if not asdi:
                        out[m][str(d)][ch] = limit(game, spec, opponent, m,
                                                   d, ch)
                        continue
                    got = freeze(game, spec, opponent, m, d, ch)
                    if got is None:
                        out[m][str(d)][ch] = lag[m][str(d)][ch] = None
                        lift[m][str(d)][ch] = None
                        continue
                    at, n, up = got
                    lag[m][str(d)][ch] = n
                    lift[m][str(d)][ch] = up
                    out[m][str(d)][ch] = search(
                        lambda p: landed(game, spec, opponent, m, d, ch, p,
                                         at, n))
    return opponent, out, lag, lift


def least(table, opponent, move):
    """Per character, the least limit over the distances the move hit it
    from (those it knocked it down from at 0% count as -1)."""
    out = {}
    for by_char in table[opponent][move].values():
        for ch, v in by_char.items():
            if v is not None:
                out[ch] = v if ch not in out else min(out[ch], v)
    return out


PAGE = os.path.join(ROOT, "data", "techniques", "crouch-cancel.md")
NAMES = {"fox": "Fox", "marth": "Marth", "jigglypuff": "Jigglypuff",
         "falco": "Falco", "sheik": "Sheik",
         "captain-falcon": "Captain Falcon", "peach": "Peach",
         "ice-climbers": "Ice Climbers", "pikachu": "Pikachu",
         "yoshi": "Yoshi", "samus": "Samus"}
WORDS = {"dtilt": "down tilt", "ftilt": "forward tilt", "jab": "jab",
         "fsmash": "forward smash", "dsmash": "down smash",
         "run_attack": "dash attack"}
OPEN, CLOSE = "<!-- cc-limits", "<!-- /cc-limits -->"


ASDI_PAGE = os.path.join(ROOT, "data", "techniques", "asdi.md")
ASDI_OPEN, ASDI_CLOSE = "<!-- asdi-limits", "<!-- /asdi-limits -->"


def asdi_table(table, hitlag):
    """ASDI down's table for its page: per opponent and move, for the
    distances it hit every character from, the least limit of Fox, Pichu
    and Bowser, and the hit's freeze."""
    def show(v):
        return "not at 0%" if v < 0 else "%d+" % TOP if v >= TOP else \
            "%d%%" % v
    rows = []
    for cpu in TOP11:
        for move in ASDI_MOVES:
            by_d = table.get(cpu, {}).get(move, {})
            full = {d: per for d, per in by_d.items()
                    if per and all(v is not None for v in per.values())}
            if not full:
                continue
            chars = next(iter(full.values()))
            lo = {ch: min(per[ch] for per in full.values()) for ch in chars}
            hi = {ch: max(per[ch] for per in full.values()) for ch in chars}
            spread = max(hi[ch] - lo[ch] for ch in chars)
            lag = sorted({v for d in full
                          for v in hitlag[cpu][move][d].values()
                          if v is not None})
            rows.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                NAMES[cpu], WORDS[move], ", ".join(sorted(full, key=int)),
                show(lo["fox"]), show(lo["pichu"]), show(lo["bowser"]),
                " or ".join(map(str, lag)),
                "the same from each" if spread == 0 else
                "up to %d more from another" % spread))
    words = (
        "Measured in this build (`python tools/melee_drills/cc_limits.py "
        "--asdi`, every character in\n`data/actor/asdi_down.json`): the "
        "most damage, before the hit, at which a standing\ncharacter that "
        "holds the C-stick down through the hit's freeze is on the floor "
        "when the\nfreeze ends and stays on its feet: band 1 above. One "
        "percent more and the hit tumbles it\nor lifts it. Listed for the "
        "distances (units between the two) the move hit all 26\ncharacters "
        "from. \"%d+\": still held at %d%%, where the search stops (the "
        "weakest jabs);\n\"not at 0%%\": lifted or knocked down even at 0%% "
        "(the Ice Climbers: the partner's hit\ncomes after the first)."
        % (TOP, TOP))
    return (ASDI_OPEN + ": python tools/melee_drills/cc_limits.py --asdi "
            "--table -->\n" + words + "\n\n"
            "| Opponent | Move | From | Fox holds to | Pichu | Bowser | "
            "Freeze (frames) | By distance |\n|-|-|-|-|-|-|-|-|\n" +
            "\n".join(rows) + "\n" + ASDI_CLOSE)


def page_table(table):
    """The page's table: per opponent and move, for the distances it hit
    every character from, the least limit of Fox, Pichu and Bowser."""
    def show(v):
        return "falls at 0%" if v < 0 else "%d+" % TOP if v >= TOP else \
            "%d%%" % v
    rows = []
    for cpu in TOP11:
        for move in MOVES:
            by_d = table.get(cpu, {}).get(move, {})
            full = {d: per for d, per in by_d.items()
                    if per and all(v is not None for v in per.values())}
            if not full:
                continue
            chars = next(iter(full.values()))
            lo = {ch: min(per[ch] for per in full.values()) for ch in chars}
            hi = {ch: max(per[ch] for per in full.values()) for ch in chars}
            spread = max(hi[ch] - lo[ch] for ch in chars)
            rows.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                NAMES[cpu], WORDS[move], ", ".join(sorted(full, key=int)),
                show(lo["fox"]), show(lo["pichu"]), show(lo["bowser"]),
                "the same from each" if spread == 0 else
                "up to %d more from another" % spread))
    return (OPEN + ": python tools/melee_drills/cc_limits.py --table -->\n"
            "Measured in this build (`python tools/melee_drills/"
            "cc_limits.py`, every character in\n"
            "`data/actor/crouch_cancel.json`): the most damage, before the "
            "hit, at which a crouching\ncharacter stays on its feet. One "
            "percent more and the hit tumbles it. Listed for the\n"
            "distances (units between the two) the move hit all 26 "
            "crouching characters from; where a\nmove has a weak and a "
            "strong part the least is given, and the last column says how "
            "far\nthe distances differ.\n\n"
            "| Opponent | Move | From | Fox holds to | Pichu | Bowser | By "
            "distance |\n|-|-|-|-|-|-|-|\n" + "\n".join(rows) + "\n" +
            CLOSE)


def write_page(table, hitlag=None):
    page, a, b, text = (PAGE, OPEN, CLOSE, None) if hitlag is None else (
        ASDI_PAGE, ASDI_OPEN, ASDI_CLOSE, asdi_table(table, hitlag))
    s = open(page).read()
    if a not in s:
        raise SystemExit("no %s ... %s in %s" % (a, b, page))
    s = s[:s.index(a)] + (text or page_table(table)) + \
        s[s.index(b) + len(b):]
    open(page, "w").write(s)
    print("wrote the table into", page)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--table", action="store_true",
                    help="write the measured table's summary into the "
                         "knowledge base's page, and measure nothing")
    ap.add_argument("--asdi", action="store_true",
                    help="where ASDI down stops (the character standing, "
                         "the C-stick down through the freeze), into "
                         "data/actor/asdi_down.json")
    ap.add_argument("--opponents", default=",".join(TOP11))
    ap.add_argument("--moves")
    ap.add_argument("--distances")
    ap.add_argument("--chars", help="characters crouching (all 26)")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--out")
    args = ap.parse_args()
    args.out = args.out or (ASDI_OUT if args.asdi else OUT)
    args.moves = args.moves or ",".join(ASDI_MOVES if args.asdi else MOVES)
    args.distances = args.distances or ",".join(map(str, (
        ASDI_DISTANCES if args.asdi else DISTANCES)))
    if args.table:
        doc = json.load(open(args.out))
        write_page(doc["limits"], doc["hitlag"] if args.asdi else None)
        return
    chars = args.chars.split(",") if args.chars else characters()
    moves = args.moves.split(",")
    distances = [int(d) for d in args.distances.split(",")]
    jobs = [(o, moves, distances, chars, args.asdi)
            for o in args.opponents.split(",")]
    table, hitlag, lifts = {}, {}, {}
    if os.path.exists(args.out):
        was = json.load(open(args.out))
        table, hitlag = was.get("limits", {}), was.get("hitlag", {})
        lifts = was.get("lifts", {})
    with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        for opponent, got, lag, lift in pool.map(measure, jobs):
            for into, new in ((table, got), (hitlag, lag), (lifts, lift)):
                mine = into.setdefault(opponent, {})
                for m, by_d in new.items():
                    for d, by_char in by_d.items():
                        mine.setdefault(m, {}).setdefault(d, {}).update(
                            by_char)
            print("%s: %d moves, %d distances, %d characters" % (
                opponent, len(moves), len(distances), len(chars)),
                flush=True)
    about = ("The most damage at which a %s when hit by an opponent's "
             "move from a distance (units): null not hit, -1 not even at "
             "0%%, %d still at %d%%. tools/melee_drills/cc_limits.py%s" % (
                 "standing character that holds the C-stick down through "
                 "the hit's freeze (ASDI down) is on the floor when it "
                 "ends" if args.asdi else
                 "crouching character stays on its feet", TOP, TOP,
                 " --asdi; hitlag: the freeze in frames; lifts: whether "
                 "the hit lifts it at 0% when it holds nothing"
                 if args.asdi
                 else ""))
    doc = {"about": about, "limits": table}
    if args.asdi:
        doc["hitlag"] = hitlag
        doc["lifts"] = lifts
    json.dump(doc, open(args.out, "w"), indent=1, sort_keys=True)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
