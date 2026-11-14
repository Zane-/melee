"""A character's course as the client lists it, and what the player has
done in it.

The course is read from data/courses/<id>.md: each part's plan table (one
row per drill, in order). Which drills can be played in this client is a
separate matter: a drill plays here when it is written in the drill format
(data/drills/<drill id>.json, docs/ai/drill-format.md); the others are
listed and say so.

What the player has done (drills marked done, tries, the last drill) is
kept in save/client.json at the top of the repository, which git ignores.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTS = ("Tech", "Punish", "Defense", "Neutral")
SAVE = ROOT / "save" / "client.json"

# part: (what it trains, as the hub says it; the same in a few words, as the
# drill list's footer says it). Plain words: the owner, 2026-11-13, asked
# for "professional neutral language" and no taglines.
ABOUT = {
    "Tech": ("Individual techniques, graded frame by frame.",
             "Individual techniques."),
    "Punish": ("Conversions from a hit, a grab or a shielded move.",
               "Conversions."),
    "Defense": ("Escaping combos, pressure and edgeguards.",
                "Escapes: SDI, teching, recovery."),
    "Neutral": ("Winning the first hit from a neutral position.",
                "Openings."),
}


def _clean(cell):
    cell = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)
    return cell.replace("`", "").strip()


def load(cid):
    """{"id", "summary", "parts": {part: [drill, ...]}, "by_id"} or None.
    A drill: number, id, name, goal, cpu, requires, leads, part."""
    path = ROOT / "data" / "courses" / (cid + ".md")
    if not path.exists():
        return None
    text = path.read_text()
    front = text.split("---")[1] if text.startswith("---") else ""
    m = re.search(r"^summary:\s*(.+)$", front, re.M)
    course = dict(id=cid, summary=m.group(1).strip() if m else "", parts={},
                  by_id={})
    for part in PARTS:
        m = re.search(r"^## " + part + r"\s*$(.*?)(?=^## |\Z)", text,
                      re.M | re.S)
        drills = []
        for row in re.findall(r"^\| (\d+) \|(.*)\|\s*$", m.group(1) if m
                              else "", re.M):
            cells = [_clean(c) for c in row[1].split("|")]
            if len(cells) < 6:
                continue
            drill = dict(number=int(row[0]), id=cells[0], name=cells[1],
                         goal=cells[2], cpu=cells[3], requires=cells[4],
                         leads=cells[5], part=part)
            drills.append(drill)
            course["by_id"][drill["id"]] = drill
        course["parts"][part] = drills
    return course


def refer(course, drill, text):
    """A "Requires" or "Leads to" cell in words: numbers are drills of the
    same part, ids are drills anywhere in the course."""
    out = []
    for word in [w.strip() for w in text.split(",")]:
        if word in ("", "-"):
            continue
        if word.isdigit():
            same = [d for d in course["parts"][drill["part"]]
                    if d["number"] == int(word)]
            out.append("%s · %s" % (word, same[0]["name"]) if same else word)
        elif word in course["by_id"]:
            other = course["by_id"][word]
            out.append(other["name"] if other["part"] == drill["part"]
                       else "%s (%s)" % (other["name"], other["part"]))
        else:
            out.append(word)
    return out


#: In scenarios(): the drill runs on the course runtime (tools/melee_course).
COURSE = "course"


def scenarios():
    """{drill id: what plays it} for the drills that play in this client:
    the drills in the drill format (data/drills/, tools/melee_drills,
    docs/ai/drill-format.md), on the course runtime. (Scenario files in
    data/scenarios/ are the Melee Actor's, not drills.)"""
    from melee_course import registry
    return {d: COURSE for d in registry.ids()}


class Progress:
    """What the player has done: {"drills": {id: {"done", "tries", "yes",
    "best"}}, "last": {"character", "drill"}}."""

    def __init__(self, path=SAVE):
        self.path = Path(path)
        self.data = dict(drills={}, last=None)
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text()))
            except ValueError:
                pass

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=1) + "\n")

    def drill(self, ident):
        return self.data["drills"].setdefault(
            ident, dict(done=False, tries=0, yes=0, best=0))

    def done(self, ident):
        return bool(self.data["drills"].get(ident, {}).get("done"))

    def toggle(self, ident):
        d = self.drill(ident)
        d["done"] = not d["done"]
        self.save()
        return d["done"]

    def record(self, ident, character, results):
        """Add a visit's attempts (a list of True and False)."""
        d = self.drill(ident)
        d["tries"] += len(results)
        d["yes"] += sum(results)
        run = best = 0
        for ok in results:
            run = run + 1 if ok else 0
            best = max(best, run)
        d["best"] = max(d["best"], best)
        self.data["last"] = dict(character=character, drill=ident)
        self.save()


if __name__ == "__main__":
    c = load("fox")
    here = scenarios()
    for part in PARTS:
        print(part, len(c["parts"][part]), "drills;",
              sum(d["id"] in here for d in c["parts"][part]), "playable")
    d = c["by_id"]["fox-waveshine"]
    print(d["name"], "| builds on", refer(c, d, d["requires"]), "| leads to",
          refer(c, d, d["leads"]), "| cpu:", d["cpu"])
