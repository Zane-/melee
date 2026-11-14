"""The course drills the owner changed on the native build, checked there.

    python tests/course/native_changes.py

From the owner's play session (2026-11-13). The overlay's specs prove the
rest of each drill (tests/course/specs.py plays these drills the C's way
where an option can, and marks the specs whose behaviour changed). Here:

- dash dance: direction switches counted, the dance ends when the player
  stops (a success) or runs (a failure), the longest dance is kept, and a
  light ray (target) reached brings the next;
- Illusion: levels 1 to 4, the frame of the window the second B is on,
  taken in turn;
- short hop double laser: a laser after a double jump does not make a pair
  with the first (the owner saw a ledge jump counted);
- JC grab: an up smash is not counted (it has its own drill); JC up smash
  succeeds out of jump squat and fails as an up air;
- waveshine: a landing 5 frames late still counts by default, 6 does not;
- every result of a timing drill carries a timeline.
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from native import Native  # noqa: E402
from melee_course import engine, registry  # noqa: E402
from melee_course.engine import B, X, Z  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))


def play(session, script, start=20):
    """One attempt with the player's pad from `script`: {frame: pad} from
    the attempt's frame `start` on (the frame numbers are the loop's), each
    pad held until the next entry."""
    keys = sorted(script)
    held = dict(buttons=0)

    def each(game, frame):
        f = frame - start
        for k in keys:
            if k == f:
                held.clear()
                held.update(script[k])
        session.set_player_pad(**held)
    return session.run(each_frame=each)


def play_pad(session, script, frame, start=20):
    """The pad `script` holds at loop frame `frame` (see play)."""
    f = frame - start
    held = dict(buttons=0)
    for k in sorted(script):
        if k <= f:
            held = script[k]
    session.set_player_pad(**held)


def drill(game, ident, **options):
    return engine.Session(registry.get(ident), game, live=False, seed=7,
                          options=options)


def dance(dashes, each=8, then=None):
    """Dashes of `each` frames, right first, then `then` (a pad) or let
    go."""
    script = {}
    for k in range(dashes):
        script[k * each] = dict(lx=127 if k % 2 == 0 else -127)
    script[dashes * each] = then or dict()
    return script


def main():
    with Native() as game:
        # ---- dash dance --------------------------------------------------
        s = drill(game, "universal-dash-dance", Targets=1)     # rays off
        r = play(s, dance(5))
        check("dash dance: five dashes then let go is a success of four "
              "switches", r["success"] and r["report"].get("switches") == 4,
              r["full_words"].replace("\n", "; "))
        r = play(s, dance(3, then=dict(lx=127)))
        check("dancing into a run is a failure", not r["success"] and
              not r["skip"] and "Ran" in r["full_words"],
              r["full_words"].replace("\n", "; "))
        check("and the longest dance is kept", r["report"].get("best") == 4,
              str(r["report"].get("best")))
        s = drill(game, "universal-dash-dance")              # rays on
        d = s.d
        r = None

        def toward(game_, frame):
            if d.target is None or frame < 20:
                s.set_player_pad()
                return
            me = game_.fighter(0)
            s.set_player_pad(lx=127 if d.target > me.pos[0] else -127)
            if frame > 20 + 200:
                s.set_player_pad()
        r = s.run(each_frame=toward)
        rays = d.rays(s.c)
        check("with targets on, a light ray is on the stage",
              len(rays) == 1 and -71 < rays[0][0] < 71, str(rays))
        check("and dashing to it reaches it, the next one coming down",
              d.reached >= 1, "%d reached; %s" % (
                  d.reached, r["full_words"].replace("\n", "; ")))

        # ---- Illusion levels ---------------------------------------------
        for level in (1, 2, 3, 4):
            s = drill(game, "fox-illusion-shorten", Level=level)
            # side-B on 0, B on the level's frame of the window (19 + k - 1
            # frames after)
            r = play(s, {0: dict(buttons=B, lx=127), 1: dict(),
                         18 + level: dict(buttons=B), 19 + level: dict()})
            check("Illusion level %d: B %d frames after side-B" % (
                level, 18 + level), r["success"] and
                r["report"].get("level") == level,
                r["full_words"].replace("\n", "; "))
        s = drill(game, "fox-illusion-shorten", Level=1)
        r = play(s, {0: dict(buttons=B, lx=127), 1: dict(),
                     21: dict(buttons=B), 22: dict()})
        check("level 1 asked, level 3 pressed: a failure, 2 late",
              not r["success"] and "2 late" in r["full_words"],
              r["full_words"].replace("\n", "; "))
        s = drill(game, "fox-illusion-shorten")                 # in turn
        got = []
        for level in (1, 2):
            r = play(s, {0: dict(buttons=B, lx=127), 1: dict(),
                         18 + level: dict(buttons=B), 19 + level: dict()},
                     start=60 if got else 20)
            got.append((r["success"], r["report"].get("level")))
        check("in turn: level 1, then level 2 is asked",
              got == [(True, 1), (True, 2)], str(got))
        check("the result carries a timeline",
              r.get("timeline") and r["timeline"]["rows"][1]["label"] == "B",
              str(r.get("timeline", {}).get("rows", "")[:1]))

        # ---- short hop double laser --------------------------------------
        s = drill(game, "fox-shdl")
        # "It also counts stuff off the ledge too! (i.e. jump from ledge
        # single laser)": a short hop and a laser, then (as if it drifted
        # off) on the ledge, a ledge jump and a laser back onto the stage:
        # not a pair. Then a real one.
        script = {0: dict(buttons=X), 1: dict(), 3: dict(buttons=B),
                  4: dict(), 40: dict(buttons=X), 41: dict(),
                  44: dict(buttons=B), 45: dict(),
                  100: dict(buttons=X), 101: dict(),
                  103: dict(buttons=B), 104: dict(),
                  110: dict(buttons=B), 111: dict()}
        hung = []

        def to_ledge(game_, frame):
            if frame == 20 + 15 and not hung:
                game_.ledge(0)
                hung.append(game_.fighter(0).state)
        s.d.v = {}
        first = s.run(each_frame=lambda g, f: (to_ledge(g, f),
                                               play_pad(s, script, f)))
        r = first
        check("short hop double laser: a laser from a ledge jump does not "
              "pair with the hop's; the next real one counts",
              hung and r["success"] and r["timeline"] is not None and
              r["frames"] > 100, "ledge state %s; %s after %d frames" % (
                  hung, r["full_words"].replace("\n", "; "), r["frames"]))

        # ---- JC grab and JC up smash -------------------------------------
        run_up = {0: dict(lx=127)}
        s = drill(game, "universal-jc-grab")
        r = play(s, {**run_up, **{14: dict(lx=127, buttons=X),
                                    15: dict(cy=127), 17: dict()}})
        check("JC grab: an up smash is not counted", r["skip"] and
              "not counted" in r["full_words"],
              r["full_words"].replace("\n", "; "))
        s = drill(game, "universal-jc-upsmash")
        r = play(s, {**run_up, **{14: dict(lx=127, buttons=X),
                                    15: dict(cy=127), 17: dict()}})
        check("JC up smash: up smash one frame after the jump",
              r["success"] and r["timeline"] is not None,
              r["full_words"].replace("\n", "; "))
        s = drill(game, "universal-jc-upsmash")
        r = play(s, {**run_up, **{14: dict(lx=127, buttons=X),
                                    15: dict(), 18: dict(cy=127),
                                    20: dict()}})
        check("JC up smash: the C-stick up after jump squat is too late",
              not r["success"] and not r["skip"],
              r["full_words"].replace("\n", "; "))
        s = drill(game, "universal-jc-upsmash")
        r = play(s, {**run_up, **{14: dict(lx=127, buttons=X | Z),
                                    15: dict()}})
        check("JC up smash: a grab is not counted", r["skip"],
              r["full_words"].replace("\n", "; "))

        # ---- ledgedash: starts, a refresh ---------------------------------
        s = drill(game, "universal-ledgedash")       # falling, by default
        plan = dict(step=0, at=0, hangs=0)
        CLIFF_WAIT = 253

        def ledge_play(game_, frame):
            f = game_.fighter(0)
            hanging = f.state == CLIFF_WAIT
            if plan["step"] == 0:                # falling onto the ledge
                if hanging:
                    plan.update(step=1, at=frame, hangs=plan["hangs"] + 1)
                s.set_player_pad()
            elif plan["step"] == 1:              # drop, up+B: a refresh
                k = frame - plan["at"]
                if k == 10:
                    s.set_player_pad(lx=-127)
                elif k == 11:
                    s.set_player_pad(ly=127, buttons=B)
                else:
                    s.set_player_pad()
                if k > 12 and hanging:
                    plan.update(step=2, at=frame, hangs=plan["hangs"] + 1)
            else:                                # drop, jump, air dodge
                k = frame - plan["at"] - 12
                if k == 0:
                    s.set_player_pad(lx=-127)
                elif k == 1:
                    s.set_player_pad(lx=127, buttons=X)
                elif k in (4, 5):
                    s.set_player_pad(lx=110, ly=-65, buttons=engine.R,
                                     trigger=140)
                else:
                    s.set_player_pad()
        r = s.run(each_frame=ledge_play)
        check("ledgedash: falling to the ledge, a refresh (drop and Firefox "
              "back), then the dash: a success, the refresh not a failure",
              r["success"] and plan["hangs"] == 2 and
              r["report"].get("refreshes") == 1,
              "%d grabs; %s" % (plan["hangs"],
                                r["full_words"].replace("\n", "; ")))
        tl = r.get("timeline") or {}
        rows = {row["label"]: row for row in tl.get("rows", [])}
        check("and its timeline shows the jump, the dodge and the "
              "intangible frames", rows.get("Jump", {}).get("you") and
              rows.get("Dodge", {}).get("you") and
              rows.get("Intang", {}).get("you"), str(
                  {k: v["you"] for k, v in rows.items()}))
        for start in (2, 3):
            s = drill(game, "universal-ledgedash", Start=start)
            seen = []

            def watch(game_, frame):
                seen.append(game_.fighter(0).state)
                s.set_player_pad()
                if frame > 80:
                    s.set_player_pad(buttons=engine.DDOWN)   # a reset
            s.dpad = True
            r = s.run(each_frame=watch)
            REBIRTH_WAIT, WAIT = 13, 14
            want = WAIT if start == 2 else REBIRTH_WAIT
            check("ledgedash start %s: the try starts there" % (
                ["", "", "on the stage", "on the respawn platform"][start]),
                seen[5:60].count(want) > 50, "states %s" % sorted(set(
                    seen[5:60])))

        # ---- aerial into shine: the shield held in place --------------------
        for hold, name in ((0, "held in place"), (1, "pushed back")):
            s = drill(game, "fox-shffl-nair-shine", Opponent=hold)
            r = s.run(demo=True)
            # the try ends as the shine starts; its hit on the shield comes
            # after: the opponent where it was put and 20 frames later
            xs = [round(game.fighter(1).pos[0], 1)]
            game.step(20)
            xs.append(round(game.fighter(1).pos[0], 1))
            # it was put 3.35 from the middle (fox_pressure.DISTANCE / 2)
            moved = abs(abs(xs[-1]) - 3.35)
            check("aerial into shine, the opponent %s: the aerial and the "
                  "shine moved it %.1f" % (name, moved),
                  (moved < 0.5) if hold == 0 else (moved > 3.0),
                  "x %s; %s" % (xs, r["full_words"].replace("\n", "; ")))
        check("and the result carries a timeline", r.get("timeline") and
              [row["label"] for row in r["timeline"]["rows"]] ==
              ["Press", "Land", "Shine"], str(r.get("timeline", {}).get(
                  "rows", "")))

        # ---- shield drop: platforms, starts, stages ------------------------
        from melee_course.drills.tech_ledge import SD_PLATFORMS, SD_DECK
        for stage in SD_PLATFORMS:
            for k, entry in enumerate(SD_DECK):
                side, how = entry.data
                s = engine.Session(registry.get("universal-shield-drop"),
                                   game, live=False, seed=7,
                                   common={engine.OPT_SCENARIO: k + 1})
                s.set_stage(stage)
                if how == 0:
                    r = s.run(demo=True)
                    if r.get("demo_marks") is not None and not r["success"]:
                        r = s.run(demo=True)
                    ok = r["success"]
                    detail = r["full_words"].replace("\n", "; ")
                else:
                    ys = []

                    def stand(game_, frame):
                        s.set_player_pad()
                        if frame == 60:
                            f = game_.fighter(0)
                            ys.append((round(f.pos[1], 1), f.airborne))
                            s.set_player_pad(buttons=engine.DDOWN)
                    s.dpad = True
                    s.run(each_frame=stand)
                    want = SD_PLATFORMS[stage][side][1] if how == 1 else 0.0
                    # Fountain of Dreams' side platforms move
                    tol = 12.0 if stage == "fountain-of-dreams" and \
                        side != "top" and how == 1 else 0.5
                    if how == 2:      # the floor below (Yoshi's slopes)
                        want, tol = 0.0, 2.0
                    ok = ys and not ys[0][1] and abs(ys[0][0] - want) < tol
                    detail = "at y %s, want %.1f" % (ys, want)
                check("shield drop on %s: %s" % (stage, entry.name.lower()),
                      ok, detail)

        # ---- waveshine: up to 5 frames late ------------------------------
        # each frame the air dodge is late lands it two frames late; a jump
        # a frame late, one. Jump on 4 (script 4: frame 5, a frame late),
        # dodge 2 frames after the first airborne frame: landed 5 late.
        for jump, late, ok in ((4, 5, True), (3, 6, False)):
            s = drill(game, "fox-waveshine")
            r = play(s, {0: dict(buttons=B, ly=-127), 1: dict(),
                         jump: dict(buttons=X), jump + 1: dict(),
                         9: dict(buttons=engine.R, lx=90, ly=-90,
                                 trigger=255), 11: dict()})
            check("waveshine landed %d frames late: %s" % (
                late, "success" if ok else "failure"),
                bool(r["success"]) == ok and r["measured"] == 7 + late and
                r.get("timeline"), r["full_words"].replace("\n", "; "))
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
