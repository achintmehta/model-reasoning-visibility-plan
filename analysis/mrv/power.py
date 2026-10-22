"""Power, recomputed under the exact tests of the analysis (protocol section 7, DESIGN.md section 8).

Each simulated grid is one model's two arms: 20 runs per task x condition stratum per arm (120 a
side) and 10 sampled apps per stratum per arm (60 a side). Its run table is passed to the same
functions the analysis uses (analyse.family and analyse.mechanism), so the permutation tests,
Holm's correction, the bootstrap intervals and the verdicts are exactly those of the analysis.
Only the resampling sizes are smaller (2,000 each, DESIGN.md section 10 item 5).

Scenarios follow protocol section 7. The data are simple on purpose: failures are Bernoulli,
log steps are normal, quality scores are normal with the training rounds' spread (SD 41 points)
and per-run reasoning measures are drawn around the scenario's values. Each scenario reports
the share of grids in which each test rejects (or each verdict is reached) with its Monte Carlo
standard error.
"""
import math
import time

import numpy as np

from . import analyse, config

STRATA = [f"{t}|{c}" for t in config.TASKS for c in config.CONDITIONS]
QUALITY_SD = 41.0
STEPS_SD = 0.5           # SD of log steps (a scale only: shifts are given in SD units)


def arm_params(**kw):
    p = {"p_fail": 0.02, "steps_shift_sd": 0.0, "quality_mean": 50.0, "rate": 0.9, "rate_sd": 0.05,
         "log_med": math.log(300.0), "log_med_sd": 0.6, "p_silent": 0.05}
    p.update(kw)
    return p


def simulate(a, b, rng, model="sim", arms=("unseen", "seen"), per_stratum=config.REPLICATES,
             sampled_per_stratum=config.QUALITY_PER_CELL):
    """One simulated grid's run table for one model and two arms."""
    rows = []
    for arm, p in zip(arms, (a, b)):
        for s in STRATA:
            task, cond = s.split("|")
            sampled = np.zeros(per_stratum, dtype=bool)
            sampled[rng.choice(per_stratum, size=sampled_per_stratum, replace=False)] = True
            for i in range(per_stratum):
                failed = rng.random() < p["p_fail"]
                log_steps = math.log(60.0) + STEPS_SD * (p["steps_shift_sd"] + rng.normal())
                rate = min(1.0, max(0.0, rng.normal(p["rate"], p["rate_sd"])))
                n = 60
                k = int(rng.binomial(n, rate))
                med = float(np.exp(rng.normal(p["log_med"], p["log_med_sd"]))) if k else float("nan")
                rows.append({
                    "model": model, "arm": arm, "task": task, "condition": cond, "stratum": s,
                    "failed": 1.0 if failed else 0.0,
                    "log_steps": float("nan") if failed else log_steps,
                    "quality": float(rng.normal(p["quality_mean"], QUALITY_SD)) if sampled[i] else float("nan"),
                    "reasoning_rate": k / n,
                    "log_reasoning_median_chars": math.log(med) if k else float("nan"),
                    "silent_turn": 1.0 if rng.random() < p["p_silent"] else 0.0,
                    "nudged": 0.0, "substituted": 0.0,
                })
    return rows


# Protocol section 7's scenarios, plus a null (test 1 of DESIGN.md section 9.2) and H3-H5 at
# effects of the size the pilot reported in protocol section 1.3. (name, arm a, arm b, what to count)
def scenarios():
    q = QUALITY_SD
    base = arm_params()
    out = [("null: all measures equal", base, base, "behaviour")]
    for pb in (0.10, 0.15, 0.20):
        out.append((f"failure 2% vs {int(pb * 100)}%", base, arm_params(p_fail=pb), "behaviour"))
    for d in (0.3, 0.4, 0.5):
        out.append((f"steps shift {d} SD", base, arm_params(steps_shift_sd=d), "behaviour"))
    for d in (0.5, 0.6, 0.7):
        out.append((f"quality shift {d} SD ({d * q:.0f} points)", base,
                    arm_params(quality_mean=50.0 + d * q), "behaviour"))
    for pf in (0.02, 0.05):
        out.append((f"equivalence: both arms at {int(pf * 100)}% failure, steps ratio 1",
                    arm_params(p_fail=pf), arm_params(p_fail=pf), "behaviour"))
    out.append(("mechanism null", base, base, "mechanism"))
    out.append(("H3: reasoning rate 0.90 vs 0.97", arm_params(rate=0.90), arm_params(rate=0.97), "mechanism"))
    out.append(("H4: median reasoning chars ratio 0.8", base,
                arm_params(log_med=math.log(300.0 * 0.8)), "mechanism"))
    out.append(("H5: silent turn 10% vs 2%", arm_params(p_silent=0.10), arm_params(p_silent=0.02), "mechanism"))
    return out


def run_scenario(name, a, b, kind, n_grids, settings, seed_label=""):
    """The share of n_grids simulated grids reaching each verdict, per measure."""
    rng = np.random.default_rng(config.seed_int(settings.seed, f"power|{name}|{seed_label}"))
    counts = {}
    any_rejected = 0
    t0 = time.time()
    for g in range(n_grids):
        rows = simulate(a, b, rng)
        st = analyse.Settings(settings.n_perm, settings.n_boot, f"{settings.seed}:{name}:{g}")
        if kind == "behaviour":
            fam = analyse.family(rows, "sim", "H1", "unseen", "seen", st, "power")
        else:
            fam = analyse.mechanism(rows, "sim", st, "power")
        rejected = False
        for r in fam:
            c = counts.setdefault(r["measure"], {})
            c[r["verdict"]] = c.get(r["verdict"], 0) + 1
            rejected = rejected or r["verdict"] in ("different", "supported")
        any_rejected += rejected
    out = []
    for measure, c in counts.items():
        for v, k in sorted(c.items()):
            share = k / n_grids
            out.append({"scenario": name, "measure": measure, "verdict": v, "share": share,
                        "mc_se": math.sqrt(share * (1 - share) / n_grids), "grids": n_grids})
    share = any_rejected / n_grids
    out.append({"scenario": name, "measure": "family", "verdict": "any rejection", "share": share,
                "mc_se": math.sqrt(share * (1 - share) / n_grids), "grids": n_grids})
    for r in out:
        r["seconds"] = round(time.time() - t0, 1)
    return out


def run(n_grids=2000, n_perm=2000, n_boot=2000, only=None):
    st = analyse.Settings(n_perm, n_boot)
    out = []
    for name, a, b, kind in scenarios():
        if only and not any(o == name for o in only):
            continue
        out += run_scenario(name, a, b, kind, n_grids, st)
    return out


# ---------------------------------------------------------------- interval coverage

def coverage_scenarios():
    """Failure rates at and near 0, where a percentile interval is most at risk (DESIGN.md
    section 10 item 3), and the steps and quality intervals at the design's sizes."""
    out = []
    for pa, pb in ((0.0, 0.02), (0.01, 0.01), (0.02, 0.02), (0.02, 0.05), (0.05, 0.05), (0.02, 0.10), (0.10, 0.10)):
        out.append((f"failure {pa:.0%} vs {pb:.0%}", arm_params(p_fail=pa), arm_params(p_fail=pb)))
    out.append(("steps ratio 1.22 (0.4 SD)", arm_params(), arm_params(steps_shift_sd=0.4)))
    out.append(("quality shift 24 points", arm_params(), arm_params(quality_mean=74.0)))
    return out


def true_values(a, b):
    return {"failure": b["p_fail"] - a["p_fail"],
            "steps": math.exp(STEPS_SD * (b["steps_shift_sd"] - a["steps_shift_sd"])),
            "quality": b["quality_mean"] - a["quality_mean"]}


def coverage(n_grids=2000, n_boot=2000, seed=config.ANALYSIS_SEED, only=None):
    """How often the 95% and 90% percentile intervals cover the planted value."""
    out = []
    for name, a, b in coverage_scenarios():
        if only and not any(o == name for o in only):
            continue
        rng = np.random.default_rng(config.seed_int(seed, f"coverage|{name}"))
        truth = true_values(a, b)
        hits = {m: [0, 0, 0] for m in truth}
        for g in range(n_grids):
            rows = simulate(a, b, rng)
            st = analyse.Settings(0, n_boot, f"{seed}:coverage:{name}:{g}")
            for measure, column, kind, _ in analyse.BEHAVIOUR:
                e = analyse.estimate(rows, "sim", "unseen", "seen", column, kind, st, f"cov|{measure}")
                t = truth[measure]
                h = hits[measure]
                h[0] += e["ci95_lo"] <= t <= e["ci95_hi"]
                h[1] += e["ci90_lo"] <= t <= e["ci90_hi"]
                h[2] += 1
        for m, (c95, c90, n) in hits.items():
            out.append({"scenario": name, "measure": m, "true_value": truth[m], "grids": n,
                        "coverage95": c95 / n, "coverage90": c90 / n,
                        "mc_se95": math.sqrt((c95 / n) * (1 - c95 / n) / n)})
    return out
