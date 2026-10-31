# Calibration: the grader's training round

These are the grades of the training round that calibrated the grader before the actual grid
runs (protocol section 5.1 item 9). **These are training material only and no grade here enters any
analysis of the study.**

## What was graded

- **The apps:** the 66 apps of the certifying smoke (protocol section 5.1 item 6), one run per arm
  per condition per model, published on Zenodo (doi:10.5281/zenodo.23239990). 30 are
  kanban-board apps and 36 message-board apps.
- **Blind ids:** each app was copied under a fresh random six-digit id before grading,
  because the smoke's own run ids name the arm. The grader saw only these ids.
- **The un-blinding key** (blind id -> model, condition, arm, smoke run) is **not** included
  yet. It will be published once the grid's grading has ended, so that no result by arm reaches
  the grader before then.
- **Who and when:** one grader, the study lead, graded every app from 2026-10-11 to 2026-10-18,
  following `rubrics/README.md` and `rubrics/GRADING-COMMANDS.md`.

## Card versions

The rubric cards changed during the round, as calibration is meant to do: wording that left a call
unclear was rewritten (rubric README, "Calibration"). The sheets were graded under the
successive drafts of version 2.1 and then refreshed to version 2.2 (the frozen grading material, tag
`model-reasoning-visibility-plan-freeze-101926` of the harness repository) on 2026-10-18.
The refresh replaced only the card text copied into each sheet already graded. No result or note
changed.

Rubric items whose procedure changed during the round, so that earlier sheets were graded under the
older step:

- **KB-S1** became a nine-drag step ending on a "between" drag (it was ten drags, ending where
  it started). Four sheets that passed S1 under the old step were not re-graded under the new
  one: 157123, 613328, 706655 and 992726.
- **KB-F2, KB-F3, KB-F4** now fail whenever a card had to be seeded with `seed_card.py`, and
  **KB-R2** names seeded cards explicitly.
- **KB-D6, KB-D7** now state that they fail when no drop ever moves a card (this was already
  the card's Dependencies rule).

At the end of the round, on 2026-10-18, the sheets were checked item by item against the cards.
Results that did not follow them were corrected by the grader: drag items in 517146 and 333726,
KB-P1 in 730011, KB-S1 in 616618, and L0 in 489403 after checking its setup log. Accommodation
codes were also written into the launch items' notes where they were missing. Every sheet passes
`score_sheet.py check` against card version 2.2.

Where an install command differed from the form `grade_setup.sh` prints, the sheet's notes say
what was run: 520543 and 842377 (A0 without `--no-save`) and 616618 (A8 as one `npm install`
without `--no-save`). These commands installed the same versions the printed form would have.

The calls the cards left open in this round were settled during the round. They are not
carried into the precedents log, which starts empty for the grid (protocol section 5.3).

## Files

| folder | what it holds |
|---|---|
| `score-sheets/` | one `<blind id>.score.json` per app: every item's result (`pass`, `fail` or `skip`) and notes, the accommodations used, the grading date |
| `probe/` | one `<blind id>.api-probe.json` per app: the API conformance probe (protocol section 6.5), recorded apart from the score |
| `setup/<blind id>/<date-time>/` | one folder per run of `grade_setup.sh` which contains the logs for setting up the application: `grade-setup.log` (the install, the evidence for L0), `GRADER-ENV.txt` (Node, npm, the `before` date, lockfile hashes, OS, and a browser field that holds a placeholder, not the versions used: protocol section 5.3) and, where an A0 command was run, `a0.log`. Where `grade_setup.sh` was run more than once for an app, every run's folder is kept. |

A sheet's score is computed with `rubrics/score_sheet.py score <sheet>`.
