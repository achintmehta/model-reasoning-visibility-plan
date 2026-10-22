#!/usr/bin/env python3
"""blind_tools.py — the blind ids the grader works from: calibration copies, the re-grade
draw, and the grader's lists. Run by whoever makes the lists, not by the grader (protocol
§5.3): it reads and writes the un-blinding state.

    blind_tools.py calibrate --state DIR --to ROOT [--round NAME] RUN_DIR [RUN_DIR ...]
    blind_tools.py sample    --state DIR --seed SEED --draw NAME --per-cell N [--models M,M]
    blind_tools.py extend    --state DIR --draw NAME --to N
    blind_tools.py draw      --state DIR --seed SEED --draw NAME (--per-cell N | --all)
                             [--models M,M] [--task T]
    blind_tools.py fresh     --state DIR --seed SEED --draw NAME --task T --results DIR
                             [--n 24] [--today DATE]
    blind_tools.py lists     --state DIR --results DIR (--models M,M | --calibration ROUND)
                             [--today DATE] [--seed SEED]

The state folder (`blind-state/`, kept off the runs tree and away from the grader):
  blind-ids.txt          the harness's ledger of every id ever drawn; every id made here is
                         appended to it first, so no id is ever used twice
  blind-key.jsonl        the harness's un-blinding key, one line per grid run (read only)
  calibration-key.jsonl  one line per calibration copy: its id, task and source run
  quality-sample.jsonl   one line per grid app: its cell and its place in the cell's random
                         grading order, {"blind_id", "draw", "rank", ...}
  sample-levels.jsonl    how many of each cell's order are graded, per draw: {"draw", "level", ...}
  regrade-key.jsonl      one line per second id: {"blind_id": second, "regrade_of": first, ...}
  grading-index.tsv      "<id><TAB><run folder>" for every id that is not a folder name
                         (re-grade ids): give it to grade_setup.sh as GRADING_INDEX
  lists/list-NNN.txt     every list handed out, one blind id per line

calibrate  Copies each run's app/ (without node_modules and .git) and its environment.txt
           to ROOT/<task>/runs/<fresh id>/, the blind layout grade_setup.sh reads, because
           the smoke folders' own ids and paths name the arm. Nothing else of the run is copied.
sample     The seeded quality sample (protocol §5.3): the apps of every model x task x condition
           x arm cell are put in a random order, and the first N of every cell are graded. Made
           once per tier, before its first list. Only sampled apps go on the grid's lists, and the
           re-grade draw picks from them.
extend     Grades more of a tier if time allows: raises the level of a sample draw to N, so the
           next apps in every cell's order are graded too, the same number in every cell. Decided
           by the time left, never by results.
draw       The seeded re-grade draw: N apps of every model x task x condition x arm cell (or
           every app, for the deciding round), each given a second id. An app drawn before is
           never drawn again.
fresh      After a check below the bar: at least N apps of the task, spread evenly over its
           cells, from those first graded at least 14 days earlier and not yet re-graded.
lists      The next list: the first gradings still to do, plus every second id whose first
           grading is at least 14 days old, shuffled together, with nothing that says which is
           which. Ids on an earlier list are never listed again.

Stdlib only.
"""
import argparse
import collections
import datetime
import glob
import json
import os
import random
import re
import shutil
import sys

COOL_DOWN_DAYS = 14
ID_DIGITS = 6
SMOKE_RE = re.compile(r"(?P<model>[^/]+)/(?P<task>kanban-board|message-board)/(?P<condition>[^/]+)/runs/(?P<cid>\d+)/?$")
ARM_OF_DIGIT = {"1": "off", "2": "unseen", "3": "seen"}


# ----------------------------------------------------------------------------- state

class State:
    def __init__(self, path):
        self.dir = path
        os.makedirs(path, exist_ok=True)
        self.ledger = os.path.join(path, "blind-ids.txt")
        self.key = os.path.join(path, "blind-key.jsonl")
        self.cal = os.path.join(path, "calibration-key.jsonl")
        self.regrade = os.path.join(path, "regrade-key.jsonl")
        self.sample = os.path.join(path, "quality-sample.jsonl")
        self.levels = os.path.join(path, "sample-levels.jsonl")
        self.index = os.path.join(path, "grading-index.tsv")
        self.lists = os.path.join(path, "lists")

    @staticmethod
    def jsonl(path):
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]

    def used_ids(self):
        ids = set()
        if os.path.exists(self.ledger):
            with open(self.ledger, encoding="utf-8") as f:
                ids |= {x.split()[0] for x in f if x.strip()}
        for p in (self.key, self.cal, self.regrade):
            ids |= {r["blind_id"] for r in self.jsonl(p)}
        return ids

    def new_id(self, rng):
        used = self.used_ids()
        for _ in range(10000):
            i = str(rng.randrange(10 ** (ID_DIGITS - 1), 10 ** ID_DIGITS))
            if i not in used:
                with open(self.ledger, "a", encoding="utf-8") as f:   # burned before use
                    f.write(i + "\n")
                return i
        sys.exit("could not find a free id")

    def append(self, path, rec):
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

    def apps(self):
        """Every first-grading app: {id: {task, model, condition, arm, run, source}}."""
        out = {}
        for r in self.jsonl(self.key):
            out[r["blind_id"]] = {"task": r["task"], "model": r.get("model_key"),
                                  "condition": r.get("condition"), "arm": r.get("arm"),
                                  "run": r.get("run_base"), "round": None}
        for r in self.jsonl(self.cal):
            out[r["blind_id"]] = {"task": r["task"], "model": r.get("model"),
                                  "condition": r.get("condition"), "arm": r.get("arm"),
                                  "run": r["copy"], "round": r.get("round")}
        return out


def today(arg):
    return datetime.date.fromisoformat(arg) if arg else datetime.date.today()


def graded_on(results):
    """{blind id: date of its grading}, from the score sheets in the results folder."""
    out = {}
    for p in glob.glob(os.path.join(results, "*.score.json")):
        try:
            with open(p, encoding="utf-8") as f:
                s = json.load(f)
            out[s["blind_id"]] = datetime.date.fromisoformat(s["graded_on"])
        except (OSError, ValueError, KeyError):
            continue
    return out


def cell(app):
    return (app["model"], app["task"], app["condition"], app["arm"])


# ----------------------------------------------------------------------------- commands

def cmd_calibrate(a, st):
    rng = random.SystemRandom()
    made = 0
    for src in a.runs:
        src = os.path.abspath(src.rstrip("/"))
        envs = [p for p in glob.glob(os.path.join(src, "*", "logs", "environment.txt"))
                if not p.startswith(os.path.join(src, "app") + os.sep)]
        if not os.path.isdir(os.path.join(src, "app")) or len(envs) != 1:
            sys.exit(f"not a run folder (app/ and one */logs/environment.txt): {src}")
        m = SMOKE_RE.search(src)
        if not m:
            sys.exit(f"cannot tell the task from the path: {src}")
        info = m.groupdict()
        bid = st.new_id(rng)
        dest = os.path.join(a.to, info["task"], "runs", bid)
        shutil.copytree(os.path.join(src, "app"), os.path.join(dest, "app"), symlinks=True,
                        ignore=shutil.ignore_patterns("node_modules", ".git"))
        os.makedirs(os.path.join(dest, "smoke", "logs"))
        shutil.copy2(envs[0], os.path.join(dest, "smoke", "logs", "environment.txt"))
        st.append(st.cal, {"blind_id": bid, "task": info["task"], "model": info["model"],
                           "condition": info["condition"],
                           "arm": ARM_OF_DIGIT.get(info["cid"][0]), "source": src,
                           "copy": os.path.abspath(dest), "round": a.round,
                           "made_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
        made += 1
    print(f"{made} calibration copies under {a.to} (round {a.round}); key: {st.cal}")


def give_second_ids(st, firsts, apps, seed, draw, rng):
    for first in firsts:
        second = st.new_id(rng)
        st.append(st.regrade, {"blind_id": second, "regrade_of": first, "draw": draw, "seed": seed,
                               "drawn_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
        with open(st.index, "a", encoding="utf-8") as f:
            f.write(f"{second}\t{apps[first]['run']}\n")
    print(f"draw {draw}: {len(firsts)} apps get a second id; key: {st.regrade}; index: {st.index}")


def levels(st):
    """{draw: how many of each cell's order are graded}: the last level recorded for each draw."""
    out = {}
    for r in st.jsonl(st.levels):
        out[r["draw"]] = r["level"]
    return out


def sampled(st):
    """The grid apps to be graded: those within their draw's level in their cell's order."""
    lv = levels(st)
    return {r["blind_id"] for r in st.jsonl(st.sample) if r["rank"] <= lv.get(r["draw"], 0)}


def in_any_sample(st):
    return {r["blind_id"] for r in st.jsonl(st.sample)}


def eligible(st, a):
    apps = st.apps()
    drawn = {r["regrade_of"] for r in st.jsonl(st.regrade)}
    sample = sampled(st)
    models = set(a.models.split(",")) if getattr(a, "models", None) else None
    # A grid app can be re-graded only if it is in the quality sample; calibration apps always.
    return apps, {i: x for i, x in apps.items() if i not in drawn
                  and (x["round"] is not None or i in sample)
                  and (models is None or x["model"] in models)
                  and (not a.task or x["task"] == a.task)}


def cmd_sample(a, st):
    apps = st.apps()
    done = in_any_sample(st)
    if a.draw in levels(st):
        sys.exit(f"draw {a.draw} exists already; to grade more of it, use `extend`")
    models = set(a.models.split(",")) if a.models else None
    pool = {i: x for i, x in apps.items() if x["round"] is None
            and (models is None or x["model"] in models)}
    by_cell = collections.defaultdict(list)
    for i in sorted(pool):
        by_cell[cell(pool[i])].append(i)
    rng = random.Random(f"{a.seed}:{a.draw}:sample")
    when = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    ordered, cells = 0, 0
    for c in sorted(by_cell, key=lambda c: tuple(str(x) for x in c)):
        ids = by_cell[c]
        if any(i in done for i in ids):
            print(f"note: cell {c} already has a grading order; left as it is")
            continue
        if len(ids) < a.per_cell:
            print(f"note: cell {c} has {len(ids)} apps, fewer than {a.per_cell}: all of them are graded")
        order = ids[:]
        rng.shuffle(order)                       # the cell's grading order
        for rank, i in enumerate(order, 1):
            st.append(st.sample, {"blind_id": i, "draw": a.draw, "seed": a.seed, "rank": rank,
                                  "cell": list(c), "drawn_at": when})
        ordered += len(order); cells += 1
    st.append(st.levels, {"draw": a.draw, "level": a.per_cell, "set_at": when})
    print(f"sample {a.draw}: {ordered} apps in {cells} cells put in a random grading order; the first "
          f"{a.per_cell} of every cell are graded ({len(sampled(st))} apps in all samples); key: {st.sample}")


def cmd_extend(a, st):
    lv = levels(st)
    if a.draw not in lv:
        sys.exit(f"no sample draw named {a.draw}")
    if a.to <= lv[a.draw]:
        sys.exit(f"draw {a.draw} already grades the first {lv[a.draw]} of every cell; --to must be larger")
    before = sampled(st)
    st.append(st.levels, {"draw": a.draw, "level": a.to,
                          "set_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
    added = sampled(st) - before
    print(f"sample {a.draw}: now the first {a.to} of every cell are graded; {len(added)} more apps "
          f"(the next on the lists). Decide this by time left, never by results.")


def cmd_draw(a, st):
    apps, pool = eligible(st, a)
    rng = random.Random(f"{a.seed}:{a.draw}")
    by_cell = collections.defaultdict(list)
    for i in sorted(pool):
        by_cell[cell(pool[i])].append(i)
    picked = []
    for c in sorted(by_cell, key=lambda c: tuple(str(x) for x in c)):
        ids = by_cell[c]
        picked += ids if a.all else rng.sample(ids, min(a.per_cell, len(ids)))
        if not a.all and len(ids) < a.per_cell:
            print(f"note: cell {c} has {len(ids)} apps, fewer than {a.per_cell}")
    give_second_ids(st, sorted(picked), apps, a.seed, a.draw, random.SystemRandom())


def cmd_fresh(a, st):
    apps, pool = eligible(st, a)
    graded = graded_on(a.results)
    cutoff = today(a.today) - datetime.timedelta(days=COOL_DOWN_DAYS)
    pool = {i: x for i, x in pool.items() if i in graded and graded[i] <= cutoff}
    rng = random.Random(f"{a.seed}:{a.draw}")
    by_cell = collections.defaultdict(list)
    for i in sorted(pool):
        by_cell[cell(pool[i])].append(i)
    for ids in by_cell.values():
        rng.shuffle(ids)
    picked, cells = [], sorted(by_cell, key=lambda c: tuple(str(x) for x in c))
    while len(picked) < a.n and any(by_cell[c] for c in cells):   # round robin: spread evenly
        for c in cells:
            if by_cell[c] and len(picked) < a.n:
                picked.append(by_cell[c].pop())
    if len(picked) < a.n:
        print(f"only {len(picked)} apps of {a.task} are eligible, fewer than {a.n}: "
              f"log and report this as a deviation (README, 'A task whose check is below the bar')")
    give_second_ids(st, sorted(picked), apps, a.seed, a.draw, random.SystemRandom())


def cmd_lists(a, st):
    apps = st.apps()
    if a.calibration:
        firsts = {i for i, x in apps.items() if x["round"] == a.calibration}
    else:
        models = set(a.models.split(","))
        grid = {i: x for i, x in apps.items() if x["round"] is None and x["model"] in models}
        sample = sampled(st)
        # Every cell must have its sample before any of its apps is listed (protocol §5.3).
        unsampled = sorted({cell(x) for i, x in grid.items()}
                           - {cell(x) for i, x in grid.items() if i in sample}, key=str)
        if unsampled:
            sys.exit(f"{len(unsampled)} cells have no quality sample yet, for example {unsampled[0]}: "
                     f"run `blind_tools.py sample` for these models first")
        firsts = {i for i in grid if i in sample}
    graded = graded_on(a.results)
    os.makedirs(st.lists, exist_ok=True)
    listed = set()
    old = sorted(glob.glob(os.path.join(st.lists, "list-*.txt")))
    for p in old:
        with open(p, encoding="utf-8") as f:
            listed |= {x.strip() for x in f if x.strip()}
    cutoff = today(a.today) - datetime.timedelta(days=COOL_DOWN_DAYS)
    first_todo = [i for i in firsts if i not in graded and i not in listed]
    seconds = [r["blind_id"] for r in st.jsonl(st.regrade)
               if r["regrade_of"] in graded and graded[r["regrade_of"]] <= cutoff
               and r["blind_id"] not in graded and r["blind_id"] not in listed]
    ids = sorted(first_todo + seconds)
    if not ids:
        print("nothing to list yet")
        return
    n = len(old) + 1
    rng = random.Random(f"{a.seed}:list-{n}") if a.seed else random.SystemRandom()
    rng.shuffle(ids)
    path = os.path.join(st.lists, f"list-{n:03d}.txt")
    with open(path, "x", encoding="utf-8") as f:
        f.write("\n".join(ids) + "\n")
    waiting = sum(1 for r in st.jsonl(st.regrade) if r["blind_id"] not in graded and r["blind_id"] not in listed
                  and r["blind_id"] not in seconds)
    print(f"{path}: {len(ids)} ids. Give the grader this file only.")
    print(f"(for you: {len(first_todo)} first gradings, {len(seconds)} re-grades; "
          f"{waiting} re-grades still waiting for their first grading or its 14 days)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("calibrate")
    c.add_argument("runs", nargs="+")
    c.add_argument("--to", required=True)
    c.add_argument("--round", default="deciding")
    sm = sub.add_parser("sample")
    sm.add_argument("--seed", required=True)
    sm.add_argument("--draw", required=True, help="a name for this sample, e.g. tier1")
    sm.add_argument("--per-cell", type=int, default=10)
    sm.add_argument("--models")
    ex = sub.add_parser("extend")
    ex.add_argument("--draw", required=True)
    ex.add_argument("--to", type=int, required=True)
    d = sub.add_parser("draw")
    d.add_argument("--seed", required=True)
    d.add_argument("--draw", required=True, help="a name for this draw, e.g. tier1")
    g = d.add_mutually_exclusive_group(required=True)
    g.add_argument("--per-cell", type=int)
    g.add_argument("--all", action="store_true")
    d.add_argument("--models")
    d.add_argument("--task")
    f = sub.add_parser("fresh")
    f.add_argument("--seed", required=True)
    f.add_argument("--draw", required=True)
    f.add_argument("--task", required=True)
    f.add_argument("--results", required=True)
    f.add_argument("--n", type=int, default=24)
    f.add_argument("--today")
    f.add_argument("--models")
    lst = sub.add_parser("lists")
    lst.add_argument("--results", required=True)
    gg = lst.add_mutually_exclusive_group(required=True)
    gg.add_argument("--models")
    gg.add_argument("--calibration", metavar="ROUND")
    lst.add_argument("--today")
    lst.add_argument("--seed")
    for p in (c, sm, ex, d, f, lst):
        p.add_argument("--state", required=True)
    a = ap.parse_args(argv)
    st = State(a.state)
    {"calibrate": cmd_calibrate, "sample": cmd_sample, "extend": cmd_extend, "draw": cmd_draw, "fresh": cmd_fresh,
     "lists": cmd_lists}[a.cmd](a, st)


if __name__ == "__main__":
    main()
