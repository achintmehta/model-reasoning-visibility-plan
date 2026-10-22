#!/usr/bin/env python3
"""Run the whole analysis: the grid's files in, the results folder out (DESIGN.md section 11).

    python3 run_analysis.py --key STATE/blind-key.jsonl --runs STUDY_ROOT --state STATE \\
        --results RESULTS --power POWER_DIR --out OUT

    python3 run_analysis.py power --out OUT [--grids 2000]     # protocol section 7, recomputed
    python3 run_analysis.py coverage --out OUT [--grids 2000]  # DESIGN.md section 10 item 3
    python3 run_analysis.py fake --out DIR [--models M,M]      # a fake grid to try it on
    python3 run_analysis.py check --key STATE/blind-key.jsonl --runs STUDY_ROOT
                                                    # the input checks only, no outcomes

`check` is run after each tier's batch and before its quality sample is drawn (DESIGN.md
section 2). It prints only labels and causes, never a blind id or an outcome, so it can be read
without un-blinding any app. Runs that are void for a cause the runner could not see are
listed there, and their slots are re-run by hand under the same label.

Writes into OUT, and nowhere else:
  run-table.csv       one row per analysed run (DESIGN.md section 3)
  confirmatory.csv    H1, H2 and H3-H5 per model: estimates, intervals, p, Holm, verdicts
  sensitivity.csv     section 8.3
  exploratory.csv     section 8.4 and the cost ratios of section 6.2
  descriptives.csv    section 6.4 per model x arm, with intervals
  voids.csv           section 9: void attempts by cause and empty slots, per model x arm
  items.csv           section 6.4 (11): each rubric item's pass share per model x task x arm
  compute.csv         section 6.2: machine time, GPU compute, energy
  report.md           the summary, with the seed, the resampling sizes and the inputs' sha256
  intermediate/       every step between the files and these tables, at full precision, with
                      every bootstrap replicate and every permuted statistic (its README.md,
                      DESIGN.md section 12)

The output depends only on the inputs and the seed: run twice, it is byte-identical.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from mrv import analyse, config, describe, load, power, record  # noqa: E402

RUBRICS = HERE.parent / "rubrics"


def fmt(x):
    if isinstance(x, float):
        if math.isnan(x):
            return ""
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return f"{x:.6g}"
    if isinstance(x, (list, tuple)):
        return " ".join(fmt(v) for v in x)
    if x is None:
        return ""
    return str(x)


def write_csv(path, rows, columns=None):
    columns = columns or (list(rows[0].keys()) if rows else ["empty"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(columns)
        for r in rows:
            w.writerow([fmt(r.get(c, "")) for c in columns])


def fmt_full(x):
    """A value at full precision: floats as Python's shortest exact repr, so that a recheck
    from the intermediate files gives the same number to the last bit."""
    if isinstance(x, (float, np.floating)):
        x = float(x)
        if math.isnan(x):
            return ""
        return repr(x)
    if isinstance(x, (np.integer,)):
        return str(int(x))
    if x is None:
        return ""
    return str(x)


def write_full_csv(path, rows):
    """Rows of varying keys, every key a column, in the order first seen, full precision."""
    columns = []
    for r in rows:
        for k in r:
            if k not in columns:
                columns.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(columns or ["empty"])
        for r in rows:
            w.writerow([fmt_full(r.get(c, "")) for c in columns])


def write_series(path, series):
    """One line per test: its id, the number of values, then every value at full precision.
    Gzipped with no time stamp, so the file is byte-identical from run to run."""
    import gzip
    with open(path, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        gz.write(b"id,n,values...\n")
        for key in sorted(series):
            vals = series[key]
            gz.write(key.encode("utf-8"))
            gz.write(("," + str(len(vals)) + "," + ",".join(fmt_full(float(v)) for v in vals) + "\n").encode("utf-8"))


INTERMEDIATE_README = """# Intermediate record

Every step between the grid's files and the final tables, written by run_analysis.py. Values
are at full precision (a float is written as the shortest decimal that reads back to the same
number), so every final number can be recomputed exactly from these files. DESIGN.md section 12
says how each final column is rebuilt from them, and tests/test_analysis.py (test 7) does it.

| file | one row per | what it holds |
|---|---|---|
| attempts.csv | key line (attempt) | exit code, manifest status, void cause, re-run causes, and its role: the slot's analysed run, a void attempt, or left out |
| steps.csv | step of an analysed run | reasoning characters as counted (0 for a field that is a misfiled call), the canary's count, whether the reasoning came from the reply text, tool calls, silent, prose, call written as text |
| run-evidence.csv | analysed run | the status used and why, the self-check and the call that showed it, the server-log lines summed for GPU time, the largest prompt, the power samples in the run's span |
| scores.csv | score sheet | items passed, failed and skipped, weight passed and scored, the score, accommodations, and why the app counts as substituted. Re-grade sheets are listed and marked as left out |
| probes.csv | probe file | the checks' results by kind and the API conformance |
| test-units.csv | unit of a test | the run (blind id), its arm, stratum and value, and whether it was used (a missing value is not) |
| test-strata.csv | stratum of a test | each arm's count, mean and variance in the stratum |
| test-detail.csv | test or estimate | counts and means, the estimate, the interval method and ends, for Newcombe every Wilson piece, for the bootstrap its stream, seed, size and replicate mean and SD, for the permutation test its stream, seed, observed statistic, the number of permuted statistics at least as extreme, the tolerance and p = (1 + extreme) / (permutations + 1). For a difference of two estimates, the two it combines |
| holm.csv | test in a Holm family | p, its rank, its multiplier, the product capped at 1, the running maximum (the adjusted p) |
| verdicts.csv | test | the adjusted p, the 90% interval, the bounds, the rule that decided the verdict, and how X was computed |
| bootstrap-replicates.csv.gz | test with a bootstrap interval | every replicate, in draw order |
| permutation-statistics.csv.gz | permutation test | every permuted statistic, in draw order |
| describe-replicates.csv.gz | descriptive with a bootstrap interval | every replicate (its id is the `id` column of descriptives.csv) |

The test id joins every file: it is the `test_id` column of confirmatory.csv, sensitivity.csv
and exploratory.csv. An interval is the linear-interpolation quantile (numpy.quantile) of the
finite replicates at the probabilities lo = (1 - level) / 2 and 1 - lo, computed in double
precision (so 0.025000000000000022 and 0.975 for 95%), as mrv/stats.py percentile_ci does.
"""


def write_intermediate(rec, folder):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "README.md").write_text(INTERMEDIATE_README, encoding="utf-8")
    for name in ("attempts", "steps", "run-evidence", "scores", "probes", "test-units", "test-strata",
                 "test-detail", "holm", "verdicts"):
        write_full_csv(folder / f"{name}.csv", rec.tables.get(name, []))
    for name, fname in (("bootstrap", "bootstrap-replicates"), ("permutation", "permutation-statistics"),
                        ("describe", "describe-replicates")):
        write_series(folder / f"{fname}.csv.gz", rec.series.get(name, {}))


def sha256_files(paths):
    h = hashlib.sha256()
    for p in sorted(str(x) for x in paths):
        h.update(os.path.basename(p).encode())
        with open(p, "rb") as f:
            h.update(hashlib.sha256(f.read()).digest())
    return h.hexdigest()


def md_table(rows, columns):
    out = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    for r in rows:
        out.append("| " + " | ".join(fmt(r.get(c, "")) for c in columns) + " |")
    return "\n".join(out)


def analysis(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    registered = None
    if a.registered:
        registered = json.loads(Path(a.registered).read_text(encoding="utf-8"))
    probe = a.probe or (os.path.join(a.results, "probe") if a.results else None)
    rec = record.Recorder()
    with record.recording(rec):
        return _analysis(a, out, registered, probe, rec)


def _analysis(a, out, registered, probe, rec):
    t = load.build_table(a.key, a.runs, a.results, a.state, a.rubrics, probe, a.power, registered)
    rows = t["rows"]
    if t["ungraded"] and not a.allow_ungraded:
        raise load.InputError(f"{len(t['ungraded'])} apps of the quality sample have no score of record: "
                              + ", ".join(t["ungraded"][:20]))
    st = analyse.Settings(a.n_perm, a.n_boot)
    res = analyse.run_all(rows, st)
    cols = [c for c in rows[0].keys()] if rows else []
    rows_sorted = sorted(rows, key=lambda r: (r["model"], r["task"], r["condition"], r["arm"], r["replicate"]))
    write_csv(out / "run-table.csv", rows_sorted, cols)
    for name in ("confirmatory", "sensitivity", "exploratory"):
        write_csv(out / f"{name}.csv", analyse.flat(res[name]), list(analyse.COLUMNS))
    desc = describe.per_cell(rows, st)
    write_csv(out / "descriptives.csv", desc)
    voids = describe.voids(t["voids"], rows, t["sampled_void"])
    write_csv(out / "voids.csv", voids)
    write_csv(out / "items.csv", describe.items(rows, t["items"]),
              ["model", "task", "arm", "item", "n", "share_pass"])
    comp = describe.compute(rows, t["spans"])
    write_csv(out / "compute.csv", comp)
    write_intermediate(rec, out / "intermediate")

    inputs = {"un-blinding key": sha256_files([a.key])}
    if a.results:
        inputs["score sheets"] = sha256_files(Path(a.results).glob("*.score.json"))
    if probe and os.path.isdir(probe):
        inputs["probe files"] = sha256_files(Path(probe).glob("*.api-probe.json"))
    if a.state:
        inputs["quality sample"] = sha256_files([p for p in (Path(a.state) / "quality-sample.jsonl",
                                                              Path(a.state) / "sample-levels.jsonl") if p.exists()])
    if a.power and os.path.isdir(a.power):
        inputs["power logs"] = sha256_files(Path(a.power).glob("power-*.csv"))
    inputs["verify_smokes.py (vendored)"] = config.VERIFY_SMOKES_SHA256

    rep = ["# Analysis results", "",
           f"Analysis seed {st.seed}, {st.n_perm} permutations, {st.n_boot} bootstrap resamples "
           f"(protocol section 8.1). Holm within each family at alpha = {config.ALPHA}.", "",
           "## Inputs (sha256)", ""]
    rep += [f"- {k}: `{v}`" for k, v in inputs.items()]
    rep += ["", "## Runs", "",
            f"{len(rows)} analysed runs, {len(t['voids']['attempts'])} void attempts, "
            f"{len(t['voids']['slots'])} empty slots, {len(t['voids']['after_outcome'])} attempts made after their "
            f"slot's analysed run (left out). {len(t['sampled_void'])} apps of the quality sample "
            f"are void attempts and enter no analysis. {len(t['ungraded'])} sampled apps have no score of record.", "",
            md_table(voids, ["model", "arm", "analysed_runs", "void_attempts", "void_rate", "empty_slots",
                            "void_in_quality_sample", "causes"]),
            "", "## Confirmatory tests (protocol sections 8.1 and 8.2)", "",
            "Differences are arm b minus arm a. Steps and H4 are ratios of geometric means (b over a).", "",
            md_table(analyse.flat(res["confirmatory"]),
                     ["model", "family", "measure", "arm_a", "arm_b", "n_a", "n_b", "estimate", "ci95_lo",
                      "ci95_hi", "ci90_lo", "ci90_hi", "p", "p_holm", "verdict", "x"]),
            "", "## Sensitivity (protocol section 8.3)", "",
            md_table(analyse.flat(res["sensitivity"]),
                     ["analysis", "model", "family", "measure", "n_a", "n_b", "estimate", "ci95_lo", "ci95_hi",
                      "p", "p_holm", "verdict"]),
            "", "## Exploratory (protocol section 8.4, cost of section 6.2)", "",
            md_table(analyse.flat(res["exploratory"]),
                     ["analysis", "model", "family", "measure", "n_a", "n_b", "estimate", "ci95_lo", "ci95_hi"]),
            "", "## Compute and energy (protocol section 6.2)", "",
            md_table(comp, list(comp[0].keys())), "",
            "Descriptives per model x arm (section 6.4) are in descriptives.csv, and the rubric item by item in items.csv.", ""]
    (out / "report.md").write_text("\n".join(rep), encoding="utf-8")
    print(f"{len(rows)} runs analysed -> {out}")
    return 0


def power_cmd(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = power.run(a.grids, a.n_perm, a.n_boot, only=a.only)
    name = "power.csv" if not a.part else f"power-part-{a.part}.csv"
    write_csv(out / name, rows)
    print(f"power: {len(rows)} rows -> {out / name}")
    return 0


def coverage_cmd(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = power.coverage(a.grids, a.n_boot, only=a.only)
    name = "coverage.csv" if not a.part else f"coverage-part-{a.part}.csv"
    write_csv(out / name, rows)
    print(f"coverage: {len(rows)} rows -> {out / name}")
    return 0


def fake_cmd(a):
    """Write a fake grid (mrv/fakedata.py) and print the command that analyses it."""
    from mrv import fakedata
    out = Path(a.out).resolve()
    if out.exists() and any(out.iterdir()):
        print(f"REFUSED: {out} exists and is not empty", file=sys.stderr)
        return 2
    sc = fakedata.scenario(p_void=a.void_rate)
    if a.seen_fail is not None:
        sc["cells"].append(({"arm": "seen"}, {"p_fail": a.seen_fail}))
    models = set(a.models.split(",")) if a.models else None
    plan = fakedata.make_plan(sc, a.seed, models=models, max_replicate=a.replicates)
    paths = fakedata.write_grid(plan, out)
    print(f"fake grid: {len(plan['attempts'])} attempts, {len(paths['sample'])} apps in the quality sample -> {out}")
    print("analyse it with:")
    print(f"  python3 run_analysis.py --key {paths['key']} --runs {paths['runs']} --state {paths['state']} "
          f"--results {paths['results']} --power {paths['power']} --out {out / 'results-out'}")
    return 0


def check_cmd(a):
    """The input checks of protocol section 9 alone: every key line has its run and every run
    its key line, and no run is void for a cause the runner could not see without a re-run.
    Prints counts, labels and causes only."""
    registered = json.loads(Path(a.registered).read_text(encoding="utf-8")) if a.registered else None
    try:
        attempts = load.load_attempts(a.key, a.runs, registered)
        res = load.resolve_slots(attempts)
    except load.InputError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    print(f"{len(attempts)} attempts, {len(res['chosen'])} slots with an analysed run, "
          f"{len(res['void_attempts'])} void attempts, {len(res['empty_slots'])} empty slots, "
          f"{len(res['after_outcome'])} attempts after their slot's analysed run")
    if res["unresolved"]:
        print("NEEDS A RE-RUN: " + load.unresolved_message(res["unresolved"]), file=sys.stderr)
        return 2
    print("ok: nothing needs a re-run")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "check":
        ap = argparse.ArgumentParser(description="run_analysis.py check: the input checks only")
        ap.add_argument("--key", required=True)
        ap.add_argument("--runs", required=True)
        ap.add_argument("--registered", help="a JSON file replacing the registered configuration (tests only)")
        return check_cmd(ap.parse_args(argv[1:]))
    if argv and argv[0] == "fake":
        ap = argparse.ArgumentParser(description="run_analysis.py fake: write a fake grid")
        ap.add_argument("--out", required=True)
        ap.add_argument("--models", help="comma-separated model keys (default: all eight)")
        ap.add_argument("--seed", default="demo")
        ap.add_argument("--void-rate", type=float, default=0.0)
        ap.add_argument("--replicates", type=int, help="keep only replicates 1..N of every cell (a small grid)")
        ap.add_argument("--seen-fail", type=float, help="plant a SEEN failure rate (the base is 0.15)")
        return fake_cmd(ap.parse_args(argv[1:]))
    if argv and argv[0] in ("power", "coverage"):
        ap = argparse.ArgumentParser(description=f"run_analysis.py {argv[0]}")
        ap.add_argument("--out", required=True)
        ap.add_argument("--grids", type=int, default=2000)
        ap.add_argument("--n-perm", type=int, default=2000)
        ap.add_argument("--n-boot", type=int, default=2000)
        ap.add_argument("--part", help="write OUT/<kind>-part-PART.csv, for a run split over several calls")
        ap.add_argument("--only", action="append", help="run only the scenario of this exact name (repeatable)")
        a = ap.parse_args(argv[1:])
        return power_cmd(a) if argv[0] == "power" else coverage_cmd(a)
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--key", required=True, help="blind-state/blind-key.jsonl")
    ap.add_argument("--runs", required=True, help="the study root: <model>/<task>/runs/<blind id>")
    ap.add_argument("--state", help="the blind-state folder (quality sample, re-grade key)")
    ap.add_argument("--results", help="the score sheets (<blind id>.score.json)")
    ap.add_argument("--probe", help="the probe files (default: RESULTS/probe)")
    ap.add_argument("--power", help="the power logs folder (power-*.csv)")
    ap.add_argument("--rubrics", default=str(RUBRICS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-perm", type=int, default=config.N_PERM)
    ap.add_argument("--n-boot", type=int, default=config.N_BOOT)
    ap.add_argument("--registered", help="a JSON file replacing the registered configuration (tests only)")
    ap.add_argument("--allow-ungraded", action="store_true", help="analyse before grading is complete (tests only)")
    a = ap.parse_args(argv)
    try:
        return analysis(a)
    except load.InputError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
