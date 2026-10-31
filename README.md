# Does a coding agent's model need to re-read its own reasoning? Plan and protocol

This repository holds the pre-registration of the study: its protocol and study plan, the
frozen harness and grading material, the grades from the grading material's training round on
the certifying smoke's apps, and the material that shaped and calibrated them. It is the single
place where the study's design is kept.

## The study in one paragraph

An AI coding agent is a language model inside a harness. A model capable of reasoning writes
a private scratchpad (its reasoning) before every action. On the next step the harness can
either show the model its earlier reasoning again or throw it away. The study measures whether
that matters, by running the same agent on the same tasks under three arms per model:

| arm | thinking | earlier reasoning shown again? |
|---|---|---|
| OFF | switched off | n/a |
| UNSEEN | on | no, discarded after each step |
| SEEN | on | yes, replayed in the conversation |

Each run builds a small web app (a message board or a kanban board) from a written spec. The
study compares how often runs fail, how many steps they take, and the quality of the apps they
build (using blind grading by a human with fixed rubric cards).

## Status

**Frozen for registration, 2026-10-31.** The harness and the grading materials are frozen, and
the grading material is calibrated. The final study grid's schedules and seeds are fixed, and the
analysis code is written and tested on fake data. The registration freeze is made: the tag
`model-reasoning-visibility-registration-103126` holds everything here, and `registration/SHA256SUMS` the sha256 of every file
(protocol section 5.1 item 10). The grid starts once the protocol is registered on OSF. No study
data exist yet.

## Contents

| folder | what it holds |
|---|---|
| `model-reasoning-visibility-plan/` | **the protocol** (`model-reasoning-visibility-study-protocol.md`), the registrable design, and **the study plan** (`model-reasoning-visibility-study-plan.md`), the full working record behind it. These two files are the source of truth: the protocol alone is registered on OSF, and where the two differ, the protocol governs. |
| `harness/` | the archive of the frozen harness, task specifications and grading material |
| `rubrics/` | the grading material, unpacked for reading: the two rubric cards (`*.rubric.md`, `*.rubric.json`), the grading rules (`README.md`), the commands in order (`GRADING-COMMANDS.md`) and the grading scripts. Identical to `tasks/rubrics/` in the archive, except `README.md`, reworded after the freeze for readers: its opening lines are rewritten, it speaks of "the grader" instead of "you", it explains how the sample and the re-grade set are drawn, it says the study lead, the only grader, runs the draws, it says the precedents log starts empty for the grid, it gives the consistency bar as fixed rather than a draft, and two sentences that predated the quality sample now match the protocol (only the sampled apps are graded, and two of every cell's ten are re-graded). The archive holds the frozen copy. |
| `calibration/` | the grading material's training round on the 66 certifying-smoke apps: their score sheets, API probe results and setup logs, under blind ids. Used to calibrate the grading material, never analysed. See its `README.md`. |
| `grading/` | contains a copy of the precedents log: how the cards apply to cases they did not foresee. The live log is kept beside the grid's grades. |
| `probe-prompts/` | the prompt the server renders for each model and arm, from the prompt probe (protocol section 4.2). Used to check that each arm's prompt carries, or leaves out, the past reasoning as intended. See its `README.md`. |
| `marker-tests/` | the per-model replay test to verify that the SEEN arms were working as expected: a codeword planted in replayed reasoning and asked back, showing that the SEEN arm's reasoning actually reaches each model |
| `analysis/` | the analysis code (Python, numpy only), its design (`DESIGN.md`), its fake-data tests (`tests/`, with the log of the full run), the power and interval-coverage figures recomputed under it (`power-results/`), and a hand-checkable verification on a small fake grid with an Excel workbook (`verification/`). Run `python3 -m unittest -v tests.test_analysis` from that folder. |
| `registration/` | the freeze record: the sha256 of every file in this repository (`SHA256SUMS`), and the final study grid's schedules with their own sha256 (`schedules/`). See its `README.md`. |

## The frozen harness, task specifications and grading material

The frozen harness is provided as a source code archive under `harness/eval-coding-agent-model-reasoning-visibility-plan-freeze-101926.tar.gz`. It contains the source code for the agent, the task specifications (the message-board and kanban-board spec files) and the grading material (`tasks/rubrics/`, unpacked in `rubrics/`).

| | |
|---|---|
| repository | `eval-coding-agent`, which is private: the agent, the run wrappers, the tasks and the grading material in `tasks/rubrics/`. The archive below is the public copy of its frozen code. |
| tag | `model-reasoning-visibility-plan-freeze-101926`: the protocol's `study-freeze` and `grader-freeze` |
| commit | `90a4758` |
| archive | `harness/eval-coding-agent-model-reasoning-visibility-plan-freeze-101926.tar.gz` (95 files, identical to the tag) |
| archive sha256 | `6ee3bb5808338941662dcec67fe0e4936975474a2e3da0a5b48b7659af95066b` |

The harness repository itself stays private. Everything the study runs and grades with is in
the archive. The grid runs from this tag. It differs from commit `5ac366f`, from which the certifying smoke
was made. The difference between the two is only in `tasks/rubrics/`, which no run reads: every file a run executes
or reads is the one the smoke certified (protocol section 5.1 item 1).

## Related records

| what | where |
|---|---|
| certifying smoke set (66 runs, not study data) | [doi:10.5281/zenodo.23239989](https://doi.org/10.5281/zenodo.23239989) and `github.com/achintmehta/model-reasoning-visibility-study-smoke-runs` hold the 66 runs that certified the harness before the grid, whose apps the grading material was calibrated on. Not part of the study data. |
| OSF pre-registration | to be added once the protocol is registered |
| grid data (the study data: 2,400 runs, 2,640 with the optional tier 6) | not yet made. Released once the grid's grading has ended (protocol section 11): every grid run (its manifest, trace, tool-call record, console log, server log, environment record and the app it built), the score sheets, the API probe files and the grading setup logs, the final precedents log, the analysis outputs with their intermediate record, and the un-blinding keys of the grid and of the training round. Code under MIT, documents and data under CC BY 4.0, all scanned for credentials and personal data first. |

## Not here yet

The OSF registration's link, and, once the grid's grading has ended, the un-blinding keys of
the training round and of the grid.

## Licences

- **Code** (the grading scripts in `rubrics/`, the contents of the harness archive, and the
  analysis code) is released under the MIT licence (`LICENSE`).
- **Everything else** (the protocol, the study plan, the rubric cards and their rules, and all
  data) is released under the Creative Commons Attribution 4.0 International licence
  (`LICENSE-CC-BY-4.0.md`).

## Author

Achint Mehta, ORCID [0009-0004-4192-8750](https://orcid.org/0009-0004-4192-8750)
