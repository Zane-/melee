"""The roster as the client shows it.

Names and traits come from the knowledge base (data/characters/<id>.md:
the first three archetype words, weight, fall speed, frames of jump squat).
Whether a character has a course of its own, and how many drills each part
of it has, comes from data/courses/<id>.md. The colour each character wears
and its two letters are the client's own choice; no art of the game is used.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# id: (two letters, short name for a small panel, colour, text colour on it)
LOOK = {
    "bowser": ("Bw", None, "#F2A007", "#12161C"),
    "captain-falcon": ("CF", "C. Falcon", "#3D4FA8", "#FFFFFF"),
    "donkey-kong": ("DK", None, "#8A5A2B", "#FFFFFF"),
    "dr-mario": ("DM", None, "#FFFFFF", "#12161C"),
    "falco": ("Fa", None, "#2F6FD0", "#FFFFFF"),
    "fox": ("Fx", None, "#E08A2E", "#12161C"),
    "ganondorf": ("Gn", None, "#5A2A3C", "#FFFFFF"),
    "ice-climbers": ("IC", None, "#7FB6F2", "#12161C"),
    "jigglypuff": ("Jp", None, "#F9C4D8", "#12161C"),
    "kirby": ("Kb", None, "#F06C9B", "#12161C"),
    "link": ("Lk", None, "#3F9A4A", "#12161C"),
    "luigi": ("Lg", None, "#2FA84F", "#12161C"),
    "mario": ("Mr", None, "#E23B2E", "#FFFFFF"),
    "marth": ("Mt", None, "#2B3F8C", "#FFFFFF"),
    "mewtwo": ("M2", None, "#B9A7D6", "#12161C"),
    "mr-game-and-watch": ("GW", "Game & Watch", "#12161C", "#FFFFFF"),
    "ness": ("Ns", None, "#C8324A", "#FFFFFF"),
    "peach": ("Pe", None, "#F7A8C0", "#12161C"),
    "pichu": ("Pc", None, "#F7E26B", "#12161C"),
    "pikachu": ("Pk", None, "#F5C518", "#12161C"),
    "roy": ("Ry", None, "#B5262B", "#FFFFFF"),
    "samus": ("Sm", None, "#D9442A", "#FFFFFF"),
    "sheik": ("Sh", None, "#4B5DB8", "#FFFFFF"),
    "yoshi": ("Ys", None, "#5BBE3A", "#12161C"),
    "young-link": ("YL", None, "#8FCB6B", "#12161C"),
    "zelda": ("Zd", None, "#C9A3E0", "#12161C"),
}
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


def roster():
    """Every character, in the order of their names."""
    out = []
    for cid, (mono, short, color, fg) in LOOK.items():
        front = _front(ROOT / "data" / "characters" / (cid + ".md"))
        name = _field(front, "name") or cid
        words = re.findall(r"[\w-]+", _field(front, "archetype"))[:3]
        out.append(dict(
            id=cid, name=name, short=short or name, mono=mono, color=color,
            fg=fg, tags=[w.replace("-", " ") for w in words],
            weight=_field(front, "weight"), fall=_field(front, "fall_speed"),
            squat=_field(front, "jump_squat"), course=_course(cid)))
    out.sort(key=lambda c: c["name"])
    return out


if __name__ == "__main__":
    for c in roster():
        print("%-18s %-34s w%-4s f%-5s j%s %s" % (
            c["name"], " · ".join(c["tags"]), c["weight"], c["fall"],
            c["squat"], c["course"][1] if c["course"] else ""))
