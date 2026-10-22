# Rubric v2 — hand grading for the model reasoning-visibility study (DRAFT for review, 2026-10-01; install item, API probe, one grader with a 14-day re-grade)

These rules apply to both cards in this folder: `message-board.rubric.md` and
`kanban-board.rubric.md`.
The commands, in the order you run them, are in `GRADING-COMMANDS.md`: the same for a
practice round, the calibration rounds and the grid.

In this study the rubric score is the app-quality measure, given by one grader. Beside it, the API
probe (below) records whether each app's backend follows the API the spec names. Its results
are kept apart from the score and analysed as their own outcome.

## One grader, and the re-grade

- **One grader grades every app.** The score of record is an app's first grading.
- **The re-grade.** Before each tier, a seeded draw picks four apps of every model × task ×
  condition × arm cell, a fifth of all apps. Each gets a second blind id, and you grade it a
  second time at least 14 days after its first grading. The two gradings measure how
  consistently the cards are applied; the re-grade never changes the score of record.
- **Your list.** You receive shuffled lists of blind ids. A re-grade's second id joins a list
  only once its 14 days have passed, mixed in among first gradings of later apps. Nothing on a
  list says which ids are re-grades, so grade every app the same way.
- **Blind.** You see only the blind id: `grade_setup.sh` takes the id, finds the run itself,
  and prints and records nothing but the id. Never open `manifest.json`, the trace or the
  run's logs.
- **No looking back.** Never look up an earlier score sheet while grading. If an app seems
  familiar, grade it from the card as if it were new.
- **Order.** Work through each list in its shuffled order, so that any drift over the weeks
  cannot follow the arms.
- **A fresh copy.** Start every grading, a re-grade included, from a fresh copy
  (`grade_setup.sh`). The card's script posts messages and creates kanban cards, so a copy
  already graded is not fresh.
- **Your score sheet.** Once a score sheet is in, it changes only through a ruling in the
  precedents log.
- **Your results folder** is `grading/` in the study's research folder (beside `smoke-runs/`),
  outside this tagged folder and outside the runs. It holds your score sheets, the API probe's
  files (`--out`) and the precedents log (`precedents-log.md`). It names apps only by blind
  id; the un-blinding key never goes there. Commit it to git after every session.
- **Consistency** is measured on the re-graded apps only, in the consistency checks
  ("Calibration, consistency checks and the precedents log", below):
  - for the score: the mean absolute difference between an app's two gradings, and the
    intraclass correlation (ICC) across the re-graded apps;
  - for each item: Cohen's kappa beside the raw share of apps whose item came out the same
    both times.
- **The bar** (a draft, under review). For each task, an app's two gradings differ by no more
  than 5 points on average, in a check of at least 24 re-graded apps of the task.

## Before each app (grader-side, except the install, which is L0)

1. **Copy, clean and install.** Run `grade_setup.sh <blind id>` (in this folder). Tell it once
   per session where the runs are: `GRADING_ROOTS` (folders in the blind layout,
   `<root>/<task>/runs/<id>/`) and, for re-grade ids and calibration copies, `GRADING_INDEX` (a
   list of `<id><TAB><run folder>` lines, made by whoever makes your lists). It prints the blind id
   and the task, never the run's folder, and does five things, in order:
   - finds the run;
   - checks that your Node is the run's, and stops with the `nvm` command if not;
   - copies the app to `~/grading-work/<blind id>/app` (`GRADING_WORK` to change it; never
     grade on `/mnt/d`: PGLite and npm both misbehave there);
   - removes the database directory the app shipped with (every PGlite data folder, the one
     its code passes to `new PGlite(...)`), and any parent left empty, and logs each removal
     beside the lines of code that call PGlite;
   - installs the dependencies in every folder of the app that has a `package.json` (spec task
     1.4 speaks of "its package.json files"; a workspace member is installed by its workspace
     root): with `npm ci` from that folder's lockfile if the run has one, otherwise from the
     lockfile the app's first grading saved beside the run (`grading-lock*.json`), otherwise
     with `npm install`, whose lockfile is then saved there. For that last case your npm
     `before` date must be the run's, and it stops if not.

   Check its log of what it removed, and read the install output and its summary: they decide
   **L0**. Four install failures have an accommodation (A0), so the rest of the card can be
   graded; L0 still fails, and the summary gives the command to run in that folder:
   - a dependency conflict npm refuses (`ERESOLVE`): re-run with
     `npm install --legacy-peer-deps`;
   - a lockfile that does not match its `package.json` (`npm ci` stops with `EUSAGE`, "can only
     install packages when your package.json and package-lock.json are in sync"): re-run with
     `npm install`, which installs what the `package.json` declares;
   - a dependency the app's own `package.json` declares, asked for in a range that no version published
     before the study's `before` date matches (`ETARGET`, "No matching version found for <name>@<range>"): re-run with
     `npm install --no-save <name>@latest`, which installs everything the `package.json`
     declares but takes that one package at the newest version published before the study's
     `before` date. `--no-save` leaves `package.json` and any lockfile untouched; nothing is
     written but `node_modules`. If it then stops on `ETARGET` for another declared package,
     add that one to the same command (`npm install --no-save <a>@latest <b>@latest`). For a
     package a workspace member declares, the summary adds `-w <member>`. A package that does
     not exist at all (`E404`), or a missing version of a package no `package.json` of the
     app declares, has no A0. If the app then fails because its code does not match the
     version installed, that is graded like any other failure. Write `A0 ETARGET:` and the
     exact command in L0's notes: the analysis finds these apps by it (protocol §8.3).
   - a lifecycle script of the folder's own `package.json` (`preinstall`, `install`,
     `postinstall` or `prepare`) that fails, such as an `install` script that runs
     `cd backend && npm install && cd frontend && npm install` from the wrong folder: re-run the
     same install with `--ignore-scripts`, which installs the folder's dependencies and skips
     its lifecycle scripts (npm already blocks the dependencies' own install scripts). The
     other folders are installed by `grade_setup.sh` as usual, so nothing the script was meant
     to install is missing. A script in a dependency, rather than the app's own, has no A0.

   Any other install
   error fails L0, and every item after it fails too. A registry that cannot be reached is a
   grader-side problem: retry, or `skip`. Its exit status is 3 when an install failed. The
   copy's folder also holds `GRADER-ENV.txt` (your Node, npm, `before` date, lockfile hashes, OS
   and browser; set `GRADER_BROWSER` if it cannot find the browser) and `grade-setup.log`. The
   copy is scratch, so with `GRADING_RESULTS` set both are also kept with your results, in
   `setup/<blind id>/<date-time>/`, one folder per run of `grade_setup.sh` (a run that stops
   early included). Each A0 command in the summary ends in `| tee -a .../a0.log`, so its output
   is kept there too: run it as printed. They are committed with the score sheets; the sheet
   says what you decided, and these logs are the evidence behind L0. With
   `GRADING_RESULTS` set to your results folder, it also puts a blank score sheet there,
   `<blind id>.score.json` ("Score sheets", below). With `grading-shell.sh` sourced once per
   session (`source grading-shell.sh`, "GRADING-COMMANDS.md", part B), `grade_setup.sh` also moves
   your shell into the copy's project root once it is ready, so `npm run dev` cannot start an
   earlier app by mistake; if it stops before the copy is ready, your shell stays where it was.
   After the install it also checks the declared launch without running it (`launch_check.js`):
   it follows `npm run dev` through every command it starts and warns about what would stop
   it, such as a command that is not installed (`sh: concurrently: not found`), a `node` file
   or a script that does not exist, or `vite` started in a folder with no page (a 404 at `/`).
   **It decides nothing.** Run the declared command all the same and score L1 and L2 on what it
   does; the warnings only tell you which accommodation you are likely to need. After an A0,
   run it again with the command the summary prints.
2. **Free the ports.** Make sure nothing is listening on the app's ports (`ss -ltnp`).
3. **Browser.**
   - **The same browsers for every grading, re-grades included:** window A is **Firefox**;
     windows B and C (C only on the message board) are **Microsoft Edge** windows. A and B in
     different browsers share no cache and no connections. Set `GRADER_BROWSER` to both
     versions, for example `"A: Firefox 143.0; B, C: Edge 141.0"`, so that `GRADER-ENV.txt`
     records them.
   - Each window's page area must be at least 1,000 px wide. Windows may overlap.
   - Undock DevTools into its own window. In Firefox, tick **Disable Cache** in the Network
     panel and turn on **Persist Logs** (the Network panel's gear menu); in Edge, tick
     **Disable cache** and **Preserve log**.
   - **Window A's Network panel** is where the cards' DevTools checks are read. A request's
     status is in the Status column and its body in the Response tab. The event stream is the
     request whose **Type** column shows `event-stream` (a `text/event-stream` response);
     Firefox lists it under XHR and shows `(xhr)` beside its initiator even when the page opened
     it with `EventSource`, so neither tells you how it was opened. It is still open when its
     row has no end (it keeps no final time), and it is one request, not a new one every few
     seconds, which would be polling.
   - Open DevTools **before** you enter the app's address, so that the first requests are
     recorded.
4. **Pausing, resuming and killing the backend: `backend.sh`** (in this folder; use its full
   path, or add this folder to your PATH). Run it from the app's folder, or give the folder
   with `-d`.
   - `backend.sh status` shows the app's listening processes and which one it takes for the
     backend. Run it once after the app has started.
   - `backend.sh pause` pauses the backend (`kill -STOP`): requests wait and the event stream
     goes quiet. `backend.sh resume` resumes it (`kill -CONT`).
   - `backend.sh kill` kills it (`kill -9`) for the restart step, and lists what of the app is
     still listening, to Ctrl-C.
   - **How it finds the backend:** the process listening on a TCP port whose folder (or a path
     in its command line) is inside the app, and which is not the frontend's dev server (its
     command line does not name vite or another dev server, and its port does not serve
     Vite's page). It acts on that listening process itself, not on `npm` or `concurrently`
     above it, which would leave the server running.
   - If it finds no candidate or more than one, it lists what it saw and stops: run it again
     with the backend's port, `-p <port>` (for example a backend that runs Vite inside itself
     looks like a dev server).

**Grader-side problems.** A problem with your machine rather than the app is fixed and graded
through. One example is a dev server that the browser can reach only with `--host`, because
the server and the browser disagree on the interface. If a grader-side problem cannot be fixed,
mark the affected items `skip` and say why. `skip` is never used for anything the app does.

- **`EALLOWSCRIPTS` from `npm run dev`** ("--allow-scripts is not allowed in project-scoped
  installs") is a grader-side problem. It appears when your npm configuration sets
  `allow-scripts` and the app's `dev` script runs `npm install` itself: npm hands its settings
  to the inner npm as environment variables, and npm 12 refuses `allow-scripts` from there. Find
  the setting, remove it, and run the declared command again (the failed attempt installed
  nothing, so the copy is still fresh). Say in L1's notes that the first launch failed on your
  npm setting. Check it is gone before every session ("GRADING-COMMANDS.md", part B):

  ```bash
  npm config get allow-scripts                     # note the value; it should print nothing
  grep -n allow ~/.npmrc "$(npm config get globalconfig)" 2>/dev/null   # where it is set
  env | grep -i npm_config_allow                   # should print nothing
  npm config delete allow-scripts --location=user  # or delete the line from the file grep found
  ```

## Launch

**The declared command.** This is `npm run dev` at the project root. Spec task 1.4 requires it
to start the backend and the frontend together, from a fresh checkout, with no manual step.

- **No root `dev` script.** L1 and L2 fail. To grade the rest, use the command the app's
  README gives (A7); if there is none, start each part with its own declared script (A5).

**Started.** A part of the app (backend or frontend) has started when its process is running
and its port is open (`ss -ltnp`). After running the command, wait up to 60 s for both parts to
start, and load the page only once they have, so a start-up race is not graded as a defect. A
part that throws an exception or exits while starting, or has not started after 60 s, has not
started.

**The four launch items.** Each catches a different failure:

| item | asks | judged on |
|---|---|---|
| L0 | Do the app's dependencies install? | `grade_setup.sh`'s install, in every folder with a `package.json`, before any accommodation. |
| L1 | Does the backend start with the declared command? | The declared command, with no accommodation: A1, A5, A6, A7 or A8 fail it. The backend must have started and still be running when the page is opened. |
| L2 | Does the frontend start with the declared command, and does its page load? | The declared command, with no accommodation: A2, A3, A5, A6, A7 or A8 fail it. While the page loads, no error from the app's own source files in the Console, and all of the page's own scripts and styles load. An app with no Vite dev server, whose backend serves the page, is judged on that page. |
| L3 | Once both run, does the page reach the backend? | The launch where the backend runs and the page's scripts load: the declared command if they do there, otherwise the first accommodated launch where they do. Never after an A4 or an A7. |

A failure at launch therefore costs the launch item it belongs to and no other: a dependency
that will not install fails L0 (a dependency the code uses but never declares installs fine and
fails L1 or L2 instead, with A8 letting the rest be graded); a backend that does not start with
the declared command fails L1; a frontend that does not start with it, or whose page cannot
load its own code or files, fails L2; and a page that cannot reach a running backend fails only
L3. The accommodations let the rest of the card be graded; they never earn L1 or L2 back.

## Accommodations (so the rest of the card can still be graded)

When the declared launch does not give a working page (one that renders and reaches the
backend), stop it (Ctrl-C; check the ports are free) and try these in order. Stop after 5
minutes in total. **Do not edit any file.**

| code | accommodation |
|---|---|
| A0 | (At install, not launch.) Re-run an install that stopped on a refused dependency conflict (`ERESOLVE`) with `npm install --legacy-peer-deps`; one whose lockfile does not match its `package.json` (`EUSAGE`) with `npm install`; or one that stopped because no version of a declared dependency published before the `before` date matches its range (`ETARGET`) with `npm install --no-save <name>@latest`; or one whose own `preinstall`, `install`, `postinstall` or `prepare` script failed with the same install and `--ignore-scripts` ("Before each app"). |
| A1 | Create the data directory the backend's code names (one `mkdir`). |
| A2 | Run the backend with its own package script and start the frontend so that its own Vite config loads: `npx vite` with no positional root, `npx vite .` in the folder that holds `vite.config.*`, or `npx vite --config <its config> <root>`. Then open the address the dev server prints, including the root path it shows (for example `/client/`). |
| A3 | Use a production build made from the app's own config: its `build` script, or `npx vite build`. Then its own `start` or `preview` script, `npx vite preview`, or its backend serving the build. |
| A4 | Set an environment variable the app's code reads (`PORT`, `VITE_API_URL`, `VITE_API_BASE`, …) to the value the other side expects. |
| A5 | Start the backend and the frontend with their own package scripts in their respective directories, in two terminals. |
| A6 | Start the frontend or the backend with its declared start command, corrected only in the entry point or config file it names, when the one it names does not exist or is the wrong one and the app's own files contain the right one. The correction is made on the command line; no file is edited. |
| A7 | Any other step that gets a working page and keeps to the rules below, when A1–A6 and A8 do not apply or have not worked: for example, running a script the app's own `package.json` declares that A1–A6 do not name (a backend `build` before its `start`, a database `init` script), or starting a part the way the app's own README says. |
| A8 | Install a package the app does not declare, when a part fails to start because its own code imports it or its own declared script runs it and no `package.json` of the app declares it (`Cannot find module 'X'`, `Cannot find package 'X'`, `sh: X: not found`): `npm install --no-save X@latest` in the folder that needs it, then start again. Repeat for each package named the same way. Tried after A1–A6, before A7. |

- Never add a file or a config value, and never type an address, port or path that neither the
  app nor its dev server gives you. A6 is the one exception, and only for the entry point
  or config file it corrects.
- **A6 corrects a file reference, nothing else.** Keep the rest of the declared command as it
  is and change only which of the app's own entry point or config files it runs (for example
  `node --watch backend/server.js` becomes `node --watch backend/server.mjs`). Never edit a
  file, and never write code or config of your own. Write the command you ran in the notes of
  the launch item it stands in for. The first time a kind of correction is used, record it in
  the precedents log, and correct the same problem the same way in every app. A part started
  by an A6 fails L1 (backend) or L2 (frontend); L3 is judged on the A6 launch like any other
  accommodated launch.
- **A8 installs exactly the package the error names, nothing else.** Only a name given by
  the error itself (`Cannot find module 'X'`, `Cannot find package 'X'`, `sh: X: not found`),
  and only if a package of exactly that name exists on npm: a command whose package has a
  different name (`tsc` from `typescript`, for example) gets no A8. Install it with
  `npm install --no-save X@latest` in the folder of the part that needs it; the `before` date
  in `grade_setup.sh`'s npm config keeps `@latest` to versions published before the runs, and
  `--no-save` leaves `package.json` and the lock file as they are. Never for a package the app
  declares (a declared package that will not install is A0's case), and never a version, a
  global install or a second package the error did not name. Try A1–A6 first (a missing
  `concurrently` in a root `dev` script is A5's case: start each part with its own script).
  Write the commands in the notes of the launch item it stands in for. A part started after
  an A8 fails L1 (backend) or L2 (frontend); L3 is judged on the A8 launch like any other
  accommodated launch. The first time a package is installed this way, record it in the
  precedents log.
- **A7 is the last resort**, inside the same 5 minutes. Besides the rule above, it never edits
  a file, never installs anything (no `npm install <package>`, no global tool; A0's `ETARGET`
  re-run at install and A8 are the only such installs), and never runs a
  tool or script that the app's own files do not declare.
  - **Write down exactly what you did:** the problem, the folder and the commands, in the notes
    of the launch item it stands in for, so that a re-grade can repeat it.
  - **It earns no launch item.** A part started by an A7 fails L1 (backend) or L2 (frontend),
    as any start that is not the declared command does, and L3 is never judged on an A7 launch,
    as with A4. The rest of the card is graded on it as usual.
  - **Same problem, same step.** The first time a kind of A7 is used, record it in the
    precedents log: the problem and the step that got past it. Use that step for every app with
    the same problem, and no other. After the grader freeze, a new kind of A7 is a ruling
    (below).
- Record the code of each accommodation you used in the notes of the launch item it stands in
  for.
- If nothing gives a working page within 5 minutes, carry on as "When only one half of the app
  works" (Scoring) says: with no page at all, every item not yet scored fails; with a page whose
  backend does not answer, grade the rest on the page. The launch items already judged keep
  their scores.

## Scoring

- **Every item is `pass` or `fail`.** `partial` is not used, and the merge for v2 cards should
  reject it. `skip` is only for grader-side problems.
- Work through the card's script in order. Each step starts from the state the previous step
  left behind.
- **Type exactly the texts the card gives.** Before typing one, clear the input if it still
  holds anything, such as the last text when the app does not empty the input after a submit
  (the card scores that once, where it happens; it must not spoil the next text).
- **"Within 2 seconds, without reload"** means you do not reload or navigate that window.
- **No N/A.** When a part of the app does not work, every item that needs that part fails.
  `skip` stays for grader-side problems only. Each item is part of the card's total weight, so
  marking items N/A would shrink the total for a broken app and let it lose less than an app
  that works but makes mistakes.
- **No pass by default.** An item passes only when you saw what it asks for. If what it looks
  at never appeared (no message was posted, no card exists, nothing was dropped), it fails,
  even though nothing wrong was seen: "every message shows its full text" fails when there are
  no messages.
- **When only one half of the app works.** After the launch and the accommodations (at most 5
  minutes), carry on with the launch that got furthest:
  - **No page** (the frontend never serves a page that renders, whether or not the backend
    runs): judge the launch items as their rows say, and fail every other item without running
    its steps. Still run the API probe at the end, which checks the backend on its own.
  - **A page, but no backend** (the page renders, but the backend does not run or the page
    cannot reach it): carry on through the script. Do every step the page lets you do, and
    score each item on what you see. An item that needs only the page can pass (for example
    KB-F2, a control for creating a card); an item that needs the backend's data fails. If no
    backend runs at all, run the API probe with `--no-backend`.
  - **A part that stops later,** during the script, is a crash (below), not this rule.
- **Dependencies.**
  - An item whose setup cannot be done because of the app fails. The card names each
    dependency.
  - Where the card gives a fallback, use it so that later items can still be graded.
- **If the app crashes during a step,** every item scored at that step fails. Restart the app
  with the same command, reload every window, continue with the next step, and note the crash.
- **If the interface gets stuck** (a control stays disabled, or a card can no longer be picked
  up), reload the stuck window and carry on, and say so in the notes (neither card scores this on
  its own: rubric v2.1). The item in progress is graded as normal after the reload.
- **Before failing an item, prove which side the failure is on.** The server answering means
  the environment is fine; what it answers with is the app's responsibility. Check the
  backend's terminal and the Network panel first. Say in the notes which it was: backend error,
  wrong response, interface bug, or no request sent.
- **Score to the criterion text,** and put everything else in the notes. Out of scope: styling,
  accessibility, performance, and features the spec does not ask for.

## Notes

Keep notes short and factual. Say what you saw, with any error message, and which
accommodation you used.

Each card's "fails when" column gives examples of how an item fails. When a failure matches
one, use the same words for it in the notes, so that notes can be counted.

## API probe (last, once the score sheet is complete; not part of the score)

The probe (`api_probe.py`, in this folder) calls the backend's API directly and checks what the
spec states exactly: the paths and methods it names, the move request's body, where a new or
moved card goes, and what the event stream carries.

- **When.** Run it as the card's last step, once your score sheet for the app is complete, with
  the app still running as the script left it. The probe adds its own messages or cards (their
  texts begin `api-probe`), so it never runs before grading ends, and nothing it shows changes a
  score.
- **How.** Find the port the backend process listens on (`ss -ltnp`; not the Vite dev server's
  port), then run

  `python3 api_probe.py <message-board|kanban-board> <backend-port> <blind id> --out <your results folder>/probe`

  It takes 10 to 15 seconds (it holds the event stream open for 10) and writes
  `probe/<blind id>.api-probe.json` in your results folder, committed with the score sheets. You don't need to read the output: the file is the record.
- **If it refuses.**
  - *Nothing answers on port …*: check the port. If no backend runs at all, even with the
    accommodations (an install that failed with no A0 included), run it with `--no-backend`
    and any port, for example `0`. Every check is then recorded as failed, so every app has a
    probe file.
  - *Port … is a Vite dev server*: give the backend's own port. Use `--allow-vite` only for an
    app that has no separate backend and serves its API from the Vite dev server itself.
  - If it stops with a Python error, keep your copy of the app and note the blind id.

**What it checks.** Each check ends `pass` or `fail`, or `inconclusive` when the spec leaves open
a detail the probe needs (it names no body field for a new message or card, so the probe tries
`text`, `message` and `content`, and for cards `columnId` or `column_id`), or `blocked` when it
needs an inconclusive check. A check whose prerequisite failed fails too. What the spec leaves
open (the JSON shapes, the body fields that worked, how a missing neighbour is sent) is recorded
under "observations" and never scored. So is how the server answers a message with empty
text (`empty_message`: the status, whether it was refused, accepted or failed, and whether a blank
message was stored), which the spec does not address; it replaced the message-board card's
item MB-E2 in rubric v2.1.

| check | spec | asks |
|---|---|---|
| MB-API1 | 2.4 | `GET /api/messages` answers with data (JSON) |
| MB-API2 | 3.1 | `GET /api/stream` is an event stream (`text/event-stream`) that stays open for 10 s |
| MB-API3 | 3.2 | `POST /api/messages` stores the message: it then appears in `GET /api/messages` |
| MB-API4 | 3.3 | the new message is broadcast on the event stream within 2 s |
| KB-API1 | 2.4 | `GET /api/board` answers with data (JSON) |
| KB-API2 | 2.4 | the board lists the columns, each with its own cards |
| KB-API3 | 3.3 | `GET /api/stream` is an event stream that stays open for 10 s |
| KB-API4 | 3.1 | `POST /api/cards` stores the card in the column it names |
| KB-API5 | 3.1 | the new card is placed at the end of its column |
| KB-API6 | 3.3 | the create is broadcast with the card and its column id within 2 s |
| KB-API7 | 3.2 | `PATCH /api/cards/:id/move` with `{ columnId, beforeId, afterId }` is accepted (2xx) |
| KB-API8 | 3.2 | the move answers with the moved card |
| KB-API9 | 3.2 | the card lands between `afterId` and `beforeId`, and only there |
| KB-API10 | 3.3 | the move is broadcast with the card and its column id within 2 s |

The probe moves its own cards: two in column 1 and one in column 2, which it moves between the
two. If it cannot create cards, it moves cards already on the board instead.

## Score sheets

One sheet per grading, `<blind id>.score.json` in your results folder. A re-grade has its own
blind id, so its own sheet. `grade_setup.sh` makes the blank sheet; `score_sheet.py new <task>
<blind id>` makes one by hand.

- **Grade from the sheet.** It follows the card's script, so you can work through it top to
  bottom without the card open:
  - `card_notes`: the card's notes from above its script (texts to type, windows, order,
    dependencies);
  - `steps`: one entry per step, in order: `do` (what to do), `then_score` (what it scores),
    and the `items` scored at that step, each with its `goal`, `criterion`, `fails_when` and
    `weight` copied from the card. The `goal` says in a few words what the item checks; it is a
    reminder, never the test: the criterion and `fails_when` decide the result. An item checked over two steps (MB-R4) sits at the later one. A step
    with nothing to score has no items. The card stays the reference: if the copied text and
    the card ever differ, the card wins, and `refresh` (below) brings the sheet back in line.
- **Fill it in** in any text editor, as you go through the steps:
  - `graded_on`: the date you graded the app (YYYY-MM-DD);
  - for every item, `result` (`pass`, `fail` or `skip`) and `notes`. A `skip` needs notes
    saying what the grader-side problem was. Changing the copied text changes nothing;
  - `accommodations`: the codes you used (A0 to A8). Name each in the notes of the launch item
    it stands in for; an A6, an A7 or an A8 also needs its exact commands there;
  - `notes`: anything else you noticed.
- **Check it** before you move on: `python3 score_sheet.py check <sheet>`. It refuses a sheet
  with an item missing, a value other than pass, fail or skip (`partial` is not used), a skip
  without notes, an undated sheet, or a card version other than the one in use.
- **After a card changes** (calibration only), close the sheet in your editor and run
  `python3 score_sheet.py refresh <sheet>`: it rewrites the steps and copied text from the
  current card and keeps every result and note. It also puts a sheet made before the sheets
  had steps into steps.
- **Once it is in, it changes only through a ruling** (above). `score_sheet.py score <sheet>`
  prints its score: the weighted share of the items scored pass or fail that pass, out of 100,
  skipped items left out (protocol §6.1).

## The tools around the grading (not run by the grader)

These read the un-blinding state, so whoever makes your lists runs them, not you (protocol
§5.3). They keep their state in `blind-state/`, beside the harness's id ledger and key.

- **`blind_tools.py`**
  - `calibrate`: copies calibration apps (app and `environment.txt` only) to the blind layout
    under fresh ids, because the smoke folders' ids and paths name the arm;
  - `sample`: the seeded quality sample (protocol §5.3, v2.5.46): every cell's apps in a random
    grading order, of which the first ten are graded, so every model, task, condition and arm
    has the same number. `lists` lists nothing for a tier until its sample is drawn, and only
    sampled apps after that;
  - `extend`: grades more of a tier if there is time, to the next apps in every cell's order
    (`--to 12` is the 11th and 12th of every cell), decided by time, never by results;
  - `draw`: the seeded re-grade draw, from the sampled apps (`--per-cell 2`; `--all` re-grades every app of a
    calibration round),
    giving each drawn app a second id. It writes `grading-index.tsv`, which `grade_setup.sh`
    reads as `GRADING_INDEX`;
  - `fresh`: the fresh set after a check below the bar;
  - `lists`: your next shuffled list, first gradings and the re-grades whose 14 days have
    passed together, with nothing marking which is which.
- **`merge_grades.py`** merges the complete score sheets into `scores.csv` and runs the
  consistency check (`consistency.md`): pairs, mean absolute difference against the bar, ICC,
  each item's kappa beside its raw agreement, and every changed item with both notes. It
  names apps only by blind id, so you can read it. Its `--unblinded` file joins the scores of
  record with model, condition and arm for the analysis, and is never given to you.

## Calibration, consistency checks and the precedents log

- **Calibration, before the grid.** Every calibration app is first copied under a fresh random
  id, because the smoke ids name the arm.
  - **Training rounds, small at first,** use the certifying smoke's 66 apps, each graded once, then if needed this study's earlier
    smoke apps. No training grading enters the analysis. In each round, grade every app, then
    read back over the score sheets item by item and fix any wording that left a call unclear.
  - **No separate deciding round.** When the training rounds leave no call unclear, the
    cards are frozen: this folder is committed and tagged `grader-freeze`, **the grader
    freeze**, and is not edited after it. The ambiguities the rounds settled become the
    first entries in the precedents log, whose state then is hashed with the grader at the
    registration freeze.
  - **The first test of consistency is the grid's**: its re-grade set, checked as below. The
    report says the cards were frozen before their consistency had been measured.
  - Grid runs may be made before the grader freeze, but no grid app is graded before it.
- **Consistency checks (during the grid).** A consistency check asks whether you are still
  applying a card the same way as before. It uses only the **re-graded apps**: the fifth of
  each tier drawn for a second grading ("One grader, and the re-grade", above). The other apps,
  graded once, play no part in it.
  - **What it compares.** For each re-graded app, the score of its first grading against the
    score of its re-grade. From those pairs it reports the mean absolute difference between the
    two scores (this is what the bar is set on), the intraclass correlation (ICC), and for each
    item Cohen's kappa beside the share of apps whose item came out the same both times.
  - **One task at a time.** Message-board and kanban apps are checked separately, because each
    has its own card: a check of a task uses at least 24 re-graded apps of that task.
  - **When.** A task's first check is made as soon as 24 of its re-grades are in; after that,
    one is made when each tier's re-grades are complete.
  - **The result.** A task **meets the bar** when the mean absolute difference is 5 points or
    less ("The bar", above), and grading of that task goes on. Otherwise it is **below the bar**.
  - **After every check,** whichever its result, go through the items that changed between the
    two gradings. One that shows an ambiguity in the cards is settled by a ruling (below). No
    re-grade changes a score of record on its own.
  - **A task whose check is below the bar:** stop grading that task's apps, except for the
    fresh set below; the other task's grading goes on.
    - **A fresh set.** Draw a fresh set of at least 24 of its apps, spread evenly over their
      cells, from those first graded at least 14 days earlier and not yet re-graded. Re-grade
      them before any other app of that task, and check them in the same way. Grading of the
      task resumes once they meet the bar.
    - **If the fresh set is below the bar too, or too few apps are left to draw it,** the
      failure is logged and reported as a deviation. How any remaining grading of that task
      goes on is decided before more of it is graded.
- **Rulings, after the grader freeze.** The cards never change after the grader freeze. A
  question they did not foresee is settled by a **ruling**: a written decision on how an
  existing item's criterion applies, recorded in the precedents log.
  - **Where.** `grading/precedents-log.md` in your results folder, outside this tagged
    folder, so that it can grow after the freeze. Its first entries are the calibration entries from the training rounds (above). Each entry follows the log's template: an id
    (P-001, …), the date, its kind (calibration or ruling), the item, the question the card
    left open, the ruling, the blind ids that raised it, the blind ids re-graded because of
    it, and any entry it replaces. Entries are never edited or deleted: a new entry replaces
    an old one and says so. Commit the log after every entry; its state at the registration
    freeze is hashed with the grader.
  - **What a ruling may do.** It only says how an item's criterion applies. It never adds,
    removes or reweights an item, and never rewords a card.
  - **How it is made.** It is made from the changed items alone, or from the case met while
    grading, without reference to any result by model, condition or arm, and names apps only
    by blind id. It is dated, logged as a deviation and applied to every run: its log entry is
    the deviation's record.
  - **Re-grading.** Re-grade the affected items, from a fresh copy, in every app already
    graded that the ruling would change; for an app in the re-grade set, in both of its
    gradings. List them in the entry.
  - **An item that cannot be applied at all** (it turns out to be wrong, or no app can be
    judged on it) is beyond a ruling, which cannot remove it. Report it as a deviation, and
    decide how it is handled (for example, the analysis with and without it) before more of
    that task is graded. Record the decision in the precedents log.
