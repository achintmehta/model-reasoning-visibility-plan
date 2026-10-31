# model-reasoning-visibility-plan: the protocol and the study plan

This folder holds the two documents that define the study "Does a coding agent's model need to
re-read its own reasoning?". Together they are the study's source of truth. Only the protocol is registered on OSF, and where the two differ, the protocol governs. Both are written to
be understandable without a statistics or ML background.

| file | what it is |
|------|------------|
| `model-reasoning-visibility-study-protocol.md` | **the protocol**: the registrable design, condensed from the study plan. It is the document registered at the registration freeze and the one to read first. |
| `model-reasoning-visibility-study-plan.md` | **the study plan**: the full working record behind the protocol. Every probe, smoke set and decision that led to the protocol's settings, with its version history. |

## The protocol

The protocol says what is asked, how it is tested and what would count as an answer, in the
order a pre-registration expects. Sections 1 to 3 say what is asked and how. Sections 4 to 9
carry the detail a replication needs.

| section | what it covers |
|---------|----------------|
| 1. The question and the hypotheses | the question, why it could matter in either direction, and the hypotheses (H1 to H5) |
| 2. Design | the three arms (OFF, UNSEEN and SEEN) and their two contrasts, the tasks, the conditions, the grid, blinding and seeds, and the smoke runs |
| 3. Models | the roster of models and the requirements a model had to meet to enter the grid |
| 4. The frozen settings | how each model's thinking is switched, the templates actually served and the prompt probe, the server, the agent, decoding and the instructions, all fixed before the grid |
| 5. Procedure | the freeze checklist, how the grid is run tier by tier, and how the apps are graded |
| 6. Measures | the behaviour measures (failure, steps and app quality), cost, the mechanism measures, the descriptives and API conformance |
| 7. Sample size and power | how many runs the grid makes and what they can detect |
| 8. Analysis plan | the confirmatory tests, equivalence, the sensitivity and exploratory analyses, and how deviations are handled |
| 9. Validity rules | what makes a run void and how voids are handled |
| 10. Interpretation | how each pattern of results is read, and what would make the study inconclusive |
| 11. Disclosure and availability | what is released, when, and under which licences |
| Appendix A | the models excluded, and why |
| Appendix B | an optional, exploratory extension to frontier models |

Its Status line at the top says what is done and what is still to do before the grid.

## The study plan

The study plan is the longer document the protocol was condensed from. Read it for the
reasoning or the evidence behind a choice the protocol states.

| section | what it covers |
|---------|----------------|
| 1. The question | the question the study asks |
| 2. What could differ, and why | the expectations, reasoned from first principles before any data |
| 3. The experiment | the design in outline |
| 4. What exactly gets run | the conditions, the run counts and every frozen setting, with the probes and smoke sets that fixed them and the commands in order |
| 5. The models | the models chosen, how each was probed, and the models considered and not chosen |
| 6. How many runs, and what the numbers can prove | the sample size and the power |
| 7. What if the models disagree with each other? | how disagreement between models is read |
| 8. Extension: frontier models | the optional, exploratory extension |
| 9. Checklist, in order | every step before and during the grid |
| 10. Fine print | the validity rules and the analysis, for reproducibility |

**The version history** is in the plan's Status paragraph at the top. Every version, from v2.1
to the current one, has an entry there saying what it changed and why. A change to either
document is recorded there.

## Related folders

The rest of the repository holds what the two documents refer to: the analysis code
(`analysis/`), the grading material (`rubrics/`), the frozen harness (`harness/`), the grid's
schedules (`registration/`), the probe prompts (`probe-prompts/`) and the grader's training
round (`calibration/`). The top-level `README.md` describes each.
