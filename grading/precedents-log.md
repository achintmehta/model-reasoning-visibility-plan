# Precedents log

The decisions on how the rubric cards apply to cases they did not foresee. The cards
themselves (`tasks/rubrics/` in the harness repository, tagged
`model-reasoning-visibility-plan-freeze-101926`, the grader freeze) never change
after the grader freeze. This log is how their reading is kept the same for every app.

Rules (rubric README, "Rulings, after the grader freeze", and protocol section 5.3):

- **Every entry is a ruling.** Rulings are made after the grader freeze, while the grid is
  graded. Each is a deviation (protocol section 8.5): its entry is its record, and the report
  lists it. The calls the training round settled are not carried into this log.
- **What an entry may do.** Say how an item's criterion applies. It never adds, removes or
  reweights an item, and never rewords a card.
- **How it is made.** From the changed items of a consistency check, or a case met while
  grading, alone: never with reference to any result by model, condition or arm. Name apps
  only by blind id.
- **Same case, same reading.** Every later grading applies the entry. Apps already graded that
  it would change are re-graded on the affected items, from a fresh copy, and an app in
  the re-grade set in both of its gradings. List them in the entry.
- **An item that cannot be applied at all** is not fixed here: it is reported as a deviation,
  and how it is handled is decided before more of its task is graded (README).
- **Append only.** Never edit or delete an entry. To change one, add a new entry that
  replaces it and says so. Commit the log to git after every entry. Its state at the
  registration freeze is hashed with the grader.

## Entry template

```
### P-000 - <task> <item id>: <short title>

- date: YYYY-MM-DD
- question: what the card leaves open, in one or two sentences
- ruling: how the item's criterion applies, in one or two sentences, written so it can be
  applied without this entry's background
- raised by: <blind ids of the changed pairs or the app where it came up>
- re-graded: <blind ids re-graded on this item because of it, or "none">
- replaces: <entry id, or "none">
```

## Entries

None yet. The first ruling will be P-001.
