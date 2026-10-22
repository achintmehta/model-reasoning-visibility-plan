# Intermediate record

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
