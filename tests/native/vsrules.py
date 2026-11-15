"""A Versus match's rules on the native build (the host's `vsrules`,
src/host/match.c): a time limit, items, the damage ratio, headless.

    python tests/native/vsrules.py

The owner, 2026-11-14: "global options openable via Z which has basic
settings like time, items, random stage selection filters, etc. just like
the original game!". The client's Rules (modes.Rules) reach the game as
native.match's `rules`; this proves the game plays them:

- the damage ratio at 2.0 sends twice as hard: Marth at 60% is launched
  by Fox's forward smash with twice the hitstun (knockback x 0.4; the
  game's ratio is a
  factor of the knockback of a fighter's hits and throws, ftcoll.c's
  ftColl_80079AB0, not of the damage: the forward smash deals its own);
- with items at "very high", the game spawns them (state()'s "items": an
  item of the common kinds), and with only the Bob-omb switched on, every
  item it spawns is a Bob-omb or carries one (a capsule, crate, barrel or
  egg);
- with a 10-second limit the game's clock ends the match (TIME!): state()'s
  "ended" moves on and its "outcome" is the time-out (1);
- the next match asked for with no rules has neither items nor a clock (a
  drill's, the Lab's: they never inherit Versus's).
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))

import native  # noqa: E402

OUTCOME_TIMEOUT = 1
COMMON = range(0, 0x23)              # the game's common items (ItemKind)
CONTAINERS = {0, 1, 2, 3}            # capsule, crate, barrel, egg
BOBOMB = 0x06
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


def smash_launch(n, rules):
    """(Marth's damage, his hitstun as hitlag ends: the knockback x 0.4)
    from Fox's forward smash at 60%, in a match with `rules`."""
    n.start("fox", "marth", "final-destination", seed=3, rules=rules)
    n.place(0, -10, 0, facing=1)
    n.place(1, 6, 0, facing=-1, percent=60.0)
    n.step(10)
    before = n.fighter(1).percent
    n.pad(0, cstick=(1, 0))
    n.step(2)
    n.pad(0)
    for _ in range(60):              # the smash's hit, then hitlag
        n.step()
        f = n.state()["p"][1]
        if f["percent"] > before and not f["hitlag"]:
            break
    f = n.state()["p"][1]
    return f["percent"] - before, f["hitstun"]


def main():
    n = native.Native()
    try:
        dmg1, speed1 = smash_launch(n, None)
        dmg2, speed2 = smash_launch(n, dict(ratio=2.0))
        check("the damage ratio at 2.0: the same damage, about twice the "
              "knockback (hitstun)", dmg1 > 0 and dmg1 == dmg2 and speed1 > 0 and
              1.8 < speed2 / speed1 < 2.2,
              "%.1f%% at %.2f, then %.1f%% at %.2f" % (dmg1, speed1, dmg2,
                                                     speed2))

        # items at very high, only the Bob-omb on
        n.start("fox", "marth", "final-destination", seed=5,
                rules=dict(items=4, mask=0xF | 1 << BOBOMB))
        kinds = set()
        for _ in range(60 * 40):     # 40 s at most
            n.step()
            kinds |= {it["kind"] for it in n.state()["items"]
                      if it["kind"] in COMMON}
            if kinds - CONTAINERS:
                break
        check("items at very high: the game spawns them",
              bool(kinds), "kinds %s" % sorted(kinds))
        check("only the Bob-omb switched on: nothing else comes, but in a "
              "container", kinds <= CONTAINERS | {BOBOMB},
              "kinds %s" % sorted(kinds))

        # a 10-second clock
        n.start("fox", "marth", "final-destination", seed=7,
                rules=dict(time=10), settle=False)
        ended = n.state()["ended"]
        for frame in range(60 * 30):  # 10 s, the countdown, TIME!'s freeze
            n.step()
            if n.state()["ended"] != ended:
                break
        st = n.state()
        check("a 10-second limit: the game's clock ends the match, a "
              "time-out", st["ended"] != ended and
              st["outcome"] == OUTCOME_TIMEOUT,
              "after %d frames: ended %d -> %d, outcome %d" % (
                  frame + 1, ended, st["ended"], st["outcome"]))

        # no rules: neither items nor a clock
        n.start("fox", "marth", "final-destination", seed=5, settle=False)
        ended = n.state()["ended"]
        seen = set()
        for _ in range(60 * 15):
            n.step()
            seen |= {it["kind"] for it in n.state()["items"]
                     if it["kind"] in COMMON}
        st = n.state()
        check("the next match with no rules: no items, no clock",
              not seen and st["ended"] == ended,
              "items %s, ended %d -> %d" % (sorted(seen), ended,
                                            st["ended"]))
    finally:
        n.close()
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
