"""Every ported course drill, by its id in data/courses/.

A module in drills/ lists its drills in `DRILLS` (classes); this collects
them. `get(id)` gives a fresh instance.
"""
import importlib
import os
import pkgutil

HERE = os.path.dirname(os.path.abspath(__file__))
_drills = None


def _load():
    global _drills
    if _drills is None:
        _drills = {}
        from melee_course import drills as pkg
        for mod in pkgutil.iter_modules(pkg.__path__):
            m = importlib.import_module("melee_course.drills." + mod.name)
            for cls in getattr(m, "DRILLS", ()):
                if cls.id in _drills:
                    raise ValueError("drill %s is in two modules" % cls.id)
                _drills[cls.id] = cls
    return _drills


def ids():
    return sorted(_load())


def has(drill_id):
    return drill_id in _load()


def get(drill_id):
    return _load()[drill_id]()
