"""A fake grid in the real formats, for the tests of DESIGN.md section 9.

The grid's slots come from the registered schedules (registration/schedules/). Each slot gets
one or more attempts, each attempt a run folder written as the harness writes one (manifest,
trace, commands, server log), a key line with the fields of write_blind_key() in
run_one_with_server.sh, and, for the apps the real blind_tools.py puts in the quality sample,
a score sheet made with the rubric's own score_sheet.py and an API probe file.

Effects are planted through a scenario: base rates, then overrides for any cell that matches
a model, task, condition or arm. The planted values are the truth the tests compare against.
Nothing here reads a grid run or a grade.

    plan = make_plan(scenario, seed, schedules_dir, rubrics_dir)
    write_grid(plan, root, rubrics_dir)      # the files
    rows = truth_rows(plan)                  # what the run table must hold, for the round trip
"""
import csv
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

from . import config
from .load import rubrics_module

PLAN_DIR = Path(__file__).resolve().parents[2]
SCHEDULES = PLAN_DIR / "registration" / "schedules"
RUBRICS = PLAN_DIR / "rubrics"

# Base rates. Every rate is per run unless named otherwise. The values are realistic in scale
# only: they are not the smoke set's outcomes and they set no planted effect.
BASE = {
    "p_void": 0.0,            # an attempt is void (half unparseable output, half runner failure)
    "p_fail": 0.15,           # the run does not finish
    "steps_mu": math.log(60), # log steps, normal
    "steps_sd": 0.5,
    "rate": 0.9,              # chance that a step reasons (0 in OFF unless set)
    "med_chars": 300.0,       # median reasoning characters on a reasoning step
    "p_silent": 0.10,         # the run has one silent turn
    "p_prose": 0.10,          # the run has one turn of prose alone
    "p_nudge": 0.10,          # the run is nudged
    "p_check": 0.5,           # the run checks its own work (feedback conditions)
    "q_works": 0.6,           # a graded app works (items then pass at 0.9, else at 0.1)
    "p_sub": 0.05,            # a graded app needed a substituted (A0 ETARGET) or added (A8) package
    "p_api": 0.7,             # a probe check passes
    "watts": 250.0,
}
FAIL_STATUSES = config.FAIL_STATUSES
GRADED_ON = "2026-10-20"


def scenario(**overrides):
    """A scenario: {"base": {...}, "cells": [(match, params), ...]}. Keyword arguments set base
    rates. Add cell overrides with scenario_cells()."""
    base = dict(BASE)
    base.update(overrides)
    return {"base": base, "cells": []}


def params_for(sc, model, task, condition, arm):
    p = dict(sc["base"])
    if arm == "off":
        p["rate"] = 0.0
    for match, over in sc["cells"]:
        here = {"model": model, "task": task, "condition": condition, "arm": arm}
        if all(here[k] == v or (isinstance(v, (list, tuple)) and here[k] in v) for k, v in match.items()):
            p.update(over)
    return p


def read_schedules(schedules_dir=SCHEDULES, models=None, max_replicate=None):
    out = []
    for path in sorted(Path(schedules_dir).glob("schedule-real-*.tsv")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 7:
                    continue
                seq, model, task, cond, arm, cid, label = parts[:7]
                rep = int(label.rsplit("/r", 1)[1])
                if (models is None or model in models) and (max_replicate is None or rep <= max_replicate):
                    out.append({"model": model, "task": task, "condition": cond, "arm": arm, "label": label,
                                "replicate": int(label.rsplit("/r", 1)[1])})
    return out


def make_plan(sc, seed, schedules_dir=SCHEDULES, rubrics_dir=RUBRICS, models=None, max_replicate=None):
    """Every attempt of every slot, with all its planted values."""
    rng = np.random.default_rng(config.seed_int(seed, "fakedata"))
    ss = rubrics_module(rubrics_dir)
    cards = {t: ss.load_card(t, str(rubrics_dir)) for t in config.TASKS}
    used = set()

    def new_id():
        while True:
            i = str(int(rng.integers(100000, 1000000)))
            if i not in used:
                used.add(i)
                return i

    attempts = []
    clock = 1.80e9
    for slot in read_schedules(schedules_dir, models, max_replicate):
        p = params_for(sc, slot["model"], slot["task"], slot["condition"], slot["arm"])
        for k in range(3):
            a = dict(slot)
            a["blind_id"] = new_id()
            a["attempt"] = k + 1
            void = rng.random() < p["p_void"]
            a["void"] = (("unparseable" if rng.random() < 0.5 else "runner") if void else None)
            failed = rng.random() < p["p_fail"]
            a["status"] = "api_error" if void else (str(rng.choice(FAIL_STATUSES)) if failed else "finished")
            steps = max(3, int(round(math.exp(rng.normal(p["steps_mu"], p["steps_sd"])))))
            a["steps"] = steps
            # Reasoning, step by step: 0 means no reasoning on that step.
            lens = []
            for _ in range(steps):
                if rng.random() < p["rate"]:
                    lens.append(max(1, int(round(p["med_chars"] * math.exp(rng.normal(0.0, 0.6))))))
                else:
                    lens.append(0)
            a["lengths"] = lens
            # One silent turn and one prose turn at most, never on the last step.
            a["silent_step"] = int(rng.integers(1, steps)) if rng.random() < p["p_silent"] else None
            ps = int(rng.integers(1, steps)) if rng.random() < p["p_prose"] else None
            a["prose_step"] = ps if ps != a["silent_step"] else None
            a["nudges"] = int(rng.integers(1, 3)) if rng.random() < p["p_nudge"] else 0
            a["self_check"] = bool(rng.random() < p["p_check"])
            a["tokens_prompt"] = int(steps * rng.integers(3000, 9000))
            a["tokens_completion"] = int(sum(lens) / 4 + steps * 80)
            a["max_prompt"] = int(rng.integers(8000, 64000))
            a["prompt_ms"] = [round(float(rng.uniform(20, 900)), 2) for _ in range(steps)]
            a["eval_ms"] = [round(float(rng.uniform(500, 8000)), 2) for _ in range(steps)]
            a["fsr"] = {"count": int(rng.integers(0, 4)), "writes": 0, "edits": 0, "reverts": int(rng.integers(0, 2)),
                        "max_times": int(rng.integers(1, 4))}
            a["fsr"]["writes"] = int(rng.integers(0, a["fsr"]["count"] + 1))
            a["fsr"]["edits"] = a["fsr"]["count"] - a["fsr"]["writes"]
            dur = float(steps * 4 + rng.integers(5, 30))
            a["start"], a["end"] = clock, clock + dur
            clock += dur + float(rng.integers(20, 60))
            # The app, if it is graded: its card's items and its probe's checks.
            card = cards[slot["task"]]
            works = rng.random() < p["q_works"]
            a["items"] = {it["id"]: ("pass" if rng.random() < (0.9 if works else 0.1) else "fail")
                          for it in card["items"]}
            u = rng.random()
            a["substituted"] = ("A8" if u < p["p_sub"] / 2 else "ETARGET" if u < p["p_sub"] else None)
            a["api"] = ["pass" if rng.random() < p["p_api"] else "fail" for _ in range(4 if slot["task"] == "message-board" else 10)]
            a["watts"] = p["watts"]
            attempts.append(a)
            if not void:
                break
    return {"scenario": sc, "seed": seed, "attempts": attempts, "cards": cards}


# ---------------------------------------------------------------- writing the files

def _words(n):
    s = ("we need to check the route and the handler first then write the file " * (n // 60 + 1))
    return s[:n]


def _trace_rows(a):
    rows = []
    last = a["steps"]
    for i in range(1, last + 1):
        rsn = _words(a["lengths"][i - 1]) if a["lengths"][i - 1] else ""
        if i == a["silent_step"]:
            text, calls = "", []
        elif i == a["prose_step"]:
            text, calls = "The server should now accept the request.", []
        elif i == last and a["status"] == "finished":
            text, calls = "", [{"name": "finish", "arguments": {"summary": "done"}}]
        else:
            text, calls = "", [{"name": "write_file", "arguments": {"path": f"src/f{i}.js", "content": "x"}}]
        rows.append({"kind": "request", "step": i, "messages": [], "tools": []})
        raw = {"role": "assistant", "content": text, "reasoning_content": rsn,
               "tool_calls": [{"type": "function", "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])}}
                              for c in calls]}
        rows.append({"kind": "response", "step": i, "text": text, "latency_s": 1.0, "tool_calls": calls, "raw": raw})
        if calls:
            rows.append({"kind": "tool_result", "step": i, "tool": calls[0]["name"], "result": "ok", "had_image": False})
    return rows


def _manifest(a, template):
    m = dict(template)
    m.update(config.REGISTERED)
    reasoned = [x for x in a["lengths"] if x]
    m.update({
        "condition": a["condition"], "task_sha": config.TASK_SHA[a["task"]],
        "reasoning_replayed": a["arm"] == "seen",
        "started_at": a["start"], "ended_at": a["end"], "status": a["status"], "steps": a["steps"],
        "total_tokens_used": {"prompt_tokens": a["tokens_prompt"], "completion_tokens": a["tokens_completion"],
                              "total_tokens": a["tokens_prompt"] + a["tokens_completion"]},
        "finish_nudges": a["nudges"], "finish_nudge_steps": [],
        "loop_guard_fired": {"guard": "cycle", "step": a["steps"]} if a["status"] == "stuck_looping" else None,
        "reasoning_turns": len(reasoned), "reasoning_chars": sum(reasoned),
        "reasoning_replayed_turns": len(reasoned) if a["arm"] == "seen" else 0,
        "reasoning_replayed_chars": sum(reasoned) if a["arm"] == "seen" else 0,
        "file_state_repeats": a["fsr"],
        "quantization_detail": {"status": "ok", "model_key": a["model"]},
    })
    if a["void"] == "unparseable":
        m["api_error"] = {"model_output_unparseable": True, "body": "unparsed peg-native output"}
    elif a["void"] == "runner":
        m["api_error"] = {"body": "connection reset by peer"}
    return m


def _server_log(a):
    lines = []
    for i in range(a["steps"]):
        n = a["max_prompt"] if i == a["steps"] - 1 else int(a["max_prompt"] * (i + 1) / a["steps"])
        lines.append('srv  params_from_: {"n_prompt_tokens":%d}' % n)
        lines.append("slot print_timing: id  0 | task %d | prompt eval time =   %8.2f ms /  2043 tokens" % (i, a["prompt_ms"][i]))
        lines.append("slot print_timing: id  0 | task %d |        eval time =   %8.2f ms /   331 tokens" % (i, a["eval_ms"][i]))
    return "\n".join(lines) + "\n"


def _commands(a):
    out = []
    for i in range(1, a["steps"] + 1):
        out.append({"step": i, "tool": "write_file", "args_head": '{"path": "src/f.js"}'})
    if a["self_check"]:
        out.insert(min(2, len(out)), {"step": 2, "tool": "run_command", "args_head": "npm run dev"})
    return out


def _iso(epoch):
    import datetime
    return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc).isoformat(timespec="seconds")


def key_line(a, root):
    """A key line with exactly the fields write_blind_key() writes."""
    base = str(Path(root) / "runs" / a["model"] / a["task"] / "runs" / a["blind_id"])
    return {"blind_id": a["blind_id"], "task": a["task"], "condition": a["condition"], "arm": a["arm"],
            "model_key": a["model"], "alias": a["model"], "quant": "Q4_K_M",
            "replay_reasoning": "1" if a["arm"] == "seen" else "0", "extra_body": None,
            "label": a["label"], "run_base": base, "started_at": _iso(a["start"]),
            "ended_at": _iso(a["end"]), "agent_rc": 1 if a["void"] else 0,
            "status": a["status"]}


def write_grid(plan, root, rubrics_dir=RUBRICS, template=None, per_cell=config.QUALITY_PER_CELL,
               regrade_per_cell=0, extend_to=None):
    """Write the fake grid under root: runs/, state/, results/ (sheets and probe/), power/.
    Then make the quality sample with the real blind_tools.py, one draw per tier, and grade
    (fill a sheet and a probe file for) every sampled app."""
    root = Path(root)
    state, results, probe, power = root / "state", root / "results", root / "results" / "probe", root / "power"
    for d in (state, results, probe, power):
        d.mkdir(parents=True, exist_ok=True)
    template = template or {}
    by_id = {}
    with open(state / "blind-key.jsonl", "w", encoding="utf-8") as key, \
            open(state / "blind-ids.txt", "w", encoding="utf-8") as ledger:
        for a in plan["attempts"]:
            by_id[a["blind_id"]] = a
            logs = root / "runs" / a["model"] / a["task"] / "runs" / a["blind_id"] / "smoke" / "logs"
            logs.mkdir(parents=True, exist_ok=True)
            (logs / "manifest.json").write_text(json.dumps(_manifest(a, template), indent=1), encoding="utf-8")
            with open(logs / "trace.jsonl", "w", encoding="utf-8") as f:
                for r in _trace_rows(a):
                    f.write(json.dumps(r) + "\n")
            (logs / "commands.json").write_text(json.dumps(_commands(a)), encoding="utf-8")
            (logs / "llama-server.log").write_text(_server_log(a), encoding="utf-8")
            key.write(json.dumps(key_line(a, root)) + "\n")
            ledger.write(a["blind_id"] + "\n")
    with open(power / "power-fake.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for a in plan["attempts"]:
            t = a["start"] + 2.5
            while t < a["end"]:
                w.writerow([f"{t:.1f}", f"{a['watts']:.1f}", "90"])
                t += 5.0
    bt = Path(rubrics_dir) / "blind_tools.py"
    present = {a["model"] for a in plan["attempts"]}
    for tier, models in config.TIERS.items():
        ms = [m for m in models if m in present]
        if not ms:
            continue
        _run([sys.executable, str(bt), "sample", "--state", str(state), "--seed", config.DRAW_SEED,
              "--draw", tier, "--per-cell", str(per_cell), "--models", ",".join(ms)])
        if extend_to:
            _run([sys.executable, str(bt), "extend", "--state", str(state), "--draw", tier, "--to", str(extend_to)])
        if regrade_per_cell:
            _run([sys.executable, str(bt), "draw", "--state", str(state), "--seed", config.DRAW_SEED,
                  "--draw", f"{tier}-regrade", "--per-cell", str(regrade_per_cell), "--models", ",".join(ms)])
    from .load import quality_sample, read_jsonl
    sample = quality_sample(str(state))
    ss = rubrics_module(rubrics_dir)
    for bid in sample:
        _grade(ss, plan["cards"], by_id[bid], bid, results, probe)
    for r in read_jsonl(state / "regrade-key.jsonl"):
        first = by_id[r["regrade_of"]]
        second = dict(first, items={k: "fail" for k in first["items"]}, substituted=None)
        _grade(ss, plan["cards"], second, r["blind_id"], results, probe)
    return {"key": state / "blind-key.jsonl", "runs": root / "runs", "state": state, "results": results,
            "probe": probe, "power": power, "sample": sample}


def _run(cmd):
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{out.stdout}\n{out.stderr}")


def _grade(ss, cards, a, bid, results, probe):
    card = cards[a["task"]]
    sheet = ss.blank(a["task"], bid, card)
    sheet["graded_on"] = GRADED_ON
    sheet["grader"] = "fake"
    l0 = f"{'KB' if a['task'] == 'kanban-board' else 'MB'}-L0"
    for st in sheet["steps"]:
        for iid, v in st["items"].items():
            v["result"] = a["items"][iid]
            v["notes"] = "fake"
            if iid == l0 and a["substituted"] == "ETARGET":
                v["notes"] = "A0: npm ci stopped with ETARGET, re-run with npm install --no-save pkg@latest"
            if iid == l0 and a["substituted"] == "A8":
                v["notes"] = "A8: npm install --no-save concurrently, then npm run dev"
    if a["substituted"] == "ETARGET":
        sheet["accommodations"] = ["A0"]
    elif a["substituted"] == "A8":
        sheet["accommodations"] = ["A8"]
    probs = ss.problems(sheet, card)
    if probs:
        raise RuntimeError(f"fake sheet {bid} is not complete: {probs}")
    (Path(results) / f"{bid}.score.json").write_text(json.dumps(sheet, indent=1), encoding="utf-8")
    pre = "KB" if a["task"] == "kanban-board" else "MB"
    checks = [{"id": f"{pre}-API{i + 1}", "spec": "2.4", "asks": "fake", "result": r, "detail": ""}
              for i, r in enumerate(a["api"])]
    summary = {k: sum(1 for c in checks if c["result"] == k) for k in ("pass", "fail", "inconclusive", "blocked")}
    (Path(probe) / f"{bid}.api-probe.json").write_text(json.dumps(
        {"probe_version": "1.0.0", "task": a["task"], "blind_id": bid, "checks": checks, "summary": summary}),
        encoding="utf-8")


# ---------------------------------------------------------------- the truth

def truth_rows(plan, sample, rubrics_dir=RUBRICS):
    """The run table the loader must produce from the written grid, computed from the plan."""
    ss = rubrics_module(rubrics_dir)
    by_slot = {}
    for a in plan["attempts"]:
        if a["void"] is None:
            by_slot[a["label"]] = a
    out = {}
    for label, a in by_slot.items():
        thinking = [x for x in a["lengths"] if x]
        sheet = ss.blank(a["task"], a["blind_id"], plan["cards"][a["task"]])
        for st in sheet["steps"]:
            for iid, v in st["items"].items():
                v["result"] = a["items"][iid]
        q, _, _ = ss.score(sheet, plan["cards"][a["task"]])
        n_api = sum(1 for r in a["api"] if r in ("pass", "fail"))
        sampled = a["blind_id"] in sample
        out[a["blind_id"]] = {
            "model": a["model"], "task": a["task"], "condition": a["condition"], "arm": a["arm"],
            "replicate": a["replicate"], "status": a["status"], "steps": float(a["steps"]),
            "failed": 0.0 if a["status"] == "finished" else 1.0,
            "nudged": 1.0 if a["nudges"] else 0.0,
            "reasoning_rate": len(thinking) / a["steps"],
            "reasoning_median_chars": float(np.median(thinking)) if thinking else float("nan"),
            "silent_turn": 1.0 if a["silent_step"] else 0.0,
            "prose_turns": 1.0 if a["prose_step"] else 0.0,
            "self_check": (1.0 if a["self_check"] else 0.0) if a["condition"] in config.FEEDBACK_CONDITIONS else float("nan"),
            "max_prompt_tokens": float(a["max_prompt"]),
            "gpu_s": (sum(a["prompt_ms"]) + sum(a["eval_ms"])) / 1000.0,
            "machine_s": a["end"] - a["start"],
            "tokens_total": float(a["tokens_prompt"] + a["tokens_completion"]),
            "sampled": 1.0 if sampled else 0.0,
            "quality": float(q) if sampled else float("nan"),
            "substituted": 1.0 if (sampled and a["substituted"]) else 0.0,
            "api_conformance": (sum(1 for r in a["api"] if r == "pass") / n_api) if sampled else float("nan"),
        }
    return out
