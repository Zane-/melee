"""The roster as the client shows it.

Names and traits come from the knowledge base (data/characters/<id>.md:
the first three archetype words, weight, fall speed, frames of jump squat).
Whether a character has a course of its own, and how many drills each part
of it has, comes from data/courses/<id>.md. The colour each character wears
is the client's own choice; the pictures are the game's (art.py).

Zelda and Sheik share one place, as on the game's own select screen: Sheik
first (the owner, 2026-11-13: "this should be default"), Zelda one button
away. Each is a character of its own here; the place holds Sheik, and
`other` is the one it becomes.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# id: (short name for a small panel, colour, text colour on it, the series
# whose emblem it wears, how far its portrait is moved up in a small panel
# so the face shows: pixels of the 136x188 picture)
LOOK = {
    "bowser": (None, "#F2A007", "#12161C", "mushroom", 8),
    "captain-falcon": ("C. Falcon", "#3D4FA8", "#FFFFFF", "f-zero", 0),
    "donkey-kong": ("DK", "#8A5A2B", "#FFFFFF", "donkey-kong", 22),
    "dr-mario": (None, "#FFFFFF", "#12161C", "mushroom", 4),
    "falco": (None, "#2F6FD0", "#FFFFFF", "star-fox", 0),
    "fox": (None, "#E08A2E", "#12161C", "star-fox", 4),
    "ganondorf": (None, "#5A2A3C", "#FFFFFF", "zelda", 0),
    "ice-climbers": (None, "#7FB6F2", "#12161C", "ice-climber", 20),
    "jigglypuff": (None, "#F9C4D8", "#12161C", "pokemon", 34),
    "kirby": (None, "#F06C9B", "#12161C", "kirby", 30),
    "link": (None, "#3F9A4A", "#12161C", "zelda", 4),
    "luigi": (None, "#2FA84F", "#12161C", "mushroom", 6),
    "mario": (None, "#E23B2E", "#FFFFFF", "mushroom", 6),
    "marth": (None, "#2B3F8C", "#FFFFFF", "fire-emblem", 0),
    "mewtwo": (None, "#B9A7D6", "#12161C", "pokemon", 0),
    # an LCD screen: his portrait is a black silhouette, lost on ink
    "mr-game-and-watch": ("Game & Watch", "#C6CCB2", "#12161C",
                          "game-and-watch", 6),
    "ness": (None, "#C8324A", "#FFFFFF", "earthbound", 8),
    "peach": (None, "#F7A8C0", "#12161C", "mushroom", 6),
    "pichu": (None, "#F7E26B", "#12161C", "pokemon", 14),
    "pikachu": (None, "#F5C518", "#12161C", "pokemon", 6),
    "roy": (None, "#B5262B", "#FFFFFF", "fire-emblem", 0),
    "samus": (None, "#D9442A", "#FFFFFF", "metroid", 0),
    "sheik": (None, "#4B5DB8", "#FFFFFF", "zelda", 0),
    "yoshi": (None, "#5BBE3A", "#12161C", "yoshi", 4),
    "young-link": (None, "#8FCB6B", "#12161C", "zelda", 0),
    "zelda": (None, "#C9A3E0", "#12161C", "zelda", 0),
}
# how many costumes each has in the game
COSTUMES = {
    "captain-falcon": 6, "kirby": 6, "yoshi": 6, "fox": 4, "falco": 4,
    "bowser": 4, "luigi": 4, "mewtwo": 4, "mr-game-and-watch": 4, "ness": 4,
    "pikachu": 4, "pichu": 4, "ice-climbers": 4,
}
SHARED = ("sheik", "zelda")     # one place: the first, then the other
PARTS = ("Tech", "Punish", "Defense", "Neutral")


def _front(path):
    text = path.read_text()
    return text.split("---")[1] if text.startswith("---") else ""


def _field(front, key):
    m = re.search(r"^\s*" + key + r":\s*(.+)$", front, re.M)
    return m.group(1).strip().strip('"') if m else ""


def _course(cid):
    """(summary, {part: number of drills}) or None."""
    path = ROOT / "data" / "courses" / (cid + ".md")
    if not path.exists():
        return None
    text = path.read_text()
    counts = {}
    for part in PARTS:
        m = re.search(r"^## " + part + r"\s*$(.*?)(?=^## |\Z)", text,
                      re.M | re.S)
        counts[part] = len(re.findall(r"^\| \d+ \|", m.group(1), re.M)) \
            if m else 0
    return _field(_front(path), "summary"), counts


def character(cid):
    """One character, as the roster has it (no `other`)."""
    short, color, fg, series, face = LOOK[cid]
    front = _front(ROOT / "data" / "characters" / (cid + ".md"))
    name = _field(front, "name") or cid
    words = re.findall(r"[\w-]+", _field(front, "archetype"))[:3]
    return dict(
        id=cid, name=name, short=short or name, color=color, fg=fg,
        series=series, face=face, costumes=COSTUMES.get(cid, 5),
        tags=[w.replace("-", " ") for w in words],
        weight=_field(front, "weight"), fall=_field(front, "fall_speed"),
        squat=_field(front, "jump_squat"), course=_course(cid))


def roster():
    """Every place on the select screen, in the order of their names:
    Zelda's is Sheik's, with Zelda as its `other`."""
    out, by = [], {}
    for cid in LOOK:
        by[cid] = character(cid)
    first, second = (by[c] for c in SHARED)
    first["other"], second["other"] = second, first
    out = [c for c in by.values() if c["id"] != SHARED[1]]
    out.sort(key=lambda c: c["name"])
    return out


def find(roster_, cid):
    """(place, character) of `cid`, which may be a place's other form."""
    for i, c in enumerate(roster_):
        if c["id"] == cid:
            return i, c
        if c.get("other") is not None and c["other"]["id"] == cid:
            return i, c["other"]
    raise KeyError(cid)


if __name__ == "__main__":
    for c in roster():
        print("%-18s %-34s w%-4s f%-5s j%s %s %s" % (
            c["name"], " · ".join(c["tags"]), c["weight"], c["fall"],
            c["squat"], c["course"][1] if c["course"] else "",
            "/ " + c["other"]["name"] if c.get("other") else ""))
