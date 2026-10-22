"""The intermediate record: every step between the grid's files and the final tables, written
by run_analysis.py into OUT/intermediate/ (DESIGN.md section 12).

The analysis functions call add() and series() as they compute. Outside a recording() block
both do nothing, so the power simulation and the tests that do not ask for a record pay nothing.

    rec = Recorder()
    with recording(rec):
        ... the analysis ...
    rec.tables["holm"]           a list of dicts, one per row
    rec.series["bootstrap"]      {test id: numpy array of the replicates}
"""
import contextlib
from collections import defaultdict

import numpy as np

_current = None


class Recorder:
    def __init__(self):
        self.tables = defaultdict(list)
        self.series = defaultdict(dict)


def active():
    return _current is not None


def add(table, row):
    if _current is not None:
        _current.tables[table].append(row)


def series(name, key, values):
    if _current is not None:
        _current.series[name][key] = np.array(values, dtype=float, copy=True)


@contextlib.contextmanager
def recording(rec):
    global _current
    previous = _current
    _current = rec
    try:
        yield rec
    finally:
        _current = previous
