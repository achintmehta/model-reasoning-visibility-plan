# Message Board — rubric v2.2 (2026-10-18)

**Scores:** `pass` or `fail` (`skip` only for grader-side problems). 15 items, total weight 27.
Read `README.md` first: it covers setup, the declared launch, the four launch items,
accommodations, dependencies, and `backend.sh` for pausing, resuming and killing the backend.

**Texts to type:** `alpha 1`, `bravo 2`, `charlie 3`. Before typing each one, clear the input if it
still holds anything: an input left full after a post fails F2 there, and must not turn the
next post into `alpha 1bravo 2`.

**Windows:** A, B and C are three separate browser windows, each showing the app's address:
the page URL the app gives you: the Local address its dev server prints (for example
`http://localhost:5173/`), or the backend's own address when the backend serves the page.
Every window uses the same address. Open each window's DevTools before entering the address.

## Script

| step | do this | then score |
|---|---|---|
| 0 | Run `grade_setup.sh` (README, "Before each app") and read its install output. | L0 |
| 1 | Run the declared command. Open window A: a new browser window, open its DevTools, then go to the app's address. In A's Network panel, find the request for the message history. | L1, L2, L3. If the page doesn't work, use the accommodations in the README. |
| 2 | Wait 10 seconds. In A's Network panel, find the event-stream request (Type `event-stream`; README, "Browser"). | R1 |
| 3 | In A, type `alpha 1` and submit (Enter or the send button). | F1, F2, F3 |
| 4 | Open window B: a new browser window, open its DevTools, then go to the app's address, the same one as A. | F4 |
| 5 | In A, post `bravo 2`. Do not reload or navigate B. | R2, and B's half of R4 |
| 6 | Open window C the same way: a new browser window, open its DevTools, then go to the app's address. In B, post `charlie 3`. Do not reload or navigate A or C. | R3, R4 |
| 7 | Reload A. | D1 |
| 8 | Kill the backend (`backend.sh kill`) and Ctrl-C the rest of the app. Check that its ports are free. Start it again with the same command, wait until it has started (see "Started" in the README), and reload A. | P1 |
| 9 | Look back over the whole card. | U1 |
| 10 | With the score sheet complete and the app still running, run the API probe (README, "API probe"). Do not change any score afterwards. | — (recorded apart from the score) |

## Items

The **spec** column names what each item rests on: the task numbers in `tasks/message-board`.

| id | wt | goal | passes when | fails when (examples) | spec |
|---|---|---|---|---|---|
| MB-L0 | 1 | Check if the app installs without an accommodation | Installing the app's dependencies from its own files completes without an error, in every folder that has a `package.json` (README, "Before each app"). Warnings do not count. | The install stops with an error: a package or version that does not exist, a dependency conflict npm refuses, or a lockfile that does not match its `package.json` (even if A0 then gets it installed). | 1.1, 1.2, 1.4 |
| MB-L1 | 3 | Check if the backend boots with the declared command | The backend starts with the declared command, with no accommodation, and keeps running: it has started (see "Started" in the README) and is still running when the page is opened. | The backend throws an exception or exits while starting, never starts, or starts only with an accommodation (A1, A5, A6, A7 or A8). | 1.1, 1.4, 2.1-2.3 |
| MB-L2 | 3 | Check if the frontend boots and its page loads cleanly | The frontend starts with the declared command, with no accommodation, and its page loads: while it loads, the Console shows no error from the app's own source files, and all of the page's own scripts and styles load. An app with no Vite dev server, whose backend serves the page, is judged on that page. | The frontend's code fails as it loads, some of the page's own files fail to load, or the frontend starts only with an accommodation (A2, A3, A5, A6, A7 or A8). | 1.2, 1.3, 1.4, 4.1 |
| MB-L3 | 2 | Check if the frontend can talk to the backend | On the launch where the backend runs and the page's scripts load (the declared command if they do there, otherwise the first accommodated launch where they do), the page's request for the message history returns 200 with a JSON body (check the Response tab). No A4 or A7 accommodation. | The page cannot reach the backend: its request fails, returns an error, or returns something other than the backend's JSON, such as the page's own HTML. | 1.4, 2.1 |
| MB-R1 | 1 | Check if the page opens a live-update stream | Ten seconds after the page loaded, A's Network panel shows a request to the backend's event stream (Type `event-stream`; README, "Browser") that is still open. | No event stream is opened (for example, the page polls instead), or it has closed with an error. | 3.1, 4.3 |
| MB-F1 | 2 | Check if a posted message shows up at once | `alpha 1` appears in A's own list within 2 seconds, without a manual reload. | The sending window shows the message only after a manual reload, or the post fails. | 3.2, 3.3, 4.4, 4.5 |
| MB-F2 | 1 | Check if the input clears after posting | The input is empty again after submitting. | The text stays in the input. | 4.5 |
| MB-F3 | 1 | Check if a posted message is not shown twice | Two seconds after submitting, `alpha 1` is shown exactly once in A. Depends on F1. | The sending window shows it twice until a reload. | 4.4 |
| MB-F4 | 2 | Check if a newly opened window loads the history | `alpha 1` is listed in B, exactly once, as soon as B has loaded, with no action. | The history is not loaded on page load, is loaded but not shown, or a message is shown twice (for example, once from the history and again from the event stream). | 2.4, 4.2 |
| MB-R2 | 3 | Check if a message reaches another window live | `bravo 2` appears in B within 2 seconds, without a reload. | B shows new messages only after a reload. | 3.3, 4.4 |
| MB-R3 | 2 | Check if a message reaches every other window live | `charlie 3` appears in both A and C within 2 seconds, without a reload. | Only some of the other windows receive it, for example only the last one connected. | 3.3 |
| MB-R4 | 1 | Check if live messages are not duplicated | Two seconds after each post, each receiving window shows the new message exactly once (B for `bravo 2`; A and C for `charlie 3`). Depends on R2 and R3. | A receiving window shows a message twice. | 4.4 |
| MB-D1 | 1 | Check if messages survive a page reload, once each | After reloading A, each of `alpha 1`, `bravo 2` and `charlie 3` is listed exactly once. Depends on F1. | A message was stored twice, for example because the interface submitted it twice. | 3.2 |
| MB-P1 | 3 | Check if messages survive a backend restart | After the restart, `alpha 1`, `bravo 2` and `charlie 3` are all listed: the list is the one shown before the kill. How often each is listed is judged by D1, not here. | Messages are lost when the process is killed (held in memory, or written only on a clean shutdown), or the app does not start a second time. | 2.2 |
| MB-U1 | 1 | Check if messages show as readable text | Every message shows as its own full text in a list (not `[object Object]`, not `undefined`, not raw JSON), and no element overlaps another. | Messages render as objects or blanks, or elements overlap. | 4.1 |

Put anything else you notice in the notes, not in a score.
