# Analysis code: design

This is the design of the code that turns the grid's runs and grades into the numbers of
protocol sections 6 to 8. It is written before any grid run exists, tested on fake data, and frozen at the
registration freeze (protocol section 5.1 item 10, section 8.5). Every section names the protocol rule it
implements. Section 10 lists the analysis details the protocol had not spelled out, as decided and fixed before the code was written.

## 1. Scope

Each row is one thing the analysis code produces. The middle column names the protocol
section that asks for it. The last column says whether it makes a statistical test (a p-value
or a test verdict) or only reports numbers. Everything in the table, tests or not, is checked
on fake data (section 9).

| what the code produces | protocol | statistical test? |
|---|---|---|
| the run table: one row per grid run, every measure | sections 6.1 to 6.4 | no, it is the data every other row is computed from |
| confirmatory tests: H1, H2 (three measures each), H3-H5 | section 8.1 | yes: permutation tests, p-values, Holm within each family |
| intervals for every estimate | section 8.1 | no: estimates with 95% intervals |
| equivalence and the three-way verdict | section 8.2 | yes: two one-sided tests, read from the 90% interval |
| sensitivity: runs without a nudge, and substituted or added packages scored 0 | section 8.3 | the confirmatory tests rerun on these data, reported beside the headline, outside the Holm families |
| exploratory: verification split, within-lab pairs, API conformance, registered shapes | sections 8.4 and 1.3 | no: intervals only |
| descriptives per model x arm | section 6.4 | no |
| cost, compute and energy | section 6.2 | no: estimates, with intervals for cost |
| grader consistency (already in `rubrics/merge_grades.py`, reused, not rewritten) | sections 6.1 and 5.3 | no: agreement statistics against the 5-point bar |
| power, recomputed under these exact tests | section 7 | no: a simulation of the tests above |
| the fake-data test of all of the above | section 8.5 | no: it checks the code |

## 2. Inputs (read only, nothing is written next to them)

| input | where | gives |
|---|---|---|
| un-blinding key | `blind-state/blind-key.jsonl` (grid checkout) | blind id -> model, task, condition, arm, replicate, run folder, status |
| run records | `<run>/smoke/logs/manifest.json`, `trace.jsonl`, `llama-server.log.zst` | status, steps, tokens, nudges, loop guard, reasoning, tool calls, file-state repeats, retries, times. Per-step reasoning and replies. GPU timings |
| scores of record | the score sheets (`<results>/<id>.score.json`) | each sampled app's first-grading score, its item results, its accommodations. Read with the rubric's own `score_sheet.py` (its completeness check and its score), as `merge_grades.py` reads them |
| quality sample | `blind-state/quality-sample.jsonl`, `sample-levels.jsonl` | which apps are graded (rank <= level of their tier's draw) |
| re-grade key | `blind-state/regrade-key.jsonl` | first <-> second id, for consistency and the probe's reproducibility |
| API probe | `<results>/probe/<id>.api-probe.json` | each check's result (section 6.5) |
| power logs | `power/power-*.csv` (epoch, watts, utilisation) | energy per run (section 6.2) |

The attempts and voids of each slot are read from the key, which has one line per attempt
(failed ones included) with its exit code, so the batch progress files are not needed.

**The void rule** (protocol section 9). Each cause of section 9's list, and how the run records
it, which is what `load.is_void` and `load.needs_rerun` read:

| cause (protocol section 9) | how the run records it | the runner sees it? | in the analysis |
|---|---|---|---|
| the server crashed or reset, or did not answer | the harness ends the run as `api_error` (with `server_model_crash` and the server's reply in `api_error.body`) and re-raises, so the runner exits with a code other than 0 | yes: the batch driver re-attempts the slot, three attempts in all | a void attempt, cause "runner failed" or "api error" |
| output the server could not parse | `api_error.model_output_unparseable`, or the server's message in `api_error.body` (`parse_void`, the gate script's rule) | yes, as above | a void attempt, cause "unparseable output", counted per model x arm |
| no manifest at all | the run folder has no `manifest.json` | yes: the exit code is not 0 | a void attempt, cause "no manifest" |
| a recorded setting differs from section 4 | the manifest's `harness_git`, `task_sha`, `base_prompt_sha`, `condition_briefing_sha`, `decoding_registry_sha`, `think_preamble_sha`, `briefing_mode`, `replay_format` and `max_total_tokens` against the registered values | no: the run exits 0 | stops the analysis until the slot is re-run (below) |
| the wrong file was served | the manifest's `quantization_detail.status` is not `ok` (the served file did not resolve in the quantization registry) | no: the run exits 0 | stops the analysis until the slot is re-run |
| the npm registry was unreachable | nothing in the manifest: a command that installs packages (`npm`, `pnpm` or `yarn` with `install`, `i`, `ci` or `add`, `npx`, `npm create` or `npm init` with a package) whose output in the trace holds `ENOTFOUND`, `ETIMEDOUT` or `ECONNRESET`. The trace keeps every tool result whole, where `console.log` shortens them | no: the run exits 0 | stops the analysis until the slot is re-run |

`system_prompt_sha` is not compared: it covers the workspace path, which differs from run to
run. Its fixed parts are covered by `base_prompt_sha` and `condition_briefing_sha`.

A void the runner sees is re-attempted by the batch driver. A void it cannot see would leave
the slot marked done, so the analysis stops and lists it (label and cause, no blind id and no
outcome), and the study lead re-runs the slot by hand under the same label. The listed attempt
then counts as a void attempt, and the re-run is the slot's analysed run. To catch these before
any app of a tier is graded, `run_analysis.py check` runs the same checks and prints only
labels and causes. It is run after each tier's batch and before the tier's quality sample is
drawn, so that a re-run app can enter the sample.

**Outcomes, never voids.** A context overflow is an outcome (protocol section 9). The frozen
harness records it as `context_overflow` and exits 0 (`harness/agent.py`: `run_agent` returns
it, and `main()` records an overflow that escapes `run_agent` the same way without re-raising).
An older build filed it as `api_error` and exited 1. If such a run ever appears
(`overflow_filed_as_error`, the gate script's rule), it is the slot's outcome, entered as
`context_overflow`, and the batch driver's re-attempt after it enters no analysis.

**One analysed run per slot.** The slot's analysed run is its first attempt, in the order the
attempts started, that is neither void nor in need of a re-run. An attempt after it should not
exist and is listed in the report. A slot whose every attempt is void is empty, and empty
slots are reported per model x arm.

The code also refuses to run if any grid run lacks a key line or a manifest, if a key line has
no run, or if a score sheet of a first grading is incomplete.

## 3. The run table

One row per grid run that is not void (voids are counted per model x arm, section 9, and enter no
analysis). Columns, each with its source:

| column | definition | protocol |
|---|---|---|
| `model`, `task`, `condition`, `arm`, `replicate` | from the key | section 2 |
| `stratum` | task x condition (six) | section 8.1 |
| `failed` | `status != "finished"` | section 6.1 |
| `status`, `loop_guard` | manifest `status` (one of `config.STATUSES`, the harness's own list. An overflow filed as `api_error` is entered as `context_overflow`), and the guard of `loop_guard_fired` | section 6.4 (1) |
| `steps`, `log_steps` | manifest `steps`. Its log for finished runs only | section 6.1 |
| `tokens_prompt`, `tokens_completion`, `tokens_total` | manifest `total_tokens_used` | section 6.2 |
| `nudged` | manifest `finish_nudges > 0` | section 8.3 |
| `finish_nudges`, `finish_nudge_steps` | manifest, the number of nudges and the steps they came at | section 6.4 (5) |
| `reasoning_rate` (H3) | share of steps whose reasoning field is non-empty and is not wholly a tool call (`field_is_call`, the canaries' rule). The reasoning field includes any reasoning the server left in the reply text (`reasoning_split`), as in the gate script | section 6.3 |
| `reasoning_median_chars` (H4) | median reasoning characters over those steps. Missing if none | section 6.3 |
| `silent_turn` (H5) | any response with neither text nor a tool call | section 6.3 |
| `call_as_text_steps` | steps with no parsed call whose reasoning or text holds one (`call_as_text`) | section 6.4 (4) |
| `canary_longest_chars`, `canary_steps_over` | the OFF canary's rule (gate G2): the longest reasoning step with Seed-OSS's budget reports removed, and the steps over 200 characters | section 6.4 (3) |
| `prose_turns`, `silent_turns` | turns without a tool call, split | section 6.4 (5) |
| `self_check` | a server started, an HTTP request, a build/test command, a browser tool (execution and interactive only) | section 6.4 (6) |
| `file_state_*` | manifest `file_state_repeats` | section 6.4 (7) |
| `max_prompt_tokens` | largest prompt of the run: the largest `n_prompt_tokens` in the server log | section 6.4 (9) |
| `machine_s` | `ended_at - started_at` | section 6.2, section 6.4 (10) |
| `gpu_s` | sum of prompt-eval and eval times in the server log | section 6.2 |
| `energy_wh` | board power integrated over the run's span by the trapezoid rule, the span's ends taking the power of the nearest sample inside it (if logged) | section 6.2 |
| `sampled`, `quality` | in the quality sample. Score of record (0-100) | section 5.3, section 6.1 |
| `substituted` | graded after an A0 `ETARGET` re-run or an A8 | section 8.3 |
| `api_conformance` | share of probe checks passed, over passed + failed | section 6.5 |

The reasoning-field rules (`field_is_call`, `call_as_text`, `reasoning_split`) are taken from
`verify_smokes.py` of the certifying smoke set (doi:10.5281/zenodo.23239989), copied verbatim
with its sha256 recorded, so that the analysis counts reasoning exactly as the canaries did.

## 4. Confirmatory tests (section 8.1)

Per model. Contrasts: **H1** UNSEEN vs SEEN (every model run), **H2** OFF vs UNSEEN (the six with
an off-switch).

- **Statistics.** Failure: difference in the share failing (all runs). Steps: difference in mean
  `log_steps` (finished runs), reported as a ratio of geometric means. Quality: difference in
  mean score (sampled apps).
- **Permutation.** Arm labels are permuted *within each of the six strata*, among the units that
  enter that statistic (all runs, finished runs, sampled apps). 10,000 permutations, the analysis
  seed (section 10). Two-sided p = (1 + #{|T\*| >= |T|}) / (10,000 + 1).
- **H3-H5**, one-sided in the registered direction: SEEN - UNSEEN in mean `reasoning_rate`
  (> 0). In mean log `reasoning_median_chars` (< 0, runs with a value only). In the share with
  a `silent_turn` (UNSEEN - SEEN > 0). p = (1 + #{T\* >= T}) / 10,001 in that direction.
- **Holm** at alpha = 0.05 within each family of each model: H1's three p, H2's three p, H3-H5's three
  p. No correction across families or models (section 1.3).

## 5. Intervals (section 8.1)

Two methods, chosen on the fake-data coverage check of section 10, item 3:

- **A difference between two shares of runs** (failure, and H5's share of runs with a silent
  turn) gets Newcombe's hybrid score interval (his method 10), 95% and 90%. It is computed on
  the plain shares. The design gives every stratum of an arm the same number of runs (20), so
  the plain share equals the stratified one. When a slot is empty the two differ slightly, and
  the report counts empty slots per model x arm beside it.
- **Every other estimate** (steps, quality, H3, H4, API conformance, the cost ratios) gets a
  rescaled stratified bootstrap: within each arm, units are resampled with replacement inside
  each stratum (keeping each stratum's count), and each stratum's resampled mean is rescaled
  about the stratum's mean by sqrt(k / (k - 1)), k its size, so that the bootstrap variance is
  the unbiased one. 10,000 resamples, the analysis seed. The 95% and 90% intervals are the
  percentile intervals of the rescaled replicates. For quality, the units are the sampled apps.
  For steps, the finished runs. The estimate is the plain mean of each arm, which is also the
  strata's means weighted by their sizes, so the replicates are centred on it.

A single arm's share in the descriptives gets a Wilson interval, any other single-arm mean the
same rescaled bootstrap.

Estimates reported for every contrast: failure difference (percentage points), ratio of
geometric mean steps, quality difference (points), H3-H5 differences, and the cost ratios of
section 6.2 (SEEN/UNSEEN and UNSEEN/OFF mean tokens, all runs and finished runs).

## 6. Equivalence and verdicts (section 8.2)

- Failure: equivalent when the 90% interval lies inside +/-10 points. Steps: when it lies inside
  0.8-1.25. Quality: no bound.
- Verdict per measure: **different** if its Holm-adjusted p < 0.05. Else **equivalent** if the
  90% interval is inside the bounds. Else **undetermined**. (Quality: different or undetermined.)
- For a null, the code also prints X, the largest absolute value in the 90% interval, for the
  sentence "keeping reasoning visible changes nothing by more than X".

## 7. Sensitivity and exploratory (section 8.3, section 8.4)

- **Runs without a nudge:** H1 recomputed on runs with `nudged == False` in both arms. Same tests
  and intervals, reported beside the headline, outside the Holm families.
- **Substituted packages:** H1 and H2 quality recomputed with every `substituted` app scored 0.
  The test uses the headline's random streams, and its p is Holm-corrected together with the
  headline family's failure and steps p values, so it is the headline family with only the
  quality scores changed.
- **Verification split** (`verification:no_verification`, `verification:feedback`,
  `verification:difference`): the UNSEEN -> SEEN estimates inside `no_verification` and inside
  the two feedback conditions, and the first minus the second (a ratio of ratios for steps),
  each with its interval. The difference's interval comes from the two blocks' own bootstrap
  replicates, which are independent draws, and for failure from the two blocks' Newcombe
  intervals combined by MOVER (below).
- **Quality of finished runs** (`quality:finished`): the quality contrast over the sampled apps
  of finished runs only, per contrast, interval only, read beside the headline quality
  contrast that grades every sampled app finished or not (protocol section 6.1).
- **Within-lab pairs** (Qwen 27B / 35B-A3B, Gemma 31B / 26B-A4B): each twin's estimate, each
  sibling's, and their difference (a ratio of ratios for steps), bootstrapped independently
  per model. The twin's and the sibling's estimates reuse the confirmatory random streams, so
  they are the confirmatory estimates and intervals exactly. For failure, the difference of
  the two Newcombe intervals is combined by the same construction Newcombe's interval is made
  by (MOVER, Zou and Donner). Intervals only.
- **API conformance:** arm differences per contrast, intervals only.
- **Registered shapes** (section 1.3) and the descriptives of section 6.4: per model x arm, with intervals
  where section 6.4 asks for them. A share of runs (failure, each terminal status, nudged,
  self-check, the canary share) gets a Wilson interval, named in `describe.SHARE_COLUMNS`,
  any other mean the rescaled bootstrap. Reasoning in OFF is reported twice: the plain share of
  steps with reasoning, and the OFF canary's rule (the share of runs with a reasoning step over
  200 characters, budget reports not counted, and the arm's longest such step).

## 8. Power, recomputed (section 7)

Monte Carlo under the exact procedures above: for each scenario, simulate the grid's design
(120 runs a side, 20 per stratum, 60 sampled apps a side), run the permutation test with Holm,
and count rejections. Scenarios:

- failure 2% vs 10%, 15%, 20%. Steps shifts of 0.3-0.5 SD. Quality shifts of 0.5-0.7 SD at
  SD = 41 points: each with the other two measures null, so Holm is applied as in the study.
- equivalence: both arms at 2% and at 5% failure, and steps ratio 1.0, counting how often
  "equivalent" is declared.
- H3-H5 at effects of the size the smoke runs reported (protocol section 1.3), each with the other two
  null: reasoning rate 0.90 against 0.97, median reasoning characters 0.8 times, and a silent
  turn in 10% of runs against 2%. And a mechanism null.
- a null with every measure equal, which is also test 1 of section 9.2.

The same simulation measures how often the 95% and 90% intervals cover the planted
value, at failure rates at and near 0 (0% against 2%, 1%, 2% and 5% in both arms, 2% against 5%
and 10%, 10% in both) and for steps and quality at the design's sizes (section 10, item 3).

Each simulated grid's run table goes through the same functions as the grid's
(`analyse.family`, `analyse.mechanism`, `analyse.estimate`), so what is simulated is the
analysis itself. The data are simple on purpose: failures are Bernoulli, log steps normal,
quality scores normal with SD 41 points, and the reasoning measures drawn around the scenario's
values.

To keep it tractable each simulated test uses 2,000 permutations and 2,000 resamples, with
2,000 simulated grids per scenario. The run times and the Monte Carlo error are reported.

## 9. Fake data, and how the code is tested (section 8.5)

### 9.1 Reference material already on hand

The fake grid is built from real files, so that the code is tested against the formats it will
meet, not against formats written for the test. Nothing here is grid data, and none of it is
unblinded.

| source | what it gives the tests |
|---|---|
| the certifying smoke set, 66 runs (the smoke-runs repository, doi:10.5281/zenodo.23239989) | every file a run writes, in its real format: `manifest.json`, `trace.jsonl`, `commands.json`, `console.log`, `environment.txt` and `llama-server.log.zst`. Fake runs are made by copying a smoke run's files and rewriting the fields a scenario sets (arm, status, steps, reasoning). |
| `verify_smokes.py` in the same repository | the reasoning-field rules (`field_is_call`, `call_as_text`, `reasoning_split`) that H3 to H5 must count by |
| `verify_smokes_result.txt` in the same repository | the gate script's own numbers for the 66 smoke runs, per model and arm: steps, reasoning share, median reasoning characters, turns without a tool call, calls written as text, terminal statuses. The analysis code, run on the same 66 runs, must reproduce them exactly (a real-data check, see test 6 below). |
| the smoke set's `batch-state/` | the formats of a schedule and a progress file |
| the grid's schedules (`registration/schedules/`) | the exact list of runs the grid will make, 2,640 slots. The fake grid has these slots, so the code is tested on the real design, not an approximation of it. |
| `write_blind_key()` in `run_one_with_server.sh` (the frozen harness) | the exact fields of an un-blinding key line, written by the same code for the fake grid |
| the training round (`calibration/`, 66 score sheets and 66 probe files) | the formats of a score sheet and a probe file, and a realistic spread of scores and probe results (blind ids only, no arms) |
| the grading tools (`rubrics/blind_tools.py`, `rubrics/merge_grades.py`) | run as they are on the fake grid's state: the quality sample and re-grade draw are made by `blind_tools.py`, and the scores of record by `merge_grades.py --unblinded`, so the analysis reads exactly what those tools write |

Two rules keep this clean. Smoke outcomes are used only for formats and for realistic base rates
with the arm labels shuffled, never to set the size of a planted effect: effect sizes come from
the protocol's power scenarios (section 7). And the training round's un-blinding key and the mock
grading's unblinded scores are not used at all.

### 9.2 The tests

A generator writes a complete fake grid in these formats, with effects planted where a scenario
asks for them. The tests check that:

1. a null grid gives rejection rates near 5% per test, and Holm keeps each family's rate at or
   below 5%.
2. planted effects are found, and their intervals cover the planted value at about the nominal
   rate.
3. two runs with the same seeds give byte-identical output.
4. edge cases work: a model with no OFF arm, an arm with no failures, a stratum with voids, a
   run with no reasoning step (H4 missing), every run nudged, an extended quality sample, and
   apps with substituted or added packages.
5. the input checks refuse a mismatched `harness_git`, a missing manifest and an orphan key line,
   and the void rule of section 2 holds: an overflow filed as `api_error` is entered as a
   `context_overflow` failure and the re-attempt after it is left out, and a wrong model file or
   an unreachable npm registry stops the analysis (listing labels, never blind ids) until a
   re-run of the slot exists, which then becomes its analysed run.
6. on the 66 real smoke runs, the run table's per-model, per-arm numbers equal those in
   `verify_smokes_result.txt`.
7. every final number is rebuilt from the intermediate record of section 12 alone: the run
   table's reasoning measures from `steps.csv`, quality from `scores.csv`, each estimate from
   its units, each bootstrap interval from its replicates (bit for bit), each Newcombe interval
   from Wilson's formula written out in the test, each p from its permuted statistics, Holm
   from its steps, and each verdict from its rule.

## 10. Decisions

These are analysis details the protocol had not spelled out. The study lead decided them on
2026-10-21, items 1, 2, 4 and 5 before any analysis code was written, and items 3 and 6 on the
fake-data tests, before the registration freeze and without any grid data. They are fixed in the
protocol (sections 5.3, 8.1 and 8.2). The code carries them out and makes no choice of its own.

1. **Steps permutation.** Steps uses finished runs only, so arm labels are permuted among the
   finished runs within each stratum.
2. **The 90% interval for equivalence** is made by the same method as the measure's 95%
   interval (item 3): Newcombe's for failure, the rescaled bootstrap's for steps.
3. **Interval methods**, decided on the fake-data coverage check, as planned. The rule, proposed
   before the check was run: a method whose 95% interval covers less than 93% in any failure
   scenario at or below 5% is replaced, and the replacement is the method with the best worst
   case. On 2,000 simulated grids per scenario (`power-results/interval-comparison.txt`), the
   plain percentile interval of the stratified bootstrap covered 91.1% at 0% against 2% failure,
   so it failed the rule. BCa, the replacement first named here, did worse (worst case 90.2%).
   Newcombe's hybrid score interval never covered less than 96.1%, and it is the interval the
   protocol's power figures were computed with. The same check found the percentile interval of
   quality covering about 93%, because a stratum holds only 10 sampled apps and the plain
   bootstrap understates a stratum's variance by (k - 1) / k. Rescaling each stratum by
   sqrt(k / (k - 1)) brings it to about 94.4%. The study lead chose, on 2026-10-21: Newcombe for
   every difference between two shares of runs, and the rescaled stratified bootstrap for
   every other estimate (section 5). The frozen methods' coverage is in
   `power-results/coverage.csv`: at least 95.75% for failure, and 93.85% to 95.7% for steps and
   quality, at nominal 95%.
4. **The analysis seed** is `61f43c6f3593702f`, one seed for every permutation and bootstrap,
   recorded in the protocol (section 8.1).
5. **Power simulation size:** 2,000 simulated grids per scenario, each test with 2,000
   permutations and 2,000 resamples, with the Monte Carlo error reported.
6. **Void attempts in the quality sample.** `blind_tools.py sample` puts every key line of a cell
   in the cell's random order, void attempts included, so a void attempt can be among a cell's
   first ten. It is left as it is (study lead, 2026-10-21): such an app enters no analysis, its
   cell has fewer than ten graded apps, and the report counts these per model x arm.

## 11. Layout

```
analysis/
  DESIGN.md            this file
  requirements.txt     numpy only, beside the standard library (tested on Python 3.10.12, numpy 2.2.6)
  mrv/                 the package
    config.py          seeds, design, contrasts, bounds, registered values
    load.py            inputs -> run table, and the input checks
    record.py          the intermediate record of section 12
    vendor/            verify_smokes.py copied unchanged (sha256 checked on import)
    stats.py           permutation tests, Holm, stratified bootstrap, equivalence
    analyse.py         sections 8.1 to 8.4 per model, and the verdicts
    describe.py        section 6.4 descriptives, section 6.2 compute and energy, section 9 voids
    power.py           section 7 recomputation
    fakedata.py        the fake-grid generator
  run_analysis.py      CLI: inputs -> results/ (CSV + a markdown report, with seeds and input hashes)
  tests/               the fake-data tests of section 9, and test-log.txt, the log of their full run
  verification/        the hand-checkable verification on a small fake grid (its README.md)
  power-results/       power and interval coverage recomputed under these tests (its README.md)
```

## 12. The intermediate record

Every analysis run writes `OUT/intermediate/`: every step between the grid's files and the final
tables, so that each step can be checked on its own. Its `README.md` lists the files. Values are
written at full precision (a float as the shortest decimal that reads back to the same number),
so that a recheck gives the same number to the last bit, where the final tables round to six
significant digits.

| step | file | rebuilt from it |
|---|---|---|
| each slot's run | `attempts.csv`: every key line, its exit code, manifest status, void cause, re-run causes and role | the set of analysed runs is the rows whose role is "analysed run of its slot" |
| reading a run's trace | `steps.csv`: one row per step | `reasoning_rate` = steps with `reasoning_chars` > 0 over steps. `reasoning_median_chars` = their median. `silent_turn`, `call_as_text_steps`, `prose_turns` and the canary columns likewise |
| the rest of a run's files | `run-evidence.csv` | the status used and why, the self-check and the call that showed it, GPU time as the sum of the server log's timing lines, the largest prompt, the power samples in the span |
| scoring an app | `scores.csv`, `probes.csv` | quality = round(100 x `weight_passed` / `weight_scored`, 2). Substituted, with the reason. API conformance = pass / (pass + fail) |
| the units of each test | `test-units.csv`, `test-strata.csv` | n, the arm means and the estimate: b minus a, exp of it for a ratio of geometric means, b over a for a ratio of means |
| each interval | `test-detail.csv`, `bootstrap-replicates.csv.gz` | a bootstrap interval is `numpy.quantile` (linear) of the finite replicates at lo = (1 - level) / 2 and 1 - lo, in double precision. A Newcombe interval from its recorded Wilson pieces. A difference of two estimates from the two it combines |
| each permutation test | `test-detail.csv`, `permutation-statistics.csv.gz` | `extreme` = the permuted statistics at least as extreme as the observed one (within the recorded tolerance, in the test's direction). p = (1 + extreme) / (permutations + 1) |
| Holm | `holm.csv` | in rank order, the running maximum of min(1, multiplier x p) |
| verdicts and X | `verdicts.csv` | the rule that decided each verdict, and how X was computed |
| descriptive intervals | `describe-replicates.csv.gz`, keyed by the `id` column of `descriptives.csv` | as for the bootstrap intervals above |

Every test and estimate has a `test_id`, the first column of `confirmatory.csv`,
`sensitivity.csv` and `exploratory.csv`, which joins the files. It is also the key of its
replicates and permuted statistics, and the random streams it used are recorded beside it
(their label and the 64-bit seed derived from the analysis seed). The record is written inside
the same run as the final tables and changes no random stream, so the final tables are the
same with or without it. On a fake grid of the full design (2,640 runs) the analysis took about
70 seconds and the record came to about 53 MB, most of it the replicates.

