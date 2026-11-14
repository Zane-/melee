"""Between two attempts of a drill, the D-pad and the pause menu work as in
an attempt, on a virtual display with keys pressed on it.

    python tests/client/between.py

Fox's shield pressure (Punish): after a result, in the frames left to read
it, D-pad up opens the guide, and a changed pause option ("Hits") takes
effect. Both once ended the client: what they ask for was raised outside
the attempt that handles it (the owner, 2026-11-13: D-pad up in the shield
drop drill, "Hits" in shield pressure).
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "melee_client"))
sys.path.insert(0, str(ROOT / "tools" / "melee_native"))

import client  # noqa: E402
import courses  # noqa: E402
import window  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""))



def waiting_for(drills):
    """The drills this test plays that are not back yet: the drills were
    wiped 2026-11-14 and are rebuilt one at a time in the drill format
    (docs/ai/drill-format.md); this test moves onto the first rebuilt ones
    it can use."""
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(
        __file__)), "..", "..", "tools"))
    from melee_course import registry
    return [d for d in drills if not registry.has(d)]

def main():
    missing = waiting_for(['fox-shield-pressure'])
    if missing:
        print("skip: plays %s, not rebuilt yet in the drill format"
              % ", ".join(missing))
        return 0
    w = window.Window(window=(1280, 720))
    state = dict(n=0)
    c = None

    def frames(n):
        for _ in range(n):
            c.frame()

    def tap(key, after=6):
        w.key(key)
        frames(2)
        w.key(key, False)
        frames(after)

    def first_result(game, frame=None):
        """D-pad up as soon as a result is shown, between attempts."""
        state["n"] += 1
        n = state["n"]
        if c.last_result is not None and "up" not in state and frame == -1:
            state["up"] = n
            game.key("t")
        if "up" in state and n == state["up"] + 3:
            game.key("t", False)
        if frame == -2 and "guide" not in state:
            state["guide"] = n
        if "guide" in state and n in (state["guide"] + 20,
                                      state["guide"] + 23):
            game.key("t", n == state["guide"] + 20)     # close the guide
        if "guide" in state and n > state["guide"] + 60:
            raise client.Leave("main")
        if n > 1200:
            raise client.Leave("main")

    def pause_hits(game, frame=None):
        """The pause menu between attempts: Hits one more, then resume."""
        state["n"] += 1
        n, s = state["n"], state.get("s", 0)
        if s == 0 and c.last_result is not None and frame == -1:
            game.key("Return")
            state["s"] = 1
        elif s == 1:
            game.key("Return", False)
            state["s"] = 2
        elif s == 2 and c.pause_open and n % 2 == 0:
            if "hits" not in state:
                names = [o.name for o in c.session.d.options]
                state["hits"] = names.index("Hits")
            if c.pause_focus == "opt%d" % state["hits"]:
                state["before"] = c.session.opts[state["hits"]]
                game.key("Right")
                state["s"] = 3
            else:
                game.key("Down")
        elif s == 2 and c.pause_open:
            game.key("Down", False)
        elif s == 3:
            game.key("Right", False)
            state["s"] = 4
        elif s == 4:
            game.key("z")
            state["s"] = 5
        elif s == 5:
            game.key("z", False)
            state["s"] = 6
            state["after"] = c.session.opts[state["hits"]]
            state["resumed"] = n
        elif s == 6 and n > state["resumed"] + 120:
            raise client.Leave("main")
        if n > 1500:
            raise client.Leave("main")

    try:
        w.step(30)
        save = os.path.join(tempfile.mkdtemp(prefix="melee-client-"),
                            "client.json")
        c = client.Client(w, source="keyboard", save=save,
                          out=tempfile.mkdtemp(prefix="melee-ui-"))
        w.pace(False)
        frames(6)

        def open_drill(ident):
            if c.screen == "main":
                tap("x")
                tap("x")
            for _ in range(4):
                if ident in [d["id"] for d in c.course["parts"][
                        courses.PARTS[int(c.hub_at[1:])]]]:
                    break
                tap("Right")
            tap("x")
            for _ in range(40):
                if c.drills()[c.row[c.part]]["id"] == ident:
                    break
                tap("Down")
            w.key("x")

        def start(person):
            """The A down: the drill runs inside the list's frame that
            sees it, which may be the next but one (the key reaches the
            window in its own time)."""
            c.person = person
            for _ in range(20):
                frames(1)
                if state.get("n"):
                    break

        open_drill("fox-shield-pressure")
        start(first_result)
        check("D-pad up between attempts opens the guide",
              "guide" in state, str(state))
        c.person = None
        w.key("x", False)
        frames(10)

        state.clear()
        state["n"] = 0
        open_drill("fox-shield-pressure")
        start(pause_hits)
        check("the pause menu between attempts changes Hits, and the drill "
              "goes on", state.get("after") is not None and
              state["after"] != state.get("before") and
              state["n"] > state.get("resumed", 1 << 30) + 100,
              "%s -> %s" % (state.get("before"), state.get("after")))
    finally:
        w.close()
    print("%d of %d checks passed" % (sum(checks), len(checks)))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
