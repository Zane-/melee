"""The input display as a GameCube controller of SmashWiki's icons (the
owner, 2026-11-14: "use the official button icons so it looks more like an
actual gamecube controller"), in the match and on the coach's cards.
Checked on a virtual display:

    python tests/client/input_display.py [--shots DIR]

- every part of the controller has its picture (buttons.ensure made them);
- over a match, the game fills it in each frame (src/host/inputs.c,
  ui.cpp's host_ui_pad): a button held is lit and let go is not, the
  sticks' caps move the way the sticks are pushed, a trigger goes in as far
  as it is pressed; one controller for one port, two for two, none when
  the display is off;
- the coach's card's display takes a pad the same way (Play._pad, the same
  sums: screens.pad_lines).
"""
import argparse
import json
import os
import re
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_native"))
sys.path.insert(0, os.path.join(ROOT, "tools", "melee_client"))

import buttons  # noqa: E402
import client  # noqa: E402
import screens  # noqa: E402
import window  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name,
                        "  (" + detail + ")" if detail else ""), flush=True)


def look(w, ident):
    return json.loads(w._cmd("ui look " + ident))


def pct(text):
    """"31.5%" -> 31.5 (None if not set)."""
    m = re.match(r"(-?[\d.]+)%", text or "")
    return float(m.group(1)) if m else None


def _same(card, s, lt):
    """The card's lines against the game's looks, as numbers (RmlUi reads
    a share back to the whole hundredth: within 0.6 of one; an opacity
    within 0.02)."""
    nums = [float(x) for line in card for x in re.findall(r"[\d.]+", line)]
    game = [pct(s["left"]), pct(s["top"]), pct(lt["top"]),
            float(lt["opacity"])]
    return len(nums) == 4 and all(
        abs(a - b) <= (0.6 if i < 3 else 0.02)
        for i, (a, b) in enumerate(zip(nums, game)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--shots", help="directory for pictures")
    args = ap.parse_args()
    if args.shots:
        os.makedirs(args.shots, exist_ok=True)

    screens.BUTTONS.update(buttons.ensure())
    missing = [n for n in buttons.PAD if n not in screens.BUTTONS]
    check("every part of the controller has its picture", not missing,
          ", ".join(missing))
    html = screens.pad_display("y")
    srcs = re.findall(r'src="file://([^"]+)"', html)
    check("the card's controller is made of them",
          len(srcs) >= 18 and all(os.path.exists(s) for s in srcs) and
          "pvx" not in html, "%d pictures" % len(srcs))

    # the card's sums, as Play._pad gives them
    lines = dict(screens.pad_lines("y", 0x800 | 0x8, (1.0, 0.0), (0.0, -1.0),
                                   0.5, 1.0))
    check("the card's display: Y and D-pad up lit, B not",
          lines["Y"].endswith("on 1") and lines["DU"].endswith("on 1") and
          lines["B"].endswith("on 0"))
    check("the card's display: the stick right, the C-stick down, L half in",
          "left: 41.0%; top: 21.0%" in lines["S"] and
          "left: 21.0%; top: 41.0%" in lines["C"] and
          "top: 8.0%; opacity: 0.68" in lines["L"], lines["S"])

    out = tempfile.mkdtemp(prefix="melee-ui-")
    w = None
    try:
        w = window.Window(window=(1280, 720))
        w.step(10)
        with open(os.path.join(out, "style.rcss"), "w") as f:
            f.write(screens.STYLE.read_text())
        doc = os.path.join(out, "match.rml")
        with open(doc, "w") as f:
            f.write(screens.page("Match", screens.over_game(), paper=False))
        w.ui("load " + doc)
        w.start("fox", "marth")
        w.step(30)
        w.inputs(1)
        w.step(3)
        check("display on for port 1: one controller, at the corner",
              "on" in look(w, "gp0")["class"].split() and
              "on" not in look(w, "gp1")["class"].split())

        # L a quarter of the pad's range: 63 of the 140 the game counts as
        # all the way in (gmmain.c's scale_analogLR)
        w.pad(0, buttons=("A", "Z"), stick=(1.0, 0.0), cstick=(0.0, 1.0),
              l=0.25)
        w.step(3)
        a, b, z = (look(w, "cg0i" + p) for p in ("A", "B", "Z"))
        s, c, lt = (look(w, "cg0i" + p) for p in ("S", "C", "L"))
        check("A and Z held: lit; B not",
              "on" in a["class"].split() and "on" in z["class"].split() and
              "on" not in b["class"].split(),
              "%s / %s / %s" % (a["class"], z["class"], b["class"]))
        check("the stick pushed right: its cap at the gate's right",
              pct(s["left"]) is not None and pct(s["left"]) > 35 and
              abs(pct(s["top"]) - 21) < 3, "%s %s" % (s["left"], s["top"]))
        check("the C-stick pushed up: its cap at the top",
              pct(c["top"]) is not None and pct(c["top"]) < 7,
              "%s %s" % (c["left"], c["top"]))
        check("L under half in: moved in a little, half lit",
              pct(lt["top"]) is not None and 5 < pct(lt["top"]) < 9 and
              0.55 < float(lt["opacity"]) < 0.75,
              "%s, opacity %s" % (lt["top"], lt["opacity"]))

        # the coach's card, given the same pad recorded, shows the same
        class Lines:
            def __init__(self):
                self.lines = []

            def ui(self, line):
                self.lines.append(line)
        rec = Lines()
        client.Play(rec, [])._pad("y", {"buttons": 0x100 | 0x10, "lx": 80,
                                        "cy": 80, "lt": 63})
        card = [x for x in rec.lines if x.startswith(("attr cyiS ",
                                                      "attr cyiL "))]
        check("the card shows that pad as the game does",
              _same(card, s, lt), "; ".join(card) + " / game %s %s %s %s" % (
                  s["left"], s["top"], lt["top"], lt["opacity"]))
        if args.shots:
            w.shot(os.path.join(args.shots, "held.png"))

        w.pad(0)
        w.step(3)
        a, s, lt = (look(w, "cg0i" + p) for p in ("A", "S", "L"))
        check("let go: A dark, the cap back in the middle, L out",
              "on" not in a["class"].split() and
              abs(pct(s["left"]) - 21) < 1 and pct(lt["top"]) == 0,
              "%s %s %s" % (a["class"], s["left"], lt["top"]))

        w.inputs(3)
        w.step(3)
        check("both ports: two controllers",
              "on" in look(w, "gp0")["class"].split() and
              "on" in look(w, "gp1")["class"].split())
        if args.shots:
            w.shot(os.path.join(args.shots, "both.png"))
        w.inputs(0)
        w.step(3)
        check("display off: none",
              "on" not in look(w, "gp0")["class"].split() and
              "on" not in look(w, "gp1")["class"].split())
    finally:
        if w is not None:
            w.close()

    print("%d of %d checks passed" % (sum(checks), len(checks)))
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
