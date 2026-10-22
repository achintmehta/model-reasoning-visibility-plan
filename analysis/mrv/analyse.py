"""The tests and intervals of protocol sections 8.1 to 8.4, per model (DESIGN.md sections 4 to 7).

Every function takes the run table (a list of dicts, see load.build_table) and returns plain
rows (lists of dicts), so that run_analysis.py can write them as CSV and as the report.

Each test and each bootstrap has its own random stream, derived from the analysis seed and a
label naming the model, the contrast, the measure and the analysis. The numbers therefore do
not depend on the order in which anything is computed.
"""
import math

import numpy as np

from . import config, record, stats

# The three behaviour measures of protocol section 6.1: (name, column, bootstrap kind, bounds).
# Units with a missing value are dropped, so `log_steps` keeps finished runs only and
# `quality` keeps sampled apps only.
BEHAVIOUR = (
    ("failure", "failed", "diff", (-config.EQUIV_FAILURE, config.EQUIV_FAILURE)),
    ("steps", "log_steps", "ratio_geo", config.EQUIV_STEPS),
    ("quality", "quality", "diff", None),
)

# The mechanism measures of protocol section 6.3, UNSEEN (a) against SEEN (b): (name, column,
# bootstrap kind, the direction of the registered alternative for b minus a).
MECHANISM = (
    ("H3", "reasoning_rate", "diff", "greater"),
    ("H4", "log_reasoning_median_chars", "ratio_geo", "less"),
    ("H5", "silent_turn", "diff", "less"),
)


# Columns that are a share of runs (0 or 1 per run). A difference between two of these shares
# gets Newcombe's interval, every other estimate the rescaled stratified bootstrap (DESIGN.md
# section 10 item 3).
SHARES = ("failed", "silent_turn")


class Settings:
    """Resampling sizes and the seed. The defaults are the registered ones (protocol section 8.1)."""

    def __init__(self, n_perm=config.N_PERM, n_boot=config.N_BOOT, seed=config.ANALYSIS_SEED):
        self.n_perm, self.n_boot, self.seed = n_perm, n_boot, seed

    def rng(self, label):
        return np.random.default_rng(config.seed_int(self.seed, label))


def arms_of(rows, model):
    present = {r["arm"] for r in rows if r["model"] == model}
    return [a for a in config.ARMS.get(model, ("off", "unseen", "seen")) if a in present]


def models_of(rows):
    seen = {r["model"] for r in rows}
    return [m for m in config.ARMS if m in seen] + sorted(seen - set(config.ARMS))


def _pick(rows, model, a, b, column, where=None):
    """(values, is_b, strata) for one contrast, from the rows of arms a and b of one model."""
    sel = [r for r in rows if r["model"] == model and r["arm"] in (a, b) and (where is None or where(r))]
    return ([float(r[column]) for r in sel], [r["arm"] == b for r in sel], [r["stratum"] for r in sel])


def _scale(kind):
    return "ratio" if kind.startswith("ratio") else "difference"


def estimate(rows, model, a, b, column, kind, st, label, where=None, test=None, value=None, test_id=None):
    """One contrast's estimate with its 95% and 90% intervals, and optionally its permutation
    test (test = "two-sided", "greater" or "less"). `value` rewrites a column's value per row
    (the sensitivity analysis that scores substituted apps 0). `label` names the random
    streams. `test_id` names the estimate in the intermediate record (default: the label)."""
    test_id = test_id or label
    sel = [r for r in rows if r["model"] == model and r["arm"] in (a, b) and (where is None or where(r))]
    vals = [value(r) for r in sel] if value is not None else [float(r[column]) for r in sel]
    is_b = [r["arm"] == b for r in sel]
    strata = [r["stratum"] for r in sel]
    v = np.asarray(vals, dtype=float)
    fb = np.asarray(is_b, dtype=bool)
    ok = ~np.isnan(v)
    out = {"test_id": test_id, "n_a": int((ok & ~fb).sum()), "n_b": int((ok & fb).sum()), "scale": _scale(kind)}
    out["mean_a"] = float(v[ok & ~fb].mean()) if out["n_a"] else float("nan")
    out["mean_b"] = float(v[ok & fb].mean()) if out["n_b"] else float("nan")
    detail = {"test_id": test_id, "model": model, "arm_a": a, "arm_b": b, "column": column, "kind": kind,
              "n_a": out["n_a"], "n_b": out["n_b"], "mean_a": out["mean_a"], "mean_b": out["mean_b"]}
    if column in SHARES and kind == "diff" and value is None:
        xa, xb = float(v[ok & ~fb].sum()), float(v[ok & fb].sum())
        out["estimate"] = out["mean_b"] - out["mean_a"] if out["n_a"] and out["n_b"] else float("nan")
        out["ci95_lo"], out["ci95_hi"] = stats.newcombe(xa, out["n_a"], xb, out["n_b"], 0.95)
        out["ci90_lo"], out["ci90_hi"] = stats.newcombe(xa, out["n_a"], xb, out["n_b"], 0.90)
        out["replicates"] = np.array([])
        out["interval"] = "newcombe"
        detail.update({"x_a": xa, "x_b": xb})
        for lev in (0.95, 0.90):
            parts = stats.newcombe_parts(xa, out["n_a"], xb, out["n_b"], lev)
            tag = "95" if lev == 0.95 else "90"
            detail.update({f"newcombe{tag}_{k}": v_ for k, v_ in parts.items() if k not in ("p_a", "p_b")})
    else:
        est, reps = stats.bootstrap(vals, is_b, strata, st.n_boot, st.rng(label + "|boot"), kind=kind)
        out["estimate"] = est
        out["ci95_lo"], out["ci95_hi"] = stats.percentile_ci(reps, 0.95)
        out["ci90_lo"], out["ci90_hi"] = stats.percentile_ci(reps, 0.90)
        out["replicates"] = reps
        out["interval"] = "bootstrap"
        fin = reps[np.isfinite(reps)] if reps.size else reps
        detail.update({"boot_stream": label + "|boot", "boot_seed": config.seed_int(st.seed, label + "|boot"),
                       "n_boot": st.n_boot, "replicates_finite": int(fin.size),
                       "replicates_mean": float(fin.mean()) if fin.size else float("nan"),
                       "replicates_sd": float(fin.std(ddof=1)) if fin.size > 1 else float("nan"),
                       "quantiles": "numpy.quantile (linear) at lo = (1 - level) / 2 and 1 - lo, in double precision"})
        record.series("bootstrap", test_id, reps)
    detail.update({"estimate": out["estimate"], "interval": out["interval"],
                   "ci95_lo": out["ci95_lo"], "ci95_hi": out["ci95_hi"],
                   "ci90_lo": out["ci90_lo"], "ci90_hi": out["ci90_hi"]})
    if test is not None:
        pd = {}
        _, p, _, _ = stats.perm_test(vals, is_b, strata, st.n_perm, st.rng(label + "|perm"), test, detail=pd)
        out["p"] = p
        detail.update({"alternative": test, "perm_stream": label + "|perm",
                       "perm_seed": config.seed_int(st.seed, label + "|perm"), "n_perm": st.n_perm,
                       "t_obs": pd.get("t_obs", float("nan")), "extreme": pd.get("extreme", ""),
                       "tolerance": pd.get("eps", float("nan")), "p": p})
        if "t_star" in pd:
            record.series("permutation", test_id, pd["t_star"])
    if record.active():
        record.add("test-detail", detail)
        for r, x, bb in zip(sel, vals, is_b):
            record.add("test-units", {"test_id": test_id, "blind_id": r["blind_id"], "model": model,
                                      "arm": r["arm"], "stratum": r["stratum"], "arm_b": 1 if bb else 0,
                                      "value": x, "used": 0 if x != x else 1})
        for sname in sorted(set(strata)):
            row = {"test_id": test_id, "stratum": sname}
            for arm_name, flag in (("a", False), ("b", True)):
                xs = v[ok & (fb == flag) & (np.asarray(strata, dtype=object) == sname)]
                row.update({f"n_{arm_name}": int(xs.size),
                            f"mean_{arm_name}": float(xs.mean()) if xs.size else float("nan"),
                            f"var_{arm_name}": float(xs.var(ddof=1)) if xs.size > 1 else float("nan")})
            record.add("test-strata", row)
    return out


def _x(row):
    """X of "changes nothing by more than X" (protocol section 8.2), on the measure's scale:
    points for a difference, a factor for a ratio."""
    lo, hi = row["ci90_lo"], row["ci90_hi"]
    if not (lo == lo and hi == hi):
        return float("nan")
    if row["scale"] == "ratio":
        return max(hi, 1.0 / lo) if lo > 0 else float("inf")
    return stats.largest_excluded((lo, hi))


def family(rows, model, name, a, b, st, tag, where=None, value=None, measures=BEHAVIOUR, label_tag=None):
    """H1 or H2 for one model: three tests, Holm within them, the verdicts of section 8.2.
    label_tag names the random streams (default: tag), so that a rerun can share the
    headline's streams."""
    out = []
    for measure, column, kind, bounds in measures:
        label = f"{label_tag or tag}|{model}|{name}|{measure}"
        e = estimate(rows, model, a, b, column, kind, st, label, where=where, test="two-sided",
                     value=value if measure == "quality" else None, test_id=f"{tag}|{model}|{name}|{measure}")
        out.append({"analysis": tag, "model": model, "family": name, "measure": measure,
                    "arm_a": a, "arm_b": b, "bounds": bounds, **e})
    adj = stats.holm([r["p"] for r in out])
    for r, pa in zip(out, adj):
        r["p_holm"] = float(pa)
        r["verdict"] = stats.verdict(r["p_holm"], (r["ci90_lo"], r["ci90_hi"]), r["bounds"], config.ALPHA)
        if r["n_a"] == 0 or r["n_b"] == 0:
            r["verdict"] = "no data"
        r["x"] = _x(r) if r["verdict"] != "different" else float("nan")
    _record_family(out, f"{tag}|{model}|{name}")
    return out


def _record_family(fam, family_id):
    """Holm step by step, and how each verdict was reached, into the intermediate record."""
    if not record.active():
        return
    for r, h in zip(fam, stats.holm_steps([r["p"] for r in fam])):
        record.add("holm", {"family_id": family_id, "test_id": r["test_id"], "measure": r["measure"],
                            "p": r["p"], "rank": h["rank"], "multiplier": h["multiplier"],
                            "product_capped_at_1": h["product"], "adjusted_running_max": h["adjusted"],
                            "p_holm": r["p_holm"]})
        bounds = r.get("bounds")
        lo, hi = r["ci90_lo"], r["ci90_hi"]
        if r["verdict"] == "no data":
            rule = "an arm has no units"
        elif r["p_holm"] < config.ALPHA:
            rule = f"p_holm < alpha ({config.ALPHA})"
        elif r["family"] == "H3-H5":
            rule = f"p_holm >= alpha ({config.ALPHA})"
        elif bounds is None:
            rule = f"p_holm >= alpha ({config.ALPHA}) and the measure has no equivalence bound"
        elif bounds[0] < lo and hi < bounds[1]:
            rule = f"p_holm >= alpha and the 90% interval lies inside ({bounds[0]}, {bounds[1]})"
        else:
            rule = f"p_holm >= alpha and the 90% interval is not inside ({bounds[0]}, {bounds[1]})"
        if r["verdict"] in ("different", "no data", "supported", "not supported"):
            xrule = ""
        elif r["scale"] == "ratio":
            xrule = "max(90% high, 1 / 90% low)"
        else:
            xrule = "max(|90% low|, |90% high|)"
        record.add("verdicts", {"test_id": r["test_id"], "family_id": family_id, "p_holm": r["p_holm"],
                                "alpha": config.ALPHA, "ci90_lo": lo, "ci90_hi": hi,
                                "bound_lo": bounds[0] if bounds else "", "bound_hi": bounds[1] if bounds else "",
                                "rule": rule, "verdict": r["verdict"], "x_rule": xrule, "x": r.get("x", float("nan"))})


def confirmatory(rows, st):
    """H1 and H2 (three measures each) and H3-H5, per model, with Holm within each family."""
    out = []
    for model in models_of(rows):
        arms = arms_of(rows, model)
        for name, a, b in config.CONTRASTS:
            if a in arms and b in arms:
                out += family(rows, model, name, a, b, st, "confirmatory")
        if "unseen" in arms and "seen" in arms:
            out += mechanism(rows, model, st, "confirmatory")
    return out


def mechanism(rows, model, st, tag):
    """H3-H5 for one model: three one-sided tests, Holm within them."""
    fam = []
    for name, column, kind, alt in MECHANISM:
        e = estimate(rows, model, "unseen", "seen", column, kind, st, f"{tag}|{model}|{name}", test=alt,
                     test_id=f"{tag}|{model}|H3-H5|{name}")
        fam.append({"analysis": tag, "model": model, "family": "H3-H5", "measure": name,
                    "arm_a": "unseen", "arm_b": "seen", "bounds": None, "alternative": alt, **e})
    adj = stats.holm([r["p"] for r in fam])
    for r, pa in zip(fam, adj):
        r["p_holm"] = float(pa)
        r["verdict"] = ("no data" if (r["n_a"] == 0 or r["n_b"] == 0) else
                        "supported" if pa == pa and pa < config.ALPHA else "not supported")
        r["x"] = float("nan")
    _record_family(fam, f"{tag}|{model}|H3-H5")
    return fam


def sensitivity(rows, st):
    """Protocol section 8.3: H1 on runs with no nudge (all three measures), and H1 and H2
    quality with every substituted app scored 0. The no-nudge rerun is Holm-corrected within
    its own three tests. The substituted-0 quality test shares the headline's random streams,
    so its failure and steps tests are the headline's own, and its p is Holm-corrected with
    the headline family's failure and steps p values. Both are reported beside the headline,
    outside the confirmatory families."""
    out = []
    for model in models_of(rows):
        arms = arms_of(rows, model)
        if "unseen" in arms and "seen" in arms:
            out += family(rows, model, "H1", "unseen", "seen", st, "no-nudge",
                           where=lambda r: r["nudged"] == 0.0)
        for name, a, b in config.CONTRASTS:
            if a in arms and b in arms:
                fam = family(rows, model, name, a, b, st, "substituted-0", label_tag="confirmatory",
                              value=lambda r: (0.0 if r["substituted"] == 1.0 else r["quality"])
                              if r["quality"] == r["quality"] else float("nan"))
                out += [r for r in fam if r["measure"] == "quality"]
    return out


def difference(e1, e2, kind, column, test_id=None):
    """The first estimate minus the second (their ratio for a ratio), with a 95% interval: the
    two estimates' Newcombe intervals combined by MOVER for a share, otherwise the percentile
    interval of the difference (or ratio) of their bootstrap replicates, which are independent
    draws. Returns (estimate, low, high, method, replicates)."""
    r1, r2 = e1["replicates"], e2["replicates"]
    n = min(r1.size, r2.size)
    if column in SHARES:
        d = e1["estimate"] - e2["estimate"]
        lo, hi = stats.mover_diff(e1["estimate"], (e1["ci95_lo"], e1["ci95_hi"]),
                                  e2["estimate"], (e2["ci95_lo"], e2["ci95_hi"]))
        method, reps = "newcombe (MOVER)", np.array([])
    else:
        if kind.startswith("ratio"):
            d = e1["estimate"] / e2["estimate"] if e2["estimate"] else float("nan")
            reps = r1[:n] / r2[:n]
        else:
            d = e1["estimate"] - e2["estimate"]
            reps = r1[:n] - r2[:n]
        lo, hi = stats.percentile_ci(reps, 0.95)
        method = "bootstrap"
    if test_id and record.active():
        record.add("test-detail", {"test_id": test_id, "kind": kind, "column": column,
                                   "of_first": e1["test_id"], "of_second": e2["test_id"],
                                   "combined": "ratio of the two" if kind.startswith("ratio") and column not in SHARES
                                   else "first minus second",
                                   "estimate": d, "interval": method, "ci95_lo": lo, "ci95_hi": hi,
                                   "first_estimate": e1["estimate"], "first_ci95_lo": e1["ci95_lo"],
                                   "first_ci95_hi": e1["ci95_hi"], "second_estimate": e2["estimate"],
                                   "second_ci95_lo": e2["ci95_lo"], "second_ci95_hi": e2["ci95_hi"],
                                   "n_boot": int(reps.size) if reps.size else ""})
        if reps.size:
            record.series("bootstrap", test_id, reps)
    return d, lo, hi, method, reps


def exploratory(rows, st):
    """Protocol section 8.4 and section 6.2: intervals, no tests."""
    out = []
    models = models_of(rows)
    for model in models:
        arms = arms_of(rows, model)
        for name, a, b in config.CONTRASTS:
            if not (a in arms and b in arms):
                continue
            # Visibility without verification: H1 inside no_verification and inside the two
            # feedback conditions (protocol section 8.4). Reported for H1 only.
            # Each block's estimate, and the no_verification block's minus the feedback
            # block's (a ratio of ratios for steps), from the two blocks' own replicates.
            if name == "H1":
                for measure, column, kind, _ in BEHAVIOUR:
                    blocks = {}
                    for block, conds in (("no_verification", ("no_verification",)),
                                         ("feedback", config.FEEDBACK_CONDITIONS)):
                        e = estimate(rows, model, a, b, column, kind, st,
                                     f"verification|{model}|{name}|{block}|{measure}",
                                     where=lambda r, c=conds: r["condition"] in c)
                        blocks[block] = e
                        out.append({"analysis": f"verification:{block}", "model": model,
                                    "family": name, "measure": measure, "arm_a": a, "arm_b": b, **e})
                    tid = f"verification-difference|{model}|{name}|{measure}"
                    d, lo, hi, method, reps = difference(blocks["no_verification"], blocks["feedback"], kind, column, tid)
                    out.append({"test_id": tid, "analysis": "verification:difference", "model": model, "family": name,
                                "measure": measure, "arm_a": a, "arm_b": b, "scale": _scale(kind),
                                "estimate": d, "ci95_lo": lo, "ci95_hi": hi,
                                "n_a": blocks["no_verification"]["n_a"] + blocks["feedback"]["n_a"],
                                "n_b": blocks["no_verification"]["n_b"] + blocks["feedback"]["n_b"],
                                "interval": method, "replicates": reps})
            # Quality over the finished runs' apps only (protocol section 6.1: steps and
            # quality are read beside failure, never alone).
            e = estimate(rows, model, a, b, "quality", "diff", st, f"quality-finished|{model}|{name}",
                         where=lambda r: r["failed"] == 0.0)
            out.append({"analysis": "quality:finished", "model": model, "family": name,
                        "measure": "quality", "arm_a": a, "arm_b": b, **e})
            # API conformance (protocol section 6.5).
            e = estimate(rows, model, a, b, "api_conformance", "diff", st, f"api|{model}|{name}")
            out.append({"analysis": "api-conformance", "model": model, "family": name,
                        "measure": "api_conformance", "arm_a": a, "arm_b": b, **e})
            # Cost (protocol section 6.2): ratio of mean tokens, all runs and finished runs.
            for subset, where in (("all", None), ("finished", lambda r: r["failed"] == 0.0)):
                e = estimate(rows, model, a, b, "tokens_total", "ratio_of_means", st,
                             f"cost|{model}|{name}|{subset}", where=where)
                out.append({"analysis": f"cost:{subset}", "model": model, "family": name,
                            "measure": "tokens_total", "arm_a": a, "arm_b": b, **e})
    # The within-lab pairs (protocol section 8.4): each twin's estimate, each sibling's, and
    # their difference (a ratio of ratios for steps), each model bootstrapped on its own. The
    # twin's and the sibling's estimates reuse the confirmatory random streams, so they are
    # the confirmatory estimates and intervals exactly.
    for twin, sib in config.TWINS:
        if twin not in models or sib not in models:
            continue
        for name, a, b in config.CONTRASTS:
            if not all(x in arms_of(rows, m) for m in (twin, sib) for x in (a, b)):
                continue
            for measure, column, kind, _ in BEHAVIOUR:
                et = estimate(rows, twin, a, b, column, kind, st, f"confirmatory|{twin}|{name}|{measure}",
                              test_id=f"pair:twin|{twin}|{name}|{measure}")
                es = estimate(rows, sib, a, b, column, kind, st, f"confirmatory|{sib}|{name}|{measure}",
                              test_id=f"pair:sibling|{sib}|{name}|{measure}")
                tid = f"pair:twin-minus-sibling|{twin} vs {sib}|{name}|{measure}"
                d, lo, hi, method, reps = difference(et, es, kind, column, tid)
                for who, e in (("twin", et), ("sibling", es)):
                    out.append({"analysis": f"pair:{who}", "model": twin if who == "twin" else sib,
                                "family": name, "measure": measure, "arm_a": a, "arm_b": b, **e})
                out.append({"test_id": tid, "analysis": "pair:twin-minus-sibling", "model": f"{twin} vs {sib}",
                            "family": name, "measure": measure, "arm_a": a, "arm_b": b,
                            "scale": _scale(kind), "estimate": d, "ci95_lo": lo, "ci95_hi": hi,
                            "n_a": et["n_a"] + es["n_a"], "n_b": et["n_b"] + es["n_b"],
                            "interval": method, "replicates": reps})
    return out


COLUMNS = ("test_id", "analysis", "model", "family", "measure", "arm_a", "arm_b", "n_a", "n_b", "mean_a",
           "mean_b", "scale", "estimate", "ci95_lo", "ci95_hi", "ci90_lo", "ci90_hi",
           "interval", "alternative", "p", "p_holm", "verdict", "x")


def flat(rows):
    """Result rows without the bootstrap replicates, every column present, for the CSV."""
    out = []
    for r in rows:
        out.append({c: r.get(c, "") for c in COLUMNS})
    return out


def run_all(rows, st=None):
    st = st or Settings()
    return {"confirmatory": confirmatory(rows, st), "sensitivity": sensitivity(rows, st),
            "exploratory": exploratory(rows, st)}
