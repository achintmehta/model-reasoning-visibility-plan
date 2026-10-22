"""The descriptives of protocol section 6.4, the cost, compute and energy of section 6.2, the
void counts of section 9 and the registered shapes of section 1.3: per model x arm, reported
and never tested (DESIGN.md section 7).
"""
import math
import statistics
from collections import Counter, defaultdict

import numpy as np

from . import config, record, stats
from .analyse import arms_of, models_of

# The statuses a run can end with, in the order they are printed (config.STATUSES).
STATUSES = config.STATUSES

# Per-run quantities summarised per model x arm, each as a mean with a 95% stratified-bootstrap
# interval: (column, what it is, protocol section).
WITH_INTERVALS = (
    ("failed", "share of runs not finished", "6.1"),
    ("steps", "steps per run", "6.1"),
    ("reasoning_rate", "share of steps with reasoning", "6.3, 6.4 (3)"),
    ("reasoning_chars_per_step", "reasoning characters per step", "6.4 (2)"),
    ("replayed_turns", "turns of reasoning replayed (SEEN)", "6.4 (2)"),
    ("replayed_chars", "characters of reasoning replayed (SEEN)", "6.4 (2)"),
    ("call_as_text_steps", "tool calls written as text, per run", "6.4 (4)"),
    ("silent_turns", "silent turns per run", "6.4 (5)"),
    ("prose_turns", "turns of prose alone per run", "6.4 (5)"),
    ("finish_nudges", "finish nudges per run", "6.4 (5)"),
    ("nudged", "share of runs nudged", "8.3"),
    ("self_check", "share of runs checking their own work (feedback conditions)", "6.4 (6)"),
    ("file_state_count", "file-state notes per run", "6.4 (7)"),
    ("file_state_writes", "of them, on writes", "6.4 (7)"),
    ("file_state_edits", "of them, on edits", "6.4 (7)"),
    ("file_state_reverts", "reverts per run", "6.4 (7)"),
    ("file_state_max_times", "most calls leaving one file with one content", "6.4 (7)"),
    ("max_prompt_tokens", "largest prompt of the run (tokens)", "6.4 (9)"),
    ("machine_s", "machine time per run (seconds)", "6.2, 6.4 (10)"),
    ("tokens_total", "tokens per run", "6.2"),
    ("quality", "quality score (sampled apps)", "6.1"),
    ("api_conformance", "API conformance (sampled apps)", "6.5"),
)

# The quantities above that are a share of runs (0 or 1 per run): a Wilson interval, not the
# bootstrap. Status shares and the canary share below are shares too.
SHARE_COLUMNS = ("failed", "nudged", "self_check")

GEMMA_WINDOW = 65536


def _cells(rows):
    out = defaultdict(list)
    for r in rows:
        out[(r["model"], r["arm"])].append(r)
    return out


def _mean_ci(sel, column, rng, n_boot, share=False, rid=None):
    """A mean and its 95% interval: Wilson's for a share of runs (share=True), the rescaled
    stratified bootstrap otherwise. The bootstrap replicates go to the intermediate record
    under `rid`."""
    vals = [float(r[column]) for r in sel]
    known = [v for v in vals if v == v]
    n = len(known)
    if share and n:
        lo, hi = stats.wilson(sum(known), n, 0.95)
        return n, sum(known) / n, lo, hi
    m, reps = stats.boot_mean(vals, [r["stratum"] for r in sel], n_boot, rng)
    lo, hi = stats.percentile_ci(reps, 0.95)
    if rid:
        record.series("describe", rid, reps)
    return n, m, lo, hi


def per_cell(rows, st):
    """One row per model x arm x quantity: n, mean and the 95% interval, plus each terminal
    status's share (the registered shapes of section 1.3 are among these)."""
    out = []
    cells = _cells(rows)
    for model in models_of(rows):
        for arm in arms_of(rows, model):
            sel = cells[(model, arm)]
            for col, what, sec in WITH_INTERVALS:
                rid = f"describe|{model}|{arm}|{col}"
                n, m, lo, hi = _mean_ci(sel, col, st.rng(rid), st.n_boot, share=col in SHARE_COLUMNS, rid=rid)
                out.append({"id": rid, "interval": "wilson" if col in SHARE_COLUMNS else "bootstrap", "model": model, "arm": arm, "quantity": col, "what": what,
                            "protocol": sec, "n": n, "mean": m, "ci95_lo": lo, "ci95_hi": hi})
            statuses = Counter(r["status"] for r in sel)
            for s in list(STATUSES) + sorted(set(statuses) - set(STATUSES)):
                ind = [dict(r, _s=1.0 if r["status"] == s else 0.0) for r in sel]
                n, m, lo, hi = _mean_ci(ind, "_s", st.rng(f"describe|{model}|{arm}|status|{s}"), st.n_boot, share=True)
                out.append({"interval": "wilson", "model": model, "arm": arm, "quantity": f"status:{s}",
                            "what": f"share of runs ending {s}", "protocol": "6.4 (1)",
                            "n": n, "mean": m, "ci95_lo": lo, "ci95_hi": hi})
            for g, c in sorted(Counter(r["loop_guard"] for r in sel if r["loop_guard"]).items()):
                out.append({"model": model, "arm": arm, "quantity": f"loop_guard:{g}",
                            "what": "runs ended by this loop guard", "protocol": "6.4 (1)",
                            "n": len(sel), "mean": c, "ci95_lo": "", "ci95_hi": ""})
            # Reasoning in OFF by the canary's rule (gate G2: a step over OFF_MAX characters,
            # budget reports not counted), beside the plain share of steps with reasoning above.
            ind = [dict(r, _c=1.0 if r["canary_steps_over"] > 0 else 0.0) for r in sel
                   if r["canary_steps_over"] == r["canary_steps_over"]]
            n, m, lo, hi = _mean_ci(ind, "_c", None, st.n_boot, share=True)
            out.append({"interval": "wilson", "model": model, "arm": arm, "quantity": "canary:runs_over",
                        "what": "share of runs with a reasoning step over 200 characters by the OFF canary's rule",
                        "protocol": "6.4 (3)", "n": n, "mean": m, "ci95_lo": lo, "ci95_hi": hi})
            longest = [r["canary_longest_chars"] for r in sel if r["canary_longest_chars"] == r["canary_longest_chars"]]
            out.append({"model": model, "arm": arm, "quantity": "canary:longest",
                        "what": "longest reasoning step in the arm by the OFF canary's rule (characters)",
                        "protocol": "6.4 (3)", "n": len(longest), "mean": max(longest) if longest else float("nan"),
                        "ci95_lo": "", "ci95_hi": ""})
            thinking = [r["reasoning_median_chars"] for r in sel if r["reasoning_median_chars"] == r["reasoning_median_chars"]]
            out.append({"model": model, "arm": arm, "quantity": "median_of_run_medians",
                        "what": "median over runs of the run's median reasoning characters (H4)",
                        "protocol": "6.3", "n": len(thinking),
                        "mean": statistics.median(thinking) if thinking else float("nan"),
                        "ci95_lo": "", "ci95_hi": ""})
            if model.startswith("gemma-q4"):
                near = sum(1 for r in sel if r["max_prompt_tokens"] == r["max_prompt_tokens"]
                           and r["max_prompt_tokens"] >= 0.9 * GEMMA_WINDOW)
                out.append({"model": model, "arm": arm, "quantity": "within_10pct_of_window",
                            "what": "runs whose largest prompt came within 10% of the 65,536-token window",
                            "protocol": "6.4 (9)", "n": len(sel), "mean": near, "ci95_lo": "", "ci95_hi": ""})
    return out


def voids(void_info, rows, sampled_void=()):
    """Protocol section 9 and section 6.4 (8): void attempts by cause, and empty slots, per
    model x arm. Counted over attempts, not slots. Also the void attempts that fell in the
    quality sample (DESIGN.md section 10 item 6)."""
    out = []
    tally = Counter()
    in_sample = Counter()
    sv = set(sampled_void)
    for a in void_info["attempts"]:
        if a["blind_id"] in sv:
            in_sample[(a["slot"][0], a["slot"][3])] += 1
    for a in void_info["attempts"]:
        model, _, _, arm, _ = a["slot"]
        tally[(model, arm, a["cause"])] += 1
    analysed = Counter((r["model"], r["arm"]) for r in rows)
    empty = Counter((s[0], s[3]) for s in void_info["slots"])
    keys = sorted(set(analysed) | set(empty) | {(m, a) for m, a, _ in tally})
    for model, arm in keys:
        causes = {c: n for (m, a, c), n in tally.items() if m == model and a == arm}
        attempts = analysed[(model, arm)] + sum(causes.values())
        out.append({"model": model, "arm": arm, "analysed_runs": analysed[(model, arm)],
                    "void_attempts": sum(causes.values()), "attempts": attempts,
                    "void_rate": (sum(causes.values()) / attempts) if attempts else float("nan"),
                    "empty_slots": empty[(model, arm)],
                    "void_in_quality_sample": in_sample[(model, arm)],
                    "causes": ", ".join(f"{c}: {n}" for c, n in sorted(causes.items())) or "none"})
    return out


def items(rows, item_results):
    """Protocol section 6.4 (11): the share of sampled apps passing each rubric item, per model x
    arm, launch items first. Skipped items are left out of the share."""
    out = []
    by_cell = defaultdict(list)
    for r in rows:
        if r["sampled"] == 1.0 and r["blind_id"] in item_results:
            by_cell[(r["model"], r["task"], r["arm"])].append(item_results[r["blind_id"]])
    for (model, task, arm), sheets in sorted(by_cell.items()):
        ids = sorted({i for s in sheets for i in s}, key=lambda i: (0 if "-L" in i else 1, i))
        for i in ids:
            res = [s.get(i) for s in sheets if s.get(i) in ("pass", "fail")]
            out.append({"model": model, "task": task, "arm": arm, "item": i, "n": len(res),
                        "share_pass": (sum(1 for x in res if x == "pass") / len(res)) if res else float("nan")})
    return out


def compute(rows, starts_ends):
    """Protocol section 6.2: machine time, GPU compute and energy summed per model x arm, per
    model and over the grid. Energy for a run outside every power log is bounded by the board's
    300 W limit, and those runs are counted. `starts_ends` is every attempt's (start, end), void
    ones included, for the time between runs."""
    out = []

    def add(scope, sel):
        logged = [r for r in sel if r["energy_wh"] == r["energy_wh"]]
        bound = [r for r in sel if r["energy_wh"] != r["energy_wh"] and r["machine_s"] == r["machine_s"]]
        out.append({
            "scope": scope, "runs": len(sel),
            "machine_h": sum(r["machine_s"] for r in sel if r["machine_s"] == r["machine_s"]) / 3600.0,
            "gpu_h": sum(r["gpu_s"] for r in sel if r["gpu_s"] == r["gpu_s"]) / 3600.0,
            "energy_kwh_logged": sum(r["energy_wh"] for r in logged) / 1000.0,
            "runs_with_power_log": len(logged),
            "energy_kwh_bound_unlogged": sum(r["machine_s"] for r in bound) * config.BOARD_POWER_LIMIT_W / 3.6e6,
            "runs_without_power_log": len(bound),
            "tokens": sum(r["tokens_total"] for r in sel if r["tokens_total"] == r["tokens_total"]),
        })
    cells = _cells(rows)
    for model in models_of(rows):
        for arm in arms_of(rows, model):
            add(f"{model}/{arm}", cells[(model, arm)])
        add(f"{model}/all", [r for r in rows if r["model"] == model])
    add("grid", rows)
    # Time between runs: the gaps between one attempt's end and the next one's start. Gaps
    # of an hour or more are taken as the breaks between batches and counted apart.
    se = sorted((s, e) for s, e in starts_ends if s == s and e == e)
    gaps = [b[0] - a[1] for a, b in zip(se, se[1:]) if b[0] > a[1]]
    inside = [g for g in gaps if g < 3600]
    out.append({"scope": "between runs (gaps under an hour)", "runs": len(inside),
                "machine_h": sum(inside) / 3600.0, "gpu_h": "", "energy_kwh_logged": "",
                "runs_with_power_log": "", "energy_kwh_bound_unlogged": "",
                "runs_without_power_log": "", "tokens": ""})
    out.append({"scope": "breaks between batches (gaps of an hour or more)",
                "runs": len(gaps) - len(inside), "machine_h": "", "gpu_h": "",
                "energy_kwh_logged": "", "runs_with_power_log": "", "energy_kwh_bound_unlogged": "",
                "runs_without_power_log": "", "tokens": ""})
    return out
