#!/usr/bin/env python3
"""seed_card.py — create kanban cards through the app's own API (the kanban card's seeding fallback).

Use it only when the interface cannot create a card, or cannot create one in the column needed
(kanban-board.rubric.md, "Seeding fallback"):

    python3 seed_card.py [--host HOST] <backend-port> <column-number> <text> [<text> ...]
    python3 seed_card.py 3001 1 apple banana cherry date
    python3 seed_card.py 3001 2 elder fig

Find the backend's port with `backend.sh status`.

The board:
- It reads GET /api/board (spec 2.4) the way api_probe.py does, with the same code, so the two
  never disagree about what the board holds.
- Columns are numbered from 1, in the order the API lists them, which the spec makes their
  order by position (2.3, 2.4): column 1 is the leftmost on screen. The script prints the
  columns' titles; check that column 1 is the one you mean.
- Cards are read in the order the API lists them within their column.

The request:
- The spec names POST /api/cards (3.1) but not the body's fields, so it tries columnId, then
  column_id, with the text as `text`, `title` or `content`, then all of them at once; then the
  same bodies at POST /api/columns/<id>/cards.
- It moves on to the next shape only when the server rejects the shape (400, 404, 405, 415,
  422). On any other answer, or none, it stops, because the card may already be stored.

The checks:
- A text already on the board is skipped, so a re-run never stores a card twice.
- After each create it reads the board again. If the card is not there exactly once, at the
  end of the column, it prints a WARNING: note it, it is not a fail.
- The exit status is non-zero only when a card could not be created.

It never changes the app's files and uses only the API the app already serves. Stdlib only;
it imports api_probe.py from its own folder.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api_probe import (CARD_TEXT_KEYS, Client, is_2xx, is_vite, locate,  # noqa: E402
                       parse_board, pick_host, status_text)

SHAPE_REJECTED = {400, 404, 405, 415, 422}
BODIES = [("columnId", t) for t in CARD_TEXT_KEYS] + [("column_id", t) for t in CARD_TEXT_KEYS] + [
    ("columnId", "column_id", "column") + CARD_TEXT_KEYS]


def raw_columns(board):
    """The board's column objects as listed, aligned with parse_board's columns."""
    if isinstance(board, list):
        return board
    if isinstance(board, dict):
        if isinstance(board.get("columns"), list):
            return board["columns"]
        lists = [v for v in board.values() if isinstance(v, list) and v and all(isinstance(x, dict) for x in v)]
        return lists[0] if lists else []
    return []


def read_board(client, port, via_vite):
    r = client.request("GET", "/api/board")
    if not is_2xx(r.status) or r.json is None:
        hint = (" Port %s is the Vite dev server, and it does not pass /api/board on: give the "
                "backend's own port (backend.sh status)." % port) if via_vite else \
               " Is %s the backend's port? (backend.sh status)" % port
        sys.exit(f"GET /api/board answered {status_text(r)}"
                 f"{', not JSON' if is_2xx(r.status) else ''}.{hint}")
    _, cols, note = parse_board(r.json)
    if not cols:
        sys.exit(f"GET /api/board: {note}, so no column can be chosen. Body: {json.dumps(r.json)[:200]}")
    labels = []
    for i, c in enumerate(cols):
        raw = raw_columns(r.json)
        rc = raw[i] if i < len(raw) and isinstance(raw[i], dict) else {}
        labels.append(rc.get("title") or rc.get("name") or str(c.get("id")))
    return cols, labels


def body(fields, col_id, text):
    return {f: (text if f in CARD_TEXT_KEYS else col_id) for f in fields}


def create(client, col_id, text):
    """(path, body) of the request that stored the card, or (None, why)."""
    for path in ("/api/cards", f"/api/columns/{col_id}/cards"):
        for fields in BODIES:
            b = body(fields, col_id, text)
            r = client.request("POST", path, b)
            if is_2xx(r.status):
                return path, b
            if r.status not in SHAPE_REJECTED:
                return None, (f"POST {path} {json.dumps(b)} answered {status_text(r)}; stopped, "
                              f"because the card may already be stored. Check the board before running again")
    return None, "every request shape was rejected (400, 404, 405, 415 or 422)"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Create kanban cards through the app's own API (seeding fallback).")
    ap.add_argument("port", type=int, help="the backend's port (backend.sh status)")
    ap.add_argument("column", type=int, help="the column, numbered from 1 left to right")
    ap.add_argument("texts", nargs="+", metavar="text", help="the cards' texts, created in this order")
    ap.add_argument("--host", help="the host (default: 127.0.0.1, then ::1)")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(line_buffering=True)   # keep the printed lines in order with the errors

    host = pick_host(a.port, a.host)
    if host is None:
        sys.exit(f"nothing answers on port {a.port}. Find the backend's port with backend.sh status.")
    via_vite = is_vite(host, a.port)
    client = Client(host, a.port)

    cols, labels = read_board(client, a.port, via_vite)
    print("columns: " + ", ".join(f"{i + 1}={lab}" for i, lab in enumerate(labels)))
    if via_vite:
        print(f"note: port {a.port} is the Vite dev server; the requests go through its proxy to the backend")
    if not 1 <= a.column <= len(cols):
        sys.exit(f"column {a.column} does not exist: the board has {len(cols)} columns")
    col_id = cols[a.column - 1]["id"]
    if col_id is None:
        sys.exit(f"column {a.column} ({labels[a.column - 1]}) has no id in GET /api/board")

    failed = False
    for text in a.texts:
        cols, _ = read_board(client, a.port, via_vite)
        there = locate(cols, text=text)
        if there:
            print(f"{text!r} is already on the board at {[(c + 1, k + 1) for c, k in there]} "
                  f"(column, place); skipped")
            continue
        path, how = create(client, col_id, text)
        if path is None:
            print(f"could not create {text!r}: {how}", file=sys.stderr)
            failed = True
            break
        after, _ = read_board(client, a.port, via_vite)
        hits = locate(after, text=text)
        target = after[a.column - 1]["cards"]
        if len(hits) == 1 and hits[0] == (a.column - 1, len(target) - 1):
            print(f"created {text!r} at the end of column {a.column}, via POST {path} {json.dumps(how)}")
        else:
            where = [(c + 1, k + 1) for c, k in hits] or "nowhere"
            print(f"WARNING: created {text!r} via POST {path} {json.dumps(how)}, but GET /api/board shows "
                  f"it at {where} (column, place), not once at the end of column {a.column}. "
                  f"Note this; it is not a fail.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
