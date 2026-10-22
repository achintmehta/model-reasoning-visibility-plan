#!/usr/bin/env python3
"""score_sheet.py — the score sheet for one grading: make it, check it, score it.

    python3 score_sheet.py new <task> <blind id> [--dir DIR]   # a blank sheet to fill in
    python3 score_sheet.py check <sheet.json> [...]            # refuses anything incomplete
    python3 score_sheet.py score <sheet.json> [...]            # the score of each sheet
    python3 score_sheet.py refresh <sheet.json> [...]          # bring a sheet in line with the cards

One sheet per grading, named <blind id>.score.json, in your results folder (GRADING_RESULTS,
or --dir). A re-grade has its own blind id, so its own sheet.

The sheet follows the card's script, so you can grade from it alone:
- `card_notes`: the card's notes from above its script (texts to type, windows, order,
  dependencies), for reference.
- `steps`: one entry per step of the script, in order. Each has the step's number, what to `do`,
  what it scores (`then_score`), and the `items` scored at that step, each with its `goal` (what it
  checks, in a few words), its criterion, its `fails_when` examples and its weight copied from the card, and the two fields you fill:
  `result` (`pass`, `fail` or `skip`) and `notes` (what you saw). `skip` is only for a
  grader-side problem, and its notes must say what it was. Changing the copied text changes
  nothing.

Filling it in (any text editor):
- `graded_on`: the date you graded the app, YYYY-MM-DD.
- each item's `result` and `notes`, step by step.
- `accommodations`: the codes you used (A0 to A8), each also named in the notes of the launch
  item it stands in for. An A6, an A7 or an A8 also needs its exact commands in those notes.
- `notes`: anything else you noticed (rubric README, "Notes").

After a card changes (calibration only), `refresh` rewrites each sheet's steps and copied
criteria from the current card (and puts an older, flat sheet into steps), keeps every result
and note of an item that still exists, adds new items blank, and lists any item the card no longer has (its result is dropped, its notes are
kept in the sheet's `notes`). Close the sheet in your editor first.

The score (protocol §6.1) is the weighted share of the items scored pass or fail that pass,
out of 100. Skipped items are left out. A sheet scores only when `check` passes.

Stdlib only.
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = ("kanban-board", "message-board")
RESULTS = ("pass", "fail", "skip")
ACCOMMODATIONS = ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8")
ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def load_card(task, cards_dir=HERE):
    with open(os.path.join(cards_dir, f"{task}.rubric.json"), encoding="utf-8") as f:
        card = json.load(f)
    card["_md"] = os.path.join(cards_dir, f"{task}.rubric.md")
    return card


def read_md(card):
    """The card's notes above its script, and its script: [(step, do, then_score)]."""
    notes, script = [], []
    try:
        with open(card["_md"], encoding="utf-8") as f:
            text = f.read()
    except (OSError, KeyError):
        return notes, script
    head, _, rest = text.partition("## Script")
    for para in head.split("\n\n")[1:]:
        if not para.strip() or para.lstrip().startswith("**Scores:**"):
            continue
        # one entry per line of text, a bullet starting a new entry
        entries = []
        for line in para.splitlines():
            t = line.strip()
            if t.startswith("- ") or not entries:
                entries.append(t)
            elif t:
                entries[-1] += " " + t
        notes += entries
    for line in rest.partition("## Items")[0].splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"\d+", cells[0]):
            script.append((cells[0], " | ".join(cells[1:-1]), cells[-1]))
    return notes, script


def last_step(step):
    """An item scored over several steps ("5, 6") is filled in at the last of them."""
    nums = re.findall(r"\d+", str(step))
    return nums[-1] if nums else str(step)


def items_of(sheet):
    """Every item of a sheet, by id, whether the sheet is in steps or flat."""
    if isinstance(sheet.get("steps"), list):
        out = {}
        for st in sheet["steps"]:
            for iid, v in (st.get("items") or {}).items():
                out[iid] = v
        return out
    return sheet.get("items") if isinstance(sheet.get("items"), dict) else {}


def build_steps(card, old=None):
    """The sheet's steps from the card, keeping any result and notes in old (by item id)."""
    old = old or {}
    notes, script = read_md(card)
    by_step = {}
    for it in card["items"]:
        o = old.get(it["id"], {})
        by_step.setdefault(last_step(it["step"]), {})[it["id"]] = {
            "goal": it.get("goal", ""), "criterion": it["criterion"], "fails_when": it.get("fails_when", ""),
            "weight": it["weight"], "result": o.get("result", ""), "notes": o.get("notes", "")}
    steps, seen = [], set()
    for num, do, then in script:
        steps.append({"step": num, "do": do, "then_score": then, "items": by_step.get(num, {})})
        seen.add(num)
    for num, items in by_step.items():          # an item whose step is not in the script
        if num not in seen:
            steps.append({"step": num, "do": "", "then_score": "", "items": items})
    return notes, steps


def blank(task, blind_id, card):
    notes, steps = build_steps(card)
    return {
        "blind_id": blind_id,
        "task": task,
        "card_version": card["version"],
        "graded_on": "",
        "grader": os.environ.get("GRADER", ""),
        "accommodations": [],
        "card_notes": notes,
        "steps": steps,
        "notes": "",
    }


def problems(sheet, card):
    """Every reason the sheet is not complete and valid (an empty list when it is)."""
    out = []
    want = {it["id"]: it for it in card["items"]}
    if not ID_RE.match(str(sheet.get("blind_id", ""))):
        out.append("blind_id is missing or malformed")
    if sheet.get("task") != card["task"]:
        out.append(f"task is {sheet.get('task')!r}, the card is {card['task']!r}")
    if sheet.get("card_version") != card["version"]:
        out.append(f"card_version is {sheet.get('card_version')!r}; the card in use is {card['version']!r}")
    try:
        d = datetime.date.fromisoformat(str(sheet.get("graded_on", "")))
        if d > datetime.date.today() + datetime.timedelta(days=1):
            out.append(f"graded_on {d} is in the future")
    except ValueError:
        out.append("graded_on is not a date (YYYY-MM-DD)")
    acc = sheet.get("accommodations", [])
    if not isinstance(acc, list) or any(a not in ACCOMMODATIONS for a in acc):
        out.append(f"accommodations must be a list of {', '.join(ACCOMMODATIONS)}")
    items = items_of(sheet)
    if not items:
        return out + ["no items found (neither steps nor items)"]
    if isinstance(sheet.get("steps"), list):
        ids = [i for st in sheet["steps"] for i in (st.get("items") or {})]
        dup = sorted({i for i in ids if ids.count(i) > 1})
        if dup:
            out.append(f"items listed more than once: {', '.join(dup)}")
    for iid in want:
        if iid not in items:
            out.append(f"{iid} is missing")
            continue
        r = items[iid].get("result") if isinstance(items[iid], dict) else None
        if r not in RESULTS:
            out.append(f"{iid}: result is {r!r}; it must be pass, fail or skip"
                       + (" (partial is not used)" if r == "partial" else ""))
        elif r == "skip" and not str(items[iid].get("notes", "")).strip():
            out.append(f"{iid}: a skip needs notes saying what the grader-side problem was")
    for iid in items:
        if iid not in want:
            out.append(f"{iid} is not an item of the card")
    launch = " ".join(str(items.get(i, {}).get("notes", "")) for i in want if "-L" in i)
    for code in ("A6", "A7", "A8"):
        if code in acc and code not in launch:
            out.append(f"{code} was used: name it, with its exact commands, in the notes of the launch item it stands in for")
    return out


def score(sheet, card):
    """(score out of 100 or None, weight passed, weight scored)."""
    w = {it["id"]: it["weight"] for it in card["items"]}
    items = items_of(sheet)
    passed = sum(w[i] for i, v in items.items() if v.get("result") == "pass")
    scored = sum(w[i] for i, v in items.items() if v.get("result") in ("pass", "fail"))
    return (round(100.0 * passed / scored, 2) if scored else None), passed, scored


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="write a blank sheet")
    n.add_argument("task", choices=TASKS)
    n.add_argument("blind_id")
    n.add_argument("--dir", default=os.environ.get("GRADING_RESULTS", "."))
    for name in ("check", "score", "refresh"):
        c = sub.add_parser(name)
        c.add_argument("sheets", nargs="+")
    a = ap.parse_args(argv)

    if a.cmd == "new":
        if not ID_RE.match(a.blind_id):
            sys.exit(f"not a blind id: {a.blind_id!r}")
        os.makedirs(a.dir, exist_ok=True)
        path = os.path.join(a.dir, f"{a.blind_id}.score.json")
        if os.path.exists(path):
            sys.exit(f"{path} already exists; a sheet, once in, changes only through a ruling")
        with open(path, "x", encoding="utf-8") as f:
            json.dump(blank(a.task, a.blind_id, load_card(a.task)), f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(path)
        return 0

    if a.cmd == "refresh":
        for p in a.sheets:
            sheet = read(p)
            card = load_card(sheet["task"])
            old = items_of(sheet)
            notes, steps = build_steps(card, old)
            want = {it["id"] for it in card["items"]}
            dropped = []
            for iid, o in old.items():
                if iid not in want:
                    dropped.append(iid)
                    if o.get("notes"):
                        sheet["notes"] = (sheet.get("notes", "") + f" [{iid}, dropped by refresh: {o['notes']}]").strip()
            rest = {k: v for k, v in sheet.items() if k not in ("items", "steps", "card_notes", "notes")}
            sheet = {**rest, "card_version": card["version"], "card_notes": notes, "steps": steps,
                     "notes": sheet.get("notes", "")}
            new = {it["id"] for it in card["items"]}
            with open(p, "w", encoding="utf-8") as f:
                json.dump(sheet, f, indent=2, ensure_ascii=False)
                f.write("\n")
            added = [i for i in sorted(new) if i not in old]
            print(f"{p}: refreshed" + (f"; new, blank: {', '.join(added)}" if added else "")
                  + (f"; no longer on the card: {', '.join(dropped)}" if dropped else ""))
        return 0

    bad = 0
    for p in a.sheets:
        try:
            sheet = read(p)
            card = load_card(sheet.get("task")) if sheet.get("task") in TASKS else None
        except (OSError, ValueError) as e:
            print(f"{p}: cannot read: {e}")
            bad += 1
            continue
        if card is None:
            print(f"{p}: task is {sheet.get('task')!r}, not one of {', '.join(TASKS)}")
            bad += 1
            continue
        probs = problems(sheet, card)
        if probs:
            bad += 1
            print(f"{p}: NOT COMPLETE")
            for x in probs:
                print(f"  - {x}")
            continue
        s, passed, scored = score(sheet, card)
        if a.cmd == "check":
            print(f"{p}: ok")
        else:
            print(f"{sheet['blind_id']}\t{sheet['task']}\t{s}\t{passed}/{scored}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
