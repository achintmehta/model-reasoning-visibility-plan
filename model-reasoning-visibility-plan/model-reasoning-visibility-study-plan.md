# Does a coding agent's model need to re-read its own reasoning?

**A study plan, written to be understandable without a statistics or ML background.**
Status: DRAFT v2.5.55, 2026-10-22, clean-room protocol. v2.1 adds thinking-OFF as a
third arm of the grid (the ladder design) and retires the separate control cell. v2.1.1
re-pins the engine to llama.cpp b10964. v2.1.2 pins the Node/npm toolchain and records it per run. v2.1.3 freezes dependency resolution with npm's `before` date instead of exact pins in the task text. v2.1.4 adds section 4.5, the reproducible grading procedure. v2.1.5 adds section 4.6, the commands in order. v2.1.6 adds the pre-run freeze items (code tag, client timeout, network void rule, machine hygiene, smoke verifications, blind-state backup). v2.1.7 records the timeout change as done. v2.1.8 makes the CUDA runtime DLLs part of the engine pin and adds the GPU checks. v2.1.9 records that the GPU gate measures GPU memory (b10964 logs no backend lines). **v2.2.0** adds section 4.2.1, the thinking-mechanism audit: the smoke set found Magistral not thinking in either arm (its reasoning is system-prompt-driven, so the harness's own system prompt displaced it) and found Seed-OSS's budget-0 mode emitting a fixed template stub, so the OFF canary rule is now written in terms of reasoning LENGTH rather than presence, Magistral gains a third arm through a registered thinking preamble, the token budget is fixed at 8M, and the Magistral preamble probe (v2.2.1) settles on the vendor text over the trimmed one. **v2.2.2** records the Seed-OSS probe: reasoning replay is now off in the OFF arm for every model, which rescues Seed's third rung and puts four of five models on the full ladder. **v2.3.0** records the clean 42-run smoke set of 2026-09-21: all ten gates in `verify_smokes.py` pass, machine time is measured at ~75 h for the whole grid, the token budget is wired through the wrapper after gate G10 caught the plan and the tooling disagreeing about it, and two shapes from the smoke set are pre-registered in section 10. **v2.3.1** adds section 4.2.2, which documents all five chat templates as extracted from the GGUFs actually served (four match the fingerprint every run records, Gemma's differs by one trailing newline), sets out what each arm sends per model, and adds a freeze gate: Magistral's and gpt-oss's templates have no slot for the reasoning field, so whether their primary contrast is real must be proven against the server rather than assumed. **v2.5.55** makes every step of the analysis checkable, at the study lead's request: each run of the analysis also writes an intermediate record (`analysis/DESIGN.md` section 12) holding every attempt and its role, every step of every analysed run, the evidence behind each run's measures, every score's weights, the units, strata, streams and seeds of every test, every bootstrap replicate and permuted statistic, Holm step by step, and the rule behind each verdict, all at full precision. A new test rebuilds every final number from that record alone. No random stream and no final number changes. **v2.5.54** answers a review of the analysis code, all before the registration freeze and without any grid data. The void rule is one rule in the protocol (section 9) and in `analysis/DESIGN.md` (section 2): a void the runner sees (a failed runner, an API error, output the server could not parse) is re-attempted by the batch driver, and a void it cannot see (a recorded setting that differs, a model file that did not resolve, the npm registry unreachable during an install, which the harness does not record and the analysis now finds in the trace) stops the analysis, which lists the slot and cause without a blind id, until the study lead re-runs the slot by hand under the same label. `run_analysis.py check` runs that check alone, after each tier's batch and before its quality sample. A context overflow filed as an API error by an older build is entered as the outcome `context_overflow` (the frozen harness records it so and exits 0). The terminal statuses are one list, copied from the harness into protocol section 6.1 and the code, which adds `truncated_tool_args` and keeps `budget_exhausted` (both are statuses the harness returns). The code now also writes the quality contrast over finished runs, the verification split's difference, `finish_nudge_steps`, and reasoning in OFF by the canary's rule. The within-lab pairs reuse the confirmatory random streams, energy is integrated by the trapezoid rule, and the substituted-0 quality test shares the headline's streams and Holm family (protocol section 8.3). Protocol sections 1.3 (H4), 7, 8.1 and 8.2 are corrected or completed. **v2.5.53** records the analysis code (`analysis/`, designed in `analysis/DESIGN.md`), written in Python with numpy only, tested on fake grids in the real file formats and on the certifying smoke set, whose gate script's per-model, per-arm numbers it reproduces exactly. Two decisions came from its fake-data tests, both taken by the study lead before the registration freeze and without any grid data. First, the interval methods (protocol section 8.1): the plain percentile interval of the stratified bootstrap covered a failure difference only about 91% of the time at 0% against 2% failure, and BCa did worse, so every difference between two shares of runs (failure, and H5) now gets Newcombe's hybrid score interval, and every other estimate a stratified bootstrap with each stratum rescaled by the square root of k / (k - 1), which also lifts the quality interval from about 93% to 94% coverage. Second, a void attempt that `blind_tools.py sample` puts among a cell's first ten is left there, enters no analysis and is counted (protocol section 5.3). The power figures of protocol section 7 are recomputed under the registered tests (`analysis/power-results/`): the failure figures are lower than first stated (2% against 15% is detected 90% of the time, not 96%) because the first figures left out the Holm correction, and the equivalence figures stand (99.8% at 2%, 91.4% at 5%). **v2.5.52** rewrites the plan and the protocol in plain ASCII, at the study lead's decision: no em or en dashes, no semicolons in sentences, and no section signs or other non-ASCII characters (section numbers are written out as "section 5.1"). The meaning is unchanged, and quotations of prompts and outputs are kept verbatim. It also fixes the analysis seed, `61f43c6f3593702f`, and the analysis choices the protocol had left to the code (protocol sections 8.1 and 8.2): steps are permuted among the finished runs of each stratum, and every interval, the 90% intervals of the equivalence tests included, is the percentile interval of the stratified bootstrap. **v2.5.51** fixes the seed of the quality-sample and re-grade draws, `bb696caef027c79c` (16 random hex digits, drawn with Python's `secrets` on 2026-10-21), one seed for every draw, with the draw names `tier1` ... `tier6` and `fresh-<task>-<k>` (protocol section 5.3). **v2.5.50** records the grid's schedules, made on 2026-10-21 in the grid's own checkout of the frozen tag (`/mnt/d/eval-coding-agent-grid`, a `git worktree` at `90a4758`), one per batch command, with `STOP` set so that no run would start: 2,640 runs (gemma-q4, qwen-q4, seed-q4 and glm-q4 360 each, gpt-oss-20b and Muse Glimmer 240 each, the qwen-moe and gemma-moe pair 720), each model's arms 120 runs apiece. Files, signatures and sha256s in the plan repository, `registration/schedules/`. **v2.5.49** corrects the protocol's toolchain row to what every certifying smoke run recorded, Node v24.21.0 with npm 12.0.2 (it still named v18.20.8 and 10.8.2), and adds to the protocol, following the LLM-guidelines checklist for software engineering research: how each request is put together (zero-shot, no context files, section 4.6), compute and energy reporting (section 6.2), the threats the design does not remove (contamination, generalization, one grader, section 9), and a new section 11 on AI assistance and on what is released and when (MIT for code, CC BY 4.0 for documents and data). **v2.5.48** freezes the harness and the grader together, at the study lead's decision: commit `90a4758`, tag `model-reasoning-visibility-plan-freeze-101926` (archive sha256 `6ee3bb58...066b`, in the plan repository), which is the certified `5ac366f` plus the grader at card version 2.2 in `tasks/rubrics/`, a folder no run reads. The grid runs from this tag, so its manifests show `harness_git` `90a4758` where the certifying smoke shows `5ac366f`. Every file a run executes or reads is the same. The same tag is the grader freeze. **v2.5.47** adds accommodation A8, at the study lead's decision, after a certifying smoke app could only be started once a package its declared script runs, and which it never declared, was installed by hand: when a part fails to start because its own code imports, or its own declared script runs, a package no `package.json` of the app declares, and the error names it, exactly that package is installed with `npm install --no-save <name>@latest` (nothing but `node_modules` is written), after A1-A6 and before A7. The part fails its launch item (L1 or L2) as after any accommodation, L3 is judged on that launch, and the quality contrast's second report (protocol section 8.3) scores these apps 0 alongside the `ETARGET` ones. **v2.5.46** halves the grading and commits tiers 1-5, at the study lead's decision, after timing the training rounds at about 30 minutes a kanban app and 20 a message-board app (about 1,320 hours for the whole grid). Every run is still made, and failure incidence, steps and the mechanism measures use every run. App quality and the API probe use **the quality sample**: ten of the twenty apps of every model x task x condition x arm cell, drawn before each tier is graded with a seed fixed at the freeze (`blind_tools.py sample`). Only these are graded, and the re-grade set is two of them per cell. Quality power falls from shifts of about 0.4 to about 0.6 standard deviations (about 24 points at the training rounds' spread, SD about 41). Failure and steps keep full power. At that spread the +/-10-point equivalence statement on quality could not be reached, so it is dropped: quality is reported as different or undetermined. Tiers 1-5 (2,400 runs, about 600 grading hours) are committed. Tier 6, Muse Glimmer, is optional. The sample is drawn as a random grading order within every cell, of which the first ten are graded, so every model, task, condition and arm has the same number of graded apps. If time allows, a whole tier can be extended to the eleventh, twelfth, ... app of every cell (`blind_tools.py extend`), decided by time and never by results. **v2.5.45** extends A0 to an app's own failing install script, at the study lead's decision: 3 of the 66 certifying smoke apps carry a root `install` script that runs `cd backend && npm install && cd frontend && npm install` (or the same with other folder names), whose second `cd` starts from the wrong folder, so the root install stops although every folder's dependencies install. The install is re-run with `--ignore-scripts`. L0 still fails. **v2.5.44** extends accommodation A0 to `ETARGET`, at the study lead's decision: 4 of the 66 certifying smoke apps asked for a version of `@electric-sql/pglite` that was never published (`^1.0.0`, `^0.8.4`, `^0.1.20`, `^0.0.10`) and so scored 0 on one wrong number. The install is re-run with `npm install --no-save <that package>@latest`, which edits no file. L0 still fails, and the quality contrast is reported a second time with these apps scored 0. **v2.5.43** drops the separate deciding round of the rubric's calibration, at the study lead's decision: the certifying smoke's 66 apps become the training rounds' apps, graded once each and never in the analysis, and no other runs are made for calibration. The cards are frozen (`grader-freeze`) when the training rounds leave no call unclear. The grid's own re-grade set gives the first consistency check, against the same bar, with the fresh-set procedure if it falls below. The training rounds give a first measure of the score's spread for the power computation, recomputed at the first check, and the report says the cards were frozen before their consistency was measured. The training rounds use only this study's own smoke apps, not those of another study (`batch-20260613` is dropped). The launch items go from six to four: the backend's "code runs" and "no manual step" items merge into one (L1, weight 3: the declared command starts the backend, with no accommodation), and so do the frontend's (L2, weight 3: the declared command starts it and its page loads). The page reaching the backend becomes L3. Message-board is now 15 items and kanban 26, with their weights unchanged at 27 and 50. A new accommodation A6 starts a part with its declared command corrected only in the entry point or config file it names, and the old last resort becomes A7.  **v2.5.42** drops the message-board card's two empty-message items, at the study lead's decision, and moves the server half into the API probe as an unscored observation. MB-E2 asked the grader to POST `{"text": ""}` from the browser console and passed a 4xx answer. The spec says nothing about empty messages, and the rule for the probe is that only what the spec states exactly is scored. The probe now records, last, how the server answers an empty message (`empty_message`: `{"text": ""}`, and the body field MB-API3 found if that is another, the status, refused, accepted, no such route or server error, and whether a blank message was stored). MB-E1, the interface half (step 7: submit with the input empty, and no entry may appear), has no spec basis either and leaves the card with it. Steps 7 and 9 go, the rest are renumbered (reload 7, kill and restart 8, look-back 9, API probe 10), and MB-U1 no longer needs to ignore an empty entry. MB-U2 ("apart from the reloads the script asks for, the page never needed a reload") leaves too: no spec task states it (the nearest is 4.4's "seamlessly") its concrete failures are already scored by F1, F2 and R2-R4, so it risked charging one defect twice, and as a judged catch-all it was the item likeliest to score differently at the 14-day re-grade. Message-board is 17 items and weight 27 (rubric v2.1). The kanban card's KB-U2 is unchanged. The kanban card's KB-D5 (the optimistic move with the backend paused) is reworded to its spec tasks: at 1 s the card is in its new slot (4.3), and within 5 s of resuming it is in the server's slot, has not gone back, and never shows in two places (4.4, 4.5). "disappear or blink" and "flickers" leave it, since no spec task states them and judging them would vary between gradings. The kanban card also loses two items with no exact spec basis, which the cards' new spec column made plain: KB-D8 ("after reloading, the card is back in its original place" for a card dropped outside every column, the spec never addresses such a drop) and KB-U2 (the same catch-all as MB-U2). KB-D9 stays: the board A showed before the reload must be the one it shows after (4.3, 4.5, and acceptance criterion 5), so a card that jumps on screen but not on the server still fails. KB-D2's sources gain 4.3 and Decision 3, KB-D9's acceptance criterion 5. Kanban is 28 items and weight 50 (kanban rubric v2.1). The grader gains `backend.sh`, which finds the app's backend by itself (the process listening on a TCP port whose folder or command line is inside the app, and which is not the frontend's dev server by its command line or by serving Vite's page), acts on that listening process rather than `npm` or `concurrently` above it, and pauses, resumes or kills it. With no candidate or several it lists what it saw and takes `-p <port>`. The cards' pause steps (kanban 9, 11, 12) and restart steps (kanban 14, message-board 8) now name it, in place of finding the process id by hand. Steps 9 and 11 stay separate: a D5 read during step 11's conflicting drags would depend on B's move. Only grader files change. The frozen harness and the certified smoke do not. **v2.5.41** records the certifying smoke. It was made from commit `5ac366f4175dc0929c28ad45e1560d26760f83fa` on 2026-10-07, 66 runs in 6.3 hours, every run's `harness_git` that commit with no `+dirty`, and every gate passes, G2 by its registered waiver for Gemma-4-26B-A4B's OFF arm (its longest OFF reasoning 80,891 characters). No run reached the budget: the peak was 7.9M, GLM-4.7-Flash's UNSEEN `message-board`/execution run, which took a different path from the judged run of v2.5.39, so that waiver was not needed. `G9_JUDGED` keeps it, bound to the old trajectory. No slot was voided and no attempt failed. The harness moved reasoning out of the reply text on 23 steps (Seed-OSS: 18 UNSEEN, 5 OFF), all at a closing tag, so the opening-tag list is empty. One leftover was taken out of the set before it was checked: the killed run of the aborted smoke on `a48c79f` (Qwen3.6-35B-A3B OFF, `message-board`/interactive, stopped at the step-36 hang), which the batch runner had filed as that slot's failed attempt because its folder was still in the output root. It was not made from `5ac366f` and is kept apart, with the aborted set. Server logs: 1.69 GB for the 66 runs (median 16.8 MB, largest 102 MB). This set replaces every earlier one. The deciding round of the rubric's calibration (section 9) is graded on its 66 apps. The commit is tagged `model-reasoning-visibility-study-freeze-100826`. Its archive (86 files, checked identical to the tag) has sha256 `a96e1233eb518605ce068f684e1b6f2301510514a6d569d9ba02332d73a8de49`, and the smoke set is published as `achintmehta/model-reasoning-visibility-study-smoke-runs`, archived on Zenodo under CC BY 4.0 as doi:10.5281/zenodo.23239990 (version v1.0.0, concept DOI, all versions, doi:10.5281/zenodo.23239989). **v2.5.40** fixes a hang in the shell tools, at the study lead's decision, so the grid waits for one more certifying smoke. The smoke on commit `a48c79f` stopped for good at run 45, Qwen3.6-35B-A3B's OFF `message-board`/interactive run, and its predecessor had stalled at the same point: at step 36 the model sampled its SSE stream with `run_command_and_capture_output` (`timeout 3 bash -c '(curl -s -N .../api/stream > f &); sleep 1; curl -X POST ...; sleep 1; kill %1; cat f' 2>&1`, duration 5). GNU `timeout` moves itself and its children to a process group of their own, so the backgrounded curl (an SSE stream that never ends) outlived the tool's group kill with the tool's stderr pipe open, and the tool, after the kill, waited for that pipe's end with no limit. Reproduced offline. The tools now signal the command's whole SESSION (a process leaves it only by calling setsid), never wait on the pipes without a limit after a kill, and `stop_background_command` and the end-of-run teardown kill a background command's whole session too, so nothing a run started outlives it. `test_capture_output_hang.py` pins the hang's exact shape, the same through `run_command`, a child that left the session, and the teardown. **v2.5.39** follows the smoke made on 2026-10-06 from commit `2ea877a` (66 runs, every gate passing but G9, G2 by its waiver), at the study lead's decisions, and changes the harness, so the grid waits for one more certifying smoke. (1) *Gemma's opening tag only with its name.* The set's one split at an opening tag, listed by v2.5.38 for checking by hand, was wrong: a Gemma-4-26B-A4B OFF reply (`message-board`/interactive, step 23) was a tool call opened with `<|channel>` instead of `<|tool_call>` (`<|channel>call:run_command{...}<tool_call|>`) and the harness had filed its 2,583 characters as reasoning, so the failed call vanished from the history, where any other model's call written as text stays. The harness now takes Gemma's opening tag only as `<|channel>thought`, the way a Gemma thought begins. A bare `<|channel>` stays in the reply, and a call behind it counts as `callTxt`. G4 looks for `<|channel>thought` too. The other 26 splits, all Seed-OSS at `</seed:think>`, were checked and held no call markup. (2) *A judged G9 waiver.* GLM-4.7-Flash's UNSEEN `message-board`/execution run reached the 20M budget at step 347 without meeting either looping rule (27 of its last 30 calls repeat earlier ones, 15 distinct). By eye it was stuck: from about step 100, 56-92% of the calls in each 25-step block repeat a call already made. For about 250 steps it alternated between two PGlite import forms, restarting the server and probing `/health` 41 times. Its last reasoning reports the same import error. The study lead judged it stuck rather than widen the rule a third time or raise the budget (the only other runs ever to reach 20M were looping, every other peak was under 8.6M). `verify_smokes.py` records the judgement in `G9_JUDGED`, keyed by slot and holding only for that run's trace fingerprint (`983e9b6b92b0ba8d`): a run of the slot that goes differently fails G9 until judged again. **v2.5.38** extends the reasoning recovery to Gemma 4's thought channel, at the study lead's decision, so the grid waits for one more certifying smoke. The smoke made on 2026-10-05 from commit `d11e15b` (66 runs) passed every gate under the previous script, but the G4 of v2.5.37 failed it on one step: the last reply of a Gemma-4-26B-A4B OFF run (`kanban-board`/execution) began with Gemma's channel opener `<|channel>` and repeated one line 1,212 times to the 32,768-token cap, filed as reply text. The run ended `runaway_no_tool_call`, so nothing was replayed after it. The same set showed the v2.5.37 recovery working: 10 Seed-OSS steps moved, 5 UNSEEN and 5 OFF, recorded in each manifest, and no Seed tag left in any kept reply. Seed's UNSEEN leaks fell from 75 steps to 5, consistent with replayed tag-less thinking having fed the pattern. Of three choices: not failing G4 on a run's final, never-replayed step. Extending Gemma-4-26B-A4B's G2 waiver to G4, or splitting at Gemma's channel tags too: the third was taken: the harness now treats `<channel|>` as a closing tag and `<|channel>` (with its channel name, `thought`) as an opening one, exactly as the think tags, and `verify_smokes.py`'s independent copy of the rule does the same. gpt-oss's channel syntax (`<|channel|>`, `<|message|>`) is a different grammar and is not split. G4 still fails on it, as on any think or channel marker the harness does not split. G4 also now fails on any roster template's turn-structure marker in the reply text (`<|im_start|>`, `<|im_end|>`, `<|turn>`, `<turn|>`, `<|start|>`, `<|end|>`, `<|return|>`, `<|call|>`, `<|eot|>`, `<|eom|>`, `<|system|>`, `<|user|>`, `<|assistant|>`, `<|observation|>`, `<seed:bos>`, `<seed:eos>`): not reasoning, but a sign the server mis-split the output, which no other gate would see. The 2026-10-05 set has none. And because a split at an opening tag never closed assumes the thought ran to the end of the reply (the only case where where it ended is inferred, not marked) `verify_smokes.py` counts those splits apart from the closing-tag ones (G4's line and an `atOpen` column) and lists each step, with its tag, the characters moved and the run's status, for checking by hand. Re-checked, the 2026-10-05 set's Gemma step counts as OFF reasoning (128,655 characters), listed under that model's G2 waiver. **v2.5.37** settles G4 and the lost-call question (section 9 items 3b and 0), at the study lead's decision, and changes the harness, so the grid waits for one more certifying smoke. (1) *Reasoning left in the reply text.* Asked what G4 should look for, every step of the 2026-10-04 smoke was searched for think and channel markers in its reply text. Only Seed-OSS had any: on 75 of its 131 UNSEEN steps, 2 of 23 OFF and none of 128 SEEN, it began thinking without writing `<seed:think>` (the server's token log shows the first token is prose) and closed with `</seed:think>`, so the server filed the whole thought as reply text and the next request's rendered prompt carried it word for word: UNSEEN showing past reasoning on most of Seed's steps, which the old G4, looking only for opening markers, passed. The harness now does what the server would have done had the tag been written (`harness/agent.py`, `split_reasoning_from_text`): when a reply's text holds a closing think tag (`</seed:think>`, `</think>`, `[/THINK]`) the text up to the last one is reasoning and the rest is the reply, and an opening tag never closed splits there. The rule names tags, not models, runs on every turn of every arm before the turn is counted, replayed or discarded, keeps the server's message untouched in the trace beside the reply as kept, and is counted per run (`reasoning_recovered_turns`, `_chars`, `_markers`). `test_reasoning_recovery.py` pins it offline in both replay modes. G4 now fails on any think marker, opening or closing, or Gemma 4 / gpt-oss channel marker, in the reply text as kept, and recomputes the recovered reasoning itself so G2, G3 and a new `recov` descriptive count it as reasoning. G2 stops counting Seed-OSS's `<seed:cot_budget_reflect>` budget reports, one of which, split between the field and the text, measured 229 characters once the text was counted. Re-checked under these gates, the 2026-10-04 set fails G4 on exactly its 77 Seed-OSS steps and passes the rest, Seed's UNSEEN reasoning rate rising from 42% to 98%. (2) *The lost calls.* At `-lv 5` the server log keeps every generated token, so no replay was needed: in all 9 of Qwen3.6-35B-A3B's lost UNSEEN calls in that set the model wrote prose and then only the closing tags, never an opening `<tool_call>` or `<function=` and never `</think>`. Behaviour, an outcome counted as `callTxt`. The parser lost nothing. The tag on `600a8d2` is superseded. The commit carrying (1) is tagged once its smoke passes. **v2.5.36** records the marker tests (section 9 item 3): every model ACCEPTED. The seven not yet tested were probed on 2026-10-05 with `tools/probe_reasoning_replay.py --model-key <key>`, each against a server the wrapper at commit `600a8d2` started (through a throwaway `no_verification` run, outside the study's folders), so each probe sent its model's own thinking-arm body with the frozen serving flags. Each model repeated the codeword that existed only in the replayed reasoning. Qwen3.6-27B did so in its reasoning, with an empty reply, which the probe counts by design. With Muse Glimmer's of 2026-09-30, all eight pass, so no model leaves the roster. **v2.5.35** records the certifying smoke on the commit that removes private-endpoint routing, at the study lead's decision. Commit `600a8d2565226c220b3db6c5e44511fc78277fca` deletes three scripts of an earlier study (`run_batch.sh`, `rerun_batch.sh`, `extra_replicates_targeted.sh`), removes from `run.sh` the routing of a hosted endpoint no grid model uses, and rewords two comments in `harness/agent.py` and `harness/llm.py`. No path a grid run takes changes, but `run.sh` is on that path and every manifest records `harness_git`, so the smoke was made again: on 2026-10-04, in 6.5 hours, 66 runs, every run's `harness_git` that commit, and every gate passing, G9 by its waiver, for a GLM-4.7-Flash SEEN kanban/execution run that reached the 20M budget while each of its last 30 calls repeated an earlier one. G2 passes outright (longest OFF stub 134 chars), no run overflowed its context, and gpt-oss again lost one SEEN kanban/execution slot to unparseable output: three byte-identical attempts, one void, under G14's ceiling. This set replaces the one made at `76f2770`, and the commit is tagged `model-reasoning-visibility-study-freeze-100426`, the tag this plan calls `study-freeze`. **v2.5.34** records the certifying smoke and widens G9's loop waiver, at the study lead's decision. The smoke was made from a checkout of commit `76f27706eddb289ba3772f30627c77e3a289fa05` on 2026-10-04: 66 runs, 7.4 hours, every run's `harness_git` that commit with no `+dirty`, every server started at its new window (Seed-OSS at 262,144 among them), and every gate passing but G9. gpt-oss lost one SEEN slot to its answer-channel failure, under G14's ceiling without the waiver. Qwen3.6-27B had one UNSEEN `context_overflow` at 262,144, kept as an outcome with its totals (G18). G9 failed on Gemma-4-26B-A4B's OFF message-board/interactive run, which reached 20,047,498 tokens in 385 steps. It was looping: from about its 110th call it cycled through rewriting `db.js` among three PGlite import forms, stopping the server, starting it, opening the page and reading the log (the file-state note counts 61 reverts, one content written 23 times) and, numbers masked, its last 100 calls are all calls it had already made, 8 distinct. G9's waiver for a run that reaches the budget while looping (v2.5.14) asked for at most 3 distinct calls among the last 30, which a five-call cycle with three edit variants does not meet, and the harness's no-progress guard did not end it because each cycle's `stop_background_command <pid>` and `tail .agent_logs/cmd_out_<timestamp>.log` carried new numbers (masking them in the guard was considered in v2.5.33 and not adopted). The waiver now also accepts a run whose last 30 calls, numbers masked, each repeat a call it had already made earlier in the run: the harness's no-progress definition with pids and timestamps masked. The change was made after seeing this run, and is recorded as such. It lives in `verify_smokes.py`, outside the harness, so it does not change `harness_git`. Re-checked, the set passes every gate, two of them by registered waivers (G2, G9). This is the certifying smoke (protocol section 5.1 item 6): commit `76f2770` is the one to tag `study-freeze`, and `verify_smokes.py` is to be brought into the repository before the tag, so the archive carries the gates that certified it. **v2.5.33** fixes the shell tool's timeout, at the study lead's decision, after a run in the smoke on commit `799e87e` cycled for more than 50 steps: start the backend in the foreground with `run_command`, have the call time out after 180 s, fail to start it again in the background (port in use), find the holder with `lsof`, kill it by pid, and start it in the foreground once more. The tool used `subprocess.run(timeout=...)`, which on a timeout kills only its direct child, the `sh -c` shell. The server that shell had started lived on in its own process group, still holding its port, while the tool told the model it had been "terminated". The tool's result was false, and the loop followed from it. `_run()` in `harness/tools.py` now starts the command with `Popen` and, on a timeout, kills its whole process group and reaps it, and the message says that the command was terminated together with every process it started. A child that deliberately left the group (`setsid`) cannot hang the call: after two seconds its pipes are closed. Behaviour is otherwise unchanged: output, exit codes and the signal note are as before. Tested by a new `test_timeout_kills_group.py`: a never-exiting foreground server returns at the timeout and its port is free afterwards (under the old code it stayed open), ordinary and signal-killed commands report as before, and an escaped child does not hang the call. The existing test scripts pass. The no-progress guard was left as it is: that run's `kill -9 <pid>` calls differ only in the pid, so the guard did not see them as repeats, and masking long numbers was considered and not adopted. The smoke on `799e87e` was stopped. The certifying smoke is made on the commit that carries this fix. **v2.5.32** follows the certifying smoke made on commit `c5e0b69` (2026-10-03: 66 runs, harness clean, every gate but G14 passing), at the study lead's decisions, and needs one more smoke on the commit that carries it. (1) *Every model at its native window where it fits.* Read from the GGUF headers and computed at f16 with `--swa-full`: Qwen3.6-27B and Qwen3.6-35B-A3B go to their native 262,144 (about 17 and 5 GB of cache, their attention being one layer in four), and Gemma-4-26B-A4B to its native 262,144 (about 59 GB, its OFF kanban/execution run in that smoke outgrew 131,072 at step 196). Seed-OSS goes to 262,144, the most that fits, not its native 524,288 (64 full-attention layers at 256 KB a token would need about 137 GB). Gemma-4-31B stays at 65,536: with `--swa-full` all 60 of its layers keep a full cache, about 0.9 MB a token, so its native 262,144 would need some 236 GB and the card holds about 89,000 tokens. Its smokes never passed about 20,000. gpt-oss, GLM and Muse were already at theirs. llama-server allocates the cache at boot, so a window that does not fit fails at startup, never mid-run, and the smoke shows it. (2) *gpt-oss stays, with G14 waived for it.* That smoke voided 2 of gpt-oss's 3 SEEN slots (both the answer-channel kind, each replayed word for word by its retries) and 1 UNSEEN slot. With `--swa-full`, gpt-oss has now failed 6 of 24 distinct attempts across four sets (the answer-channel kind 2 of 24, against 5 of 20 without the flag). In a smoke a retry replays the failure, so one bad draw voids a slot and three slots per arm make G14 a coin toss. In the grid each retry is a fresh draw, and at about one in four per attempt roughly one slot in fifty ends void. So G14's ceiling is waived for gpt-oss alone, as G2 is for Gemma-4-26B-A4B: its voids are listed, counted per arm and reported, with the worst case (every void a failure) beside the estimate, and section 9's stop-and-look rule stands in the grid. `verify_smokes.py` gains `G14_WAIVED`. (3) *A harness fix found in that smoke.* A run ended by `context_overflow` lost its summary (total tokens, reasoning counts, tool-call counts, guard counts) because the refusal escaped the agent loop before `get_extra_data()` ran. The trace keeps no token usage, so the cost measure could not have been recovered for those runs. The loop now catches the refusal and returns `context_overflow` with its summary. Tested against a mock server. The harness's test scripts pass. Wrapper `2026-10-03-native-ctx`. **v2.5.31** makes two fixes, found while the certifying smoke on commit `6a2462c` was running. That smoke was stopped and is to be made again on the commit that carries them. First, the run wrapper hard-coded the harness's folder (`AGENT_DIR=/mnt/d/eval-coding-agent`), so a run launched from any other copy of the repository still ran that folder's `harness/` and `run.sh`, and recorded that folder's state as `harness_git`. It now takes the folder the wrapper sits in (overridable with `AGENT_DIR` only deliberately), so the grid can run from its own checkout of `study-freeze` and nothing changed in the working copy (the rubric cards, which live in the same repository and are frozen after the grid may have started (v2.5.25)) can reach a grid run (protocol section 5.1 item 1). Second, the manifest's `decoding_overridden` compared each run's samplers with `llm.DECODING_DEFAULTS`, the greedy defaults of an earlier study, so every sampled run was stamped as overridden although it sent exactly its registered values. G15 was never affected, since it checks the values against the registry itself. It now compares temperature, top_p, top_k, min_p and presence_penalty with the run's profile in `decoding-registry.json`, and max_tokens with the 32,768 cap, recording `decoding_overridden_basis` (`registry`, or `fallback_defaults` for a run given no profile). Tested against a mock server: registered values give `{}`, an off-registry temperature or an omitted top_k are listed. The harness's seven test scripts pass. Wrapper `2026-10-03-agentdir-local`. **v2.5.30** records each model's native window (the `context_length` its GGUF header declares) beside the window it runs at: a new column in the protocol's section 3.1 roster, a short definition of both there and in section 4.3 of this plan, and a correction to Muse Glimmer's entry, whose file declares 131,072 rather than "262,144 at most". Documentation only. No setting changes. **v2.5.29** raises GLM-4.7-Flash's context window from 131,072 to its native 202,752, at the study lead's decision. In the 2026-10-01 smoke its kanban/execution SEEN run outgrew 131,072 (a 132,135-token request, refused with HTTP 400) and the rule every model's window follows is the smallest with no overflow in its smoke runs (protocol section 4.3). The window cannot go higher: 202,752 is `deepseek2.context_length` in the GGUF header. GLM's MLA attention keeps its cache small (a 512-wide latent and a 64-wide rotary key per layer, 47 layers): about 11-21 GB at 202,752 tokens beside 18.3 GB of weights, on the 96 GB card. A run that outgrows even this ends as `context_overflow` (v2.5.28). The other models' windows are unchanged. Wrapper `2026-10-02-glm-ctx-202752`. The certifying smoke, made after this change, confirms that GLM serves at the new window. **v2.5.28** settles how a context overflow is filed (protocol section 5.1 item 8), at the study lead's decision: as an outcome. llama.cpp b10964 refuses a request that has outgrown the window with HTTP 400 (`exceed_context_size_error`, with `n_prompt_tokens` and `n_ctx`), as the 2026-10-01 smoke showed on GLM-4.7-Flash SEEN. The harness had filed that as `api_error` and the batch driver re-ran the slot, replacing the overflow. Now `llm.py` recognises the refusal (`context_overflow()`), never retries it, and `agent.py` ends the run with a new terminal status, `context_overflow`, records the server's token counts and the step in the manifest's `context_overflow` field, and exits 0, so the batch driver keeps the run. It counts as a failure, beside `truncated_no_tool_call`, the overflow that cuts a reply short. Tested against a mock server that refuses the second request: status `context_overflow`, exit code 0, no `api_error`. `verify_smokes.py` gains G18, which fails any run or kept failed attempt filed as `api_error` with an overflow body and counts `context_overflow` runs per model x arm. On the 2026-10-01 smoke it fails, rightly, on GLM's re-run SEEN slot. **v2.5.27** fixes llama-server's log level at `-lv 5`, at the study lead's decision, for every run: until now the default, 3, was frozen and higher levels were a diagnostic only. At 5 each run's server log keeps every request's rendered prompt and the model's raw output before parsing, so every run records for itself that its arm reached the template, and every output the parser rejected is kept whole. Logging does not change generation. The 66-run smoke of 2026-10-01 had in fact been made at `-lv 5` (an uncommitted `SERVER_VERBOSITY="5"` in the batch driver), and gives the cost: 1.7 GB of server logs, median 18.5 MB a run and at most 127 MB, so about 70 GB across the 2,640-run grid, about 4 GB under `zstd -19`. Wiring: `-lv 5` joins `FROZEN_FLAGS`, last, so that smoke's banners read as frozen-spec ones. `SERVER_VERBOSITY` now defaults to 5, and any other digit makes a diagnostic run. The line in the batch driver is removed (wrapper `2026-10-02-lv5-frozen`). Gate G17 now compares each run's banner with the whole frozen flag set, `--swa-full` and `-lv 5` included, so a flag missing, added or changed fails: that smoke passes it, and the gpt-oss control made without `--swa-full` fails it. The same smoke also confirmed what section 5.1 item 8 left to be confirmed: llama.cpp b10964 refuses a request that outgrows the window, with HTTP 400 ("request (132135 tokens) exceeds the available context size (131072 tokens)", GLM-4.7-Flash, SEEN), and the batch driver re-attempted it, replacing an overflow with a fresh run. How that is filed is still open. **v2.5.26** serves every model with `--swa-full`, at the study lead's decision, for uniformity: v2.5.24 gave it to gpt-oss alone, on the evidence of its parse failures. Read from the GGUF headers, four of the eight models have sliding-window attention (gpt-oss-20b (window 128), Gemma-4-31B and Gemma-4-26B-A4B (1,024, on 5 of every 6 layers) and Muse Glimmer (2,048)) and on them the flag makes partial reuse of the prompt cache exact. Qwen3.6-27B and Qwen3.6-35B-A3B (recurrent layers with full attention every fourth), Seed-OSS and GLM-4.7-Flash (full attention) are unchanged by it. Gemma and Muse showed no unparseable output without it, so this is not a fix for them. Its cost is GPU memory, computed from the headers at f16: about 54 GB more for Gemma-4-31B at 65,536 tokens (some 78 GB with weights and the full-attention layers, on the 96 GB card), 27 GB for Gemma-4-26B-A4B at 131,072, 5 GB for Muse and 3 GB for gpt-oss, and possibly speed, since a sliding-window layer's attention may now run over the whole cache at long contexts. The final certifying smoke on the clean commit measures both: G16 would show a reply slowed past the client timeout, and the runs' timings any change to the machine-time estimate. The flag moved into the wrapper's frozen flags (wrapper `2026-10-01-swa-full-all`). `NO_SWA_FULL=1` drops it, for diagnostics only. G17 now expects it on every run. **v2.5.25** moves the grading to one grader, at the study lead's decision. One grader grades every app. The score of record is its first grading. A seeded draw before each tier picks a fifth of the apps (four of every model x task x condition x arm cell) for a blind re-grade under a second blind id, at least 14 days after the first grading, mixed in among first gradings of later apps. The two gradings measure the grader's consistency (test-retest), against the same bar as before: a mean absolute difference of at most 5 points per task, in checks of at least 24 re-graded apps. ICC and per-item kappa reported only. The calibration's deciding round is graded and then wholly re-graded after 14 days. Grid runs may be made during that cool-down, but no grid app is graded or un-blinded before the cards freeze, and the grader is then tagged on its own (`grader-freeze`). The workload is unchanged at 3,168 gradings, about 607 hours, now all one person's. The limitation is stated: consistency is not agreement between people, and a misreading applied consistently passes. In exchange, every arm is graded by the same person. Changed: protocol section 5.1 items 1 and 9, section 5.3, section 6.1, section 6.5 and section 7. This plan's section 4.5 and section 9. The rubric README. **v2.5.24** serves gpt-oss with `--swa-full`, at the study lead's decision, and adds gate G17. The 66-run certifying smoke failed G14 on gpt-oss alone: its server could not parse its output in 5 of 8 distinct attempts, voiding 2 of 3 SEEN slots and 1 of 3 UNSEEN. llama.cpp issue #27720 ties gpt-oss's malformed harmony headers to partial reuse of the prompt cache, which its server logs showed on nearly every turn. No newer engine build fixes the parse (the maintainer declined a lenient parser), so the engine pin stays at b10964. `--swa-full` keeps gpt-oss's whole sliding-window cache, so reuse is exact. It is a per-model serving flag, the same in both arms, recorded on the args line of every run's server log. Four sets on 2026-10-01 decided it: without the flag, the smoke (replicate 01) and a 12-run control on replicate 02 with both arms on both tasks lost 9 of 20 distinct attempts (SEEN 5 of 9, UNSEEN 4 of 11), 5 of them attempts to close the run through the answer channel. With it, a re-smoke of gpt-oss's six slots at the same paths and seed and a 12-run diagnostic on replicate 02 lost 3 of 18 (SEEN 1 of 9, UNSEEN 2 of 9), none of that kind (Fisher's exact p = 0.09 overall, 0.048 for the answer-channel kind). Without the flag only 1 of 6 SEEN runs on replicate 02 finished. With it, 3 of 6. The registered gpt-oss shape (section 1.3 of the protocol) now shows as stops without a tool call rather than voids. Wiring: `MODEL_SERVER_FLAGS` in the wrapper's model map (wrapper `2026-10-01-gptoss-swa-full`), a diagnostic-only `NO_MODEL_SERVER_FLAGS=1`, and `gptoss_swa_diag.sh`. `verify_smokes.py` G17 checks every run's flags against `EXPECTED_SERVER_FLAGS` (`--swa-full` for gpt-oss, none for any other model). These sets ran on harness `d9d7492+dirty`, the earlier 60 on `b61c604+dirty`. The certifying smoke is to be made once more, whole, on the clean tagged commit. **v2.5.23** retitles the study, at the study lead's decision, from "Do AI agents need to re-read their own thoughts?" to "Does a coding agent's model need to re-read its own reasoning?": the agent is the model inside a harness, and it is the model that does or does not see its earlier reasoning, by the harness's choice. The protocol's section 1.1 now opens by saying so, and its passages on memory and reliability speak of the model. Nothing in the design changes. **v2.5.22** moves the API check out of the rubric and into a probe, at the study lead's decision. Noting each request's method and path in the Network panel cost the graders time on every app, so the API items I1-I5 of v2.5.21 are withdrawn, and the steps that asked for them go back to their earlier wording. In their place, once the score sheet is complete and with the app still running, the grader runs `api_probe.py`, which calls the backend directly and checks only what the spec states exactly (tasks 2.4 and 3.1-3.3): 4 checks for message-board, 10 for kanban, including the move body `{ columnId, beforeId, afterId }`, where the moved card lands, and the broadcasts. A failed check counts like any rubric failure. Where the spec leaves open a detail the probe needs (it names no body field for a new message or card), the probe tries the likely names and files what it cannot settle as inconclusive, outside the share. JSON shapes and the field names that worked are recorded as observations, never scored. The probe measures the backend, not the page's requests, so a dev-server proxy that rewrites the paths now fails it. Its results form a separate, exploratory outcome, API conformance (the protocol's section 6.5 and section 8.4), and the probe is frozen and hashed with the grader. The checks are numbered MB-API and KB-API, because P1 is already the persistence item. Tested on 12 of the earlier smoke apps and on mock backends built to break each check. The install item L0 of v2.5.21 stays: message-board is now 20 items and weight 30, kanban 30 and 52. **v2.5.21** adds two kinds of rubric item, at the study lead's decision, both grading what the specs state. First, an install item, L0, the first launch item: the app's dependencies install from its own files, in every folder that has a `package.json` (task 1.4: "once the dependencies declared in its package.json files are installed"). Until now an install failure fell between grader-side setup and the scored launch. An install that stops on a dependency conflict npm refuses is re-run with `--legacy-peer-deps` (accommodation A0) so the rest of the card can be graded, and L0 fails all the same. A registry that cannot be reached is the grader's problem, not the app's. Second, API items (I1-I3 for message-board, I1-I5 for kanban), weight 1 each: the page uses the endpoints the spec names (method and path, judged in the Network panel on requests the page itself makes) and, for the kanban move, a body naming `columnId`, `beforeId` and `afterId`. The functional items stay path-agnostic, so an app that works on paths of its own fails only these. Message-board goes from 19 items and weight 29 to 23 and 33. Kanban from 29 and 51 to 35 and 57 (the protocol's section 6.1). The API items are numbered I, not A, because A0-A5 are the accommodations. `grade_setup.sh` must install in every `package.json` folder (section 4.5). **v2.5.20** puts Muse Glimmer 30B into the grid, at the study lead's decision, as tier 6 with two arms. Its pilot (v2.5.19) passed every step: the template served (sha256 `114f55ebdc1804c1`, as every pilot run recorded) reads `reasoning_strength` and renders every past turn's reasoning as a `to=self` message with no flag. The live probe gave UNSEEN -> SEEN +232 characters, both turns' reasoning and nothing else. The marker test came back ACCEPTED, and its six smoke runs, made in 30 minutes, all finished, with no parse void, no retry, no call left as text and no turn without a call, and passed all sixteen gates once its expected body (`reasoning_strength: high` in both arms), replay format (`field`) and preamble (none) were registered in `verify_smokes.py`. The template does not render an assistant turn's prose when the turn makes tool calls, in either arm, so it costs the comparison nothing. Muse wrote no prose beside a call in its pilot. Its file is `Muse-Glimmer-30B-UD-Q4_K_XL.gguf`, 15,878,222,368 bytes, sha256 `82bece304887a313`. The header names no quantizer, so the registry records the publisher as unknown, though the file is unsloth's. The grid becomes 2,640 runs and the smoke 66 (36 message-board, 30 kanban), about 240 hours of machine time with Muse's ~20 projected from its pilot, and 3,168 gradings, about 607 hours. H1 and H3-H5 are tested in eight models, H2 still in six. One thing the pilot shows about smokes in general: the smoke schedule alternates tasks, so a two-arm model's UNSEEN runs are all message-board and its SEEN runs all kanban (true of gpt-oss in every smoke as well) and a smoke's per-arm numbers for such a model cannot be read as arm effects. The grid is balanced. Only comments change in the wrapper, the driver, the decoding registry and the desk renderer. **v2.5.19** wires Meta's Muse Glimmer 30B into the harness for a pilot, at the study lead's decision. It is not in the grid or the certifying smoke, and the protocol does not change unless its own six-run smoke passes the gates every model passed. It runs two arms, like gpt-oss, because its reasoning strength (low to xhigh) has no off level. Its template reads `reasoning_strength`, which every request sends as `high`, the template default and Meta's advice for agentic coding. By Meta's published template, it renders every past turn's `reasoning_content` as its own `to=self` message, with no flag and no last-user-message gate, so SEEN is the field sent or not and the finish nudge cannot shrink it. The served GGUF's template has still to confirm this. Its calls are written in ATEM, a harmony-like envelope that llama-server parses on the pinned b10964 (support since b10353). That parser is new, and parse voids, filed per arm as gpt-oss's are, are the pilot's first question. The file is unsloth's UD-Q4_K_XL (15.9 GB, no plain Q4_K_M is published), keyed like Magistral's, and its sampling is Meta's 1.0 / 0.95 / 64 (section 4.4.1). The patch (`add_muse.py`: all-or-nothing, with `.bak-muse` backups and its own checks) changes the wrapper's model map (`muse-q4xl`), the batch driver's arms, the decoding registry, the desk renderer's arm row, the probe's hint, the harness's list of tool-call markup (ATEM, so a call left in a reply is counted as one), and `verify_smokes.py`'s call markup and G4's openers (`to=self`, Muse's own header). Its expected body, replay format and preamble are registered only after its smoke, so G11-G13 fail it by design until then. Checking the patch found a latent wrapper bug, fixed in the same patch: `decoding_flags()` never stopped a run. Its `2>&1` sat on a line of its own after a heredoc, where bash reads it as a separate command that always succeeds, and its caller did not test the result either, so a model with no registered profile would have run on llama.cpp's own samplers, caught only afterwards by G15. Every roster model's arms resolve to the same bodies and flags as before. The harness commit moves, so the certifying smoke must be made after these changes and the spec changes of v2.5.17 are committed. **v2.5.18** drops the automated checklist, `functional_pct`, at the study lead's decision: app quality is now the hand-graded rubric score alone (section 4.5, the protocol's section 5.3 and section 6.1). The checklist drove the backend's API and event stream, so it could not see what a user meets first (a frontend that does not start, a page that cannot reach its backend, an interface that does not work) and two quality scores for one app would leave open which one counts. Every check it ran has a counterpart among the rubric's items, checked in the browser. `automatic_probes.py` stays in the grader folder, which other studies share, but this study never runs it. Grading is shared, also at the study lead's decision: a 20% overlap, with calibration between the two graders in gradual rounds before any independent grading. A seeded draw gives every app a primary grader, balanced within every model x task x condition x arm cell, and a random fifth of the apps, four of every cell, is graded by both. The primary grader's score is the score of record, and each grader works from one unmarked, shuffled list of blind ids per tier. The agreement bar, proposed here and open for the study lead's review, is that for each task the two graders' scores differ by no more than 5 points on average, in a check of at least 24 apps. An intraclass correlation is reported but is not the bar, because it depends on how much the apps differ from one another. Before the freeze the graders calibrate the cards: training rounds, small at first, on apps built to the earlier specs, then a deciding round on the certifying smoke's 60 apps, every app copied under a fresh random id. In the grid, tier 1's overlap is graded first, and no other app is graded until it meets the bar. Later tiers are checked as each finishes. A task below the bar stops, its ambiguities are settled by rulings in a precedents log, which may only say how a criterion applies, and it resumes after a fresh overlap set passes. The design takes 2,880 gradings, about 550 hours at the draft cards' rough timings (about 275 per grader, plus calibration, any fresh overlap sets and any re-grades). Grading every app twice would take 4,800. The quality bound stays at +/-10 points. The score's spread, first measured in the deciding round, decides its power, computed before the freeze (section 6). Three further changes come with it. `grade_setup.sh` belongs to the grader: it takes a blind id, finds the run itself and records nothing but the id, and it removes the database an app shipped with before installing, so that the launch items measure the same thing in every condition. The grader is therefore committed and tagged at the freeze, after its calibration, rather than with the harness (section 9 items 0, 5 and 6). And the rubric is reported item by item as a descriptive (the protocol's section 6.4). **v2.5.17** changes both task specs, at the study lead's decision, before the smoke is made again. Each gains task 1.4: from a fresh checkout, once the dependencies its package.json files declare are installed, `npm run dev` at the project root starts backend and frontend with no manual step, the backend creates any directory it needs, and the page reaches the backend's API and event stream. The kanban spec also gains task 4.6: creating a card in any column from the interface. Until now the create-card control and the launch requirements were only implied. The draft hand-grading rubric, under review, scores them, and a rubric should grade only what the spec asks for. New lengths and hashes: message-board 5,516 characters, `296815692d88f5cb`. Kanban-board 7,853, `01d2615d510ad8b1`. The spec files are tracked, so the change must be committed before the smoke (section 9 item 0). Every earlier smoke used the old specs, so a set that mixed the two would fail G6. **v2.5.16** sets out how each smoke gate and canary works, at the study lead's request, read from `verify_smokes.py` as it stands (sha256 `3dd092d2ec2f0eae`): what each reads from a run, when it passes and what it guards against (section 9 items 2 and 3b, the protocol's section 5.1 sets out the same). The section 9 table gains the four gates it had left out: G11, G12, G13 and G15. Among what is stated for the first time: G4 looks only for opening markers (`<think>`, `<seed:think>` and `[THINK]`) so it cannot see a split that failed where the template opens the thought itself, as Qwen's does, nor Gemma 4's `<|channel>` or gpt-oss's `<|channel|>`. In the nudge-rule smoke of 2026-09-27 it passed two replies that were a bare channel marker, `<|channel>` in a Gemma-4-26B-A4B OFF step and `<|channel|>commentary` in a gpt-oss UNSEEN step, and what G4 should look for is open. G7 checks that a run's weights resolved in the registry. That the server loaded them is checked by the wrapper before every run, not by a gate. The rule on a silenced OFF arm is a judgement read from the gate report's descriptives, not a computed gate. And `callTxt` counts only steps that made no call, while G2 lists a misfiled call only in an OFF run and only when it would have crossed the 200-character line. Nothing in the design, the harness or the script changes. **v2.5.15** raises the replicates from sixteen to twenty per cell, at the study lead's decision: 120 runs per arm per model, 360 for a three-arm model and 240 for gpt-oss, 2,400 grid runs where there were 1,920, and 2,460 with the smokes (section 4.2). At the pace of the nudge-rule smoke of 2026-09-27 (60 runs in 5 h 29 min, server start and stop included, the grid is that set 40 times over, arm for arm and condition for condition), the grid takes about 220 hours of machine time, some nine days of continuous running (section 4.2, section 6). The set is used here for its timing alone, and its gates are still to be set out. section 6 is recomputed by the method that reproduces its sixteen-replicate figures exactly: a 2% failure rate against 15% is now detected 96% of the time where it was 90%, 2% against 10% 68% of the time where it was 56%, the equivalence statement at a 5% failure rate is declared 91% of the time where it was 80%, and two arms with no failures bound the difference at +/-2.2 points where they bounded it at +/-2.7. Nothing else in the design changes, the harness included: the batch driver takes the replicate count from `REPLICATES`, so every grid command in section 4.6 now carries `REPLICATES=20`, and a smoke is one run per arm per condition whatever the count, so no smoke is made again for this change. **v2.5.14** sets out the certifying smoke at 20M (2026-09-26/27, 60 runs from `543d0e2`): 49 of 60 finished against 43 in the 12M set, and every gate passed but two, G2, Gemma-4-26B-A4B writing thinking prose in an OFF run, and G9, the GLM slot that exhausted 12M exhausting 20M in a counting loop. The study lead waives both: Gemma-4-26B-A4B keeps its OFF arm, watched, and a run that reaches the budget while looping is an outcome (section 4.1, section 9). It corrects the replay claim: a re-run replays its predecessor only until a tool result differs, and command output carries times and process ids, so only `no_verification` runs replay exactly, all nine the file-state note reached got it at exactly the step predicted (section 10, fifth). And it changes one registered rule: the finish nudge is given after every turn without a tool call, and a run ends as `stopped_no_tool_call` only when the reply to a nudge has none either (section 10, sixth), a harness change, so one more certifying smoke (section 4.6). **v2.5.13** adds a note to the file tools, at the study lead's request, before the certifying smoke: when a `write_file` or `edit_file` call leaves a file with exactly the bytes an earlier write or edit call of the run left it with, the result says how many such calls there have now been and how many calls ago the previous one was (section 4.4). It is the same text in every arm and condition, a fact about the model's own calls, and it ends nothing. Each manifest counts the calls that got it, reported per model x arm as a descriptive (section 10, tenth). Replayed through the note, the recorded calls of the 93 September smoke runs get it 208 times in 38 runs, 24 of which finished (it reaches healthy runs) and 23 of the 60 runs of the all-model smoke, whose paths and seeds the certifying smoke reuses, get it by step 54, so they can replay their predecessors only up to there (section 4.1). The batch driver is now `run_thinking_batch.sh` (it was `run_quantization_batch.sh`, every mention in this plan uses the new name), and the freeze commit must now take in the harness change and `decoding-registry.json` (section 9 item 0). **v2.5.12** takes the decisions v2.5.11 left open, on the gpt-oss probe it proposed: 24 runs, both arms, gpt-oss's four `execution` and `interactive` cells, replicates 02-04. The probe voided 8 of 24 runs on output the server could not parse, 4 of 12 in each arm: one in three, G14's ceiling. **The sentence stays, and no model leaves.** **G2 is waived and watched:** the one Gemma-4-26B-A4B OFF runaway is recorded as such, and reasoning in OFF steps is counted per model in the grid. **The token budget rises to 20M** for every model, the study lead's answer to G9. **The blind layout's seed is fixed:** the wrapper takes the replicate from the schedule label and refuses a blind run whose label has none. The probe also shows a shape registered now, before any grid run: gpt-oss's malformed outputs in SEEN were closing summaries, and SEEN stopped without a tool call more often (section 10, third). Because every manifest records its budget and G10 insists on one value across a set, a 12M smoke cannot certify a 20M grid, so **the certifying smoke is made again**, from the same paths and seeds: each run should replay its predecessor except where the new budget reaches. **v2.5.11** sets out the smoke of all seven grid models made under the reinstated sentence (2026-09-25/26, 60 runs) against the criteria section 4.1 registered for it: three gates fail, G2, a Gemma-4-26B-A4B OFF run ending on a runaway reply filed as reasoning. G6, two GLM runs started two minutes before the harness was committed, their code proven identical. G9, a GLM run that exhausted the budget: finished runs fall from 53 to 43 of 60, and six of the seven models are flagged. But `no_verification`, where the sentence has nothing to act on, lost runs at the same rate as the conditions where it acts, so most of the fall is the re-roll that any change to the prompt causes. The sentence's own effects are gpt-oss's two voids, GLM's longer and loopier runs, and more runs checking their work. The arms cannot be compared on a smoke, whose layout gives each arm different cells. The decision is open. The set also showed that **a smoke retry is an exact replay** (gpt-oss's six runs repeat its re-smoke response for response, and each retry repeats its first attempt) so `verify_smokes.py` now marks replays and counts distinct failures (section 10, fifth), and that **the blind layout, as the wrapper stands, sends no per-request seed at all** (section 4.4), to be fixed before the grid. **v2.5.10** reinstates the v2.5.6 briefing sentence, at the study lead's second reading of the same re-smoke: under it both models began running commands, which is what it was added for, and gpt-oss's two parse-failure voids fell one in each arm, so they cost runs without tilting the contrast, and they came in the two runs where gpt-oss did the work its `execution` and `interactive` conditions exist to measure. Magistral stays out on its own record (section 5.1). Both texts are now named constants in `conditions.py`, and which one is registered is a single line. The sentence stands or falls on a smoke of all seven grid models made under it, read against each model's latest smoke under the original text, on criteria registered in section 4.1 before any of it runs. If it stays, that set is the certifying smoke. The runbook gives the set its own state directory, because the batch driver keys its state on the mode and the model list alone and would otherwise resume one set of the seven as another. The section 4.4 briefing row, which v2.5.9 left at the v2.5.6 hash, now records the history. It moves `harness_git`. **v2.5.9** takes three decisions on the re-smoke of gpt-oss and Magistral, the first runs made under the v2.5.6 briefing (2026-09-25, 15 runs). **Magistral leaves the grid.** It ran commands in 3 of its 6 `execution` and `interactive` runs, where it had run none, but finished 3 of 9 runs against 5 of 9 before (every OFF run stopping at step 2 in prose, two SEEN runs writing their calls as text) so its review closes with its removal (section 5) and its record moves to section 5.1. The grid is **1,980 runs and ~129 h, from seven models and five labs**, three dense and four mixture-of-experts, six of the seven on all three rungs. **The v2.5.6 briefing sentence is withdrawn.** gpt-oss did run commands under it, in 2 of its 4 `execution` and `interactive` runs, and those were the two runs it lost, each failing all three attempts on output its server could not parse (6 of the 8 attempts at those four runs) where under the original briefing its sampled runs had never produced such a failure. The universal briefing is the original text again (`02f244a9339a0cb6`) and the v2.5.6 text is kept, unused, for provenance. Section 4.1 also records why every model keeps one briefing rather than its vendor's own system prompt: none of the seven vendors publishes one, and what a model's prompt must contain its own template already puts there. **Every failed attempt is now kept.** The batch driver moves a failed smoke attempt to `<condition>/failed-attempts/` before re-running the slot, instead of overwriting it, and `verify_smokes.py` counts every attempt per model x arm and by cause, printing what the model wrote whenever its server could not parse it: so whether such failures fall on one arm more than the other can be read, over attempts rather than slots (section 10, fifth). The harness's message for that failure no longer cites greedy decoding, which ended in v2.4.0. All of it moves `harness_git`, so the certifying re-smoke (now seven models, 60 runs) comes after it. **v2.5.8** closes the first freeze item of section 9 item 0: **every retried model call is now recorded.** A read timeout does not fail a call (the client re-sends it and generation restarts from zero) so a runaway reply timed out and re-rolled into a short one used to read as a clean run. The harness now writes `api_retries` into every manifest (how many calls were retried, how many of them timed out, and for each retry the call, the reason (`timeout`, `connection`, `http_<code>`, `server_crash`) and how long the failed attempt ran) always present, so "no retries" is distinguishable from "not recorded". `verify_smokes.py` gains **G16**, which fails any set containing a timeout retry, and any run made before the record existed unless `--no-retry-record` is passed. Other retries are listed, not failed. A new offline test, `test_retry_record.py`, pins it end to end, through the harness's own entry point against a scripted local server. It changes `harness_git`, so the certifying re-smoke comes after it, as planned. **v2.5.7** restores **gpt-oss-20b** to the grid, at the study lead's correction: the model meant for removal in v2.5.6 was Magistral, not gpt-oss. The plan's roster, grid and tiers return to v2.5.5's (eight models from six labs, 2,277 runs) and v2.5.6's briefing sentence stays (section 4.1), so the certifying re-smoke is the first reading of both models under it: whether gpt-oss, told it has a live environment, runs anything, and whether Magistral does. **Magistral is put under review** instead of removed: its removal is proposed, it stays in the batch driver and the re-smoke, and the decision is taken on that re-smoke, read on the three things that raised it, how many of its runs finish, how many of its turns write a call as text, and whether its `execution` and `interactive` runs run anything (section 5). Without it the grid would be 1,980 runs and ~129 h from five labs. **v2.5.6** makes two changes, both before the certifying re-smoke. **The universal briefing gains one sentence** ("If execution tools are provided, they give you a live development environment: the commands you run through them execute for real in your workspace, on a machine with Node.js and npm installed and the npm registry reachable, so the packages you install and the servers you start are real.") because the 12M smoke set caught gpt-oss reasoning that it had no environment to run in while shell tools were listed for it, and Magistral reasoning that its task was only to create files. It is the remedy the harness's own rules name for a tool nobody notices: descriptive, conditional so that it reads truthfully under every tool set, naming no tool, and asking no one to use anything (section 4.1). The briefing's sha moves from `02f244a9339a0cb6` to `c988f43155c49538`. **And gpt-oss-20b leaves the grid**, at the study lead's decision, on its smoke behaviour: it finished every run and ran no command in any of them, and with no off-switch it carried only two arms. The roster is now seven models from five labs, four dense and three mixture-of-experts, every one on the full three-arm ladder: 2,079 runs, ~137 h by the table and about 152 h at the latest smokes' pace (section 4.2, section 6). Its record moves to section 5.1, with what its removal costs: OpenAI's lab, the only two-arm model, and the "grew up SEEN" test case. **v2.5.5** puts the two mixture-of-experts twins, **Qwen3.6-35B-A3B** and **Gemma-4-26B-A4B-it**, into the grid as its fifth tier: eight models from six labs, four dense and four mixture-of-experts, 2,277 runs and ~139 h by the table's own measurements, about 154 h at the latest smokes' pace, because Seed-OSS's runs have lengthened under vendor sampling (section 4.2, section 6). The within-pair comparison is registered now, before any grid run, as exploratory (intervals, no tests, the pairs' confounds printed beside every number (section 10)) and the Qwen slot is fixed at Qwen3.6-27B, since a pair must share its generation. **G2 is refined**: a reasoning field whose whole text is a tool call is a call filed in the wrong field, not thinking, so it is set aside, listed and counted. `verify_smokes.py` implements it, and each of the eight models' latest smoke sets now passes all fifteen gates, the Gemma twin's included. A new descriptive, `callTxt`, counts the steps whose call was written as text instead of made, and another reports whether each run checked its own work: the 12M smoke set found Magistral and gpt-oss running no command at all in any of their `execution` and `interactive` runs, one of the two profiles once cited against Nemotron (section 10). A new section, section 5.1, records every model considered and not chosen and why (the four that reached the harness, the nine weighed in full at the desk, and the rest of the 2026-09-25 search by the requirement each failed) and corrects this plan's DeepSeek entry: the pinned engine does carry its architecture, and size alone rules it out. Granite leaves the batch driver, where it had stayed after its retirement. A third freeze item opens: replay one of the Qwen twin's lost-call requests raw before the tag (section 9). **v2.5.4** records steps 4 and 5 for both mixture-of-experts twins and registers them. Every prompt the live probe rendered for a twin is byte-identical to its dense sibling's, so inside each pair the treatment is the same bytes (+144 and +202 chars). `qwen-moe-q4` and `gemma-moe-q4` are now in `verify_smokes.py`'s three `EXPECTED_*` tables, and on their 18-run smoke 14 of the 15 gates pass. **G2 fails on one step that is not thinking**: one of Gemma-4-26B-A4B's 129 OFF steps carries 1,288 characters in the reasoning field, and they are a `finish` call's arguments followed by the tool's name, a call the model made properly on the next step. Read literally, section 9 item 2 would drop the twin to two arms. Whether the step is waived or the canary refined is open (section 5). Qwen3.6-35B-A3B finished 7 of 9 runs and Gemma-4-26B-A4B 8 of 9, every failure in UNSEEN, and both checked their own work in all six runs that offered the tools. Three of the Qwen twin's UNSEEN turns lost their tool call: the reasoning field ends in a call's closing tags, with no opening tag and no `</think>`. The Gemma twin's one failure was a repetition loop that filled the 65,536-token window it had inherited from the 31B. Under section 4.3's rule, which sets each model's window by its own smokes, **its window is raised to 131,072** and its nine smokes are to be re-made. In the grid the twins would take about 24 h and 25 h, bringing it to ~139 h and 2,277 runs. Whether they enter it is not yet decided. **v2.5.3** records steps 1-3 for both mixture-of-experts twins, now on the machine. Both files hash to the sha256 Hugging Face publishes for unsloth's current builds (`ac0e2c1189e055fa...` for Qwen3.6-35B-A3B, `f2c28b3dc4776931...` for Gemma-4-26B-A4B-it). The templates baked into them are **byte-identical to their dense siblings'** (`55d4931433fe502b` for the Qwen pair and, as served, `aa3185dfc6505104` for the Gemma pair) so the pairs share their templates exactly, not approximately, and the desk render reproduces the siblings' deltas (+144 and +202 chars). The one check v2.5.2 set for Gemma's file was framed partly wrong: no GGUF template here carries Google's `Published:` header line, the 31B's included. What decides the question is that the file reads `preserve_thinking` in its history gate, which it does. LM Studio saved both files under `-UD` folders, and the wrapper's paths follow them. The live probe and the smoke remain. **v2.5.2** wires two mixture-of-experts **twins** of roster models for their smokes: **Qwen3.6-35B-A3B** (`qwen-moe-q4`), twin of Qwen3.6-27B, and **Gemma-4-26B-A4B-it** (`gemma-moe-q4`), twin of Gemma-4-31B. Each takes its dense sibling's switch, request bodies, context window and sampling by construction (the same `THINK_KIND`, and decoding entries whose values each vendor's card gives for the twin as well) so that inside a pair the vendor, template and settings are shared and the architecture is what differs. It is not all that differs: the twins have a tenth of their siblings' active parameters and run unsloth's `UD-Q4_K_M` against the siblings' plain `Q4_K_M`, and section 5 says so. If both pass, the roster becomes four dense and four mixture-of-experts models from six labs, with two within-lab pairs. How a pair is reported is to be registered before the freeze (section 10). `hash_quants.py` gains `--key`, which files a registry entry under a key such as `UD-Q4_K_M` while `gguf_file_type` keeps what the header says. None of the five protocol steps is done. The files are not yet on the machine. **v2.5.1** retires **Nemotron-3-Nano-30B-A3B** from the study, taking v2.5.0's recommendation: it leaves the batch driver and the standby slot, and the slot is open. Like EXAONE and Granite it stays in the wrapper's model map, unregistered, and in section 5 as a worked near-miss, so every probe, smoke and diagnostic run behind the decision can be re-made. Its section 5 record now links a source for each claim it rests on: NVIDIA's technical report, model card and reproduction guide. The Terminal-Bench and OpenDevin sources for the three JSON formats it fell into with thinking off. NVIDIA's Prime Intellect tutorial, in which the model, thinking off, "exhausted five turns calling unsupported tools". A user report that it calls OpenHands' `str_replace_editor` in agents that have no such tool, and the NVIDIA reply calling its coding failures "a model limitation". The roster is unchanged: four dense models and two mixture-of-experts ones, gpt-oss and GLM. **v2.5.0** puts **GLM-4.7-Flash** (Zhipu) into the roster as its **sixth model**, with three arms, in the grid rather than on the bench. It passed all five steps of the standby protocol on 2026-09-25: the file hashes to the re-upload Hugging Face publishes (`29837ed2c0fc5f51...`), its template (`d63ad536c3c81880`) is the one every GLM run records, and a nudged desk render and the live probe agree at **+158 chars** from UNSEEN to SEEN. Registered in `verify_smokes.py`'s three `EXPECTED_*` tables by this version, its nine-run smoke passes all fifteen gates. That is a pass, not a clean bill: six of nine runs finished, the other three were loops the `no_progress` guard stopped (two OFF, one SEEN), and it checked its own work in both of its finished `interactive` runs but not in its one finished `execution` run (section 5). The grid grows by 297 runs to **1,683** and by about 15 hours to **~90 h**, as a fourth tier (section 4.2, section 6). Every contrast is still climbed inside one model, so a sixth ladder is a sixth replication and changes no test. The marker test now sends the wrapper's own thinking-arm body (`probe_reasoning_replay.py --model-key`): it used to send none, and because its last message is a user message, every template that clears history by default would have reported a false IGNORED. **Nemotron** passed its live probe (+150 chars) and was smoked, and is not registered. With thinking OFF it answered step 1 with a JSON agent protocol of its own instead of a tool call in 11 of 15 runs: envelopes that mostly match Terminal-Bench's Terminus agents, and NVIDIA's technical report says its terminal training trajectories were generated with Terminus-1 and Terminus-2. With thinking on, none of its finished runs ever ran what it had built. A review of NVIDIA's documentation found nothing this harness leaves out for the thinking arms. The one documented setting the study declines is greedy decoding for reasoning-off (section 4.4.1). section 5 records it all and recommends that Nemotron is not fieldable. Whether that leaves the standby slot open is not yet decided. **v2.4.5** wires **GLM-4.7-Flash** (Zhipu) as the second-line standby behind Nemotron (`glm-q4`, three arms, its own `THINK_KIND`) as the like-for-like substitute if Nemotron fails on template or parser grounds. It shares Nemotron's ~3B-active profile, so it is the wrong fallback if Nemotron fails on competence. Meta's Muse Glimmer 30B (dense, two arms, not wired) is the hedge for that case. Its keep-history flag is a third name, `clear_thinking`, with Granite's polarity, read from Z.ai's published template: a plain `or`, so `false` keeps every past turn's reasoning. None of its five protocol steps is done, because the file is not yet on the machine. Its sampling is Z.ai's agentic-coding evaluation profile, 0.7 / 1.0, in both modes (section 4.4.1), and only GGUFs re-uploaded on or after 2026-01-21 are usable: the launch files looped from a llama.cpp bug. **v2.4.4** retires Granite from the standby slot and proposes **Nemotron-3-Nano-30B-A3B** (NVIDIA) for it. Granite's SEEN arm is 0 of 3 under two decoders, and had it been brought up it would have taken 48.7% of the smoke set's model-generation time, 2.25x the next model. A diagnostic run at a 98,304-token per-reply cap could not test v2.4.3's prediction as designed: at that cap a runaway reply outlasts the 3,600 s client timeout, and a timed-out call is retried rather than failed, so the harness silently re-rolls it, the cap stays at 32,768 and the coupling is written into section 4.4. Nemotron uses Granite's switch names and polarity, now read out of the served template rather than a card: steps 1-3 of the standby protocol are done (hashed, template sha256 `b3043677cd5fc67f`, a nudged desk render adding +150 chars from UNSEEN to SEEN), the live probe and the smoke are not. Its sampling is the card's tool-calling profile in both modes, a registered deviation for OFF (section 4.4.1). The roster is now deliberately mixed dense/mixture-of-experts, as read from each GGUF header: gpt-oss was already MoE, which makes the note that Granite's being dense "matches the roster" wrong, and it is corrected in place (section 5). Architecture is described, never tested (section 10). Two freeze items open in section 9 item 0: retries are not recorded in the manifest, and the harness now prints a heartbeat while a reply is outstanding and a line per applied tool call, print-only, but they change `harness_git`, so the smoke set must be regenerated. `template_probe.py` now also checks that past tool-call arguments reach the prompt. **v2.4.3** identifies what actually kills Granite's SEEN arm and adds the terminal status that names it. Those runs were not cut off: they spent the entire 32,768-token per-reply allowance on reasoning and emitted nothing (88,845 characters, 3,531 lines, 360 unique, "Let me do it." 768 times) a degenerate repetition loop inside a single generation, which no loop guard can see because all three count tool calls ACROSS steps and this pathology emits none. `runaway_no_tool_call` now separates it from a genuine truncation (`completion_tokens == max_tokens` versus far below it), and `truncation_detected` carries a repetition measure so a loop is distinguishable from a legitimately huge reply. Consequence for v2.4.2: the budget raise cannot help this arm, which dies on the per-reply cap, not the per-run one. **v2.4.2** raises `MAX_TOTAL_TOKENS` from 8,000,000 to **12,000,000**. Under vendor sampling Granite reaches the 8M ceiling in three of nine smoke runs. The raise is safe for the rest and measurably so: across the 51-run set the heaviest non-Granite run used 2,719,615 tokens, 34% of the old cap, and the median used 148,789, so no other model came within 2.5x of it. A set spanning the change fails G10, which is the gate reporting a mixed configuration rather than a false alarm. The smoke set that certifies the grid must be made entirely at 12M. **v2.4.1** records what section 4.4.1's registered prediction returned on the 51-run sampled smoke of 2026-09-23: **not confirmed**. Granite's SEEN arm fails identically under both decoders, the other pathologies moved rather than fell, gpt-oss improved clearly, and Granite gained a new budget failure. The decoding change stands on construct validity, not on the pathology argument, and the write-up says so. Granite is now registered in all three `EXPECTED_*` tables so its gates are informative rather than merely red. 14 of 15 gates pass, G9 the only failure. **v2.4.0** replaces frozen greedy decoding with **per-model, vendor-recommended sampling** (section 4.4.1). Temperature 0 / top_k 1 was chosen to minimise nuisance variance. It also put five reasoning-tuned models at an operating point none of their makers documents, produced a smoke-set pathology profile that reads as the greedy failure profile (`stuck_looping`, `truncated_no_tool_call`, empty turns: losses that censor runs rather than add variance, because a model that enters a repetition loop at temperature 0 has no mechanism to leave it), and left sixteen replicates unable to differ except through uncontrolled numerical noise. Every contrast in this study is climbed **inside** one model, so decoding varying between models is not a confound. Settings follow each vendor's documentation, per thinking mode. Only Qwen documents a mode split, so this changes exactly one cell's samplers in the grid, and the resulting caveat is confined to Qwen's generation contrast. Seed becomes a real per-replicate variable. **v2.3.16** records the Granite smoke (9 runs) and the harness bug it exposed. `write_file` crashed the whole run with `FileExistsError` whenever a model wrote a FILE and then tried to write inside it as a directory (`mkdir(exist_ok=True)` forgives an existing directory and nothing else) killing 1 SEEN and 1 UNSEEN run of 9. Attrition caused by what the model chose to do lands unevenly across the ladder and biases the contrast rather than merely shrinking it, so the tool now returns a recoverable error into the transcript instead. **This changes `harness_git`, so the smoke set must be regenerated before the grid.** The smoke also shows Granite's ladder misbehaving at both ends: OFF ran 304 steps and exhausted the 8M budget in 2 of 3 runs (G9's only real failure), while SEEN collapsed to 20 steps with 2 empty turns and 2 `truncated_no_tool_call`. Verified as a treatment, unproven as a usable model. **v2.3.15** passes Granite on the live server: SEEN carries both turns' reasoning, UNSEEN carries none, the prose survives, and the nudged SEEN case keeps everything, so `truncate_history_thinking: false` works end to end and the `arguments`-as-a-mapping risk is closed, because llama.cpp parses the JSON string into an object before rendering. The UNSEEN->SEEN delta is **+150 chars on both the offline render and the server**, two independent Jinja implementations agreeing on the size of the treatment. The same version records the Smart App Control incident and adds the engine preflight that would have caught it in one line. **v2.3.14** records Granite's desk check against the GGUF now on the machine: the template reads `reasoning_content` as a field, gates history on `not (truncate_history_thinking and loop.index0 < ns.last_user_idx)` (a plain AND, so `false` defeats it unconditionally) and carries no `loop.last` trap. Rendered with a finish nudge, `false` keeps both turns' reasoning and the default `true` loses both, mirroring Gemma exactly. One risk survives to the live probe: the template wants `tool_call.arguments` as a mapping and the OpenAI wire format sends a string. **v2.3.13** replaces the standby: **Granite 4.2-30B** takes the slot (`granite-q4`/`granite-q8` in the wrapper under a new `enable_thinking_granite` kind, three arms in the batch driver) because its card documents `truncate_history_thinking: false`, a keep-the-history flag of the opposite polarity to `preserve_thinking`, which is exactly the capability EXAONE's template appears to lack. It is Apache 2.0, ungated, dense 30B at 128K, and was quantised at llama.cpp b10603, older than our b10964 pin. EXAONE stays in section 5 as a worked near-miss rather than a bench player. The same change fixes a drift this study had been running with: `template_probe.sh` now derives each arm's body from the wrapper's own `think_body()` instead of a hand-kept copy that had been omitting `preserve_thinking` for Gemma and Qwen. **v2.3.12** corrects the EXAONE source (there is no unsloth build of it, so the file comes from LG's own (licence-gated) repo or a community mirror) and records what its *published* chat template says: `skip_think` defaults to **true** and the reasoning branch is additionally gated on `loop.last`, so with the body EXAONE currently inherits its SEEN arm would render no past reasoning at all. The standby is therefore not a drop-in, and section 5 now says so before anyone reaches for it on the day. **v2.3.11** adds EXAONE-4.0-32B to the harness as the roster's standby (`exaone-q4`/`exaone-q8` in the wrapper, three arms in the batch driver) deliberately unregistered in `verify_smokes.py` so its gates fail until it is verified, and records in section 5 what is known about it, what is not, and that its card's recommended sampling conflicts with the study's frozen greedy decoding. **v2.3.10** adds both registered preambles verbatim to section 4.2.2 with their hashes and the per-arm table, so the plan states the exact text sent rather than naming a key. **v2.3.9** confirms the switch on a full re-smoke across all three conditions: Magistral's SEEN arm goes from 10 steps and 1/3 finishing to 20 steps and 3/3, its thinking arms now carry zero no-tool turns in 41 steps, and its OFF arm is byte-identical as it must be. All thirteen gates pass on the merged 42-run set. **v2.3.8** switches Magistral's preamble to `mistral-min` on 10 runs per variant (100% of steps reasoning against 91%, no step-1 narration against 4 runs in 10, 10/10 finishing against 9/10) reversing a choice originally made on one run each, and corrects the 15% no-tool-call figure to ~3% over 187 steps. Gate G13 now pins the preamble per model. **v2.3.7** records the clean 42-run smoke set of 2026-09-22: all twelve gates pass, and two operating facts go on the record, Magistral fails to call a tool on 15% of its steps against 1-3% for every other model, and gpt-oss produced one HTTP 500 from llama.cpp's harmony parser, which is a void under section 10. **v2.3.6** records the post-fix probe: all five models pass, Magistral additively at +174 chars, gpt-oss with its prose-for-reasoning substitution registered as a known asymmetry. The gate's content check now tests named strings rather than diffing lines, which had produced three false alarms. **v2.3.5** records what the live `/apply-template` probe found: gpt-oss's contrast is real, but Magistral's SEEN arm was showing the model *less* than UNSEEN (llama.cpp deletes the assistant's prose when a reasoning field it cannot render is sent) so Magistral now replays inline as `[THINK]...[/THINK]` via the new `--replay-format`, and the probe's verdict now requires the reasoning present, absent from UNSEEN, and nothing lost. **v2.3.4** adds `SERVER_VERBOSITY`, an opt-in diagnostic that raises llama-server's `-lv` for a single run, and records in section 4.3 why it stays outside the frozen serving flags. **v2.3.3** rewrites section 4.2.2 around the three layers the switch travels through (the `chat_template_kwargs` extension in the request body, llama-server's merge of it into the Jinja render context, and what each template's own code does with the variables it defines) with one part per model quoting the Jinja that decides it. **v2.3.2** adds `preserve_thinking` to Gemma's and Qwen's bodies in every arm, after finding that the harness's finish nudge moves the templates' last-user-message window and silently truncates SEEN's visible reasoning (it had fired in 5 of 15 SEEN smoke runs) and registers a zero-nudge sensitivity analysis in section 10. Every expectation in
this document is stated from first principles and public documentation. No
study data exist at the time of writing, and every run of the study is made
from scratch under this plan. Standalone: this plan replaces earlier
drafts and carries everything it needs.

---

## 1. The question

When an AI coding agent works on a task, it does something like thinking out
loud before each action: it writes a private scratchpad ("the tests are failing
because the import is wrong... let me check the config first"), and then it
acts: opens a file, runs a command, makes an edit.

Here is the thing almost nobody decides on purpose: **on the next step, does
the AI get to re-read its own earlier scratchpads, or are they thrown away?**

Think of it as two ways of working at a desk. In one, every sticky note you
ever wrote stays on the desk in front of you. In the other, someone quietly
bins each note the moment you finish writing it: you still *did* the
thinking, you just never see it again.

Both setups exist in the real world, and the industry disagrees about which
is right. Anthropic and DeepSeek **require** the notes to be kept when tools
are being used. OpenAI **hides** the notes on its servers so you couldn't
re-show them if you wanted to. And most home-built setups running open models
quietly bin the notes without anyone choosing.

**The hypothesis this study tests:** *an agent behaves differently when it
can see its own past thinking than when it never sees it again.* Maybe it
doesn't, maybe having the thought is what matters, and remembering it adds
nothing. Either answer, measured properly, is worth knowing: one says the
notes matter. The other says every provider forcing you to keep (and pay
for) them is charging you for nothing.

To make "having the thought" a measured thing rather than an assumption, the
study also runs the agent with **no thinking at all**. That gives a ladder
of three setups (no notes, notes written but binned, notes kept) and two
questions, asked in order: does *writing* the notes change behavior, and
does *keeping* them change it further? The second is the primary question.
The first is the registered secondary.

---

## 2. What could differ, and why: expectations from first principles

Nothing here is measured yet. These are the mechanisms that make the
question worth asking, and they are the reason the study measures several
things rather than one:

- **Memory.** The notes are the agent's only record of its own plan. Without
  them it may have to re-derive decisions, take more steps, or contradict
  itself: *or* it may do better, because a long trail of old thoughts is
  also a distraction: the more a model writes, the more of its own past it
  has to wade through on every step. Direction unknown. That is the point.
- **Cost.** Keeping the notes is mechanically expensive: every past
  scratchpad is re-sent on every step, so the context grows faster, each
  step costs more, and the context window fills sooner. This much is
  arithmetic. What it buys is the question.
- **Formatting stability.** Several recent models were *trained* with their
  thoughts present in the conversation history (OpenAI's format for its open
  models carries reasoning between tool calls, MiniMax's and DeepSeek's APIs
  mandate it). A model shown a history with its thoughts stripped is being
  shown a shape it may never have seen in training, and it could stumble: 
for example by misplacing where its "thinking" ends and its "action"
  begins. Others were trained the opposite way (the standard Qwen template
  strips old thoughts). So the effect may depend on each model's upbringing.
- **Reliability.** Agents sometimes get stuck repeating a failed action. a
  scratchpad that persists is one plausible way to notice "I already tried
  this": or, equally plausibly, the thought of trying is what matters and
  the memory of it adds nothing.

Providers have picked sides on this without publishing controlled
comparisons. This study is the controlled comparison.

---

## 3. The experiment

Three setups, identical in every way except two switches:

| | **OFF** | **UNSEEN** | **SEEN** |
|---|---|---|---|
| The model thinks before each action | **no** | yes | yes |
| Its past thinking stays in front of it | (nothing to keep) | **no: binned after each step** | **yes** |

Two contrasts come out of this, and they are kept apart on purpose:
**OFF -> UNSEEN** measures what *generating* a scratchpad does. **UNSEEN ->
SEEN** measures what *re-reading* it does. The second is the study's primary
question. The first is the registered secondary. The OFF arm exists only for
models with a genuine off-switch (section 5): a model that cannot stop thinking
simply has no OFF arm, and its ladder has two rungs.

One "run" = the agent is asked to build a small web app (a message board, or
a kanban board: tasks with a known booby-trap: a package name whose exact
capitalization matters) and works alone until it finishes, gets stuck, or
dies. We run each model many times in every setup and compare.

**Fairness rules** (the boring part that makes it science):

- Same machine, same server software (llama.cpp build b10964, pinned), same
  settings, same instructions, same guard rails, for every run. Only the
  two switches (thinking on/off, thoughts kept/binned) differ.
- Runs rotate OFF, UNSEEN, SEEN, OFF, ... so time-of-day, disk state, or a
  warming GPU can't favor one arm.
- Every model file is fingerprinted (sha256) and the server is asked, every
  boot, to confirm it is actually serving that exact file.
- **The marker test:** before a model enters the study, we plant a nonsense
  phrase in its thinking and check the round trip, with the switch ON the
  model can repeat the phrase later (proof it truly sees past thinking), and
  with the switch OFF it cannot (proof the binning is real). A model that
  fails either direction is out. Without this, UNSEEN and SEEN could silently
  be the same setup.
- The schedule and the analysis plan are frozen (hashed, optionally
  timestamped publicly on OSF) **before** the first real run. No peeking, no
  changing the rules mid-game.

**What we count**: four things, per run:

1. **Did it fail in a "wheels came off" way?** The harness has fixed,
   mechanical endings for a run that does not finish: stuck in a repeat
   loop. Replying with words but no action. Running out of context window.
   Running out of token budget. Each is counted and reported separately.
   Together they are the reliability measure.
2. **How long did it wander?** Steps taken to finish.
3. **Is the app any good?** Two people grade the apps by hand, blind to the
   arm, working through each app's own interface with a fixed scoring card
   for its task. The card asks whether the app starts the way the spec says,
   whether the page reaches its backend, whether each feature works, whether
   other windows update, and whether the data survive a crash. *v2.5.46:* a
   seeded half of every cell, the quality sample, is graded, finished or not.
   One grader grades them, and a random fifth of them again, blind, at least
   14 days later, to check that the cards are
   applied the same way twice. The cards are frozen before any grid app is
   graded, after the grader has calibrated them on apps from outside the
   grid.
4. **What did it cost?** Tokens spent: the electricity-and-time bill.

A difference on any of these, in either direction, is a finding: for
either contrast. If *none* of them budge between UNSEEN and SEEN, we don't
shrug: we report the strongest statement the data supports: "keeping
thoughts visible changes nothing by more than X%," with X computed, plus the
measured price of keeping them anyway. And because the OFF arm sits beside
them, that statement comes with its own proof of sensitivity: if turning
thinking off *does* move the needle while keeping thoughts visible does not,
the lab has demonstrably measured a reasoning-configuration effect, the
null on visibility is a finding, not blindness.

---

## 4. What exactly gets run: conditions, run counts, and the frozen settings

This section is the operational spec: everything a run inherits that is
*not* the visibility switch. All of it is identical across SEEN and UNSEEN,
and all of it is written into each run's `manifest.json` so drift is
detectable mechanically rather than by memory.

### 4.1 The three task conditions

The harness gives the agent a *verification surface* (the set of tools it
may use to check its own work) and that surface comes in named
"conditions" (a ladder from "can't run anything" up to "can run and see
everything"). This study uses three rungs of that ladder: two because they
are the realistic ways a coding agent is deployed, and one because it is the
sharpest possible test of the hypothesis:

| condition | what the agent can do | in plain words |
|---|---|---|
| **no_verification** | nothing executes and nothing is observed: it reads the spec, writes the files, and declares itself finished (dependencies are installed by the harness afterwards, for grading) | a developer told to write the whole app on paper and hand it in: no compiler, no browser, no second look |
| **execution** | full shell: install packages, build, start servers, run tests, read the text output | a developer with a terminal but no browser: it can run the app, not click it |
| **interactive** | everything in execution **plus** a persistent headless browser it can drive: open a URL, click, type, drag, wait, and read the page's structure (elements with selectors, page text) and console errors, text only, no pixels. Can hold several pages/tabs at once | the same developer with a browser too: it can add a card, type a message, and see whether the page actually reacted |

`interactive` is exactly `execution` plus "hands". `no_verification` is
`execution` minus the terminal. Under the briefing mode we use (`universal`),
the written instructions are byte-identical in every condition: the *only*
difference is which tool schemas appear in the request. *v2.5.6:* that text gains one
sentence, the same in every condition: "If execution tools are provided, they give you a live development environment: the commands you run through them execute for real in your workspace, on a machine with Node.js and npm installed and the npm registry reachable, so the packages you install and the servers you start are real." The 12M smoke set caught gpt-oss reasoning
that it had no environment to run in while shell tools were listed for it, and Magistral
reasoning that its task was only to create files (section 10). The sentence is the remedy the
harness's own rules name for a tool nobody notices (a tool-neutral strengthening of the
briefing) and it keeps to those rules: it describes what execution tools act on and never
asks anyone to use them, it is conditional, so it reads truthfully under every tool set and
is inert in `no_verification`, and it names no tool. A model that still declines to run its
app can no longer be said to have been misinformed about its environment. The briefing's sha
moves from `02f244a9339a0cb6` to `c988f43155c49538`. The base prompt's stays
`a1b949af9e7bda1c`, and every smoke made before it has to be made again. *v2.5.9:
withdrawn.* On the re-smoke made under it, both models did start running commands (gpt-oss
in 2 of its 4 `execution` and `interactive` runs, Magistral in 3 of its 6) but gpt-oss's two
command-running runs were the two it lost, each failing all three attempts on output its
server could not parse (section 10, fifth), and Magistral finished 3 of its 9 runs and left the grid
(section 5.1). The study lead withdrew the sentence. The briefing is the original text again, sha
`02f244a9339a0cb6`, the hash every smoke before v2.5.6 carries. The v2.5.6 text stays in
`conditions.py`, unused, as `UNIVERSAL_BRIEFING_V256`, so the one set made with it can still
be named, and a model that does not run its app is recorded as such (section 10, ninth), as it was
before v2.5.6. *v2.5.10: reinstated, pending a smoke of every grid model.* Read a second
time, the same re-smoke says the sentence did what it was added for (both models ran
commands where they had run none) and that what it cost fell evenly: gpt-oss's two
parse-failure voids came one in each arm, in the two runs where it did the work the
`execution` and `interactive` conditions exist to measure. Magistral's removal stands on its
own record (section 5.1). So the study lead reinstated the sentence, sha `c988f43155c49538` again.
Both texts are now named constants in `conditions.py` (`UNIVERSAL_BRIEFING_V1` and
`UNIVERSAL_BRIEFING_V256`) and which one is registered is a single line. The sentence now
stands or falls on a smoke of all seven grid models made under it, one run per arm per
condition, 60 runs, read against each model's latest smoke under the original text.
**Registered before any of those runs is read:** if the set passes every gate and no model
is flagged, the sentence stays. A model is flagged if, under the sentence, it fails a gate (
G14, more than one unparseable-output void in three in an arm, is the likeliest) or finishes
two or more fewer of its nine runs than on that smoke (one or more fewer of its six, for
gpt-oss), or loses runs to a kind of failure it did not show there. Those smokes finished
Gemma-4-31B 9 of 9, Qwen3.6-27B 8, Seed-OSS 9, gpt-oss 6 of 6, GLM 6, Qwen3.6-35B-A3B 7 and
Gemma-4-26B-A4B 8, all under `02f244a9339a0cb6`. Each flagged model is set out here
with its numbers, and the study lead decides before the freeze whether the sentence stays
and whether the model does. If the sentence goes, the original is registered again and the
certifying smoke is made under it. If it stays, this set is the certifying smoke, provided
the harness is committed before it is made (nothing modified and nothing untracked in
`harness/`, both of which `harness_git` counts) and not changed after it (section 9 item 0). Its
runs also recalibrate the machine-time row of section 4.2. The conditions are
**blocks, not treatments**: the visibility switch is tested inside each,
results are stratified by them, and they are never compared to each other as
a finding.

**The all-model smoke under the reinstated sentence, set out (v2.5.11).** Made on 2026-09-25
and 26 from the committed harness (`a110393`) (but for two GLM `no_verification` runs started
two minutes before the commit, whose `harness_git` hash reproduces exactly from that commit's
diff, so their code is the same) 60 runs and four kept failed attempts in 5 h 18 min.
**Gates:** three fail. G2: one Gemma-4-26B-A4B OFF run (`kanban-board x execution`) ended on a
97,329-character reply filed as reasoning, a runaway of 2,698 lines of which 430 are distinct.
Its other 65 OFF steps carried no reasoning, bar one of 85 characters. G6: the two GLM runs'
`harness_git`, different in form only. G9: a GLM SEEN run exhausted the 12M budget (12,008,378
tokens) starting its server, probing its port and starting it again (`npx tsx index.ts` 20
times, `netstat`, `fuser` and `curl` 16 to 18 times each, 245 commands in all) a cycle too
varied for the loop guards to see. **Finished runs**, against each model's latest smoke under
the original text: Gemma-4-31B 9 -> 8, Qwen3.6-27B 8 -> 8, Seed-OSS 9 -> 8, gpt-oss 6 -> 4, GLM
6 -> 3, Qwen3.6-35B-A3B 7 -> 5, Gemma-4-26B-A4B 8 -> 7, 53 -> 43 of 60. **Flagged** by the rule
registered above: every model but Qwen3.6-27B, gpt-oss, GLM and Qwen3.6-35B-A3B on the count,
Gemma-4-26B-A4B and GLM on a gate, and Gemma-4-31B and Seed-OSS on the new-kind clause alone.
That clause was too sensitive, and it is recorded as such: with nine runs, a first appearance of
some failure kind is to be expected whenever every trajectory is re-rolled, and here every one
was, because under a fixed seed any byte of the prompt changes every run's path. **What the set
can and cannot say.** `no_verification`, where the sentence has nothing to act on, lost runs as
often as the conditions where it does: of the slots that had finished under the original text,
4 of about 19 failed in `no_verification` and 6 of about 34 in `execution` and `interactive`.
So most of the fall is the re-roll, as far as nine runs a model can say anything. What is the
sentence's own: gpt-oss's two voids, both in the two runs where it ran commands (section 10, fifth).
GLM's runs, 2.2 times longer, with loops on commands (the same `npm install` 31 times,
every recorded result a success) and the budget exhaustion above, and more of the `execution` and
`interactive` runs checking their work: Seed-OSS 4 -> 5 of 6, GLM 3 -> 5, gpt-oss 0 -> 1 of 4,
the rest unchanged at 5 or 6 (by a count close to section 10's, not identical to it). At the set's pace
the grid is about 161 h against about 150 h under the original text: GLM adds 18 h, Seed-OSS
gives back 6. **The arms cannot be compared on this set.** The smoke layout gives UNSEEN two
`kanban-board` cells and OFF and SEEN one each, and `kanban-board x interactive`, the hardest
cell, is run by UNSEEN alone among the three-arm models: it finished 1 of 6. On
`message-board`, the same models' UNSEEN runs finished 6 of 6. The grid, with every arm in
every cell, is where arms are compared. **The decision is open**: the study lead's, under
the rule above. A test proposed before it: gpt-oss's four `execution` and `interactive`
cells, both arms, three more replicates each (24 runs, about 40 minutes), which gives its
void rate when it can run commands, arm by arm, on balanced cells.

**The decision (v2.5.12).** The probe was made from the committed harness: gpt-oss, both arms,
its four `execution` and `interactive` cells, replicates 02-04, 24 runs, each run once by hand.
gpt-oss voided 8 of them on output its server could not parse, 4 of 12 in each arm: one in
three, G14's ceiling, and every gate passed. With the smoke's four, 5 of 14 in each arm. The
study lead's decisions, under the rule above: **the sentence stays, and no model leaves the
grid.** **G2 is waived** for the one Gemma-4-26B-A4B OFF runaway, and the reasoning carried by
OFF steps is counted per model in the grid, so that a switch that leaks is seen. **G9 is
answered by raising the token budget to 20M** for every model (section 4.4): knowing that the run
which reached 12M was cycling, so the raise may only let it cycle longer. **G6** is answered
by the re-smoke below. What one in three costs gpt-oss in the grid: about a third of its
first attempts at its 128 `execution` and `interactive` slots void, and since a retry in the
blind layout is a fresh draw (a new workspace path) about 4% of those slots end up empty
after three attempts, for about an hour of extra machine time. Its void rate is reported per
arm, over attempts, and a grid rate materially above one in three is the reason to stop and
look that section 10 registers. **The certifying smoke is made again**, because every manifest
records the budget it ran under and G10 requires one value across a set: a 12M set cannot
certify a 20M grid. It is made from the same smoke root, seeds and briefing as the set above (
which was made under `/tmp/runs/smokes`, not the separate root the runbook suggested) so
each run should replay its predecessor exactly (section 10, fifth), except where the new budget
reaches: in that set, the one GLM run that hit 12M. Its two pre-commit GLM runs are made
again with the rest, which settles G6.

*v2.5.13: the replay holds only up to the file-state note.* The note added to the file tools
in v2.5.13 (section 4.4) changes what a model sees from the first call it fires on. Replayed
through it, 23 of the set's 60 runs get it (Gemma-4-31B in 6 of 9, Gemma-4-26B-A4B and
Qwen3.6-35B-A3B in 5, GLM in 3, Qwen3.6-27B in 2, gpt-oss in 2 of 6, Seed-OSS in none) 
first at steps 2 to 54, median 15, so those runs can replay their predecessors only up to
that call. The other 37 should still replay throughout, but for the GLM run the new budget
reaches.

**The certifying smoke at 20M, set out (v2.5.14).** Made on 2026-09-26 and 27 from the
committed harness (`543d0e2`): 60 runs in 4 h 56 min, one failed attempt (gpt-oss's) and no
voids. **Gates:** every gate passes but two. G2: in Gemma-4-26B-A4B's `message-board x
interactive` OFF run the model opened its thought channel at step 6 and wrote 1,213 characters
of planning into the reasoning field, emitted the channel marker as content at step 10, and
ended at step 21 in a 92,936-character runaway that opened with it. In its `kanban-board x
execution` OFF run the tail of a tool call (code, and the call's closing tokens) was filed
as 251 characters of reasoning. Gemma-4-31B's OFF runs show none of this. G9: the GLM SEEN
`kanban-board x execution` run, the slot that exhausted 12M, exhausted 20M (20,019,397). From
step 103 it wrote the same 163 characters of reasoning every step, and from step 113 it posted
"Test card in done 2", "...3" and so on to "...184": 183 calls, each succeeding, each differing
only in its counter, so no loop guard saw a repeat. The raise let it loop longer, as section 4.4
foresaw, and at a cost of 15 minutes. **Finished runs**, against the 12M set: Gemma-4-31B
8 -> 9, Qwen3.6-27B 8 -> 7, Seed-OSS 8 -> 9, gpt-oss 4 -> 6 of 6, GLM 3 -> 5, Qwen3.6-35B-A3B
5 -> 8, Gemma-4-26B-A4B 7 -> 5, 43 -> 49 of 60. By slot, ten runs that had failed finished and
four that had finished failed. **The file-state note** fired in 25 runs, 113 times, and 21 of
the 25 finished. In `no_verification`, where a run replays its predecessor exactly up to the
note (section 10, fifth), 4 of the 5 runs that had failed at 12M finished after it first fired (
Gemma-4-31B's rewrite loop, Qwen3.6-35B-A3B's `vite.config.js` loop and its runaway, GLM's
loop) and none of the four that had finished failed. The fifth, Qwen3.6-35B-A3B's 31
identical-string edits of `package.json`, went on regardless: "The edit_file tool is not
working. Let me try running npm install directly." Five runs, and any change re-rolls the rest
of a run, so this cannot tell what the note says from the fact that it changes something.
**The other failures:** GLM's two OFF runs each made the same `npm install -D ...` call 31 times
in a row, every one succeeding, until the no-progress guard. A GLM UNSEEN run alternated two
npm commands until the cycle guard. One Gemma-4-26B-A4B UNSEEN run alternated an edit and a
write of one file until the cycle guard, the note firing twice first, and another ran away
again, in `kanban-board x interactive`. Qwen3.6-27B lost two UNSEEN runs to two turns without
a tool call (section 10, third and sixth).

**The decisions (v2.5.14).** The study lead's, on this set. **G2 is waived and watched
again:** Gemma-4-26B-A4B keeps its OFF arm, its OFF reasoning is counted per model in the grid
as v2.5.12 registered, and `verify_smokes.py` lists its over-length OFF runs under the waiver
instead of failing G2, a departure from section 9 item 2, recorded there as one. **G9 is answered by
accepting the outcome:** the budget stays at 20M, the run counts as `token_budget_exhausted`,
a non-completion, as it always did, and `verify_smokes.py` waives G9 for a run that reached the
budget while looping, its last 30 calls at most 3 distinct once every number in them is
masked. Any other run over the budget, or within a fifth of it, still fails the gate. **The
finish nudge is given after every turn without a tool call** (section 10, sixth), since under the
rule it replaced a single one-token reply was ending runs that were working. That is a harness
change, so the grid waits for one more certifying smoke, made after the commit that takes it
in (section 4.6, section 9 item 0).

**One briefing for every model, not each vendor's own system prompt (v2.5.9).** Whether each
model should run under the system prompt its maker recommends was put to the plan, and the
answer is no, for three reasons. First, none of the seven has one (nor Muse Glimmer, the eighth since v2.5.20, whose documentation gives none): no vendor publishes a
recommended system prompt for general or agentic use of these checkpoints (the cards give
sampling, thinking switches and tool formats (section 4.4.1)) and the one roster model whose maker
did was Magistral, whose reasoning instructions this study appended as its thinking switch
(section 4.2.1) and which has left the grid. Second, what a model's prompt must contain, its own
chat template already puts there, in every arm of every run: gpt-oss's template writes the
harmony `system` message itself and renders the caller's system prompt as the `developer`
message, where OpenAI's guide puts instructions. Gemma's adds its `<|think|>` token. GLM's
adds its tool-calling instructions, and Seed-OSS's default line, "You are Doubao...", appears
only when no system prompt is sent at all, which never happens here. The agent tools some
vendors ship (Qwen Code, OpenAI's Codex) carry prompts written for their own tool sets, not
this harness's. Third, the design gains nothing from a per-model prompt and would lose
something: every contrast is climbed inside one model, where the prompt is the same in every
arm whichever prompt it is, while prompts that differed between models would add a
between-model difference the study could not separate from the models themselves. What the
vendors do publish runs the other way: four of the five makers, Google, Alibaba, Z.ai and
OpenAI. Four of six since v2.5.20, Meta saying nothing either way: advise keeping a model's past reasoning between tool calls in agentic use. So the
UNSEEN arm runs those models against their makers' advice, by design. That is the question
the study asks, and the paper says so. (Laguna XS 2.1 was passed over for more than advice:
its card warns that reasoning may not be generated at all in follow-up steps once earlier
thinking is dropped, section 5.1.)

Why `no_verification` earns its slot: in the two feedback conditions the
*world* acts as the model's external memory, test output, command results
and page reads keep telling it where it stands, so it can afford to forget
its own plan. With nothing to run, the model's own scratchpad is the *only*
record of what it decided three steps ago. If re-reading one's thoughts
matters anywhere, it should matter most there. A null result there makes
"have the thought, bin the note" far stronger, and an effect that appears
*only* there is a clean mechanistic story. It is also the cheapest block on
the ladder (no tools to exercise, so the shortest runs). Expect interactive
runs, by contrast, to be the longest and hungriest for context, because
there are the most tools to exercise. One consequence of the third block is
written down now, not discovered later: the question *"is the visibility
effect larger when the agent cannot verify?"* is pre-specified as
**exploratory** (reported, but not a hypothesis and not error-controlled) 
so the study still tests exactly one thing. (Do not confuse the
`interactive` condition with the harness's `INTERACTIVE=1` flag, which lets
a human type into a run for debugging and marks it contaminated, that flag
is never set for study runs.)

### 4.2 The run grid, per model

Twenty replicates in every cell. Tasks and conditions are blocks. The arm is
the treatment. How many arms a model runs depends on whether it has a
*working* thinking off-switch: which the smoke set established per model, by
reading what each model actually emitted step by step, rather than taking the
model card's word for it. That audit moved two of the five models and is
written up in section 4.2.1. Read it before the tables below make sense.

| task x condition | OFF | UNSEEN | SEEN | per block (3-arm / 2-arm) |
|---|---|---|---|---|
| message-board x no_verification | 20 | 20 | 20 | 60 / 40 |
| message-board x execution | 20 | 20 | 20 | 60 / 40 |
| message-board x interactive | 20 | 20 | 20 | 60 / 40 |
| kanban-board x no_verification | 20 | 20 | 20 | 60 / 40 |
| kanban-board x execution | 20 | 20 | 20 | 60 / 40 |
| kanban-board x interactive | 20 | 20 | 20 | 60 / 40 |
| **per arm / per model** | **120** | **120** | **120** | **360 / 240** |

On top of the grid: **smoke runs** (1 per arm per condition = 9 or 6 per
model, run before the grid, excluded by design, they also calibrate timing
tested the grading tools and are the training rounds' apps, no grading of a smoke app enters the analysis, section 9 item 5). There is no separate control cell any more: 
the OFF arm *is* the sensitivity check, at full strength (section 6).

| | Gemma 31B | Qwen 27B | Seed-OSS | gpt-oss | GLM | Qwen 35B-A3B *(v2.5.5)* | Gemma 26B-A4B *(v2.5.5)* | Muse *(v2.5.20)* | total |
|---|---|---|---|---|---|---|---|---|---|
| arms | 3 | 3 | 3 * | 2 | 3 | 3 | 3 | 2 | |
| grid | 360 | 360 | 360 | 240 | 360 | 360 | 360 | 240 | 2,640 |
| smokes | 9 | 9 | 9 | 6 | 9 | 9 | 9 | 6 | 66 |
| **runs** | **369** | **369** | **369** | **246** | **369** | **369** | **369** | **246** | **2,706** |
| machine time, grid | ~26 h | ~50 h | ~54 h | ~7 h | ~31 h | ~28 h | ~24 h | ~20 h | **~240 h (10 days)** |

Six of the eight models run the full three-rung ladder, and each rung adds
exactly one thing to the rung below it: OFF is no thinking and nothing to
replay, UNSEEN is thinking discarded, SEEN is thinking replayed. gpt-oss and
Muse Glimmer, which have no off-switch, run two rungs. *v2.5.20:* Muse's ~20 h is its six-run
pilot of 2026-09-30, 30 minutes, taken 40 times over, as the other columns are. *v2.5.9:* Magistral's column is gone. It left the
grid on its re-smoke (section 5, section 5.1), taking 297 runs and about 10 hours with it.

* Seed-OSS's OFF rung survives only because reasoning replay is off in that
arm. See section 4.2.1.

*v2.5.15:* twenty replicates where there were sixteen, at the study lead's decision. At sixteen
the grid was 1,920 runs (48 / 32 per block, 288 for a three-arm model and 192 for gpt-oss) 
and 1,980 with the smokes, and the machine-time row read ~18 h, ~28 h, ~17 h, ~2 h, ~15 h,
~24 h and ~25 h, ~129 h (5.4 days) in all. The paragraph below describes that row. The row now
projects twenty replicates from the nudge-rule smoke of 2026-09-27, used for its timing alone
while its gates are still to be set out: 60 runs in 5 h 29 min, server start and stop included,
and the grid is that set 40 times over, arm for arm and condition for condition, though not
task for task. Nine runs a model, six for gpt-oss, make the per-model figures rough. At sixteen
replicates the same pace would give about 176 h.

Until v2.5.15 the machine-time row was measured, on the 2026-09-21 smoke set, with every
model running the arms it will actually run. Mean wall clock per run: gpt-oss
0.8 min, Magistral 2.1, Seed-OSS 3.5, Gemma 3.7, Qwen 5.8. The longest single
run was a 76-step Qwen `execution` SEEN run at 14.0 min. GLM, added in v2.5.0, is
measured on its own nine-run smoke of 2026-09-25: 3.1 min per run, the longest a 119-step
`interactive` SEEN run at 9.9 min. The twins, added in v2.5.5, are measured on their own
nine-run smokes of the same day: 4.9 min per run for Qwen3.6-35B-A3B, the longest an 80-step
`execution` OFF run at 13.2 min, and 5.2 for Gemma-4-26B-A4B, the longest the 79-step
`interactive` UNSEEN run that filled its context window, at 13.6 min. *v2.5.5:* at the latest
smokes' pace the row would read about 154 h, not ~139 h. *v2.5.9:* without Magistral,
and re-measured on each model's latest smoke (the agent's own wall clock, before the 6-12
seconds of server handling per run), about 150 h against the table's ~129 h. The same
measure puts all eight at 158 h. Seed-OSS's runs lengthened from 3.5
to 8.2 minutes in the 12M smoke set, the first made under vendor sampling, while no other
model moved by as much as a minute. The certifying re-smoke recalibrates the whole row.
Booting the server,
proving it is serving the right file and stopping it again costs 6-12 seconds
per run: negligible, because after the first load the GGUF stays in the page
cache, so there is no reason to keep a server alive across runs and lose
per-run isolation for it. About five and a half days was the *continuous* figure by that
row, and over six at the pace of the smokes then latest. At twenty replicates it is about
nine (v2.5.15), and about ten with Muse (v2.5.20). Budget more for the grading that follows
each tier: about 607 hours in all, for one grader, at the draft rubric's rough timings (section 4.5, v2.5.18, v2.5.20, v2.5.25).

Order: one model resident on the server at a time (no swapping mid-model).
Within each task x condition block the arms strictly rotate OFF, UNSEEN,
SEEN, OFF, ... (UNSEEN, SEEN, ... for two-arm models). The full schedule is
written down and frozen before the first run.

**Run ids and folders.** Classic layout: id `<arm><replicate>` with 1 =
OFF, 2 = UNSEEN, 3 = SEEN, replicates 01-20 (01-16 until v2.5.15), stored
as `<root>/<task>/<condition>/runs/<id>/`. For the study proper we use the
**blind layout** (`BLIND=1` in the run wrapper): the run is stored as
`<root>/<task>/runs/<random 6-digit id>/` (no condition and no arm anywhere
in the path) so whoever grades the apps cannot be steered by the folder
name. Ids are drawn at random and burned forever in an append-only ledger
(`blind-state/blind-ids.txt`), and every run's condition, arm, model and
quant are recorded in its `manifest.json` plus one line in the un-blinding
key (`blind-state/blind-key.jsonl`, kept outside the runs tree). Each run's
whole lifecycle (boot the server, prove it is serving the right file, run
the agent, stop the server, archive the server log next to the run) is one
invocation of `run_one_with_server.sh`.

### 4.2.1 Which off-switch actually works: the thinking-mechanism audit

A model card tells you how to turn thinking off. It does not tell you whether
that switch survives contact with an agent loop. The smoke set (thirty-two
completed runs, one per arm per condition per model, excluded from analysis by
design) is where that got checked, and it moved two of the five models.

**Gemma and Qwen behaved exactly as documented.** With
`enable_thinking: false` they produced no reasoning at all: zero characters
across 244 OFF steps. With it true, reasoning appeared on essentially every
step. Nothing to change.

*v2.5.9: Magistral has left the grid (section 5.1). Its part of this audit is kept as the record of
how its arms were built and why.*

**Magistral was not thinking in either arm.** All 36 of its responses came
back with an empty reasoning field and no `[THINK]` block anywhere in the
text. This is not a parser problem and not a quantization problem. Magistral's
reasoning is driven by a *system prompt*, which its chat template supplies
only when the caller supplies none: and the harness always supplies its own
("You are a software engineer..."), which displaced Mistral's reasoning
instructions. So Magistral's UNSEEN and SEEN arms were the same condition
under two names. Worse, that failure is invisible in the totals: "no
reasoning was replayed" and "there was no reasoning to replay" write the same
manifest. The fix makes the omission deliberate and turns it into the switch.
The harness gained `--think-preamble KEY`, which appends one of two
*registered* preambles to the system prompt and records the key and its hash
in every manifest, folded into `system_prompt_sha`. Only registry keys are
accepted, so prompt text cannot reach a study run from a command line, and
adding a preamble is a code change that moves `harness_git`. Magistral's two
thinking arms carry the preamble. Its OFF arm omits it, which is a *measured*
off-switch rather than a hoped-for one: 36 of 36 responses without it carried
no reasoning. Note carefully what this does and does not vary: the primary
UNSEEN->SEEN contrast holds the preamble constant and moves only replay,
exactly as for every other model. Only the secondary OFF->UNSEEN contrast is
implemented by a prompt change rather than a template switch, and the paper
says so rather than letting the reader assume otherwise.

Two preambles were registered because the vendor's own text carries one
sentence that has nothing to do with thinking ("Format your response using
Markdown, and use LaTeX for any mathematical equations") and answering in
Markdown prose instead of calling `write_file` is a failure mode this model
had already demonstrated, once at 25,626 characters with no tool call. So
`mistral` is the model-card text verbatim and `mistral-min` is the same
thinking protocol with that sentence cut.

**The study uses `mistral-min`, and the way that decision was reached is worth
recording in full, because it was made wrongly first.** A single probe run per
variant chose the vendor text: with `mistral` the model reasoned on 9 of 9
steps, with `mistral-min` on 1 of 3 and seemingly abandoning the protocol. On
one run each, that looked decisive. It was not. Ten runs per variant, on the
same task and condition, reverse it on every measure:

| | `mistral` (vendor) | `mistral-min` |
|---|---|---|
| steps carrying reasoning | 85 / 93 (91%) | **94 / 94 (100%)** |
| runs reasoning on every step | 8 / 10 | **10 / 10** |
| median reasoning characters | 381 | **477** |
| runs writing prose at step 1 | 4 / 10 (up to 12,099 chars) | **0 / 10** |
| runs narrating instead of calling a tool | 1 / 10 | **0 / 10** |
| runs finishing | 9 / 10 | **10 / 10** |
| steps per run | 9.3 | 9.4 |

Re-smoking Magistral across all three conditions confirmed it outside the single cell the
comparison was made in, and the OFF arm gives a free check on the whole pipeline while it
is at it: carrying no preamble, it is untouched by the switch and came back *identical*:

| arm | steps (vendor -> trimmed) | no-tool turns | runs finishing |
|---|---|---|---|
| OFF | 24 -> 24 | 4 -> 4 | 2/3 -> 2/3 *(unchanged, as it must be)* |
| UNSEEN | 27 -> 21 | 1 -> **0** | 3/3 -> 3/3 |
| SEEN | 10 -> **20** | 4 -> **0** | 1/3 -> **3/3** |

Magistral's no-tool turns are now confined entirely to the OFF arm (zero across 41 steps
in the two thinking arms) which fits the mechanism: with no thinking instructions at all,
the model reverts to answering in prose. That is a property of the OFF rung rather than a
fault, and the failure-incidence measure is what records it.

The single probe had caught `mistral-min` on a run where it reasoned once and
stopped. Across ten runs it never does that: and it is the *vendor* text that
intermittently stops, twice at around 25% of steps. The narration worry that
motivated trimming in the first place was also real and pointed the same way:
with the vendor text four runs in ten wrote prose at step 1 alongside the tool
call, and one wrote prose instead of calling a tool and died.

So the study deviates from the model card by one sentence, and says so. The
deviation is minimal and has a reason beyond the measurement: in a harness
where the model writes files through tools rather than replying in prose, an
instruction about formatting replies in Markdown and LaTeX is not merely
irrelevant, it pulls against the behaviour the task requires. A *measured*
deviation with twenty runs behind it is more defensible than unmeasured
adherence: and the same twenty runs corrected a second error, the claim that
Magistral fails to call tools on 15% of its steps. That figure came from 61
steps across nine smoke runs and was dominated by two 2-step runs. Over 187
steps the rate is about 3%, in line with gpt-oss.

Both corrections have the same shape, and it is the methodological point of
this section: **a configuration chosen on one run is not chosen, it is
guessed.**

**The two registered preambles.** These are the strings in
`harness.agent.THINK_PREAMBLES`. The sha256 prefix of each is what every run
records as `think_preamble_sha`, so a run's manifest identifies which text it
was made with rather than merely naming a key.

*One caveat about the blocks below:* each real string is **three lines** (one
long line, one blank, one long line) and is reproduced here soft-wrapped so it
fits the page. The wrapped text is therefore not byte-identical to what is
sent, and its hash would not match. The hashes quoted are of the true strings.
The authoritative bytes are the dictionary entries in the harness, and the hash
is what lets anyone confirm they have the right ones.

`mistral-min`: 358 characters, `612ec84fef27da7d`, **what the study uses**:

```
First draft your thinking process (inner monologue) until you arrive at a response.

Your thinking process must follow the template below:[THINK]Your thoughts or/and draft,
like working through an exercise on scratch paper. Be as casual and as long as you want
until you are confident to generate the response.[/THINK]Here, provide a self-contained
response.
```

`mistral`: 554 characters, `88ea600602b0dbfc`, Mistral's own
`default_system_message` copied verbatim from the GGUF's template, kept
registered and reachable with `MAGISTRAL_PREAMBLE=mistral` so the comparison
above can be reproduced:

```
First draft your thinking process (inner monologue) until you arrive at a response.
Format your response using Markdown, and use LaTeX for any mathematical equations.
Write both your thoughts and the response in the same language as the input.

Your thinking process must follow the template below:[THINK]Your thoughts or/and draft,
like working through an exercise on scratch paper. Be as casual and as long as you want
until you are confident to generate the response. Use the same language as the
input.[/THINK]Here, provide a self-contained response.
```

The deviation is exactly two sentences: the Markdown/LaTeX formatting
instruction and the language-matching instruction (which appears twice, once
in the preamble and once inside the `[THINK]` block). The thinking protocol
itself is untouched: same opening instruction, same `[THINK]...[/THINK]`
template, same closing sentence.

The preamble is appended **last** in the system prompt, after the base prompt
and the condition briefing, at a fixed position so `system_prompt_sha` is a
function of the parts and nothing else. Per arm, as recorded in all nine of
Magistral's smoke runs:

| arm | `think_preamble_key` | `think_preamble_sha` | appended |
|---|---|---|---|
| OFF | `none` | `e3b0c44298fc1c14` | nothing: this *is* the off-switch |
| UNSEEN | `mistral-min` | `612ec84fef27da7d` | 358 characters |
| SEEN | `mistral-min` | `612ec84fef27da7d` | 358 characters |

`e3b0c44298fc1c14` is the sha256 of the empty string, so an OFF run that ever
recorded anything else would be visibly wrong on inspection. And note what the
last two rows share: **the two thinking arms carry an identical preamble and an
identical hash**, so the primary UNSEEN->SEEN contrast never varies the system
prompt, only replay moves. Gates G5 and G13 both enforce it.

Two residues are worth recording. First, Magistral appends a stray `[/THINK]`
to the end of any turn that carries a substantive prose answer: the final
nine characters of its `finish` message, and nothing more. The opening
`[THINK]` never appears in the content field, so no reasoning is leaking past
the parser. It is cosmetic, it is recorded here so nobody rediscovers it as a
bug, and the canary in section 9 checks for the *opener*, which would be the real
fault. Second, one of the 36 no-preamble smoke responses also carried a stray
marker, so the OFF arm is "does not think", not "has never seen the
protocol": which is the correct reading of an off-switch anyway.

**Seed-OSS's off-switch works, but the model stops talking.**
`thinking_budget: 0` does suppress real reasoning. What is left is not
nothing, though: the template emits a fixed 133-character stub on every single
turn (*the current thinking budget is 0, so I will directly start answering
the question*) which the server duly reports in the reasoning field. Against
a median of 390 characters of real reasoning in Seed's SEEN arm, that stub is
plainly an artifact. But a canary that asks only "is the reasoning field
empty?" would have failed Seed-OSS for thinking when it was not thinking at
all, which is why the canary rule (section 9) is now written in terms of length. The
harder problem is the silence: 55% of Seed's budget-0 turns returned the stub
and *nothing else*, no text, no tool call, half a second of generation. The
harness nudges once when a model goes quiet and stops on the second silence,
so all three OFF runs died within three or four steps.

**That turned out to be the replay, and the fix is a rule rather than a
patch.** Re-running the same `thinking_budget: 0` configuration with reasoning
replay switched off (so the stub never re-enters the conversation) produced
**zero empty turns in 33 steps**, against six in eleven before. Seed-OSS keeps
its third arm. The rule is not a Seed-specific exception, though, because the
honest reading applies to every model: *in the OFF arm there is no reasoning,
so replay is set off explicitly rather than left at the harness default.* For
Gemma, Qwen and preamble-free Magistral that changes nothing observable (280
OFF steps between them carried zero characters of reasoning, so replaying it
was already a no-op) and for Seed-OSS it is the difference between a working
arm and a dead one. One rule, no carve-out, and the manifest now records
`reasoning_replayed = false` in every OFF run rather than an accidental true.

Worth noticing what the failure actually was, because it rhymes with the
question this study asks. Seed did not break because thinking was off. It
broke because it was shown a history in which every one of its own past turns
consisted of a stub saying, in effect, *I have no budget to think, I will just
answer*: and it went on producing turns that were nothing but that stub. A
model conditioning on its own visible reasoning history until it degenerates
is an extreme instance of the very mechanism section 2 describes. It is an anecdote
from an instrument check rather than a result, and it is recorded as one.

**gpt-oss has no off-switch**, as its card says, and runs two arms. Its first
smoke set never ran at all, for a reason worth recording because it is the
kind of fault this whole apparatus exists to catch: the run wrapper built its
request body with a shell default that silently appended a stray brace, the
agent rejected the malformed JSON, and six runs died identically at startup.
The wrapper now validates the body as JSON *before* starting the server.

The general lesson, and it belongs in the paper: an OFF arm is a claim about
the instrument, not about the model, and the only way to check it is to read
what the model actually emitted, step by step, inside the loop you intend to
run. Not the model card, and not the run totals.

### 4.2.2 How each model's thinking is switched, model by model

Nothing in this study is more load-bearing than the claim that the three arms differ in
exactly one thing. That claim is not about our code: it is about six Jinja programs
written by six different labs, and the only way to check it is to read them.

The switch travels through **three layers**, and a failure at any one of them is silent.
The first two are identical for every model, so they are described once here. What
differs per model is the third, and the vocabulary the first two carry.

**Layer 1: the request body.** The harness sends an ordinary OpenAI-shaped
`POST /v1/chat/completions`, and adds one extra top-level field:

```json
{ "model": "gemma-4-31b", "messages": [ ... ], "max_tokens": 32768,
  "chat_template_kwargs": {"enable_thinking": false, "preserve_thinking": true},
  "top_k": 1, "temperature": 0.0, "top_p": 1.0, "tools": [ ... ] }
```

`chat_template_kwargs` is **not part of the OpenAI specification**. OpenAI's API has no
chat templates at all (it formats messages internally and never exposes the step) so
there is nothing for such a parameter to hook into. It is an extension that the
open-weight serving stack converged on (llama.cpp, vLLM, SGLang), and that is exactly why
the harness needs an escape hatch to send it: no SDK has a named argument for it, so it
rides in `--extra-body`, a dict spread into the payload at `llm.py:334`. The practical
consequence is worth stating plainly: **an OpenAI-compatible server ignores body fields it
does not recognise rather than rejecting them.** Misspell the field and nothing errors.
The template silently falls back to its own defaults and the arms quietly collapse. Only
the behavioural gates in section 9 catch that.

**Layer 2: llama-server merges it into the render context.** With `--jinja`, llama-server
runs the template baked into the GGUF at `tokenizer.chat_template` and merges every key of
`chat_template_kwargs` into that render as a **top-level Jinja variable**. So
`{"enable_thinking": false}` in the body makes the bare name `enable_thinking` resolve to
`false` inside the template. Keys the template never mentions are simply unused: harmless,
and equally invisible. (Without `--jinja` llama.cpp falls back to a built-in C++ formatter
that ignores `chat_template_kwargs` entirely, which would collapse every arm into one,
this is why `--jinja` is in the frozen serving flags rather than left to a default.)

**Layer 3 (the template decides what that means.** This is where the models diverge
completely) six templates for the eight models the grid held until v2.5.9, since each twin serves its sibling's, five for the seven it held from then, and six for the eight it holds since v2.5.20, Magistral's part kept as the record: and the rest of this section is one part per model. Each says: what we put in
`chat_template_kwargs`, which variables that defines, and what the template's own code does
with them.

**Where these templates come from.** They were extracted from the study's own GGUF files
with `gguf_chat_template.py`, which reads only the header: not the vendor's published
template, which can differ from what a quantizer repacked. Five of the six match (and Muse
Glimmer's, v2.5.20, `114f55ebdc1804c1`), byte for byte, the `chat_template_sha` that every run already records in `serving_probe` (GLM's
among them, v2.5.0). Gemma's differs by exactly one trailing newline that llama-server
strips before reporting it.

| model | template file | chars | sha256[:16] (as served) | switch vocabulary |
|---|---|---|---|---|
| Gemma-4-31B-it | `gemma-4-31B-it-Q4_K_M.jinja` | 18,921 | `aa3185dfc6505104` | `enable_thinking`, `preserve_thinking` |
| Qwen3.6-27B | `Qwen3.6-27B-Q4_K_M.jinja` | 8,057 | `55d4931433fe502b` | `enable_thinking`, `preserve_thinking` |
| Seed-OSS-36B | `Seed-OSS-36B-Instruct-Q4_K_M.jinja` | 7,438 | `25b74a75d793cc03` | `thinking_budget` |
| Magistral-Small-2509 *(retired, v2.5.9)* | `Magistral-Small-2509-UD-Q4_K_XL.jinja` | 4,690 | `3f6683b4cea89122` | *(none: system prompt)* |
| gpt-oss-20b | `gpt-oss-20b-F16.jinja` | 17,221 | `70da0d2348e40aaf` | `reasoning_effort` |
| GLM-4.7-Flash | `GLM-4.7-Flash-Q4_K_M.jinja` | 3,120 | `d63ad536c3c81880` | `enable_thinking`, `clear_thinking` |
| Qwen3.6-35B-A3B *(v2.5.5)* | `Qwen3.6-35B-A3B-UD-Q4_K_M.jinja` | 8,057 | `55d4931433fe502b` | the 27B's, byte for byte |
| Gemma-4-26B-A4B-it *(v2.5.5)* | `gemma-4-26B-A4B-it-UD-Q4_K_M.jinja` | 18,921 | `aa3185dfc6505104` | the 31B's, byte for byte |

*v2.5.3:* the two proposed mixture-of-experts twins (section 5) serve their dense siblings'
templates byte for byte (Qwen3.6-35B-A3B's is `55d4931433fe502b`, and Gemma-4-26B-A4B-it's
is `aa3185dfc6505104` as served (the extracted file, with its trailing newline, is
`845f1ee48e39fc94`, as the 31B's is)) so everything this section says about Qwen's and
Gemma's templates holds for the twins unchanged.

One thing is common to every model and is not a template variable at all: **whether each past
assistant message in `messages` carries a `reasoning_content` field**. That is the
UNSEEN/SEEN switch, and no kwarg can substitute for it: a template cannot render data the
request did not contain.

---

#### Gemma-4-31B-it

**What we send.** `{"enable_thinking": false|true, "preserve_thinking": true}`.

**What that defines.** Both names resolve inside the template. Both have defaults, and the
default for the one that matters is the dangerous direction:

```jinja
{%- set enable_thinking = enable_thinking | default(false) -%}
{%- set preserve_thinking = preserve_thinking | default(false) -%}
```

A request that says nothing gets a model that does not think. The thinking arms must ask
explicitly. Silence is not neutral here.

**What the template does.** Gemma keeps reasoning in a *channel*, `<|channel>thought ...
<channel|>`, with a `strip_thinking` macro that removes those markers from ordinary
content. `enable_thinking` acts in two places. At the top it injects a `<|think|>` token
into the first system turn:

```jinja
{%- if enable_thinking -%}
    {{- '<|think|>\n' -}}
```

and at the generation point, when thinking is *off*, it pre-fills an already-closed empty
thought: which is the actual suppression mechanism, not a mere instruction:

```jinja
{%- if not enable_thinking -%}
    {{- '<|channel>thought\n<channel|>' -}}
```

`preserve_thinking` governs the *history*. Past reasoning is read from either `reasoning`
or `reasoning_content`, and rendered only if a gate passes:

```jinja
{%- set thinking_text = message.get('reasoning') or message.get('reasoning_content') -%}
{%- set thinking_gate = (loop.index0 > ns_turn.last_user_idx) or (preserve_thinking and message.get('tool_calls')) -%}
```

Read the left branch carefully: a past turn's thought renders only if that turn sits
*after the last user message*. In an agentic loop that normally means everything, because
the only user message is the task. But the harness appends a `role: user` finish nudge
when a model returns a turn with no tool call, and that moves the boundary: without
`preserve_thinking`, every thought produced before the nudge vanishes from the model's view
for the rest of the run. That is why we send it in all three arms. Note the right branch is
ANDed with `message.get('tool_calls')`, so it rescues every turn *except* one that made no
tool call: which is precisely the turn that triggered the nudge. section 10 registers a
sensitivity analysis over zero-nudge runs for that residue.

| arm | `chat_template_kwargs` | `reasoning_content` sent? | what the model is given |
|---|---|---|---|
| OFF | `{"enable_thinking": false, "preserve_thinking": true}` | no | a thought channel, pre-filled and already closed |
| UNSEEN | `{"enable_thinking": true, "preserve_thinking": true}` | no | an open thought channel. History carries no thoughts |
| SEEN | `{"enable_thinking": true, "preserve_thinking": true}` | yes | an open thought channel. Past turns show their thoughts |

---

#### Qwen3.6-27B

**What we send.** `{"enable_thinking": false|true, "preserve_thinking": true}`: the same
two names as Gemma, which is a coincidence of convention rather than a shared standard.

**What that defines.** `enable_thinking` is read only at the generation point, and it is
tested for being *explicitly* false rather than defaulted:

```jinja
{%- if add_generation_prompt %}
    {{- '<|im_start|>assistant\n' }}
    {%- if enable_thinking is defined and enable_thinking is false %}
        {{- '<think>\n\n</think>\n\n' }}
    {%- else %}
        {{- '<think>\n' }}
    {%- endif %}
```

**What the template does.** Off is a `<think></think>` block that is already closed and
empty. On is subtler than it looks: the template emits a bare `<think>\n` and *leaves it
open*, so the model begins generation inside a thought. A Qwen turn with no reasoning is
therefore not a turn where thinking was unavailable: it is a turn where the model chose to
close the block immediately. That is what it does on roughly two thirds of its UNSEEN
steps, and section 10 registers it as a behavioural finding rather than a manipulation failure.

For history, Qwen reads `reasoning_content` if present and otherwise digs the text out of
`<think>` markers inside content, then renders it before the visible reply:

```jinja
{%- if (preserve_thinking is defined and preserve_thinking is true) or (loop.index0 > ns.last_query_index) %}
    {{- '<|im_start|>' + message.role + '\n<think>\n' + reasoning_content + '\n</think>\n\n' + content }}
```

Same last-user-message trap as Gemma, and the same fix: but Qwen's is a plain OR, with no
`tool_calls` condition, so `preserve_thinking` closes the hole completely here. Verified by
rendering: with a nudge in the history and the flag set, every prior turn's reasoning is
present.

| arm | `chat_template_kwargs` | `reasoning_content` sent? | what the model is given |
|---|---|---|---|
| OFF | `{"enable_thinking": false, "preserve_thinking": true}` | no | `<think></think>`, closed and empty |
| UNSEEN | `{"enable_thinking": true, "preserve_thinking": true}` | no | `<think>` left open. History carries no thoughts |
| SEEN | `{"enable_thinking": true, "preserve_thinking": true}` | yes | `<think>` left open. Past turns show their thoughts |

---

#### Seed-OSS-36B-Instruct

**What we send.** `{"thinking_budget": 0}` for OFF, and nothing at all for the thinking
arms. ByteDance exposes no on/off switch: it exposes a *budget*, defaulting to -1 for
unlimited, so the thinking arms simply let the default stand.

**What that defines.** `thinking_budget`, an integer. No `enable_thinking` and no
`preserve_thinking` exist in this template. Sending them would be silently ignored.

**What the template does.** Budget 0 acts in two places, and both matter. First it injects
a sentence into the system prompt:

```jinja
{%- if thinking_budget == 0 %}
{{ "You are an intelligent assistant that can answer questions in one step without the
need for reasoning and thinking, that is, your thinking budget is 0. ..." }}
```

Second (and this is the part that explains the artifact in section 4.2.1) at the generation
point it *opens a budget-reflection block and leaves the model to finish it*:

```jinja
{%- if thinking_budget == 0 %}
{{ think_begin_token+budget_begin_token }}
```

So the fixed 133-character stub the OFF arm produces is not the model thinking. It is the
model completing a sentence the template started for it. That is why section 9's OFF canary is
written in terms of reasoning *length* rather than presence.

History is the important asymmetry. Seed renders past reasoning **unconditionally**, with
no last-user-message gate of any kind:

```jinja
{%- if message.reasoning_content is defined and message.reasoning_content is string
      and message.reasoning_content | trim | length > 0 %}
{{ "\n" + think_begin_token + message.reasoning_content | trim + think_end_token }}
```

Two consequences. Seed is provably immune to the finish-nudge problem (verified by
rendering) and needs no `preserve_thinking`. And it is why replaying the budget-0 stub was
so destructive: the model saw a history in which every one of its own turns was nothing but
that stub, and obliged, going silent on 55% of its turns. Hence the rule in section 4.2.1 that the
OFF arm sets replay off explicitly for every model.

| arm | `chat_template_kwargs` | `reasoning_content` sent? | what the model is given |
|---|---|---|---|
| OFF | `{"thinking_budget": 0}` | no | a "budget is 0" system line, plus a pre-opened reflect block |
| UNSEEN | `{}` (template default, -1) | no | unlimited thinking. History carries no thoughts |
| SEEN | `{}` (template default, -1) | yes | unlimited thinking. Past turns show their thoughts |

---

#### Magistral-Small-2509 *(retired, v2.5.9: kept as the record, section 5.1)*

**What we send.** No thinking kwarg at all: `{}`. The switch is not in
`chat_template_kwargs` for this model. It is in the **system prompt**.

**What that defines.** Nothing. This template reads no thinking variable of any name, so
layer 2 has nothing to carry and layer 1 has nothing to put in it.

**What the template does.** It holds Mistral's `[THINK]` protocol text as a
`default_system_message`, and uses it on exactly one condition:

```jinja
{%- if messages[0]['role'] == 'system' %}
    {%- set system_message = messages[0]['content'] %}
{%- else %}
    {%- set system_message = default_system_message %}
```

Supply your own system prompt (as the harness always does) and the reasoning
instructions are simply gone. That is the entire mechanism, and it is why Magistral
produced zero reasoning across 36 smoke responses before this was found. So its switch is
the harness's `--think-preamble`: the thinking arms append the registered `mistral`
preamble to the system prompt, the OFF arm omits it, and that omission is a *measured*
off-switch rather than a hoped-for one.

Its assistant branch renders `message['content']` and `[TOOL_CALLS]...[ARGS]...` and nothing
else: **`reasoning_content` appears nowhere in this template**. That is not a cosmetic gap,
and it took a live probe to see how bad it is. Sending the field anyway does not merely get
it ignored: llama.cpp **deletes the assistant's own prose** and puts nothing in its place.
Measured against the running server, the SEEN prompt came back 42 characters *shorter* than
UNSEEN (exactly the two assistant contents) with neither reasoning string present:

```
UNSEEN:  [/INST]Starting with the manifest.[TOOL_CALLS]write_file[ARGS]...[TOOL_RESULTS]...
SEEN:    [/INST][TOOL_CALLS]write_file[ARGS]...[TOOL_RESULTS]...
```

So the arm whose entire purpose is to show the model *more* of its own history was showing
it *less*. Left in place, that would very likely have produced "SEEN is worse than UNSEEN"
for Magistral (in the exact direction this study is testing) purely as an artifact.

**The fix is to replay the reasoning the way the model writes it.** Magistral's thinking is
not a separate field in the first place: it lives inline in the reply as `[THINK]...[/THINK]`,
which is what the model emits and what llama.cpp parses apart on the way in. So for this
model, and only this model, the SEEN arm reassembles the reply: `[THINK]{reasoning}[/THINK]`
prepended to the content, with no `reasoning_content` field at all. Rendered against its own
template that gives `[/INST][THINK]...[/THINK]Starting with the manifest.[TOOL_CALLS]...`:
content kept, reasoning present, vendor wire format. The harness carries this as
`--replay-format {field,inline-think}`, recorded per run as `replay_format`, and the paper
declares it as a per-model implementation of replay rather than leaving a reader to assume
all five models used the same route.

| arm | `chat_template_kwargs` | system preamble | how reasoning is replayed |
|---|---|---|---|
| OFF | `{}` | omitted: the measured off-switch | not replayed |
| UNSEEN | `{}` | `mistral-min` (registered deviation) | not replayed |
| SEEN | `{}` | `mistral-min` (registered deviation) | **inline**, `[THINK]...[/THINK]` in the reply text |

---

#### gpt-oss-20b

**What we send.** `{"reasoning_effort": "medium"}`, frozen, in both arms.

**What that defines.** `reasoning_effort`, a string. It has a default, and the template
renders it straight into the system block as plain text the model reads:

```jinja
{%- if reasoning_effort is not defined %}
    {%- set reasoning_effort = "medium" %}
{%- endif %}
{{- "Reasoning: " + reasoning_effort + "\n\n" }}
```

Low, medium and high are the only values. There is no off, which is why gpt-oss runs two
arms rather than three.

**What the template does.** This is OpenAI's harmony format, with three named channels: 
`analysis`, `commentary`, `final`. Its handling of past reasoning is the most explicit of
the five and the most restrictive: chain-of-thought is deliberately dropped for every turn
before the last `final` message ("CoT is dropped during all previous turns, so we never
render it for inference"), and rendered as `<|channel|>analysis<|message|>...` only for
tool-calling turns after it. An agentic run emits no `final` message until it finishes, so
the whole run counts as "after" and the reasoning is eligible in principle.

In principle, because of the field name: this template reads `message.thinking`, not
`message.reasoning_content`. It also refuses both at once: 

```jinja
{%- if message.content and message.thinking %}
    {{- raise_exception("Cannot pass both content and thinking in an assistant message with tool calls!") }}
```

 so whatever llama.cpp does to bridge the two, it is not a simple field rename. Also the
subject of the open question below.

| arm | `chat_template_kwargs` | `reasoning_content` sent? | what the model is given |
|---|---|---|---|
| OFF | *not available*: the format has no off-switch | n/a | n/a |
| UNSEEN | `{"reasoning_effort": "medium"}` | no | analysis channel open. History carries no analysis |
| SEEN | `{"reasoning_effort": "medium"}` | yes | analysis channel open. Past turns show their analysis |

---

#### GLM-4.7-Flash

*Added in v2.5.0. Quoted from the template extracted from the served GGUF (sha256
`d63ad536c3c81880`, 3,120 chars, the value every GLM run records).*

**What we send.** `{"enable_thinking": false|true, "clear_thinking": false}`.

**What that defines.** Neither name gets a default in the template: each is tested with
`is defined`, so an absent flag means *thinking on* and *history cleared*. Thinking is read
in one place, the generation prompt: 

```jinja
<|assistant|>{{- '</think>' if (enable_thinking is defined and not enable_thinking) else '<think>' -}}
```

 so the OFF arm ends the prompt on a bare `</think>`, the think block closed before the
model writes a token, and the thinking arms end on an open `<think>`.

**What the template does.** A past assistant turn's reasoning is taken from
`reasoning_content` when that is a string. Only otherwise does the template look for a
`</think>` inside the content and split reasoning out of it. It is then rendered under one
gate:

```jinja
{%- if ((clear_thinking is defined and not clear_thinking) or loop.index0 > ns.last_user_index) and reasoning_content -%}
{{ '<think>' + reasoning_content.strip() +  '</think>'}}
{%- else -%}
{{ '</think>' }}
```

That is the shape of Qwen's gate (a last-user-message window with the keep-history flag
ORed in) with the flag's polarity reversed, as Granite's is: `false` keeps. Because it is a
plain `or`, `false` keeps every past turn's reasoning wherever the finish nudge moves the
boundary. Left unset, every turn before the last user message renders as a bare `</think>`.
The assistant's prose follows the think block rather than replacing it, so the treatment is
additive. Past tool calls render as `<tool_call>name<arg_key>...</arg_key><arg_value>...</arg_value></tool_call>`
by iterating `arguments.items()` (a mapping, which llama.cpp supplies by parsing the wire
format's JSON string first) and tool results as `<tool_response>` blocks after an
`<|observation|>` marker. The tool list is a `<|system|>` block of its own, ahead of the
harness's system prompt.

| arm | `chat_template_kwargs` | `reasoning_content` sent? | what the model is given |
|---|---|---|---|
| OFF | `{"enable_thinking": false, "clear_thinking": false}` | no | the think block closed at the generation prompt. Past turns render `</think>` |
| UNSEEN | `{"enable_thinking": true, "clear_thinking": false}` | no | an open `<think>`. Past turns render `</think>` and no reasoning |
| SEEN | `{"enable_thinking": true, "clear_thinking": false}` | yes | an open `<think>`. Every past turn shows `<think>...</think>` before its prose |

One property of this template needs watching, and was checked: because it falls back to
splitting reasoning out of the *content*, a stray `</think>` left in a reply's content by
the parser would carry reasoning back into an UNSEEN prompt. None of the 430 replies in
GLM's nine smoke runs has one, and gate G4 already fails any run whose content carries an
opening think marker.

---

**What the probe found, and why this section no longer leaves anything open.** Rendering all five
templates directly (`render_arms.py`, feeding the same exchange through each) shows
Gemma, Qwen and Seed-OSS carrying both turns' reasoning into the SEEN prompt, exactly as
intended. It also shows **Magistral and gpt-oss dropping it entirely**: Magistral's template
has no branch for the field, gpt-oss's reads a field of another name, and for both the
UNSEEN and SEEN prompts come out byte-identical.

That was not the verdict, though, because the template is not the whole pipeline: llama.cpp
pre-processes a request before rendering it. `template_probe.sh` asked the live server (
booting each model on its own GGUF and sending one canonical exchange to `/apply-template`
per arm, the same path a real completion takes) and the two cases came out opposite.

**gpt-oss was fine.** llama.cpp does bridge `reasoning_content` into harmony's `thinking`
slot, so the field-name mismatch was not fatal and its primary contrast is real. One
asymmetry is worth registering: harmony renders *either* `content` *or* `thinking` as the
analysis message, never both, so gpt-oss's SEEN arm swaps the prose for the reasoning
rather than adding to it. In practice that costs almost nothing (only 2% of its
tool-calling turns carry any content at all (1 of 65 in the smoke set)) against 45% for
Qwen and 75% for Seed-OSS, both of which preserve it correctly.

**Magistral was not**, in the way described in its section above, and is now fixed by
replaying inline instead: verified against the live server after the fix: its SEEN prompt
came back 174 characters *longer* than UNSEEN, with both thoughts present and the
assistant's prose intact, rendering as
`[/INST][THINK]...[/THINK]Starting with the manifest.[TOOL_CALLS]...`.

The final state of the gate across all eight:

| model | UNSEEN -> SEEN | verdict |
|---|---|---|
| Gemma-4-31B-it | +202 chars | additive, prose intact |
| Qwen3.6-27B | +144 chars | additive, prose intact |
| Seed-OSS-36B | +196 chars | additive, prose intact |
| Magistral-Small-2509 *(retired, v2.5.9)* | +174 chars | additive, prose intact (inline replay) |
| gpt-oss-20b | +102 chars | real, but **substitutes** prose for reasoning: registered asymmetry |
| GLM-4.7-Flash *(v2.5.0)* | +158 chars | additive, prose intact (1,119 -> 1,277, the offline render agrees) |
| Qwen3.6-35B-A3B *(v2.5.4)* | +144 chars | additive, prose intact. All three prompts byte-identical to the 27B's |
| Gemma-4-26B-A4B-it *(v2.5.4)* | +202 chars | additive, prose intact. All three prompts byte-identical to the 31B's |
| Muse Glimmer 30B *(v2.5.20)* | +232 chars | additive. Its template renders a tool-call turn's prose in neither arm |

There is a methodological lesson in how nearly this was missed, and it belongs in the
paper. The first version of this gate asked only whether the two prompts were
byte-identical. Magistral's differ (by having the model's own prose deleted) so the gate
printed *"the treatment is real"* directly beneath its own line reporting that the
reasoning was absent. **A gate that can pass a negative treatment is worse than no gate.**
It now requires three things together: the reasoning is in the SEEN prompt, it is not in
the UNSEEN prompt, and the assistant's own prose has not silently disappeared between them.

That third condition took two attempts to write correctly, which is its own small lesson.
The first version diffed the two prompts by line: and these prompts are close to one
continuous line, so an inserted thought reads as a removed line plus an added one, and
three of the five models were reported as having lost content when none had. The check now
tests for the specific strings that Magistral actually lost, by name. A gate whose failures
are mostly false is a gate that gets ignored, which is the same disease as a gate that
cannot fail at all.

**This is a freeze gate.** No model runs its grid until its UNSEEN and SEEN prompts are
shown to differ *in the right direction*.

```bash
cd /mnt/d/eval-coding-agent
./template_probe.sh gemma-q4 qwen-q4 seed-q4 gptoss-20b glm-q4 qwen-moe-q4 gemma-moe-q4 muse-q4xl   # v2.5.20: the eight in the grid
```

### 4.3 The frozen serving settings (llama-server)

| flag | value | why / what it means |
|---|---|---|
| build | llama.cpp **b10964**, Windows CUDA 13.3 build (commit hash as printed by `llama-server --version`) **plus the CUDA 13.3 runtime DLLs** (`cudart64_13.dll`, `cublas64_13.dll`, `cublasLt64_13.dll`, from the release's separate `cudart-...` zip) placed beside `llama-server.exe` | pinned. The build number and commit are recorded in every run's `serving_probe`. The DLLs are part of the pin, not an installation detail: without them the CUDA backend plugin fails to load and the server **silently runs on the CPU**, it still answers `/health` and `/props`, just 10-30x slower. `llama-server.exe --list-devices` must list `CUDA0`, and the run wrapper refuses to start a run unless **GPU memory actually grows** by at least half the model file's size once the server reports healthy (checked with `nvidia-smi`, b10964's log format prints no backend/offload lines, so the log cannot be used for this, and the server's own `/health` is happy either way). Pre-built binaries are published only as these numbered builds (the semantic version tags (v0.4.x) are source-only) so the numbered build is the correct artifact. Keep the build zip, the cudart zip and their sha256s with the study materials |
| `-m` + `--alias` | the registry-hashed GGUF. Alias = the model name the agent asks for | the server is asked at every boot (`/props`) to confirm it is serving that exact file. Mismatch aborts the run |
| `-c` (context window) | **per model**, see below | how much conversation the model can hold before it dies of overflow |
| `-np 1` | one request at a time | no other request shares the GPU or the cache with a study run |
| `-ngl 999` | all layers on the GPU | no CPU offload. Speed and numerics identical run to run |
| `-fa on` | flash attention | pinned so attention kernels don't differ between runs |
| `-b 2048` | prompt-processing batch size | throughput knob, pinned |
| `--cache-type-k f16`, `--cache-type-v f16` | KV cache kept at 16-bit | the cache is *not* quantized: precision is not a hidden second variable |
| `--jinja` | use the model's own chat template | required for tool calling and for the thinking tags to be parsed at all |
| `--seed 0` | server-side sampler seed | was moot under greedy decoding and is not any more (section 4.4.1). The server flag is pinned. The value that matters is the **per-request** seed, which is varied per replicate and recorded per run, because the twenty replicates of one cell are twenty observations only if they are twenty draws. *v2.5.11: not in the blind layout, as the wrapper stands.* It derives the seed from the run id's replicate digits before the blind layout replaces the id, and the id it has at that point is the schedule label, so the arithmetic fails, an error is printed, and the run is sent with no seed, the server's pinned `--seed 0` then applies to every request. Replicates would still differ, because each run's prompt carries its own random workspace path, but not as registered here. To be fixed before the grid. *v2.5.12: fixed.* In the blind layout the wrapper now takes the replicate from the label's trailing `r<NN>` and refuses a blind run whose label yields none. A classic id that is not `<arm digit><NN>` runs unseeded, as before, but says so |
| `--host 0.0.0.0 --port 7777` | serving address | the wrapper refuses to start if anything already answers on 7777 |

Context window per model: *v2.5.32: every model now runs at its native
window where the card can hold its cache, otherwise at the largest round
window that fits (see the history entry). The rule below, and the
provisional values, are kept as the record of how the windows were first
set.* Until v2.5.32 the rule was *the smallest window that produces
zero overflow deaths in that model's smoke runs*, recorded per run, with
overflow deaths still counted as outcomes (section 10) if they happen anyway.
Provisional values, set from each model's documented context and how
verbosely it reasons, confirmed or raised at the smokes. *(v2.5.30)* A model's **native
window** is the longest context its file declares (`context_length` in the GGUF header): the
most the server can be given without extending the model's position encoding, which this
study never does. Read from the study's own files: Gemma-4-31B, Gemma-4-26B-A4B, Qwen3.6-27B
and Qwen3.6-35B-A3B 262,144. Seed-OSS 524,288. GLM-4.7-Flash 202,752. Gpt-oss-20b and Muse
Glimmer 131,072. gpt-oss, GLM and Muse run at their native window, so theirs cannot be raised
if they overflow. Every other window has room to spare. The protocol's section 3.1 table carries
both columns.

| model | `-c` (provisional) | basis |
|---|---|---|
| Gemma-4-31B | 65,536 | moderate reasoning length. Raise only if a smoke overflows. *v2.5.32:* kept, its native 262,144 would need ~236 GB of cache with `--swa-full`. The card holds ~89,000 tokens |
| Qwen3.6-27B | **262,144** *(v2.5.32)* | its native window (131,072 until v2.5.32). ~17 GB of cache |
| Seed-OSS-36B | **262,144** *(v2.5.32)* | the most that fits (131,072 until v2.5.32). Its native 524,288 would need ~137 GB of cache |
| Magistral-Small-2509 *(retired, v2.5.9)* | 65,536 | 128k window, but Mistral warns quality degrades past ~40k: flagged, not fixed |
| gpt-oss-20b | 131,072 | small model, verbose reasoning. The window is cheap |
| GLM-4.7-Flash | **202,752** *(v2.5.29)* | its native window (GGUF header). 131,072 until v2.5.29, when its kanban/execution SEEN run in the 2026-10-01 smoke outgrew it (a 132,135-token request). Its nine earlier smokes peaked at 50,683 tokens |
| Qwen3.6-35B-A3B *(twin, v2.5.4)* | **262,144** *(v2.5.32)* | its native window (131,072, the 27B's, until v2.5.32). Its nine smokes peaked at 69,284 tokens |
| Muse Glimmer 30B *(v2.5.20)* | 131,072 | its native window, so the most it can be given (`context_length` 131,072 in its GGUF header, v2.5.30 corrects "262,144 at most", which the file does not declare). Its six pilot runs had no overflow |
| Gemma-4-26B-A4B *(twin, v2.5.4)* | **262,144** *(v2.5.32)* | its native window. 131,072 from v2.5.4 (raised from the 31B's 65,536, which its first smoke filled once) until its OFF kanban/execution run in the 2026-10-03 smoke outgrew it at step 196. ~59 GB of cache with `--swa-full` |


**Server logging is fixed at `-lv 5`** *(v2.5.27, until then it was fixed at the
default, 3, with higher levels a diagnostic only)*. llama-server's `-lv` takes 0 generic,
1 error, 2 warning, 3 info (its default), and 4 and 5 for trace and debug. At 5 every run's
`llama-server.log` keeps, for each request, the prompt the server rendered from the chat
template and the model's raw output before parsing. Each run therefore records for itself
that its arm reached the template, and an output the parser rejected (gpt-oss's malformed
harmony headers, say) is kept whole rather than as the parser's one-line warning.

The flag is part of `FROZEN_FLAGS`, last, so every study run's banner reads
`... --port 7777 -lv 5`, and gate G17 checks the banner against the whole frozen set. A run
at another level is a diagnostic: `SERVER_VERBOSITY=<digit>` replaces the 5, stamps
`[DIAGNOSTIC]` and the level into the log, and fails G17:

```bash
SERVER_VERBOSITY=3 OUTPUT_ROOT=/tmp/runs/probe ./run_one_with_server.sh gemma-q4 message-board execution 901
```

The cost is volume, because the rendered prompt is the *entire conversation so far*,
re-logged on every step. The certifying smoke of 2026-10-07 (v2.5.41) wrote 1.69 GB of server
logs for its 66 runs (median 16.8 MB a run, the largest 102 MB), which puts the 2,640-run grid at
about 70 GB. `zstd -19` shrinks a log about 19-fold (measured on the 2026-10-04 set: 1.87 GB, failed attempts included,
to 98 MB), so about 4 GB compressed for the archive. The batch pauses below 20 GB free, so finished runs are moved off between batches.

The prompt probe stays the instrument for checking a template before any run is made:
`template_probe.sh` is the better instrument regardless of cost. `/apply-template` returns
the rendered prompt directly, per arm, in seconds, with nothing to grep and no dependence
on which llama.cpp build logs what (section 4.2.2).

### 4.4 The frozen agent settings (harness)

| setting | value | what it does |
|---|---|---|
| decoding | **per model, per thinking mode: see section 4.4.1.** Max 32,768 tokens per reply stays global (a harness guard, not a sampler) | until v2.4.0 this was one global greedy setting. It is now each vendor's documented sampling for that model, identical across that model's thinking arms. Every sampler is pinned explicitly, including the ones set to off |
| thinking switch | Set by `ARM=off\|unseen\|seen` in the run wrapper, never typed by hand. The wrapper derives the request body, the replay flag and the preamble key together and refuses to run if any is also set by hand. ON (both thinking arms): `enable_thinking: true` for Gemma, Qwen and GLM (each also sending its keep-history flag, in every arm, section 4.2.2), the template default for Seed-OSS, reasoning effort `medium` for gpt-oss, reasoning strength `high` for Muse Glimmer (v2.5.20), and the registered thinking preamble for Magistral (retired in v2.5.9). OFF: `enable_thinking: false` (Gemma, Qwen, GLM), `thinking_budget: 0` (Seed-OSS, pending section 4.2.1), no preamble (Magistral). Gpt-oss and Muse Glimmer have no off-switch and run two arms | the two thinking arms are byte-identical in request body *and* system prompt and differ only in replay, so the primary contrast varies nothing but what the model can see. The OFF arm is real only if its canaries pass the length rule in section 9: presence of a reasoning field is not the test, because a template can emit a fixed stub while the model is not thinking. A run whose recorded thinking state contradicts its arm is void |
| visibility switch | `REPLAY_REASONING=1` (SEEN) / `0` (UNSEEN) / `0` (OFF) | recorded per run as `reasoning_replayed`, with counts of replayed turns and characters. OFF is set to 0 explicitly rather than left at the harness default: there is no reasoning in that arm, so replay is a no-op for a well-behaved template but *not* for one that emits boilerplate in the reasoning field, replaying Seed-OSS's budget-reflect stub silenced the model on 55% of its turns (section 4.2.1) |
| loop guard: `MAX_SAME_CALLS` | 500 | abort if the *identical* tool call is made this many times: deliberately loose so the loop measure below does the work |
| loop guard: `MAX_CYCLE_REPEATS` | 3 | abort on an A-B-A-B alternation repeated this many times |
| loop guard: `MAX_BLOCKED_CALLS` | 3 | abort after this many calls the harness itself refused |
| loop guard: `MAX_REPEAT_STEPS` | 30 | abort after 30 consecutive steps in which every call merely repeats one already made: **this is the "stuck in a loop" definition**. The measure is tied to these four numbers, and a run made under any other guard values is void |
| `MAX_STEPS` | 10,000 | effectively no step cap: the guards and the token budget are what end runs, never a step count |
| file-state note *(v2.5.13)* | on, in every arm and condition: a `write_file` or `edit_file` call that leaves a file with exactly the bytes an earlier write or edit call of the run left it with gets one more line in its result, `NOTE: 4 write or edit calls in this run, this one included, have left client/index.html with exactly this content; the previous one was 2 calls ago.` The calls ago count every tool call made since, of any kind. An edit that failed counts for nothing. An identical-string edit, which leaves the file as it was, counts | a fact about the model's own calls and the file's bytes, never about whether the content is right, so it adds no verification surface. It sits beside the no-op and stale-process notes the file tools already carry (`CONDITIONS-CHANGES.md`). It describes an outcome, not a pattern of calls (calls that merely alternate are not flagged) and it ends nothing: the four loop guards above are unchanged. Counted per run in `file_state_repeats` (section 10, tenth) |
| finish nudge *(v2.5.14)* | after every turn without a tool call, the same `role: user` message: `You did not call any tool. If the task is complete, call the finish tool now; otherwise continue working using the provided tools.` A run ends as `stopped_no_tool_call` only when the reply to a nudge has no tool call either. A truncated or runaway reply ends it at once, un-nudged | protocol scaffolding, identical in every arm and condition. Until v2.5.14 it was given once per run and the second such turn ended the run wherever it fell. Recorded per run as `finish_nudges` and `finish_nudge_steps` (section 10, fourth and sixth) |
| client timeout per model reply | **3,600 s** (harness default since 2026-09-18, was 600 s) | replies are not streamed, so a reply of the full 32,768 tokens takes longer than 10 minutes at local generation speeds: the old default would have cut the longest *thinking* replies and retried them, a bias against the thinking arms. The smokes' longest step durations confirm the margin. **The margin is coupled to the per-reply cap (v2.4.4):** a full 32,768-token reply took 851 s on Granite, under a quarter of this. At 98,304 the same reply needs ~3,720 s and cannot fit, and a timed-out call is retried from scratch rather than failed: so raising the cap without raising this would bring the bias back, silently (section 4.4.1). Since v2.5.8 every retry is recorded in the manifest (`api_retries`), and G16 fails any smoke set that contains a timeout retry (section 9) |
| `MAX_TOTAL_TOKENS` | **20,000,000** per run, set by the run wrapper (8,000,000 until 2026-09-23, 12,000,000 until 2026-09-26) | the budget. Exhausting it ends the run with status `token_budget_exhausted`, counted as a non-completion. Raised from 8M when vendor sampling (section 4.4.1) made Granite run far longer than it had greedy: three of its nine smoke runs hit the 8M ceiling, peaking at 8,051,137, and its UNSEEN arm went from 3/3 finished at 224 steps to 2/3 budget-exhausted at 337. The raise changes nothing for any other model, and that is measured rather than assumed: across the 51-run set of 2026-09-23 the heaviest non-Granite run used **2,719,615** tokens (34% of the old cap, 23% of the new) and the median run used **148,789**, so the cap was causally inert for every model but Granite at 8M and remains so at 12M. Set in `run_one_with_server.sh`, **not** left to `run.sh`'s own default. Every run records the value it was made with. **one number for the whole study**, which is why G10 fails a set that spans the change: a mixed smoke set is tolerable during a transition, a mixed grid is not. *v2.5.12:* raised to 20M at the study lead's decision on G9, after a GLM-4.7-Flash SEEN smoke run under the reinstated briefing exhausted 12M (12,008,378), a run cycling through starting its server, probing its port and starting it again, which the raise may only let run longer. For every other model the cap stays inert: the heaviest of their runs in the two latest smoke sets used 4,780,566 tokens, 24% of it. *v2.5.14:* the same GLM slot exhausted 20M too, in a counting loop (section 4.1). The budget stays, a run that reaches it while looping is an outcome, and G9 waives it (section 9). The heaviest run that finished in the 20M set used 6,198,109 tokens, 31% of the budget |
| briefing | `universal` @ `c988f43155c49538` *(v2.5.6, `02f244a9339a0cb6` before it, and again in v2.5.9 alone, reinstated in v2.5.10, pending the all-model smoke, section 4.1)* | one instruction text, byte-identical in every condition and arm. v2.5.6 adds one sentence saying what execution tools act on (section 4.1) |
| workspace | `--clean-workspace`, fresh per run. Headless browser. `INTERACTIVE=0` | no human ever types into a study run |
| toolchain | one Node version pinned with nvm (`nvm alias default`) and one npm version for the whole study, fixed at the smokes. Recorded per run in `environment.txt` beside the logs, with the engine build and GPU driver | the agent runs `npm install` / `npm run dev` and reads their output, so Node/npm are part of what it sees. Dependency resolution is frozen at the freeze date with npm's `before` config in the WSL user's `~/.npmrc` (e.g. `before=2026-09-22T00:00:00Z`): every install on the machine (the agent's, the harness's post-run install for `no_verification`, and any later rebuild for grading) resolves each range to the newest version published before that date, transitive dependencies included. The task text is deliberately *not* changed to demand exact version pins: models would have to guess versions (impossible to check in `no_verification`), adding a failure mode unrelated to the treatment. The `before` date is recorded per run in `environment.txt`. Each run's `package-lock.json` is archived with the run |
| provenance in every manifest | quant label + registry entry with sha256, serving probe (build, file, `n_ctx`), `extra_body` verbatim, `loop_guards`, `reasoning_replayed`, `harness_git`, task and prompt hashes, and since v2.5.8 `api_retries`: every retried model call, and why | the audit trail: any run whose recorded settings differ from this table is void, mechanically |

#### 4.4.1 Decoding: per model, per thinking mode

Until v2.4.0 every run was served at temperature 0, top_p 1 and top_k 1: one
global greedy configuration, chosen to minimise variance unrelated to the
condition under test. That reasoning is sound in general and was wrong here, for
three reasons that only became visible once there were smoke runs to read.

**It ran reasoning-tuned models at an operating point none of their makers
documents.** Every model in the roster has published sampling settings, none of
them greedy, and at least one card warns outright that reasoning quality is
"affected sensitively by sampling parameters". A result obtained at temperature
0 is a result about a configuration nobody deploys.

**The smoke set's failure profile is the greedy failure profile.**
`stuck_looping`, `truncated_no_tool_call`, `stopped_no_tool_call`, empty turns,
Granite's OFF arm running 156 steps and looping, Magistral's OFF arm going
silent: degenerate repetition and premature termination are what temperature 0
does to models trained to sample. And the failure is *absorbing*: at temperature
0 a model that enters a repetition loop has no mechanism to leave it, because
the next token is a deterministic function of a context it has just filled with
its own repetition. Those losses censor runs rather than adding variance, and
censoring is the worse enemy of power: variance averages down, a dead run does
not. A run that loops in OFF and loops in SEEN yields no signal at all.

**And it made the replicate budget inert.** With greedy decoding and no seed
variation, sixteen replicates of a cell cannot differ except through
uncontrolled numerical noise (GPU arithmetic, batch composition, cache reuse) 
which is variance nobody chose, nobody can size, and nobody can report. Greedy
decoding does not remove variance. It removes the variance you selected and
leaves the variance you did not.

**Why per-model settings are sound here.** Every contrast in this study is
climbed *inside* one model: OFF -> UNSEEN -> SEEN is a within-model ladder.
Decoding varying between models is therefore not a confound for anything the
study claims, provided it is constant across a model's arms. Cross-model
comparison was already descriptive rather than inferential (the models differ
in size, architecture, quantisation and chat template) and temperature is the
least of those differences.

**The registry.** Each model runs at its vendor's documented settings, per
thinking mode. Values are quoted from the sources below and fingerprinted like
the quant and the template:

| model | mode | temperature | top_p | top_k | other | source |
|---|---|---|---|---|---|---|
| gemma-4-31B-it | both | 1.0 | 0.95 | 64 | n/a | ["standardized sampling configuration across all use cases"](https://ollama.com/library/gemma4:31b), [model card](https://build.nvidia.com/google/gemma-4-31b-it/modelcard) |
| Qwen3.6-27B | thinking (UNSEEN, SEEN) | **0.6** | 0.95 | 20 | min_p 0.0, presence_penalty 0.0 | [card, "precise coding tasks"](https://huggingface.co/Qwen/Qwen3.6-27B) |
| Qwen3.6-27B | non-thinking (OFF) | **0.7** | **0.80** | 20 | min_p 0.0, **presence_penalty 1.5** | [card, instruct mode](https://huggingface.co/Qwen/Qwen3.6-27B) |
| Seed-OSS-36B-Instruct | both | 1.1 | 0.95 | off | n/a | [card](https://huggingface.co/ByteDance-Seed/Seed-OSS-36B-Instruct) |
| Magistral-Small-2509 *(retired, v2.5.9)* | both | 0.7 | 0.95 | off | n/a | ["Please make sure to use: top_p: 0.95, temperature: 0.7"](https://huggingface.co/mistralai/Magistral-Small-2509) |
| gpt-oss-20b | thinking only | 1.0 | 1.0 | off | n/a | [OpenAI: "the recommended sampling parameters are temp = 1.0 and top_p = 1"](https://huggingface.co/openai/gpt-oss-120b/discussions/21) |
| granite-4.2-30b *(standby)* | both | 1.0 | 0.95 | off | n/a | ["across all tasks and serving backends, including general chat, reasoning, and tool calling"](https://huggingface.co/ibm-granite/granite-4.2-30b) |
| nemotron-3-nano-30b-a3b *(retired, v2.5.1)* | both | 0.6 | 0.95 | off | OFF arm: registered deviation from the card's greedy (below) | ["temperature=0.6 and top_p=0.95 are recommended for tool calling"](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16) |
| glm-4.7-flash *(roster, v2.5.0)* | both | 0.7 | 1.0 | off | the vendor's agentic-coding evaluation profile (below) | [card, settings for Terminal-Bench and SWE-bench Verified](https://huggingface.co/zai-org/GLM-4.7-Flash) |
| qwen3.6-35b-a3b *(grid twin, v2.5.5)* | thinking (UNSEEN, SEEN) | **0.6** | 0.95 | 20 | min_p 0.0, presence_penalty 0.0 | [card, "precise coding"](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) |
| qwen3.6-35b-a3b *(grid twin, v2.5.5)* | non-thinking (OFF) | **0.7** | **0.80** | 20 | min_p 0.0, **presence_penalty 1.5** | [card, instruct mode](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) |
| gemma-4-26b-a4b *(grid twin, v2.5.5)* | both | 1.0 | 0.95 | 64 | n/a | [card](https://huggingface.co/google/gemma-4-26B-A4B-it) |
| muse-glimmer-30b *(v2.5.20)* | thinking only | 1.0 | 0.95 | 64 | min_p 0.0, presence_penalty 0.0 | [Meta's card](https://huggingface.co/meta-models/Muse-Glimmer-30B), [unsloth's guide](https://unsloth.ai/docs/models/muse-glimmer) |

Qwen's thinking row takes the card's **precise-coding** profile rather than its
general one (temperature 1.0), because the tasks are coding.

**Only Qwen splits by mode, and the split is registered as a limitation.**
Gemma states one configuration for all use cases. Granite states explicitly that
the same values apply whether `enable_thinking` is true or false. Seed documents
no budget-specific split. Magistral documents no non-thinking mode at all, and
gpt-oss and Muse Glimmer have no OFF arm. So per-mode vendor settings change exactly one cell's
samplers in the entire grid (Qwen's OFF arm) and the consequence is confined
to that model. *v2.5.2:* Qwen3.6-35B-A3B, proposed as the 27B's mixture-of-experts twin
(section 5), would carry the same split (its card gives the same precise-coding and instruct
values) so if it enters the grid the split covers two models, both Qwen, and the caveat
below applies to both. *v2.5.5:* it has entered the grid, so the split covers both Qwens.

That consequence must be stated rather than buried. Qwen's OFF -> UNSEEN contrast
now varies **two** things: whether the model thinks, and how it is sampled. Those
are perfectly collinear, so no analysis can separate them, and Qwen's generation
contrast is therefore an **effectiveness** comparison (thinking mode as
deployed against non-thinking mode as deployed, each run as its vendor intends) 
not an isolation of thinking. It is a legitimate question and a different one,
and it is labelled as such wherever Qwen's OFF arm appears. Note in particular
that the non-thinking profile carries `presence_penalty: 1.5` against 0.0 in the
thinking profile: that is a strong anti-repetition intervention, and `stuck_looping`
is one of this study's own terminal statuses, so Qwen's OFF arm is expected to
look less loopy partly by construction.

**Nemotron's card does split by mode, and the split is declined as a registered
deviation (v2.4.4).** It gives three profiles: *"temperature=1.0 and top_p=1.0 are
recommended for reasoning tasks"*, *"temperature=0.6 and top_p=0.95 are recommended for
tool calling"*, and *"Use Greedy Search for reasoning off"*. Every step of this study is
a tool call, so the tool-calling profile is used in both modes: the same
task-over-general choice Qwen's row makes. For the OFF arm that departs from the card,
which says greedy, and the departure is deliberate: greedy is the operating point v2.4.0
abandoned, and a greedy OFF beside sampled thinking arms would make Nemotron a second
model whose generation contrast varies decoding as well as thinking. With one profile,
Qwen stays the only split in the roster. *v2.5.0:* the OFF arm this paragraph is about is
the one Nemotron turned out unable to run, in 11 of 15 OFF runs it abandoned tool calls at
step 1 (section 5). Greedy is the one documented setting for that mode this study has not tried.
Using it would bring back the decoding-and-thinking collinearity this paragraph declined.

**GLM-4.7-Flash takes its vendor's agentic-coding profile, and it is not a split
(v2.4.5).** Z.ai's card gives a default for most tasks, temperature 1.0 and top_p 0.95,
and the settings it used for its own agentic-coding evaluations, Terminal-Bench and
SWE-bench Verified: 0.7 and 1.0. Those are the benchmarks nearest this study's tasks, so
0.7 / 1.0 is used: the task-over-general choice Qwen's and Nemotron's rows make, and not
the case Seed's row rejects, whose alternative was tuned to Taubench, a customer-service
benchmark. No mode split is documented, so OFF uses the same values and Qwen remains the
only split. `min_p` is pinned at 0.0 because Z.ai sets none. Unsloth's suggested 0.01 for
llama.cpp is advice about the engine's default, not the vendor's setting. One more source
of defaults exists for this file, and it is overridden rather than trusted: the GGUF header
carries `general.sampling.temp` 1.0 and `general.sampling.top_p` 0.95 (the card's general
default) which an engine may apply to a request that omits them. Every GLM request sets
both explicitly, and G15 checks what each run recorded.

**The primary contrast is untouched, for every model including Qwen.** UNSEEN
and SEEN are both thinking mode at identical settings, so the persistence
contrast (the one this study is actually about) varies nothing but what the
model can see.

**Four operational rules follow, and each of them was a live bug before it was a
rule.**

*Every sampler is pinned explicitly, including the ones set to off.* At top_k 1
nothing else could matter: only one token was ever eligible. Leave greedy and
every other sampler wakes up, including llama.cpp's own defaults for anything the
request omits. "Unspecified by the vendor" must therefore be written as an
explicit off value, never left absent.

*The server's defaults are recorded.* `/props` exposes them under
`default_generation_settings`, which the per-run serving probe already queries
and did not previously read. It is captured per run, so what the engine would
have applied is on the record beside what the request asked for.

*These are request-body fields, not llama-server startup flags.* Startup flags
set server-wide defaults for requests that omit a value. The study's values vary
by arm, so they belong in the per-request payload, where they are also what the
manifest records. `FROZEN_FLAGS` sets no sampler and should not start to.

*Temperature and top_p cannot travel in `EXTRA_BODY`.* The client writes them
after the extra-body spread, so a value passed there is silently ignored: the
harness refuses them for this reason, with the note that the operator "believes
they changed a treatment and did not. That is worse than a crash." `EXTRA_BODY`
therefore carries **only** `chat_template_kwargs` (the template switch, which is
the treatment) and every sampler is a first-class flag landing in the recorded
`decoding` block. This also repairs a gap: `top_k: 1` used to ride in
`EXTRA_BODY`, so the single most consequential sampler in the old configuration
never appeared in the decoding record at all.

**Seed.** Varied per replicate and recorded per run. Under greedy it was inert,
which is why the old section 4.3 called it moot. It is the mechanism that makes twenty
replicates twenty observations rather than twenty attempts at one trajectory.

**What this costs, and the prediction that tests it.** Sampling widens
within-cell variance, so some of the power that greedy decoding bought is given
back: offset, by an unknown amount, by runs that no longer die in absorbing
loops. The smoke set must be regenerated, and the comparison against the
2026-09-23 greedy set is the test: if greedy decoding was causing the
pathologies, `stuck_looping`, `truncated_no_tool_call` and empty turns should
fall materially, and Granite's SEEN arm (3 of 3 dead under greedy) is the
sharpest place to look. If they do not move, the models simply behave that way
and the power argument for greedy regains its force. That comparison is recorded
here either way.

**What it returned (2026-09-23, 51 runs).** Not confirmed.

The sharpest test refutes it outright. Granite's SEEN arm is **identical** across the two
sets (31 steps, 3 no-tool turns, 3 empty turns, 3 of 3 `truncated_no_tool_call`) under
greedy decoding and under temperature 1.0 / top_p 0.95 alike. Same failure, entirely
different sampler. Elsewhere the pathologies moved rather than fell: Magistral's SEEN and
UNSEEN each gained a `stopped_no_tool_call` and its UNSEEN reasoning rate fell from 100% to
75%. Gemma's OFF arm gained a `stuck_looping`. So the alternative reading registered above
is the one that holds: the models largely behave that way, and greedy decoding was not
what was killing them.

One clear improvement, and it is the model that was furthest off-label: **gpt-oss** went
6/6 finished from 4/6, its harmony parse void did not recur (0 across 51 runs, against 1 in
6), and its UNSEEN median reasoning rose from 152 to 1,653 characters. Run at OpenAI's
documented temperature 1.0 / top_p 1.0 it stopped emitting malformed channel sequences.

One regression: three **Granite** runs exceeded the 8M budget, peak 8,051,137 at 101%, and
its UNSEEN arm went from 3/3 finished at 224 steps to 2/3 budget-exhausted at 337. Sampling
makes it run substantially longer.

Two caveats on the comparison itself, both recorded rather than argued away. The greedy
archive was not preserved, so this rests on the figures in this changelog and the session
log (terminal statuses, step counts, reasoning rates) not on the runs. And the harness
changed between the two sets as well (`OSError` becoming a tool result, the `write_file`
description), so decoding was never the only difference. The Granite SEEN result survives
both, because it is identical on every measure recorded.

**The consequence for the write-up.** The decoding change keeps its justification (
construct validity, replicates that can actually differ, a seed that means something) and
loses one of the three reasons given for it. That belongs in the paper as stated, not
quietly dropped: a prediction was registered, it was tested, and it failed.

**And the Qwen artifact is now observed rather than anticipated.** In the same set, Qwen's
OFF arm (the one carrying `presence_penalty: 1.5`) finished 3 of 3 across 191 steps with
zero empty turns, while its UNSEEN arm finished 1 of 3 with 5 empty turns and reasoned on
58% of steps. The non-thinking arm outperforms the thinking arm on completion, and the
non-thinking arm is the one with the anti-repetition penalty. This is exactly the effect
registered when the mode split was adopted, appearing on the first set of data, and it is
why Qwen's generation contrast is reported as an effectiveness comparison rather than an
isolation of thinking.

**Three decisions this leaves open, all before the freeze.**

1. **The token budget.** 8M was fixed when the heaviest greedy smoke run reached 3.15M.
   Under vendor sampling Granite reaches 8.05M and three runs die on it. Either the budget
   rises, or `token_budget_exhausted` is accepted as an outcome and reported per arm: but
   it cannot stay a gate failure that everyone learns to scroll past.
2. **Whether Granite is fieldable.** Its SEEN arm is dead under two independent decoders.
   It is now registered in all three `EXPECTED_*` tables, so its gates say something about
   the model rather than about the registration. The question of whether a standby whose
   SEEN arm does not work is a standby at all is still open.
3. **Qwen's mode split**, in light of the OFF/UNSEEN gap above.

**A correction to decision 1, found while reading the failures rather than counting
them.** Granite's OFF and UNSEEN arms die on the **per-run** budget: they were still
working at 135-178 steps when the 8M cap stopped them, which is what v2.4.2 addresses. Its
SEEN arm dies on something else entirely: the **per-reply** cap of 32,768 tokens (section 4.4),
which is a different number and is frozen study-wide. Raising `MAX_TOTAL_TOKENS` to 12M
therefore cannot touch the SEEN arm, and Granite should be expected back at 2 arms fixed
and SEEN still 0 of 3.

More importantly, the per-reply cap is not what broke those runs: it is what **rescued**
them. All three hit `completion_tokens` of exactly 32,768 against a `max_tokens` of 32,768,
with prompts of only 7-9k against a 131k context and **zero characters of visible output**.
The reply was 88,845 characters of reasoning: 3,531 lines, 360 of them unique, 90%
repetition, with *"Let me do it."* appearing 768 times and *"Let me read server.js."* 440
times. The model announces the tool call it is about to make, does not make it, and repeats: 
inside one generation. Without the cap it would have generated until the context filled.
Raising it would buy more of the same.

Two things follow that are about the instrument rather than about Granite, and both are
now fixed. `truncated_no_tool_call` was created to stop an infrastructure fault being
scored as a model incapable of tool calling. Here it was doing the reverse, filing a model
pathology as a limit. **`runaway_no_tool_call`** now separates them on the evidence the
code already had (completion at the ceiling means the model spent everything it was
allowed, completion far below it means something upstream cut the reply short) and
`truncation_detected` records `repeat_ratio`, `unique_lines` and the most-repeated line so
the inference is evidenced per run rather than assumed. A very large legitimate file write
also fills its allowance. The repetition ratio is what tells the two apart. On the three
Granite runs it reads 0.898, 0.843 and 0.954. *v2.5.4:* one case falls between the two. A
runaway that meets the context window before the reply cap is filed as a truncation,
because the window, not the cap, ended it: the Gemma twin's first smoke has one (section 5). On a
65,536-token window that can happen to any reply begun with more than 32,768 tokens in
context. Section 4.3's rule, which raises a window that its model's smokes overflow, is what keeps
it rare, and `truncation_detected` still carries the repetition measure that identifies the
run.

And the loop measure has a blind spot worth registering: `MAX_SAME_CALLS`,
`MAX_CYCLE_REPEATS` and `MAX_REPEAT_STEPS` all count **tool calls across steps**, so a
model that loops inside a single reply, emitting no tool calls at all, trips none of them.
That is precisely where a reasoning model is most likely to get stuck, and (on the only
instance observed so far) it happened in the arm that replays reasoning back in. Until
v2.4.3 such a run was counted as a truncation, which understated the loop measure, one of
this study's dependent variables.

**Tested on 2026-09-24, and the test could not be run as designed: which is itself the
finding.** Two things were measured. First, what a runaway reply looks like from the
inside. Granite's `kanban-board`/execution SEEN run in the 12M smoke set (run 301) spent
its 32,768 tokens on a **strict 26-line cycle**: entered 31% of the way in (about 10,100
tokens), repeated about 70 times, and matching at a 26-line offset on 1,804 of 1,804
lines. Its content is not confusion. The model had written `Database` into
`server/index.js` at step 7 (true, per the trace) and correctly names the fix, `PGlite`.
It then alternates between *"let me read the file first"* and *"actually let me just
proceed"* without ever emitting the call. A correct diagnosis that never becomes an
action. A cycle with that period is detectable after two or three repetitions, about
1,400 tokens in, which is one way to close the blind spot registered above. It is not
adopted, because cutting a reply short changes what every arm's replies are allowed to do.

Second, the direct test of *"raising it would buy more of the same"*: the same run id
re-run with `--max-tokens 98304` through the wrapper's diagnostic pass-through, not a
frozen-spec run. It failed as a test, for two reasons that are both about the instrument.
**The cap and the client timeout are coupled.** Calibrated on the runaway above (38.5
tokens/s over the reply, 33.5 by its end), a full 98,304-token reply needs about 3,720 s
against a 3,600 s timeout, so any runaway at that cap is guaranteed to time out: and a
timed-out call is not failed but re-sent, up to five times, with generation restarting
from zero. Observed: one call ran the full 3,600 s, timed out, and its retry came back in
under 30 seconds with a short reply. At that cap the timeout had become a runaway filter
that re-rolls until something short comes back (precisely the bias section 4.4's timeout row
exists to prevent) and **nothing in the manifest records that it happened** (section 9 item 0).
*v2.5.8: it does now*, `api_retries` in every manifest, and gate G16 (section 9).
**And the re-run did not reproduce the original**: same run id, so the same derived
per-request seed, yet by step 10 the re-run was writing `backend/src/api/columns.js` into a
layout the original never created (it had written `server/index.js` at step 7). The cap
also differed, so this does not isolate GPU non-determinism, but it does establish that a
seed is not a replay key (section 10): *v2.5.11:* not across a change of cap. With the prompt
and the seed unchanged, gpt-oss replays exactly (section 10). The per-reply cap therefore stays at 32,768, where it is
doing load-bearing work: it ended Granite's runaway at about 14 minutes with a recorded
`runaway_no_tool_call` instead of letting it run unbounded. The registered prediction
stands **untested rather than confirmed**. The evidence against a larger cap helping is
the cycle itself, which has no exit to reach.

**Decision 2, resolved 2026-09-25: Granite is not fieldable**, section 5 had already recommended
it. Its SEEN arm is 0 of 3 under two decoders, the loop is intrinsic rather than an
artefact of the cap, and had it been brought up it would have been the roster's most
expensive model: 42.5 minutes of model generation per replicate triple (OFF + UNSEEN +
SEEN) in the 12M smoke set, 2.25x Seed-OSS's 18.9 and 48.7% of the whole set's. The standby
slot passes to Nemotron-3-Nano-30B-A3B (section 5), pending its live probe and smoke. *It passed
the probe and was retired after the smoke, in v2.5.1 (section 5). The slot is open.*


Note that `run.sh` on its own defaults to the *smoke* guards (3/3/3/6). The
run wrapper sets the study values above. A run must never be launched with
bare `run.sh` for the study.

### 4.5 Grading an artifact reproducibly (so a second grader lands where the first did)

Grading means copying an app out of its run, installing its dependencies,
starting it and exercising it by hand, through its own interface, with the
rubric card for its task. An app's first grading and its re-grade (or
another grader a year later) must reach the same app, so the procedure is fixed and
mechanised (`grade_setup.sh <blind id>`, since v2.5.18 the script takes the
id and finds the run itself, so the grader never sees the model's folder):

1. **Never install inside the archived workspace.** The harness fingerprints
   the model-authored source tree at the end of every run. A post-hoc
   install would mutate it. The app is copied to a grading work directory
   and the archive stays byte-identical to its manifest.
2. **Same Node.** The run's `environment.txt` records the Node version the
   agent worked with. The grader's must match (the helper stops with the
   `nvm` command otherwise).
3. **A fresh database** *(v2.5.18)*. Before anything is installed, the
   database directory the app shipped with, if any, is removed, with any
   parent it leaves empty, and the removal is logged. Every app then starts
   as a new user would find it, whether or not its agent ran it, and the
   rubric's launch items measure the same thing in every condition.
4. **Same dependency tree, exactly.** If the run contains a
   `package-lock.json` (the agent ran `npm install`: normal in `execution`
   and `interactive`), the grader installs from it with `npm ci`, which
   reproduces the tree byte-for-byte. If it does not (normal in
   `no_verification`, where nothing was ever installed), the *first* grader's
   install produces the lockfile, which is saved beside the run as
   `smoke/logs/grading-lock.json` (outside the fingerprinted workspace) and
   every later grader installs from that with `npm ci`. Because the study's
   npm `before` date is set, even that first install resolves identically on
   any machine. *v2.5.21:* this happens in every folder of the app that has a
   `package.json`, and whether it succeeds is the rubric's first launch item,
   L0. An install that stops on a refused dependency conflict is re-run with
   `--legacy-peer-deps`, and one whose lockfile does not match its `package.json`
   with `npm install` (accommodation A0, added after the 2026-10-09 mock grading), so the rest can be
   graded, and L0 fails all the same. *v2.5.44:* A0 also covers `ETARGET`, an install that stops
   because no version published before the `before` date matches the range a dependency of the
   app's own `package.json` asks for: it is re-run with `npm install --no-save <that
   package>@latest`, which takes that one package at the newest version before the date and
   writes nothing but `node_modules`. The quality contrast is reported a second time with every
   app installed this way scored 0 (protocol section 8.3). *v2.5.45:* A0 also covers an install that
   stops in a lifecycle script of the folder's own `package.json` (`preinstall`, `install`,
   `postinstall`, `prepare`): it is re-run with `--ignore-scripts`.
   *v2.5.47:* at launch, accommodation A8 installs a package that the app's own code imports,
   or its own declared script runs, but no `package.json` of the app declares, when the error
   names it: exactly that package, with `npm install --no-save <name>@latest`. The part fails
   its launch item all the same, and these apps join the scored-0 report of protocol section 8.3.
5. **Same launch and same script:**
   - the launch: `npm run dev` at the project root, which both task specs
     require (task 1.4).
   - if that does not give a working page, the rubric's fixed
     accommodations, for at most 5 minutes, none of which edits a file.
   - then the card's steps in order, at its frozen version.
   - *(v2.5.22)* last, once the score sheet is complete and with the app
     still running, the API probe (`api_probe.py`), whose results are kept
     apart from the score (protocol section 6.5).
6. **The grader's own environment is recorded** (`GRADER-ENV.txt`: Node,
   npm, `before` date, lockfile hash, OS, browser) alongside the grades, the
   same way each run records the agent's.

Consistency is then a property of the grader, not of drift in what was
being graded.

**Who grades what** *(v2.5.25, replaces v2.5.18's two graders)*. One
grader grades the quality sample, and a fifth of it a second time. Before each
tier is graded, a script draws, with a seed fixed at the registration freeze (section 9 item 6), *(v2.5.46)* **the
quality sample**: ten apps of every model x task x condition x arm cell, the only apps graded,
and **the re-grade set**: two of those ten in every cell (a fifth of them, or as near as a
short cell allows). Each drawn app gets a
second blind id, recorded in the un-blinding key beside its first.

The rules that go with the draw:

- **The score of record** is an app's first grading. The re-grade
  measures consistency and nothing else.
- **A 14-day cool-down.** An app's second id goes onto the grader's list
  only once 14 days have passed since its first grading, so re-grades are
  mixed in among first gradings of later apps. The last tier's remaining
  re-grades come after its last first gradings. Nothing on a list marks a
  re-grade. The lists are made by someone other than the grader. If the
  grader also holds the un-blinding key, as the study lead may, the report
  says so as a limitation.
- **Blind.** The grader sees only the blind id: `grade_setup.sh` prints and
  records nothing else. The grader never opens the run's manifest, trace or
  logs, and never looks up an earlier score sheet while grading.
- **A fresh copy every time.** The rubric's script posts messages and
  creates kanban cards, so every grading, a re-grade included, starts from
  a fresh copy.
- **Shuffled order,** so that drift over the weeks cannot follow the arms.
  One grader also means every arm is graded by the same person, so no
  difference between graders can fall unevenly on the arms.

**The consistency bar** *(v2.5.25, proposed, and open for the study lead's
review)*. For each task, an app's two gradings differ by no more than 5
points on average: the mean absolute difference over the re-graded apps, in
a check of at least 24 of them. The intraclass correlation (two-way,
absolute agreement, single measurement) and, per item, Cohen's kappa beside
raw agreement are reported, but they are not the bar, because an intraclass
correlation depends on how much the apps differ from one another:

- with a standard deviation of 30 points in the apps' true scores, an
  intraclass correlation of 0.80 still allows two gradings to differ by
  about 17 points per app on average.
- on a set of near-identical apps, it fails a careful grader.

What one grader cannot show is agreement between people: a misreading
applied consistently passes the bar. The cards' fixed script and pass/fail
criteria carry the scale's objectivity, and the report says so.

**Calibration and consistency checks** *(v2.5.25)*.

1. **Calibration, before the grader freeze.** Every calibration app is first
   copied under a fresh random id, because the smoke ids name the arm.
   - **Training rounds, small at first,** use the certifying smoke's 66 apps, each graded once, then if needed this
     study's earlier smoke apps (no app of another study, v2.5.43). No training
     grading enters the analysis. In each round the grader grades every app, then reads
     back over the score sheets item by item and rewords whatever left a
     call unclear.
   - **No separate deciding round** (v2.5.43). When the training rounds leave
     no call unclear, the cards are frozen and the grader is tagged
     `grader-freeze` (the grader freeze), after the harness's `study-freeze`.
     The ambiguities the rounds settled become the first entries of the
     precedents log, which is hashed with the grader.
   - **The first consistency check is the grid's own**, on its re-grade set,
     against the same bar (item 2 below). The report says the cards were
     frozen before their consistency had been measured.
   - **Grid runs may be made before the grader freeze** (v2.5.25), but no
     grid app is graded or un-blinded before it.
2. **Consistency checks** are made per task, on at least 24 re-graded apps
   of the task: the first as soon as 24 re-grades of a task are in, then
   one when each tier's re-grades are complete.
   - **Changed items.** After every check the grader goes through the items
     that changed between the two gradings. One that shows an ambiguity in
     the cards is settled by a ruling (below). No re-grade changes a score
     of record on its own.
   - **Below the bar.** A task below the bar stops. The other task goes on.
   - **A fresh set.** A fresh set of at least 24 of its apps, spread evenly
     over their cells, is drawn from those first graded at least 14 days
     earlier and not yet re-graded, and is re-graded before any other app
     of that task. Grading resumes once they meet the bar.
   - **No fresh set to be had.** If the fresh set fails too, or too few
     apps are left to draw it, the failure is logged and reported as a
     deviation. How any remaining grading goes on is decided before more of
     that task is graded.
3. **Rulings.** After the grader freeze, a question the cards did not foresee is
   settled by a ruling in the precedents log. The log is `precedents-log.md` in the
   grading results folder (`grading/`), beside the grades and outside the tagged
   grader. Entries are appended, never edited, and committed to git one by one, and
   its state at the registration freeze is hashed with the grader. An item that
   cannot be applied at all is beyond a ruling: it is reported as a deviation, and
   how it is handled is decided before more of its task is graded.
   - **What a ruling may do.** It only says how an item's criterion
     applies. It never adds, removes or reweights an item.
   - **Who makes it.** The grader makes it from the changed items alone,
     without reference to any result by arm.
   - **How it is recorded.** It is dated, logged as a deviation and applied
     to every run.
   - **What it changes.** Every app already graded that the ruling would
     change is re-graded on the affected items, from a fresh copy (for an
     app in the re-grade set, both of its gradings). A tier already
     analysed is reported both before and after the ruling.

   A score sheet, once in, changes only through a ruling.

**Workload.** At the draft cards' rough timings (8 minutes for a
message-board app, 15 for a kanban app):

- **This design** takes 3,168 gradings (2,640 first gradings and 528
  re-grades) about 607 hours, all by one grader (the same total as
  v2.5.18's two graders, who would have shared it).
- **On top of that** come the training rounds, any fresh re-grade sets and any
  re-grades after rulings.

### 4.6 The commands, in order

Everything below runs in WSL from the folder holding the scripts
(`run_one_with_server.sh`, `run_thinking_batch.sh`).
The scripts keep their state next to themselves: `blind-state/` (id ledger
+ un-blinding key) and `batch-state/` (schedules, progress, log). Grading
runs from the grader's own folder, where `grade_setup.sh` lives (section 4.5,
v2.5.18).

**One-time setup, before any smoke run**

```bash
# 1. Pin the toolchain for the whole study
node --version                                  # this is the study's Node
nvm alias default <that version>
npm config set before 2026-09-22T00:00:00Z      # the freeze date: dependency resolution frozen here
npm config get before                           # verify

# 2. Engine build (recorded per run by serving_probe and environment.txt) - and that it
#    actually sees the GPU: the CUDA runtime DLLs must sit beside the .exe (section 4.3)
/mnt/d/tools/llama-b10964-bin-win-cuda-13.3-x64/llama-server.exe --version
/mnt/d/tools/llama-b10964-bin-win-cuda-13.3-x64/llama-server.exe --list-devices   # must list CUDA0

# 3. Model files fingerprinted into the registry (one entry per roster file)
cd /mnt/d/eval-coding-agent && python3 tools/hash_quants.py --help   # then per file, into quant-registry.json

# 4. Marker test per model: boot the server with the wrapper (any arm), then, in a
#    second terminal, prove the reasoning round-trip; must print ACCEPTED. --model-key sends
#    the wrapper's own thinking-arm body (v2.5.0); a bare --model sends none, and every
#    template that clears history by default then reports a false IGNORED
python3 tools/probe_reasoning_replay.py --base-url http://192.168.1.110:7777/v1 --model-key <model-key>
#    The OFF direction is proven by the smokes: an UNSEEN smoke's manifest must show
#    reasoning_replayed=false; an OFF smoke must pass the length canary (section 9 item 2).

# 5. The templates actually served: extract each GGUF's own chat template and check it
#    against the chat_template_sha every run records (section 4.2.2)
cd /mnt/d/thinking_research_runs
python3 gguf_chat_template.py "/mnt/d/llm_models/LM Studio/unsloth/"*/*.gguf --out templates
python3 render_arms.py templates          # what each TEMPLATE does with each arm

# 6. FREEZE GATE - what the SERVER actually renders per arm, pre-processing included.
#    No model runs its grid until its UNSEEN and SEEN prompts are shown to differ.
cd /mnt/d/eval-coding-agent
./template_probe.sh gemma-q4 qwen-q4 seed-q4 gptoss-20b glm-q4 qwen-moe-q4 gemma-moe-q4 muse-q4xl   # v2.5.20: the eight in the grid
```

**Smoke runs** (one per arm per condition, classic layout under `/tmp/runs/smokes/<model>/`)

```bash
# v2.5.14: the certifying smoke under the nudge rule (section 10, sixth): the seven grid models, 60
# runs, made after the commit that takes the rule in (section 9 item 0). Two things first, or a set
# is lost or skipped. Copy the 20M set aside -- D:\thinking_research_runs\smokes to
# smokes-20m-543d0e2 -- since this one is made under the same root, and comparing the two
# (section 10, fifth) needs both; the 12M set was lost this way. And give it its own state
# directory: the batch driver keys its state on the mode and the model list alone, so a set
# in a directory that already has one RESUMES it, skipping every run marked done -- and the
# 20M set was made in the default batch-state/.
STATE_DIR=/mnt/d/eval-coding-agent/batch-state/smoke7-nudge SMOKE_ROOT=/tmp/runs/smokes \
  ./run_thinking_batch.sh smoke gemma-q4 qwen-q4 seed-q4 gptoss-20b glm-q4 qwen-moe-q4 gemma-moe-q4

# v2.5.20: THE certifying smoke -- all eight grid models, 66 runs, made only after the spec
# changes (v2.5.17) and the harness changes (v2.5.19, v2.5.20) are committed, in a state
# directory and a root of its own so that it neither resumes nor overwrites an earlier set.
STATE_DIR=/mnt/d/eval-coding-agent/batch-state/smoke8-certify SMOKE_ROOT=/tmp/runs/smokes-certify \
  ./run_thinking_batch.sh smoke gemma-q4 qwen-q4 seed-q4 gptoss-20b glm-q4 qwen-moe-q4 gemma-moe-q4 muse-q4xl
cd /mnt/d/thinking_research_runs && python3 verify_smokes.py /tmp/runs/smokes-certify --verbose
```

Read the smokes with `probe_report.py`, which reports per run the things the
manifest totals hide: steps, silent turns, reasoning rate, and the
min/median/max of the reasoning field, the last of these being how a template
artifact is told apart from real thinking (section 4.2.1):

```bash
cd /mnt/d/thinking_research_runs && python3 probe_report.py /tmp/runs/smokes
python3 probe_report.py --steps /tmp/runs/smokes/<model>/<task>/<condition>/runs/<id>   # step by step
```

Then: timings, context windows (any overflow?), token budget, the thinking
canaries in both directions, and the grading tools tried on the smoke apps, which are then the training rounds' apps (section 9 item 5, v2.5.43). Fix
settings in this plan, then **freeze**: hash this file and the schedule files
the batch generates
(`sha256sum batch-state/schedule-*.tsv model-reasoning-visibility-study-plan.md`).

**Arm probes** (only when a model's off-switch or on-switch is in doubt, they
bypass `ARM=` deliberately, which is why they set the treatment variables by
hand: no study run may ever do this)

```bash
# Magistral: does the registered preamble make it think, and does llama.cpp put the
# result in reasoning_content rather than leaving [THINK] in the content?
# ANSWERED 2026-09-20: yes for the vendor text, which is now the default (section 4.2.1).
# (Magistral left the grid in v2.5.9; these two lines stay as the record of the probe.)
MAGISTRAL_PREAMBLE=mistral-min ARM=unseen OUTPUT_ROOT=/tmp/runs/probe ./run_one_with_server.sh magistral-q4xl message-board no_verification 291
ARM=unseen OUTPUT_ROOT=/tmp/runs/probe ./run_one_with_server.sh magistral-q4xl message-board no_verification 292

# Seed-OSS: are the silent turns under thinking_budget:0 caused by replaying the stub?
EXTRA_BODY='{"chat_template_kwargs":{"thinking_budget":0},"top_k":1}' REPLAY_REASONING=0 \
  OUTPUT_ROOT=/tmp/runs/probe ./run_one_with_server.sh seed-q4 kanban-board execution 191
```

**Real runs** (blind layout under `/tmp/runs/study/<model>/`, one model at a time)

```bash
REPLICATES=20 ./run_thinking_batch.sh gemma-q4
REPLICATES=20 ./run_thinking_batch.sh qwen-q4
REPLICATES=20 ./run_thinking_batch.sh seed-q4
REPLICATES=20 ./run_thinking_batch.sh gptoss-20b
REPLICATES=20 ./run_thinking_batch.sh glm-q4
REPLICATES=20 ./run_thinking_batch.sh qwen-moe-q4 gemma-moe-q4
REPLICATES=20 ./run_thinking_batch.sh muse-q4xl                # v2.5.20: tier 6
```

*v2.5.15:* the batch driver takes the replicate count from `REPLICATES`, whose default is 16,
so every grid command carries `REPLICATES=20`. The count is part of each schedule's signature,
so re-running a command without it stops instead of running a different grid. Before the
freeze, each grid schedule (`batch-state/schedule-real-*.tsv`) must hold 360 runs: 240 for
gpt-oss and Muse, and 720 for the tier-5 pair, which share one. `touch batch-state/STOP` before a
command writes its schedule and stops before the first run. The smoke command takes no
`REPLICATES`: a smoke is one run per arm per condition whatever the count.

Controls while a batch runs: re-run the same command to **resume** after any
interruption. `touch batch-state/STOP` to stop cleanly after the current
run. When disk is short the batch pauses by itself and resumes once space is
freed. A single run by hand, if ever needed (same wrapper the batch uses):

```bash
ARM=seen   ./run_one_with_server.sh qwen-q4 message-board execution 301      # classic layout
BLIND=1 ARM=off ./run_one_with_server.sh gemma-q4 kanban-board interactive gemma-q4/kanban-board/interactive/off/r03   # blind layout; since v2.5.12 the label is required, and its r03 is the seed
```

**Archiving for disk space** (any time between runs)

```bash
mv /tmp/runs/study/<model> <archive>/study/<model>          # the runs
cp blind-state/blind-ids.txt blind-state/blind-key.jsonl <archive>/   # COPY, never move: the originals feed the next run
```

**Grading** (the grader, on the ids the lists give, every app of the quality sample from a fresh copy, section 4.5)

The full sequence (the list maker's draw and lists, the grader's session setup, each app's
commands, and the merge) is `tasks/rubrics/GRADING-COMMANDS.md`, the same for practice,
calibration and the grid. In short, for each blind id:

```bash
nvm use <the study's Node>                       # the version pinned in section 4.4; grade_setup.sh stops if the run's differs
grade_setup.sh <blind id>                        # finds the run, copies it to ~/grading-work/<id>/app, removes its shipped database, installs, writes a blank score sheet
cd ~/grading-work/<blind id>/app && npm run dev  # task 1.4; then the task's rubric card, step by step
python3 score_sheet.py check <results>/<blind id>.score.json
python3 api_probe.py <task> <backend port> <blind id> --out <results>/probe   # last
```

---

## 5. The models

Eight open-weight models from six labs: one from each, and since v2.5.5 two
mixture-of-experts twins of the Google and Alibaba models. Mistral's Magistral left in v2.5.9
(below, and section 5.1), and Meta's Muse Glimmer joined in v2.5.20: all runnable on the study machine, all served the same way. One quantization (compression level) per
model: the mainstream ~4-bit rung the model's publisher recommends for
deployment, fingerprinted in our registry. Compression level is not varied:
it is not the question, and varying it would multiply the grid.

| model | lab | download (Hugging Face) | file to use | size | thinking switch | notes from the model card |
|---|---|---|---|---|---|---|
| **Gemma-4-31B-it** | Google | `unsloth/gemma-4-31B-it-GGUF` | `Q4_K_M` | 18.3 GB | `enable_thinking` true/false -> **three arms** | dense 31B. A clean on/off toggle |
| **Qwen3.6-27B** | Alibaba | `unsloth/Qwen3.6-27B-GGUF` | `Q4_K_M` (unsloth's own pick is `UD-Q4_K_XL`, 17.6 GB: either, but one, hashed) | 16.8 GB | `enable_thinking` true/false -> **three arms** | strong tool calling. Verbose reasoning. Qwen3.8-27B has since shipped: either version was acceptable, but the choice is fixed before freeze. *v2.5.5:* fixed at Qwen3.6-27B, because its twin is a 3.6 model and a pair must share its generation |
| **Seed-OSS-36B-Instruct** | ByteDance | `unsloth/Seed-OSS-36B-Instruct-GGUF` | `Q4_K_M` (the file actually on the machine and in the registry) | 22 GB | **thinking budget, not `enable_thinking`**: `thinking_budget: 0` suppresses real reasoning but leaves a fixed template stub and silences 55% of turns -> **three arms or two, pending the probe in section 4.2.1** | its own `<seed:think>` / `<seed:tool_call>` tag grammar: a different dialect from the others, and the one that broke the naive canary rule |
| **gpt-oss-20b** | OpenAI | `unsloth/gpt-oss-20b-GGUF` | native `MXFP4` (F16 GGUF 13.8 GB, it ships 4-bit by design) | ~12-14 GB | always-thinking. Effort levels only (low/medium/high), no off -> **two arms**. Effort `medium`, frozen | OpenAI's own format docs expect its reasoning to be **carried along between tool calls**: this model grew up in a SEEN world, so its UNSEEN arm tests it against its upbringing |
| **GLM-4.7-Flash** *(v2.5.0)* | Zhipu (Z.ai) | `unsloth/GLM-4.7-Flash-GGUF` | `Q4_K_M`: only a file re-uploaded on or after 2026-01-21 (the launch files are broken, below) | 18.3 GB | `enable_thinking` true/false, past reasoning kept by `clear_thinking: false` -> **three arms** | mixture-of-experts, ~3B active, MIT-licensed, built for local agentic coding. Run at the card's agentic-coding evaluation settings (section 4.4.1) |
| **Qwen3.6-35B-A3B** *(v2.5.5)* | Alibaba | `unsloth/Qwen3.6-35B-A3B-GGUF` | `UD-Q4_K_M` (unsloth's Dynamic quant, the header records `Q4_K_M`) | 22.1 GB | `enable_thinking` true/false, past reasoning kept by `preserve_thinking`, as for Qwen3.6-27B -> **three arms** | mixture-of-experts twin of Qwen3.6-27B: 35B total, 3B active, 8 of 256 experts plus one shared. The 27B's template, request bodies and sampling by construction (section 5) |
| **Gemma-4-26B-A4B-it** *(v2.5.5)* | Google | `unsloth/gemma-4-26B-A4B-it-GGUF` | `UD-Q4_K_M` (as above) | 16.9 GB | `enable_thinking` true/false, past reasoning kept by `preserve_thinking`, as for Gemma-4-31B -> **three arms** | mixture-of-experts twin of Gemma-4-31B: 25.2B total, 3.8B active, 8 of 128 plus one shared. The 31B's template, bodies and sampling, and its own 131,072-token window (section 4.3) |
| **Muse Glimmer 30B** *(v2.5.20)* | Meta | `unsloth/Muse-Glimmer-30B-GGUF` | `UD-Q4_K_XL` (no plain `Q4_K_M` is published, the header records `Q4_K_M`) | 15.9 GB | reasoning strength low/medium/high/xhigh, no off -> **two arms**. Strength `high`, frozen | dense, ~29.6B with a 1.8B vision encoder not loaded here. Apache 2.0. ATEM format, reasoning as a `to=self` message that its template shows for every past turn with no flag. Meta's sampling 1.0 / 0.95 / 64 |

Every model passes the same gates before entry (section 9): registry fingerprint,
the marker test in both directions, thinking canaries in both directions
under the length rule, and its smoke runs. All eight fingerprints are in the
registry and every smoke resolved its rung with `quantization_detail.status =
ok`, including the twins', whose registry keys are deliberately labelled
`UD-Q4_K_M` even though their GGUF headers record the base type `Q4_K_M`: 
unsloth's Dynamic quants record the base, and a reader should not be left
thinking the twins ran at the same rung as their siblings (Magistral's key, `UD-Q4_K_XL`,
was labelled the same way while it was in the roster, and Muse Glimmer's, `UD-Q4_K_XL`,
is, v2.5.20).

**Architecture is described, not selected on (v2.4.4).** Read from each file's GGUF
header rather than recalled: Gemma-4-31B, Qwen3.6-27B, Seed-OSS-36B, Magistral-Small-2509
and Granite 4.2-30B are dense. Gpt-oss-20b is a mixture-of-experts model routing 4 of 32
experts per token. Nemotron-3-Nano-30B-A3B routes 6 of 128 plus one shared. GLM-4.7-Flash
routes 4 of 64 plus one shared, behind a first layer that is dense (v2.5.0), and the twins
route 8 of 256 plus one shared (Qwen3.6-35B-A3B) and 8 of 128 plus one shared
(Gemma-4-26B-A4B). Muse Glimmer 30B is dense (v2.5.20). The roster (four dense models and two
sparse ones as of v2.5.0, four and four since v2.5.5, three and four since Magistral left in
v2.5.9, four and four again since v2.5.20) is mixed on purpose. Every contrast in
this study is climbed inside one model, so a model's
architecture cannot confound a contrast. The only dense-only rule anywhere in this
project belongs to study 08, where mixture-of-experts routing interacts with the
precision ladder that is that study's treatment. There is no ladder here. What does
carry over is a competence risk at low active-parameter counts (study 08's gate failed
a ~3B-active mixture-of-experts model in the same harness and task suite) and that is
judged per model by the smoke gate, not by architecture: gpt-oss, at ~3.6B active, is
this roster's most reliable smoke performer. *v2.5.5:* reliable at finishing, and the least
active: in the 12M smoke set it ran no command at all in any of its four `execution` and
`interactive` runs (section 10, ninth). *v2.5.7:* it stays in the grid, and the certifying
re-smoke (the first under the v2.5.6 briefing (section 4.1)) is the first reading of whether
knowing it has a live environment changes that. *v2.5.9:* it did (gpt-oss ran commands in 2
of its 4 `execution` and `interactive` runs under that briefing) and those two runs were the
two it lost, on output its server could not parse (section 10, fifth). The briefing is withdrawn
(section 4.1), so the certifying re-smoke reads gpt-oss under the original text again.
*v2.5.10:* reinstated (section 4.1), so the smoke of all seven grid models reads it under the v2.5.6
text once more. Architecture is reported per model and never
tested as a moderator (section 10).

**Magistral left the grid (v2.5.9).** It was put under review in v2.5.7, to be decided on its
first smoke under the v2.5.6 briefing and read on three things: how many of its runs finish,
how many of its turns write a call as text, and whether its `execution` and `interactive`
runs run anything. The re-smoke (2026-09-25, nine runs, briefing sha `c988f43155c49538`)
moved only the third. It ran commands in 3 of its 6 `execution` and `interactive` runs, where
it had run none. But it finished 3 of 9 runs, against 5 of 9 in the 12M set (OFF 0 of 3,
UNSEEN 2 of 3, SEEN 1 of 3) and all six failures ended `stopped_no_tool_call`: each OFF run
at step 2, having described in prose what it meant to do instead of calling a tool. Two SEEN
runs writing their `write_file` calls as text, the opening `[TOOL_CALLS]` token missing
(`toolwrite_file[ARGS]{...}`, four such turns, none in its other arms), and one UNSEEN run
ending at step 16 on a 17,040-character review of its own code. On the study lead's decision
it leaves the grid, and with it 297 runs and about 10 hours: the grid is 1,980 runs and
~129 h, from seven models and five labs, three dense and four mixture-of-experts. The study
loses its only model switched by a system-prompt preamble rather than a template flag and
its only model replayed inline. Section 4.2.1 and section 4.2.2 keep its parts as the record. It is out of
the batch driver, as every retired model is, and stays in the wrapper's model map, the
`EXPECTED_*` tables and the templates folder, so every cited run can be re-made. Its full
record is in section 5.1.

**GLM-4.7-Flash** (Zhipu / Z.ai) **joined the roster in v2.5.0** as its sixth model. It
came from the bench (wired as the second-line standby in v2.4.5) and went through the
same five steps as every model, against the file on this machine:

1. *Hashed.* Unsloth's `GLM-4.7-Flash-Q4_K_M.gguf`, 18,312,339,808 bytes, sha256
   `29837ed2c0fc5f51...`: the value Hugging Face publishes for the re-upload of 2026-01-21.
   Only a re-uploaded file will do: the launch GGUFs looped and produced garbage from a
   llama.cpp expert-scoring bug, since fixed, and this file's header records the corrected
   sigmoid gating. Architecture `deepseek2`, which the pinned b10964 carries.
2. *Template extracted*: `d63ad536c3c81880`, 3,120 chars, the `chat_template_sha` every GLM
   run records from `/props`. Its history gate is the one v2.4.5 quoted from Z.ai's
   published template, unchanged, and `clear_thinking: false` keeps history (section 4.2.2).
3. *Desk-rendered with a nudge*: UNSEEN -> SEEN +158 chars, the prose intact.
4. *Live probe*: +158 chars on the server as well (1,119 -> 1,277), both turns' reasoning in
   SEEN and none in UNSEEN.
5. *Smoked and registered.* Nine runs, one per arm per condition. GLM is now in all three
   `EXPECTED_*` tables of `verify_smokes.py`, and the nine pass all fifteen gates.

Its marker test (section 9 item 3) passed: ACCEPTED on 2026-10-05, with the corrected probe (v2.5.36).

What the smoke shows is a usable model, not a strong one. Six of nine runs finished (OFF
one of three, UNSEEN three of three, SEEN two of three) and the three that did not were all
`stuck_looping`, ended by the `no_progress` guard: two OFF runs and one SEEN. It reasoned on
every thinking-arm step (321 of 321) and on no OFF step, never returned a turn without a
tool call, and kept to its native tool-call format with thinking off: the failure that
sank Nemotron's OFF arm (below) does not occur. It checked its own work in both of its
finished `interactive` runs, with 12 and 40 actions that ran, served or queried the app,
and not at all in its one finished `execution` run. Its reasoning is short, a median of 127
characters per reasoning step in UNSEEN and 122 in SEEN, at the low end of the roster's
range (section 10), and it is cheap: 3.1 minutes per run on average, and a peak context of 50,683
tokens against its 131,072 window. Three runs per arm cannot say more than that, and none
of its apps has been graded yet. The rubric's calibration (section 9 item 5) takes in the apps of
its certifying smoke.

**Two mixture-of-experts twins, Qwen3.6-35B-A3B and Gemma-4-26B-A4B-it, were proposed in
v2.5.2 and joined the grid in v2.5.5, as its fifth tier (section 6).** Each is the mixture-of-experts sibling of a dense roster model from
the same lab (Qwen3.6-27B and Gemma-4-31B) on the same chat-template family with the same
switch names. They were chosen to bring the roster to four dense and four
mixture-of-experts models, and to do it in the one arrangement where architecture can be
read at all: inside a lab. Between labs, architecture travels with everything else that
differs between two models. Inside a pair, the vendor, the template, the switches, the
request bodies and the samplers are shared. So each twin is wired onto its sibling's
settings by construction rather than by copy: the same `THINK_KIND`, so `think_body()`
sends both members of a pair the same bytes. The sibling's context window, and a decoding
entry with the sibling's values, which each vendor's card gives for the twin as well.
*v2.5.4:* one of those has since parted company. The Gemma twin's first smoke overflowed the
31B's 65,536-token window, and section 4.3's rule, which sets every model's window by its own
smokes, raises the twin's to 131,072 (below). The window changes no byte either model is
sent.

| | Qwen pair | Gemma pair |
|---|---|---|
| dense (roster) | Qwen3.6-27B, `Q4_K_M` | Gemma-4-31B-it, `Q4_K_M` |
| mixture-of-experts (grid, v2.5.5) | [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B): 35B total, 3B active, 8 of 256 experts plus one shared | [Gemma-4-26B-A4B-it](https://huggingface.co/google/gemma-4-26B-A4B-it): 25.2B total, 3.8B active, 8 of 128 plus one shared |
| twin's file | [unsloth](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF) `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf`, 22.1 GB | [unsloth](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) `gemma-4-26B-A4B-it-UD-Q4_K_M.gguf`, 16.9 GB |
| wrapper key | `qwen-moe-q4` | `gemma-moe-q4` |
| served template (v2.5.3) | byte-identical to the 27B's, `55d4931433fe502b`: `(preserve_thinking is defined and preserve_thinking is true) or (loop.index0 > ns.last_query_index)` | byte-identical to the 31B's, `aa3185dfc6505104` as served: `(loop.index0 > ns_turn.last_user_idx) or (preserve_thinking and message.get('tool_calls'))` |
| sampling | the 27B's, mode split included | the 31B's, one profile |
| context window (v2.5.4) | the 27B's, 131,072 | 131,072, raised by section 4.3's rule from the 31B's 65,536 |
| licence | Apache 2.0 | Apache 2.0 |

Three things differ inside each pair besides the routing, and the paper will have to say
so. **Active size:** 3B and 3.8B active against 27B and 31B dense, so a within-pair
difference means "mixture-of-experts at about a tenth of the active compute", not routing
alone. **Quantization recipe:** unsloth publishes these mixture-of-experts builds only as
its Dynamic quants, so the twins run `UD-Q4_K_M` against their siblings' plain `Q4_K_M`.
The header records `Q4_K_M` either way, and the twins' registry keys say `UD-Q4_K_M` on
purpose, as Magistral's says `UD-Q4_K_XL`: `hash_quants.py --key` files them that way.
**Capability:** Google's card puts the 26B below the 31B (LiveCodeBench v6 77.1 against
80.0, tau^2 average 68.2 against 76.9). Qwen's card reports 73.4 on SWE-bench Verified and
51.5 on Terminal-Bench 2.0 for the 35B. Neither twin adds a lab: with both, the roster was
eight models from six labs, seven from five since Magistral left (v2.5.9).

**Steps 1-3 are done (v2.5.3), against the files on this machine.** LM Studio saved them
under folders named for the rung (`unsloth/Qwen3.6-35B-A3B-UD/` and
`unsloth/gemma-4-26B-A4B-it-UD/`) and the wrapper's paths say so.

1. *Hashed.* Qwen3.6-35B-A3B: 22,134,528,992 bytes, sha256 `ac0e2c1189e055fa...`.
   Gemma-4-26B-A4B-it: 16,947,541,728 bytes, sha256 `f2c28b3dc4776931...`. Both are the values
   Hugging Face publishes for unsloth's current files, so the downloads are intact and are
   the builds on `main`. Both headers record `Q4_K_M` (file type 15) and unsloth's own
   importance matrix, and both are keyed `UD-Q4_K_M` in the registry. The Qwen header reads
   `qwen35moe`: 40 layers, full attention on every fourth, 256 experts with 8 routed plus a
   shared expert. The Gemma header reads `gemma4`: 30 layers, a 1,024-token sliding window,
   128 experts with 8 routed. Each also carries default samplers (temperature 1.0 and top_p
   0.95, with top_k 20 for Qwen and 64 for Gemma) which the registry's explicit values
   override on every request, as for GLM (section 4.4.1).
2. *Template extracted.* Each is **byte-identical to its dense sibling's**: `55d4931433fe502b`
   (8,057 chars) for the Qwen pair, and `845f1ee48e39fc94` extracted (`aa3185dfc6505104` once
   llama-server strips the trailing newline) for the Gemma pair, the shas every Qwen3.6-27B
   and Gemma-4-31B run records. v2.5.2 asked Gemma's file for `preserve_thinking` and for a
   `Published: 2026-07-09` header line. The second half of that was the wrong test: no GGUF
   template on this machine carries the header line, the 31B's included. The first half is
   what decides it, and it passes: the gate reads `preserve_thinking`, in the very bytes the
   31B's probes and smokes already validated.
3. *Desk-rendered.* The renders are the siblings' own: UNSEEN -> SEEN +144 chars for Qwen
   (1,630 -> 1,774) and +202 for Gemma (645 -> 847), the deltas the siblings' live probes
   measured (section 4.2.2).

**Steps 4 and 5 are done (v2.5.4).**

4. *Probed live* (`template_probe.sh qwen-moe-q4 gemma-moe-q4`). Every prompt the server
   rendered for a twin is **byte-identical** to the one it rendered for the dense sibling (
all six files in `probe-prompts/`) at 1,724 / 1,713 / 1,857 chars for Qwen's OFF, UNSEEN
   and SEEN and 637 / 652 / 854 for Gemma's. Inside each pair the treatment is therefore the
   same bytes: UNSEEN -> SEEN adds +144 and +202 chars, both turns' reasoning is in SEEN and
   none is in UNSEEN, the prose survives, a finish nudge keeps both turns (1,949 and 933
   chars), and past tool-call arguments render in every arm.
5. *Smoked and registered.* Nine runs each on 2026-09-25 at the 12M budget, all eighteen on
   one harness build. Both twins are entered in `verify_smokes.py`'s three `EXPECTED_*`
   tables with their siblings' values: the `enable_thinking` bodies, `field` replay, no
   preamble. **Fourteen of the fifteen gates pass. G2 fails on one step, and the step is not
   thinking** (below).

Their marker tests (section 9 item 3) passed: both ACCEPTED on 2026-10-05, with the corrected
probe (v2.5.36).

The twins beside their siblings, whose figures are their runs in the 12M smoke set: the
same bodies and samplers, an earlier harness build. Three runs per cell describe. They do
not test. A run checked its own work if it started a server, made an HTTP request, ran a
build or test command, or used a browser tool, as in Nemotron's record below.

| nine smoke runs each | Qwen3.6-27B | Qwen3.6-35B-A3B | Gemma-4-31B | Gemma-4-26B-A4B |
|---|---|---|---|---|
| finished, OFF / UNSEEN / SEEN | 3 / 2 / 3 | 3 / **1** / 3 | 3 / 3 / 3 | 3 / **2** / 3 |
| steps | 366 | 456 | 220 | 403 |
| mean wall clock per run | 5.4 min | 4.9 min | 3.0 min | 5.2 min |
| largest context reached (window) | 59,604 (131,072) | 69,284 (131,072) | 20,110 (65,536) | **65,535 (65,536)** |
| UNSEEN steps that reasoned | 57% | 96% | 99% | 80% |
| median reasoning chars per reasoning step, UNSEEN -> SEEN | 170 -> 86 | 241 -> 135 | 552 -> 117 | 493 -> 175 |
| `execution` and `interactive` runs that checked their own work | 5 of 6 | 6 of 6 | 6 of 6 | 6 of 6 |
| UNSEEN turns without a tool call | 3, nothing in either field | 4: three hold a tool call's closing tags, one is a runaway | 1, prose | 3: one a loop that filled the window, two prose |

Both Qwens are weakest in UNSEEN, the shape section 10 registered for the 27B, by different routes.
The Gemma twin needs 1.8 times its sibling's steps, which is why it is the slower of the two
despite a tenth of the active parameters, while the Qwen twin is faster per run than the 27B
on a quarter more steps.

**G2, the OFF canary.** In Gemma-4-26B-A4B's `message-board`/interactive OFF run, step 41
carries 1,288 characters in the reasoning field, and they are not reasoning: a JSON object
whose one key is `summary` (the argument of the `finish` tool) followed by a line reading
`finish`. No call was parsed from the turn, so the harness nudged. At step 42 the model made
the same call properly and the run finished. The twin's other 128 OFF steps carry no
reasoning at all. Read literally, section 9 item 2 fails the arm, and a model whose OFF canary
fails runs two arms. The rule is there to catch a model thinking with thinking switched off,
and this is a tool call in the wrong field, but the grid would give the twin 96 OFF runs in
which to do it again, so it needs a rule rather than a one-off judgement. Two are open:
waive this step on the record, or refine the canary so that a reasoning field whose text is
a tool call (a JSON object whose keys are one tool's parameters, with or without the tool's
name) is counted and reported as a misfiled call instead of as thinking. The second is
mechanical, and the same count would take in the Qwen twin's turns below. **Not yet
decided.** *v2.5.5: decided (the canary is refined.* section 9 item 2 now sets aside a reasoning
field whose whole text is a tool call) the arguments of one of the harness's tools, or
nothing but tool-call markup, and `verify_smokes.py` implements the rule: G2 lists every
field it set aside, and every step that lost a call this way is counted as `callTxt` (section 10,
eighth). On this smoke G2 now passes, with step 41 listed as a `finish` call. The rule moves
two figures in the table above and no others: the Qwen twin's bare closing tags no longer
count as reasoning, so its UNSEEN arm reads 95% and a median of 243 where it read 96% and 241.

**The Qwen twin's lost calls.** Three of its four UNSEEN turns without a tool call have a
reasoning field that ends in the closing tags of a call in Qwen's format (`</parameter>`,
`</function>`, `</tool_call>`, once each) with no opening tag and no `</think>` anywhere in
it. In two of them the tags follow a sentence announcing the call (*"Let me create all the
files."*). The third is the three tags and nothing else. No call was parsed from any of them, so each reached the
harness as a turn without a tool call: two were nudged and recovered, and the third ended
`kanban-board`/interactive as `stopped_no_tool_call`. The fourth ended
`kanban-board`/no_verification as `runaway_no_tool_call`: 32,768 tokens of reasoning in
1,493 lines, 36 of them unique, one repeated 227 times. The trace keeps the server's parsed
reply, not the raw completion, so it cannot say whether the model wrote only the closing
tags or wrote a whole call inside its reasoning that the server's parser consumed in part.
The two readings differ in kind: the first is behaviour, an outcome under section 10. The second
is a parser losing a call, nearer to the harmony-parser fault that voids gpt-oss runs
(section 10): and replaying the recorded request of one of those steps through `/apply-template`
and `/completion`, which return the raw text unparsed, would tell them apart. It has not
been done. *v2.5.37:* it no longer needs doing, at `-lv 5` the server log keeps every
generated token, and in all 9 lost calls of the 2026-10-04 smoke the model wrote only the
closing tags: behaviour. The 27B's three UNSEEN turns without a tool call have another signature: nothing
in either field. *v2.5.5:* `callTxt` now counts the three turns, and the replay is a freeze
item (section 9 item 0). There is one documented fault of this class on the pinned engine. Ling
3.0's template, like Qwen's, pre-opens the thinking block, and on builds before b11057 (
b10964 among them) llama.cpp's parser mishandled Ling's tool calls made before `</think>`,
filing them as reasoning or dropping them
([issue #27462](https://github.com/ggml-org/llama.cpp/issues/27462)). Only a dedicated Ling
parser in a later build fixed it (section 5.1). That does not show the same happens to Qwen's
format. It shows that it can happen on this engine, which is why the replay is worth its few
minutes.

**The Gemma twin's failure, and its window.** Its `kanban-board`/interactive UNSEEN run ended
at step 79 with a reply cut off by the context window: a prompt of 46,793 tokens and 18,743
of reply make 65,536, the 31B's window, which the twin had inherited by construction. The
reply was a loop (1,521 lines, 258 unique, *"I'll update `server/index.js`."* 105 times) 
so it is a runaway that met the window before the 32,768-token reply cap, and the harness,
which tells a runaway from a truncation by whether the cap was reached, files it
`truncated_no_tool_call` (section 4.4.1). Either way it is an overflow death, an outcome under section 10.
But section 4.3 sets each model's window as the smallest that produces no overflow death in its own
smokes, and the twin's transcripts run far longer than its sibling's: its prompts reached
60,087 tokens, where the 31B's never passed 19,047. **So the twin's window is raised to
131,072** (v2.5.4, in the wrapper). Memory is no constraint on the 96 GB card. The
window changes no byte either model is sent, so the pair's bodies stay identical. Its nine
smokes are to be re-made at the new window, in the regenerated smoke set if not before.

**Machine time, and what is not yet decided.** At the smoke's pace the twins would take
about **24 h** and **25 h** for their 288 grid runs each (4.9 and 5.2 minutes per run),
bringing the grid from ~90 h to **~139 h** (5.8 days continuous) and from 1,683 runs to
2,277 with their smokes. Three things are open: whether the twins enter the grid, and if so
as a fifth tier with the within-pair comparison either registered as exploratory or not
made (section 10, seventh). How G2 treats a misfiled call, and the Gemma twin's re-smoke at its new
window. *v2.5.5:* the first two are settled (the twins are in the grid as its fifth tier
(section 4.2, section 6), with the within-pair comparison registered as exploratory (section 10, seventh), and
G2 is refined (above)) and the third goes with the full re-smoke that certifies the grid.
**Probed, smoked and registered in v2.5.4. In the grid since v2.5.5.**

Bench players and near-misses. **As of v2.5.1 the standby slot is open.** Granite held it
until v2.4.4, when it was found not fieldable and the slot passed to Nemotron-3-Nano-30B-A3B
(NVIDIA, below). Nemotron was probed, smoked and retired in v2.5.1. What follows about both
is kept as the record of why. Until v2.4.4 the slot was held by
**Granite 4.2-30B**
(IBM), and the harness carries it (`granite-q4` / `granite-q8` in the run
wrapper, three arms in the batch driver) so it can be brought up without a code
change on the day. It took the slot from EXAONE-4.0-32B in v2.3.13, and the
reason is worth stating because it changed what this study selects a substitute
*for*. A standby used to be chosen on having a thinking on/off switch, which is
the OFF->UNSEEN requirement. The binding constraint turns out to be the other
one: whether the template will render a *past* assistant turn's reasoning back
into the prompt. That is rarer than it sounds: of the five models the roster then held, Gemma
and Qwen manage it only with `preserve_thinking`, Magistral needed inline
replay, and gpt-oss substitutes prose for it.

Granite is the first candidate whose vendor documents the thing the SEEN arm
needs. Thinking is `enable_thinking` true/false, the same switch Gemma and Qwen
use, so it is a three-arm model. History is governed by a separate flag,
`truncate_history_thinking`, which **defaults to true** (prior turns' thinking
is stripped to save context) and can be set **false** to keep it. That is a
`preserve_thinking` analogue with the opposite polarity, and the polarity is the
trap: setting it the intuitive way round would leave SEEN rendering nothing
while every manifest recorded that the reasoning had been sent. It is therefore
given its own `THINK_KIND` (`enable_thinking_granite`) with two explicit literal
bodies rather than being folded into the existing kind behind a variable flag
name. It is sent in all three arms, as `preserve_thinking` is, so the only
things that move across the ladder remain `enable_thinking` and whether the
reasoning is replayed at all.

The rest of the fit is unusually clean: dense 30B (not MoE, so the compute
profile matches the roster (*a reason that was wrong when written: gpt-oss-20b is
itself a mixture-of-experts model, see the architecture paragraph above, v2.4.4*),
128K context, Apache 2.0 and ungated, and `Q4_K_M`
at roughly 18 GB) mid-band. The engine question is settled in our favour rather
than pending: `bartowski/granite-4.2-30b-GGUF` was quantised at llama.cpp
**b10603** and this study pins **b10964**, so the architecture predates the pin
instead of chasing it. There is **no unsloth build of 4.2** (unsloth stops at
`granite-4.1-30b`), so the file comes from that mirror or from IBM's own
`ibm-granite/granite-4.2-30b-GGUF`: two different artefacts, whichever is used
gets hashed and its template fingerprinted.

None of which makes it verified. Nobody has read the template out of the GGUF
that would actually be served, and `truncate_history_thinking` is a line on a
model card, not a measurement. The tooling is arranged so nothing pretends
otherwise: Granite has no entry in `verify_smokes.py`'s `EXPECTED_BODY`,
`EXPECTED_REPLAY_FORMAT` or `EXPECTED_PREAMBLE`, so gates G11-G13 fail it with
*"no expected ... registered for this model"* until someone adds those entries
deliberately, after the checks. Smoke it. Do not grid it before that. Step 3 of
the sequence has a specific question for this model: confirm that
`truncate_history_thinking` is the name the served template reads, and that
**false** is the value that keeps history.

That check has now been done at the desk, against the file on the machine
(IBM's own build, 17,721,455,328 bytes, template sha256 `f0ba43f79b3cabca`,
9,013 chars): everything below is rendered bytes, not a model card. Three
variables are declared with defaults at the top: `enable_thinking` true,
`low_effort` false, and `truncate_history_thinking` **true**. The generation
prompt ends `<|im_start|>assistant\n<think>\n` when thinking is on and
`<|im_start|>assistant\n<think></think>` when it is off, so the OFF arm is a
pre-closed think block rather than an absent one. A past assistant turn's
reasoning is read off the field and folded into its content: 

```jinja
{%- set content = "<think>\n" ~ message.reasoning_content ~ "\n</think>\n" ~ (message.content | default('', true)) %}
```

 which means the `field` replay route is correct and no inline form is needed.
History is then gated, in both the tool-call and the plain branch, by

```jinja
{%- set include_content = not (truncate_history_thinking and loop.index0 < ns.last_user_idx) %}
```

This is the same shape of gate as Gemma's and Qwen's, and it is a plain `and`,
so setting the flag false defeats it unconditionally: unlike Gemma's, which
also ANDs with `tool_calls`. `loop.last` appears twice in the template and both
times it places `<|im_end|>`. There is no EXAONE-style last-message trap.

Rendered under the canonical exchange, the flag is a **no-op without a nudge**
and decisive with one, which is exactly why a desk check that omits the nudge
proves nothing:

```
Granite   nudge=False   flag=False R1,R2 present  |  flag=True  R1,R2 present
          nudge=True    flag=False R1,R2 present  |  flag=True  R1,R2 GONE
Gemma     nudge=True    preserve=False R1,R2 GONE |  preserve=True R1,R2 present
```

The treatment is purely additive: the assistant's own prose survives beside the
`<think>` block rather than being replaced by it, so Granite does not carry
gpt-oss's substitution asymmetry.

**One risk survives to the live probe, and it is not small.** The template
iterates a tool call's arguments as a mapping (
`{%- for args_name, args_value in tool_call.arguments|items %}`) while the
OpenAI wire format this harness speaks sends `arguments` as a JSON *string*.
Rendered offline with a string the template raises `TypeError: Can only get item
pairs from a mapping`, and it renders only once the arguments are parsed into an
object. Whether llama.cpp does that parse before handing the messages to the
template is unknown and cannot be settled by reading either side. If it does
not, every turn after the first will fail to render and the model is unusable
here regardless of how good its thinking flags are. `template_probe.sh
granite-q4` answers it in one call, because its canonical exchange contains two
past tool calls.

**Answered, on the server, 2026-09-23.** llama.cpp does parse the arguments
string into an object before rendering, so the risk is closed and Granite
renders normally. The probe's three arms plus the nudged case:

```
arm        chars    R1     R2    chat_template_kwargs
OFF         1680   False  False  {"enable_thinking": false, "truncate_history_thinking": false}
UNSEEN      1673   False  False  {"enable_thinking": true,  "truncate_history_thinking": false}
SEEN        1823   True   True   {"enable_thinking": true,  "truncate_history_thinking": false}
nudged SEEN 1915   True   True   both turns still visible
```

UNSEEN -> SEEN adds **+150 chars**, the reasoning is present, the assistant's own
prose survives intact, and the nudge does not truncate it. Two things are worth
recording beyond the pass. First, the offline render of the same exchange gave
1725 / 1718 / 1868: a constant 45-character offset from the server across every
arm, and **the same +150 delta**: two independent Jinja implementations,
`jinja2` here and llama.cpp's `minja` there, agree exactly on the size of the
treatment while disagreeing by a fixed amount on the framing around it. Second,
Granite is additive rather than substitutive, so unlike gpt-oss it carries no
prose-for-reasoning asymmetry.

**And then it was smoked, and the treatment being real turned out not to be the
question.** Registered in all three `EXPECTED_*` tables as of v2.4.1, Granite passes every
configuration gate (body, replay format, preamble, decoding) and fails as a model. Across
nine runs it finished three. Its two failure modes split cleanly by arm and have nothing to
do with each other:

*OFF and UNSEEN run too long.* 135-178 steps, still working, stopped by the per-run token
budget rather than by any confusion: three of the nine hit the 8M ceiling, which is what
raised it to 12M (section 4.4). These arms may well be fine at the higher budget.

*SEEN does not run at all.* Three of three, at steps 9-11, the model spends the **entire**
32,768-token per-reply allowance on reasoning and emits zero characters of output: 88,845
characters, 3,531 lines, 360 unique, *"Let me do it."* 768 times. It narrates the tool call
it is about to make, does not make it, and loops. The prompt is 7-9k against a 131k
context, so nothing is starved. This is the model failing to terminate. It happened
identically under greedy decoding, so it is not the sampler either. The 12M budget will not
touch it, because the binding limit is the per-reply cap and not the per-run one.

The second is the disqualifying one, and it is worth naming precisely what it is: in the
arm where Granite is shown its own prior reasoning, what it does with that reasoning is
produce more of it, without bound. Whatever else that is, a model whose SEEN arm cannot
complete a single run is not a substitute for a model that fails its gates: it is a
second failure wearing the first one's uniform. **Recommendation: Granite is not
fieldable as it stands.** It stays registered rather than removed, because registered means
its gates now say something about the model instead of about the paperwork, and because
the failure it exhibits is the most interesting thing any standby has produced.

Two smaller notes from the same pass. The file records no
`general.quantized_by` and no imatrix, so its build provenance is not in the
bytes and the sha256 is the only pin: worth stating because the ungated mirror
of the same rung *is* imatrix-built, and the two are not interchangeable. And
the GGUF's own `base_model` url points at `granite-4.1-30b-base`. Separately,
`render_arms.py` needed a `tojson(ensure_ascii=...)` shim to render this template
at all: stock Jinja2's filter takes no such argument while `transformers` and
llama.cpp's minja both accept it, and without the shim the renderer fails in a
way that reads like a broken template rather than a broken renderer.

**Nemotron-3-Nano-30B-A3B** (NVIDIA) (**retired in v2.5.1**, below) was proposed for the
standby slot in v2.4.4, on the capability that put Granite there: its template renders a
past turn's reasoning under a keep-history flag. It was wired as `nemotron-q4` (three arms
in the batch driver until v2.5.1, its own `THINK_KIND` (`enable_thinking_nemotron`), its own
row in `render_arms.py`) and kept out of the `EXPECTED_*` tables until its live probe and
smoke passed. G11-G13 fail it by design.

The file is unsloth's `Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf` from
`unsloth/Nemotron-3-Nano-30B-A3B-GGUF`: 24,574,373,664 bytes, sha256
`0e7f6e51fdd90399...`, imatrix-built from unsloth's calibration set, header rung `Q4_K_M`.
LM Studio saved it under `unsloth/Nemotron-3-Nano-30B-A3B/`, without the `-GGUF` suffix
the other unsloth folders carry, and the wrapper's path says so. The header architecture
is `nemotron_h_moe`: Mamba-2 and attention layers with a mixture-of-experts feed-forward,
6 of 128 experts routed per token plus one shared, about 3.5B of 30B parameters active.
That architecture string is present in the pinned b10964's `llama.dll`, so the engine
loads it without a bump. Its tool calls use the Qwen3-Coder XML form, and that parser
(`qwen3_coder`) is in the build too. The only Nemotron-named chat format in the build is
Nano v2's, so whether its reasoning arrives in `reasoning_content` rather than inline
is the first thing the live probe has to show.

The template was read out of that file (sha256 `b3043677cd5fc67f`, 10,653 chars: 
unsloth's patched version of NVIDIA's, which is the one served). It declares
`enable_thinking` and `truncate_history_thinking`, both defaulting to **true**. The
generation prompt ends in an open `<think>` with thinking on and a pre-closed
`<think></think>` with it off. A past turn's reasoning is read off the `reasoning_content`
field, and history is gated in **both** assistant branches by Granite's expression,
character for character: 

```jinja
{%- set include_content = not (truncate_history_thinking and loop.index0 < ns.last_user_idx) %}
```

 so `false` defeats it unconditionally, and there is no `loop.last` trap. Rendered
offline (jinja2, the canonical exchange, arguments as the mappings llama.cpp passes):

```
arm      chars   R1     R2     assistant prose   past-call arguments
OFF       1784   False  False  kept              rendered
UNSEEN    1777   False  False  kept              rendered
SEEN      1927   True   True   kept              rendered

Nemotron  nudge=False  flag=False R1,R2 present  |  flag=True (default) R1,R2 present
          nudge=True   flag=False R1,R2 present  |  flag=True (default) R1,R2 GONE
```

UNSEEN -> SEEN adds **+150 chars**, Granite's offline delta exactly. The treatment is
additive, and OFF differs from UNSEEN only in the generation prompt. One property needed
checking because it fails silently: the template renders a past call's arguments only when
they are a **mapping**, with no else-branch, so given the JSON string the wire format
carries it renders `<function=write_file></function>` and raises nothing, where Granite's
raises a `TypeError`. That is not new to this model. Qwen's and Seed's templates do the
same, and all three work because llama.cpp parses arguments into a mapping before
rendering, as Granite's live probe showed on this build. `template_probe.py` now checks it
for every model rather than leaning on that one probe.

Sampling is the card's tool-calling profile in both modes, with the OFF arm a registered
deviation from its greedy recommendation (section 4.4.1).

**The open risk is competence, not architecture.** Study 08's gate failed a ~3B-active
mixture-of-experts model in the same harness and task suite (`qwen3-coder-next`, 92
steps of thrashing and no working app) while gpt-oss, at ~3.6B active, is this roster's
most reliable smoke performer. Neither result predicts this model. Its smoke decides it.

**Probed and smoked in v2.5.0, and not registered.** The live probe passed exactly as the
desk render said it would: UNSEEN -> SEEN **+150 chars** on the server (1,718 -> 1,868), the
reasoning parsed into `reasoning_content` on every thinking-arm step of the smoke, and
nothing leaked into the content. The treatment is real. The model is the problem, in two
unrelated ways.

*With thinking OFF it stops using the tool interface.* In 11 of 15 OFF runs (the three
smoke runs plus twelve diagnostic runs on fresh seeds, made with `nemotron_off_diag.sh`
outside every smoke set) its first reply contained no tool call but a JSON "agent
protocol" of its own, the harness's nudge got the same again, and the run ended at step 2.
The other four used native calls throughout. No run switched between the two. The
envelopes are not improvised:

```
{"analysis": ..., "plan": ..., "commands": [{"tool": ..., "arguments": ...}], "task_complete": false}
{"thoughts": ..., "plan": ..., "commands": [{..., "is_blocking": ..., "timeout_sec": ...}], "is_task_complete": ...}
{"action": "write_file", "args": {...}}          (after a line of prose, in a json code fence)
```

The first carries exactly the top-level keys of Terminal-Bench's Terminus-2 agent
(`analysis`, `plan`, `commands`, `task_complete`, [prompt template](https://github.com/laude-institute/terminal-bench/blob/main/terminal_bench/agents/prompt-templates/terminus-json-plain.txt)), with this
harness's tool names put where Terminus puts keystrokes. The second carries Terminus-1's
command fields and completion flag ([`terminus_1.py`](https://github.com/laude-institute/terminal-bench/blob/main/terminal_bench/agents/terminus_1.py)). The third matches the JSON
action format of the early OpenDevin agents, the project that became OpenHands
([planner prompt, 0.9.0](https://github.com/All-Hands-AI/OpenHands/blob/0.9.0/agenthub/planner_agent/prompt.py)). [NVIDIA's technical report](https://arxiv.org/abs/2512.20848) (section 3.1.2) says its terminal-use training
data consists of trajectories generated "using the Terminus-1 and Terminus-2 agents" (
plain-text JSON protocols with no native tool calls) by Qwen3-Coder-480B-A35B-Instruct and
Kimi-K2-Instruct-0905, and that its software-engineering data was distilled from OpenHands,
SWE-Agent and Mini-SWE-Agent trajectories with the same Qwen3-Coder as teacher. Both
teachers are non-thinking models, so those samples carried no reasoning: the condition
this study's OFF arm recreates. The same report says the on/off switch was taught by
stripping the reasoning from "a random 10% of samples" (section 3.1.5), and lists no
software-engineering or terminal environment among its reinforcement-learning environments
(section 3.2). Nothing this harness sends primes the format: none of the envelopes' keys appears
in its 776-character system prompt or in the task text, and the drift came in four of five
`no_verification` runs, a condition that offers no shell tool at all, as often as in
`execution`. Read together, with its thinking switched off the model falls back to the
scaffolds it was trained in.

*With thinking on it finishes without checking.* Both thinking arms parse cleanly, and six
of the nine smoke runs finished, SEEN three of three. But in the four finished runs whose
condition offered verification tools (`execution` and `interactive`) the model never ran,
served, requested or browsed what it had built: zero verification actions, counting a
server started, an HTTP request, a build or test command, or a browser tool. The one run in
which it did start a server is the one that then died of a runaway reply
(`runaway_no_tool_call`, a 23-line cycle over the PGlite export). Gemma, on the same tasks,
verified in every one of its `execution` and `interactive` smoke runs. It is the pattern
study 08's gate failed on: a run that finishes, and ships an app nobody has run.

**What the documentation offers against either.** [NVIDIA's model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16) gives three
sampling profiles (reasoning, tool calling, and greedy for reasoning off) recommends a high
`max_tokens`, and serves tool calls through the Qwen3-Coder XML parser. The thinking arms
here use the tool-calling profile, a 32,768-token reply cap and llama.cpp's parser for that
format, and the SEEN arm keeps within-task reasoning the way the report says multi-step
turns were trained (UNSEEN withholds it, which is the treatment). NVIDIA's [reproduction
guide](https://github.com/NVIDIA-NeMo/Evaluator/blob/main/packages/nemo-evaluator-launcher/examples/nemotron/nano-v3-reproducibility.md) switches thinking off only for its long-context RULER runs and runs its tool-calling
benchmarks at the template's default, thinking on. The one NVIDIA-published run of the
model with thinking off in a tool environment ([a Prime Intellect tutorial](https://developer.nvidia.com/blog/start-customizing-nvidia-nemotron-3-nano-with-prime-intellect-lab-in-minutes/),
at temperature 1.0) shows it failing because it "exhausted five turns calling unsupported tools". The one
documented setting this study declines is greedy decoding for the OFF arm (section 4.4.1). It is
untested here and may or may not change which format the model reaches for. The training
record above is why the format is there to reach for. NVIDIA's reported agentic results
are modest: 38.8 on SWE-Bench, run in OpenHands, one of the harnesses its training
trajectories came from, and 8.5 on Terminal Bench's hard subset (model card). Users who ran
it in other agents, Qwen Code and OpenCode, report that it calls `str_replace_editor`: a
tool neither agent has, and the file-editing tool of the OpenHands scaffold its
software-engineering data came from: it would "hallucinate a lot about `str_replace_editor`
tool" ([discussion #3](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16/discussions/3)). And NVIDIA staff, answering a user report that the model
"fails consistently at basic coding tasks", called it "a model limitation"
([discussion #15](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16/discussions/15)).

**Recommendation (v2.5.0): not fieldable as it stands, taken in v2.5.1.** Its thinking arms
would run. Whether their apps work is ungraded, but a model that never runs what it builds
is the profile study 08 excluded, and its OFF arm does not run at all. **Nemotron is
retired.** It has left the batch driver and the standby slot, which is open. It stays in
the wrapper's model map, unregistered, so that every run cited above can be re-made by
name, as EXAONE's and Granite's entries are. Meta's **Muse Glimmer 30B** (dense, Apache 2.0, released
2026-08-10, whose template renders past reasoning whenever the field is sent and needs no
flag) is the candidate v2.4.5 named for exactly this case, a competence failure, at the
price of two arms, since its reasoning strength has no off level. It is neither wired nor
verified. *v2.5.19:* wired for a pilot, as `muse-q4xl`. *v2.5.20:* the pilot passed, and it
is in the grid as tier 6.

**GLM-4.7-Flash** was wired here as the second-line standby in v2.4.5, behind Nemotron,
from what Z.ai's published files said. Everything that entry recorded held against the file
on the machine, and GLM left the bench for the roster in v2.5.0: its entry is above, its
template in section 4.2.2.

**EXAONE-4.0-32B** (LG AI Research) held this slot until v2.3.13 and is kept
here as a worked near-miss rather than deleted, because the way it fails is more
instructive than the fact that it does. It stays in the wrapper's model map (`exaone-q4` /
`exaone-q8`), deliberately out of the batch driver, and unregistered in `verify_smokes.py`.

Where EXAONE would come from, if it is ever wanted. **There is no `unsloth` build of EXAONE-4.0-32B**: the roster's
models all come from unsloth, and this one does not, so the publisher
convention breaks here. The authoritative file is LG's own
`LGAI-EXAONE/EXAONE-4.0-32B-GGUF`, which carries `EXAONE-4.0-32B-Q4_K_M.gguf`
at 19.3 GB under a custom EXAONE licence that has to be accepted on the Hub
before the file will download: meaning an access token and a click-through, not
an anonymous pull. Ungated mirrors of the same quantisation exist
(`bartowski/LGAI-EXAONE_EXAONE-4.0-32B-GGUF`, built at llama.cpp b5934,
`lmstudio-community/`, `mradermacher/`), and they are convenient, but a mirror
is a different artefact: the chat template is baked into the GGUF, the template
*is* the treatment in this study, and mirrors are cut at different upstream
commits. Whichever is used gets hashed into `quant-registry.json` and has its
template extracted and fingerprinted like every other file here, and the choice
is recorded rather than assumed. The wrapper's `GGUF_REL` expects
`EXAONE-4.0-32B-GGUF/EXAONE-4.0-32B-Q4_K_M.gguf` beneath `MODELS_ROOT`. Since
that root points at the `unsloth/` publisher folder, either drop the file there
under that folder name or override `MODELS_ROOT`.

What is known from its card and from llama.cpp: it uses the same switch as
Gemma and Qwen, `chat_template_kwargs.enable_thinking` true/false. Its context
is 131,072, and llama.cpp has supported the architecture since **b5932**, well
before the b10964 this study pins: so the engine is not a barrier. Its Q4_K_M
is 19.3 GB, which sits in the same band as the rest of the roster.

**And what its published template says is a problem.** Read from
`chat_template.jinja` in LG's GGUF repo (*the published file, not yet the bytes
in a GGUF on this machine, so this is a strong indication and not a measurement*) 
three lines decide the primary contrast:

```jinja
{%- if not skip_think is defined %}
{%- set skip_think = true %}
...
{%- if (not skip_think and loop.last) and reasoning_content is defined %}
```

The template does read the field (`{%- set reasoning_content = msg.reasoning_content %}`) 
so the replay route is right. But rendering it requires `skip_think` to be
false, and it **defaults to true**. The name the template knows is `skip_think`,
not the `preserve_thinking` EXAONE currently inherits from Gemma's and Qwen's
`THINK_KIND`, which this template never reads. Worse, the condition also
requires `loop.last`: only the final message in the list may show reasoning, and
in an agentic history the final message is a tool result, so no assistant turn
is ever `loop.last`. The `{%- else %}` branch then writes an empty
`<think>\n\n</think>` in its place: the prior thought is not merely skipped,
it is overwritten with a blank one.

Taken at face value that makes EXAONE's **SEEN arm null as configured**, and
null in a way no kwarg in the present body reaches. Adding `skip_think: false`
clears the first gate. Nothing in `chat_template_kwargs` clears `loop.last`.
Inline replay does not rescue it either, since the inlined text lands in the
same local variable behind the same gate. If the gate is real, the only route
left is serving EXAONE under a patched template via llama.cpp's
`--chat-template-file`: which is a real deviation, because every other model in
this study is served the template that shipped inside its own GGUF, and it would
have to be pre-registered and diffed rather than quietly applied.

None of that is settled until it is measured on the file itself. The sequence is
unchanged and now has a sharper question to answer:

1. **Extract and read the template from the GGUF actually downloaded**
   (`gguf_chat_template.py`), and confirm or refute the two gates above. A
   mirror may carry a different revision than LG's repo page.
2. **Prove it on the live server** (`template_probe.sh exaone-q4`), with a nudge
   in the history. This is the freeze gate every model passes, and for EXAONE it
   is the one that decides whether the standby is usable at all. A
   byte-identical UNSEEN/SEEN pair here means the arm is not a treatment.
3. **~~How it behaves under frozen greedy decoding.~~ RESOLVED in v2.4.0.** This
   entry used to read: EXAONE's card recommends `temperature=0.6, top_p=0.95`
   for reasoning mode and warns that reasoning is "affected sensitively by
   sampling parameters", while the study served every model at temperature 0 /
   top_k 1 ("not negotiable without re-running everything") so EXAONE would
   show worse reasoning here than its published numbers suggest. It is kept
   rather than deleted because it is where the decoding question was first
   written down, against the standby nobody had downloaded, three weeks before
   the smoke runs made the same point about the five models that were actually
   being served. The premise no longer holds: section 4.4.1 serves every model at its
   own documented settings, so a candidate's recommended sampling is now a
   registry entry rather than a reason it will underperform. The general lesson
   is worth more than the entry: a caveat written about a bench player usually
   applies to the starters too, and this one went unexamined for three weeks
   because it was filed under someone else's name.

The practical consequence is worth stating plainly, because a substitute is
reached for under time pressure: **EXAONE is not a drop-in.** If a roster model
fails its gates on the day, swapping EXAONE in costs a licence acceptance, a
19.3 GB download, a template extraction, a probe, and (on present evidence) 
most likely a decision about whether a patched template is acceptable. Budget
that, or accept the roster running one model short with the slot reported empty.

Also worth deciding deliberately rather than by inertia: **EXAONE-4.0.1-32B**
and **EXAONE-4.5** have since shipped. This plan named 4.0-32B when it was
current. If the substitute is ever called up, the version should be chosen then
and fingerprinted like any other.

**Olmo-3.1-32B-Think** (AI2) is the second choice, and the one to reach for if
openness matters more than the third rung. `unsloth/Olmo-3.1-32B-Think-GGUF`
puts `Q4_K_M` at 19.5 GB under the publisher path this study already uses, and
the model is open all the way down (data, code, intermediate checkpoints) 
which is worth something in a paper about model behaviour. The catch is that
thinking is a separate checkpoint rather than a switch: `-Think` and `-Instruct`
are different weights and no in-checkpoint off-switch is documented. So it is a
**two-arm model** like gpt-oss, carrying the primary contrast but not the
secondary one. One move must be ruled out explicitly, because it will occur to
someone under time pressure: pairing `-Think` as UNSEEN/SEEN against
`-Instruct` as OFF is **not** a valid OFF arm. It confounds thinking with
different weights, which is the precise thing the within-model ladder exists to
prevent, and it would be an unregistered between-model comparison wearing the
ladder's clothes.

**Devstral-Small-2-24B** (Mistral) is already on the study machine and cannot
serve. Its template was extracted from the GGUF on disk
(`Devstral-Small-2-24B-Instruct-2512-Q4_K_M.gguf`, template sha256
`adb1c45376c8a8a1`, 13,673 chars) and searched: zero occurrences of `think`,
`reasoning`, `reasoning_content` or `enable_thinking`. It is a non-thinking
coding model and has no arm of this study available to it. Recorded here so that
the file which is already downloaded is not mistaken for the cheapest
substitute.

**DeepSeek** has no open
model that fits one machine: its smallest current release, **DeepSeek-V4-
Flash**, is a 284B mixture-of-experts (13B active) that needs 110-162 GB of
memory (more than the study machine's 96 GB card, and this study never offloads to the
CPU (section 4.3), and its API forbids the UNSEEN arm outright, so DeepSeek is excluded) section 8
records why. *v2.5.5 correction:* this entry used to say it also needed a newer engine
build than ours. The pinned b10964 does carry its architecture (`deepseek4`), so size
alone rules it out locally.

Six labs, six different template grammars and thinking dialects: if a
visibility effect shows up in several of them, it is not one vendor's quirk.

### 5.1 Models considered and not chosen *(v2.5.5)*

Eight models are in the grid: seven since Magistral left it in v2.5.9, and Muse Glimmer since v2.5.20. More were weighed, and this section is the record of every one
that was not chosen and why: so that a reader can check that nothing convenient was dropped
quietly, and so that a replacement, if one is ever needed, starts from what is already known
instead of from a search. Four requirements decided every case, in this order.

1. **A thinking mode whose past reasoning the template can show.** The primary contrast,
   UNSEEN against SEEN, exists only if the served template renders a past turn's reasoning
   when the request carries it. A model with no thinking mode has no arm here at all. a
   template that drops past reasoning makes SEEN the same prompt as UNSEEN.
2. **An off-switch inside the same checkpoint.** The third rung, OFF, must be the same
   weights with thinking switched off. A model whose thinking is a separate checkpoint, or
   cannot be switched off, runs two arms at most, as gpt-oss and Muse Glimmer do.
3. **It fits the machine as frozen.** Wholly on the study machine's 96 GB card at about four
   bits with its context (section 4.3 never offloads to the CPU) served by the pinned llama.cpp
   b10964 with the template its GGUF carries. A replacement template or a newer engine would
   be a deviation made for one model.
4. **It is fieldable on its smoke.** Its arms run, it calls tools in its own format, and it
   finishes.

**Models that reached the harness**

| model | lab | architecture | considered as | how far it got | why not chosen |
|---|---|---|---|---|---|
| Magistral-Small-2509 | Mistral | dense, 24B | roster model until v2.5.9 | wired, hashed, preamble registered and chosen on 10 runs per variant, replayed inline, probed live (+174 chars), smoked from 2026-09-20 to its re-smoke of 2026-09-25, registered | finished 5 of 9 smoke runs, then 3 of 9 on its re-smoke. Every failure a turn without a tool call, and all three re-smoke OFF runs stopped at step 2 |
| Granite 4.2-30B | IBM | dense, 30B | standby, v2.3.13-v2.4.4 | wired, hashed, template extracted, probed live (+150 chars), smoked in four sets, registered | its SEEN arm finished 0 of 3 under two decoders, every run spending its whole 32,768-token reply allowance in a repetition loop |
| Nemotron-3-Nano-30B-A3B | NVIDIA | mixture-of-experts, ~3.5B of 30B active | standby, v2.4.4-v2.5.1 | wired, hashed, template extracted, probed live (+150), smoked, 12 OFF diagnostic runs. Never registered | its OFF arm answered with a JSON agent protocol of its own instead of a tool call in 11 of 15 runs |
| EXAONE-4.0-32B | LG AI Research | dense, 32B | standby, v2.3.11-v2.3.13 | wired from its card and published template. Never downloaded | its template shows past reasoning only on the last message, with `skip_think` defaulting to true, so SEEN would render none |
| Devstral-Small-2-24B | Mistral | dense, 24B | already on the machine (study 08) | template extracted | no thinking mode at all |

**Models weighed at the desk**

| model | lab | architecture | considered as | why not chosen |
|---|---|---|---|---|
| Muse Glimmer 30B | Meta | dense, 30B | hedge against a Nemotron competence failure, v2.4.5 | two arms only: its reasoning strength has no off level. *v2.5.20:* in the grid after all, as tier 6, at the study lead's decision, for a sixth lab and a fourth dense model |
| Olmo-3.1-32B-Think | AI2 | dense, 32B | second choice in the first standby search | thinking is a separate checkpoint: two arms |
| Laguna XS 2.1 | Poolside | mixture-of-experts, 3B of 33B active | three-arm finalist, 2026-09-25 | passed over for the within-lab twins. Its card warns reasoning may stop once earlier thinking is dropped, which is what UNSEEN does |
| North Mini Code 1.0 | Cohere | mixture-of-experts, 3B of 30B active | three-arm finalist, 2026-09-25 | passed over for the twins. No documented thinking-off mode, and its card asks for thinking to be passed back |
| Qwen3-Coder-Next | Alibaba | mixture-of-experts, ~3B active | asked about, 2026-09-25 | no thinking mode. Failed study 08's gate on competence |
| DeepSeek-V4-Flash | DeepSeek | mixture-of-experts, 13B of 284B active | original roster, and the section 8 extension | 110-162 GB, beyond the card. Its API forbids UNSEEN |
| Mistral Small 4 | Mistral | mixture-of-experts, 6.5B of 119B active | the 2026-09-25 search | only a newer template than its GGUFs carry shows past reasoning |
| Laguna S 2.1 | Poolside | mixture-of-experts, 8B of 118B active | the 2026-09-25 search | its GGUF's template does not keep past thinking |
| Ling-3.0-flash | inclusionAI | mixture-of-experts, 5.1B of 124B active | the 2026-09-25 search | the pinned engine mishandles its tool calls made before `</think>` |

**Each decision in full**, most-tested first.

**Magistral-Small-2509** (Mistral, dense 24B, Apache 2.0). A roster model until v2.5.9, and
the one that took the most work to field. Its thinking is driven by the system prompt rather
than a template flag, so its switch became a registered preamble (the vendor's reasoning
instructions, trimmed to `mistral-min` on 10 runs per variant) carried in its thinking arms
and omitted in OFF, a measured off-switch: 36 of 36 preamble-free responses carried no
reasoning. Its template has no slot for the reasoning field, so it was the one model replayed
inline, `[THINK]...[/THINK]` ahead of its prose, verified live at +174 chars (section 4.2.1, section 4.2.2).
What it never became was reliable at calling tools. In the 12M smoke set, under its vendor
sampling, it finished 5 of 9 runs (OFF 1 of 3, UNSEEN and SEEN 2 of 3 each) with 12 of its
64 turns carrying no tool call, and all four failures ended `stopped_no_tool_call` after it
put in its message what should have been a call, and it ran no command in any of its six
`execution` and `interactive` runs, reasoning that "the task doesn't explicitly require
running the application, just creating the files". Put under review in v2.5.7, it was
re-smoked under the v2.5.6 briefing, which told a model that its execution tools act on a
live environment. That moved one of the three things the review named: it ran commands in 3
of its 6 `execution` and `interactive` runs. The other two went the wrong way. It finished 3
of 9 (OFF 0 of 3, UNSEEN 2 of 3, SEEN 1 of 3) and all six failures ended
`stopped_no_tool_call`: each OFF run at step 2, having described in prose what it meant to
do instead of calling a tool. Two SEEN runs writing their `write_file` calls as text with the
opening `[TOOL_CALLS]` token missing (`toolwrite_file[ARGS]{...}`, four such turns, none in its
other arms), and one UNSEEN run ending at step 16 on a 17,040-character review of its own
code. A model whose OFF arm stops at step 2 can run two arms at most, as Nemotron's case
settled (below), and its thinking arms finished 3 of 6. Removed from the grid in v2.5.9 at
the study lead's decision, when the v2.5.6 briefing sentence was withdrawn too (section 4.1).
v2.5.10 reinstated the sentence for the models that remain, and Magistral stays out on its
own record. It stays in the
wrapper's model map, the `EXPECTED_*` tables and the templates folder, so every cited run can
be re-made, and its sections in section 4.2.1 and section 4.2.2 are kept as the record.

**Granite 4.2-30B** (IBM, dense 30B, 128K context, Apache 2.0). It took the standby slot
from EXAONE in v2.3.13 because its card documents `truncate_history_thinking: false`, the
keep-history flag EXAONE's template lacks, and it got further than any other model not
chosen: wired as `granite-q4`, hashed, its template extracted and read (a plain AND gate
that `false` defeats, and no `loop.last` trap), probed live at +150 chars on both the
offline render and the server, smoked in four sets, and registered in all three
`EXPECTED_*` tables since v2.4.1. It failed on its SEEN arm, 0 of 3 under greedy decoding
and 0 of 3 under its card's sampling. Every one of those runs spent its whole 32,768-token
reply allowance on reasoning and emitted nothing: one reply ran to 88,845 characters in
3,531 lines, 360 of them unique, *"Let me do it."* 768 times. Another was a strict 26-line
cycle repeated about 70 times (section 4.4.1). The loop is the model's, not the cap's, and a larger cap could not even be tried:
a 98,304-token reply outlasts the 3,600 s client timeout, and a timed-out call is silently
retried. Its other arms ran long enough to force the token budget from 8M to 12M, and it
would have taken 48.7% of the smoke set's generation time, 2.25 times the next model.
Retired in v2.4.4. It stayed in the batch driver by oversight until v2.5.5, and it stays
in the wrapper's model map and the `EXPECTED_*` tables so every cited run can be re-made.

**Nemotron-3-Nano-30B-A3B** (NVIDIA, 6 of 128 experts plus one shared, ~3.5B of 30B
active). Proposed for the slot in v2.4.4, with Granite's switch names and polarity, it
passed every template check (hashed, template `b3043677cd5fc67f`, desk render and live
probe both +150 chars) and then failed on behaviour. With thinking off it answered step 1
with a JSON agent protocol of its own in 11 of 15 runs (three smokes and twelve diagnostic
runs), in formats matching Terminal-Bench's Terminus agents (which NVIDIA's technical
report says generated its terminal training data) and the early OpenDevin agents,
forerunners of the OpenHands scaffold its software-engineering data came from. Each such run
ended at step 2. With thinking on, six of nine smoke runs finished, and none of its four finished
`execution` and `interactive` runs ran, served, requested or browsed what it had built.
NVIDIA's documentation offered no remedy for either: its own thinking-off tool run
"exhausted five turns calling unsupported tools", users report it calling OpenHands'
`str_replace_editor` in agents that have no such tool, and NVIDIA staff called its coding
failures "a model limitation". Retired in v2.5.1. Its full record, with sources, is in section 5
above. *In fairness, v2.5.5:* the second reason does not set it apart from the roster, 
in the 12M smoke set Magistral and gpt-oss ran no command at all in any of their
`execution` and `interactive` runs either (section 10, ninth). What does set it apart is the
first. A model whose OFF arm stops at step 2 can run two arms at most, and the roster
already had a two-arm mixture-of-experts model in gpt-oss, while three-arm ones were
available.

**EXAONE-4.0-32B** (LG AI Research, dense 32B, custom licence, gated on the Hub). Named as
the fallback in the predecessor plan (study 41) and wired here as the standby in v2.3.11,
it was never downloaded, because LG's published template settled it first. `skip_think`
defaults to true and the template never reads `preserve_thinking`. A past turn's reasoning
renders only under `not skip_think and loop.last`, and in an agent's history the last
message is a tool result, so SEEN would render no past reasoning at all. No request setting
reaches `loop.last`. Only a patched template would, which is a deviation made for one
model. There is also no unsloth build, the file sits behind a licence click-through, and
newer versions (4.0.1, 4.5) have since shipped. Replaced by Granite in v2.3.13. Its record
is in section 5 above.

**Devstral-Small-2-24B** (Mistral, dense 24B). Already on the machine from study 08, so the
cheapest candidate on paper. Its template, extracted from that file, contains no `think`,
`reasoning`, `reasoning_content` or `enable_thinking` at all: a non-thinking coding model,
with no arm available to it in this study.

**Muse Glimmer 30B** (Meta, dense 30B, Apache 2.0, released 2026-08-10). Named in v2.4.5 as
the hedge if Nemotron failed on competence. Its template renders past reasoning whenever
the field is sent, with no flag needed, and its architecture is in the pinned build: but
its reasoning strength has no off level, so it runs two arms. When Nemotron failed, the
choice was put between it and three-arm mixture-of-experts models, and the three-arm twins
were chosen. Neither wired nor verified. *v2.5.19:* wired for a pilot at the study lead's
decision, for a sixth lab and a fourth dense model, two arms being a cost the design already
carries for gpt-oss. See the history entry. Olmo-3.1-32B-Think, below, would also run two arms.
It was not reconsidered. *v2.5.20:* its pilot passed, and it is in the grid as tier 6.

**Olmo-3.1-32B-Think** (AI2). The second choice in the first standby search, and the most
open model considered: data, code and intermediate checkpoints. Its thinking is a separate
checkpoint: `-Think` and `-Instruct` are different weights with no in-checkpoint off-switch,
so it runs two arms, and pairing Think against Instruct as OFF would be a between-model
comparison dressed as the ladder. Granite, with three arms, was preferred.

**Laguna XS 2.1** (Poolside, 3B of 33B active, OpenMDW licence) and **North Mini Code 1.0**
(Cohere, 3B of 30B active, 8 of 128 experts, Apache 2.0). The two new-lab finalists of the
2026-09-25 search for three-arm mixture-of-experts models. Both architectures are in the
pinned build (`laguna`, `cohere2moe`), and both templates can show past reasoning. They were
the "more labs" option and the twins the "architecture inside a lab" option, and the twins
were chosen because only a within-lab pair holds vendor, template, switch and sampling fixed
while the architecture changes (section 5). Each also carried a specific risk. Laguna's card warns
that reasoning "may not be generated in follow-up steps if prior thinking blocks are
dropped", which is exactly what UNSEEN does, so its UNSEEN arm would run outside what its
maker supports and a failure there could not be read as a visibility effect. North Mini
Code's card documents no thinking-off mode and asks agents to "pass on all the
model-generated thinking contents to future agentic steps", so both OFF and UNSEEN would
run outside its documented use. Its early GGUFs also had loader and template faults.

**Qwen3-Coder-Next** (Alibaba, ~3B active). It has no thinking mode, so no arm here, and it
failed study 08's gate on competence in this same harness and task suite: 92 steps of
thrashing and no working app.

**DeepSeek-V4-Flash** (DeepSeek, 13B of 284B active). The natural DeepSeek candidate, excluded
twice over. It needs 110-162 GB, beyond the 96 GB card, and this study never offloads to the
CPU (section 4.3). The pinned build does carry its architecture, so size, not the engine, is what
rules it out (the section 5 entry above is corrected in v2.5.5). And DeepSeek's API forbids the
UNSEEN arm outright: with tools present, omitting past reasoning returns HTTP 400 (section 8).

**Mistral Small 4, Laguna S 2.1 and Ling-3.0-flash**: near-passes from the same search,
each within reach of the card at about four bits (Laguna S only at the smaller of its two
published sizes), and each needing something the frozen setup does not allow. Mistral Small 4 (6.5B of 119B active, 73 GB) renders past reasoning only with its
August 2026 template, while the published GGUFs carry the March one, and it would have been
a second Mistral model. Laguna S 2.1 (8B of 118B active) ships a GGUF whose template does
not keep past thinking, users report its tool calls leaking into its reasoning, and its
four-bit size is published as both 68 and 96 GB. Ling-3.0-flash (inclusionAI, 5.1B of 124B
active, MIT, 78 GB) has a template that passes, but on builds before b11057, the pinned one
included, llama.cpp's parser mishandles its tool calls made before `</think>` (filing them
as reasoning or dropping them (issue #27462)) and only a dedicated parser in a later build
fixes it. Each would have needed a replacement template or a newer engine for one model.

**The rest of the 2026-09-25 search** was settled at the desk, from each model's card and
published template, and is recorded by the requirement it failed.

| requirement failed | models |
|---|---|
| 1: the template cannot show past reasoning, or ignores the switch | Hunyuan-A13B (its template reads neither the switch nor past reasoning, its licence also excludes the EU, UK and South Korea). Cogito v2 109B and Trinity Mini 26B-A3B (never render past reasoning, Trinity Mini also cannot switch thinking off). Sarvam 105B and 30B, K-EXAONE-236B-A23B (also 143 GB), Qwen3.5-35B-A3B and Qwen3.5-122B-A10B (show past reasoning only after the last user message and have no keep-history flag, so every finish nudge would silently shrink SEEN: the fault `preserve_thinking` closes for Gemma and Qwen3.6, section 4.2.2). Solar Open 100B (its keep-all flag reads `message.reasoning`, not the field the server sends, it shows only the last turn's thinking by default, and it has no documented off mode) |
| 1: no thinking mode | Kimi-Linear-48B-A3B. Granite 4.0 H-Small and H-Tiny. JoyAI-LLM-Flash. LongCat-Flash-Lite. GroveMoE. Dots.llm1. LFM2-8B-A1B and LFM2-24B-A2B. Ling-2.6-flash. Trinity Nano Preview |
| 2: thinking cannot be switched off in the checkpoint | LFM2.5-8B-A1B and INTELLECT-3.1 (always think). ERNIE-4.5-21B-A3B-Thinking, Kanana-2-30B-A3B, Instella-MoE-16B-A3B and the Ling/Ring 2.x pairs (thinking is a separate checkpoint). VAETKI (thinking is forced off whenever tools are present) |
| 3: too large for the 96 GB card at about four bits | Qwen3.8-Flash-Next (111 GB, its template passes). MiniMax M2, M2.5 and M2.7 (101-108 GB, they also cannot switch thinking off) and M3. Step-3.5-Flash (120 GB). MiMo-V2-Flash (187 GB). Hy3 (182 GB) and Hy4 Preview. Command A+ (132-135 GB). Solar Open 2. Laguna M.1. Inkling. Trinity Large (242 GB). K-EXAONE-2.0. Kimi K3. DeepSeek V4 Pro. GLM-5.x. Qwen3.8-2.4T-A95B |
| 3: needs an engine other than the pinned one | openPangu-2.0-Flash and K2-Horizon-MoVA-36B-A4B (a llama.cpp fork). Ling-3.0-tiny (Ling-3.0-flash's parser fault) |
| outside the search, or not available to run | ERNIE 5.1 (hosted only). Qwen3.7 (closed weights). LFM2.5-24B-A2B (announced, not released). EXAONE 4.5 33B (dense, so outside a mixture-of-experts search, and under a non-commercial licence). Hy-MT2 (a translation model) |

Laguna XS.2 (3B of 33B active) passed on a template read only from a mirror and was not
carried forward. The shortlist took Poolside's XS 2.1 instead. The first two standby
searches weighed models beyond those named here, and their notes do not survive. This
section records every model whose decision the plan can document. Models mentioned only in
passing were never candidates: Qwen3.8-27B as an alternative release for the Qwen slot, now
closed by the twin pairing (section 5). Gpt-oss-120b as the source of OpenAI's sampling advice, and
Nemotron's teacher models. The frontier models of section 8 are an extension, not a roster.

---

## 6. How many runs, and what the numbers can prove

**120 runs per side, per model** (20 per task x condition cell, six cells),
which is 360 runs for a three-arm model and 240 for gpt-oss and Muse: an estimated
~24-54 hours of machine time for a three-arm model, ~7 for gpt-oss and ~20 for Muse (section 4.2).

Why 120? Two reasons, in plain words (the figures are computed as the note
below the list sets out):

- **To detect.** The design is sized so that a failure-rate difference of
  15-20 percentage points between the arms (say, one arm failing 2% of the
  time and the other 15-20%) is caught with 96% to over 99% probability, and
  even a 2% vs 10% difference is caught two times in three (68%). On the
  continuous measures (steps and app quality) it resolves shifts of about
  0.4 standard deviations even after the multiple-comparison correction.
- **To bound.** If nothing differs, 120-a-side lets us say "any reliability
  difference is smaller than ~3-6 percentage points" (+/-2.2pp if neither arm
  fails at all). When the arms truly match at a ~2% failure rate, the +/-10pp
  equivalence statement gets declared over 99% of the time. At a 5% rate,
  91%. At 32-a-side the same statement goes soft (declared only ~27% of the
  time at 2%), which is why we don't run less.

*v2.5.15:* recomputed for twenty replicates, by the method that reproduces
the sixteen-replicate figures exactly: Fisher's exact test, two-sided at
alpha = .05, for the failure rates. The 90% Newcombe hybrid-score interval for
the bound, read at observed failure rates of about 1-8% in both arms, and
for the equivalence statement, and a normal approximation at 80% power, with
Holm over three measures, for steps and quality. At 96 a side they read
90-99% and 56%, about half a standard deviation, ~3-7 points and +/-2.7, and
98% and 80%. The 32-a-side figure does not depend on the replicate count.

*v2.5.18:* app quality is now one grader's rubric score (section 4.5), so its
spread includes the grader's own inconsistency (v2.5.25: one grader). The 0.4 standard deviations above
are in units of that spread, whatever it proves to be. The spread is first measured in the training rounds, on the certifying smoke's apps (section 9 item 5, v2.5.43),
and the power of the +/-10-point quality bound is computed from it as a stated assumption,
with the rest, before the freeze, then recomputed at the grid's first consistency check.
*v2.5.46:* the training rounds put it at about 41 points (41 apps). Quality is graded on the
quality sample, 60 apps a side, so shifts of about 0.6 standard deviations (about 24 points)
are resolved, and the +/-10-point quality bound, out of reach at that spread, is dropped.

**Run order and budget by tier**: each tier is a complete, publishable unit:

| tier | models | new runs | machine time | what it buys |
|---|---|---|---|---|
| 1 | Gemma + Qwen | 720 (+18 smokes) | ~76 h | the core paper: two labs, both with the full three-rung ladder |
| 2 | + Seed-OSS | +360 (+9) | ~54 h | third lab, third thinking dialect, third full ladder (its OFF rung rescued by the replay rule in section 4.2.1) |
| 3 | + gpt-oss | +240 (+6) | ~7 h | four labs. The "grew up SEEN" model, on its two rungs. *v2.5.9:* Magistral, the tier's other model until then, left the grid (section 5.1), taking +288 (+9) and ~10 h with it |
| 4 | + GLM *(v2.5.0)* | +360 (+9) | ~31 h | a fifth lab and template dialect (the sixth until Magistral left, v2.5.9). The roster's second mixture-of-experts model, and a keep-history flag of the opposite polarity to Gemma's and Qwen's (section 4.2.2) |
| 5 | + Qwen3.6-35B-A3B + Gemma-4-26B-A4B *(v2.5.5)* | +720 (+18) | ~52 h | two within-lab mixture-of-experts twins of tier 1's models: the roster becomes four dense and four mixture-of-experts models (three and four since v2.5.9), and the within-pair comparison is registered as exploratory (section 10) |
| 6 | + Muse Glimmer 30B *(v2.5.20)* | +240 (+6) | ~20 h | a sixth lab and a fourth dense model, back to four and four. A second model with no off-switch, on two rungs |

*v2.5.46:* tiers 1-5 are committed and tier 6 is optional. Grading the quality sample takes
about 180 hours for tier 1, 90 for tier 2, 60 for tier 3, 90 for tier 4 and 180 for tier 5
(about 600 in all), and 60 for tier 6.

*v2.5.15:* twenty replicates, at the pace of the nudge-rule smoke of 2026-09-27 (section 4.2). At
sixteen the new runs read 576, +288, +192, +288 and +576, and the machine time ~41 h
(measured), ~40, ~2, ~15 and ~49 h.

**The OFF arm as the built-in smoke detector.** Prior agent research (the
ReAct line of ablations) finds that agents deprived of any scratchpad fail
more, so OFF is expected to differ visibly from the thinking arms. That
expectation is what makes a null on the primary question interpretable: if
OFF -> UNSEEN moves the needle while UNSEEN -> SEEN does not, the lab has
demonstrably measured a reasoning-configuration effect and the visibility
null is a finding, *having* the thought matters, *remembering* it doesn't.
The awkward case is written down in advance: if OFF, UNSEEN and SEEN are
indistinguishable on every margin in every three-arm model, we cannot tell
"visibility doesn't matter" from "these tasks are insensitive to reasoning
configuration altogether", and the paper says exactly that. The OFF arm has
the same 120-a-side operating characteristics as the primary contrast, so it
is powered to detect the same sizes of effect.

---

## 7. What if the models disagree with each other?

They may well (six labs, six training recipes, six ideas about whether
a model should see its own thoughts) and **that is a result, not a
failure.** Think of testing a medication on five species: if it sedates cats
but not dogs, you haven't failed to conclude. You've learned the effect is
real *and* conditional, and the interesting question becomes what cats have
that dogs don't. Papers are made of exactly this.

What makes model-disagreement publishable rather than mushy is deciding the
rules **before** looking:

- Every model gets the same protocol and enough runs (120 a side) to stand
  alone: so "model A changes, model B doesn't" is two solid facts, not one
  fact and one excuse.
- The headline is written for every outcome in advance:

| pattern | headline |
|---|---|
| Effects in most/all models, same direction | Thought-visibility broadly changes agent behavior (the cleanest outcome) |
| OFF differs from the thinking arms. UNSEEN and SEEN don't | *Have the thought, bin the note*: generating reasoning is what matters and persisting it is bounded as unimportant, the most deployment-relevant outcome, and the one the ladder was built to isolate |
| Effects in some models, quiet in others | Visibility effects are **model-dependent**: we name which models, which margins, and the observable traits that go with them (for instance, if verbose thinkers pay a distraction tax, or if models trained with thoughts in their history destabilize without them). The paper is framed for this outcome from the start. |
| No effect anywhere, bounds tight | "Have the thought, bin the note": persistence is bounded as unimportant while costing a measured premium, direct deployment guidance |
| No effect, bounds loose | Undetermined. Reported honestly as such (the design makes this unlikely) |

- What would actually make the study inconclusive is none of these: it's
  the mistakes the fairness rules exist to prevent: deciding *after* seeing
  the data which models "count," running too few runs per model to
  characterize each one, or measures that shift mid-study. Avoid those and
  a mixed result is simply a map: *where* seeing your own thoughts matters,
  and where it doesn't. Venue-wise (IEEE Access), mixed and negative
  results are publishable when the method is airtight. A mechanism you can
  show in a trace is worth more than a uniform effect with no explanation.

---

## 8. Extension: frontier models over OpenRouter (optional, exploratory)

The same switch can be approximated for closed frontier models (Claude
Opus, GPT-5-class, Gemini) through OpenRouter, which exposes reasoning in a
standard shape (`reasoning` / `reasoning_details` on each reply, which you
may pass back on later turns: or withhold). That is our SEEN/UNSEEN switch,
API-style. Worth doing *after* the local study, labeled exploratory, because
the ground is less firm out there:

- **DeepSeek (considered and excluded (DeepSeek-V4-Flash).** It was the
  natural DeepSeek candidate: open weights (284B mixture-of-experts, 13B
  active) far too large to serve locally, but cheap and fast through the
  API), reasoning returned in the open, a real thinking toggle, native tool
  calling. It is excluded because **the experiment cannot be run on it as
  the vendor serves it**: DeepSeek's API documentation states that when a
  request includes tools, the reasoning from every previous turn *must* be
  passed back, and omitting it returns an error (HTTP 400). The UNSEEN arm
  is therefore not a configuration DeepSeek permits: the switch this study
  flips is welded to ON. (Thinking itself can be disabled, but that is a
  different switch and not the one under test.) Third-party hosts of the
  open weights reachable through OpenRouter would not enforce the rule, but
  running both arms there would require pinning a single provider, adapting
  the harness's reasoning field names, and re-proving the marker test on
  that stack. That effort is judged not worth a 24-run exploratory cell.
  What remains is the data point itself, which the paper reports: one of
  the largest open-model vendors has made "the model must re-read its
  thoughts" a hard API contract, not a default, precisely the design
  decision this study measures.
- **Gemini:** reasoning comes back openly -> both arms runnable. The clean
  frontier target.
- **OpenAI GPT:** raw thoughts are never shown, but *encrypted* reasoning
  blocks can be passed back or withheld, so we can still manipulate
  persistence without ever reading the thoughts. A lovely twist: visibility
  *to the model* without visibility to us.
- **Anthropic Claude:** thinking blocks are **required** to be passed back
  during tool use, the UNSEEN arm violates the API contract. That's not a
  dead end, it's a data point: for some providers, this experiment is
  forbidden by policy, which the paper should say out loud.

Honest caveats, plainly: no fingerprinting (the provider can change the
model under you mid-study), no temperature-0 guarantees, real money per run
(long agent runs are token-hungry), and rate limits shaping the schedule.
So: small n (e.g., 12 a side on 2-3 frontier models), clearly fenced as
"does the local finding echo at the frontier?", never pooled with the
registered results.

---

## 9. Checklist, in order

0. **Freeze the code and the machine.** Commit the harness (`eval-coding-agent`)
   and tag it (`study-freeze`). Every real run's manifest must then show the
   same `harness_git`, and the harness is not edited until the last run. The
   grader (`tasks/rubrics/` in the same repository: the rubric cards, their rules and the
   scripts that go with them) is committed in the same tag (v2.5.48:
   `model-reasoning-visibility-plan-freeze-101926`, both `study-freeze` and `grader-freeze`) at the end of its calibration's training rounds
   (item 5, v2.5.43), before any grid app is graded, and is not edited
   after that either. The precedents log is kept beside the grades, outside it
   (v2.5.18). (The
   per-reply client timeout is already 3,600 s, section 4.4.) Confirm the engine
   sees the GPU: `llama-server.exe --list-devices` lists `CUDA0`, with the
   three CUDA runtime DLLs beside the .exe (section 4.3). Pin the Node version
   (`nvm alias default`) and set the npm `before`
   date and `prefer-offline` (`npm config set prefer-offline true`: the
   smokes warm the cache so real runs rarely touch the network). On the
   Windows side, pause Windows Update for the batch's duration (a driver or
   feature update mid-batch changes the serving stack, a forced reboot kills
   a run), disable sleep, and reserve the machine's LAN address in the
   router so the server's IP cannot move mid-batch. Nothing else may use
   ports 3000, 5173-5175 (the apps) or 7777 (the server). **Check Smart App
   Control**: `reg query "HKLM\SYSTEM\CurrentControlSet\Control\CI\Policy" /v
   VerifiedAndReputablePolicyState`, where `1` is enforced. On 2026-09-23 this
   machine ran all 42 smokes on b10964, was shut down, and came back with SAC
   committed from evaluation to enforced. From that boot the Windows loader
   refused every unsigned binary in the engine folder (51 of its 54) and
   `llama-server.exe` exited `0xC0E90002` *before* `main()`, printing nothing at
   all. No stdout, no stderr, an empty log, a health check that never went
   green: from the runner's side, indistinguishable from a model that failed to
   load, and three hours to tell apart. SAC has no per-app exclusion, so the
   only lever is off. Since KB5083769 (2026-04-14) it can be turned back on
   without reinstalling, so turning it off for the batch and back on afterwards
   is the sane course. Note the diagnosis is not where anyone looks first: SAC
   blocks land in `Microsoft-Windows-CodeIntegrity/Operational` as event 3077,
   **not** in the Application log, and they are not Defender detections, both
   of those come back empty and look reassuring. The engine preflight added in
   v2.3.15 (`llama-server.exe --version` must identify itself before any run or
   probe starts, in both `run_one_with_server.sh` and `template_probe.sh`) turns
   this whole class into one line of output, and it matters most in the case
   nobody would catch by hand: a policy flip at hour 40 of a 75-hour grid.

   **Two items are open at v2.4.4, before the tag.** First, retries are not recorded. A
   read timeout does not fail a call: the client re-sends it, up to five times, and
   generation restarts from zero, and no manifest field records that it happened. So a
   run in which a runaway reply was timed out and re-rolled into a short one reads as a
   clean run, and cannot be found afterwards (section 4.4.1). Record the retry count per run, and
   gate any set that contains a timeout retry. Second, the harness now prints a heartbeat
   every 30 s while a reply is outstanding, a line when each tool call is applied, and a
   line when tool results are sent back: print-only by construction, but they change
   `harness_git`, so the smoke set that certifies the grid must be regenerated after them,
   as after every harness edit before them.
   *v2.5.8: the first is closed.* `harness/llm.py` keeps a record of every retried call and
   `harness/agent.py` writes it into the manifest as `api_retries`: `count`, `timeouts`, and
   one event per retry, the call (the step, one call per step), the retry number, the kind
   (`timeout`, `connection`, `http_<code>` or `server_crash`), how long the failed attempt ran
   and the wait before the next. It is written in the same place as `api_error`, so a run
   that dies after exhausting its retries still records them, and it is always present,
   empty when nothing was retried. A timeout also prints a line saying the reply is being
   re-rolled. `verify_smokes.py`'s gate G16 fails any set containing a timeout retry, and
   any run with no `api_retries` field (made before the record existed) unless
   `--no-retry-record` is passed, as `--budget` exists for the 8M-era sets. Connection
   drops, HTTP 5xx and a crashed server reloading are listed in its line, not failed, being
   random infrastructure events where a timeout falls on exactly the longest replies.
   `test_retry_record.py` pins the record offline: a read timeout, an HTTP 503, a retry
   budget that runs out, and one run end to end through `harness.agent`'s own entry point
   against a scripted local server, whose manifest must carry the event.
   *v2.5.5:* both are still open, and a third joins them. Before the tag, replay one of
   Qwen3.6-35B-A3B's lost-call requests raw (its recorded request through
   `/apply-template`, then the prompt through `/completion` a few times) and record whether
   the model writes a whole call before `</think>` that the server's parser then loses, or
   only the closing tags (section 5). If the parser loses calls, it is an engine fault that falls
   on one arm, and how such runs are counted is settled before the freeze, not after it.
   And because the retry record is a harness change, the full re-smoke that certifies the
   grid comes after it, or it has to be made twice.
   *v2.5.12:* the commit and the tag must take in `run_one_with_server.sh`,
   `run_thinking_batch.sh` and `decoding-registry.json`, which were still untracked at
   `a110393`. The wrapper decides what every arm sends and the registry how every model is
   sampled, and `harness_git` sees only tracked files and `harness/`, so until they are
   committed a change to either would leave no trace in any manifest.
   *v2.5.13:* `b2a401d` took in the wrapper and the batch driver, the latter renamed
   `run_thinking_batch.sh`. Still to go in: `decoding-registry.json`, untracked yet, and
   the v2.5.13 change (`harness/tools.py` and `harness/agent.py` with their backups in
   `harness/`, `run_thinking_batch.sh` and `CONDITIONS-CHANGES.md`) because `harness_git`
   reads any uncommitted change to a tracked file anywhere in the repository, and any
   untracked file in `harness/`, as dirty. The certifying smoke comes after that commit.
   *v2.5.14:* `543d0e2` took in the v2.5.13 change, and the 20M smoke was made from it.
   Still to go in: `decoding-registry.json`, still untracked, and the v2.5.14 change, 
`harness/agent.py` with its backup in `harness/`, and `CONDITIONS-CHANGES.md`. The next
   certifying smoke comes after that commit.
1. Registry entries + sha256 fingerprints for all eight models' study files.
2. Wire each model's thinking switch through `ARM=` in the run wrapper (never
   by hand-typed bodies) and run thinking canaries **both ways**, judged on
   reasoning *length*, not presence:

   - **OFF passes** when no step in the run carries a reasoning field longer
     than 200 characters. Presence alone is not a failure: the largest pure
     template artifact observed is Seed-OSS's 159-character budget-reflect
     stub, and a presence rule would have wrongly failed it. *v2.5.4:* one step of
     Gemma-4-26B-A4B's smoke fails this rule without thinking (the field holds a
     `finish` call's arguments and the tool's name) and whether that step is waived
     or the rule refined is open (section 5). *v2.5.5:* refined. A reasoning field whose whole
     text is a tool call (the JSON arguments of one of the harness's tools, optionally
     fenced, wrapped or followed by the tool's name, or nothing but tool-call markup) is a
     call filed in the wrong field, not thinking. It counts as no reasoning in every
     canary, G2 lists it, and the step is counted (section 10, eighth). A field that mixes prose
     with a call is still reasoning.
   - **ON passes** when at least one step carries more than 200 characters of
     reasoning *and* reasoning appears on at least a fifth of the run's steps.
     Note the deliberate looseness of that second clause: in the smoke set
     Qwen reasoned on 100% of SEEN steps but only 62% of UNSEEN steps, which
     is a downstream effect of the treatment rather than a manipulation
     failure (section 10), and a rule demanding every step would have voided a real
     result.
   - **Reasoning must reach the reasoning field.** No step in any run may
     contain an opening `[THINK]` or `<think>` marker in its *content*: that
     would mean the server's parser failed to split the turn and the chain of
     thought is sitting in the visible text, where the UNSEEN arm cannot strip
     it and the manipulation is silently null. Trailing *closing* markers are
     a known Magistral cosmetic artifact (section 4.2.1) and do not fail the canary.
   - **A third rule, added after Seed-OSS:** an OFF configuration that leaves
     the model producing turns with neither text nor a tool call at a rate
     that prevents runs from completing does not have a usable OFF arm,
     whatever the reasoning field says. That model drops to two arms and the
     plan records the switch as tested-and-rejected.

   A model whose OFF canaries fail runs two arms. gpt-oss and Muse Glimmer have no
   off-switch and stay two-arm. (Magistral's OFF configuration was the absence of its registered
   thinking preamble, section 4.2.1, it left the grid in v2.5.9.)
   *v2.5.14: one departure, on the record.* Gemma-4-26B-A4B's OFF canary failed in two
   smoke sets running: at 12M a runaway filed as reasoning, and at 20M 1,213 characters of
   planning prose after the model opened its thought channel (section 4.1). The study lead keeps
   the arm, waived and watched: its OFF reasoning is counted per model in the grid, and
   `verify_smokes.py` lists its over-length OFF runs under the waiver instead of failing G2.
   Any other model's OFF canary still fails the gate.
   *v2.5.16: how the canaries are read.* Each reads the run's trace, where every step
   records what the server returned: the visible text, the reasoning field and the parsed
   tool calls. They are gates G2, G3 and G4 of item 3b. The protocol's section 5.1 sets them out in
   full. The 200-character line is applied to a run's longest step, and it has room on both
   sides: in the nudge-rule smoke of 2026-09-27, whose gates are still to be set out, no
   Seed-OSS OFF step was longer than 134 characters and no other OFF step carried any
   reasoning, bar one waived Gemma-4-26B-A4B runaway of 93,180 characters, while every one
   of the 42 thinking-arm runs had a step of at least 608 characters. Many thinking steps
   are short (the median, by model and arm, ran from 106 to 512 characters and was under
   200 in 8 of the 14) which is why ON asks for one step over the line per run and counts
   reasoning of any length toward its fifth. The lowest rate of any thinking-arm run was
   29%, in a Seed-OSS UNSEEN run. G4 checks `<seed:think>` as well as the two markers named
   above (and, since v2.5.19, Muse Glimmer's `to=self` header) and, since v2.5.37, every
   closing think marker and the channel markers of Gemma 4 and gpt-oss as well, in the reply
   text as the harness kept it. The harness by then moves reasoning the server left in the
   text to the reasoning field, so a marker still there is a split it missed (v2.5.37). A misfiled call is set aside even on a step that also made a call, but G2 lists one
   only in an OFF run and only when it would have crossed the line, and `callTxt` counts
   only steps that made no call. The third rule is a judgement, not a computed gate: it is
   read from the gate report's descriptives, which count per model x arm the turns with
   neither text nor a tool call and how each run ended. 3. **Marker test per model, both
   directions**, archived: run with `--model-key`, so the probe sends the wrapper's own
   thinking-arm body (v2.5.0). A model that fails is replaced by a standby if section 5 names one
   by then (after the section 5 checks, not before) or dropped with its slot reported empty. As
   of v2.5.1, section 5 names none. **Done** (v2.5.36): all eight ACCEPTED, Muse Glimmer on
   2026-09-30, the other seven on 2026-10-05. 3a. **Prove the arms differ in the prompt, per model**
   (`template_probe.sh`, section 4.2.2). Every check in item 2 reads what the model *emitted*. This
   one reads what the model was *given*, which is the other half and the half that can be
   silently null. One of the six distinct templates (eight models, each twin serves its
   sibling's) has no slot for the reasoning field under that name: gpt-oss's, which
   llama.cpp bridges (section 4.2.2). Magistral's, while it was in the roster, had none at all: 
and with a template like that the UNSEEN and SEEN prompts can come back byte-identical
   while every manifest faithfully records that the reasoning was sent. A model whose two
   thinking arms render the same prompt does not run its grid.

3b. **Run the gates.** The gates of items 2 and 4 are implemented in
   `verify_smokes.py`, which reads the runs rather than the summary table and
   fails loudly instead of reading fine.

   *v2.5.16: how the gates work.* The script finds every run under the root that has a
   trace and reads two files from each: the trace's response rows, one per step, with what
   the server returned, and the manifest, where the harness records how the run was
   configured and how it ended. The arm comes from the run id. Where a gate compares a run
   with an expected value (the body each arm must send, the replay route, the preamble) 
the script states that value itself rather than taking it from the wrapper, so that a
   change to the wrapper cannot carry the check along with it. The samplers are the
   exception, which G15 reads from the same registry file the wrapper reads. It prints one
   line per gate: `pass`. `FAIL` with each failure, be it a run, a model, a model x arm or
   a value that differs across the set, or `WAIVE` with what a registered waiver covered: 
exits with the number of failed gates, and ends by giving that number and how many gates
   passed only by a waiver. The descriptives and the table of every attempt follow, never
   gated. The tables below list all sixteen gates, grouped, as in the protocol's section 5.1, by
   what each protects. Until v2.5.16 this table listed twelve, leaving out G11, G12, G13 and
   G15.

   *The arm reached the model as registered.*

   | gate | passes when | what it guards against |
   |---|---|---|
   | G1 | every SEEN run records `reasoning_replayed=true`, and every UNSEEN and OFF run `false` | the one switch that separates SEEN from UNSEEN set wrongly: a run made with an older wrapper, or an arm mislabelled. OFF is replay-off by rule (section 4.2.1), so an OFF run recording `true` fails too |
   | G8 | a model's UNSEEN and SEEN runs all sent the same template switches (`extra_body`) | the two thinking arms differing in anything but replay |
   | G11 | every run sent exactly the body registered for its model and arm (section 4.2.2) | the arms agreeing with each other (G8) yet all being wrong: a misspelled switch or a missing keep-history flag draws no error, because a template ignores variables it does not read |
   | G12 | every run records the replay route frozen for its model (`replay_format=field`, a replayed thought travelling in the `reasoning_content` field) the same for every model | SEEN's reasoning sent by a route the template does not read, which drops it and leaves SEEN no different from UNSEEN |
   | G5 | no OFF run carries a thinking preamble, and a model's two thinking arms carry the same one | the primary contrast varying the system prompt |
   | G13 | every run carries the frozen preamble: none, for every model | the arms agreeing on a preamble (G5) that is not the registered one |
   | G15 | every run was configured from `decoding-registry.json` and recorded the samplers it gives the run's model and mode (section 4.4.1): thinking for UNSEEN and SEEN, non-thinking for OFF. A model's UNSEEN and SEEN runs were sampled alike, and the set used one version of the registry | a sampler lost on its way from the registry through the wrapper to the harness, or the thinking arms sampled differently: the primary contrast must vary only what the model can see |

   *The model did what its arm says*: the canaries of item 2.

   | gate | passes when | what it guards against |
   |---|---|---|
   | G2 | no OFF step carries more than 200 characters of reasoning, misfiled calls set aside: *waived for Gemma-4-26B-A4B-it*, whose over-length OFF runs are listed under the waiver (section 4.1). Any other model's fail | thinking with thinking switched off |
   | G3 | each UNSEEN and SEEN run has a step with more than 200 characters of reasoning, and reasoning of any length on at least a fifth of its steps | a thinking arm that is not thinking |
   | G4 | no step's reply text, as the harness kept and replayed it, contains a think marker, opening or closing (`<think>`, `</think>`, `<seed:think>`, `</seed:think>`, `[THINK]`, `[/THINK]`), a channel marker (`<|channel>thought`, `<channel|>`, `<|channel|>`, `<|message|>`), for Muse Glimmer `to=self`, or (since v2.5.38) any roster template's turn-structure marker (`<|im_start|>`, `<|im_end|>`, `<|turn>`, `<turn|>`, `<|start|>`, `<|end|>`, `<|return|>`, `<|call|>`, `<|eot|>`, `<|eom|>`, `<|system|>`, `<|user|>`, `<|assistant|>`, `<|observation|>`, `<seed:bos>`, `<seed:eos>`) | reasoning left in the visible text, where UNSEEN cannot strip it, or output the server mis-split: a split the harness missed (v2.5.37) |

   *The set was made under one configuration.*

   | gate | passes when | what it guards against |
   |---|---|---|
   | G6 | the base prompt, the briefing and `harness_git` each have one value across the set, and each task one task hash | runs from different code or inputs mixed in one set. `harness_git` is the harness commit, marked dirty when a tracked file has uncommitted changes or `harness/` holds an untracked file, so an edit made during a set shows |
   | G7 | every run's model and quantization label resolved to an entry in `quant-registry.json` (`quantization_detail.status=ok`), which the manifest copies with the file's sha256 and size | a run whose weights cannot be traced to a fingerprinted file. That the server loaded the intended file is checked by the wrapper before every run, not here: the server's `/props` must name it |
   | G10 | every run recorded the 20,000,000-token budget (`max_total_tokens`) | a set made at another budget, which nothing in a run's outcome would show |

   *No run was cut short or lost by the instrument.*

   | gate | passes when | what it guards against |
   |---|---|---|
   | G9 | no run's token count (prompt and reply tokens summed over all its calls) exceeds the budget or comes within a fifth of it (over 16,000,000): *waived for a run that reached the budget while looping*: `token_budget_exhausted`, with its last 30 tool calls at most 3 distinct once every number in them is masked | a budget that cuts runs short, so that it, not the model, decides how they end. A run that reaches it while looping is an outcome, not a run the budget censored |
   | G14 | every run that ended in an API error has a cause (output its server could not parse, or a server crash) and no model x arm loses more than a third of its runs to unparseable output | voids that are not missing at random: their chance depends on what the model writes, which is what the arms manipulate (section 10, fifth). With three runs per model x arm, one such void passes and two fail |
   | G16 | no run records a retried call that had timed out, and every run records its retries (`api_retries`) | a timed-out call re-sent and regenerated from zero: timeouts fall on the longest replies, so a re-roll silently replaces exactly those. Other retries (a dropped connection, a server error) are listed, not failed |

   G10 exists because it fired the first time it was run: the plan said 8M
   while all 42 smokes had been made at `run.sh`'s own 6M default, and nothing
   in the summary table showed it. Run it after every smoke set and before the
   freeze. `--budget N` verifies a set made before a budget change, so a gate
   that no longer applies does not become a gate people learn to ignore.
   *v2.5.9:* after the gates, `verify_smokes.py` now counts every attempt, failed ones
   included, per model x arm and by cause (the batch driver keeps each failed smoke attempt
   under `<condition>/failed-attempts/` rather than overwriting it) and prints what the model
   wrote whenever its server could not parse it (section 10, fifth). It is reported, never gated.

   ```bash
   cd /mnt/d/thinking_research_runs && python3 verify_smokes.py smokes
   ```

4. **Smoke runs** (one per arm per condition, per model): confirm every
   block runs cleanly, calibrate machine time and the context windows,
   settle the token budget, and read the longest single-step duration
   against the client timeout. Verify from the smokes' traces and manifests that the
   task, prompt and briefing hashes are the ones this plan freezes, that
   every OFF and ON run passes the length canary in item 2, that
   `think_preamble_key` is the one its arm calls for, and that
   `reasoning_replayed` matches the arm. Interrupt one smoke on purpose
   (Ctrl-C) and re-run the batch command: the server must be gone
   (`tasklist.exe | grep -i llama` shows nothing) and the batch must resume
   at the right line. Excluded from analysis by design.
5. **Calibrate the rubric** (v2.5.18, section 4.5).
   - **First the tools,** all in the grader:
     - the score sheet.
     - a merge that keeps each app's first grading as its score, accepts
       only pass, fail and skip, and reports consistency on the re-grade
       set: the mean absolute difference between an app's two gradings (the
       bar), the intraclass correlation, and Cohen's kappa beside raw
       agreement per item.
     - `grade_setup.sh`, taking a blind id, finding the run itself,
       recording nothing but the id, and removing the database the app
       shipped with before it installs.
     - the seeded draw that picks the re-grade set and gives each of its
       apps a second blind id, and the script that makes the grader's
       unmarked, shuffled lists, adding a second id only once its 14 days
       have passed.
     - `seed_card.py` beside the cards.
   - **Then the rounds.** Every calibration app is first copied under a
     fresh random id.
     - **Training rounds,** small at first, use the certifying smoke's apps (all 66, then if needed this study's earlier
       smoke apps, each once).
     - **No separate deciding round** (v2.5.43): the cards are frozen when the
       training rounds leave no call unclear, and the grid's first
       consistency check is the first measure of their consistency.

     The quality scale is then fixed before any grid app is graded. Grid
     runs may be made before the grader freeze (v2.5.25).
6. Registration freeze: hash this plan, the run schedule, the analysis code
   (written and tested on fake data first), and the two tags (the harness's
   `study-freeze` (item 0) and the grader's `grader-freeze` (item 5, the rubric
   cards included)) with the precedents log as it then stands. Optional
   public timestamp (OSF).
   Back up `blind-state/` (the id ledger and the un-blinding key are the
   only link between a blind run and its cell: copy them off the machine
   after every batch, not only at the end).
7. Tier 1 grid (Gemma + Qwen). Grade it. Its re-grades join the lists as
   their 14 days pass (section 4.5).
   Analyze. 8. Tiers 2, 3 and 4 as budget allows. 9. Frontier extension if desired. 10. Write the paper.

---

## 10. Fine print (validity rules and analysis, for reproducibility)

The frozen serving and agent settings are the tables in sections 4.3 to 4.4. This
section is what happens to a run once it exists. Every run carries its
fingerprint check, marker-test verdict, guard values, and the switch's
actual state in its manifest. A run is **void** only for infrastructure
faults (server crash or reset, wrong file served, any recorded setting
differing from section 4, the npm registry unreachable during the run (network
errors such as `ENOTFOUND` / `ETIMEDOUT` / `ECONNRESET` in `console.log`
around an install, which the agent would otherwise be left to "debug")) 
never for behaving badly, which is data: loops,
no-action stops, budget exhaustion and context-overflow deaths are all
*outcomes*. Overflow in particular is not an accident to be retried, because
keeping thoughts visible fills the context faster: that asymmetry is part
of what's being measured. A void run's slot is re-run (at most twice), with
the reason logged.

Two things the smoke set surfaced are registered **here, in advance, as
descriptives rather than outcomes**, because both could otherwise be
discovered in the data and written up as findings.

First, **how often a model thinks is itself affected by the treatment.**
`reasoning_turns / steps` is recorded per run and reported per model x arm.
In the smoke set Qwen reasoned on 100% of its SEEN steps but only 62% of its
UNSEEN steps, while Gemma reasoned on essentially every step in both. The
plausible mechanism is that a model conditions on its own visible history: if
each past turn shows thinking, it keeps thinking. So if a visibility effect
appears in Qwen, part of it may travel through *how often it thinks* rather
than through *what it can see*: a mediation this design cannot separate, and
the paper will say so rather than implying a single mechanism. *v2.5.4:* the twins' smokes,
made after this was registered, reverse their siblings' patterns: Qwen3.6-35B-A3B reasoned
on 96% of its UNSEEN steps, and Gemma-4-26B-A4B on 80% where the 31B reasons on 99% (section 5).
Recorded, not counted.

Second, **the treatment is not the same size in every model**, and its size
is recorded rather than assumed. `reasoning_chars / step` in the UNSEEN arm is
exactly the quantity that arm withholds, and it varies by an order of
magnitude across the roster: a median of 276 characters per step for Gemma, 85
for Qwen, 154 for Seed-OSS and 486 for Magistral under the vendor preamble,
where the content field is otherwise empty and essentially all of the model's
prose is reasoning. GLM, added in v2.5.0, reads 127 on its own nine-run smoke, and the twins (v2.5.4) read 241
(Qwen3.6-35B-A3B) and 493 (Gemma-4-26B-A4B) on theirs. A
visibility effect that appears in one model and not
another may therefore be a difference in how much text the arms differ by, not
a difference in kind. The number is reported per model x arm alongside every
contrast.

Third, **two shapes from the smoke set are written down here, before any grid
run exists, so that finding them later is confirmation rather than
discovery.** Neither is a result: three runs per cell prove nothing, and the
smokes are excluded from analysis by design. Registering them is what makes
them worth anything if they reappear.

*Seeing seems to substitute for producing.* In four of the five models the
SEEN arm generated **less** new reasoning per reasoning step than the UNSEEN
arm: gpt-oss 989 -> 38 characters, Gemma 422 -> 104, Magistral 374 -> 319, with
Seed-OSS the exception in the other direction at 167 -> 337. The natural
reading is that a model which can see what it already worked out does not work
it out again. If it holds at scale it is a mechanism rather than a nuisance,
and it is reported per model x arm. GLM's nine-run smoke, made after this was registered,
reads 127 -> 122: flat. It is recorded here, not counted for or against the shape. The
twins' smokes (v2.5.4) read 241 -> 135 for Qwen3.6-35B-A3B and 493 -> 175 for
Gemma-4-26B-A4B, both in the shape's direction, and are recorded on the same terms.
Magistral's reading stays as recorded. It left the grid in v2.5.9, so the grid's test of the
shape is on the seven models that remain, and on Muse Glimmer, the eighth since v2.5.20.

*Qwen's ladder may not be monotonic.* Its UNSEEN arm was the worst of its
three rungs, not the middle one. It reasoned on 37% of steps against 100% in
SEEN, produced the only silent turns in the entire 42-run set (4 of 146), and
two of its three UNSEEN runs ended `stopped_no_tool_call` while all six of its
OFF and SEEN runs finished. Thinking that cannot be seen being *worse than not
thinking at all* is precisely the shape the third rung was added to detect: 
and precisely the shape that would look like a fishing expedition if it were
first mentioned after the grid had run. *v2.5.4:* Qwen3.6-35B-A3B, the 27B's
mixture-of-experts twin, shows the same shape on its own smoke (OFF and SEEN three of
three, UNSEEN one of three) by another route: it reasoned on 96% of its UNSEEN steps, and
the turns it lost carry a tool call's closing tags in the reasoning field rather than
nothing at all (section 5). Recorded, not counted: the shape was registered for the 27B, and the
twin is another model. *v2.5.14:* again, in the 20M set, Qwen3.6-27B finished 1 of 3 UNSEEN
runs against 3 of 3 in OFF and in SEEN, and both losses ended on two turns with neither text
nor a tool call, each of the four a single token, the end of the turn. The rendered prompt
suggests a mechanism. In UNSEEN, where reasoning is not sent back, Qwen's template writes every
earlier turn with an empty think block and opens a new one for the reply, a transcript in which
the model apparently never thinks. Four times it closed the turn inside the open block. Across
the 20M and 12M sets, 18 of the 21 turns with neither text nor a tool call came in UNSEEN, none
in SEEN. Recorded, not counted.

*gpt-oss may end differently when it can see its reasoning (v2.5.12).* In the gpt-oss probe
and the smoke together, its voids came in equal numbers per arm but split by kind. The tool
name written into the channel slot came 4 times in UNSEEN and 2 in SEEN. The closing summary
written on the `final` channel with a stray `<|constrain|>` (twice as an attempt to call
`finish` from there) came only in SEEN, 3 times of 3, each in an `interactive` run as it
wrapped up. The fifth UNSEEN void opened a channel with no name at all. In the probe, SEEN also stopped without a tool call in 2 runs and UNSEEN in none,
with 8 turns without a call against 2. The reading registered: the model that grew up seeing
its reasoning (section 5) is likelier to close a run through its answer channel when it can see it.
Recorded, not counted. The grid, with every arm in every cell, tests it. *v2.5.14:* a
reading against it, in the 20M set, gpt-oss's one failed attempt tried to close its run
through the final channel, `<|channel|>final <|constrain|>finish...`, in UNSEEN.

Fourth, **the primary contrast is reported a second time over zero-nudge runs only.**
The harness's finish nudge is a `role: user` message, and Gemma's and Qwen's templates
gate a past turn's visible reasoning on the position of the last user message (section 4.2.2).
`preserve_thinking` closes that hole for turns that made tool calls. It does not close it
for a turn that made none, which is the very turn that triggers a nudge. So a nudged SEEN
run carries a marginally weaker treatment than an unnudged one. `finish_nudges` is already
in every manifest. The headline estimate uses all runs. The sensitivity estimate drops any
run with `finish_nudges > 0` from both arms of the contrast, and both are reported. If they
disagree, the nudge is doing work and the paper says so. *v2.5.14:* a run can now be nudged
more than once (sixth, below). The sensitivity estimate still drops every run with any nudge.

Fifth, **one operating fact from the smoke set survived scrutiny and one did not.** The
first reading of the 2026-09-22 smokes said Magistral returns a turn with no tool call on
15% of its steps against 1-3% for every other model, and that most of its runs would
therefore be too short to grade. That figure came from 61 steps across nine runs and was
dominated by two 2-step runs in which both steps failed. Twenty runs at one cell put the
rate at about **3%** (in line with gpt-oss) and every one of the ten made with the
preamble the study actually uses finished. The 15% is not reported. What is worth keeping
from it is the shape: Magistral's no-tool turns concentrate almost entirely at **step 1**,
where the three arms are byte-identical, so whatever rate it settles at adds noise to every
arm equally rather than biasing the contrast between them.

And gpt-oss produced one HTTP 500 from llama.cpp's harmony parser (*"the model produced
output that does not match the expected peg-native format"*) in 6 smoke runs. That is an
infrastructure fault and voids the run under the rule above. The batch driver already
retries up to three times before voiding. If the rate holds it costs roughly one run in six
for gpt-oss, which the retry budget absorbs, but a materially higher rate in the grid is a
reason to stop and look rather than to keep re-running.
*v2.5.9: this void is not an infrastructure fault, and it came back under the v2.5.6 briefing.* The server's
parser refuses what the *model* wrote, so the chance of such a void depends on what the model
generates, which is what the arms manipulate: these runs are not missing at random, and
`verify_smokes.py` counts them per model x arm, failing any arm that loses more than one run
in three to them (G14, section 9). Under the study's sampling and the original briefing gpt-oss had
not produced one (none in the 12M set's six runs, none across 51, section 4.4.1). On its re-smoke
under the v2.5.6 briefing (section 4.1) it lost two of six runs to it, one in each arm (UNSEEN in
`message-board x execution`, SEEN in `kanban-board x interactive`) each failing all three
attempts: 6 of the 8 attempts at its `execution` and `interactive` runs. They were the two
runs in which it ran commands, and both failed after 36 and 32 steps, where no other gpt-oss
run in either set went past 21. What it wrote is in the server logs:
`<|channel|>functions.list_dir to=assistant<|channel|>commentary json<|message|>{"path": ""}` in
the first, and in the second its closing message,
`<|channel|>final <|constrain|>commentary<|message|>Implemented a full collaborative Kanban board:...`.
The briefing is withdrawn, so the certifying re-smoke is the reading that counts. And since
v2.5.9 the batch driver keeps every failed attempt instead of overwriting it, so that reading
and every one after it is taken **over attempts, not slots**: a slot that parses on its
second attempt has still failed once, and three attempts per slot would otherwise filter the
failure out of exactly the arm that suffers it more. The rule above stands: a materially
higher rate in the grid is a reason to stop and look.
*v2.5.10:* the briefing is reinstated (section 4.1), so the next reading is the smoke of all seven
grid models under it. A gpt-oss arm that loses more than one run in three there fails G14,
and gpt-oss is set out for the decision section 4.1 registers.
*v2.5.11: every retry of a smoke slot is a replay.* gpt-oss's six runs in the all-model smoke
repeat its re-smoke, made hours earlier, response for response, and each retry of its
two failing slots repeats that slot's first attempt: the same `list_dir` call with `to=assistant`
in the channel slot, the same closing message with `<|constrain|>` in it. In the classic smoke
layout every attempt of a slot sends the same prompt, workspace path included, with the same
per-replicate seed, and on this engine that yields the same tokens: so a retry cannot recover a
failure the model caused, only repeat it, and a slot's three attempts are one failure.
`verify_smokes.py` now marks a replay and counts distinct failures. The void rate above is
therefore two distinct failures in six runs, one in each arm. It is not a rate over attempts
until the attempts differ. In the blind layout each attempt draws a new random workspace path,
so a retry there is a new draw.
*v2.5.12:* the probe of section 4.1, 24 runs each made once, 8 voids, 4 of 12 in each arm, eight
distinct failures.
*v2.5.14: a replay holds only until a tool result differs.* In the 20M set gpt-oss's one
retry repeated its first attempt exactly for five steps. The sixth request differed only in
npm's error message, which names its log file by the time it was written, and from there the
retry went another way and finished, where the first attempt had failed at step 45. Command
output carries times and process ids (npm's log names, PIDs, durations) so a run that
executes commands replays its predecessor only until the first such result. A
`no_verification` run, whose tool results depend on nothing but its own calls, replays
exactly: the nine that the file-state note reached got it at exactly the step the replay of
the 12M set predicted. So a slot's attempts are one failure only when they are identical,
which `verify_smokes.py` checks by fingerprint rather than assuming.

Sixth, **a turn with neither text nor a tool call is an outcome, not a
fault.** The harness nudges after every turn without a tool call and ends the run
only when the reply to a nudge has none either (v2.5.14). Such runs are analyzed, not
voided. The single exception
is the canary rule in section 9 item 2: a configuration that silences a model often
enough to stop runs completing is a broken *arm*, and the arm is dropped
before the grid rather than after it.
*v2.5.14:* until then the harness nudged once and ended the run on the second such turn,
wherever it fell. In the 20M smoke that ended three runs whose two such turns were 4, 7 and
21 steps apart, the model working normally between them: one of them right after a diff had
shown it the one-letter difference that was its bug. Since these turns come almost all in
UNSEEN (third, above), the rule decides where their cost shows: under the old one in runs
ended, under this one in the count of turns without a tool call and in steps, which are
reported per model x arm.

Seventh, **architecture is reported, never tested.** The roster mixes dense and
mixture-of-experts models on purpose (section 5), with two sparse models (gpt-oss, and GLM as of
v2.5.0) against four dense ones, so a claim such as "the visibility effect is larger in MoE
models" would rest on n = 2 and is not made. Architecture (dense or mixture-of-experts,
and routed-of-total experts as read from each GGUF header) is listed per model beside
every result, and
nothing more. *v2.5.2:* if the two proposed twins (section 5) enter the grid, the roster becomes
four dense and four mixture-of-experts models, with two within-lab pairs among them (three
dense and four since Magistral left, v2.5.9, four and four again with Muse Glimmer, v2.5.20). That
changes the counts, not this rule: a within-pair comparison is a new analysis, and if it is
wanted it is registered before the freeze (as exploratory, with the pairs' confounds
(active size, quantization recipe) stated) or it is not reported as a comparison at all.
*v2.5.5: registered, as exploratory.* The twins are in the grid, so the comparison is fixed
now, before any grid run. Within each pair (Qwen3.6-27B with Qwen3.6-35B-A3B, Gemma-4-31B
with Gemma-4-26B-A4B) and for each registered contrast and measure below, the report gives
the twin's estimate, the sibling's, and the twin's minus the sibling's (a ratio of ratios for
steps), with a 95% interval from a stratified bootstrap (strata = task x condition, 10,000
resamples, fixed seed). No test is run on the difference, no p-value is reported for it, and
it sits outside the Holm families. Every such number is printed with the pair's confounds: a
tenth of the active parameters, a different quantization recipe (`UD-Q4_K_M` against
`Q4_K_M`), a capability gap on the vendors' own benchmarks, and for the Gemma pair a
different context window (131,072 against 65,536), which is inert for every run that stays
below the smaller one, the number of the 31B's runs that come within 10% of it is reported
beside it. A difference of two effects carries about 1.4 times the standard error of either
model's own effect, so only large differences can be resolved. And the comparison speaks for
two pairs only: no claim is made about mixture-of-experts models in general, and the other
four models (Seed-OSS, gpt-oss, GLM and Muse Glimmer) which have no sibling here, stay out
of it.
Relatedly, **a per-request seed is not a replay key.** A re-run of a Granite
smoke run under the same run id, and so the same derived seed, had diverged from the
original by step 10, laying the app out differently (section 4.4.1, its per-reply cap also
differed, so this does not isolate GPU non-determinism). Replicates are analysed as
independent draws, which the stratified permutation tests below already assume.
Seed-matched runs in different arms are not treated as pairs. *v2.5.11:* on gpt-oss a
seed is a replay key after all: a byte-identical prompt with the same seed replayed a 36-step
run exactly, in all three attempts of the all-model smoke and in the re-smoke hours before it
(fifth, above). The Granite re-run
had also changed its per-reply cap. Nothing in the analysis changes (replicates were never
paired) but a smoke retry is a replay, and it is counted as one.

Eighth, **a tool call written as text is counted, not guessed at** (v2.5.5). In the latest
smokes, models wrote calls instead of making them: the arguments of `finish` in the reasoning
field (Gemma-4-26B-A4B, OFF), a call's closing tags left in its reasoning (Qwen3.6-35B-A3B,
UNSEEN, three times), a `finish` payload fenced as JSON in its prose (Gemma-4-31B once in
UNSEEN, Magistral once in SEEN), a Mistral call without its opening `[TOOL_CALLS]` token
(Magistral, OFF). Each is a turn without a tool call, which this section already counts as
an outcome, never a fault.
What is added is the count: `callTxt`, the steps with no parsed call whose reasoning or
content holds one written as text, reported per model x arm. If it differs between UNSEEN
and SEEN, that difference is part of the visibility effect and is reported as such. A
reasoning field that is nothing but a call is also kept out of every reasoning measure
(section 9 item 2), so it cannot pass for thinking.

Ninth, **whether a run checks its own work is reported per model x arm** (v2.5.5). The
latest smokes found it ranging from every run to none. Of each model's `execution` and
`interactive` runs, these ran, served, requested or browsed what they had built: 6 of 6 for
Gemma-4-31B and for both twins, 5 of 6 for Qwen3.6-27B, 4 of 6 for Seed-OSS, 3 of 6 for GLM,
and none for Magistral (0 of 6) or gpt-oss (0 of 4), which ran no command at all.
*v2.5.6-v2.5.7:* the briefing now says that execution tools act on a live development
environment (section 4.1). How Magistral's and gpt-oss's numbers move on the certifying re-smoke is
the first reading of that change, and Magistral's place in the grid waits on it (section 5).
*v2.5.9:* both moved (gpt-oss ran commands in 2 of its 4 runs, Magistral in 3 of its 6) but
gpt-oss's two command-running runs were the two it lost to parse failures (fifth, above), and
Magistral finished 3 of 9 and left the grid (section 5.1). The sentence is withdrawn (section 4.1), so the
certifying re-smoke reads every model under the original briefing, and gpt-oss's 0 of 4 may
well return. It is recorded as it was before v2.5.6. *v2.5.10:* reinstated (section 4.1). The
smoke of all seven grid models under it is the next reading of these numbers.
Checking is not a registered outcome of this study, and no model is dropped for skipping it.
But it is the profile study 08's gate excluded and one of the two reasons given against
Nemotron (section 5.1), and a model that never runs its app is graded on an app its author never
saw work. So the verification actions per run (a server started, an HTTP request, a build
or test command, a browser tool) are reported beside every result, per model x arm.

Tenth, **how often a file is left with content it held before is reported per model x arm**
(v2.5.13). Since v2.5.13 a `write_file` or `edit_file` call that leaves a file with exactly
the bytes an earlier write or edit call of the run left it with gets a note saying how many
such calls there have now been and how many calls ago the previous one was (section 4.4), and the
manifest counts those calls in `file_state_repeats`: `count`, split into `writes` and
`edits`. `reverts`, those that moved the bytes back to an earlier content, and `max_times`,
the most calls that left one file with one content. Replayed through the note, the recorded
calls of the 93 September smoke runs get it 208 times in 38 runs, 24 of which finished:
185 of the 208 left the file as it was (77 rewrites of identical bytes and 108
identical-string edits) and 23 moved it back to an earlier content. The most was 32 calls
leaving one file with one content, in a run that finished. The note is the same text in
every arm and states nothing the transcript does not already imply (every arm keeps all of
its earlier calls in context) but what a model does with it may differ by arm: a model that
can also see what it reasoned about the file before may read "5 calls" differently from one
that cannot. So `file_state_repeats` is reported beside every result, and if it differs
between UNSEEN and SEEN, that difference is part of the visibility effect and is reported as
such. It is not a registered outcome, and it ends nothing: a run that repeats itself long
enough is still ended by the loop guards, whose values are unchanged. *v2.5.14:* in the 20M
set it fired in 25 of 60 runs, 113 times, and 21 of the 25 finished. In `no_verification`,
where the comparison with the 12M set is exact up to the note, 4 of the 5 runs that had
failed there finished after it first fired, and none that had finished failed (section 4.1).

Analysis: two registered contrasts, each on the same three behaviour
measures (failure incidence, steps, quality): **primary** UNSEEN vs SEEN
(visibility), **secondary** OFF vs UNSEEN (generation), the latter only in
three-arm models. Two-sided tests throughout. Within each contrast the three
measures are corrected for multiple comparisons (Holm), and the two
contrasts are reported as separate questions with that structure stated,
not pooled into one family. Equivalence bounds are pre-set for any measure
that comes up null (+/-10pp reliability, 0.8-1.25x steps, +/-10 points of rubric score, dropped in v2.5.46). Stratified permutation tests with a fixed
seed, strata = task x condition (six strata). Cost reported as an estimate
with intervals, not a test. One **exploratory** contrast is pre-specified and
fenced: the visibility effect inside the `no_verification` block versus
inside the two feedback blocks, reported with intervals, never as a
hypothesis test. A second, the within-pair comparison, is registered on the same terms in
the seventh item above (v2.5.5). All analysis code is written against fake data and frozen
at the registration freeze (section 9 item 6). Grid runs may already have been made by then, but no
grid app is graded or un-blinded before it. Every
deviation afterwards is logged with date and reason and reported in the paper.
