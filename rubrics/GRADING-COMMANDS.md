# Grading: the commands, in order

The same commands for every grading: a practice round on smoke runs, the calibration rounds,
and the grid. Only the setup of the session (part A) differs, and only in where the runs, the
list and the state are. The rules for each step are in `README.md` and the two cards; this
page is the order of the commands. Everything runs in WSL.

R=/mnt/d/eval-coding-agent/tasks/rubrics stands for this folder (at the grid: the checkout of
the `grader-freeze` tag).

## A. Before grading (whoever makes the lists, not the grader)

The un-blinding state lives in a state folder the grader does not open. For the grid it is the
harness's `blind-state/`; for a practice or calibration round, a folder of its own.

**Grid** (the runs are already in the blind layout, `<study root>/<model>/<task>/runs/<id>/`):

```bash
S=/mnt/d/eval-coding-agent/blind-state            # the harness's ledger and key
python3 $R/blind_tools.py sample --state $S --seed <seed fixed at the freeze> --draw tier1 \
    --per-cell 10 --models gemma-q4,qwen-q4       # the quality sample: the only apps graded
python3 $R/blind_tools.py draw  --state $S --seed <seed fixed at the freeze> --draw tier1 \
    --per-cell 2 --models gemma-q4,qwen-q4        # the re-grade set, from the sample
                                                  # (both once per tier, before it is graded)
# only if there is time to grade more of a tier, never because of results:
python3 $R/blind_tools.py extend --state $S --draw tier1 --to 12   # the 11th and 12th of every cell
python3 $R/blind_tools.py lists  --state $S --results <results folder> --models gemma-q4,qwen-q4
python3 $R/blind_tools.py lists --state $S --results <results folder> --models gemma-q4,qwen-q4
```

**Practice or calibration round** (smoke runs, whose folder names give the arm away):

```bash
S=~/practice/state                                 # never the study's blind-state/
python3 $R/blind_tools.py calibrate --state $S --to ~/practice/runs --round practice1 \
    /mnt/d/model-reasoning-visibility-research/smoke-runs/gemma-q4/kanban-board/execution/runs/301
python3 $R/blind_tools.py draw  --state $S --seed practice --draw practice1 --all   # if it will be re-graded
python3 $R/blind_tools.py lists --state $S --results <results folder> --calibration practice1
```

`lists` prints the list's path (`$S/lists/list-NNN.txt`). Give the grader that file, and the
values for part B: where the runs are, and the index.

## B. Once per grading session (the grader)

```bash
nvm use 24.21.0                                    # the runs' Node; grade_setup.sh stops if it differs
npm config get before                              # the study's date, 2026-09-22T00:00:00.000Z
npm config get allow-scripts                       # must print nothing (README, "Grader-side problems")
env | grep -i npm_config_allow                     # must print nothing
#   if either prints something: npm config delete allow-scripts --location=user
#   (or delete the line from ~/.npmrc or the global npmrc), then check again
export GRADING_ROOTS=<given in part A>             # grid: <study root>/<model> per model, ':'-separated
                                                   # practice: ~/practice/runs
export GRADING_INDEX=<state>/grading-index.tsv     # for re-grade ids; given in part A
export GRADING_RESULTS=<results folder>            # grid: /mnt/d/model-reasoning-visibility-research/grading
export GRADING_WORK=~/grading-work                 # on the Linux filesystem, never under /mnt
export GRADER_BROWSER="A: Firefox <version>; B, C: Edge <version>"   # recorded in GRADER-ENV.txt
export PATH="$R:$PATH"                             # grade_setup.sh and backend.sh by name
source "$R/grading-shell.sh"                       # grade_setup.sh then moves your shell into the app
```

## C. For each blind id, in the list's order

```bash
ID=<next id on the list>

# step 0: copy, clean, install (L0), and a blank score sheet
grade_setup.sh $ID                                 # read the install output and its summary; once the
                                                   # copy is ready, your shell is in its project root
#   A0 if the summary gives one: copy and run the whole command it prints (it saves its output)

# free the ports, then the declared launch (L1-L3)
ss -ltnp                                           # nothing may listen on the app's ports
cd "$GRADING_WORK/$ID/app"                         # or the folder grade_setup.sh names as the project root
npm run dev                                        # task 1.4; in its own terminal, left running
#   accommodations if the page does not work (README, "Accommodations"), at most 5 minutes

# in a second terminal, once the app has started
cd "$GRADING_WORK/$ID/app"
backend.sh status                                  # check it found the backend: "Backend: pid ..., port ..."

# the card's script, step by step, in windows A (Firefox), B and C (Edge), with:
backend.sh pause ; backend.sh resume               # kanban steps 9, 11, 12
backend.sh kill                                    # the restart step (message board 8, kanban 14); then
                                                   # Ctrl-C the rest, check the ports, npm run dev again
python3 $R/seed_card.py <backend port> <column> <text>...   # kanban, only if the interface cannot create a card

# the score sheet: $GRADING_RESULTS/$ID.score.json holds the card's steps in order, each with
# the items it scores; open it beside the app and fill in each item's result and notes as you go
python3 $R/score_sheet.py check "$GRADING_RESULTS/$ID.score.json"

# last, with the sheet complete and the app still running
python3 $R/api_probe.py <kanban-board|message-board> <backend port> $ID --out "$GRADING_RESULTS/probe"

# stop the app: Ctrl-C in its terminal, then check the ports are free
ss -ltnp
```

Commit the results folder after every session (the score sheets, the probe files, and `setup/`, which holds
each setup's log, grader environment and A0 output):

```bash
cd "$GRADING_RESULTS" && git add -A && git commit -m "grading session $(date +%F)"
```

## D. After the gradings (whoever makes the lists)

```bash
python3 $R/blind_tools.py lists --state $S --results <results folder> ...   # the next list: new first
                                                                           # gradings and the re-grades whose 14 days have passed
python3 $R/merge_grades.py --results <results folder> --state $S          # scores.csv and the consistency check
less <results folder>/merge/consistency.md                                 # the grader may read this one
python3 $R/blind_tools.py fresh --state $S --seed <seed> --draw <name> \
    --task <task> --results <results folder>                               # only after a check below the bar
python3 $R/merge_grades.py --results <results folder> --state $S \
    --unblinded <file outside the grader's reach>                         # for the analysis, never for the grader
```

For a practice round, keep its results folder apart from the study's `grading/` (for example
`~/practice/results`), so that no practice sheet is ever merged with the study's.
