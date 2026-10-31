# registration: the record of what was fixed before the grid

In this study, every model is run many times on the same app-building tasks, under each of its
arms (OFF, UNSEEN and SEEN). This folder holds the files that fix the schedule of those runs
before any grid run is made, so that anyone can later check that the grid was run as registered
(protocol section 5.1, item 10, "Registration freeze"). It holds the freeze record of
2026-10-31 (`SHA256SUMS`, below) and the grid's schedules (`schedules/`).

## SHA256SUMS: the freeze record

`SHA256SUMS` holds the sha256 of every file in this repository at the tag
`model-reasoning-visibility-registration-103126`, except itself. That includes the protocol and the study plan,
the analysis code with its tests, their log, the power results and the verification record,
the archive of the frozen harness and grader (`harness/`), the grading material unpacked for
reading (`rubrics/`), the grader's training round (`calibration/`), the precedents log
(`grading/`), the prompt probes, the marker tests, the grid's schedules, the READMEs and the
licences. The OSF registration of the protocol cites the tag and the sha256 of this file, so
that it names exactly what was frozen with it.

To check that nothing has changed since the freeze, from the repository's top folder:

```bash
git checkout model-reasoning-visibility-registration-103126
sha256sum -c registration/SHA256SUMS
```

Every file should report `OK`. The repository's `.gitattributes` turns off git's line-ending
conversion, so a checkout on any system gives the same bytes.

## schedules/: the exact list of grid runs

To make the schedules, we started each batch command of protocol section 5.2 exactly as it will
be started for the grid, in the grid's own checkout of the frozen harness tag
(`model-reasoning-visibility-plan-freeze-101926`), but with the file `batch-state/STOP`
created first. With `STOP` set, the batch driver
(`run_thinking_batch.sh`) writes its schedule and signature and stops before the first run.
The files were made on 2026-10-21 and copied here unchanged.

| file | batch command | tier | models | runs |
|------|---------------|------|--------|------|
| `schedule-real-gemma-q4.tsv` | `REPLICATES=20 ./run_thinking_batch.sh gemma-q4` | 1 | Gemma-4-31B-it | 360 |
| `schedule-real-qwen-q4.tsv` | `REPLICATES=20 ./run_thinking_batch.sh qwen-q4` | 1 | Qwen3.6-27B | 360 |
| `schedule-real-seed-q4.tsv` | `REPLICATES=20 ./run_thinking_batch.sh seed-q4` | 2 | Seed-OSS-36B-Instruct | 360 |
| `schedule-real-gptoss-20b.tsv` | `REPLICATES=20 ./run_thinking_batch.sh gptoss-20b` | 3 | gpt-oss-20b | 240 |
| `schedule-real-glm-q4.tsv` | `REPLICATES=20 ./run_thinking_batch.sh glm-q4` | 4 | GLM-4.7-Flash | 360 |
| `schedule-real-qwen-moe-q4-gemma-moe-q4.tsv` | `REPLICATES=20 ./run_thinking_batch.sh qwen-moe-q4 gemma-moe-q4` | 5 | Qwen3.6-35B-A3B, Gemma-4-26B-A4B-it | 720 |
| `schedule-real-muse-q4xl.tsv` | `REPLICATES=20 ./run_thinking_batch.sh muse-q4xl` | 6 (optional) | Muse Glimmer 30B | 240 |

That gives us 2,640 runs in all: 2,400 for the committed tiers 1 to 5 and 240 for the optional
tier 6. Every model has 120 runs per arm: 2 tasks, 3 conditions and 20 replicates. gpt-oss-20b
and Muse Glimmer have no OFF arm, so they have 240 runs instead of 360.

The folder has three kinds of file:

| file | what it is |
|------|------------|
| `schedule-real-<set>.tsv` | the schedule: one line per run, giving its model, task, condition, arm and replicate (see below), in the order the batch runs them |
| `schedule-real-<set>.sig` | the signature of the configuration the schedule was made from |
| `SHA256SUMS` | the sha256 of all fourteen files above |

### The schedule files

Each line is one run, with seven tab-separated columns and no header line:

| column | meaning | example |
|--------|---------|---------|
| 1 | the run's place in the batch order, from 1 | `4` |
| 2 | the model key (the run wrapper's name for the model) | `gemma-q4` |
| 3 | the task: `message-board` or `kanban-board` | `message-board` |
| 4 | the condition: `no_verification`, `execution` or `interactive` | `no_verification` |
| 5 | the arm: `off`, `unseen` or `seen` | `off` |
| 6 | the run's short id: the arm's digit (1 for OFF, 2 for UNSEEN, 3 for SEEN) followed by the two-digit replicate | `102` |
| 7 | the run's label: model, task, condition, arm and replicate | `gemma-q4/message-board/no_verification/off/r02` |

The order is one model at a time (in the tier 5 file, all of Qwen3.6-35B-A3B's runs come
first), then task, then condition, then replicate. Within each replicate the arms follow
each other in the order OFF, UNSEEN, SEEN, so the arms of a cell are run side by side over the
whole batch and not one after another.

A schedule names each run's cell, but not its blind id. Blind ids are given at run time and
recorded only in the blind key, which is released once the grid's grading has ended (protocol
section 11). Publishing the schedules therefore does not reveal which graded app belongs to
which arm.

### The signature files

A schedule file is never regenerated, which is what freezes it. That leaves one risk. Suppose
a setting the schedule was made from changes later, for example a model is given a third arm,
or the run wrapper starts sending different switches. The batch driver would still follow the
old schedule, and nothing would warn that the schedule no longer matches the settings. The
signature guards against that. It is the sha256 of six lines: the mode (`real`), the replicate
count, the task list, the condition list, each model's arms, and the sha256 of the run wrapper
(`run_one_with_server.sh`), which holds the rest of what an arm sends (the model file, the
`chat_template_kwargs` and any preamble). Before every run the batch driver recomputes the
signature, and it stops if the result differs from the `.sig` file.

### Checking the files

From this folder's `schedules/`, check that no file has changed since it was hashed:

```bash
sha256sum -c SHA256SUMS
```

Every file should report `OK`.

A signature can be recomputed from the harness archive in `harness/` of this repository. For
example, for `schedule-real-gemma-q4.sig`, from the repository's top folder:

```bash
mkdir -p /tmp/harness
tar xzf harness/eval-coding-agent-model-reasoning-visibility-plan-freeze-101926.tar.gz -C /tmp/harness
runner=$(sha256sum /tmp/harness/eval-coding-agent-model-reasoning-visibility-plan-freeze-101926/run_one_with_server.sh | cut -d' ' -f1)
printf 'mode=real\nreplicates=20\ntasks=message-board kanban-board\nconditions=no_verification execution interactive\narms[gemma-q4]=off unseen seen\nrunner=%s\n' "$runner" | sha256sum
```

The result should equal the line in `schedule-real-gemma-q4.sig`. The run wrapper's sha256 is
`a95bfd7cb2aba3c079af673a6a555388d91749634feba6faa977954635f37465`. For another file, change
the `arms[...]` line: `arms[gptoss-20b]=unseen seen` and `arms[muse-q4xl]=unseen seen` for the
two-arm models, and for the tier 5 file two lines, `arms[qwen-moe-q4]=off unseen seen` then
`arms[gemma-moe-q4]=off unseen seen`.

The schedules themselves can be made again from `gen_schedule()` in the archive's
`run_thinking_batch.sh`, which writes the same lines byte for byte. All seven schedules and all
seven signatures were checked this way against the archive.

## Who uses these files

- **The batch driver** reads its schedule and signature from `batch-state/` in the grid's
  checkout. These copies are the public record of them.
- **The analysis code** builds its fake test grid from these schedules, so it is tested on
  the real design and not an approximation of it (`analysis/DESIGN.md`).
- **A reader** can compare the released grid data (protocol section 11) with these schedules
  to see that every scheduled run was made, and no unscheduled one.
