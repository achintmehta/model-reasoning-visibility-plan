# Precedents log

The decisions on how the rubric cards apply to cases they did not foresee. The cards
themselves (`tasks/rubrics/` in the harness repository, tagged
`model-reasoning-visibility-plan-freeze-101926`, the grader freeze) never change
after the grader freeze; this log is how their reading is kept the same for every app.

Rules (rubric README, "Rulings, after the grader freeze"; protocol §5.3):

- **Two kinds of entry.**
  - *Calibration* entries are made before the grader freeze, from the training rounds:
    the calls the cards left unclear, and how they were settled. They are the log's first
    entries.
  - *Rulings* are made after the grader freeze. Each is a deviation (protocol §8.5): this
    entry is its record, and the report lists it.
- **What an entry may do.** Say how an item's criterion applies. It never adds, removes or
  reweights an item, and never rewords a card.
- **How it is made.** From the changed items of a consistency check, or a case met while
  grading, alone: never with reference to any result by model, condition or arm. Name apps
  only by blind id.
- **Same case, same reading.** Every later grading applies the entry. Apps already graded that
  it would change are re-graded on the affected items, from a fresh copy; an app in the
  re-grade set, in both of its gradings. List them in the entry.
- **An item that cannot be applied at all** is not fixed here: it is reported as a deviation,
  and how it is handled is decided before more of its task is graded (README).
- **Append only.** Never edit or delete an entry. To change one, add a new entry that
  replaces it and says so. Commit the log to git after every entry. Its state at the
  registration freeze is hashed with the grader.

## Entry template

```
### P-000 — <task> <item id>: <short title>

- date: YYYY-MM-DD
- kind: calibration | ruling
- question: what the card leaves open, in one or two sentences
- ruling: how the item's criterion applies, in one or two sentences, written so it can be
  applied without this entry's background
- raised by: <blind ids of the changed pairs or the app where it came up>
- re-graded: <blind ids re-graded on this item because of it, or "none">
- replaces: <entry id, or "none">
```

## Entries

### P-001 — kanban-board KB-L1 / A6: the declared script names a backend file that does not exist

- date: 2026-10-18
- kind: calibration
- question: The declared `dev:backend` script runs `backend/server.js`, which does not exist; the
  app's backend is `backend/server.mjs`. May the grader run the declared command on that file?
- ruling: Yes, as A6: keep the declared command and change only the file it names to the app's
  own entry file (here `node --watch backend/server.mjs`, run where the script runs). The part
  so started fails L1 (L2 for a frontend), and L3 is judged on that launch. An app whose
  declared script names a missing entry file gets the same correction only when its own files
  show which file is the right one, as here; otherwise there is no A6.
- raised by: 246270
- re-graded: none
- replaces: none

### P-002 — both tasks, L1 / L2 / A8: a package the part's code imports and no package.json declares

- date: 2026-10-18
- kind: calibration
- question: The backend's code imports `express`, `cors` and `@electric-sql/pglite`, but its
  `package.json` declares no dependencies, so the declared command stops with
  `Cannot find module 'express'`. How is the rest of the card reached?
- ruling: A8, after A1–A6: in the folder of the part that needs it, install exactly the package
  the error names with `npm install --no-save <name>@latest`, start again, and repeat for each
  package the next error names. The part fails L1 (L2 for a frontend); L3 is judged on that
  launch. The commands go in the launch item's notes. 616618 was installed with one
  `npm install @electric-sql/pglite cors express` without `--no-save`; that takes the same
  versions, so the grading stands, and its KB-L1 notes say so. Later apps use the A8 form.
- raised by: 616618
- re-graded: none
- replaces: none

### P-003 — both tasks, L1 / A8: a package dropped by a duplicate "dependencies" key

- date: 2026-10-18
- kind: calibration
- question: The root `package.json` lists `express`, `cors` and `@electric-sql/pglite` under
  `"dependencies"`, but a second, empty `"dependencies"` key later in the file replaces that
  list, so npm installs none of them. Does A8 apply, given that A8 is never used for a package
  the app declares?
- ruling: A package counts as declared only if the `package.json` as npm reads it (the last
  value of a duplicated key) declares it. Here none is declared, so the install passes L0 and
  A8 applies as in P-002: one `npm install --no-save <name>@latest` per package an error names.
- raised by: 844429
- re-graded: none
- replaces: none

### P-004 — both tasks, L2 / L3: Console errors from requests to a backend that is not running

- date: 2026-10-18
- kind: calibration
- question: L2 fails on an error from the app's own source files in the Console while the page
  loads. When the backend is down, the page's own requests to it log errors (a failed fetch, a
  Vite proxy error, connection refused). Do those fail L2?
- ruling: No. An error that only reports a failed request to the backend counts against L3 and
  the items that need the backend, not L2. L2 fails on errors from the page's code itself (a
  syntax or reference error, an exception not caused by a failed request, a module that cannot
  load) or on the page's own scripts and styles failing to load.
- raised by: 882029, 458243, 948020, 895919
- re-graded: none
- replaces: none

### P-005 — both tasks, KB-R1 / MB-R1: an event-stream request that is sent but not answered

- date: 2026-10-18
- kind: calibration
- question: Does R1 pass when the page sends its event-stream request but the backend does not
  answer it?
- ruling: No. R1 needs the backend's answer: status 200, Type `event-stream`, still open ten
  seconds later. A request that fails (connection refused, a 4xx or 5xx status, a proxy error),
  or a series of retries that each fail, fails R1. Firefox files EventSource requests under its
  XHR filter and shows the initiator as xhr; the Type column decides, not the filter.
- raised by: 882029
- re-graded: none
- replaces: none

### P-006 — kanban-board KB-R1: an open event stream on a board with no columns

- date: 2026-10-18
- kind: calibration
- question: The board shows no columns (`/api/board` returns `{"columns": []}`), so no card can
  be created and no change is ever sent, but the page's event stream is open. Does R1 pass?
- ruling: Yes. R1 judges only that the stream is open ten seconds after the reload. The items
  that need a card or a change fail under "No pass by default".
- raised by: 784336, 730011
- re-graded: none
- replaces: none

### P-007 — kanban-board KB-R3: a card that lands somewhere other than where it was dropped

- date: 2026-10-18
- kind: calibration
- question: R4 says it is judged on the slot A shows the card in, whether or not that is where
  it was dropped. R3 does not say so. When `apple` lands at the bottom of column 2 instead of
  between `elder` and `fig`, what does R3 judge?
- ruling: The same as R4: whether B shows `apple` in the column and position A shows it, once,
  within 2 seconds and without a reload. Whether that is where it was dropped is judged by D2
  and D1 only.
- raised by: 200419, 616618
- re-graded: none
- replaces: none

