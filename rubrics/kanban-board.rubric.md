# Kanban Board — rubric v2.2 (2026-10-18)

**Scores:** `pass` or `fail` (`skip` only for grader-side problems). 26 items, total weight 50.
Read `README.md` first: it covers setup, the declared launch, the four launch items,
accommodations, dependencies, and `backend.sh` for pausing, resuming and killing the backend.

**Cards:** step 4 creates six cards through A's interface: `apple`, `banana`, `cherry` and
`date` in column 1, then `elder` and `fig` in column 2. The later steps refer to them by name. Before typing each text, clear the input if it still holds anything, so that a leftover text does not run into the next card.

**Windows:** A and B are two separate browser windows, each showing the app's address:
the page URL the app gives you: the Local address its dev server prints (for example
`http://localhost:5173/`), or the backend's own address when the backend serves the page.
Every window uses the same address. Open each window's DevTools before entering the address.

**Reloads:** steps 6 to 14 each begin by reloading both windows, so that every step starts from the board the server stored. A window that missed an update, or shows a move the server did not store, does not carry it into later steps, and each item judges only its own step. Score a step's items before you start the next step, and note anything D6 or D7 will need, such as a blank card text or a ghost left after a drop: the next step's opening reload clears it. A reload later in a step is part of what that step checks, and when an item speaks of "the reload" or "reloading", it means that later one, never the step's opening reload. Do not reload anywhere else.

**Order:** the spec orders the board by `position`: `GET /api/board` returns the columns and
each column's cards ordered by it (tasks 2.3, 2.4), a new card goes at the end of its column
(3.1, 4.6), and a moved card takes a position between the neighbours it was dropped between
(3.2). On screen that means:
- **Columns** run left to right. "Column 1", "column 2" and "column 3" are the first three.
- **Cards** in a column run top to bottom. The "top" or "first" card is the topmost; the
  "end" or "bottom" of a column is below its last card.
- If an app lays a column out some other way, read its order the way the app presents it
  and say so in the notes.

**Dependencies:**
- **Drag items.** Every drag item (D1–D9, R3, R4, C1, C2, S1) fails if no card can be dragged
  at all, or if no drop ever moves a card (the card can be picked up but always goes back where
  it was). There is then no moved card to judge, and nothing passes by default.
- **F4** depends on F3.
- **Seeding fallback.** If the interface cannot create a card, or cannot create one in the
  column needed, create the missing cards with
  `python3 seed_card.py <backend-port> <column-number> <text>...` and grade the rest on them.
  If `seed_card.py` cannot create a card either, every item that needs that card fails. A
  placement warning from `seed_card.py` is noted, not failed.
- **A card stored twice.** If a card was stored twice (F5 fails), read every later "exactly
  once" as "no more often than at the start of the step", and drag the first copy.

## Script

| step | do this | then score |
|---|---|---|
| 0 | Run `grade_setup.sh` (README, "Before each app") and read its install output. | L0 |
| 1 | Run the declared command. Open window A: a new browser window, open its DevTools, then go to the app's address. In A's Network panel, find the request for the board. | L1, L2, L3. If the page doesn't work, use the accommodations in the README. |
| 2 | Look at the board in A and reload it once. Ten seconds after the reload, find the event-stream request (Type `event-stream`; README, "Browser"). | F1, R1 |
| 3 | Open window B: a new browser window, open its DevTools, then go to the app's address, the same one as A. Do not reload or navigate B except where a step tells you to, or where the README's crash and stuck-interface rules require it. | — |
| 4 | Using A's interface, create six cards, one at a time and in this order: `apple`, `banana`, `cherry` and `date` in column 1, then `elder` and `fig` in column 2. Watch B as you go, and A's Network panel for each card's `POST /api/cards`. Column 1 should now read `apple`, `banana`, `cherry`, `date` from the top, and column 2 `elder`, `fig`. | F2, F3, F4, R2 |
| 5 | Reload A. | F5 |
| 6 | Reload A and B. Then, in A, drag `apple` with the mouse into column 2 and drop it between `elder` and `fig`. Watch B. Then reload A. | D2, R3 (before the reload), D1 (after it) |
| 7 | Reload A and B. Then, in A, drag the last card of column 1 (`date`) to the top of column 1. Watch B. Then reload A. | D3, R4 |
| 8 | Reload A and B. Then, in A, drag `fig` into column 3, which is empty at this point. Release it inside the column's outline, below its title and as low as the outline allows. | D4 |
| 9 | Reload A and B. Then pause the backend (`backend.sh pause`). In A, drag the last card of column 1 into the slot between the first two cards. After 1 second, check where it is. Resume it (`backend.sh resume`) and watch A for 5 seconds. Then reload A: the reloaded board is the one the server stored. | D5 |
| 10 | Reload A and B. Then, in A, pick up the second card of column 1, move it over column 2, then carry it outside every column (for example over the page heading) and release it there. Note the board as A shows it. Then reload A. | D9 |
| 11 | Reload A and B. Then pause the backend (`backend.sh pause`). In B, drag the last card of column 1 to the top of column 1. In A, drag the first card of column 1 to the bottom of column 1. Resume it (`backend.sh resume`), wait 5 seconds and compare A with B. Then reload both windows and compare again. | C1 |
| 12 | Reload A and B. Then pause the backend (`backend.sh pause`). In B, drag `elder` into column 3. In A, drag `elder` to the top of column 1. Resume it (`backend.sh resume`), wait 5 seconds and compare. Then reload both windows and compare again. | C2 |
| 13 | Reload A and B. Then, in A, drag the last card of column 1 into the slot between the first two cards, then drag the same card back to the bottom. Do this four times, then drag it into the slot between the first two cards once more (nine drags, all in A, with the backend running; the last one leaves it second). Then reload A and B. If column 1 has fewer than three cards at the start, S1 fails. | S1 |
| 14 | Reload A and B. Then write down the whole board as A shows it. Kill the backend (`backend.sh kill`) and Ctrl-C the rest of the app. Check that its ports are free. Start it again with the same command, wait until it has started (see "Started" in the README), and reload A and B. | P1 |
| 15 | Look back over every drop in steps 6–13, and over the whole card. | D6, D7, U1 |
| 16 | With the score sheet complete and the app still running, run the API probe (README, "API probe"). Do not change any score afterwards. | — (recorded apart from the score) |

## Items

The **spec** column names what each item rests on: the task numbers in `tasks/kanban-board`, `AC n` for the n-th of its "Acceptance Criteria (graded)", and `Decision n` for its design decisions.

| id | wt | goal | passes when | fails when (examples) | spec |
|---|---|---|---|---|---|
| KB-L0 | 1 | Check if the app installs without an accommodation | Installing the app's dependencies from its own files completes without an error, in every folder that has a `package.json` (README, "Before each app"). Warnings do not count. | The install stops with an error: a package or version that does not exist, a dependency conflict npm refuses, or a lockfile that does not match its `package.json` (even if A0 then gets it installed). | 1.1, 1.2, 1.4 |
| KB-L1 | 3 | Check if the backend boots with the declared command | The backend starts with the declared command, with no accommodation, and keeps running: it has started (see "Started" in the README) and is still running when the page is opened. | The backend throws an exception or exits while starting, never starts, or starts only with an accommodation (A1, A5, A6, A7 or A8). | 1.1, 1.4, 2.1-2.3 |
| KB-L2 | 3 | Check if the frontend boots and its page loads cleanly | The frontend starts with the declared command, with no accommodation, and its page loads: while it loads, the Console shows no error from the app's own source files, and all of the page's own scripts and styles load. An app with no Vite dev server, whose backend serves the page, is judged on that page. | The frontend's code fails as it loads, some of the page's own files fail to load, or the frontend starts only with an accommodation (A2, A3, A5, A6, A7 or A8). | 1.2, 1.3, 1.4, 4.1 |
| KB-L3 | 2 | Check if the frontend can talk to the backend | On the launch where the backend runs and the page's scripts load (the declared command if they do there, otherwise the first accommodated launch where they do), the page's request for the board returns 200 with a JSON body (check the Response tab). No A4 or A7 accommodation. | The page cannot reach the backend: its request fails, returns an error, or returns something other than the backend's JSON, such as the page's own HTML. | 1.4, 2.1 |
| KB-F1 | 2 | Check if the board shows its columns | At least three columns are shown side by side, each with its title, in the same order after the reload. | Fewer than three columns, no titles, or the column order changes on reload. | 2.3, 2.4, 4.1 |
| KB-R1 | 1 | Check if the page opens a live-update stream | Ten seconds after the reload, A's Network panel shows a request to the backend's event stream (Type `event-stream`; README, "Browser") that is still open. | No event stream is opened, or it has closed with an error. | 3.3, 4.4 |
| KB-F2 | 1 | Check if the page can create a card | The interface offers a control for creating a card in a chosen column, and submitting it sends `POST /api/cards` with that column's id and the card's text to the backend (check A's Network panel). | The interface cannot add a card: there is no control for creating one, or submitting sends no request, or a request other than `POST /api/cards` with the column's id and the text. Fails whenever any card of step 4 had to be created with `seed_card.py`. | 4.6; Goals; AC 1 |
| KB-F3 | 2 | Check if a new card shows up at once, in its column | Each card submitted from the interface appears in A within 2 seconds, without a reload, at the end of the column it was created in. Depends on F2. Only cards added through the interface count: cards created with `seed_card.py` never pass F3 (they are judged in R2 and F5). | Any card of step 4 had to be created with `seed_card.py` (the interface could not add it); or a submitted card does not appear, for example because the backend rejects the request; or it appears in another column or somewhere other than the end of its column. | 3.1, 4.6 |
| KB-F4 | 1 | Check if a new card is not shown twice | Two seconds after each creation, the new card is shown exactly once in A. Depends on F3. | The creating window shows a new card twice. Fails whenever any card of step 4 had to be created with `seed_card.py` (as F3 then fails). | AC 6 |
| KB-F5 | 2 | Check if new cards survive a page reload | After reloading A, each of the six cards is there exactly once, in the column and order it was created in. | A card was stored twice, so the copy survives the reload, or a card was lost. | AC 5 |
| KB-R2 | 3 | Check if new cards reach the other window live | Each new card, created via the interface or `seed_card.py`, appears in B within 2 seconds, without a reload, and two seconds after each creation it is shown exactly once in B. For a seeded card, it must appear in both A and B within 2 seconds, exactly once in each. | B shows new cards only after a reload, or shows a new card twice. | AC 1 |
| KB-D2 | 2 | Check if a card dragged to another column lands where dropped | `apple` lands between `elder` and `fig`, where it was dropped. | Dropped cards always go to the bottom of the column, or land somewhere else. | 3.2, 4.2, 4.3; Decision 3 |
| KB-R3 | 3 | Check if a move to another column reaches the other window live | Within 2 seconds, without a reload, B shows `apple` in the same column and position as A shows it, and in exactly one place. | B does not update, or shows the card in both columns or in a different place from A. | AC 2; 3.3, 3.4, 4.4 |
| KB-D1 | 3 | Check if a move to another column is saved | After the reload of A that follows the drag in step 6 (not the step's opening reload), `apple` is in column 2, between `elder` and `fig` where it was dropped, and nowhere in column 1. | Drag and drop does not work at all, cards cannot be dropped into another column, a cross-column move fails with a server error, or the reload shows the card somewhere in column 2 other than where it was dropped (for example at the bottom). | 4.2 |
| KB-D3 | 3 | Check if reordering inside a column works and is saved | The dragged card is first in column 1, and the other cards keep their relative order, both before and after reloading A. | Cards cannot be reordered within a column, or the order does not survive the reload. | 4.2 |
| KB-R4 | 2 | Check if a reorder reaches the other window live | Within 2 seconds, without a reload, B shows column 1 in the same order as A, with the dragged card in the slot A shows it in (whether or not that is where it was dropped: D3 judges that) and every card of the column shown exactly once in both windows. Fails if A's order did not change: a card that vanishes from the column has not been reordered. | A reorder within a column does not reach the other window; or the dragged card disappears, even if it disappears from both windows alike. | AC 3; 3.3 |
| KB-D4 | 1 | Check if a card can be dropped into an empty column | `fig` lands in column 3. | The drop works only on an exact spot, such as the middle of the column or onto a card. | 4.2 |
| KB-D5 | 2 | Check if a drag shows at once and then settles on what the server saved | One second after the drop, while the backend is still paused, the card is in its new slot: it moved without waiting for the server (spec 4.3). Within 5 seconds of resuming, A shows the card where the reload then shows it: the slot the server stored, whichever that is (spec 4.5). It never shows in two places at once (spec 4.4). | The card waits for the server before it moves; after resuming it stays somewhere other than where the reload shows it; or it shows in two places. | 4.3, 4.4, 4.5 |
| KB-D9 | 1 | Check if a drop outside every column leaves the board as the server has it | The board A showed just before the reload is the board it shows after it: A's own view matched what the server stored. | A shows the card moved, but the server never stored the move, so a reload or another window shows it elsewhere. | 4.3, 4.5; AC 5 |
| KB-C1 | 2 | Check if two windows reordering at once end up agreeing | After resuming and waiting, A and B show column 1 in the same order, each card as often as at the start of the step, and that order is unchanged after reloading both. Fails if neither drag took effect: judged after resuming, not during the pause (a window showing its own drag while paused does not count), so it fails when, after resuming and after reloading, column 1 is back in the order it had at the start of the step. | The windows settle on different orders, the order changes on reload, or a card is duplicated or lost. | AC 3 |
| KB-C2 | 2 | Check if two windows moving the same card at once end up agreeing | `elder` appears exactly once in each window, in the same column and position in both, before and after reloading both, and no other card is missing or duplicated. Fails if neither drag took effect: judged after resuming, not during the pause (a window showing its own drag while paused does not count), so it fails when, after resuming and after reloading, `elder` is back where it started, in column 2. | The card ends up in two places, in different places in the two windows, or is lost. | AC 4 |
| KB-S1 | 2 | Check if many quick drags in a row stay accurate and are saved | Every drag lands the card where it was dropped: each "between" drag visibly puts it second in column 1, between the cards that were first and second, and each drag back puts it last. After the reloads, A and B both show column 1 as A showed it after the ninth drag: the same cards, each as often as at the start of the step, with the dragged card second and the others in their order from the start of the step. The ninth drag leaves the card where only a move the server stored can keep it, so S1 fails if the reload puts it back at the bottom. | A drag lands the card somewhere other than where it was dropped (for example third instead of second), a card is lost or duplicated, the reload shows the dragged card anywhere but second (for example back at the bottom, because the server never stored the moves or an earlier move won), the order differs between A and B, or repeated moves between the same two neighbours scramble it. | 3.5; AC 6 |
| KB-P1 | 3 | Check if the board survives a backend restart | After the restart, A and B both show exactly the board you wrote down: the same columns, and the same cards in the same order. Fails if there were no cards to write down (nothing passes by default). | Cards or their order are lost when the process is killed, or the app does not start a second time. | AC 5; 2.2 |
| KB-D6 | 1 | Check if dragged cards keep their text | After every drop in steps 6–13, the moved card shows its own text. | A dragged card's text shows as `undefined` or blank until a reload. Fails if no drop in steps 6–13 ever moves a card on the page (it can be picked up but always goes back where it was): there is no moved card to judge (Dependencies). A drop that moves the card on the page counts even if a reload later puts it back. | 4.4 |
| KB-D7 | 1 | Check if drags leave no ghost copies behind | After every drop in steps 6–13, no copy, placeholder or "ghost" of the card is left on the page. | A ghost card is left floating after a drop. Fails if no drop in steps 6–13 ever moves a card on the page (it can be picked up but always goes back where it was): there is no moved card to judge (Dependencies). A drop that moves the card on the page counts even if a reload later puts it back. | 4.2, 4.4 |
| KB-U1 | 1 | Check if the board's layout is readable | Columns sit side by side, every card's full text is visible, and no card overlaps another card or a column edge. | Overlapping or clipped cards or columns, or two cards in the same slot. | AC 6 |

Put anything else you notice in the notes, not in a score.
