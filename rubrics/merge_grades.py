#!/usr/bin/env python3
"""merge_grades.py — merge the score sheets into the scores of record, and run the
consistency check on the re-graded apps (rubric README, "Consistency checks"; protocol §6.1).

    python3 merge_grades.py --results DIR --state DIR [--out DIR] [--draw NAME ...]
                            [--unblinded FILE]

Reads every <blind id>.score.json in the results folder. A sheet is merged only if it is
complete (score_sheet.py check); the others are listed and left out. Ids are paired through
the state folder's regrade-key.jsonl (second id -> first id).

Writes, into --out (default: <results>/merge):
  scores.csv            every complete grading: blind id, task, first or re-grade, date, score
  consistency.md        the check, per task: pairs, mean absolute difference against the bar,
                        ICC (two-way, absolute agreement, single measurement), each item's
                        Cohen's kappa beside its raw agreement, the difference against the days
                        between the gradings, and every changed item with both notes
  consistency.json      the same numbers, for the record

Everything above names apps by blind id only, so the grader can read it. With --unblinded,
it also writes the scores of record joined with model, task, condition and arm from the
un-blinding key, for the analysis: never give that file to the grader.

--draw limits the check to the re-grades of the named draws (for example one tier's).

Stdlib only.
"""
import argparse
import csv
import datetime
import glob
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_sheet  # noqa: E402

BAR_POINTS = 5.0
MIN_PAIRS = 24


def jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def icc_a1(pairs):
    """ICC(A,1): two-way, absolute agreement, single measurement (McGraw & Wong 1996)."""
    n, k = len(pairs), 2
    if n < 2:
        return None
    gm = sum(a + b for a, b in pairs) / (n * k)
    rows = [(a + b) / 2 for a, b in pairs]
    cols = [sum(p[j] for p in pairs) / n for j in range(k)]
    ssr = k * sum((r - gm) ** 2 for r in rows)
    ssc = n * sum((c - gm) ** 2 for c in cols)
    sst = sum((x - gm) ** 2 for p in pairs for x in p)
    sse = sst - ssr - ssc
    msr, msc, mse = ssr / (n - 1), ssc / (k - 1), sse / ((n - 1) * (k - 1))
    den = msr + (k - 1) * mse + k * (msc - mse) / n
    return None if den == 0 else (msr - mse) / den


def kappa(pairs):
    """Cohen's kappa for pass/fail pairs, and the raw agreement. Kappa is None when it is
    undefined (every grading gave the same result, so chance agreement is 1)."""
    n = len(pairs)
    if not n:
        return None, None
    po = sum(a == b for a, b in pairs) / n
    p1 = sum(a == "pass" for a, _ in pairs) / n
    p2 = sum(b == "pass" for _, b in pairs) / n
    pe = p1 * p2 + (1 - p1) * (1 - p2)
    return (None if pe == 1 else (po - pe) / (1 - pe)), po


def pearson(xs, ys):
    if len(xs) < 3 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    return statistics.correlation(xs, ys)


def fmt(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--results", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--out")
    ap.add_argument("--cards", default=HERE)
    ap.add_argument("--draw", action="append")
    ap.add_argument("--unblinded")
    a = ap.parse_args(argv)
    out = a.out or os.path.join(a.results, "merge")
    os.makedirs(out, exist_ok=True)

    cards = {t: score_sheet.load_card(t, a.cards) for t in score_sheet.TASKS}
    sheets, rejected = {}, []
    for p in sorted(glob.glob(os.path.join(a.results, "*.score.json"))):
        try:
            s = score_sheet.read(p)
        except (OSError, ValueError) as e:
            rejected.append((os.path.basename(p), [f"cannot read: {e}"]))
            continue
        card = cards.get(s.get("task"))
        probs = score_sheet.problems(s, card) if card else [f"unknown task {s.get('task')!r}"]
        if probs:
            rejected.append((os.path.basename(p), probs))
            continue
        sheets[s["blind_id"]] = s

    regrades = {r["blind_id"]: r for r in jsonl(os.path.join(a.state, "regrade-key.jsonl"))}
    rows = []
    for bid, s in sorted(sheets.items()):
        sc, passed, scored = score_sheet.score(s, cards[s["task"]])
        rg = regrades.get(bid)
        rows.append({"blind_id": bid, "task": s["task"], "kind": "re-grade" if rg else "first",
                     "regrade_of": rg["regrade_of"] if rg else "", "graded_on": s["graded_on"],
                     "card_version": s["card_version"], "score": sc,
                     "weight_passed": passed, "weight_scored": scored})
    with open(os.path.join(out, "scores.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["blind_id"])
        w.writeheader()
        w.writerows(rows)
    by_id = {r["blind_id"]: r for r in rows}

    # ---- pairs: (first sheet, re-grade sheet)
    pairs = {}
    unpaired = 0
    for second, rg in regrades.items():
        if a.draw and rg.get("draw") not in a.draw:
            continue
        first = rg["regrade_of"]
        if second in sheets and first in sheets:
            pairs[second] = (first, second)
        elif second in sheets:
            unpaired += 1

    report = {"made_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
              "draws": a.draw or "all", "bar_points": BAR_POINTS, "min_pairs": MIN_PAIRS, "tasks": {}}
    md = [f"# Consistency check ({report['made_at']})", "",
          f"Re-grades of draws: {', '.join(a.draw) if a.draw else 'all'}. Gradings merged: "
          f"{len(sheets)}; incomplete sheets left out: {len(rejected)}.", ""]
    for task in score_sheet.TASKS:
        tp = [(f, s) for f, s in pairs.values() if sheets[f]["task"] == task]
        diffs = [abs(by_id[s]["score"] - by_id[f]["score"]) for f, s in tp
                 if by_id[f]["score"] is not None and by_id[s]["score"] is not None]
        mad = statistics.mean(diffs) if diffs else None
        if len(tp) < MIN_PAIRS:
            verdict = f"too few pairs yet ({len(tp)} of {MIN_PAIRS})"
        else:
            verdict = "meets the bar" if mad is not None and mad <= BAR_POINTS else "BELOW THE BAR"
        icc = icc_a1([(by_id[f]["score"], by_id[s]["score"]) for f, s in tp
                      if by_id[f]["score"] is not None and by_id[s]["score"] is not None])
        days = [(datetime.date.fromisoformat(sheets[s]["graded_on"])
                 - datetime.date.fromisoformat(sheets[f]["graded_on"])).days for f, s in tp]
        r_days = pearson(days, [abs(by_id[s]["score"] - by_id[f]["score"]) for f, s in tp]) if tp else None
        items = []
        for it in cards[task]["items"]:
            iid = it["id"]
            pr = [(score_sheet.items_of(sheets[f])[iid]["result"], score_sheet.items_of(sheets[s])[iid]["result"]) for f, s in tp]
            pr = [p for p in pr if "skip" not in p]
            k, agree = kappa(pr)
            items.append({"item": iid, "pairs": len(pr), "kappa": k, "agreement": agree,
                          "changed": sum(x != y for x, y in pr)})
        changed = []
        for f, s in sorted(tp):
            for it in cards[task]["items"]:
                iid = it["id"]
                x, y = score_sheet.items_of(sheets[f])[iid], score_sheet.items_of(sheets[s])[iid]
                if x["result"] != y["result"]:
                    changed.append({"first": f, "second": s, "item": iid,
                                    "first_result": x["result"], "second_result": y["result"],
                                    "first_notes": x.get("notes", ""), "second_notes": y.get("notes", "")})
        report["tasks"][task] = {"pairs": len(tp), "mean_abs_diff": mad, "verdict": verdict,
                                 "icc_a1": icc, "diff_vs_days_r": r_days, "items": items,
                                 "changed": changed,
                                 "pairs_detail": [{"first": f, "second": s, "first_score": by_id[f]["score"],
                                                   "second_score": by_id[s]["score"], "days": d}
                                                  for (f, s), d in zip(tp, days)]}
        md += [f"## {task}", "",
               f"- pairs: {len(tp)}",
               f"- mean absolute difference: {fmt(mad)} points (bar: {BAR_POINTS:g} or less, on at least {MIN_PAIRS} pairs)",
               f"- **{verdict}**",
               f"- ICC (two-way, absolute agreement, single measurement): {fmt(icc, 3)}",
               f"- difference against days between gradings: r = {fmt(r_days, 2)}"
               + (f" (days {min(days)}–{max(days)})" if days else ""), "",
               "| item | pairs | changed | agreement | kappa |", "|---|---|---|---|---|"]
        for x in items:
            kap = "undefined (no variation)" if x["kappa"] is None and x["pairs"] else fmt(x["kappa"], 2)
            md.append(f"| {x['item']} | {x['pairs']} | {x['changed']} | {fmt(x['agreement'], 2)} | {kap} |")
        md += ["", f"### Changed items ({len(changed)})", ""]
        if changed:
            md += ["| first id | second id | item | first | second | first notes | second notes |",
                   "|---|---|---|---|---|---|---|"]
            for c in changed:
                cl = lambda t: str(t).replace("|", "/").replace("\n", " ")[:160]
                md.append(f"| {c['first']} | {c['second']} | {c['item']} | {c['first_result']} | "
                          f"{c['second_result']} | {cl(c['first_notes'])} | {cl(c['second_notes'])} |")
        md.append("")
    if rejected:
        md += ["## Sheets left out (incomplete)", ""]
        md += [f"- {n}: {'; '.join(p[:3])}{' …' if len(p) > 3 else ''}" for n, p in rejected]
    if unpaired:
        md += ["", f"{unpaired} re-grade sheets wait for their first grading's sheet."]
    with open(os.path.join(out, "consistency.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(out, "consistency.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    if a.unblinded:
        apps = {}
        for r in jsonl(os.path.join(a.state, "blind-key.jsonl")):
            apps[r["blind_id"]] = (r.get("model_key"), r.get("condition"), r.get("arm"))
        for r in jsonl(os.path.join(a.state, "calibration-key.jsonl")):
            apps[r["blind_id"]] = (r.get("model"), r.get("condition"), r.get("arm"))
        with open(a.unblinded, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["blind_id", "model", "task", "condition", "arm", "score_of_record", "graded_on"])
            for r in rows:
                if r["kind"] == "first":
                    m, c, arm = apps.get(r["blind_id"], (None, None, None))
                    w.writerow([r["blind_id"], m, r["task"], c, arm, r["score"], r["graded_on"]])

    for task, t in report["tasks"].items():
        print(f"{task}: {t['pairs']} pairs, mean abs diff {fmt(t['mean_abs_diff'])}, ICC {fmt(t['icc_a1'], 3)}: {t['verdict']}")
    print(f"{len(sheets)} gradings merged, {len(rejected)} incomplete left out -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
