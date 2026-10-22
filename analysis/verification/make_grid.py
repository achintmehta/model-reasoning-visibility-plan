#!/usr/bin/env python3
"""Step 1 of the verification record (README.md): make the small fake grid, analyse it, and
collect what the workbook needs.

    python3 verification/make_grid.py [GRID_DIR]        # run from plan/analysis

GRID_DIR (default: ~/mrv-verify-grid, outside the repository) receives the fake grid's run
folders, blind state, score sheets, probe files and power log. It must not exist yet. This
folder (verification/) receives what is kept with the code:
  planted-truth.csv           the planted values of every attempt
  analysis-output/            run_analysis.py's output on the grid, at the registered sizes
  bundle-for-workbook.json    the key, the quality sample, every sheet's item results and every
                              probe's check results, read from the grid's files

Everything is fixed by the scenario below, the seed and the models, so the same grid is made
every time (the key's times come from the plan, the blind ids from the seed).
"""
import csv
import glob
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from mrv import fakedata  # noqa: E402
from mrv.load import rubrics_module  # noqa: E402
import run_analysis  # noqa: E402

SEED = "verify-small"
MODELS = {"gemma-q4", "gptoss-20b"}     # one model with an OFF arm, one without
REPLICATES = 2                          # r01 and r02 of every cell: 12 runs per arm


def scenario():
    """The planted values. Rates per run unless named otherwise (mrv/fakedata.py, BASE)."""
    sc = fakedata.scenario(p_void=0.08, p_nudge=0.2, p_sub=0.15)
    sc["cells"].append(({"arm": "off"}, {"p_fail": 0.30}))
    sc["cells"].append(({"arm": "unseen"}, {"p_fail": 0.45, "steps_mu": math.log(70), "q_works": 0.35,
                                            "rate": 0.7, "med_chars": 400.0, "p_silent": 0.4}))
    sc["cells"].append(({"arm": "seen"}, {"p_fail": 0.05, "steps_mu": math.log(40), "q_works": 0.85,
                                          "rate": 0.98, "med_chars": 150.0, "p_silent": 0.0}))
    return sc


def main():
    grid = Path(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/mrv-verify-grid")).resolve()
    if grid.exists():
        sys.exit(f"{grid} exists already: give a new folder")
    plan = fakedata.make_plan(scenario(), SEED, models=MODELS, max_replicate=REPLICATES)
    paths = fakedata.write_grid(plan, grid)
    truth = fakedata.truth_rows(plan, paths["sample"])
    cols = list(next(iter(truth.values())).keys())
    with open(HERE / "planted-truth.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["blind_id", "void"] + cols)
        for a in plan["attempts"]:
            t = truth.get(a["blind_id"], {})
            w.writerow([a["blind_id"], a["void"] or ""] + [t.get(c, "") for c in cols])
    rc = run_analysis.main(["--key", str(paths["key"]), "--runs", str(paths["runs"]), "--state", str(paths["state"]),
                            "--results", str(paths["results"]), "--power", str(paths["power"]),
                            "--out", str(HERE / "analysis-output")])
    if rc != 0:
        sys.exit(f"the analysis refused the grid (exit {rc})")
    ss = rubrics_module(fakedata.RUBRICS)
    bundle = {"sheets": {}, "cards": {}, "probes": {}}
    for t in ss.TASKS:
        card = ss.load_card(t, str(fakedata.RUBRICS))
        bundle["cards"][t] = [{"id": i["id"], "weight": i["weight"], "step": i["step"]} for i in card["items"]]
    for p in sorted(glob.glob(str(paths["results"] / "*.score.json"))):
        sh = ss.read(p)
        items = ss.items_of(sh)
        bundle["sheets"][sh["blind_id"]] = {
            "task": sh["task"], "acc": sh["accommodations"],
            "items": {k: v["result"] for k, v in items.items()},
            "l0notes": {k: v.get("notes", "") for k, v in items.items() if k.endswith("-L0")}}
    for p in sorted(glob.glob(str(paths["probe"] / "*.api-probe.json"))):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        bundle["probes"][d["blind_id"]] = [c["result"] for c in d["checks"]]
    bundle["key"] = [json.loads(x) for x in open(paths["key"], encoding="utf-8") if x.strip()]
    bundle["sample"] = [{k: v for k, v in json.loads(x).items() if k != "drawn_at"}
                        for x in open(paths["state"] / "quality-sample.jsonl", encoding="utf-8") if x.strip()]
    for r in bundle["key"]:
        r.pop("run_base", None)          # the grid folder's path, which differs by machine
    with open(HERE / "bundle-for-workbook.json", "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=1, sort_keys=True)
    print(f"{len(plan['attempts'])} attempts, {len(truth)} analysed runs -> {grid}")
    print(f"kept in {HERE}: planted-truth.csv, analysis-output/, bundle-for-workbook.json")


if __name__ == "__main__":
    main()
