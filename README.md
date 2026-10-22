# Does a coding agent's model need to re-read its own reasoning? Plan and protocol

This repository holds the pre-registration of the study: its protocol and study plan, the
frozen harness and grader the study runs and grades with, and the material that shaped and
calibrated them. It is the single place where the study's design is kept.

## The study in one paragraph

An AI coding agent is a language model inside a harness. Before each action the model writes a
private scratchpad (its reasoning). On the next step the harness either shows the model its own
earlier reasoning again or throws it away. The study measures whether that matters, by running
the same agent on the same tasks under three arms per model:

| arm | thinking | earlier reasoning shown again? |
|---|---|---|
| OFF | switched off | n/a |
| UNSEEN | on | no, discarded after each step |
| SEEN | on | yes, replayed in the conversation |

Each run builds a small web app (a message board or a kanban board) from a written spec. The
study compares how often runs fail, how many steps they take, and the quality of the apps they
build, graded blind by a human with fixed rubric cards.

## Status

**Pre-registration draft.** The harness and the grader are frozen, and the grader is
calibrated. The grid's schedules and seeds are fixed, and the analysis code is written and
tested on fake data. Still to do before the grid is run: the registration freeze, which hashes
everything here (protocol section 5.1 item 10). No study data exist yet.

## Contents

| folder | what it holds |
|---|---|
| `model-reasoning-visibility-plan/` | **the protocol** (`model-reasoning-visibility-study-protocol.md`), the registrable design, and **the study plan** (`model-reasoning-visibility-study-plan.md`), the full working record behind it. These two files are the source of truth. |
| `harness/` | the archive of the frozen harness and grader (see below) |
| `rubrics/` | the grader, unpacked for reading: the two rubric cards (`*.rubric.md`, `*.rubric.json`), the grading rules (`README.md`), the commands in order (`GRADING-COMMANDS.md`) and the grading scripts. Identical to `tasks/rubrics/` in the archive. |
| `calibration/` | the grader's training round: the score sheets, API probe files and setup logs of the 66 certifying-smoke apps, under blind ids. Training only. Never analysed. See its `README.md`. |
| `grading/` | a copy of the precedents log: how the cards apply to cases they did not foresee. The live log is kept beside the grid's grades. |
| `probe-prompts/` | the prompt each arm actually renders, per model, from the prompt probe (protocol section 4.2). See its `README.md`. |
| `marker-tests/` | the per-model replay test: a codeword planted in replayed reasoning and asked back, showing that the SEEN arm's reasoning actually reaches each model |
| `analysis/` | the analysis code (Python, numpy only), its design (`DESIGN.md`), its fake-data tests (`tests/`, with the log of the full run), the power and interval-coverage figures recomputed under it (`power-results/`), and a hand-checkable verification on a small fake grid with an Excel workbook (`verification/`). Run `python3 -m unittest -v tests.test_analysis` from that folder. |
| `registration/` | the grid's schedules and their sha256 (`schedules/`) |

## The frozen harness and grader

| | |
|---|---|
| repository | `eval-coding-agent`, which is private: the agent, the run wrappers, the tasks and the grader in `tasks/rubrics/`. The archive below is the public copy of its frozen code. |
| tag | `model-reasoning-visibility-plan-freeze-101926`: the protocol's `study-freeze` and `grader-freeze` |
| commit | `90a4758` |
| archive | `harness/eval-coding-agent-model-reasoning-visibility-plan-freeze-101926.tar.gz` (95 files, identical to the tag) |
| archive sha256 | `6ee3bb5808338941662dcec67fe0e4936975474a2e3da0a5b48b7659af95066b` |

The harness repository itself stays private. Everything the study runs and grades with is in
the archive. The grid runs from this tag. It differs from commit `5ac366f`, from which the certifying smoke
was made, only in `tasks/rubrics/`, the grader, which no run reads: every file a run executes
or reads is the one the smoke certified (protocol section 5.1 item 1).

## Related records

| what | where |
|---|---|
| certifying smoke set (66 runs, not study data) | [doi:10.5281/zenodo.23239989](https://doi.org/10.5281/zenodo.23239989) and `github.com/achintmehta/model-reasoning-visibility-study-smoke-runs` |
| OSF pre-registration | to be added at the registration freeze |
| grid data | to be released once the grid's grading has ended (protocol section 11) |

## Not here yet

The registration record of everything frozen (the grid's schedules and their sha256 are
already in `registration/schedules/`), and, once the grid's grading has ended, the un-blinding
keys of the training round and of the grid.

## Licences

- **Code** (the grading scripts in `rubrics/`, the contents of the harness archive, and the
  analysis code) is released under the MIT licence (`LICENSE`).
- **Everything else** (the protocol, the study plan, the rubric cards and their rules, and all
  data) is released under the Creative Commons Attribution 4.0 International licence
  (`LICENSE-CC-BY-4.0.md`).

## Author

Achint Mehta, ORCID [0009-0004-4192-8750](https://orcid.org/0009-0004-4192-8750)
