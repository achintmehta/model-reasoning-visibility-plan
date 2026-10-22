# Verification on a small fake grid

A hand-checkable record that the analysis code computes what DESIGN.md and the protocol say. A
fake grid small enough to follow (two models, two runs in every task x condition cell, 12 runs
per arm) is made in the real file formats, analysed at the registered sizes, and every number
the analysis produced is set beside the same number computed by Excel formulas, or, for the
permutation p values, by counting every possible relabelling. Nothing here is grid data.

## Files

| file | what it is |
|---|---|
| `make_grid.py` | step 1: the scenario (planted values), the seed `verify-small` and the models. Makes the grid outside the repository, analyses it, and keeps the files below |
| `planted-truth.csv` | the planted value of every attempt |
| `analysis-output/` | `run_analysis.py`'s output on the grid (10,000 permutations and resamples), with its `intermediate/` record of every step (DESIGN.md section 12) |
| `bundle-for-workbook.json` | the key, the quality sample, every score sheet's item results and every probe's results, read from the grid |
| `exact_p.py` | step 2: exact permutation p values by counting every relabelling. It imports nothing from `mrv/` |
| `exact-p.csv` | its output |
| `build_workbook.py` | step 3: the workbook. Needs openpyxl |
| `analysis-verification.xlsx` | the workbook. Start with its "Read me" sheet, which also has the summary of every check |

## The three commands

Run from `plan/analysis`:

```bash
python3 verification/make_grid.py ~/mrv-verify-grid
python3 verification/exact_p.py verification/analysis-output/run-table.csv \
    verification/analysis-output/confirmatory.csv verification/analysis-output/sensitivity.csv \
    > verification/exact-p.csv
python3 verification/build_workbook.py
```

The first command refuses a grid folder that exists already. The grid itself (run folders,
blind state, score sheets, probes, power log) is not kept: the same seed and scenario make it
again. Run again, step 1 rewrites every kept file identically except the input hashes at the
top of `analysis-output/report.md`, because the key records the grid's folder and the
blind-state tools stamp the time on their own records. Every number is the same.

## What the workbook checks

| sheet | check |
|---|---|
| Runs | the analysis read every run's files right (its values equal the planted ones), and Excel's recomputation of failure, log steps, log median characters, quality, substitution and API conformance equals the analysis |
| Quality | every app's score from its item results and the card's weights, its substitution flag and its API share |
| Voids | each slot has exactly one analysed attempt and never a void one, and the counts per model x arm equal the analysis's |
| Tests | counts, means and estimates, Newcombe intervals (exact), Holm, verdicts and X (exact), the analysis's p within Monte Carlo error of the exact p, and each bootstrap interval close to a normal interval with the same variance |
