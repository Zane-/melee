"""Every course drill, by its id in data/courses/.

A drill in the drill format (data/drills/<id>.json, tools/melee_drills) is
played by melee_drills.drill.JsonDrill; a module in drills/ lists drills
written in Python in `DRILLS` (classes). This collects both, the format's
first. `get(id)` gives a fresh instance.
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
        from melee_drills import format as fmt
        from melee_drills.drill import JsonDrill
        for ident in fmt.ids():
            _drills[ident] = (lambda i: lambda: JsonDrill(fmt.load(i)))(
                ident)
    return _drills


def ids():
    return sorted(_load())


def has(drill_id):
    return drill_id in _load()


def get(drill_id):
    return _load()[drill_id]()
