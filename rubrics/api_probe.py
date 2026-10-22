#!/usr/bin/env python3
"""API conformance probe for the model reasoning-visibility study (kanban-board and message-board).

Run it once per app, after the grader's score sheet for that app is complete and while
the app is still running (see the rubric README, "API probe"). It talks to the backend
directly, creates its own test data (texts starting "api-probe"), and writes one JSON
file named after the blind id.

    python3 api_probe.py <kanban-board|message-board> <backend-port> <blind-id> [--out DIR]

Every check tests something the task spec states exactly. Each ends as:
    pass          the app does what the spec says;
    fail          it does not (a missing route, a wrong answer, no event, ...);
    inconclusive  the probe could not tell, because the spec leaves open a detail the
                  probe needs (such as the name of a request body field);
    blocked       the check needs the result of an inconclusive check.
A check whose prerequisite failed because of the app fails too, as in the rubric.
Details the spec leaves open are recorded under "observations" and never scored.

Standard library only. Exit codes: 0 done, 2 usage, 3 nothing answers on the port,
4 the port is a Vite dev server (pass --allow-vite only if the app serves its API there).
"""

import argparse
import datetime
import http.client
import json
import os
import socket
import sys
import threading
import time
import urllib.parse
import uuid

PROBE_VERSION = "1.0.0"
REQUEST_TIMEOUT = 5.0     # seconds for an ordinary request
STREAM_OPEN_WAIT = 3.0    # seconds to wait for the event stream's headers before writing
BROADCAST_WAIT = 2.0      # seconds an event may take to arrive (the rubric's "within 2 seconds")
STREAM_HOLD = 10.0        # the stream must still be open this long after it was opened (as in R1)
TASKS = ("kanban-board", "message-board")

CHECKS = {  # id: (spec task, what it asks). The rubric README lists the same.
    'MB-API1': ('2.4', 'GET /api/messages answers with data (JSON)'),
    'MB-API2': ('3.1', 'GET /api/stream is an event stream that stays open'),
    'MB-API3': ('3.2', 'POST /api/messages stores the message (it then appears in GET /api/messages)'),
    'MB-API4': ('3.3', 'the new message is broadcast on the event stream within 2 s'),
    'KB-API1': ('2.4', 'GET /api/board answers with data (JSON)'),
    'KB-API2': ('2.4', 'the board lists the columns, each with its own cards'),
    'KB-API3': ('3.3', 'GET /api/stream is an event stream that stays open'),
    'KB-API4': ('3.1', 'POST /api/cards stores the card in the requested column'),
    'KB-API5': ('3.1', 'the new card is placed at the end of its column'),
    'KB-API6': ('3.3', 'the create is broadcast with the card and its column id within 2 s'),
    'KB-API7': ('3.2', 'PATCH /api/cards/:id/move with { columnId, beforeId, afterId } is accepted'),
    'KB-API8': ('3.2', 'the move answers with the moved card'),
    'KB-API9': ('3.2', 'the card lands between afterId and beforeId, and only there'),
    'KB-API10': ('3.3', 'the move is broadcast with the card and its column id within 2 s'),
}


# ----------------------------------------------------------------------------- helpers

def now():
    return time.monotonic()


def is_2xx(status):
    return status is not None and 200 <= status < 300


def excerpt(raw, n=400):
    text = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else str(raw)
    return text if len(text) <= n else text[:n] + "..."


def try_json(raw):
    try:
        return json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
    except (ValueError, UnicodeDecodeError, AttributeError):
        return None


def walk_scalars(obj, depth=0):
    """Yield every scalar inside obj. A string that holds JSON is walked as well."""
    if depth > 12:
        return
    if isinstance(obj, dict):
        for v in obj.values():
            yield from walk_scalars(v, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_scalars(v, depth + 1)
    else:
        yield obj
        if isinstance(obj, str) and obj[:1] in ("{", "["):
            inner = try_json(obj)
            if inner is not None:
                yield from walk_scalars(inner, depth + 1)


def norm(v):
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v)


def has_value(obj, value):
    want = norm(value)
    return want is not None and any(norm(x) == want for x in walk_scalars(obj))


def has_text(obj, text):
    return any(isinstance(x, str) and text in x for x in walk_scalars(obj))


def column_values(obj, depth=0):
    """Every value held under a key that names a column (column_id, columnId, toColumn, ...)."""
    out = set()
    if depth > 12:
        return out
    if isinstance(obj, str) and obj[:1] in ("{", "["):
        inner = try_json(obj)
        return column_values(inner, depth + 1) if inner is not None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "column" in str(k).lower():
                if isinstance(v, dict) and "id" in v:
                    out.add(norm(v["id"]))
                elif not isinstance(v, (dict, list)):
                    out.add(norm(v))
            out |= column_values(v, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            out |= column_values(v, depth + 1)
    return out


def shape(obj):
    """A short description of a JSON value's shape, for the observations."""
    if isinstance(obj, list):
        if not obj:
            return "array (empty)"
        first = obj[0]
        if isinstance(first, dict):
            return f"array of {len(obj)} objects, keys {sorted(first.keys())}"
        return f"array of {len(obj)} {type(first).__name__}"
    if isinstance(obj, dict):
        return f"object, keys {sorted(obj.keys())}"
    return type(obj).__name__


# ----------------------------------------------------------------------------- HTTP

class Response:
    def __init__(self, status=None, ctype="", raw=b"", error=None):
        self.status, self.ctype, self.raw, self.error = status, ctype, raw, error
        self.json = try_json(raw) if raw else None


class Client:
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.log = []

    def request(self, method, path, body=None):
        headers = {"Accept": "application/json", "Accept-Encoding": "identity"}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        conn = http.client.HTTPConnection(self.host, self.port, timeout=REQUEST_TIMEOUT)
        try:
            conn.request(method, path, body=data, headers=headers)
            r = conn.getresponse()
            resp = Response(r.status, r.getheader("Content-Type", ""), r.read())
        except (OSError, http.client.HTTPException) as e:
            resp = Response(error=f"{type(e).__name__}: {e}")
        finally:
            conn.close()
        self.log.append({
            "method": method, "path": path, "body": body,
            "status": resp.status, "content_type": resp.ctype,
            "response": excerpt(resp.raw) if resp.raw else None, "error": resp.error,
        })
        return resp


def status_text(resp):
    if resp.status is None:
        return f"no answer ({resp.error})"
    return f"{resp.status} {resp.ctype or 'no content type'}".strip()


class Stream(threading.Thread):
    """Holds GET <path> open as an event stream and records every event it carries."""

    def __init__(self, host, port, path):
        super().__init__(daemon=True)
        self.host, self.port, self.path = host, port, path
        self.status = None
        self.ctype = ""
        self.error = None
        self.headers_at = None
        self.closed_at = None
        self.events = []          # dicts: t, event, data, parsed
        self.lock = threading.Lock()
        self.conn = None
        self.opened = now()

    def run(self):
        try:
            self.conn = http.client.HTTPConnection(self.host, self.port, timeout=60)
            self.conn.request("GET", self.path, headers={
                "Accept": "text/event-stream", "Cache-Control": "no-cache",
                "Accept-Encoding": "identity"})
            r = self.conn.getresponse()
            self.status, self.ctype, self.headers_at = r.status, r.getheader("Content-Type", ""), now()
            if not is_2xx(r.status):
                r.read()
                self.closed_at = now()
                return
            event, data = "message", []
            while True:
                line = r.readline()
                if not line:
                    break
                line = line.decode("utf-8", "replace").rstrip("\r\n")
                if line == "":
                    if data:
                        text = "\n".join(data)
                        with self.lock:
                            self.events.append({"t": now(), "event": event, "data": text,
                                                "parsed": try_json(text)})
                    event, data = "message", []
                    continue
                if line.startswith(":"):
                    continue
                field, _, value = line.partition(":")
                value = value[1:] if value.startswith(" ") else value
                if field == "event":
                    event = value
                elif field == "data":
                    data.append(value)
            self.closed_at = now()
        except (OSError, http.client.HTTPException) as e:
            if self.closed_at is None:
                self.error = f"{type(e).__name__}: {e}"
                self.closed_at = now()

    def is_event_stream(self):
        return is_2xx(self.status) and self.ctype.lower().startswith("text/event-stream")

    def wait_for(self, predicate, since, timeout=BROADCAST_WAIT):
        deadline = since + timeout
        while True:
            with self.lock:
                for ev in self.events:
                    if ev["t"] >= since and predicate(ev):
                        return ev
            if now() >= deadline:
                return None
            time.sleep(0.05)

    def event_payload(self, ev):
        return ev["parsed"] if ev["parsed"] is not None else ev["data"]

    def hold(self, seconds=STREAM_HOLD):
        """Wait until the stream has had `seconds` to stay open (or has closed)."""
        while now() < self.opened + seconds and self.closed_at is None:
            time.sleep(0.1)

    def stop(self):
        try:
            if self.conn and self.conn.sock:
                self.conn.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def summary(self):
        with self.lock:
            return {
                "status": self.status, "content_type": self.ctype, "error": self.error,
                "events": len(self.events),
                "event_names": sorted({e["event"] for e in self.events}),
                "first_events": [excerpt(e["data"], 300) for e in self.events[:5]],
            }


# ----------------------------------------------------------------------------- report

class Report:
    def __init__(self, task, port, blind_id, host):
        self.data = {
            "probe_version": PROBE_VERSION, "task": task, "blind_id": blind_id,
            "host": host, "port": port,
            "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "checks": [], "observations": {},
        }

    def check(self, cid, spec, asks, result, detail):
        assert result in ("pass", "fail", "inconclusive", "blocked")
        assert CHECKS[cid] == (spec, asks), f"{cid} differs from CHECKS"
        self.data["checks"].append({"id": cid, "spec": spec, "asks": asks,
                                    "result": result, "detail": detail})
        return result

    def obs(self, key, value):
        self.data["observations"][key] = value

    def finish(self, client, stream):
        counts = {k: 0 for k in ("pass", "fail", "inconclusive", "blocked")}
        for c in self.data["checks"]:
            counts[c["result"]] += 1
        self.data["summary"] = counts
        self.data["stream"] = stream.summary() if stream else None
        self.data["requests"] = client.log
        self.data["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def dependent(prereq_result, name):
    """Result for a check that cannot run because its prerequisite did not pass."""
    if prereq_result == "inconclusive" or prereq_result == "blocked":
        return "blocked", f"not run: {name} was {prereq_result}"
    return "fail", f"not run: {name} failed"


def stream_check(rep, cid, spec, stream):
    stream.hold()
    if stream.is_event_stream() and stream.closed_at is None:
        return rep.check(cid, spec, "GET /api/stream is an event stream that stays open", "pass",
                         f"{stream.status} {stream.ctype}; open for {now() - stream.opened:.0f} s")
    if stream.status is None:
        why = (f"no response headers within {now() - stream.opened:.0f} s"
               + (f" ({stream.error})" if stream.error else ""))
    elif not is_2xx(stream.status):
        why = f"answered {stream.status}"
    elif not stream.ctype.lower().startswith("text/event-stream"):
        why = f"content type is '{stream.ctype}', not text/event-stream"
    else:
        why = (f"the stream closed after {stream.closed_at - stream.opened:.1f} s"
               f" ({stream.error or 'closed by the server'})")
    return rep.check(cid, spec, "GET /api/stream is an event stream that stays open", "fail", why)


def open_stream(host, port):
    s = Stream(host, port, "/api/stream")
    s.start()
    deadline = now() + STREAM_OPEN_WAIT
    while now() < deadline and s.headers_at is None and s.closed_at is None:
        time.sleep(0.05)
    return s


def route_missing(resps):
    """True when every attempt says the route does not exist (404/405) or got no answer."""
    return all(r.status in (404, 405) or r.status is None for r in resps)


# ----------------------------------------------------------------------------- message-board

def probe_message_board(client, rep, tag):
    r = client.request("GET", "/api/messages")
    if is_2xx(r.status) and r.json is not None:
        p1 = rep.check("MB-API1", "2.4", "GET /api/messages answers with data (JSON)", "pass", status_text(r))
        rep.obs("messages_shape", shape(r.json))
    else:
        why = status_text(r) if not is_2xx(r.status) else f"{status_text(r)}, and the body is not JSON"
        p1 = rep.check("MB-API1", "2.4", "GET /api/messages answers with data (JSON)", "fail", why)

    stream = open_stream(client.host, client.port)

    # The spec names POST /api/messages but not its body field, so try the likely names.
    attempts, success, resps = [], None, []
    candidates = [("text",), ("message",), ("content",), ("text", "message", "content", "body", "msg")]
    for i, fields in enumerate(candidates, 1):
        text = f"api-probe {tag} message {i}"
        body = {f: text for f in fields}
        sent = now()
        pr = client.request("POST", "/api/messages", body)
        resps.append(pr)
        gr = client.request("GET", "/api/messages")
        stored = gr.json is not None and has_text(gr.json, text)
        attempts.append({"fields": list(fields), "status": pr.status, "stored": stored})
        if is_2xx(pr.status) and stored:
            success = (fields, text, sent, pr)
            break
    rep.obs("post_attempts", attempts)
    asks3 = "POST /api/messages stores the message (it then appears in GET /api/messages)"
    if success:
        fields, text, sent, pr = success
        p3 = rep.check("MB-API3", "3.2", asks3, "pass", f"{pr.status}; body field {'/'.join(fields)}")
        rep.obs("post_body_field", "/".join(fields) if len(fields) == 1 else "only the combined body worked")
        rep.obs("post_response", shape(pr.json) if pr.json is not None else excerpt(pr.raw, 120))
    elif route_missing(resps):
        p3 = rep.check("MB-API3", "3.2", asks3, "fail",
                       "no such route: " + ", ".join(status_text(x) for x in resps))
    elif p1 == "fail":
        p3 = rep.check("MB-API3", "3.2", asks3, "fail", "the message list cannot be read (MB-API1 failed)")
    else:
        p3 = rep.check("MB-API3", "3.2", asks3, "inconclusive",
                       "the route exists but no tried body field was stored: " +
                       ", ".join(f"{'/'.join(a['fields'])} -> {a['status']}" for a in attempts))

    asks4 = "the new message is broadcast on the event stream within 2 s"
    if p3 != "pass":
        rep.check("MB-API4", "3.3", asks4, *dependent(p3, "MB-API3"))
    elif not stream.is_event_stream():
        rep.check("MB-API4", "3.3", asks4, "fail", "no event stream to carry it (see MB-API2)")
    else:
        ev = stream.wait_for(lambda e: has_text(stream.event_payload(e), text), sent)
        if ev:
            rep.check("MB-API4", "3.3", asks4, "pass",
                      f"event '{ev['event']}' after {ev['t'] - sent:.2f} s")
            rep.obs("broadcast_event", {"event": ev["event"], "data": excerpt(ev["data"], 300)})
        else:
            rep.check("MB-API4", "3.3", asks4, "fail", "no event carrying the message within 2 s")

    stream_check(rep, "MB-API2", "3.1", stream)
    rep.data["checks"].sort(key=lambda c: int(c["id"].split("API")[1]))

    # How the server answers a message with empty text. The spec does not address it, so it is
    # an OBSERVATION, never scored; it replaces the card's former item MB-E2 (rubric v2.1),
    # which sent the same `{"text": ""}` from the browser console. Made last, so a blank message
    # the server accepts cannot affect anything checked above.
    rep.obs("empty_message", empty_message(client, success[0] if success else None))
    return stream


def _message_count(obj):
    """How many messages a GET /api/messages answer holds: a list, or the first list value of
    an object (e.g. {"messages": [...]}); None when neither."""
    if isinstance(obj, list):
        return len(obj)
    if isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, list):
                return len(v)
    return None


def empty_message(client, fields):
    """POST a message whose text is empty: `{"text": ""}`, as the former card item did, and
    again under the body field MB-API3 found if that is another one. Records each answer's
    status, its class (refused 4xx / accepted 2xx / server error 5xx), and whether the list
    grew, i.e. the blank message was stored."""
    bodies = [{"text": ""}]
    if fields and tuple(fields) != ("text",):
        bodies.append({f: "" for f in fields})
    out = []
    for body in bodies:
        before = client.request("GET", "/api/messages")
        n0 = _message_count(before.json) if before.json is not None else None
        r = client.request("POST", "/api/messages", body)
        after = client.request("GET", "/api/messages")
        n1 = _message_count(after.json) if after.json is not None else None
        s = r.status
        cls = ("no answer" if s is None else f"no such route ({s})" if s in (404, 405)
               else "refused (4xx)" if 400 <= s < 500
               else "accepted (2xx)" if 200 <= s < 300 else "server error (5xx)" if s >= 500
               else f"other ({s})")
        out.append({"body": body, "status": s, "answer": cls,
                    # None: the message list could not be read, so it is not known
                    "stored": (n1 > n0) if (n0 is not None and n1 is not None) else None})
    return out


# ----------------------------------------------------------------------------- kanban-board

CARD_TEXT_KEYS = ("text", "title", "content")


def card_id(card):
    for k in ("id", "_id", "cardId", "card_id"):
        if k in card:
            return card[k]
    return None


def card_text(card):
    for k in CARD_TEXT_KEYS:
        if isinstance(card.get(k), str):
            return card[k]
    return None


def nested_cards(col):
    """The list of cards nested in a column object, or None."""
    if isinstance(col.get("cards"), list):
        return col["cards"]
    lists = [v for v in col.values() if isinstance(v, list) and all(isinstance(x, dict) for x in v)]
    return lists[0] if len(lists) == 1 else None


def parse_board(board):
    """Return (nested_ok, columns, note). columns: [{"id", "title", "cards": [card, ...]}]."""
    cols = None
    if isinstance(board, list):
        cols = board
    elif isinstance(board, dict):
        if isinstance(board.get("columns"), list):
            cols = board["columns"]
        else:
            lists = [v for v in board.values() if isinstance(v, list) and v and all(isinstance(x, dict) for x in v)]
            cols = lists[0] if lists else None
    if not cols or not all(isinstance(c, dict) for c in cols):
        return False, [], "no list of columns found"

    nested = [nested_cards(c) for c in cols]
    if all(n is not None for n in nested):
        return True, [{"id": c.get("id"), "title": c.get("title"),
                       "cards": [x for x in n if isinstance(x, dict)]}
                      for c, n in zip(cols, nested)], "columns each hold their cards"

    # Flat fallback: {"columns": [...], "cards": [...]} -- build the view to keep probing.
    flat = board.get("cards") if isinstance(board, dict) else None
    if isinstance(flat, list):
        view = []
        for c in cols:
            mine = [x for x in flat if isinstance(x, dict) and
                    norm(x.get("column_id", x.get("columnId"))) == norm(c.get("id"))]
            if all("position" in x for x in mine):
                mine.sort(key=lambda x: x["position"])
            view.append({"id": c.get("id"), "title": c.get("title"), "cards": mine})
        return False, view, "cards are listed apart from their columns"
    return False, [], "the columns do not hold their cards"


def locate(columns, cid=None, text=None):
    """Every (column index, card index) where the card appears."""
    hits = []
    for ci, col in enumerate(columns):
        for k, card in enumerate(col["cards"]):
            if cid is not None and norm(card_id(card)) == norm(cid):
                hits.append((ci, k))
            elif cid is None and text is not None and card_text(card) == text:
                hits.append((ci, k))
    return hits


def event_places_card(payload, card, column, text=None):
    """True when an event carries the card (by id, or by text for a new card) with the column's id.

    Matching on keys rather than on any value keeps a small integer such as a position from
    standing in for an id. An event carrying the whole board passes when the board shows the
    card in that column."""
    ok, cols, _ = parse_board(payload) if isinstance(payload, (dict, list)) else (False, [], "")
    if ok:
        hits = locate(cols, cid=card, text=text) if card is not None else locate(cols, text=text)
        return any(norm(cols[ci]["id"]) == norm(column) for ci, _ in hits)
    if norm(column) not in column_values(payload):
        return False
    if card is None:
        return has_text(payload, text)
    return contains_card(payload, card)


def contains_card(obj, card):
    """True when obj holds an object whose id (or cardId) is the card's id."""
    stack = [obj]
    while stack:
        o = stack.pop()
        if isinstance(o, str) and o[:1] in ("{", "["):
            o = try_json(o)
        if isinstance(o, dict):
            if norm(card_id(o)) == norm(card) or norm(o.get("cardId")) == norm(card):
                return True
            stack.extend(o.values())
        elif isinstance(o, list):
            stack.extend(o)
    return False


def probe_kanban(client, rep, tag):
    def board():
        r = client.request("GET", "/api/board")
        ok, cols, note = parse_board(r.json) if r.json is not None else (False, [], "not JSON")
        return r, ok, cols, note

    r, nested_ok, cols, note = board()
    asks1 = "GET /api/board answers with data (JSON)"
    if is_2xx(r.status) and r.json is not None:
        p1 = rep.check("KB-API1", "2.4", asks1, "pass", status_text(r))
        rep.obs("board_shape", shape(r.json))
    else:
        why = status_text(r) if not is_2xx(r.status) else f"{status_text(r)}, and the body is not JSON"
        p1 = rep.check("KB-API1", "2.4", asks1, "fail", why)

    asks2 = "the board lists the columns, each with its own cards"
    if p1 != "pass":
        rep.check("KB-API2", "2.4", asks2, *dependent(p1, "KB-API1"))
    elif nested_ok:
        rep.check("KB-API2", "2.4", asks2, "pass", f"{len(cols)} columns; {note}")
    else:
        rep.check("KB-API2", "2.4", asks2, "fail", note)
    if cols:
        rep.obs("columns", [{"id": c["id"], "title": c["title"], "cards": len(c["cards"])} for c in cols])
        first_card = next((c["cards"][0] for c in cols if c["cards"]), None)
        if first_card:
            rep.obs("card_keys", sorted(first_card.keys()))
            if all("position" in x for c in cols for x in c["cards"]):
                try:
                    ordered = all(all(a["position"] <= b["position"] for a, b in zip(c["cards"], c["cards"][1:]))
                                  for c in cols)
                except TypeError:
                    ordered = None
                rep.obs("cards_listed_in_position_order", ordered)
            else:
                rep.obs("cards_listed_in_position_order", "positions not exposed")

    stream = open_stream(client.host, client.port)

    # ---- create (spec 3.1): the spec does not name the body fields, so try the likely ones.
    templates = [
        ("columnId", "text"),
        ("column_id", "text"),
        ("columnId", "column_id", "column", "text", "title", "content"),
    ]

    def body_for(fields, col_id, text):
        return {f: (text if f in CARD_TEXT_KEYS else col_id) for f in fields}

    attempts, created, resps = [], None, []
    a_col = cols[0] if cols else None
    if a_col is not None and a_col["id"] is not None:
        for i, fields in enumerate(templates, 1):
            text = f"api-probe {tag} card {i}"
            sent = now()
            pr = client.request("POST", "/api/cards", body_for(fields, a_col["id"], text))
            resps.append(pr)
            _, _, after, _ = board()
            hits = locate(after, text=text)
            where = [after[ci]["id"] for ci, _ in hits]
            attempts.append({"fields": list(fields), "status": pr.status, "found_in_columns": where})
            if is_2xx(pr.status) and hits and all(norm(after[ci]["id"]) == norm(a_col["id"]) for ci, _ in hits):
                created = {"fields": fields, "text": text, "sent": sent, "resp": pr, "board": after, "hits": hits}
                break
    rep.obs("create_attempts", attempts)

    asks4 = "POST /api/cards stores the card in the requested column"
    if created:
        p4 = rep.check("KB-API4", "3.1", asks4, "pass",
                       f"{created['resp'].status}; body fields {'/'.join(created['fields'])}")
        rep.obs("create_response", shape(created["resp"].json) if created["resp"].json is not None
                else excerpt(created["resp"].raw, 120))
    elif p1 != "pass" or not cols:
        p4 = rep.check("KB-API4", "3.1", asks4, *dependent(p1 if p1 != "pass" else "fail",
                                                           "KB-API1 (no columns to create in)"))
    elif route_missing(resps):
        p4 = rep.check("KB-API4", "3.1", asks4, "fail",
                       "no such route: " + ", ".join(status_text(x) for x in resps))
    else:
        p4 = rep.check("KB-API4", "3.1", asks4, "inconclusive",
                       "the route exists but no tried body stored the card in the requested column: " +
                       ", ".join(f"{'/'.join(a['fields'][:2])}{'/...' if len(a['fields']) > 2 else ''}"
                                 f" -> {a['status']}, found in {a['found_in_columns'] or 'no column'}"
                                 for a in attempts))

    asks5 = "the new card is placed at the end of its column"
    if p4 != "pass":
        rep.check("KB-API5", "3.1", asks5, *dependent(p4, "KB-API4"))
    else:
        ci, k = created["hits"][0]
        n = len(created["board"][ci]["cards"])
        if len(created["hits"]) > 1:
            rep.check("KB-API5", "3.1", asks5, "fail", f"the card was stored {len(created['hits'])} times")
        elif k == n - 1:
            rep.check("KB-API5", "3.1", asks5, "pass", f"last of {n} cards")
        else:
            rep.check("KB-API5", "3.1", asks5, "fail", f"card {k + 1} of {n}, not the last")

    asks6 = "the create is broadcast with the card and its column id within 2 s"
    if p4 != "pass":
        rep.check("KB-API6", "3.3", asks6, *dependent(p4, "KB-API4"))
    elif not stream.is_event_stream():
        rep.check("KB-API6", "3.3", asks6, "fail", "no event stream to carry it (see KB-API3)")
    else:
        ev = stream.wait_for(lambda e: event_places_card(stream.event_payload(e), None, a_col["id"],
                                                         created["text"]), created["sent"])
        bare = stream.wait_for(lambda e: has_text(stream.event_payload(e), created["text"]),
                               created["sent"], timeout=0) if ev is None else None
        if ev is None and bare is None:
            rep.check("KB-API6", "3.3", asks6, "fail", "no event carrying the new card within 2 s")
        elif ev is None:
            rep.check("KB-API6", "3.3", asks6, "fail",
                      f"event '{bare['event']}' carries the card but not its column id")
        else:
            rep.check("KB-API6", "3.3", asks6, "pass", f"event '{ev['event']}' after {ev['t'] - created['sent']:.2f} s")
            rep.obs("create_event", {"event": ev["event"], "data": excerpt(ev["data"], 300)})

    # ---- move (spec 3.2): body { columnId, beforeId, afterId } is exact.
    move_setup, setup_note = None, None
    if created and len(cols) >= 2:
        fields = created["fields"]
        b_col = cols[1]
        ids = {}
        for name, col in (("x", a_col), ("y", a_col), ("m", b_col)):
            text = f"api-probe {tag} move-{name}"
            client.request("POST", "/api/cards", body_for(fields, col["id"], text))
            _, _, after, _ = board()
            hits = locate(after, text=text)
            ids[name] = card_id(after[hits[0][0]]["cards"][hits[0][1]]) if hits else None
        if all(v is not None for v in ids.values()):
            move_setup = {"target": a_col, "x": ids["x"], "y": ids["y"], "m": ids["m"], "source": b_col}
            setup_note = "probe's own cards"
    if move_setup is None and cols:
        # Fall back on cards already on the board (left there by the grader's session).
        target = next((c for c in cols if len(c["cards"]) >= 2), None)
        mover = next((x for c in cols if c is not target for x in c["cards"]), None) if target else None
        if target and mover and all(card_id(x) is not None for x in (target["cards"][0], target["cards"][1], mover)):
            move_setup = {"target": target, "x": card_id(target["cards"][0]), "y": card_id(target["cards"][1]),
                          "m": card_id(mover), "source": None}
            setup_note = "cards already on the board (the probe could not create its own)"
    rep.obs("move_setup", setup_note or "none possible")

    asks7 = "PATCH /api/cards/:id/move with { columnId, beforeId, afterId } is accepted"
    asks8 = "the move answers with the moved card"
    asks9 = "the card lands between afterId and beforeId, and only there"
    asks10 = "the move is broadcast with the card and its column id within 2 s"
    if move_setup is None:
        if p4 != "pass":
            prereq, why_name = p4, "KB-API4 (and no cards on the board to use instead)"
        else:
            prereq, why_name = "fail", "the move setup (the board has fewer than two columns)"
        for cid, asks in (("KB-API7", asks7), ("KB-API8", asks8), ("KB-API9", asks9), ("KB-API10", asks10)):
            rep.check(cid, "3.2" if cid != "KB-API10" else "3.3", asks, *dependent(prereq, why_name))
    else:
        t, m = move_setup["target"], move_setup["m"]
        body = {"columnId": t["id"], "afterId": move_setup["x"], "beforeId": move_setup["y"]}
        path = "/api/cards/" + urllib.parse.quote(str(m), safe="") + "/move"
        time.sleep(0.2)   # let earlier events arrive first
        sent = now()
        mr = client.request("PATCH", path, body)
        p7 = rep.check("KB-API7", "3.2", asks7, "pass" if is_2xx(mr.status) else "fail", status_text(mr))
        if p7 != "pass":
            rep.check("KB-API8", "3.2", asks8, *dependent(p7, "KB-API7"))
        elif mr.json is not None and contains_card(mr.json, m):
            rep.check("KB-API8", "3.2", asks8, "pass", shape(mr.json))
        else:
            rep.check("KB-API8", "3.2", asks8, "fail",
                      "the answer does not contain the card: " + (excerpt(mr.raw, 120) if mr.raw else "empty body"))
        _, _, after, _ = board()
        hits = locate(after, cid=m)
        if p7 != "pass":
            rep.check("KB-API9", "3.2", asks9, *dependent(p7, "KB-API7"))
        elif len(hits) != 1:
            rep.check("KB-API9", "3.2", asks9, "fail", f"the card appears {len(hits)} times on the board")
        else:
            ci, k = hits[0]
            col = after[ci]
            order = [norm(card_id(x)) for x in col["cards"]]
            if norm(col["id"]) != norm(t["id"]):
                rep.check("KB-API9", "3.2", asks9, "fail", "the card is in another column")
            elif (norm(move_setup["x"]) in order and norm(move_setup["y"]) in order
                  and order.index(norm(move_setup["x"])) == k - 1 and order.index(norm(move_setup["y"])) == k + 1):
                rep.check("KB-API9", "3.2", asks9, "pass", f"card {k + 1} of {len(order)}, between its neighbours")
            else:
                rep.check("KB-API9", "3.2", asks9, "fail",
                          f"card {k + 1} of {len(order)}; afterId is at "
                          f"{order.index(norm(move_setup['x'])) + 1 if norm(move_setup['x']) in order else 'none'}, "
                          f"beforeId at {order.index(norm(move_setup['y'])) + 1 if norm(move_setup['y']) in order else 'none'}")
        if p7 != "pass":
            rep.check("KB-API10", "3.3", asks10, *dependent(p7, "KB-API7"))
        elif not stream.is_event_stream():
            rep.check("KB-API10", "3.3", asks10, "fail", "no event stream to carry it (see KB-API3)")
        else:
            ev = stream.wait_for(lambda e: event_places_card(stream.event_payload(e), m, t["id"]), sent)
            if ev:
                rep.check("KB-API10", "3.3", asks10, "pass", f"event '{ev['event']}' after {ev['t'] - sent:.2f} s")
                rep.obs("move_event", {"event": ev["event"], "data": excerpt(ev["data"], 300)})
            else:
                rep.check("KB-API10", "3.3", asks10, "fail", "no event carrying the card and its column id within 2 s")

        # Observation only: how a missing neighbour is sent (the spec does not say).
        if p7 == "pass" and move_setup["source"] is not None:
            src = move_setup["source"]
            _, _, now_board, _ = board()
            src_now = next((c for c in now_board if norm(c["id"]) == norm(src["id"])), None)
            last = card_id(src_now["cards"][-1]) if src_now and src_now["cards"] else None
            results = {}
            for label, b in (("null", {"columnId": src["id"], "afterId": last, "beforeId": None}),
                             ("omitted", {"columnId": src["id"], "afterId": last})):
                rr = client.request("PATCH", path, b)
                _, _, nb, _ = board()
                h = locate(nb, cid=m)
                at_end = (len(h) == 1 and norm(nb[h[0][0]]["id"]) == norm(src["id"])
                          and h[0][1] == len(nb[h[0][0]]["cards"]) - 1)
                results[label] = {"status": rr.status, "landed_at_end": at_end}
                if is_2xx(rr.status) and at_end:
                    break
            rep.obs("move_with_missing_neighbours", {"body": "afterId = the column's last card or null; "
                                                             "beforeId null, then left out", **results})

    stream_check(rep, "KB-API3", "3.3", stream)
    rep.data["checks"].sort(key=lambda c: int(c["id"].split("API")[1]))
    return stream


# ----------------------------------------------------------------------------- main

def pick_host(port, forced=None):
    for host in ([forced] if forced else ["127.0.0.1", "::1"]):
        try:
            with socket.create_connection((host, port), timeout=2):
                return host
        except OSError:
            continue
    return None


def is_vite(host, port):
    conn = http.client.HTTPConnection(host, port, timeout=REQUEST_TIMEOUT)
    try:
        conn.request("GET", "/@vite/client")
        r = conn.getresponse()
        raw = r.read(200000)
        # A catch-all route that serves index.html for every path must not count as Vite.
        return (r.status == 200 and "javascript" in (r.getheader("Content-Type") or "")
                and b"vite" in raw.lower())
    except (OSError, http.client.HTTPException):
        return False
    finally:
        conn.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("task", choices=TASKS)
    ap.add_argument("port", type=int, help="the port the backend listens on")
    ap.add_argument("blind_id")
    ap.add_argument("--out", default=".", help="folder for <blind id>.api-probe.json (default: here)")
    ap.add_argument("--host", default=None, help="default: 127.0.0.1, then ::1")
    ap.add_argument("--allow-vite", action="store_true",
                    help="probe a Vite dev server's port (only when the app serves its API there)")
    ap.add_argument("--no-backend", action="store_true",
                    help="record that no backend runs, even with accommodations: every check fails")
    a = ap.parse_args(argv)

    out_path = os.path.join(a.out, f"{a.blind_id}.api-probe.json")
    rep = Report(a.task, a.port, a.blind_id, a.host)

    if a.no_backend:
        client = Client(a.host or "127.0.0.1", a.port)
        rep.data["no_backend"] = True
        prefix = "MB-" if a.task == "message-board" else "KB-"
        for n, (spec, asks) in CHECKS.items():
            if n.startswith(prefix):
                rep.check(n, spec, asks, "fail", "no backend runs, even with accommodations (grader's record)")
        rep.finish(client, None)
    else:
        host = pick_host(a.port, a.host)
        if host is None:
            print(f"Nothing answers on port {a.port}. Check the backend's port with "
                  f"`ss -ltnp`. If no backend runs at all, re-run with --no-backend.", file=sys.stderr)
            return 3
        rep.data["host"] = host
        if is_vite(host, a.port) and not a.allow_vite:
            print(f"Port {a.port} is a Vite dev server, not the backend. Give the backend's own port. "
                  f"Use --allow-vite only if the app serves its API from Vite itself.", file=sys.stderr)
            return 4
        client = Client(host, a.port)
        tag = uuid.uuid4().hex[:6]
        probe = probe_message_board if a.task == "message-board" else probe_kanban
        stream = probe(client, rep, tag)
        stream.stop()
        rep.finish(client, stream)

    os.makedirs(a.out, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rep.data, f, indent=2, default=str)

    for c in rep.data["checks"]:
        print(f"{c['id']:<9} {c['result']:<12} {c['asks']}\n{'':<22} {c['detail']}")
    s = rep.data["summary"]
    print(f"\n{s['pass']} pass, {s['fail']} fail, {s['inconclusive']} inconclusive, {s['blocked']} blocked"
          f"  ->  {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
