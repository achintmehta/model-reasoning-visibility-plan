#!/usr/bin/env python3
"""The comparison behind DESIGN.md section 10 item 3: how often four interval methods cover the
planted value on simulated grids of the design's size (power.simulate).

    python3 power-results/compare_intervals.py [GRIDS] > power-results/interval-comparison.txt

Methods: the plain percentile bootstrap (stratified), the same with each stratum rescaled by
sqrt(k / (k - 1)), BCa (bias correction and a jackknife acceleration) on the plain bootstrap,
and, for failure, Newcombe's hybrid score interval. 2,000 resamples per interval, the analysis
seed. This script is the evidence for the decision and is not used by the analysis.
"""
import math
import sys
import time
from pathlib import Path
from statistics import NormalDist

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mrv import analyse, config, power, stats  # noqa: E402

ND = NormalDist()


def boot_arm(v, s, n, rng, rescale):
    total = np.zeros(n)
    for idx in stats._groups(s):
        x = v[idx]
        k = x.size
        m = x[rng.integers(0, k, size=(n, k))].mean(axis=1)
        if rescale and k > 1:
            m = x.mean() + math.sqrt(k / (k - 1)) * (m - x.mean())
        total += m * k
    return total / v.size


def jack_accel(v, b):
    ests = []
    for i in range(v.size):
        keep = np.ones(v.size, bool)
        keep[i] = False
        ests.append(v[keep & b].mean() - v[keep & ~b].mean())
    e = np.array(ests)
    d = e.mean() - e
    den = 6 * (d ** 2).sum() ** 1.5
    return (d ** 3).sum() / den if den > 0 else 0.0


def bca(reps, est, a, level):
    p = (reps < est).mean() + 0.5 * (reps == est).mean()
    z0 = ND.inv_cdf(min(max(p, 1e-6), 1 - 1e-6))
    out = []
    for q in ((1 - level) / 2, (1 + level) / 2):
        zq = ND.inv_cdf(q)
        out.append(float(np.quantile(reps, ND.cdf(z0 + (z0 + zq) / (1 - a * (z0 + zq))))))
    return out


SCENARIOS = [
    ("failure 0% vs 2%", "failure", power.arm_params(p_fail=0.0), power.arm_params(p_fail=0.02)),
    ("failure 1% vs 1%", "failure", power.arm_params(p_fail=0.01), power.arm_params(p_fail=0.01)),
    ("failure 2% vs 2%", "failure", power.arm_params(p_fail=0.02), power.arm_params(p_fail=0.02)),
    ("failure 2% vs 5%", "failure", power.arm_params(p_fail=0.02), power.arm_params(p_fail=0.05)),
    ("failure 5% vs 5%", "failure", power.arm_params(p_fail=0.05), power.arm_params(p_fail=0.05)),
    ("failure 2% vs 10%", "failure", power.arm_params(p_fail=0.02), power.arm_params(p_fail=0.10)),
    ("quality shift 24 points", "quality", power.arm_params(), power.arm_params(quality_mean=74.0)),
    ("steps shift 0.4 SD", "steps", power.arm_params(), power.arm_params(steps_shift_sd=0.4)),
]
COLUMN = {"failure": "failed", "quality": "quality", "steps": "log_steps"}
METHODS = ("percentile", "rescaled", "bca", "newcombe")


def main():
    grids = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    n_boot = 2000
    print(f"95% coverage and mean width, {grids} simulated grids per scenario, {n_boot} resamples")
    print(f"{'scenario':26}{'percentile':>12}{'rescaled':>10}{'BCa':>8}{'Newcombe':>10}   mean widths")
    for name, meas, a, b in SCENARIOS:
        t0 = time.time()
        truth = power.true_values(a, b)[meas]
        if meas == "steps":
            truth = math.log(truth)
        rng = np.random.default_rng(config.seed_int(config.ANALYSIS_SEED, "compare|" + name))
        hit = dict.fromkeys(METHODS, 0)
        width = dict.fromkeys(METHODS, 0.0)
        for _ in range(grids):
            rows = power.simulate(a, b, rng)
            v, isb, s = stats._clean(*analyse._pick(rows, "sim", "unseen", "seen", COLUMN[meas]))
            est = v[isb].mean() - v[~isb].mean()
            plain = boot_arm(v[isb], s[isb], n_boot, rng, False) - boot_arm(v[~isb], s[~isb], n_boot, rng, False)
            resc = boot_arm(v[isb], s[isb], n_boot, rng, True) - boot_arm(v[~isb], s[~isb], n_boot, rng, True)
            ci = {"percentile": stats.percentile_ci(plain, 0.95), "rescaled": stats.percentile_ci(resc, 0.95),
                  "bca": bca(plain, est, jack_accel(v, isb), 0.95)}
            if meas == "failure":
                ci["newcombe"] = stats.newcombe(v[~isb].sum(), (~isb).sum(), v[isb].sum(), isb.sum(), 0.95)
            for k, (lo, hi) in ci.items():
                hit[k] += lo - 1e-12 <= truth <= hi + 1e-12
                width[k] += hi - lo
        cov = [f"{hit[k] / grids:.3f}" if (k != "newcombe" or meas == "failure") else "-" for k in METHODS]
        wid = ", ".join(f"{k} {width[k] / grids:.4g}" for k in METHODS if k != "newcombe" or meas == "failure")
        print(f"{name:26}{cov[0]:>12}{cov[1]:>10}{cov[2]:>8}{cov[3]:>10}   {wid}   ({time.time() - t0:.0f} s)",
              flush=True)


if __name__ == "__main__":
    main()
