# Does a coding agent's model need to re-read its own reasoning?

**Status: frozen for registration, 2026-10-31.**

- No study data exist. The smoke and probe runs that shaped this protocol (section 2.6), and the
  training round that calibrated the grader on the certifying smoke's apps (section 5.1 item 9), are
  excluded from analysis by design, and every grid run is made from scratch under it.
- Done: the harness and the grader are frozen together (section 5.1 item 1), and the grader is
  calibrated (item 9). The grid's schedules are made (item 10) and the seed of its draws is
  fixed (section 5.3). The analysis code is written and tested on fake data, and the power
  figures are recomputed under it (section 7). The registration freeze is made (2026-10-31, item
  10), and the grid starts only once this protocol is registered on OSF.
- This protocol is the study's registered design, and it is what is registered on OSF.

---

## 1. The question and the hypotheses

### 1.1 The question

An AI coding agent is a language model inside a harness: the model decides each action, and
the harness carries it out and keeps the conversation. Before each action the model thinks out
loud: it writes a private scratchpad ("the tests fail because the import is wrong... let me
check the config first"), and then it picks the action, open a file, run a command, make
an edit.

What happens to that scratchpad next is something almost nobody decides on purpose: on the
next step, does the harness show the model its own earlier scratchpads again, or are they
thrown away?

Think of two ways of working at a desk. In one, every sticky note you ever wrote stays in
front of you. In the other, someone quietly bins each note the moment you finish writing
it: you still *did* the thinking. You just never see it again.

Both setups exist in the real world, and the industry disagrees about which is right.
Anthropic and DeepSeek require the notes to be passed back when tools are in use. OpenAI
hides them on its servers, so a caller could not show them again if it wanted to. And
most home-built setups running open models quietly bin them without anyone choosing to.

This study measures whether it matters. To make "having the thought" a measured thing rather
than an assumption, it also runs the agent with the model's thinking switched off. That
gives a ladder of three setups (no notes, notes written but binned, notes kept) and two questions, asked in
order: does writing the notes change what the agent does, and does keeping them change it
further? The second is the primary question. The first is the secondary one.

### 1.2 Why it could matter, in either direction

- **Memory.** The scratchpad is the model's only record of its own plan. Without it the model
  may have to re-derive decisions, take more steps, or contradict itself: or it may do
  better, because a long trail of old thoughts is also something to wade through on every
  step.
- **Cost.** Keeping the notes means re-sending every past scratchpad on every step, so the
  conversation grows faster, each step costs more, and the context window fills sooner. That
  much is arithmetic. What it buys is the question.
- **Formatting stability.** Some models were trained with their thoughts present in the
  history (OpenAI's format for its open models carries reasoning between tool calls, and
  DeepSeek's and MiniMax's APIs require it), others with past thoughts stripped (the standard
  Qwen template). A model shown a history of a shape it never saw in training may stumble, so
  the effect may depend on each model's upbringing.
- **Reliability.** A model stuck repeating a failed action might notice "I already tried
  this" only if it can see that it did: or having the thought may be what matters, and
  remembering it adds nothing.

This study aims to publish controlled comparisons, on open models run locally, where both 
setups can be built exactly and checked.

### 1.3 Hypotheses

Every hypothesis is tested within each model separately: each contrast compares a model
with itself, and each model is its own replication (section 8).

**H1: visibility (primary).** Runs in which a model is shown its own past reasoning (SEEN)
differ from runs in which that reasoning is discarded after each step (UNSEEN) on at least one
of three behaviour measures: failure incidence, steps to finish, and app quality (section 6.1).
This is kept as two-sided, because the mechanisms in section 1.2 point both ways. Tested in 
every model that is run: the seven of tiers 1-5, which are committed, and Muse Glimmer if 
the optional tier 6 is run (section 5.2).

**H2: generation (secondary).** Runs in which a model reasons and the reasoning is then
discarded (UNSEEN) differ from runs with thinking switched off (OFF) on the same three
measures. This is also kept two-sided: agents whose model does not think first are usually
expected to fail more (section 10), but in the smoke runs both Qwen models' OFF arms finished more often than their UNSEEN arms, so no
direction is assumed. Tested in the six models that have an off-switch (section 3).

Following three directional hypotheses are about how visibility acts come from the smoke runs
(section 2.6). Each is stated with the observation behind it, and all three compare UNSEEN with 
SEEN in every model that is run. (The smoke-run observations predate Muse Glimmer.

**H3: thinking that stays visible keeps going.** A model reasons on a larger share of its
steps in SEEN than in UNSEEN. In the 2026-09-26/27 smoke set every model reasoned on
98-100% of its SEEN steps and on 58-100% of its UNSEEN steps. Six of the seven reasoned less
often in UNSEEN, and the seventh, GLM-4.7-Flash, reasoned on every step in both.

**H4: seeing substitutes for producing.** On the steps where it reasons, a model writes less
new reasoning in SEEN than in UNSEEN: a model that can see what it already worked out does not
work it out again. In each of the two seven-model smoke sets (section 2.6), six of the seven
models wrote less reasoning per reasoning step in SEEN (median characters), a different model
being the exception in each.

**H5: silent turns come from discarded thinking.** A run is more likely to contain a turn with
neither text nor a tool call in UNSEEN than in SEEN. Across the two seven-model smoke
sets, 18 of the 21 such turns came in UNSEEN runs and none in SEEN. The rendered prompt
suggests why, at least for Qwen: in UNSEEN its template writes every earlier turn with an empty
think block and opens a new one for the reply (a transcript in which the model apparently
never thinks) and the model closed the turn inside the open block.

**Estimated, not tested: cost.** SEEN costs more per step by construction. The study reports
how much more per run, per model, with intervals (section 6.2).

**How the error rate is controlled.** For each model the tests fall into three families: H1's
three measures, H2's three measures, and H3-H5. Holm's correction is applied within each
family at alpha = 0.05. H1 and H2 are the questions the study was built to answer and keep their
power. H3-H5 are claims about mechanism, suggested by the smoke runs, and are held to an error rate
of their own instead of diluting the other two. No correction is made across families or
across models: each model is a separate replication with its own 120 runs a side, reported on
its own, and the study's cross-model statements count models ("in five of the seven") rather
than pooling them (section 10).

**Two shapes registered for reporting, not tested.** Two further patterns from the smoke runs are written
down now, so that seeing them in the grid is confirmation rather than discovery:

- *Qwen3.6-27B's ladder may not be monotonic.* In the 2026-09-26/27 smoke set it finished 1 of
  3 UNSEEN runs against 3 of 3 in OFF and in SEEN, the shape its earlier smoke sets had shown:
  thinking that cannot be seen may be worse than not thinking at all. Its twin,
  Qwen3.6-35B-A3B, showed the same shape by another route, and is reported on the same terms.
- *gpt-oss may end differently when it can see its reasoning.* In its smoke runs, three of the
  four attempts to close a run through its answer channel (output its server cannot parse) 
came in SEEN, and in its probe runs SEEN also stopped without a tool call in 2 runs and
  UNSEEN in none, with 8 turns without a call against 2. Served with `--swa-full` (section 4.3),
  those attempts now parse: none of its 18 attempts with the flag failed that way,
  against 5 of 20 without it. So in the grid the shape shows as replies without a tool call
  and stops, not as voids: in the diagnostic runs with the flag, SEEN stopped without a tool
  call in 2 of 9 runs and UNSEEN in none.

Both are reported per model x arm, with intervals and no test.

---

## 2. Design

### 2.1 Three arms, two contrasts

| | **OFF** | **UNSEEN** | **SEEN** |
|---|---|---|---|
| The model thinks before each action | no | yes | yes |
| Its past thinking is shown to it on later steps | (nothing to show) | no: discarded after each step | yes |

OFF -> UNSEEN measures what generating a scratchpad does (H2). UNSEEN -> SEEN measures
what re-reading it does (H1, H3-H5). An OFF arm exists only for a model with a working
off-switch. Gpt-oss-20b and Muse Glimmer have none and run UNSEEN and SEEN only.

**What differs between the arms, exactly.** These differ in two switches mainly, the thinking switch
and the visibility switch. The thinking switch is one field of the request body, 
`chat_template_kwargs`, and is set per model (section 4.1). The two thinking arms, SEEN and UNSEEN
send identical bodies. The visibility switch is whether each past assistant message in the conversation 
carries  its `reasoning_content` field: it does in SEEN and does not in UNSEEN. The visibility switch 
isthe harness configuration and it decides whether the reasnoning content is sent back (replayed)
to the server or not. In OFF condition there is no reasoning to show, and replay is set off 
explicitly rather than left at the harness default (section 4.1). Everything else (the system prompt, 
the task text, the tools, the samplers, the guards) is byte-identical across a model's arms, with 
one registered exception: the two Qwen models' OFF arm is sampled with their vendor's non-thinking profile
(section 4.5).

### 2.2 Tasks

A run asks the agent to build a small web app from a written spec, working alone until it
finishes, gets stuck, or is stopped.

| task | spec length | sha256[:16] | what the app must do |
|---|---|---|---|
| `message-board` | 5,516 chars | `296815692d88f5cb` | post text messages. Every connected client sees new ones at once. Messages survive a restart |
| `kanban-board` | 7,853 chars | `01d2615d510ad8b1` | a board of ordered columns. Create, move and reorder cards. Every client sees changes live. The board survives a restart |

Both specs mandate the same stack (a Node.js server with Express, an embedded PostgreSQL
(PGlite, the `@electric-sql/pglite` package), Server-Sent Events for live updates, and a
lightweight single-page frontend in vanilla JavaScript built with Vite) and both carry a known
trap: the spec calls the database "PGLite", the library exports `PGlite`, and the exact
capitalization matters. Both specs also require the app to start from a fresh checkout with one
command, `npm run dev` at the project root, with no manual step (task 1.4), and the kanban spec
asks for a way to create cards from the interface (task 4.6). The task text is byte-identical in
every condition and arm, and its hash is recorded in every run's manifest.

### 2.3 Conditions: three blocks

The harness gives the agent a set of tools to work with (its verification surface) and
three settings of it are used:

| condition | tools | in plain words |
|---|---|---|
| `no_verification` | `read_file`, `write_file`, `edit_file`, `list_dir`, `finish` | write the whole app "on paper": nothing runs and nothing is observed. Dependencies are installed by the harness after the run, for grading |
| `execution` | the above, plus `run_command`, `run_background_command`, `run_command_and_capture_output`, `list_background_commands`, `stop_background_command` | a terminal but no browser: install packages, build, start servers, run tests, read the output |
| `interactive` | the above, plus `browser_navigate`, `browser_click`, `browser_type`, `browser_drag`, `browser_read`, `browser_wait`, `browser_new_page`, `browser_switch_page`, `browser_close_page` | the same with a headless browser, driven through text: page structure, page text and console errors, no pixels |

The written instructions are byte-identical in every condition (section 4.6). Only the tool list
differs. The conditions are blocks, not treatments: the arms are compared inside each,
results are stratified by them, and they are never compared with each other as a finding.

**Why `no_verification` is included.** In the two feedback conditions the world acts as the
model's external memory (command output and page reads keep telling it where it stands) so
it can afford to forget its own plan. With nothing to run, the scratchpad is the only record
of what it decided three steps ago. If re-reading one's thoughts matters anywhere, it should
matter most there. Whether the visibility effect is larger without verification is therefore
pre-specified as an exploratory question: reported with intervals, never tested (section 8.4).
(The `interactive` condition is unrelated to the harness's `INTERACTIVE=1` flag, which lets a
human type into a run for debugging and is never set for a study run.)

### 2.4 The grid

Twenty replicates in every task x condition x arm cell:

| task x condition | OFF | UNSEEN | SEEN |
|---|---|---|---|
| message-board x no_verification | 20 | 20 | 20 |
| message-board x execution | 20 | 20 | 20 |
| message-board x interactive | 20 | 20 | 20 |
| kanban-board x no_verification | 20 | 20 | 20 |
| kanban-board x execution | 20 | 20 | 20 |
| kanban-board x interactive | 20 | 20 | 20 |
| per arm, per model | 120 | 120 | 120 |

| | Gemma 31B | Qwen 27B | Seed-OSS | gpt-oss | GLM | Qwen 35B-A3B | Gemma 26B-A4B | Muse | total |
|---|---|---|---|---|---|---|---|---|---|
| arms | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 2 | |
| grid runs | 360 | 360 | 360 | 240 | 360 | 360 | 360 | 240 | 2,640 |
| smoke runs | 9 | 9 | 9 | 6 | 9 | 9 | 9 | 6 | 66 |
| all runs | 369 | 369 | 369 | 246 | 369 | 369 | 369 | 246 | 2,706 |
| machine time, grid | ~26 h | ~50 h | ~54 h | ~7 h | ~31 h | ~28 h | ~24 h | ~20 h | ~240 h |

Machine time is projected from the smoke set of 2026-09-27 (60 runs in 5 h 29 min, server
start and stop included) and, for Muse Glimmer, from its own six-run smoke set of 2026-09-30,
made in 30 min. The grid is each set 40 times over, arm for arm and condition for condition, though
not task for task, and nine runs a model (six for gpt-oss and Muse) make the per-model figures
rough. About ten days of continuous running, plus grading. Tiers 1-5 (2,400 runs) are committed.
Tier 6, Muse Glimmer (240 runs), is optional (section 5.2). App quality is graded on a seeded half of
every cell (section 5.3).

**Smoke runs** (one per arm per condition per model) are made before the grid and excluded
from analysis by design. They check that every block runs cleanly, calibrate machine time,
context windows and the token budget, tested the grading tools, and are the training rounds' apps (section 5.1 item 9). No grading of a
smoke app enters the analysis.

**Order.** One model is loaded at a time. Within each task x condition block the arms rotate
strictly (OFF, UNSEEN, SEEN, OFF, ... (UNSEEN, SEEN, ... for gpt-oss and Muse Glimmer)) so time of day, disk
state or a warming GPU cannot favour one arm. The full schedule is generated, hashed and
frozen before the first run.

### 2.5 Blinding, identity and seeds

Grid runs use the blind layout and each run is stored as `<root>/<task>/runs/<random 6-digit
id>/`, with no condition and no arm anywhere in the path, so whoever grades an app cannot be
steered by its folder name. Ids are drawn at random and burned in an append-only ledger
(`blind-state/blind-ids.txt`). Each run's condition, arm, model and file are recorded in its
`manifest.json` and in one line of the un-blinding key (`blind-state/blind-key.jsonl`), which
is kept outside the runs tree. The grader sees only ids. An app in the re-grade set has
two ids, one for its first grading and one for its re-grade (section 5.3), and the key holds
both.

Each run sends its replicate number (1-20) as the per-request sampling seed, the same number
in every arm. Runs are nevertheless analysed as independent draws and never paired: each
run's prompt carries its own random workspace path, and command output carries times and
process ids, so two runs with the same seed part ways within a few steps.

### 2.6 Smoke runs

Before this protocol was fixed, the study made several sets of smoke runs (2026-09-18 to
2026-09-27) and a number of targeted probes, on these models and on others later excluded
(Appendix A). None of them enters any analysis. The smoke-run figures quoted in this protocol come
mostly from the two smoke sets of all seven models made with this protocol's briefing, 60 runs
each: 2026-09-25/26 and 2026-09-26/27. Both predate the finish-nudge rule of section 4.4, and the
first also predates the file-state note and ran at a 12M-token budget. What the smoke runs
established is built into the protocol and cited where it matters:

- that a model card's off-switch has to be checked against what the model actually emits
  inside the agent loop (section 4.1).
- that the arms must be shown to differ in the prompt the server actually renders, not only in
  the request (section 4.2).
- that some failures happen inside a single reply, where no loop guard can see them, and need
  a terminal status of their own (section 4.4).
- that one reply without a tool call should not end a run that is otherwise working (section 4.4).
- that each model is to be run at its vendor's documented sampling, per thinking mode (section 4.5).
- the patterns behind H3-H5 and the two registered shapes (section 1.3).
- that every model is served with `--swa-full` (section 4.3): on gpt-oss it cut the share of attempts
  whose output the server could not parse from 9 of 20 to 3 of 18, across four sets made on
  2026-10-01 (the smoke and a control without the flag, a re-smoke and a diagnostic set with
  it (section 9)) and it is served to the other models too, so that every sliding-window model
  reuses its cache the same exact way.

---

## 3. Models

### 3.1 Roster

Eight open-weight models from six labs, all served the same way on one machine: four dense
and four mixture-of-experts, among them two within-lab pairs. One quantization per model, the
mainstream ~4-bit build, fingerprinted by sha256 in the study's registry. Compression level is
not varied for this study.

| model | lab | architecture | arms | context window | native window | wrapper key |
|---|---|---|---|---|---|---|
| Gemma-4-31B-it | Google | dense, 31B | 3 | 65,536 | 262,144 | `gemma-q4` |
| Qwen3.6-27B | Alibaba | dense, 27B | 3 | 262,144 | 262,144 | `qwen-q4` |
| Seed-OSS-36B-Instruct | ByteDance | dense, 36B | 3 | 262,144 | 524,288 | `seed-q4` |
| gpt-oss-20b | OpenAI | mixture-of-experts: 4 of 32 experts, ~3.6B active | 2 | 131,072 | 131,072 | `gptoss-20b` |
| GLM-4.7-Flash | Zhipu (Z.ai) | mixture-of-experts: 4 of 64 + 1 shared, ~3B active | 3 | 202,752 | 202,752 | `glm-q4` |
| Qwen3.6-35B-A3B | Alibaba | mixture-of-experts: 8 of 256 + 1 shared, 3B of 35B active | 3 | 262,144 | 262,144 | `qwen-moe-q4` |
| Gemma-4-26B-A4B-it | Google | mixture-of-experts: 8 of 128 + 1 shared, 3.8B of 25.2B active | 3 | 262,144 | 262,144 | `gemma-moe-q4` |
| Muse Glimmer 30B | Meta | dense, ~29.6B (its 1.8B vision encoder is not loaded) | 2 | 131,072 | 131,072 | `muse-q4xl` |

The context window is how much conversation (system prompt, task, every earlier turn and
tool output, and in SEEN the replayed reasoning) the server holds for the model, in tokens.
Set with `-c`, and a run that outgrows it ends as an overflow, an outcome (section 6.1). The
native window is the longest context the model file itself declares (`context_length` in
its GGUF header): the most the server can be given without extending the model's position
encoding, which this study never does. Every model runs at its native window where the
96 GB card can hold the attention cache at 16 bits with `--swa-full` (section 4.3), and otherwise at
the largest round window that fits: Seed-OSS at 262,144 of its 524,288 (its cache would need
about 137 GB at native), and Gemma-4-31B at 65,536 of its 262,144 (with `--swa-full` every one
of its layers keeps a full cache, about 0.9 MB a token, so the card holds some 89,000 tokens,
and its smoke runs never passed about 20,000). llama-server allocates the cache when it starts, so
a window the card cannot hold fails at boot, never during a run.

| model | file (all from unsloth's GGUF repos on Hugging Face) | bytes | sha256[:16] | registry key |
|---|---|---|---|---|
| Gemma-4-31B-it | `gemma-4-31B-it-Q4_K_M.gguf` | 18,323,733,440 | `38bd64c852c4b460` | `Q4_K_M` |
| Qwen3.6-27B | `Qwen3.6-27B-Q4_K_M.gguf` | 16,817,244,384 | `5ed60d0af4650a85` | `Q4_K_M` |
| Seed-OSS-36B-Instruct | `Seed-OSS-36B-Instruct-Q4_K_M.gguf` | 21,762,149,536 | `2d9f3c32a61f2668` | `Q4_K_M` |
| gpt-oss-20b | `gpt-oss-20b-F16.gguf` (its experts in the native 4-bit MXFP4 it ships in) | 13,792,639,168 | `4e4f9cd88d6456e4` | `F16` |
| GLM-4.7-Flash | `GLM-4.7-Flash-Q4_K_M.gguf` | 18,312,339,808 | `29837ed2c0fc5f51` | `Q4_K_M` |
| Qwen3.6-35B-A3B | `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf` | 22,134,528,992 | `ac0e2c1189e055fa` | `UD-Q4_K_M` |
| Gemma-4-26B-A4B-it | `gemma-4-26B-A4B-it-UD-Q4_K_M.gguf` | 16,947,541,728 | `f2c28b3dc4776931` | `UD-Q4_K_M` |
| Muse Glimmer 30B | `Muse-Glimmer-30B-UD-Q4_K_XL.gguf` | 15,878,222,368 | `82bece304887a313` | `UD-Q4_K_XL` |

* Only GLM files re-uploaded on or after 2026-01-21 are usable. GLM-4.7-Flash is a
mixture-of-experts model: in each layer a router scores its 64 experts for every token, and the
4 best-scoring ones, with one shared expert, process that token, their outputs mixed by
weights made from the scores. The model was trained to turn the scores into weights with a
sigmoid function, but the GGUF files published at its launch recorded softmax instead, from a
bug in llama.cpp's conversion, and llama.cpp applies the function a file records. With the
wrong function every token mixed its experts with the wrong weights, and the launch files
"looped": in use the model fell into repetition, writing the same text over and over, and its
outputs were poor. llama.cpp fixed the bug, and unsloth re-uploaded its files on 2026-01-21
with the right function in their headers (unsloth's GLM-4.7-Flash guide). The study's file is
that re-upload: its sha256 is the one Hugging Face publishes for it, and its header sets
`deepseek2.expert_gating_func` to 2, sigmoid.
* The three `UD-` files are unsloth's Dynamic quants. Their headers record the base type
`Q4_K_M`, and the registry keys them by their Dynamic rung so that no reader takes them for
the same recipe as a plain `Q4_K_M`. 
* For Muse Glimmer unsloth publishes no plain `Q4_K_M` at
all, so its four-bit file is `UD-Q4_K_XL`. Its header names no quantizer, which is why the
registry records its publisher as unknown. Each header also carries default samplers, which the explicit
per-request values of section 4.5 override on every request.

**gpt-oss** has no off-switch (its reasoning effort has low, medium and high, and no off) so
it runs two arms, at effort `medium`. OpenAI's format documentation expects its reasoning to
be carried between tool calls: it is the roster's model raised for a SEEN world, and its
UNSEEN arm tests it against its upbringing.

**Muse Glimmer 30B** has no off-switch either (its reasoning strength runs low, medium, high
and xhigh, with no off) so it too runs two arms, at `high`, its template's default and Meta's
advice for coding and agentic work. Its format carries reasoning as a separate message
addressed to itself, and its template shows that message for every past turn that has one.
Meta's documentation says nothing about keeping or dropping past reasoning, so neither arm
runs against its maker's advice. It joined the grid after its six-run smoke set
passed every gate (section 5.1).

**The two within-lab pairs.** Qwen3.6-35B-A3B and Gemma-4-26B-A4B-it are the
mixture-of-experts siblings of Qwen3.6-27B and Gemma-4-31B-it. Inside each pair the vendor,
the chat template (byte-identical, section 4.2), the switches, the request bodies and the samplers
are the same, so a pair is the one place where architecture can be read at all. It is not all
that differs, and every within-pair number is printed with the rest: about a tenth of the
active parameters, a different quantization recipe (`UD-Q4_K_M` against `Q4_K_M`), a
capability gap on the vendors' own benchmarks (Google's card puts the 26B below the 31B,
LiveCodeBench v6 77.1 against 80.0, tau^2 average 68.2 against 76.9), and, for the Gemma pair, a
different context window, because the twin's smoke runs overflowed the 31B's 65,536 tokens
while the 31B's never passed about 20,000. How the pairs are compared is in section 8.4.

**Architecture is described, never tested.** Every contrast is climbed inside one model, so a
model's architecture cannot confound a contrast. Architecture is listed beside every result,
and no claim is made about mixture-of-experts models in general.

### 3.2 Entry requirements

A model enters the grid only if it meets four requirements, in this order (Appendix A lists
the models that did not):

1. **A thinking mode whose past reasoning its served template can show.** Without it SEEN is
   the same prompt as UNSEEN.
2. **An off-switch inside the same checkpoint**, for the OFF arm. A model whose thinking cannot
   be switched off, or is a separate checkpoint, runs two arms at most.
3. **It fits the machine as frozen:** wholly on the 96 GB GPU at about four bits with its
   context window (the study never offloads to the CPU) served by the pinned engine with the
   template its own GGUF carries. A replacement template or a newer engine would be a
   deviation made for one model.
4. **It is fieldable on its smoke runs:** its arms run, it calls tools in its own format, and
   it finishes.

Every model then passes the same checks before its grid (section 5.1): registry fingerprint, the
marker test, the prompt probe, the thinking canaries in both directions, and the gates on its
smoke runs.

---

## 4. The frozen settings

Everything a run inherits apart from the two switches is fixed here (identical across a
model's arms but for one registered exception, the Qwen models' OFF samplers (section 4.5)) and
written into each run's `manifest.json`, so that drift is detected mechanically rather than by
memory. A run whose recorded settings differ from this section is
void (section 9).

### 4.1 How each model's thinking is switched

The claim that each rung of the ladder differs from the one below it in exactly one thing is
not about the harness's code. It is about six chat templates written by six labs. The switch
travels through three layers, and a failure at any of them is silent.

1. **The request body.** The harness sends an OpenAI-shaped `POST /v1/chat/completions` with
   one extra top-level field, `chat_template_kwargs`. It is not part of the OpenAI
   specification (it is an extension the open-weight serving stack shares) and a server
   ignores fields it does not recognise, so a misspelled switch errors nowhere and the arms
   quietly collapse into one. Only the behavioural checks of section 5.1 catch that.
2. **The server.** Run with `--jinja`, llama-server renders the chat template baked into the
   GGUF and makes every key of `chat_template_kwargs` a top-level variable of that render.
   Without `--jinja` it falls back to a built-in formatter that ignores the field, which is
   why `--jinja` is a frozen flag (section 4.3).
3. **The template.** Each template decides what those variables mean, and here the models
   diverge completely.

A request, for Gemma-4-31B-it in its SEEN arm, replicate 3:

```json
{ "model": "gemma-4-31b", "messages": [ ... ], "max_tokens": 32768,
  "chat_template_kwargs": {"enable_thinking": true, "preserve_thinking": true},
  "temperature": 1.0, "top_p": 0.95, "top_k": 64, "min_p": 0.0, "presence_penalty": 0.0,
  "seed": 3, "tools": [ ... ], "tool_choice": "auto" }
```

What each arm sends, per model:

| model | OFF | UNSEEN and SEEN (identical) |
|---|---|---|
| Gemma-4-31B-it, Gemma-4-26B-A4B-it | `{"enable_thinking": false, "preserve_thinking": true}` | `{"enable_thinking": true, "preserve_thinking": true}` |
| Qwen3.6-27B, Qwen3.6-35B-A3B | `{"enable_thinking": false, "preserve_thinking": true}` | `{"enable_thinking": true, "preserve_thinking": true}` |
| Seed-OSS-36B-Instruct | `{"thinking_budget": 0}` | no field: the template's default budget, unlimited |
| gpt-oss-20b | (no off-switch) | `{"reasoning_effort": "medium"}` |
| GLM-4.7-Flash | `{"enable_thinking": false, "clear_thinking": false}` | `{"enable_thinking": true, "clear_thinking": false}` |
| Muse Glimmer 30B | (no off-switch) | `{"reasoning_strength": "high"}` |

In every model, SEEN sends each past assistant message's `reasoning_content` and UNSEEN and OFF
do not. The manifest records `reasoning_replayed`, with the number of turns and characters
replayed. The arm is set by one variable of the run wrapper (`ARM=off|unseen|seen`), which
derives the body and the replay flag together and refuses to run if either is also set by hand.
The keep-history flags (`preserve_thinking`, `clear_thinking`) are sent in all three arms, so
what moves along the ladder is the thinking switch and the replay: and, in the two Qwen
models' OFF arm, the samplers (section 4.5).

What the templates in the study's model files do with it (section 4.2):

- **Gemma** (both models). With thinking off, the template pre-fills an already-closed, empty
  thought channel at the point where the model starts writing: the actual suppression
  mechanism. With it on, it adds a `<|think|>` token to the system turn. Both variables default
  to *off* when absent, so the thinking arms must ask. A past turn's thought is shown only if
  that turn comes after the last user message, *or* `preserve_thinking` is set and the turn
  made tool calls. The flag is needed because the harness's finish nudge (section 4.4) is a user
  message: without it, every thought before a nudge would vanish for the rest of the run. It
  does not rescue a turn that made no tool call (the kind of turn that triggers a nudge) 
which is why section 8.3 reports the primary contrast again over runs with no nudge.
- **Qwen** (both models). Off is a closed, empty `<think></think>` block. On leaves `<think>`
  open, so the model begins inside a thought, and a turn without reasoning is one where the
  model chose to close the block at once. A past turn's reasoning is shown if
  `preserve_thinking` is true *or* the turn comes after the last user message: a plain OR, so
  the flag closes the nudge gap completely.
- **Seed-OSS.** ByteDance exposes a thinking *budget*, not a switch. Budget 0 adds a line to
  the system prompt saying the thinking budget is 0 and pre-opens a budget-reflection block,
  which the model completes with a short fixed stub (133-159 characters in smoke runs): an OFF
  step carries a short reasoning field without the model thinking, which is why the OFF canary
  is written in terms of length (section 5.1). Past reasoning is shown unconditionally, with no
  last-user-message gate.
- **gpt-oss.** OpenAI's harmony format, with `analysis`, `commentary` and `final` channels.
  Its template reads past reasoning under another name (`thinking`). Llama.cpp bridges
  `reasoning_content` into it, so the contrast is real. But harmony renders *either* a turn's
  prose *or* its reasoning, never both, so SEEN substitutes the reasoning for the prose rather
  than adding it: a registered asymmetry, and a small one: in smoke runs 2% of its
  tool-calling turns carried any prose.
- **GLM.** With thinking off, the think block is closed at the point where the model starts
  writing. `clear_thinking: false` keeps every past turn's reasoning: the opposite polarity to
  Gemma's and Qwen's flag, and a plain OR, so it survives any nudge. Unset, every turn before
  the last user message shows a bare `</think>`. Because the template can also split
  reasoning out of a turn's text at a `</think>`, a stray marker left in the text would carry
  reasoning into UNSEEN. None of the 430 replies of its first smoke set had one.
- **Muse Glimmer.** Meta's ATEM format, close to harmony: each message names its recipient, 
`to=self` for reasoning, a tool's name for a call, `user` for prose. A past turn's
  `reasoning_content` is rendered as its own `to=self` message for every assistant turn that
  carries one, with no flag and no last-user-message gate, so SEEN keeps it whatever the
  nudge does. The template does not render a turn's prose when the turn makes tool calls, in
  every arm alike. In its smoke set the model never wrote prose beside a call. Its calls are
  parsed by a new parser in the pinned engine, so its parse voids are watched as gpt-oss's are
  (section 9). Its smoke set had none.

**Why OFF sends no reasoning back.** There is no reasoning in OFF, so replay is set off
explicitly in the harness rather than left at the default. For a well-behaved template this 
changes nothing. For one that writes boilerplate into the reasoning field, it decides 
whether the arm works. In smoke runs, replaying Seed-OSS's budget-0 stub silenced the model 
on 55% of its OFF turns (it saw a history in which each of its own turns said, in effect, 
*I have no budget to think*, and it went on producing nothing else) while with replay off, 
33 steps carried no silent turn at all.

**An OFF arm is a claim about the instrument.** A model card says how to turn thinking off.
Only the model's own output, step by step, inside the loop the study runs, shows whether the
switch actually takes any effect. The smoke runs checked every model this way, and the canaries
of section 5.1 re-check it on every smoke set. One model's switch leaks: Gemma-4-26B-A4B-it 
occasionally opens its thought channel with thinking off, 1,213 characters of planning in one 
OFF smoke run, and in another a runaway reply that the parser filed as reasoning. Its OFF arm is 
kept and watched: reasoning carried by OFF steps is counted per model in the grid (section 6.4), 
and the smoke gate lists its over-length OFF runs under a registered waiver instead of failing 
them (section 5.1).

### 4.2 The templates actually served, and the prompt probe

The prompt probe checked, for every model, that the treatment reaches the model: in the prompt
the server renders, the past reasoning is present in SEEN and absent in UNSEEN, and the
assistant's own prose is not lost between the two (gpt-oss excepted, section 4.1).

Each template was extracted from the study's own GGUF files, not taken from the vendor's
published version, and each matches, as served, the `chat_template_sha` that every run records
from the server (Gemma's extracted file differs only by a trailing newline, which the server
strips):

| model(s) | template sha256[:16], as served | UNSEEN -> SEEN on the live server | verdict |
|---|---|---|---|
| Gemma-4-31B-it, Gemma-4-26B-A4B-it | `aa3185dfc6505104` | +202 chars | additive, prose intact |
| Qwen3.6-27B, Qwen3.6-35B-A3B | `55d4931433fe502b` | +144 chars | additive, prose intact |
| Seed-OSS-36B-Instruct | `25b74a75d793cc03` | +196 chars | additive, prose intact |
| gpt-oss-20b | `70da0d2348e40aaf` | +102 chars | real. Substitutes reasoning for prose |
| GLM-4.7-Flash | `d63ad536c3c81880` | +158 chars | additive, prose intact |
| Muse Glimmer 30B | `114f55ebdc1804c1` | +232 chars | additive. A tool-call turn's prose is rendered in neither arm |

Each twin serves its sibling's template byte for byte, and the live probe rendered
byte-identical prompts for twin and sibling in all three arms, so inside a pair the treatment
is the same bytes.

**The prompt probe is a freeze gate.** `template_probe.sh` boots each model on its own file and
sends one canonical exchange per arm (each arm's body built by the wrapper's own code, as a
run's is) to the llama.cpp server's `/apply-template` endpoint, the path a real completion takes, the
server's own pre-processing included. It passes a model only when three things hold together:
the past reasoning is in the SEEN prompt, it is not in the UNSEEN prompt, and the assistant's
own prose has not disappeared between them (gpt-oss passes under its registered asymmetry,
section 4.1). It also checks that the arguments of past tool calls reach the prompt in every arm. A
probe that asked only whether the two prompts differ would pass a treatment that removed
content, which in the probes made before the freeze one model's did. No model runs its grid until it passes. All eight
have.

### 4.3 Serving (llama-server)

| setting | value | why |
|---|---|---|
| machine | one workstation: an NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition (96 GB), Windows with WSL2 | the GPU, its driver, the OS and the toolchain are recorded per run in `environment.txt` |
| engine | llama.cpp b10964 (commit `b29c606e2`), Windows CUDA 13.3 build, with the CUDA 13.3 runtime DLLs (`cudart64_13.dll`, `cublas64_13.dll`, `cublasLt64_13.dll`) beside `llama-server.exe` | pinned. Build and commit recorded in every run. The build zip, the runtime zip and their sha256s are kept with the study materials. Without the DLLs the server silently runs on the CPU, so the wrapper refuses to start a run unless GPU memory grows by at least half the model file's size once the server reports healthy |
| `-m`, `--alias` | the registry-hashed GGUF. The model name the agent asks for | the server is asked at every boot (`/props`) to confirm it serves that exact file. A mismatch aborts the run |
| `-c` | per model (section 3.1) | the model's native window where the card can hold its cache, otherwise the largest round window that fits (Seed-OSS, Gemma-4-31B). An overflow in the grid is an outcome (section 9) |
| `-np 1` | one request at a time | nothing shares the GPU or the cache with a study run |
| `-ngl 999` | every layer on the GPU | no CPU offload |
| `-fa on`, `-b 2048` | flash attention. Prompt batch size | pinned |
| `--cache-type-k f16 --cache-type-v f16` | the attention cache kept at 16 bits | cache precision is not a hidden second variable |
| `--jinja` | the model's own chat template | required for tool calls, for thinking to be parsed at all, and for the switch to reach the template |
| `--swa-full` | every model: a model with sliding-window attention keeps its whole attention cache | without it the server reuses gpt-oss's cached prompt only in part on nearly every turn, and its output failed the server's parser in 9 of 20 attempts. With it, 3 of 18 (section 2.6, section 9). Served to every model so that every sliding-window model (gpt-oss, both Gemma-4 models and Muse Glimmer) reuses its cache exactly. On Qwen3.6, Seed-OSS and GLM, which have no sliding-window layers, it changes nothing. It costs GPU memory: about 54 GB more for Gemma-4-31B at its 65,536-token window, 27 GB for Gemma-4-26B-A4B, 5 GB for Muse Glimmer and 3 GB for gpt-oss. G17 checks every run |
| `--seed 0` | the server's default seed | every request carries its own seed (section 2.5), which takes precedence |
| `--host 0.0.0.0 --port 7777` | the serving address | the wrapper refuses to start if anything already answers on 7777 |
| logging | `-lv 5`, the most detailed level | every run's server log keeps, for each request, the prompt the server rendered from the chat template and the model's raw output before parsing: so each run records for itself that its arm reached the template (beside the prompt probe of section 4.2), and any output the parser rejected is kept whole. The rendered prompt is the whole conversation, re-logged at every step: the 66-run certifying smoke wrote 1.69 GB of server logs (median 16.8 MB a run, at most 102 MB), so the grid's come to about 70 GB, about 4 GB compressed (`zstd -19` shrinks a log about 19-fold). Logging does not change what the model generates |

Each run's whole lifecycle (boot the server, prove it serves the right file on the GPU, run
the agent, stop the server, archive the server's log beside the run) is one call of
`run_one_with_server.sh`. Booting and stopping cost 6-12 seconds a run because the file stays
in the page cache, so there is no reason to keep a server alive between runs and give up
per-run isolation for it.

### 4.4 The agent (harness)

The agent is the `eval-coding-agent` harness. Each step is one model reply, which may call
tools. The tool results are appended to the conversation and the next step begins.

| setting | value | what it does |
|---|---|---|
| system prompt | "You are a software engineer. Your workspace directory is {workspace}. Implement the task described by the user by creating files in the workspace using the provided tools. Work until the task is complete, then call finish. Use only the tools provided to you." (sha256[:16] of the template `a1b949af9e7bda1c`), followed by the briefing (section 4.6) | identical for every model, condition and arm |
| reply cap | 32,768 tokens per reply | a harness guard, not a sampler. The same for every model and arm |
| client timeout | 3,600 s per reply | replies are not streamed. The margin covers a full 32,768-token reply at local speed |
| retries | a failed call is re-sent up to five times, and every retry is recorded (`api_retries`: the step, the kind (`timeout`, `connection`, `http_<code>`, `server_crash`) and how long the failed attempt ran) | a timed-out call is regenerated from zero, and a timeout falls on exactly the longest replies, so a smoke set with a timeout retry fails its gates (section 5.1). The reply cap and the timeout are coupled: at a larger cap a runaway reply would outlast the timeout and be silently re-rolled, so neither changes without the other |
| reasoning left in the reply text | moved to the reasoning field: when a reply's text holds a closing think tag (`</seed:think>`, `</think>`, `[/THINK]`, or Gemma 4's channel closer `<channel|>`), the text up to the last one is reasoning and what follows is the reply. An opening tag never closed splits there (Gemma's only with its channel name, `<|channel>thought`: a bare `<|channel>` has opened a tool call written as text, which stays in the reply and counts as `callTxt`). gpt-oss's channel syntax is not split. G4 fails on it. Each split is recorded in the trace, which keeps the server's message untouched beside it, and counted per run (`reasoning_recovered_turns`, `_chars`, `_markers`) | the server splits reasoning out only at an opening tag. Seed-OSS often starts thinking without one in UNSEEN (75 of 131 steps in the smoke of 2026-10-04, none in SEEN), and its thinking then reached the next prompt as reply text: UNSEEN showing past reasoning. The harness does what the server would have done had the tag been written. The rule names tags, not models, and applies to every turn of every arm, before the turn is counted, replayed or discarded |
| loop guards | `MAX_SAME_CALLS` 500, `MAX_CYCLE_REPEATS` 3, `MAX_BLOCKED_CALLS` 3, `MAX_REPEAT_STEPS` 30 | end a run as `stuck_looping` (the guard that fired is recorded) or `stuck_blocked_tool`. `MAX_REPEAT_STEPS` (30 consecutive steps in which every call repeats one already made) is the study's definition of "stuck in a loop", so a run made under other values is void |
| `MAX_STEPS` | 10,000 | effectively no step cap: the guards and the token budget end runs, never a step count |
| token budget | 20,000,000 tokens per run (`MAX_TOTAL_TOKENS`), set by the run wrapper | exhausting it ends the run as `token_budget_exhausted`, a non-completion. One value for the whole study. In the 2026-09-26/27 smoke set the heaviest run that finished used 6.2M tokens, 31% of it |
| finish nudge | after every turn without a tool call, the same user message: "You did not call any tool. If the task is complete, call the finish tool now; otherwise continue working using the provided tools." | protocol scaffolding, identical in every arm and condition. The run ends as `stopped_no_tool_call` only when the reply to a nudge has no tool call either. A reply cut off at a limit ends the run at once, un-nudged. Recorded as `finish_nudges` and `finish_nudge_steps` |
| command timeout | `run_command` waits 180 s for a command to exit. A command still running then is killed with every process it started (its whole session, so a child that moved to a process group of its own, as children of GNU `timeout` do, is killed too), and the result says so. `run_command_and_capture_output` stops at the duration the model gives it, the same way, and neither tool ever waits on a command's output pipes without a limit | killing only the command's shell would leave a server it had started in the foreground running, holding its port, while the tool reported it terminated: before this was fixed, that false result left one smoke run cycling for 50 steps. The same for every model and arm |
| file-state note | a `write_file` or `edit_file` call that leaves a file with exactly the bytes an earlier write or edit call of the run left it with gets one more line in its result: "NOTE: 4 write or edit calls in this run, this one included, have left client/index.html with exactly this content; the previous one was 2 calls ago." | a fact about the model's own calls, never about whether the content is right, so it adds no verification surface. It sits beside the notes the file tools already give on a no-op write and on a stale process, and it ends nothing. "Calls ago" counts every tool call since. A failed edit counts for nothing. An edit that leaves the file unchanged counts. Tallied in `file_state_repeats` (section 6.4) |
| workspace | fresh per run (`--clean-workspace`). Headless browser. `INTERACTIVE=0` | no human ever types into a study run |
| toolchain | Node v24.21.0 through nvm, with npm 12.0.2, for the whole study. Dependency resolution frozen with npm's `before` date, `2026-09-22T00:00:00Z`, and `prefer-offline`. All recorded per run in `environment.txt` | the agent runs `npm install` and reads the output, so Node and npm are part of what it sees. Every install (the agent's, the harness's post-run install in `no_verification`, and any later rebuild for grading) resolves identically. The task text does not ask for exact versions, which a model could not check in `no_verification`. Each run's `package-lock.json` is archived with it |
| provenance | every manifest records the file and its registry entry. The serving probe (build, file, window, template sha, the server's default samplers). The request body verbatim and the samplers. The loop guards. `reasoning_replayed`. `harness_git`, which names the commit and any uncommitted change. The task and prompt hashes. `api_retries` | the audit trail: a run whose recorded settings differ from this section is void |

**Why the nudge is repeated.** In smoke runs made under a rule that ended a run at its second
turn without a tool call wherever it fell, three runs were ended by two such turns 4, 7 and 21
steps apart, the model working normally in between: two of them by one-token replies, one
right after a diff had shown the model the one-letter difference that was its bug. The rule
used here looks only at two turns in a row. A turn without a tool call gets the nudge, and if
the model then calls a tool, the run goes on as if nothing had happened, however many such
turns the run has in all. The run ends only when the model answers the nudge without a tool
call as well, the sign that it has stopped working.

**Why a reply that fills the cap has a status of its own.** Some models loop *inside* a single
reply, emitting no tool call at all (one smoke-run reply, from a model later excluded, ran to
88,845 characters with "Let me do it." 768 times) and no loop guard can see that, because
the guards count tool calls across steps. A reply without a tool call that used the whole
32,768-token allowance ends the run as `runaway_no_tool_call`. One cut short below the cap
(in practice by the context window) ends it as `truncated_no_tool_call`, and the manifest
records the repetition measure behind either (`truncation_detected`), so a loop can be told
from a legitimately huge reply. When the conversation has already outgrown the window before
a reply starts, the server refuses the request (llama.cpp: HTTP 400,
`exceed_context_size_error`) and the run ends as `context_overflow`, with the server's token
counts and the run's own totals (tokens, reasoning, tool calls) in the manifest like any other
ending's. It is an outcome, so the run exits normally and the batch driver
never re-runs it (section 9).

### 4.5 Decoding

A model does not write a fixed next word. At each step it gives every possible next token a
probability, and the samplers are the settings that decide how one is picked from them.
Temperature sets how far the choice strays from the most likely token. `top_p` keeps only the
most likely tokens that together hold that share of the probability, and `top_k` only that
many of the most likely tokens. `min_p` drops any token far less likely than the best one. A
presence penalty makes a token that has already appeared less likely, against repetition.
`top_k` and `min_p` set to 0 are off.

Each model runs at its vendor's documented sampling, per thinking mode, identical across its
two thinking arms. Every value is sent explicitly on every request (including those set to
off) and recorded per run. `decoding-registry.json` is the source the wrapper reads, and a
smoke gate checks every run against it (section 5.1).

| model | mode | temperature | top_p | top_k | min_p | presence penalty | source |
|---|---|---|---|---|---|---|---|
| Gemma-4-31B-it, Gemma-4-26B-A4B-it | both | 1.0 | 0.95 | 64 | 0 | 0 | Google, one configuration for all use cases ([Ollama library](https://ollama.com/library/gemma4:31b), [31B card](https://build.nvidia.com/google/gemma-4-31b-it/modelcard), [26B card](https://huggingface.co/google/gemma-4-26B-A4B-it)) |
| Qwen3.6-27B, Qwen3.6-35B-A3B | thinking (UNSEEN, SEEN) | 0.6 | 0.95 | 20 | 0 | 0 | the cards' precise-coding profile ([27B](https://huggingface.co/Qwen/Qwen3.6-27B), [35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)) |
| Qwen3.6-27B, Qwen3.6-35B-A3B | non-thinking (OFF) | 0.7 | 0.80 | 20 | 0 | 1.5 | the cards' instruct-mode profile |
| Seed-OSS-36B-Instruct | both | 1.1 | 0.95 | off | 0 | 0 | the [card](https://huggingface.co/ByteDance-Seed/Seed-OSS-36B-Instruct)'s general recommendation |
| gpt-oss-20b | thinking | 1.0 | 1.0 | off | 0 | 0 | [OpenAI](https://huggingface.co/openai/gpt-oss-120b/discussions/21): "temp = 1.0 and top_p = 1" |
| GLM-4.7-Flash | both | 0.7 | 1.0 | off | 0 | 0 | the [card](https://huggingface.co/zai-org/GLM-4.7-Flash)'s settings for its agentic-coding evaluations (Terminal-Bench, SWE-bench Verified) |
| Muse Glimmer 30B | thinking | 1.0 | 0.95 | 64 | 0 | 0 | Meta's recommended settings ([card](https://huggingface.co/meta-models/Muse-Glimmer-30B)) |

Where a card offers a general profile and a task-specific one, the profile nearest to agentic
coding is used: Qwen's precise-coding profile over its general one, GLM's agentic-coding
evaluation settings over its default. Seed-OSS's alternative profile was tuned to a
customer-service benchmark and is not used.

**Why vendor sampling rather than greedy decoding.** Greedy decoding runs reasoning-tuned
models at an operating point none of their makers documents, and it leaves the twenty
replicates of a cell unable to differ except through numerical noise nobody chose. Because
every contrast is climbed inside one model, decoding that differs *between* models is not a
confound, provided it is constant across a model's arms.

**One registered limitation: the Qwen models' OFF arm.** Qwen documents different sampling for
its non-thinking mode, so both Qwen models' OFF -> UNSEEN contrast changes two things at once
(whether the model thinks and how it is sampled) and no analysis can separate them. Their H2
result is an *effectiveness* comparison, each mode as its vendor deploys it, and is labelled
so wherever it appears. The non-thinking profile's presence penalty of 1.5 is a strong
anti-repetition setting, so their OFF arm may look less loopy partly by construction. In smoke
runs it did finish more often than UNSEEN. The primary contrast is untouched: UNSEEN and SEEN
are both thinking mode at identical settings. Every other model uses one profile in all its
arms.

**Operational rules.** Every sampler is pinned explicitly, `top_k` 0 (off) included, because
llama.cpp applies its own defaults to anything a request omits. The server's defaults are
recorded per run beside what the request asked for. Samplers travel in the request body,
never as server flags. The request's extra fields carry only `chat_template_kwargs`: the
harness refuses a temperature or top_p passed there, because it would be silently
overwritten.

### 4.6 Instructions

The system prompt (section 4.4) is followed by one briefing, `universal`, byte-identical in every
condition, arm and model (sha256[:16] `c988f43155c49538`):

> Environment: the tools listed in this request are the complete set available to you. Tools
> not listed do not exist in this environment and cannot be installed or obtained. Review what
> is available and use whatever helps you complete and check your work. If execution tools are
> provided, they give you a live development environment: the commands you run through them
> execute for real in your workspace, on a machine with Node.js and npm installed and the npm
> registry reachable, so the packages you install and the servers you start are real. If no
> installation or execution tools are provided, author every required file completely from
> first principles; dependencies declared in package.json files are provisioned by the
> environment after you finish.

The briefing describes the environment and names no tool, and its conditional sentences read
truthfully under every tool set. It says what execution tools act on and never asks the agent
to use them, so an agent that does not run its app has not been misinformed about its
environment. (In smoke runs without the sentence about a live environment, one model
reasoned that it had no environment to run anything in, and another that its task was only to
create the files.)

**One briefing for every model, not each vendor's own system prompt.** None of the six vendors
publishes a recommended system prompt for general or agentic use of these eight checkpoints.
And whatever a model needs in its prompt, its own chat template already adds around the
study's system prompt, as the probe prompts show (section 4.2, `probe-prompts/`). For example:

- **gpt-oss.** A system message in OpenAI's harmony format, which names the model, its
  knowledge cutoff, the date of the request and the reasoning effort, lists the valid
  channels, and says that tool calls go to the commentary channel. The study's system prompt
  follows it as the developer message, with the tools written out as a TypeScript-style list.
- **Gemma.** The `<|think|>` token at the start of the system turn, which switches thinking
  on (the OFF arm's prompt does not have it), and the tools declared in Gemma's own format
  inside the same turn.
- **GLM.** A system block before the study's system prompt that tells the model it may call
  functions, lists the tools as JSON, and gives the format a call must be written in.

Nor would the design gain from per-model prompts: every contrast is inside one model, where the prompt is the same in every
arm, while prompts that differed between models would add a difference the study could not
separate from the models. What four of the six vendors (Google, Alibaba, Z.ai and OpenAI) do
publish is advice to keep a model's past reasoning between tool calls in agentic use. The
UNSEEN arm runs those models against that advice by design. That is the question, and the paper
says so.

**How each request is put together.** Every run is zero-shot: no example of a task or of a
solution is shown. There are no context files (such as `AGENTS.md`), skills, subagents or
hooks. A run's first request holds the system prompt (section 4.4), this briefing, the task text
(section 2.2) and the tool schemas of its condition (section 2.3). Every later request adds only the agent's
own replies, the tool results and the harness's two fixed messages, the finish nudge and the
file-state note (section 4.4). How the agent's past reasoning goes back into each request is the arm
(section 4.1). The harness assembles every request at run time, from the code of the frozen tag
(section 5.1 item 1), and records the request body verbatim (section 4.4, provenance).

---

## 5. Procedure

Everything below runs in WSL on the study machine, from the folder that holds the two scripts
that make runs. The runner, `run_one_with_server.sh`, makes one run: it starts the model's
server, runs the agent on the task and stops the server. The batch driver,
`run_thinking_batch.sh`, works through a whole schedule of runs with the runner, one at a time,
and tries a run again when the runner fails. They keep their state beside themselves,
in `blind-state/` (the id ledger and the un-blinding key) and `batch-state/` (schedules,
progress, log). Grading runs from the grader's own folder (section 5.3).

### 5.1 Before the grid

What was done before the grid, in order, with the rules each step set. Item 10, the
registration freeze, is the last of them.

1. **Freeze the code and the machine** (2026-10-19). The harness and the grader are
   committed at `90a4758` and tagged `model-reasoning-visibility-plan-freeze-101926`, the one
   tag this protocol calls both `study-freeze` and `grader-freeze`. The grid runs from it. Its
   archive, `eval-coding-agent-model-reasoning-visibility-plan-freeze-101926.tar.gz` (95 files,
   identical to the tag, kept in the plan repository, `harness/`), has sha256
   `6ee3bb5808338941662dcec67fe0e4936975474a2e3da0a5b48b7659af95066b`. It differs from `5ac366f`,
   the commit the certifying smoke was made from (item 6, tag
   `model-reasoning-visibility-study-freeze-100826`), only in `tasks/rubrics/`, the grader at
   card version 2.2, which no run reads: every file the runs execute or read is the certified
   one. Grid manifests therefore show `harness_git` `90a4758`, the smoke's `5ac366f`. The report
   says so. The earlier tags (`5ac366f`'s and `600a8d2`'s among them) and their archives are
   superseded.
   - Commit the harness repository (`eval-coding-agent`: `harness/`, the run wrapper, the
     batch driver and `decoding-registry.json`) and tag it `study-freeze`. Every grid manifest
     must then show the same `harness_git`, and the harness is not edited until the last run.
     The grid runs from its own checkout of the tag (a `git worktree`), whose wrapper runs the
     harness beside it, so nothing changed in the working copy (the rubric cards included) 
can reach a grid run.
   - The grader (`tasks/rubrics/` in the same repository: the rubric cards, their rules and
     the scripts that go with them) is committed in the same tag, the `grader-freeze` (the grader
     freeze) at the end of its calibration (item 9), before any grid app is graded. It is not edited after that either. The precedents log (section 5.3) is
     kept beside the grades, outside the tagged grader, so that rulings can be added after the
     grader freeze. The log as it stands then is hashed with the grader at the registration
     freeze (item 10).
   - The engine sees the GPU (`llama-server.exe --list-devices` lists `CUDA0`), and it must
     identify itself (`--version`) before every run and probe starts.
   - Node is pinned (`nvm alias default`), and npm's `before` date and `prefer-offline` are set.
   - On the Windows side: pause Windows Update for the batch, disable sleep, reserve the
     machine's LAN address in the router, and keep ports 3000, 5173-5175 (the apps) and 7777
     (the server) free. Turn Smart App Control off for the batch: when it is enforced, Windows
     refuses the engine's unsigned binaries and the server exits before printing anything, a
     fault logged only as event 3077 in `Microsoft-Windows-CodeIntegrity/Operational`.
2. **Fingerprint every model file**. Every file is entered in the registry (`quant-registry.json`): sha256, size,
   and what the GGUF header says.
3. **Marker test per model**. `probe_reasoning_replay.py --model-key <key>` plants
   a nonsense phrase in a past turn's reasoning, sending the wrapper's own thinking-arm body,
   and the model must be able to repeat it when the reasoning is replayed (ACCEPTED). The other
   direction is proven by the smokes: every UNSEEN run records `reasoning_replayed=false`, and
   every OFF run passes the length canary. A model that fails is dropped and its slot reported
   empty. No standby is named. All eight ACCEPTED: Muse Glimmer 30B on 2026-09-30, the other
   seven on 2026-10-05, each against its server as the wrapper at commit `600a8d2` starts it,
   with the probe's output archived per model. Qwen3.6-27B gave the codeword in its reasoning
   and an empty reply. That counts, because the codeword exists only in the replayed
   reasoning.
4. **Prompt probe per model** (`template_probe.sh`, section 4.2). Passed by all eight.
5. **Thinking canaries**. Each canary reads the run's
   trace, in which every step records what the server returned: the visible text, the reasoning
   field (`reasoning_content`, the part the server split off as thinking) and the parsed tool
   calls. The canaries judge the reasoning field by its *length*, not its presence, because a
   template can fill it with a short fixed text while the model is not thinking: Seed-OSS's
   budget-0 stub, 133-159 characters, fills the field on every OFF step (section 4.1). The line is
   drawn at 200 characters and applied to a run's longest step. A stub stays under it on every
   step. A model that is thinking goes over it on some step of every run, though most of its
   steps may be short. In the smoke set of 2026-09-27, no Seed-OSS OFF step was longer than
   134 characters, while every one of the 42 thinking-arm runs had a step of at least 608. The
   median thinking step, by model and arm, ran from 106 to 512 characters, and was under 200 in
   8 of the 14.

   One rule comes first. A reasoning field whose whole text is a tool call is a call filed in
   the wrong field, not thinking, and counts as no reasoning in every canary and measure. A
   field is a call when it is one of three things: a JSON object whose keys are the parameters
   of one of the harness's tools, every required one included, optionally in a code fence,
   wrapped as `{"name": ..., "arguments": ...}`, or followed by the tool's name. A field that
   begins with a call opener such as `<tool_call>` and ends with a call closer (one that begins
   `[TOOL_CALLS]` needs none), or nothing but call markup, such as a bare
   `</parameter></function></tool_call>`. A field with prose before or after a call is
   reasoning, unless it begins `[TOOL_CALLS]`. Separately, a step that made no call is counted
   as `callTxt` (section 6.4) when its reasoning or its text is such a payload, or holds any piece of
   call markup.

   - **OFF canary (gate G2).** Passes when no step of an OFF run carries more than
     200 characters of reasoning. G2's line also lists any misfiled call in an OFF run that
     would otherwise have crossed it. Seed-OSS's budget reports (the
     `<seed:cot_budget_reflect>` blocks its template writes at a budget of 0) are not counted:
     they report the budget and are not thought, and once reasoning left in the reply text is
     counted (section 4.4) a report split between the field and the text measured 229 characters. A failure means the model thought with thinking switched
     off, so its OFF arm is not an OFF arm, and the model runs two arms. The one registered
     exception is Gemma-4-26B-A4B-it, whose OFF arm is kept and watched (section 4.1): its over-length
     OFF runs are listed under a waiver instead of failing the gate.
   - **ON canary (gate G3).** Passes when each UNSEEN and SEEN run has at least one step with
     more than 200 characters of reasoning, and has reasoning (of any length) on at least a
     fifth of its steps. The first half catches a switch that yields only a stub. The second, a
     model that thinks on almost no step. The floor is low on purpose: a model reasoning on a
     third of its UNSEEN steps is showing an effect (H3), not a broken switch, and the lowest
     rate of any thinking-arm run in the smoke set of 2026-09-27 was 29%, in a Seed-OSS UNSEEN
     run. An arm that fails has no thinking to show or to hide, so the contrast it belongs to
     cannot be run.
   - **No think or channel marker in the reply text (gate G4).** Passes when no step's reply
     text, as the harness kept it (the text it replays) contains a think marker, opening or
     closing (`<think>`, `</think>`, `<seed:think>`, `</seed:think>`, `[THINK]`, `[/THINK]`), a
     channel marker of Gemma 4 or gpt-oss (`<|channel>`, `<channel|>`, `<|channel|>`,
     `<|message|>`) or, for Muse Glimmer, `to=self`: and any roster
     template's turn-structure marker (`<|im_end|>`, `<turn|>`, `<|end|>`, `<|eot|>`,
     `<seed:eos>` and the like), which is not reasoning but means the server mis-split the
     model's output. A think or channel marker there means reasoning sits in the
     text, which UNSEEN replays like any other text, so the model would see its reasoning in both
     thinking arms and the contrast would be void without any error. Closing markers count too,
     because of what the smoke set of 2026-10-04 showed: Seed-OSS often starts thinking without
     its opening tag in UNSEEN (75 of 131 steps, 2 of 23 in OFF, none in SEEN), so the server
     files the whole thought as reply text, closing tag and all, and the next prompt carried it
     word for word. The harness moves such text to the reasoning field (section 4.4), so a
     marker G4 still finds is a split the harness missed. That includes Gemma 4's thought
     channel, after a Gemma-4-26B-A4B OFF reply in the smoke of 2026-10-05 opened `<|channel>`
     and ran to the reply cap inside it.
     A split made at an opening tag that was never closed assumes the thought ran to the end
     of the reply (the one case where its end is inferred rather than marked by the model) so
     the gate counts those steps apart (`atOpen`) and lists each for checking by hand.
     The gate recomputes the recovered reasoning itself and counts it as reasoning in
     G2, G3 and the descriptives (`recov`).
   - **A silenced OFF arm is not usable.** This rule is judged, not computed: the gate report's
     descriptives count, per model x arm, the turns with neither text nor a tool call, and how
     each run ended. An OFF configuration that leaves the model silent often enough to stop
     runs completing has no usable OFF arm, and the model drops to two arms. Seed-OSS is why
     the rule exists: replaying its budget-0 stub silenced it on 55% of its OFF turns, until
     reasoning replay was set off in every OFF arm (section 4.1).
6. **The certifying smoke, and its gates** (2026-10-07, commit `5ac366f`). 66 runs,
   6.3 hours from the first run's start to the last run's end (6.07 hours of run time, section
   6.2), and every run's `harness_git` that commit. Every gate passed, one (G2, for
   Gemma-4-26B-A4B-it's OFF arm) by a registered waiver. There was no void and no failed
   attempt, and 23 steps had reasoning moved out of the reply text, all at a closing tag. It
   replaces the sets made at `600a8d2`, `d11e15b`, `2ea877a` and `a48c79f`, each superseded by a
   harness change (section 4.4 and its command-timeout row). The set is
   published on Zenodo,
   doi:10.5281/zenodo.23239990 (version v1.0.0, all versions doi:10.5281/zenodo.23239989). One run per arm per condition per model,
   66 runs, made from the commit the grid will run from, in the classic layout
   (`<root>/<model>/<task>/<condition>/runs/<id>/`, id `<arm><replicate>` with 1 = OFF,
   2 = UNSEEN, 3 = SEEN). The set must pass every gate.

   **What the gates read.** `verify_smokes.py <root>` finds every run under the root that has a
   trace, and reads two files from each: the trace's response rows, one per step, with what the
   server returned, and the manifest, in which the harness records how the run was configured
   and how it ended. The arm comes from the run id. The script reads the runs themselves, never
   a summary table, because a table hides the failures that matter most: "no reasoning was
   replayed" and "there was no reasoning to replay" look the same in a column of totals, and an
   arm can be dead while every run in it says `finished`. Where a gate compares a run with an
   expected value (the body each arm must send, the replay route, the preamble) the script
   states that value itself rather than taking it from the run wrapper, because a check that
   takes its expectation from the thing it checks cannot catch that thing changing. The
   samplers are the exception: G15 reads them from the same registry file the wrapper reads, to
   catch a value lost between the file and the run.

   **What it reports.** One line per gate: `pass`. `FAIL`, followed by each failure: a run, a
   model, a model x arm, or a value that differs across the set, or `WAIVE`, followed by what a
   registered waiver covered and why. The exit status is the number of failed gates, and the
   last line gives that number and how many gates passed only by a waiver, so a waiver is never
   silent. Descriptives follow, reported and never gated: per model x arm, the steps, the turns
   without a tool call and the silent ones among them, the calls written as text, the share of
   steps with reasoning and the median reasoning length, the runs lost to output the server
   could not parse, and how the runs ended, then every attempt, failed ones included, by cause.

   The gates fall into four groups, by what each protects.

   *The arm reached the model as registered.*

   | gate | passes when | what it guards against |
   |---|---|---|
   | G1 | every SEEN run records `reasoning_replayed=true`, and every UNSEEN and OFF run `false` | the one switch that separates SEEN from UNSEEN set wrongly: a run made with an older wrapper, or an arm mislabelled. OFF is replay-off by rule (section 4.1), so an OFF run recording `true` fails too |
   | G8 | a model's UNSEEN and SEEN runs all sent the same template switches (`extra_body`) | the two thinking arms differing in anything but replay |
   | G11 | every run sent exactly the body registered for its model and arm (section 4.1) | the arms agreeing with each other (G8) yet all being wrong: a misspelled switch or a missing keep-history flag draws no error, because a template ignores variables it does not read |
   | G12 | every run records the replay route frozen for its model (`replay_format=field`, a replayed thought travelling in the `reasoning_content` field) the same for every model | SEEN's reasoning sent by a route the template does not read, which drops it and leaves SEEN no different from UNSEEN |
   | G5 | no OFF run carries a thinking preamble, and a model's two thinking arms carry the same one | the primary contrast varying the system prompt |
   | G17 | every run was served with exactly the frozen flags of section 4.3 (`--swa-full` and `-lv 5` included) and any flag registered for its model alone (none at present), read from the args line of the run's server log. A flag missing, added or changed fails | a run served outside the frozen spec, such as a diagnostic run made without `--swa-full` or at another log level |
   | G13 | every run carries the frozen preamble: none, for every model | the arms agreeing on a preamble (G5) that is not the registered one |
   | G15 | every run was configured from `decoding-registry.json` and recorded the samplers it gives the run's model and mode (section 4.5): thinking for UNSEEN and SEEN, non-thinking for OFF. A model's UNSEEN and SEEN runs were sampled alike, and the set used one version of the registry | a sampler lost on its way from the registry through the wrapper to the harness, or the thinking arms sampled differently: the primary contrast must vary only what the model can see |

   *The model did what its arm says*: the canaries of item 5.

   | gate | passes when | what it guards against |
   |---|---|---|
   | G2 | no OFF step carries more than 200 characters of reasoning, misfiled calls set aside: *waived for Gemma-4-26B-A4B-it*, whose over-length OFF runs are listed under the waiver (section 4.1). Any other model's fail | thinking with thinking switched off |
   | G3 | each UNSEEN and SEEN run has a step with more than 200 characters of reasoning, and reasoning of any length on at least a fifth of its steps | a thinking arm that is not thinking |
   | G4 | no step's reply text, as the harness kept and replayed it, contains a think marker, opening or closing (`<think>`, `</think>`, `<seed:think>`, `</seed:think>`, `[THINK]`, `[/THINK]`), a channel marker (`<|channel>thought`, `<channel|>`, `<|channel|>`, `<|message|>`), for Muse Glimmer `to=self`, or any roster template's turn-structure marker (`<|im_start|>`, `<|im_end|>`, `<|turn>`, `<turn|>`, `<|start|>`, `<|end|>`, `<|return|>`, `<|call|>`, `<|eot|>`, `<|eom|>`, `<|system|>`, `<|user|>`, `<|assistant|>`, `<|observation|>`, `<seed:bos>`, `<seed:eos>`) | reasoning left in the visible text, where UNSEEN cannot strip it, or output the server mis-split: a split the harness missed (section 4.4, item 5) |

   *The set was made under one configuration.*

   | gate | passes when | what it guards against |
   |---|---|---|
   | G6 | the base prompt, the briefing and `harness_git` each have one value across the set, and each task one task hash | runs from different code or inputs mixed in one set. `harness_git` is the harness commit, marked dirty when a tracked file has uncommitted changes or `harness/` holds an untracked file, so an edit made during a set shows |
   | G7 | every run's model and quantization label resolved to an entry in `quant-registry.json` (`quantization_detail.status=ok`), which the manifest copies with the file's sha256 and size | a run whose weights cannot be traced to a fingerprinted file. That the server loaded the intended file is checked by the wrapper before every run, not here: the server's `/props` must name it |
   | G10 | every run recorded the 20,000,000-token budget (`max_total_tokens`) | a set made at another budget, which nothing in a run's outcome would show |

   *No run was cut short or lost by the instrument.*

   | gate | passes when | what it guards against |
   |---|---|---|
   | G9 | no run's token count (prompt and reply tokens summed over all its calls) exceeds the budget or comes within a fifth of it (over 16,000,000) (*waived for a run that reached the budget while looping*: `token_budget_exhausted`, with its last 30 tool calls at most 3 distinct once every number in them is masked, or with every one of its last 30 calls, numbers masked, a call it had already made earlier in the run (the harness's no-progress test, with pids and timestamps masked), and for a run the study lead *judged* stuck, recorded in `verify_smokes.py` (`G9_JUDGED`) with its evidence and its trace fingerprint) the waiver holds only for that same trajectory, and a run of that slot that went differently is judged again | a budget that cuts runs short, so that it, not the model, decides how they end. A run that reaches it while looping is an outcome, not a run the budget censored |
   | G14 | every run that ended in an API error has a cause (output its server could not parse, or a server crash) and no model x arm loses more than a third of its runs to unparseable output | voids that are not missing at random: their chance depends on what the model writes, which is what the arms manipulate (section 9). With three runs per model x arm, one such void passes and two fail: *waived for gpt-oss-20b*, whose voids are listed under the waiver (section 9) |
   | G18 | no run or kept failed attempt is an `api_error` whose server body is a refusal for outgrowing the context window. `context_overflow` runs are counted per model x arm | an overflow filed as a fault and re-run, which would replace an outcome that falls mostly on SEEN (section 9) |
   | G16 | no run records a retried call that had timed out, and every run records its retries (`api_retries`) | a timed-out call re-sent and regenerated from zero: timeouts fall on the longest replies, so a re-roll silently replaces exactly those. Other retries (a dropped connection, a server error) are listed, not failed |

   On the same set: interrupt one run on purpose (Ctrl-C) and re-run the batch command, the
   server must be gone and the batch must resume at the right run. Read the longest single
   reply against the client timeout, and confirm that no run died of context overflow and none
   came near the budget but by the registered waiver. `probe_report.py` gives the per-run
   detail the manifests' totals hide: steps, silent turns, reasoning rate, and the spread of
   the reasoning field, which is how a template artifact is told from real thinking.
7. **Lost tool calls are the model's, not the parser's.** In smoke runs Qwen3.6-35B-A3B lost
   three UNSEEN tool calls whose reasoning field ended in a call's closing tags, with no opening
   tag and no end of thinking. Either the model wrote only the closing tags (behaviour, an
   outcome) or it wrote a whole call that the server's parser then lost (an engine fault that
   would fall on one arm). At `-lv 5` the server log records every token the model generates,
   before parsing, so the smoke set of 2026-10-04 holds the raw output. In all 9 of Qwen3.6-35B-A3B's lost UNSEEN calls
   in that set the model wrote prose and then only closing tags (`</parameter>`, `</function>`,
   `</tool_call>`): never an opening `<tool_call>` or `<function=`, nor a `</think>`. Nothing
   was lost by the parser: the steps are behaviour, an outcome counted as `callTxt`.
8. **How a request that outgrows the context window is filed**. When
   the conversation outgrows the window before a reply can be cut off, the server refuses the
   request: confirmed in the smoke set of 2026-10-01, where llama.cpp b10964 answered a
   GLM-4.7-Flash SEEN request with HTTP 400, "request (132135 tokens) exceeds the available
   context size (131072 tokens)". The harness then filed the refusal as `api_error`, and the
   batch driver re-attempted it as it would an infrastructure fault, the second attempt
   replacing the overflow with a run that ended otherwise. Section 9 wins: the harness now ends such
   a run as `context_overflow`, an outcome (section 6.1), and exits normally, so the batch driver
   keeps it. Gate G18 fails any run or kept attempt in which an overflow was filed as an
   error.
9. **Calibrate the rubric** (2026-10-19). The training round graded the certifying
   smoke's 66 apps, and the cards were frozen at version 2.2 in the grader freeze (item 1). What
   the calibration consisted of:
   - **Tools first,** all in the grader:
     - `grade_setup.sh`, which takes a blind id, finds the run itself, and removes the
       database the app shipped with (section 5.3).
     - `seed_card.py`.
     - `api_probe.py`, the API conformance probe (section 6.5).
     - `backend.sh`, which finds the backend of the app under grading (the process
       listening on a port inside the app's folder that is not the frontend's dev server) and
       pauses, resumes or kills it for the cards' pause and restart steps.
     - the score sheet (`score_sheet.py`).
     - a merge (`merge_grades.py`) that keeps each app's first grading as its score of record, accepts only pass,
       fail and skip, and reports the grader's consistency (section 6.1).
     - the draw of the quality sample, ten apps of every cell, the only apps graded (section 5.3,
       `blind_tools.py sample`).
     - the draw that picks the re-grade set from the sample and gives each of its apps a second blind id, and
       the script that puts a second id on the grader's list only once its 14 days have
       passed (section 5.3) (`blind_tools.py`, which also makes the calibration copies).
     - All of them were run end to end on the certifying smoke's 66 apps on 2026-10-09, with a
       machine stand-in for the grader in place of the hand grading
       (`mock-grading/` in the study's research folder). The stand-in's scores are not grades.
   - **Blind copies.** Every calibration app is copied under a fresh random id before it is
     handed out, because the smoke ids name the arm.
   - **Training rounds, small at first,** on the certifying smoke's 66 apps, built to the current specs, each graded once, and if more
     are needed this study's earlier smoke apps, built to earlier specs. No app of another study
     is used, and no training grading enters the analysis. In each round the grader grades every app of the set
     as the grid will be graded (section 5.3), then reads back over the score sheets item by item and
     rewords any item whose wording left a call unclear.
   - **No separate deciding round** (at the study lead's decision). No set of runs is made for calibration beyond the smoke sets, and no app is re-graded in it. When the training rounds leave no call unclear, the cards are frozen
     (`grader-freeze`, item 1). The calls the rounds settled are not carried into the
     precedents log (section 5.3), which starts empty for the grid: every entry in it is a
     ruling made after the grader freeze, and a deviation. The log is hashed with the grader
     (item 10).
   - **The first test of consistency is the grid's.** The grid apps are graded once each, and
     the re-grade set, a fifth of them (section 5.3), a second time at least 14 days later. The first
     consistency check is made as soon as 24 re-grades of a task are in, against the same bar
     (section 6.1). A check below the bar is handled as section 5.3 sets out: the task's grading stops, a
     fresh set is re-graded, and a second failure is a deviation (section 8.5). The report says that
     the cards were frozen before their consistency had been measured.

     The quality scale is thus fixed before any grid app is graded.
   - **What the rounds give.** The training rounds' scores give a first measure of the score's spread (section 7), from the
     certifying smoke's apps, and the rounds' timings replace
     the estimate of the grading workload.
10. **Registration freeze** (2026-10-31). This protocol is registered on OSF, as the study's
    registered design, and no grid run is made until it is. With it, the registration record
    (`registration/` in the plan repository) hashes this protocol, the batch's schedule files
    (`sha256sum batch-state/schedule-*.tsv`), the analysis code (written first and tested on
    fake data, with the power numbers of section 7 recomputed under the tests of section 8) and
    the tag of item 1, which is both the harness's `study-freeze` and the grader's
    `grader-freeze` (the rubric cards and the API probe included), with the precedents log as
    it then stands. The OSF registration names the tag and the registration record, so that it
    points to the exact files frozen with it.
    The schedules are made (2026-10-21): seven files, one per batch command of section 5.2, written
    with `STOP` set in the grid's own checkout of the tag (`/mnt/d/eval-coding-agent-grid`),
    2,640 runs in all (2,400 for tiers 1-5, 240 for tier 6), each model's arms 120 runs apiece.
    The files, their signatures and `SHA256SUMS` are in the plan repository
    (`registration/schedules/`).
    The analysis code is written (2026-10-21, `analysis/` in the plan repository, with its
    design in `analysis/DESIGN.md`). It passes its fake-data tests, reproduces the gate
    script's numbers on the 66 runs of the certifying smoke set, and the power figures of
    section 7 are recomputed under it (`analysis/power-results/`).

### 5.2 Running the grid

Tiers are run in order, and each adds whole models to the grid:

| tier | models | grid runs | machine time | what it adds |
|---|---|---|---|---|
| 1 | Gemma-4-31B-it, Qwen3.6-27B | 720 | ~76 h | the core: two labs, both on the full three-arm ladder |
| 2 | + Seed-OSS-36B-Instruct | 360 | ~54 h | a third lab and thinking dialect. Its OFF arm stands on the replay-off rule (section 4.1) |
| 3 | + gpt-oss-20b | 240 | ~7 h | a fourth lab. The model raised to carry its reasoning, on its two arms |
| 4 | + GLM-4.7-Flash | 360 | ~31 h | a fifth lab. A keep-history flag of the opposite polarity |
| 5 | + Qwen3.6-35B-A3B, Gemma-4-26B-A4B-it | 720 | ~52 h | the two within-lab mixture-of-experts pairs |
| 6 | + Muse Glimmer 30B | 240 | ~20 h | a sixth lab and a fourth dense model, on two arms. A second model with no off-switch |

Tiers 1-5 are committed: they are run and graded in order. Tier 6 is optional and follows only
if there is time for it, about 20 hours of machine time and about 60 hours of grading, decided
by the time left and never by results. No tier is analysed on its own: the analysis is made once, on the whole grid,
after the grid's grading, re-grades included, has ended. Until then no result by arm is looked
at.
Nothing in this protocol changes between tiers: every model is analysed under it unchanged,
whichever tier it is in, and no model is added or dropped on the strength of another's results.

```bash
REPLICATES=20 ./run_thinking_batch.sh gemma-q4                   # tier 1
REPLICATES=20 ./run_thinking_batch.sh qwen-q4
REPLICATES=20 ./run_thinking_batch.sh seed-q4                    # tier 2
REPLICATES=20 ./run_thinking_batch.sh gptoss-20b                 # tier 3
REPLICATES=20 ./run_thinking_batch.sh glm-q4                     # tier 4
REPLICATES=20 ./run_thinking_batch.sh qwen-moe-q4 gemma-moe-q4   # tier 5
REPLICATES=20 ./run_thinking_batch.sh muse-q4xl                  # tier 6
```

The batch driver takes the replicate count from `REPLICATES`, whose default is 16, so every
grid command carries `REPLICATES=20`. The count is part of each schedule's signature, so
re-running a command without it stops instead of running a different grid. Before the freeze,
each grid schedule (`batch-state/schedule-real-*.tsv`) must hold 360 runs: 240 for gpt-oss
and Muse Glimmer, and 720 for the tier-5 pair, which share one. `touch batch-state/STOP` before a command writes
its schedule and stops before the first run.

Runs land under `/tmp/runs/study/<model>/` in the blind layout. Re-running a command resumes
after any interruption. `touch batch-state/STOP` stops cleanly after the current run, and the
batch pauses by itself while free disk space is under 20 GB. At `-lv 5` a tier's server logs
alone run to tens of gigabytes (section 4.3), so finished runs are moved off between batches. A study run never goes out through
bare `run.sh`, whose defaults are the lighter smoke guards. Between runs, finished runs can be
moved to the archive (`mv /tmp/runs/study/<model> <archive>/study/<model>`). The ledger and the
key are *copied*, never moved, after every batch
(`cp blind-state/blind-ids.txt blind-state/blind-key.jsonl <archive>/`), because the originals
feed the next run.

**After each tier's batch**, and before its quality sample for manual grading is drawn (section 5.3), the input
checks of the analysis are run on the tier, from the plan repository's `analysis/` folder, with
`--runs` pointing wherever the tier's runs then are:

```bash
python3 run_analysis.py check --key /mnt/d/eval-coding-agent-grid/blind-state/blind-key.jsonl --runs /tmp/runs/study
```

The above command reads every run in the un-blinding key and looks for the three silent faults (explained below.)
A slot is listed if its run has one of those faults and no good re-run has replaced it yet.
The output shows counts, slot labels and causes only, never a blind id or an outcome. A slot is one
place in the schedule (a model, task, condition, arm and replicate), and its label names it.
Most faults make the runner exit with an error, and the batch driver then tries the same slot
again by itself, up to three attempts in all. Three faults do not, and they are the ones this
check is for: the wrong model file was served, a recorded setting differs from section 4, or
the npm registry could not be reached during an install. In each of them the run ends
normally, so the batch driver keeps it and moves on, although the run is void (section 9).
The check finds such runs by reading their records and lists their slots. Each listed slot is
then re-run by hand, on its own rather than through the batch driver, under the same label and
from the grid's checkout, with the command the batch driver itself would use:

```bash
ARM=<arm> BLIND=1 OUTPUT_ROOT=/tmp/runs/study/<model> ./run_one_with_server.sh <model> <task> <condition> <label>
```

and the check is run again until `run_analysis.py` lists nothing. Only then is the tier's sample for grading 
is drawn.

### 5.3 Grading

One grader grades the apps of the quality samples, using the rubric card for the app's task
(section 6.1), and records the result on a score sheet. A fifth of the graded apps are graded a second
time, blind, at least 14 days after their first grading, to measure how consistently the grader
applies the cards.

**The quality sample** (at the study lead's decision, to halve the grading). Before
each tier is graded, a script puts the 20 apps of every model x task x condition x arm cell in a
random order, with a seed fixed at the freeze, and the first ten of every cell are graded: half
of its 20, or all of a cell left with fewer (section 9). Only these apps go on the grader's lists. The
sample is therefore balanced by construction: every model, task, condition and arm has the same
number of graded apps. The script orders every attempt of a cell that the un-blinding key
lists, so a void attempt (section 9) can fall among a cell's first ten. It is left there:
it enters no analysis, its cell has one graded app fewer, and the report counts such
apps per model x arm.

- **Grading more, if time allows.** The sample of a tier may be extended, for the whole tier at
  once, to the next apps in every cell's order (the eleventh of every cell, then the twelfth,
  and so on (`blind_tools.py extend`)) so every cell of every model in the tier keeps the same
  number of graded apps. Whether to extend is decided by the time left and never by results:
  the grader is blind, and no result by arm is looked at until the grid's grading has ended (section 5.2).
  The analysis uses every graded app. The power stated in section 7 is for the first ten, the minimum.

- **Every run still counts for everything else.** Failure incidence, steps and the mechanism
  measures (section 6.1, section 6.3) use every run. App quality and the API probe (section 6.5) use the sample.
- **The grading sample runs are fixed before anything is looked at.** They are drawn by the script
  before any app of the tier is set up or any run's outcome is read, and it is never changed: 
  an app that turns out empty or broken is graded like any other, and no app is added or swapped. 
  Being random within each cell, its mean is an unbiased estimate of the cell's.

**The re-grade set.** Before each tier is graded, the same script draws, with a seed fixed at
the freeze, two of the ten sampled apps of every model x task x condition x arm cell: a fifth
of them, or as near as a cell left short allows (section 9). Each drawn app is given a second blind id,
recorded in the un-blinding key beside its first, so that nothing the grader sees ties its two
gradings together.

**The frozen grading rules** (`tasks/rubrics/README.md` at the tag) predate the quality sample
in two sentences. They say that the grader grades every app, and that the re-grade
draws four apps of every cell, a fifth of all apps. The rules in force are this section's: only
the quality sample is graded, and the re-grade set is two of its ten apps per cell, as
`GRADING-COMMANDS.md` and `blind_tools.py` at the tag already do. Nothing is graded differently
because of the two sentences. They also say that the draws and the lists are made by someone
other than the grader. In this study the grader makes them ("Who runs the draws", below). The
plan repository's reading copy (`rubrics/README.md`) has all three corrected. The frozen rules
also say that the log's first entries are the training rounds' calls: the grid's log has none.

**The seed of the draws** is `bb696caef027c79c`, fixed on 2026-10-21 and published with this
protocol. One seed serves every draw. Tier *N* of section 5.2 (N = 1 ... 6) is drawn as

```bash
python3 blind_tools.py sample --state <state> --seed bb696caef027c79c --draw tierN --per-cell 10 --models <its models>
python3 blind_tools.py draw   --state <state> --seed bb696caef027c79c --draw tierN --per-cell 2  --models <its models>
```

with its models as in section 5.2 (tier 1 `gemma-q4,qwen-q4`, tier 2 `seed-q4`, tier 3 `gptoss-20b`,
tier 4 `glm-q4`, tier 5 `qwen-moe-q4,gemma-moe-q4`, tier 6 `muse-q4xl`). A fresh set after a
check below the bar (below) is drawn with the same seed and the name `fresh-<task>-<k>`, *k*
counting that task's fresh sets. The script seeds each draw from the seed, the draw's name and
its kind, so the sample of a tier, its re-grade set and every fresh set each have a random
stream of their own. Publishing the seed gives nothing away: it orders apps that do not exist
yet, within cells whose ids are random. The second blind ids and the grader's lists come from
the system's random source.

**Order.** The script gives the grader one shuffled list of blind ids at a time. An app in the
re-grade set gets a second id, which goes onto a list only once 14 days have passed since its
first grading, so the re-grades are mixed in among first gradings of later apps. The last
tier's remaining re-grades come after its last first gradings. Nothing on a list marks which
ids are re-grades.

**Who runs the draws.** The study lead, who is also the only grader, runs the draws and makes
the lists. The script reads the un-blinding state but prints only counts and blind ids, never
an app's cell, and the grader never opens the state folder, the key or the grading index. When
the script writes a list it also prints how many of its ids are re-grades, though not which.
The report states as a limitation that the grader ran the draws.

**Consistency checks.** Each check is made per task, against the bar set out in section 6.1, on at
least 24 re-graded apps of the task, comparing each app's first grading with its re-grade.

- **When.** The first check is made as soon as 24 re-grades of a task are in. After that, one
  is made when each tier's re-grades are complete. Any drift over the weeks shows there.
- **After every check,** the grader goes through the items that changed between the two
  gradings. One that shows an ambiguity in the cards is settled by a ruling (below). No
  re-grade changes a score of record on its own.
- **A task below the bar.**
  - Its grading stops. The other task's goes on.
  - **A fresh set.** A fresh set of at least 24 of its apps, spread evenly over their cells,
    is drawn from those first graded at least 14 days earlier and not yet re-graded, and is
    re-graded before any other app of that task. They join the re-grade set. Grading resumes
    once they meet the bar.
  - **If the fresh set fails too, or too few of the task's apps are left to draw it,** the
    failure is logged and reported as a deviation (section 8.5). How any remaining grading of that
    task goes on is decided before more of it is graded.

**Blind grading**

- The grader sees only the blind id. `grade_setup.sh` takes the id, finds the run itself, and
  prints and records nothing but the id, so the grader never sees the model's folder. The
  grader never opens the run's manifest, trace or logs.
- The grader never looks up an earlier score sheet while grading, and goes through the changed
  items of a check only after that check's re-grades are all in.
- The grader works through each list in its shuffled order, so that drift over the weeks
  cannot follow the arms.

**A fresh copy every time.** The rubric's script requires posting messages and creates kanban cards,
so an app once graded is no longer fresh. Every grading, a re-grade included, starts from a copy of
its own, made so that the grader (or another grader a year later) reaches the same app
(`grade_setup.sh <blind id>`):

1. The app is copied out of its run. Nothing is ever installed inside the archived workspace,
   whose files the harness fingerprints at the end of every run.
2. The grader's Node matches the run's, as its `environment.txt` records.
3. The database directory the app shipped with, if any, is removed, with any parent it
   leaves empty, and the removal is logged. Every app then starts as a new user would find
   it, whether or not its agent ever ran it.
4. Dependencies are installed in every folder of the app that has a `package.json` (task
   1.4 speaks of "its package.json files"): with `npm ci` from that folder's
   `package-lock.json` if the run has one. If it has none, the app's first grading produces the lockfile, which is saved in the
   run's log folder as `grading-lock.json`, outside the fingerprinted workspace, and every
   later grading installs from that. The npm `before` date makes even that first install
   resolve identically on any machine.
   Whether this install succeeds is the rubric's first launch item (section 6.1). An install that
   stops on a dependency conflict npm refuses is re-run with `--legacy-peer-deps`, and one whose
   lockfile does not match its `package.json` (`npm ci` refuses it) is re-run with
   `npm install`, and one that stops because no version published before the `before` date
   matches the range a dependency of the app's own `package.json` asks for (`ETARGET`) is
   re-run with `npm install --no-save <that package>@latest`, which takes that one package at
   the newest version before the date and writes nothing but `node_modules`, and one that stops
   because a lifecycle script of the folder's own `package.json` fails (`preinstall`, `install`,
   `postinstall`, `prepare`) is re-run with `--ignore-scripts`, so the rest of the card can
   still be graded. The item fails all the same.
5. The grader's own environment is recorded beside the grades (`GRADER-ENV.txt`: Node, npm,
   the `before` date, the lockfile's hash, the OS, the browsers), with the setup's full log and
   the output of any install re-run, the evidence behind the install item.

**The browsers.** Every grading, re-grades included, uses the same two browsers on the
Windows side of the study machine: window A is Firefox 158.0.1, and windows B and C (C only
on the message board) are Microsoft Edge 155.0.4283.62. Two browsers keep window A from
sharing a cache or a connection with B and C. Their automatic updates are switched off for the
whole of the grid's grading: Firefox by its enterprise policy (`DisableAppUpdate` in
`distribution/policies.json`), Edge by disabling its update services (`edgeupdate`,
`edgeupdatem`) and its scheduled update tasks, because Edge's update policy applies only to a
machine joined to a domain. The browsers run on Windows, where `grade_setup.sh` cannot see them,
so the grader sets `GRADER_BROWSER="A: Firefox 158.0.1; B, C: Edge 155.0.4283.62"` in the grading
shell and every `GRADER-ENV.txt` records it. Each grading therefore names the versions it used.
A version that changes all the same is logged as a deviation (section 8.5), with the date and
the gradings made after it. The grading lists are shuffled across arms (above), so a change part
way through cannot fall on one arm. The training round recorded no browser versions: its
`GRADER-ENV.txt` files carry a placeholder in that field, and are left as they were made.

Every app is then started and exercised the same way:

- **Launch.** The app is started with the command both task specs require: `npm run dev` at
  the project root (task 1.4).
- **Accommodations.** If that does not give a working page, the grader tries the fixed
  accommodations the rubric allows. None of them edits a file. One of
  them (A8) installs a package: when a part stops because its own code imports, or its own
  declared script runs, a package that no `package.json` of the app declares, and the error
  names it (`Cannot find module`, `Cannot find package`, `not found`), exactly that package is
  installed with `npm install --no-save <name>@latest`, which writes nothing but `node_modules`.
  A part started this way fails its launch item, as after any accommodation.
- **The script.** The grader works through the card's steps, in order.
- **The API probe.** Once the score sheet is complete, with the app still running, the grader
  runs the probe (section 6.5). It adds messages or cards of its own, so it never runs earlier, and
  nothing it shows changes a score.

**Rulings.** After the grader freeze (section 5.1 item 1), a question the cards did not foresee is settled by a ruling in
the precedents log:

- **What a ruling may do.** It only says how an item's criterion applies. It never adds,
  removes or reweights an item.
- **Who makes it.** The grader makes it from the changed items alone, without reference to any
  result by arm.
- **How it is recorded.** It is dated, logged as a deviation (section 8.5) and applied to every
  run.
- **What it changes.** Every app already graded that the ruling would change is re-graded on
  the affected items, from a fresh copy. For an app in the re-grade set, both of its gradings
  are.
- **Where it is kept.** The precedents log is `precedents-log.md` in the grading results
  folder (`grading/`, beside the score sheets and the API probe's files), outside the tagged
  grader and outside the runs. It names apps only by blind id. It starts empty for the grid (section 5.1 item 9). Each
  entry gives an id, the date, the item, the question the card left open, the ruling,
  the blind ids that raised it and those re-graded because of it, and any entry it replaces.
  Entries are appended, never edited or deleted, and the log is committed to git after each
  one. Its state at the registration freeze is hashed with the grader (section 5.1 item 10).
- **An item that cannot be applied at all** (it proves wrong, or no app can be judged on it)
  is beyond a ruling, which cannot remove it. It is reported as a deviation (section 8.5), and how
  it is handled (for example, the analysis with and without it) is decided, without
  reference to any result by arm, before more of its task is graded, and recorded in the
  precedents log.

A score sheet, once in, changes only through a ruling.

---

## 6. Measures

This section defines what is measured on each run: the three measures the main hypotheses are
tested on (6.1), cost (6.2), the measures behind H3-H5 (6.3), what is reported without a test
(6.4) and API conformance (6.5).

### 6.1 The three behaviour measures (H1, H2)

H1 and H2 are each tested on three measures of how a run went, the behaviour measures:
failure incidence (whether the run ended without finishing), steps to finish (how many steps a
finished run took) and app quality (how good the app it built is). Each is defined below.

**Failure incidence**: whether a run ends without the agent calling `finish`. The harness
ends every run with one mechanical terminal status:

| status | how the run ended |
|---|---|
| `finished` | the agent called `finish` |
| `stuck_looping` | a loop guard fired: the same call repeated, a two-step cycle, or 30 steps of nothing but repeats (which one is recorded) |
| `stuck_blocked_tool` | three calls in a row to a tool the condition does not offer |
| `stopped_no_tool_call` | two turns in a row without a tool call, the second in reply to the finish nudge |
| `runaway_no_tool_call` | a reply without a tool call that used the whole 32,768-token allowance |
| `truncated_no_tool_call` | a reply without a tool call cut off below the cap: in practice by the context window, an overflow death |
| `truncated_tool_args` | the same call repeated by the loop guard's count, its arguments cut off and unparseable: a reply cut off at the cap, told apart from a model repeating itself |
| `context_overflow` | the conversation outgrew the context window before a reply could start, and the server refused the request: the other overflow death |
| `token_budget_exhausted` | the 20M-token budget ran out |
| `budget_exhausted` | `MAX_STEPS`, 10,000 steps, was reached. No smoke run came near it |

These are all the terminal statuses the frozen harness records for a run that ends normally
(`harness/agent.py`, and `config.STATUSES` in the analysis code). Every status but
`finished` counts as a failure, and each is also reported on its own (section 6.4). A run whose
runner (the script that makes the run, section 5) fails, exiting with an error instead of
ending normally, is filed as `api_error` (or `interrupted`, or a crash) and is void
(section 9). The contrast is the difference between the arms in the share of runs that fail.

**Steps to finish**: the number of steps a finished run took, over the runs that finished.
Each arm is summarised by its geometric mean, and the contrast is the ratio of the two arms'
geometric means. Because only finished runs enter it, a difference in steps is always read
beside the difference in failure incidence, never alone.

**App quality**: the score an app earns on the hand-graded rubric for its task, 0-100. The
rubric grades the artifact, not the transcript, so every app in the quality sample (section 5.3) is
graded, finished or not. The sample is half of each cell, drawn at random before grading, so
its mean estimates the cells without bias. Quality is measured on at least 60 apps per arm per
model (more if the sample is extended, section 5.3).
Each task has a rubric card with two parts:

- **A fixed script**, worked through in a real browser, with two or three windows open on the
  app and the backend paused or killed where a step calls for it.
- **A list of items**, each scored pass or fail against its written criterion. `skip` is kept
  for a fault on the grader's side and is never used for anything the app does.

Scores and consistency:

- **A score** is the weighted share of the items scored pass or fail that pass. Skipped items
  are left out.
- **The score of record** is an app's first grading (section 5.3). Its re-grade, for an app in the
  re-grade set, measures consistency and nothing else.
- **Consistency** (test-retest) is reported on the re-grade set, per tier and over the whole
  grid:
  - for the score: the mean absolute difference between an app's two gradings, and the
    intraclass correlation across the re-graded apps (two-way, absolute agreement, single
    measurement), with the difference also shown against the time between the gradings.
  - for each item: Cohen's kappa beside the raw share of apps whose item came out the same
    both times.
- **The bar.** For each task, an app's two gradings differ by no more than 5 points on
  average (the mean absolute difference over the re-graded apps). It applies to every consistency check (section 5.3). An intraclass correlation
  is reported but is not the bar. It depends on how much the apps differ from one another, so
  it can fail a careful grader on a set of similar apps and pass a careless one on a varied
  set.
- **What one grader cannot show.** A grader can apply a misreading consistently, so
  consistency is not agreement between people. What keeps the scale objective is the cards
  themselves (a fixed script and pass/fail criteria written to be read one way) and the
  report says so as a limitation. The single grader also means every arm is graded by the
  same person, so no difference between graders can fall unevenly on the arms.

**The four launch items** are what a user meets first:

1. The app's dependencies install.
2. The backend starts with the declared command, with no accommodation.
3. The frontend starts with the declared command, with no accommodation, and its page loads its
   own code and files.
4. The frontend page reaches the backend.

The accommodations (the grader's fixed, file-free ways round a failed launch) let the rest of
the card be graded. They never earn the first three items back: those are judged on the app's
own install and declared commands. The fourth is judged on the first launch where both parts
run, with or without accommodations, except one that needed an environment variable set so that
one side could find the other (A4 in the rubric's rules), which fixes the very connection the
item tests, or the rules' catch-all step (A7).

The rubric never depends on the API's paths: an app that works on paths of its own can pass
every item. Whether its backend offers the API the spec names is measured apart, by a probe
(section 6.5).

An app that never gives a working page keeps the launch items it passed and fails every other
item.

The items and weights of the frozen cards (version 2.2, 2026-10-18, fixed by the grader freeze,
section 5.1 item 1):

- **message-board**, 15 items, weight 27. Sections, as (items, weight):
  - launch (4, 9)
  - posting and loading the history (4, 6)
  - the event stream and live delivery to other windows (4, 7)
  - no message stored twice (1, 1)
  - messages surviving the backend being killed and restarted (1, 3)
  - layout (1, 1)
- **kanban-board**, 26 items, weight 50. Sections, as (items, weight):
  - launch (4, 9)
  - the board, and creating cards from the interface (5, 8)
  - the event stream and live updates to another window (4, 9)
  - drag and drop, across columns and within one, including a drop outside every column (8, 14)
  - two windows moving cards at once (2, 4)
  - ten repeated moves between the same neighbours (1, 2)
  - the board surviving a kill and restart (1, 3)
  - layout (1, 1)

The contrast is the difference between the arms' mean scores, over the apps of the quality
sample, finished or not. The same comparison over the sampled apps of finished runs only is
reported beside it (section 8.4).

### 6.2 Cost

Tokens per run (prompt plus completion, summed over every call) per arm, reported as the
SEEN/UNSEEN and UNSEEN/OFF ratios of the mean, with 95% intervals, over all runs and over
finished runs. Machine time per run beside it. Cost is estimated, not tested: SEEN costs more
per step by construction, and the question is how much per run, and for what.

**Compute and energy**, reported and never tested. A run's machine time is the span its
manifest records (`started_at` to `ended_at`). Its GPU compute is the sum of the
prompt-evaluation and generation times that llama-server logs for every request (`-lv 5`,
section 4.3). Both are summed per model, per arm and over the grid, however many batches the runs were
made in and on whatever days. During every batch the GPU's board power is logged every 5
seconds, outside the harness (`nvidia-smi`), and a run's energy is that power integrated over
its span. The time between runs (server boot and stop, the gaps between batches) is reported
apart. A batch without a power log is bounded from above by the card's 300 W limit, and the
report names such batches. For scale, the certifying smoke: 66 runs, 6.07 hours of run time,
3.74 of them GPU compute.

### 6.3 Mechanism measures (H3-H5)

Measured on each UNSEEN and SEEN run:

- **Reasoning rate (H3):** the share of the run's steps whose reasoning field is not empty,
  read from the run's trace. A field holding only a misfiled tool call does not count, by the
  rule the canaries use (section 5.1).
- **Reasoning per reasoning step (H4):** the median number of reasoning characters over the
  run's reasoning steps, counted as for H3. A run with no reasoning step has no value and is
  left out of H4.
- **Silent turn (H5):** whether the run contains at least one turn with neither text nor a
  tool call.

### 6.4 Descriptives, reported per model x arm, never tested

1. **Each terminal status separately**, and which loop guard fired.
2. **The size of the treatment.** Reasoning characters per step in UNSEEN, misfiled calls
   excluded as for H3, are exactly what that arm withholds, and they vary by an order of
   magnitude across the models (smoke-run medians from under 100 to about 500 characters per step).
   The turns and characters SEEN replays are recorded beside them. A visibility effect in one
   model and not another may be a difference in how much text the arms differ by, not a
   difference in kind.
3. **Reasoning in OFF steps**, per model, so that a switch that leaks is seen: watched for
   Gemma-4-26B-A4B-it (section 4.1).
4. **Tool calls written as text** (`callTxt`): steps with no parsed call whose reasoning or
   text holds one written out, a call's arguments in the reasoning field, a call's closing
   tags left in it, a `finish` call's arguments written out as the whole of the text. If it
   differs between UNSEEN and SEEN, that difference is part of the visibility effect and is
   reported as such.
5. **Turns without a tool call**, split into silent turns and turns of prose alone, with the
   nudges given (`finish_nudges`, `finish_nudge_steps`).
6. **Whether a run checks its own work** (`execution` and `interactive` only): a server started,
   an HTTP request made, a build or test command run, a browser tool used. Not an outcome, and
   no model is dropped for skipping it: but an app whose author never saw it run is graded
   beside apps whose authors did, and the smoke runs found models ranging from checking in every
   run to checking in none.
7. **Repeated file states** (`file_state_repeats`): the write and edit calls that got the
   file-state note (section 4.4), split into writes and edits, with the reverts among them (calls
   that moved a file back to an earlier content) and the most calls that left one file with one
   content. The note is the same in every arm, but a model that can also see what it reasoned
   about the file before may read it differently, so a difference between UNSEEN and SEEN is
   part of the visibility effect.
8. **Retries and voids**, by cause, over attempts (section 9).
9. **Context:** the largest prompt of each run, and, for the Gemma pair, how many of the 31B's
   runs come within 10% of its 65,536-token window.
10. **Machine time** per run.
11. **The rubric item by item:** the share of apps passing each item, the launch items first,
    so that where the apps fail is seen as well as how much.

How often a model thinks (H3) is itself shaped by the treatment, so part of any visibility
effect on behaviour may travel through how often a model thinks rather than what it can
see: a mediation this design cannot separate, and the report says so rather than implying a
single mechanism.

### 6.5 API conformance (exploratory)

The rubric judges what an app does. Whether its backend offers the API the spec names is
measured apart, by a probe (`api_probe.py`, in the grader) that calls the backend directly
once the grader's score sheet is complete (section 5.3). It is run on the apps of the quality sample.

- **The checks** test only what the spec states exactly (tasks 2.4 and 3.1-3.3). The rubric
  README lists them.
  - message-board, 4: the history, the event stream, posting, and the broadcast of a new
    message.
  - kanban-board, 10: the board and its columns holding their cards. The event stream. Card
    creation, the new card's place at the end of its column, and the create's broadcast, and
    the move: accepted with `{ columnId, beforeId, afterId }`, answering with the card,
    landing between its neighbours and nowhere else, and broadcast.
- **Results.**
  - Each check passes or fails. A failure counts like any rubric failure, and a check that
    cannot run because the app failed an earlier one fails too.
  - The spec names no body field for a new message or card, so the probe tries the likely
    names. A check it cannot settle that way is `inconclusive`, and one that needs it is
    `blocked`. Both are reported by count and left out of the share.
  - Details the spec leaves open (the JSON shapes, the field names that worked, how a missing
    neighbour is sent) are recorded as observations and never scored, as is how the
    message-board server answers a message with empty text, which the spec does not address.
  - An app whose backend never runs, even with the accommodations, fails every check.
- **The measure.** An app's API conformance is the share of its checks that pass, over those
  that passed or failed, unweighted.
- **The record.** The probe made at an app's first grading is the record. On re-graded apps,
  the probe made at the re-grade, on its own copy, is compared with it, and the share of
  checks with the same result is reported as the probe's reproducibility.
- **Analysis.** Per model and per registered contrast, the arms' difference in mean API
  conformance, with 95% stratified-bootstrap intervals, beside app quality. No test, and
  outside every Holm family (section 8.4).

---

## 7. Sample size and power

This section asks whether the grid is big enough to answer its questions. It answers with
three kinds of number:

- **Power.** If the arms truly differ by a given amount, how often the study's tests would
  detect it. "Detected 90% of the time" means that in 90 of 100 grids like this one, the test
  would find the difference.
- **Bounds.** If the arms do not differ, how small a difference the grid can rule out, and how
  often it would declare the arms equivalent.
- **Error rate.** If nothing differs at all, how often a test would wrongly declare a
  difference.

None of these numbers comes from study data, since none exist yet. Each is computed for the
grid as registered, in two ways: first by formula, then by simulating grids of fake data, each
with a known difference planted in it (or none, for the error rate), and analysing each one with the study's own analysis
code. Two inputs come from earlier work: the spread of quality scores from the training rounds,
and the effect sizes for H3-H5 from the smoke runs.

120 runs per arm per model (20 in each of six task x condition cells) which is 360 runs for a
three-arm model and 240 for gpt-oss and Muse Glimmer (since they don't have an OFF arm).
The first set of numbers below was computed for this design by formula (Fisher's exact test for the failure rates and
a 90% Newcombe interval for the bound and the equivalence statement, both evaluated exactly,
and a normal approximation with Holm over three measures, at 80% power, for steps and quality).
They were recomputed under the tests of section 8 before the freeze (section 5.1), and the
recomputed numbers follow them below:

- **To detect.** A failure rate of 2% in one arm against 15% in the other is detected 96% of
  the time, and 2% against 20% over 99% of the time. 2% against 10% two times in three (68%).
  On steps, shifts of about 0.4 standard deviations are resolved after the Holm correction. App
  quality is graded on the quality sample, at least 60 apps a side (section 5.3): shifts of about 0.6 standard
  deviations are resolved, about 24 points at the spread of the training rounds' scores
  (standard deviation about 41 points, from 41 apps).
- **To bound.** If the arms do not differ, 120 a side supports "any reliability difference is
  smaller than about 3-6 percentage points" (+/-2.2 points if neither arm fails at all). When the
  arms truly match at a 2% failure rate, the +/-10-point equivalence statement is declared over
  99% of the time, where 32 a side would declare it only about 27% of the time. At a 5% rate,
  91% of the time.
- **No equivalence statement for quality.** At the spread the training rounds measured
  (section 5.1 item 9), the 90% interval of a quality difference at 60 apps a side is itself wider than
  +/-10 points, so the +/-10-point statement could not be reached, and none is registered: quality
  is reported as different or undetermined, with its interval (section 8.2). The spread is
  recomputed from the grid's first consistency check, which also measures the grader's own
  inconsistency, and the detectable shift above is restated from it.
- **The generation contrast** (H2) has the same operating characteristics, so the OFF arm is
  powered to detect the same sizes of effect as the primary contrast.
- **H3-H5** use the same runs, and their power is computed with the rest before the freeze.
  H5's depends on how often a model goes silent at all: a model with no silent turn in either
  arm contributes no evidence to it.
- **A within-pair difference** (section 8.4) carries about 1.4 times the standard error of either
  model's own effect, so only large differences between twins can be resolved.

**Recomputed under the tests of section 8** (2,000 simulated grids of one model per
scenario, each test with 2,000 permutations and 2,000 resamples, Monte Carlo standard errors
about one point. The numbers are in `analysis/power-results/power.csv`). Each simulated grid is
analysed by the analysis code itself: the stratified permutation tests, Holm within each family
and the intervals and verdicts of sections 8.1 and 8.2.

- **To detect.** Against 2% failure in the other arm, 10% is detected 50% of the time, 15% 90%
  and 20% 99%. These are below the numbers above, which used Fisher's exact test at 5% without
  the Holm correction. In a family whose other two measures do not differ, Holm asks the first
  test for p below 0.05 / 3, and Fisher's exact test at that level gives the same 50%, 90% and
  99%. Steps: shifts of 0.3, 0.4 and 0.5 standard deviations are detected 47%, 75% and 92% of
  the time. Quality: shifts of 0.5, 0.6 and 0.7 standard deviations (20, 25 and 29 points at a
  standard deviation of 41) 64%, 79% and 91% of the time.
- **To bound.** When both arms fail at 2%, failure is declared equivalent 99.8% of the time,
  and at 5% 91.4%. When the arms' steps match, steps are declared equivalent about 92% of the
  time.
- **The quality simulation is a simplification.** Its scores are drawn from a normal
  distribution with the training rounds' standard deviation of 41 points. Real scores lie
  between 0 and 100 and need not be normal, so the quality numbers are approximate. They are
  restated from the grid's first consistency check (above).
- **Error rate.** With every measure equal, a family declares a difference 3.3% of the time,
  and the H3-H5 family 3.8%, both within the 5% Holm guarantees.
- **H3-H5**, each at the size the smoke runs suggested (section 1.3) with the other two equal: a
  reasoning rate of 0.90 in UNSEEN against 0.97 in SEEN is detected every time, a median of
  0.8 times as many reasoning characters per reasoning step 77% of the time, and a silent turn
  in 10% of UNSEEN runs against 2% of SEEN runs 64% of the time.

---

## 8. Analysis plan

### 8.1 Confirmatory tests

For each model and each contrast (H1 is UNSEEN against SEEN, and H2 is OFF against UNSEEN), the three
measures of section 6.1 are tested with stratified permutation tests: the arm labels are permuted
within the six task x condition strata, 10,000 permutations, two-sided. The
test statistics are the difference in the share of runs that fail, the difference in mean log
steps (reported as a ratio of geometric means), and the difference in mean quality score.
Failure uses every run, and steps the finished runs, since steps are defined for finished runs
alone. Quality uses the apps of the quality sample (section 5.3). Each measure's arm labels are
permuted within the same strata among the units it uses. The three p-values of one contrast in one
model form one family, corrected by Holm at alpha = 0.05.

H3-H5 are tested the same way, one-sided in the registered direction: the difference in mean
reasoning rate (SEEN above UNSEEN), in the mean log of the per-run median reasoning characters
(SEEN below UNSEEN), and in the share of runs with a silent turn (UNSEEN above SEEN). A model's
three p-values form the third Holm family.

Every estimate is reported with a 95% interval, made by one of two methods (chosen
on the fake-data coverage check, see below). A difference between two shares of runs (failure
incidence, and H5's share of runs with a silent turn) gets Newcombe's hybrid score interval.
Every other estimate gets a stratified bootstrap: within each arm, units are resampled with
replacement inside each task x condition stratum, each stratum's resampled mean is rescaled
about the stratum's own mean by the square root of k / (k - 1), k the stratum's size, so that
its variance is the usual unbiased one, 10,000 resamples, and the interval is the percentile
interval. For quality the units are the sampled apps, and for steps the finished runs.
Replicates are independent draws. Runs that share a seed in different arms are not paired.

**Why these two methods.** The analysis code was first written with the plain percentile
interval of the stratified bootstrap everywhere, and with a rule set before the check: a method
whose 95% interval covers the true value less than 93% of the time in any failure scenario at
or below 5% is replaced. On 2,000 simulated grids of this design per scenario, the plain
percentile interval of a failure difference covered 91% of the time at 0% against 2% failure,
and BCa, the replacement first considered, did worse (90%). Newcombe's interval never covered
less than 96%, and it is the interval the power figures of section 7 were first computed with.
The same check found the plain bootstrap's quality interval covering about 93%, because a
stratum holds only ten sampled apps and the plain bootstrap understates a stratum's variance by
(k - 1) / k. The rescaling brings it to about 94%. With the two methods, the 95% interval
covers the true value at least 93.8% of the time in every scenario and for every measure
(`analysis/power-results/`).

**The analysis seed** is `61f43c6f3593702f`, fixed on 2026-10-21 and published with this
protocol. Two of the methods above work by deliberate chance: a permutation test shuffles the
arm labels at random 10,000 times, and the bootstrap redraws the runs at random 10,000 times.
Run twice without a fixed starting point, the analysis would give slightly different p-values
and intervals each time. A seed is the number a computer's random generator starts from: the
same seed gives the same shuffles and redraws every time, so the analysis code gives exactly
the same numbers whenever it is run on the same data. Fixing the seed before any data exist
takes away one freedom, that of re-running the analysis with other seeds until a borderline
result falls on the wished-for side, and publishing it lets anyone repeat every number. Each
test draws from a stream of its own, made from the seed and the test's name, so that adding or
removing one test never changes another's result. Every test's stream and seed are listed in
the analysis's intermediate record (`analysis/DESIGN.md`, section 12).

### 8.2 Equivalence

For failure incidence and steps, when they do not differ, equivalence is tested against
bounds fixed now: +/-10 percentage points for failure incidence, 0.8-1.25 times for steps.
Equivalence is declared when the 90% interval lies wholly inside the bounds: two one-sided
tests at 5%. The 90% interval is made by the same method as the measure's 95% interval
(section 8.1): Newcombe's for failure incidence, the rescaled stratified bootstrap's for steps.
On the fake-data coverage check (section 8.1, `analysis/power-results/coverage.csv`) the 90%
intervals covered the true value 90.8% to 99.0% of the time for failure, 88.7% to 91.4% for
steps and 88.6% to 90.8% for quality, so each one-sided test of an equivalence statement runs at
about its nominal 5%, and at worst near 6% for steps. Each is then reported as different,
equivalent or undetermined. Quality has no equivalence bound (section 7): it is reported as 
different or undetermined, with its interval. No measure is ever reported as "no effect" 
on a non-significant test alone. A null on visibility is reported as the strongest statement 
the data support ("keeping reasoning visible changes nothing by more than X", with X computed) 
beside the measured price of keeping it.

### 8.3 Sensitivity analyses

**Runs without a nudge.** Gemma's and Qwen's templates gate a past turn's reasoning on the position of the last user
message, and the finish nudge is a user message. Their keep-history flag closes the gap for
turns that made tool calls, but not for a turn that made none: the kind of turn that triggers
a nudge (section 4.1). A nudged SEEN run therefore carries a marginally weaker treatment. The primary
contrast is reported twice: over all runs, the headline, and over runs with no nudge at all,
every nudged run dropped from both arms. If the two disagree, the nudge is doing work, and the
report says so.

**Apps installed with a substituted version or an added package.** An app graded after the
`ETARGET` re-run of section 5.3 runs against a version of a dependency it did not ask for, and an
app started after an A8 (section 5.3) runs with a package it never declared. The quality contrast is
therefore reported a second time with every such app scored 0, as it would have scored had the
install or the launch been final. If the two disagree, the substitution is doing work, and the report says so.
This second test is the headline family with only the quality scores changed: it uses the same
random relabellings and resamples as the headline quality test, and its p is Holm-corrected
together with the headline family's failure and steps p values.

### 8.4 Exploratory analyses: intervals, no tests

- **Visibility without verification.** The UNSEEN -> SEEN effect inside `no_verification`
  against the same effect inside the two feedback conditions (section 2.3), and the first minus
  the second (a ratio of ratios for steps), each with its 95% interval.
- **Quality of finished runs.** Each registered contrast's quality difference over the sampled
  apps of finished runs only, with its 95% interval, beside the headline quality contrast,
  which grades every sampled app finished or not (section 6.1).
- **The within-lab pairs.** For each pair (Qwen3.6-27B with Qwen3.6-35B-A3B, Gemma-4-31B-it
  with Gemma-4-26B-A4B-it) and each registered contrast, on the three behaviour measures of
  section 6.1: the twin's estimate, the sibling's, and the twin's minus the sibling's (a ratio of
  ratios for steps), with 95% intervals made as in section 8.1 (for failure, the twin's and the
  sibling's Newcombe intervals combined by the construction Newcombe's own interval is made by,
  the method of variance estimates recovery). No test and no p-value. Outside
  every Holm family, and every number printed with the pair's confounds (section 3.1). The comparison
  speaks for these two pairs only, and the other four models (Seed-OSS, gpt-oss, GLM and Muse
  Glimmer) which have no sibling here, stay out of it.
- **API conformance** (section 6.5): the arms' difference per model and per registered contrast,
  with 95% stratified-bootstrap intervals.
- **The registered shapes** (section 1.3) and the descriptives (section 6.4).

### 8.5 Deviations

All analysis code is written and tested on fake data, then frozen at the registration freeze
(section 5.1 item 10). No grid run is made before it: the grid starts only once this protocol
is registered. Any deviation after the freeze is logged with its date and reason and reported in the paper.

---

## 9. Validity rules

**Void runs.** A run is void only for an infrastructure fault, or when the server could not
parse what the model wrote, a separate kind of void set out below. The infrastructure faults
are these: the server crashed or reset, the wrong file was served, a recorded setting differs
from section 4, or the npm registry was unreachable during the run (`ENOTFOUND`, `ETIMEDOUT` or
`ECONNRESET` around an install), which the agent would otherwise be left to debug. A run whose runner 
(the script that makes the run, section 5) fails, exiting with an error instead of ending normally,
is re-attempted up to twice (three attempts in all). A retry is not a replay: in the blind layout
each attempt has a new id and a new workspace, so its prompt and output differ from the failed
one's. The slot's analysed run is its first attempt that does not fail, so each slot still has
one run. Every failed attempt is kept, and every void's reason is logged.
The last three causes leave the runner's exit code at 0, so the batch driver keeps the run. A
run void for one of them stops the analysis, which lists its slot and cause (never its blind id
or its outcome), and the study lead re-runs the slot by hand under the same label. The listed
run then counts as a void attempt and the re-run is the slot's run. The same check
is run on each tier after its batch and before its quality sample is drawn
(`run_analysis.py check`, which prints labels and causes only), so that a re-run app can enter
the sample. How each cause is recorded and read is set out in `analysis/DESIGN.md`, section 2.

**Outcomes, never voids.** Loops, stops without a tool call, runaway replies, budget exhaustion
and context-overflow deaths are data. Overflow in particular is not an accident to retry:
keeping thoughts visible fills the context faster, and that asymmetry is part of what is
measured. A turn with neither text nor a tool call is likewise an outcome. The one exception is
the canary rule of section 5.1, which drops a broken arm before the grid, never after it. A request
the server refuses for outgrowing the window ends the run as `context_overflow` (section 6.1), which
is never re-run (section 5.1 item 8, gate G18).

**Output the server cannot parse.** Some voids are caused by the model's own output: gpt-oss
writing its channel markup in a form its server's parser rejects. Their chance depends on what
the model generates, which is what the arms manipulate, so they are not missing at random:
they are counted per model x arm, over attempts rather than slots, and reported by kind.
Without `--swa-full` (section 4.3), gpt-oss lost 9 of 20 distinct attempts this way (section 2.6), 5 of 9 in SEEN,
most of them attempts to close the run through its answer channel. With it, 3 of 18 (1 of 9
in SEEN and 2 of 9 in UNSEEN): each a garbled tool-call header and none of that kind. In the grid, 
a rate materially above one in three is a reason to stop and look, not to keep re-running. A slot still void 
after three attempts, for any cause, is left empty: it enters no analysis, and empty slots are 
reported per model x arm.

**Waivers on the record.** Three smoke gates carry registered waivers (section 5.1): Gemma-4-26B-A4B-it's
OFF canary, its OFF arm kept and watched. A run that reaches the token budget while looping,
which is an outcome, and gpt-oss-20b's unparseable-output ceiling (G14). In a smoke every retry
replays the same prompt and seed, so one bad draw voids a whole slot, and three slots per arm
make the ceiling a coin toss: with `--swa-full`, gpt-oss failed 6 of 24 distinct attempts
across four sets, which, with fresh draws on each retry as in the grid, leaves about one slot
in fifty void. Its voids are still counted per arm and reported, and in the grid the rule
above stands: a rate materially above one in three is a reason to stop and look. Any other
model's OFF canary or void rate, and any other run over or near the budget, still fails its
gate.

**One configuration.** One token budget, one harness commit, one briefing and one sampling
registry is used for the whole grid. A run made under anything else is void, and stops the analysis
until its slot is re-run (above).

**Threats these rules do not remove.**

- **Contamination.** The two task specs were written for this study, but the apps they ask for
  (a message board and a kanban board on Express, Server-Sent Events and PGlite) are common,
  and the models' training data surely hold many like them. This can raise every arm's
  results alike. It cannot favour one arm of a model, and every contrast is within a model.
  The released copies of the specs carry a canary string, so that later training corpora can
  be checked for them. The prompts the runs use are frozen and carry none.
- **Generalization.** Two tasks on one stack. Eight open-weight models (seven committed, and Muse Glimmer in the
  optional tier 6) chosen because they fit one 96 GB GPU at about four bits and their thinking can 
  be switched (section 3.2), not sampled from any population. One engine build, one machine, one snapshot of each model. 
  Results are reported per model, and nothing is claimed beyond these models, tasks and settings, nor
  across time.
- **One grader.** Every graded app is graded by the study lead, blind to its model, condition and
  arm. How consistently is measured on the re-grade set (section 5.3).

**What would make the study inconclusive** is not a mixed result but the mistakes these rules
exist to prevent: deciding after seeing the data which models count, running too few runs to
characterise each model, or measures that shift mid-study.

---

## 10. Interpretation

**The OFF arm as a built-in detector.** Agents whose model does not think before acting are
usually found to fail more. In ReAct (Yao and others, ICLR 2023,
[arXiv:2210.03629](https://arxiv.org/abs/2210.03629)), agents that only acted succeeded on 45%
of ALFWorld's tasks against 71% for agents that reasoned before each action, and on 30%
against 40% of WebShop's. So OFF is expected to differ from the thinking arms. That is what makes a null on
the primary question interpretable: if OFF -> UNSEEN moves the needle while UNSEEN -> SEEN does
not, the study has demonstrably measured an effect of how the model reasons, and the
visibility null is a finding, having the thought matters, remembering it does not. The
awkward case is written down now: if all three arms are indistinguishable on every measure in
every three-arm model, the study cannot tell "visibility does not matter" from "these tasks are
insensitive to how the model reasons at all", and it says exactly that.

**If the models disagree**, that is a result, not a failure: six labs, six training recipes,
six ideas about whether a model should see its own thoughts. Every model runs the same
protocol with enough runs to stand alone, so "model A changes, model B does not" is two facts,
not a fact and an excuse. The headline is fixed now for every outcome:

| pattern | headline |
|---|---|
| effects in most or all models, in the same direction | thought visibility broadly changes agent behaviour |
| OFF differs from the thinking arms. UNSEEN and SEEN do not | *have the thought, bin the note*: generating reasoning is what matters, and keeping it is bounded as unimportant, the outcome the ladder was built to isolate |
| effects in some models, quiet in others | visibility effects are model-dependent: which models, which measures, and the traits that go with them, verbose thinkers paying a distraction tax, say, or models trained with their thoughts in the history losing their footing without them |
| no effect anywhere, bounds tight | *have the thought, bin the note*: keeping reasoning is bounded as unimportant, at a measured premium |
| no effect, bounds loose | undetermined, and reported as such |

A mixed result is a map of where seeing one's own thoughts matters and where it does not, and
a mechanism shown in the traces (H3-H5) is worth more than a uniform effect with no
explanation.

---

## 11. Disclosure and availability

**AI assistance.** The study lead used Claude (Anthropic), through Claude's apps, to help
write and review the harness, the grading tools (the scripts in `tasks/rubrics/`), a
heuristic script that test-graded the smoke apps to check those tools (its scores are not
grades and are never analysed), and the analysis code (`analysis/` in the plan repository: the
analysis itself, its fake-data tests, the power and coverage simulations and the verification
workbook), and to help draft and edit this protocol, the rubric cards and the study's other documents.
The task specs, the system prompt and the briefing the models receive were written by the study lead. 
No language model grades any app, and no language model other than the models under study produces 
any study data. Every design decision and every grade is the study lead's.

**What is released, and when.** Code is released under the MIT licence. Documents and data
under CC BY 4.0.

- **At the registration freeze:** this protocol, registered on OSF. The frozen harness and
  grader (the archive of the tag of section 5.1 item 1). The grader's training round (score sheets,
  API probe files and setup logs, under blind ids). The precedents log. The prompt probes and
  marker tests. The grid's schedules. The analysis code with its fake-data tests and their
  log, the power and coverage figures and the verification record. And the registration record,
  with the hashes of all of these. The
  certifying smoke is already published (section 5.1 item 6).
- **Once the grid's grading has ended:** every grid run (manifest, trace, tool-call record,
  console log, server log, environment record and the app it built), the score sheets, the
  API probe files, the setup logs, the final precedents log, the analysis outputs, and the
  un-blinding keys of the grid and of the training round.

Each release documents the formats of its files. Before anything is published it is scanned
for credentials and personal data. Anything removed or replaced is marked where it was.

---

## Appendix A: Models excluded, and why

Four requirements decided every case, in this order (section 3.2): (1) the served template can
show past reasoning. (2) thinking can be switched off inside the same checkpoint: 
otherwise two arms at most. (3) the model fits the 96 GB GPU at about four bits with its
context window, on the pinned engine and its GGUF's own template. (4) it is fieldable on
its smoke runs.

**Models that reached the harness**

| model | lab | how far it got | why excluded |
|---|---|---|---|
| Magistral-Small-2509 | Mistral | wired with a registered thinking preamble (its thinking is driven by the system prompt, not a template switch), replayed inline, probed live, smoked in several sets | unreliable at calling tools: it finished 5 of 9 smoke runs, then 3 of 9. Every failure was a turn without a tool call, and every OFF run of its last smoke stopped at step 2 (4) |
| Granite 4.2-30B | IBM | wired, probed live, smoked in four sets | its SEEN arm finished 0 of 3 under two different decoders, every run spending its whole 32,768-token reply in a repetition loop (4) |
| Nemotron-3-Nano-30B-A3B | NVIDIA | wired, probed live, smoked, plus 12 OFF diagnostic runs | with thinking off it answered with a JSON agent protocol of its own instead of a tool call in 11 of 15 runs (4) |
| EXAONE-4.0-32B | LG AI Research | wired from its card and published template | its template shows past reasoning only on the last message, so SEEN would show none (1) |
| Devstral-Small-2-24B | Mistral | template extracted | no thinking mode (1) |

**Weighed at the desk**

| model | lab | why excluded |
|---|---|---|
| Olmo-3.1-32B-Think | AI2 | thinking is a separate checkpoint: two arms only (2). Muse Glimmer, which also runs two arms, joined for a sixth lab and a fourth dense model. Olmo was not reconsidered |
| Laguna XS 2.1 | Poolside | passed over for the within-lab twins. Its card warns that reasoning may stop once earlier thinking is dropped: which is exactly what UNSEEN does |
| North Mini Code 1.0 | Cohere | passed over for the twins. No documented thinking-off mode, and its card asks for thinking to be passed back |
| Qwen3-Coder-Next | Alibaba | no thinking mode (1). It also failed an earlier study's competence gate in this harness |
| DeepSeek-V4-Flash | DeepSeek | 110-162 GB at about four bits, beyond the GPU (3), and its API refuses the UNSEEN arm outright |
| Mistral Small 4 | Mistral | only a newer template than the one its GGUFs carry shows past reasoning (3) |
| Laguna S 2.1 | Poolside | its GGUF's template does not keep past thinking, and only a replacement template would (3) |
| Ling-3.0-flash | inclusionAI | the pinned engine mishandles its tool calls made before the end of thinking (3) |

**The rest of the search** was settled from each model's card and published template, by the
requirement it failed. *Template cannot show past reasoning, or ignores the switch (1):*
Hunyuan-A13B, Cogito v2 109B, Trinity Mini 26B-A3B, Sarvam 105B and 30B, K-EXAONE-236B-A23B,
Qwen3.5-35B-A3B, Qwen3.5-122B-A10B, Solar Open 100B. *No thinking mode (1):*
Kimi-Linear-48B-A3B, Granite 4.0 H-Small and H-Tiny, JoyAI-LLM-Flash, LongCat-Flash-Lite,
GroveMoE, dots.llm1, LFM2-8B-A1B, LFM2-24B-A2B, Ling-2.6-flash, Trinity Nano Preview. *No
off-switch in the checkpoint (2):* LFM2.5-8B-A1B, INTELLECT-3.1, ERNIE-4.5-21B-A3B-Thinking,
Kanana-2-30B-A3B, Instella-MoE-16B-A3B, the Ling/Ring 2.x pairs, VAETKI. *Too large for the GPU
(3):* Qwen3.8-Flash-Next, MiniMax M2, M2.5, M2.7 and M3, Step-3.5-Flash, MiMo-V2-Flash, Hy3
and Hy4 Preview, Command A+, Solar Open 2, Laguna M.1, Inkling, Trinity Large, K-EXAONE-2.0,
Kimi K3, DeepSeek V4 Pro, GLM-5.x, Qwen3.8-2.4T-A95B. *Needs another engine (3):*
openPangu-2.0-Flash, K2-Horizon-MoVA-36B-A4B, Ling-3.0-tiny. *Not available to run:* ERNIE 5.1
(hosted only), Qwen3.7 (closed weights), LFM2.5-24B-A2B (announced, not released), EXAONE 4.5
33B (outside the search, and non-commercial), Hy-MT2 (a translation model).

---

## Appendix B: Optional extension: frontier models (exploratory)

After the local study, the same switch can be approximated for closed frontier models through
OpenRouter, which returns reasoning in a standard shape that a caller may pass back on later
turns or withhold. It is fenced as exploratory, kept small (about 12 runs a side on two or
three models) and never pooled with the registered results.

- **Gemini** returns its reasoning openly, so both arms can run: the cleanest frontier target.
- **OpenAI's GPT models** never show raw reasoning, but their encrypted reasoning blocks can be
  passed back or withheld: visibility to the model without visibility to the experimenter.
- **Anthropic's Claude** requires its thinking blocks to be passed back during tool use, so
  UNSEEN breaks the API contract.
- **DeepSeek** answers a request with tools and without the past reasoning with an error
  (HTTP 400), so UNSEEN is not a configuration it permits.

That some vendors forbid the UNSEEN arm outright is itself a finding the paper reports: for
them, "the model must re-read its thoughts" is a hard API contract, not a default. The caveats
are plain: no fingerprinting (a provider can change the model mid-study), real money per run,
and rate limits shaping the schedule.
