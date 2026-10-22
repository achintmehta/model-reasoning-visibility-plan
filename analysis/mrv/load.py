"""From the grid's files to the run table: one row per analysed run, every measure of protocol
sections 6.1 to 6.4 (DESIGN.md sections 2 and 3).

Inputs are read only. Nothing is written next to them.
"""
import csv
import glob
import hashlib
import importlib.util
import json
import math
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path

from . import config, record

HERE = Path(__file__).resolve().parent


class InputError(Exception):
    """An input that breaks a rule of protocol section 9: the analysis refuses to go on."""


# ---------------------------------------------------------------- the vendored gate script

def verify_smokes():
    """The smoke set's gate script, unchanged, after checking its sha256 (DESIGN.md section 3)."""
    path = HERE / "vendor" / "verify_smokes.py"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != config.VERIFY_SMOKES_SHA256:
        raise InputError(f"vendor/verify_smokes.py has sha256 {digest}, not the recorded one")
    if "mrv_verify_smokes" in sys.modules:
        return sys.modules["mrv_verify_smokes"]
    spec = importlib.util.spec_from_file_location("mrv_verify_smokes", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mrv_verify_smokes"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- small readers

def read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def read_text(path):
    """A text file, or its .zst twin decompressed with the zstd command."""
    p = Path(path)
    if p.exists():
        return p.read_text(encoding="utf-8", errors="replace")
    z = Path(str(p) + ".zst")
    if z.exists():
        out = subprocess.run(["zstd", "-dc", str(z)], capture_output=True, check=True).stdout
        return out.decode("utf-8", errors="replace")
    return None


# ---------------------------------------------------------------- one run's trace

def trace_measures(logs_dir):
    """The reasoning measures of one run, counted by the smoke gate script's own rules.

    The loop below follows verify_smokes.load_runs() line for line (the tests check that the two
    agree on every smoke run): a step is a `response` row of the trace, its reasoning is the raw
    reply's reasoning field plus any reasoning the server left in the reply text, and a field
    that is wholly a tool call counts as no reasoning.
    """
    vs = verify_smokes()
    trace = Path(logs_dir) / "trace.jsonl"
    if not trace.exists() and not Path(str(trace) + ".zst").exists():
        return None
    steps, lengths, empty, no_tool, reasoned, call_txt = 0, [], 0, 0, 0, 0
    off_lengths = []                 # the OFF canary's measure (gate G2): budget reports not counted
    detail = []                      # one row per step, for the intermediate record
    with vs.open_log(trace) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("kind") != "response":
                continue
            raw = row.get("raw") or {}
            text = row.get("text") if "text" in row else raw.get("content")
            text = text or ""
            rsn = raw.get("reasoning_content") or ""
            rec = vs.reasoning_split(raw.get("content") or "")[0]
            if rec:
                rsn = (rsn.rstrip() + "\n\n" + rec) if rsn.strip() else rec
            steps += 1
            is_call = bool(vs.field_is_call(rsn))
            if is_call:
                lengths.append(0)
                off_lengths.append(0)
            else:
                lengths.append(len(rsn))
                off_lengths.append(len(vs._BUDGET_REPORT.sub("", rsn).strip()))
                if rsn.strip():
                    reasoned += 1
            calls = row.get("tool_calls") or []
            as_text = silent = 0
            if not calls:
                if vs.call_as_text(rsn) or vs.call_as_text(text):
                    call_txt += 1
                    as_text = 1
                no_tool += 1
                if not text.strip():
                    empty += 1
                    silent = 1
            detail.append({"step": row.get("step", steps), "reasoning_chars": lengths[-1],
                           "canary_chars": off_lengths[-1], "field_is_call": int(is_call),
                           "recovered_from_reply_text": int(bool(rec)), "tool_calls": len(calls),
                           "no_tool_call": int(not calls), "silent": silent, "prose": int(not calls and not silent),
                           "call_as_text": as_text})
    thinking = [x for x in lengths if x]
    # A reasoning step is one with a non-empty reasoning field that is not wholly a tool call:
    # the steps the gate script's "rsn%" and "median rsn chars" count (H3 and H4).
    return {
        "trace_steps": steps,
        "reasoned_steps": reasoned,
        "reasoning_lengths": lengths,
        "thinking_steps": len(thinking),
        "reasoning_rate": len(thinking) / steps if steps else float("nan"),
        "reasoning_median_chars": float(statistics.median(thinking)) if thinking else float("nan"),
        "reasoning_chars": float(sum(thinking)),
        "silent_turns": empty,
        "prose_turns": no_tool - empty,
        "no_tool_turns": no_tool,
        "call_as_text_steps": call_txt,
        # The OFF canary's rule (gate G2 of the smoke set, protocol section 5.1): the longest
        # reasoning step with Seed-OSS's budget reports removed, and the steps above OFF_MAX.
        "canary_longest_chars": float(max(off_lengths)) if off_lengths else float("nan"),
        "canary_steps_over": float(sum(1 for x in off_lengths if x > vs.OFF_MAX)),
        "steps_detail": detail,
    }


_TIMING = re.compile(r"(?:prompt eval time|\beval time)\s*=\s*([0-9.]+)\s*ms")
_PROMPT_EVAL = re.compile(r"prompt eval time\s*=\s*([0-9.]+)\s*ms")
_PROMPT_TOKENS = re.compile(r'"n_prompt_tokens"\s*:\s*(\d+)')


def server_measures(logs_dir):
    """GPU compute (prompt evaluation plus generation, from llama-server's timings) and the
    largest prompt of the run (protocol sections 6.2 and 6.4)."""
    text = read_text(Path(logs_dir) / "llama-server.log")
    if text is None:
        return {"gpu_s": float("nan"), "max_prompt_tokens": float("nan"), "timing_lines": 0,
                "prompt_eval_ms": float("nan"), "eval_ms": float("nan"), "prompt_token_lines": 0}
    timings = [float(x) for x in _TIMING.findall(text)]
    prompt_ms = sum(float(x) for x in _PROMPT_EVAL.findall(text))
    gpu_ms = sum(timings)
    prompts = [int(x) for x in _PROMPT_TOKENS.findall(text)]
    return {"gpu_s": gpu_ms / 1000.0, "max_prompt_tokens": float(max(prompts)) if prompts else float("nan"),
            "timing_lines": len(timings), "prompt_eval_ms": prompt_ms, "eval_ms": gpu_ms - prompt_ms,
            "prompt_token_lines": len(prompts)}


_CHECK_CMD = re.compile(r"\b(npm (run )?(dev|start|test|build)|npx |node |curl |wget |vite\b|vitest|jest|"
                        r"playwright|pytest|python3? -m http)", re.I)
_FILE_TOOLS = {"read_file", "write_file", "edit_file", "list_dir", "finish"}
_COMMAND_TOOLS = {"run_command", "run_background_command", "run_command_and_capture_output",
                  "list_background_commands", "stop_background_command"}


def self_check(logs_dir, condition):
    """Whether a run checked its own work (protocol section 6.4, item 6): a server started, an
    HTTP request, a build or test command, or a browser tool. Execution and interactive only."""
    return self_check_detail(logs_dir, condition)[0]


def self_check_detail(logs_dir, condition):
    """self_check() and its evidence: the first call that counted, as 'step N tool: args'."""
    if condition not in config.FEEDBACK_CONDITIONS:
        return float("nan"), "not a feedback condition"
    path = Path(logs_dir) / "commands.json"
    try:
        calls = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return float("nan"), "no readable commands.json"
    for c in calls:
        tool = c.get("tool") or ""
        head = (c.get("args_head") or "").replace("\n", " ")[:120]
        if tool in _COMMAND_TOOLS and _CHECK_CMD.search(c.get("args_head") or ""):
            return 1.0, f"step {c.get('step')} {tool}: {head}"
        if tool and tool not in _FILE_TOOLS and tool not in _COMMAND_TOOLS:
            return 1.0, f"step {c.get('step')} {tool} (a browser or other tool)"
    return 0.0, f"none of {len(calls)} calls"


_INSTALL_CMD = re.compile(r"\b(npm|pnpm|yarn)\s+(install|i|ci|add)\b|\bnpx\s|\bnpm\s+(create|init)\s+\S")
_NETWORK_ERR = re.compile(r"\b(ENOTFOUND|ETIMEDOUT|ECONNRESET)\b")


def npm_unreachable(logs_dir):
    """Evidence that the npm registry was unreachable during an install (protocol section 9):
    a command that installs packages (npm, pnpm or yarn install, ci or add, npx, npm create)
    whose output in the trace holds ENOTFOUND, ETIMEDOUT or ECONNRESET. The trace keeps every
    tool result whole, where console.log shortens them. Returns the command, or None."""
    vs = verify_smokes()
    trace = Path(logs_dir) / "trace.jsonl"
    if not trace.exists() and not Path(str(trace) + ".zst").exists():
        return None
    with vs.open_log(trace) as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("kind") != "tool_result":
                continue
            res = str(row.get("result") or "")
            first = res.split("\n", 1)[0]
            if first.startswith("$ ") and _INSTALL_CMD.search(first) and _NETWORK_ERR.search(res):
                return first[2:200]
    return None


# ---------------------------------------------------------------- the key and the attempts

def label_parts(label):
    """'gemma-q4/message-board/no_verification/off/r01' -> (model, task, condition, arm, 1)."""
    parts = (label or "").split("/")
    if len(parts) != 5 or not parts[4].startswith("r"):
        return None
    return parts[0], parts[1], parts[2], parts[3], int(parts[4][1:])


def run_dir(runs_root, rec):
    return Path(runs_root) / rec["model_key"] / rec["task"] / "runs" / rec["blind_id"]


def check_config(man, task, registered=None):
    """The registered configuration of protocol section 9, and the model file the run was
    served (quantization_detail, resolved from the quantization registry). Returns the list of
    mismatches. `registered` replaces config.REGISTERED when given (the smoke-set test)."""
    reg = config.REGISTERED if registered is None else registered
    bad = []
    for k, v in reg.items():
        got = man.get(k)
        if k == "max_total_tokens":
            ok = got is not None and int(got) == v
        else:
            ok = got == v
        if not ok:
            bad.append(f"{k}={got!r} (registered {v!r})")
    if man.get("task_sha") != config.TASK_SHA.get(task):
        bad.append(f"task_sha={man.get('task_sha')!r} (registered {config.TASK_SHA.get(task)!r})")
    qd = man.get("quantization_detail") or {}
    if qd.get("status") != "ok":
        bad.append(f"quantization_detail status={qd.get('status')!r} (the served file did not resolve)")
    return bad


def is_void(rec, man):
    """A void attempt the runner itself saw (protocol section 9): there is no manifest, the
    runner failed (exit code not 0), or the run ended as an API error (a server fault, or
    output the server could not parse). A context overflow that a harness filed as an API
    error is an outcome, not a void. The frozen harness never files one so (it records
    context_overflow and exits 0), so this only guards against an older build."""
    if man is None:
        return "no manifest"
    vs = verify_smokes()
    if vs.overflow_filed_as_error(man):
        return None
    failed = int(rec.get("agent_rc") or 0) != 0
    api = (man.get("status") or man.get("terminal_status")) == "api_error"
    if not (failed or api):
        return None
    if vs.parse_void(man):
        return "unparseable output"
    return f"runner failed (exit code {rec.get('agent_rc')})" if failed else "api error"


def needs_rerun(man, task, logs_dir, registered=None):
    """A void the runner cannot see (protocol section 9): the run exited normally, but it was
    made under a configuration other than the registered one (or served a file that did not
    resolve), or the npm registry was unreachable during an install. Its slot is re-run by
    hand under the same label. Returns the causes, an empty list if there are none."""
    causes = ["configuration: " + x for x in check_config(man, task, registered)]
    cmd = npm_unreachable(logs_dir)
    if cmd:
        causes.append(f"npm registry unreachable during `{cmd}`")
    return causes


def load_attempts(key_path, runs_root, registered=None):
    """Every key line with its manifest, its void cause (`void`, seen by the runner) and the
    causes that need a re-run by hand (`rerun`, not seen by the runner). Refuses inputs that
    do not fit together: a key line without a run, a run without a key line, a key line
    without a grid label. `registered` replaces config.REGISTERED (the smoke-set test)."""
    recs = read_jsonl(key_path)
    if not recs:
        raise InputError(f"no key lines in {key_path}")
    out, problems = [], []
    for rec in recs:
        lp = label_parts(rec.get("label"))
        if lp is None:
            problems.append(f"{rec.get('blind_id')}: a key line without a grid label ({rec.get('label')!r})")
            continue
        d = run_dir(runs_root, rec)
        mpath = d / "smoke" / "logs" / "manifest.json"
        man = None
        if mpath.exists():
            man = json.loads(mpath.read_text(encoding="utf-8", errors="replace"))
        elif int(rec.get("agent_rc") or 0) == 0:
            problems.append(f"{rec['blind_id']}: key line without a run (no {mpath})")
        void = is_void(rec, man)
        rerun = needs_rerun(man, lp[1], d / "smoke" / "logs", registered) if (man is not None and void is None) else []
        out.append({"rec": rec, "label": lp, "dir": d, "man": man, "void": void, "rerun": rerun})
    known = {str(run_dir(runs_root, a["rec"])) for a in out}
    for m in glob.glob(str(Path(runs_root) / "*" / "*" / "runs" / "*" / "smoke" / "logs" / "manifest.json")):
        rd = str(Path(m).parent.parent.parent)
        if rd not in known:
            problems.append(f"{rd}: a run with no key line")
    if problems:
        raise InputError("the inputs break protocol section 9:\n  " + "\n  ".join(problems[:50])
                         + (f"\n  ... and {len(problems) - 50} more" if len(problems) > 50 else ""))
    return out


def resolve_slots(attempts):
    """One analysed run per slot (protocol section 9), from its attempts in the order they
    started:
    - the analysed run is the first attempt that is neither void nor in need of a re-run
    - an attempt in need of a re-run before it was re-run, and counts as a void attempt
    - an attempt in need of a re-run with no analysed run after it is unresolved: the
      analysis stops and lists it
    - an attempt after the analysed run should not exist (the batch driver ends a slot at its
      first good attempt), so it enters no analysis and is listed
    - a slot whose every attempt is void is empty
    Returns a dict: chosen, empty_slots, void_attempts (each with its cause), unresolved,
    after_outcome."""
    by_slot = {}
    for a in attempts:
        by_slot.setdefault(a["label"], []).append(a)
    out = {"chosen": [], "empty_slots": [], "void_attempts": [], "unresolved": [], "after_outcome": []}
    for slot in sorted(by_slot):
        xs = sorted(by_slot[slot], key=lambda a: a["rec"].get("started_at") or "")
        k = next((i for i, a in enumerate(xs) if a["void"] is None and not a["rerun"]), None)
        before = xs if k is None else xs[:k]
        for a in before:
            if a["void"] is not None:
                out["void_attempts"].append((a, a["void"]))
            elif k is not None:
                out["void_attempts"].append((a, "re-run by hand: " + " | ".join(a["rerun"])))
            else:
                out["unresolved"].append(a)
        if k is None:
            if not any(a["rerun"] and a["void"] is None for a in xs):
                out["empty_slots"].append(slot)
            continue
        out["chosen"].append(xs[k])
        out["after_outcome"] += xs[k + 1:]
    return out


def unresolved_message(unresolved):
    """The list the study lead re-runs by hand: each slot's label and the causes, no blind
    ids and no outcomes, so it can be read without un-blinding any app."""
    lines = []
    for a in unresolved:
        lines.append("/".join(str(x) if i < 4 else f"r{x:02d}" for i, x in enumerate(a["label"]))
                     + ": " + " | ".join(a["rerun"]))
    return ("runs that are void for a cause the runner could not see, with no re-run of their slot "
            "(protocol section 9). Re-run each slot by hand under the same label, then run the "
            "analysis again:\n  " + "\n  ".join(lines))


# ---------------------------------------------------------------- grades and probes

def rubrics_module(rubrics_dir):
    """The rubric's own score_sheet.py, loaded from the rubrics folder given."""
    path = Path(rubrics_dir) / "score_sheet.py"
    name = "mrv_score_sheet_" + hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:8]
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


def quality_sample(state_dir):
    """The apps in the quality sample: rank within their draw's current level (blind_tools.py)."""
    levels = {}
    for r in read_jsonl(os.path.join(state_dir, "sample-levels.jsonl")):
        levels[r["draw"]] = r["level"]
    return {r["blind_id"] for r in read_jsonl(os.path.join(state_dir, "quality-sample.jsonl"))
            if r["rank"] <= levels.get(r["draw"], 0)}


def scores_of_record(results_dir, state_dir, rubrics_dir):
    """{blind id: {quality, substituted, items}} for every first grading (the score of record,
    protocol section 6.1). Second ids of the re-grade set are left out."""
    ss = rubrics_module(rubrics_dir)
    seconds = {r["blind_id"] for r in read_jsonl(os.path.join(state_dir, "regrade-key.jsonl"))}
    cards = {t: ss.load_card(t, str(rubrics_dir)) for t in ss.TASKS}
    out, bad = {}, []
    for p in sorted(glob.glob(os.path.join(results_dir, "*.score.json"))):
        sheet = ss.read(p)
        bid = sheet.get("blind_id")
        if bid in seconds:
            record.add("scores", {"blind_id": bid, "task": sheet.get("task"), "role": "re-grade (left out of the analysis)"})
            continue
        card = cards.get(sheet.get("task"))
        probs = ss.problems(sheet, card) if card else [f"unknown task {sheet.get('task')!r}"]
        if probs:
            bad.append(f"{os.path.basename(p)}: " + ", ".join(probs[:3]))
            continue
        sc, passed, scored = ss.score(sheet, card)
        items = ss.items_of(sheet)
        acc = set(sheet.get("accommodations") or [])
        l0 = " ".join(str(v.get("notes", "")) for k, v in items.items() if k.endswith("-L0"))
        reason = ("A8" if "A8" in acc else "") or ("A0 with ETARGET in the L0 notes" if ("A0" in acc and "ETARGET" in l0) else "")
        out[bid] = {"quality": float("nan") if sc is None else float(sc),
                    "substituted": bool(reason),
                    "items": {k: v.get("result") for k, v in items.items()}}
        record.add("scores", {"blind_id": bid, "task": sheet.get("task"), "role": "first grading",
                              "card_version": sheet.get("card_version"), "graded_on": sheet.get("graded_on"),
                              "items_pass": sum(1 for v in items.values() if v.get("result") == "pass"),
                              "items_fail": sum(1 for v in items.values() if v.get("result") == "fail"),
                              "items_skip": sum(1 for v in items.values() if v.get("result") == "skip"),
                              "weight_passed": passed, "weight_scored": scored,
                              "score": out[bid]["quality"], "score_rule": "round(100 x weight_passed / weight_scored, 2)",
                              "accommodations": " ".join(sorted(acc)), "substituted": int(bool(reason)),
                              "substituted_because": reason})
    if bad:
        raise InputError("score sheets that are not complete (score_sheet.py check):\n  " + "\n  ".join(bad))
    return out


def api_conformance(probe_dir):
    """{blind id: share of the probe's checks passed, over those passed or failed} (section 6.5)."""
    out = {}
    for p in glob.glob(os.path.join(probe_dir, "*.api-probe.json")):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        res = [c.get("result") for c in d.get("checks") or []]
        n = sum(1 for r in res if r in ("pass", "fail"))
        out[d["blind_id"]] = (sum(1 for r in res if r == "pass") / n) if n else float("nan")
        record.add("probes", {"blind_id": d["blind_id"], "task": d.get("task"), "checks": len(res),
                              **{k: sum(1 for r in res if r == k) for k in ("pass", "fail", "inconclusive", "blocked")},
                              "api_conformance": out[d["blind_id"]], "rule": "pass / (pass + fail)"})
    return out


def power_samples(power_dir):
    """Every (epoch seconds, watts) sample of the power logs, sorted by time."""
    xs = []
    for p in glob.glob(os.path.join(power_dir, "power-*.csv")):
        with open(p, encoding="utf-8") as f:
            for row in csv.reader(f):
                try:
                    xs.append((float(row[0]), float(row[1])))
                except (ValueError, IndexError):
                    continue
    xs.sort()
    return xs


def energy_wh(samples, start, end):
    """Board power integrated over a run's span by the trapezoid rule, in watt hours: the
    samples inside the span, with the power at the span's two ends taken from the nearest
    sample inside it. NaN if the span holds no sample."""
    import bisect
    if not samples or not (end > start):
        return float("nan")
    times = [t for t, _ in samples]
    i, j = bisect.bisect_left(times, start), bisect.bisect_right(times, end)
    inside = samples[i:j]
    if not inside:
        return float("nan")
    pts = [(start, inside[0][1])] + inside + [(end, inside[-1][1])]
    joules = sum((t2 - t1) * (w1 + w2) / 2.0 for (t1, w1), (t2, w2) in zip(pts, pts[1:]))
    return joules / 3600.0


def power_samples_in(samples, start, end):
    import bisect
    times = [t for t, _ in samples]
    return bisect.bisect_right(times, end) - bisect.bisect_left(times, start) if samples else 0


# ---------------------------------------------------------------- the run table

def _record_attempts(attempts, res):
    """Every attempt, what the key and the manifest say, and what became of it."""
    if not record.active():
        return
    role = {}
    for a in res["chosen"]:
        role[id(a)] = "analysed run of its slot"
    for a, cause in res["void_attempts"]:
        role[id(a)] = "void attempt: " + cause
    for a in res["after_outcome"]:
        role[id(a)] = "left out: made after its slot's analysed run"
    for a in res["unresolved"]:
        role[id(a)] = "unresolved: needs a re-run"
    empty = {tuple(s) for s in res["empty_slots"]}
    for a in sorted(attempts, key=lambda a: (a["label"], a["rec"].get("started_at") or "")):
        rec, man = a["rec"], a["man"] or {}
        record.add("attempts", {
            "blind_id": rec["blind_id"], "label": rec.get("label"), "started_at": rec.get("started_at"),
            "agent_rc": rec.get("agent_rc"), "manifest": int(a["man"] is not None),
            "manifest_status": man.get("status"), "void_cause": a["void"] or "",
            "needs_rerun": " | ".join(a["rerun"]),
            "role": role.get(id(a), ""), "slot_empty": int(a["label"] in empty)})


def loop_guard(man):
    """Which loop guard ended the run (same_calls, cycle or no_progress), or None. The
    harness records a dict with the guard and the step."""
    g = man.get("loop_guard_fired")
    if isinstance(g, dict):
        return g.get("guard")
    return g or None


def build_table(key_path, runs_root, results_dir=None, state_dir=None, rubrics_dir=None,
                probe_dir=None, power_dir=None, registered=None):
    """The run table of DESIGN.md section 3 and what goes with it, as a dict:
    rows       one dict per analysed run (the run table)
    voids      the empty slots, the void attempts with their causes, and any attempt made
               after its slot's analysed run (protocol section 9)
    items      {blind id: {rubric item: result}} for every score of record
    spans      (start, end) in epoch seconds of every attempt, void ones included
    ungraded   blind ids of analysed runs in the quality sample with no score of record
    sampled_void  blind ids in the quality sample that are void attempts, not analysed runs
    """
    attempts = load_attempts(key_path, runs_root, registered)
    res = resolve_slots(attempts)
    if res["unresolved"]:
        raise InputError(unresolved_message(res["unresolved"]))
    chosen, void_slots = res["chosen"], res["empty_slots"]
    _record_attempts(attempts, res)
    sample = quality_sample(state_dir) if state_dir else set()
    scores = scores_of_record(results_dir, state_dir, rubrics_dir) if (results_dir and state_dir and rubrics_dir) else {}
    probes = api_conformance(probe_dir) if probe_dir else {}
    power = power_samples(power_dir) if power_dir else []
    rows = []
    for a in chosen:
        rec, man, logs = a["rec"], a["man"], a["dir"] / "smoke" / "logs"
        model, task, cond, arm, rep = a["label"]
        tm = trace_measures(logs) or {}
        sm = server_measures(logs)
        # A context overflow a harness filed as an API error is the outcome context_overflow.
        status = "context_overflow" if verify_smokes().overflow_filed_as_error(man) else man.get("status")
        steps = man.get("steps")
        finished = status == "finished"
        tok = man.get("total_tokens_used") or {}
        fsr = man.get("file_state_repeats") or {}
        start, end = man.get("started_at"), man.get("ended_at")
        bid = rec["blind_id"]
        sc = scores.get(bid, {})
        sc_value, sc_evidence = self_check_detail(logs, cond)
        if record.active():
            for d in tm.get("steps_detail", []):
                record.add("steps", {"blind_id": bid, **d})
            record.add("run-evidence", {
                "blind_id": bid, "manifest_status": man.get("status"), "status_used": status,
                "status_rule": ("an overflow filed as api_error, entered as context_overflow"
                                if status != man.get("status") else "the manifest's status"),
                "manifest_steps": steps, "trace_steps": tm.get("trace_steps"),
                "loop_guard_fired": json.dumps(man.get("loop_guard_fired")),
                "finish_nudges": man.get("finish_nudges"), "finish_nudge_steps": json.dumps(man.get("finish_nudge_steps") or []),
                "self_check": sc_value, "self_check_evidence": sc_evidence,
                "server_timing_lines": sm["timing_lines"], "prompt_eval_ms": sm["prompt_eval_ms"],
                "eval_ms": sm["eval_ms"], "gpu_s": sm["gpu_s"], "prompt_token_lines": sm["prompt_token_lines"],
                "max_prompt_tokens": sm["max_prompt_tokens"], "started_at": start, "ended_at": end,
                "power_samples_in_span": power_samples_in(power, float(start), float(end)) if (start and end) else 0,
                "energy_rule": "trapezoid over the samples in the span, the ends at the nearest sample's power",
                "sampled": int(bid in sample), "has_score_of_record": int(bid in scores)})
        rows.append({
            "blind_id": bid, "model": model, "task": task, "condition": cond, "arm": arm,
            "replicate": rep, "stratum": f"{task}|{cond}",
            "status": status, "loop_guard": loop_guard(man),
            "failed": 0.0 if finished else 1.0,
            "steps": float(steps) if steps is not None else float("nan"),
            "log_steps": math.log(steps) if finished and steps else float("nan"),
            "nudged": 1.0 if (man.get("finish_nudges") or 0) > 0 else 0.0,
            "finish_nudges": float(man.get("finish_nudges") or 0),
            "finish_nudge_steps": [int(x) for x in (man.get("finish_nudge_steps") or [])],
            "tokens_prompt": float(tok.get("prompt_tokens", float("nan"))),
            "tokens_completion": float(tok.get("completion_tokens", float("nan"))),
            "tokens_total": float(tok.get("total_tokens", float("nan"))),
            "reasoning_rate": tm.get("reasoning_rate", float("nan")),
            "reasoning_median_chars": tm.get("reasoning_median_chars", float("nan")),
            "log_reasoning_median_chars": (math.log(tm["reasoning_median_chars"])
                                           if tm.get("reasoning_median_chars", float("nan")) > 0 else float("nan")),
            "reasoning_chars": tm.get("reasoning_chars", float("nan")),
            "reasoning_chars_per_step": (tm["reasoning_chars"] / tm["trace_steps"]
                                         if tm.get("trace_steps") else float("nan")),
            "replayed_turns": float(man.get("reasoning_replayed_turns") or 0),
            "replayed_chars": float(man.get("reasoning_replayed_chars") or 0),
            "trace_steps": float(tm.get("trace_steps", float("nan"))),
            "thinking_steps": float(tm.get("thinking_steps", float("nan"))),
            "no_tool_turns": float(tm.get("no_tool_turns", float("nan"))),
            "silent_turn": 1.0 if tm.get("silent_turns", 0) > 0 else 0.0,
            "silent_turns": float(tm.get("silent_turns", float("nan"))),
            "prose_turns": float(tm.get("prose_turns", float("nan"))),
            "call_as_text_steps": float(tm.get("call_as_text_steps", float("nan"))),
            "canary_longest_chars": tm.get("canary_longest_chars", float("nan")),
            "canary_steps_over": tm.get("canary_steps_over", float("nan")),
            "self_check": sc_value,
            "file_state_count": float(fsr.get("count", 0)), "file_state_writes": float(fsr.get("writes", 0)),
            "file_state_edits": float(fsr.get("edits", 0)), "file_state_reverts": float(fsr.get("reverts", 0)),
            "file_state_max_times": float(fsr.get("max_times", 0)),
            "max_prompt_tokens": sm["max_prompt_tokens"],
            "machine_s": (float(end) - float(start)) if (start and end) else float("nan"),
            "gpu_s": sm["gpu_s"],
            "energy_wh": energy_wh(power, float(start), float(end)) if (start and end) else float("nan"),
            "sampled": 1.0 if bid in sample else 0.0,
            "quality": sc.get("quality", float("nan")) if bid in sample else float("nan"),
            "substituted": 1.0 if sc.get("substituted") else 0.0,
            "api_conformance": probes.get(bid, float("nan")) if bid in sample else float("nan"),
        })
    voids = {"slots": [list(s) for s in void_slots],
             "attempts": [{"blind_id": a["rec"]["blind_id"], "slot": list(a["label"]), "cause": cause}
                          for a, cause in res["void_attempts"]],
             "after_outcome": [{"blind_id": a["rec"]["blind_id"], "slot": list(a["label"])}
                               for a in res["after_outcome"]]}
    spans = []
    for a in attempts:
        m = a["man"] or {}
        try:
            spans.append((float(m["started_at"]), float(m["ended_at"])))
        except (KeyError, TypeError, ValueError):
            continue
    analysed = {r["blind_id"] for r in rows}
    return {"rows": rows, "voids": voids,
            "items": {bid: v["items"] for bid, v in scores.items()},
            "spans": spans,
            "ungraded": sorted(b for b in sample & analysed if b not in scores) if scores or results_dir else [],
            "sampled_void": sorted(sample - analysed)}
