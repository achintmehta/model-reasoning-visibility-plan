# Power and interval coverage, recomputed on fake data

Made on 2026-10-21 by the analysis code in this folder's parent, before the registration freeze
and before any grid app was graded or un-blinded (protocol section 8.5). Nothing here is grid data.

| file | what it is | made by |
|---|---|---|
| `power.csv` | protocol section 7 recomputed: for each scenario, the share of 2,000 simulated grids reaching each verdict, per measure, with its Monte Carlo standard error | `run_analysis.py power` |
| `coverage.csv` | how often the 95% and 90% intervals of the frozen methods cover the planted value, 2,000 grids per scenario | `run_analysis.py coverage` |
| `interval-comparison.txt` | the comparison behind DESIGN.md section 10 item 3: percentile, rescaled percentile, BCa and Newcombe, 95% coverage and mean width | `compare_intervals.py` |
| `power-percentile.csv`, `coverage-percentile.csv` | the same two runs made first, with plain percentile intervals everywhere, before the decision of item 3. Kept as the record of what that decision was based on | `run_analysis.py`, before item 3 |

Each simulated grid uses 2,000 permutations and 2,000 bootstrap resamples (DESIGN.md section 10
item 5). The runs were split over several calls, one scenario per call (`--only`, `--part`), and
the parts joined in order. Every scenario has its own random stream, derived from the analysis
seed and its name, so a split run gives the same numbers as a single one.
