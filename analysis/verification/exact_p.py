#!/usr/bin/env python3
"""Exact permutation p values for the small verification grid, written separately from the
analysis code (it imports nothing from mrv/).

A stratified permutation test relabels the arms within each task x condition stratum, keeping
each stratum's number of arm-b units. With two runs per cell there are few enough relabellings
to count them all. The statistic is mean(b) - mean(a). With the totals fixed it rises with the
sum of the b units' values, so the exact distribution of that sum (the product, over strata, of
every way to choose the stratum's b units) gives the exact p value.

    python3 exact_p.py run-table.csv tests.csv > exact-p.csv
tests.csv: the analysis's confirmatory.csv and sensitivity.csv rows.
"""
import csv
import itertools
import math
import sys
from collections import defaultdict

COLUMN = {"failure": "failed", "steps": "steps", "quality": "quality", "H3": "reasoning_rate",
          "H4": "reasoning_median_chars", "H5": "silent_turn"}


def value(r, measure, analysis):
    """The unit's value for a test, recomputed from the run table's basic columns."""
    if measure == "failure":
        return 0.0 if r["status"] == "finished" else 1.0
    if measure == "steps":
        return math.log(float(r["steps"])) if r["status"] == "finished" else None
    if measure == "quality":
        if r["sampled"] != "1" or r["quality"] == "":
            return None
        if analysis == "substituted-0" and r["substituted"] == "1":
            return 0.0
        return float(r["quality"])
    if measure == "H4":
        x = r["reasoning_median_chars"]
        return math.log(float(x)) if x not in ("", "0") else None
    x = r[COLUMN[measure]]
    return float(x) if x != "" else None


def exact_p(units, alternative):
    """units: list of (stratum, is_b, value). Returns (exact p, number of relabellings)."""
    by = defaultdict(list)
    for s, b, v in units:
        by[s].append((b, v))
    dist = {0.0: 1}
    total = 0
    for s, xs in by.items():
        k, m = len(xs), sum(1 for b, _ in xs if b)
        vals = [v for _, v in xs]
        local = defaultdict(int)
        for combo in itertools.combinations(range(k), m):
            local[round(sum(vals[i] for i in combo), 9)] += 1
        new = defaultdict(int)
        for a, ca in dist.items():
            for b, cb in local.items():
                new[round(a + b, 9)] += ca * cb
        dist = new
    nb = sum(1 for _, b, _ in units if b)
    na = len(units) - nb
    T = sum(v for _, _, v in units)
    sb = sum(v for _, b, v in units if b)
    t = lambda S: S / nb - (T - S) / na
    t_obs = t(sb)
    eps = 1e-9 * max(1.0, abs(t_obs))
    n_all = sum(dist.values())
    if alternative == "greater":
        hit = sum(c for S, c in dist.items() if t(S) >= t_obs - eps)
    elif alternative == "less":
        hit = sum(c for S, c in dist.items() if t(S) <= t_obs + eps)
    else:
        hit = sum(c for S, c in dist.items() if abs(t(S)) >= abs(t_obs) - eps)
    return hit / n_all, n_all


def main():
    rows = list(csv.DictReader(open(sys.argv[1])))
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(["analysis", "model", "family", "measure", "arm_a", "arm_b", "n_a", "n_b", "relabellings", "exact_p"])
    for path in sys.argv[2:]:
        for t in csv.DictReader(open(path)):
            alt = t["alternative"] or "two-sided"
            units = []
            for r in rows:
                if r["model"] != t["model"] or r["arm"] not in (t["arm_a"], t["arm_b"]):
                    continue
                if t["analysis"] == "no-nudge" and r["nudged"] != "0":
                    continue
                v = value(r, t["measure"], t["analysis"])
                if v is None:
                    continue
                units.append((r["task"] + "|" + r["condition"], r["arm"] == t["arm_b"], v))
            p, n = exact_p(units, alt)
            w.writerow([t["analysis"], t["model"], t["family"], t["measure"], t["arm_a"], t["arm_b"],
                        sum(1 for u in units if not u[1]), sum(1 for u in units if u[1]), n, f"{p:.6g}"])


if __name__ == "__main__":
    main()
