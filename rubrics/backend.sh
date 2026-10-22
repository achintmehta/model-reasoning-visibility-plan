#!/usr/bin/env bash
# backend.sh — find the backend of the app under grading, and pause, resume or kill it.
#
#   backend.sh [status]          show what it detected
#   backend.sh pause             kill -STOP the backend (requests wait, the event stream goes quiet)
#   backend.sh resume            kill -CONT it
#   backend.sh kill              kill -9 it (the restart step), then show what is still listening
#
#   Options, before the command:
#     -d DIR    the app's folder (default: the current folder)
#     -p PORT   the backend's port, when detection finds more than one candidate
#
# DETECTION. The backend is the process that LISTENS on a TCP port, belongs to this app, and is
# not the frontend's dev server:
#   - "belongs to this app": its working directory, or a path in its command line, is inside
#     the app's folder (so another app or service on the machine is never touched);
#   - "not the dev server": its command line does not name vite (or another dev server), and
#     its port does not answer like one (a Vite page loads /@vite/client).
# It pauses the LISTENING process itself, not `npm` or `concurrently` above it: pausing those
# does nothing to the server. Exactly one candidate is required; with none or several it lists
# what it saw and stops, and -p PORT picks one. An app whose backend also serves the page has
# one candidate, which is the backend.
set -euo pipefail

DIR="."; PORT=""
usage() { sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
while getopts ":d:p:h" o; do
  case "$o" in d) DIR="$OPTARG" ;; p) PORT="$OPTARG" ;; *) usage ;; esac
done
shift $((OPTIND - 1))
CMD="${1:-status}"
case "$CMD" in status|pause|resume|kill) ;; *) usage ;; esac
APP="$(cd "$DIR" && pwd -P)"
command -v ss >/dev/null || { echo "backend.sh: needs ss (iproute2)" >&2; exit 3; }

is_devserver_cmd() {   # the frontend's dev server, by its command line
  grep -qiE '(^|[/ ])(vite|webpack-dev-server|webpack serve|parcel|react-scripts start|next dev|astro dev)([ .]|$)|/vite/bin/|vite\.js' <<<"$1"
}
is_devserver_port() {  # ... or by what its port answers
  local body
  body="$(curl -s -m 2 "http://127.0.0.1:$1/" 2>/dev/null || true)"
  grep -q '/@vite/client' <<<"$body"
}
in_app() {             # $1 = pid: its cwd, or a path in its command line, is inside the app
  local cwd cmd
  cwd="$(readlink "/proc/$1/cwd" 2>/dev/null || true)"
  cmd="$(tr '\0' ' ' <"/proc/$1/cmdline" 2>/dev/null || true)"
  [[ "$cwd" == "$APP" || "$cwd" == "$APP"/* || " $cmd" == *" $APP"* ]]
}

# every (port, pid) pair that is listening, from ss's users:(("name",pid=N,fd=M),...)
mapfile -t PAIRS < <(ss -ltnpH 2>/dev/null | awk '{
  n = split($4, a, ":"); port = a[n]
  s = $0
  while (match(s, /pid=[0-9]+/)) { print port, substr(s, RSTART + 4, RLENGTH - 4); s = substr(s, RSTART + RLENGTH) }
}' | sort -u)

declare -A PORTS_OF=() KIND_OF=()
for pr in "${PAIRS[@]}"; do
  port="${pr% *}"; pid="${pr#* }"
  [[ -r "/proc/$pid/cmdline" ]] || continue
  in_app "$pid" || continue
  PORTS_OF[$pid]="${PORTS_OF[$pid]:-}${PORTS_OF[$pid]:+,}$port"
done

CANDS=()
for pid in "${!PORTS_OF[@]}"; do
  cmd="$(tr '\0' ' ' <"/proc/$pid/cmdline")"
  first="${PORTS_OF[$pid]%%,*}"
  if is_devserver_cmd "$cmd" || is_devserver_port "$first"; then
    KIND_OF[$pid]="dev server (frontend)"
  else
    KIND_OF[$pid]="backend candidate"
    CANDS+=("$pid")
  fi
done

show() {
  local pid="$1" cmd st
  cmd="$(tr '\0' ' ' <"/proc/$pid/cmdline" 2>/dev/null | cut -c1-110)"
  st="$(awk '{print $3}' "/proc/$pid/stat" 2>/dev/null || echo '?')"
  printf '  pid %-7s port %-11s %-22s state %s  %s\n' "$pid" "${PORTS_OF[$pid]}" "${KIND_OF[$pid]}" \
    "$([[ "$st" == T ]] && echo 'PAUSED ' || echo "$st      ")" "$cmd"
}

if [[ -n "$PORT" ]]; then
  CANDS=()
  for pid in "${!PORTS_OF[@]}"; do
    [[ ",${PORTS_OF[$pid]}," == *",$PORT,"* ]] && CANDS+=("$pid")
  done
fi

if (( ${#CANDS[@]} != 1 )); then
  echo "App folder: $APP"
  if (( ${#PORTS_OF[@]} == 0 )); then
    echo "Nothing of this app is listening on a port. Is the app running, and is this its folder (-d)?"
  else
    echo "Listening processes of this app:"
    for pid in "${!PORTS_OF[@]}"; do show "$pid"; done
    if [[ -n "$PORT" ]]; then echo "None of them listens on port $PORT."
    elif (( ${#CANDS[@]} == 0 )); then echo "No backend candidate: every listener looks like a dev server. Give the port with -p."
    else echo "More than one backend candidate. Give the backend's port with -p PORT."; fi
  fi
  exit 1
fi

PID="${CANDS[0]}"
case "$CMD" in
  status)
    echo "App folder: $APP"
    for pid in "${!PORTS_OF[@]}"; do show "$pid"; done
    echo "Backend: pid $PID, port ${PORTS_OF[$PID]}" ;;
  pause)
    kill -STOP "$PID"; sleep 0.2
    [[ "$(awk '{print $3}' "/proc/$PID/stat")" == T ]] || { echo "pid $PID did not stop" >&2; exit 1; }
    echo "PAUSED backend: pid $PID, port ${PORTS_OF[$PID]}. Resume with: backend.sh resume" ;;
  resume)
    kill -CONT "$PID"; sleep 0.2
    [[ "$(awk '{print $3}' "/proc/$PID/stat")" != T ]] || { echo "pid $PID is still stopped" >&2; exit 1; }
    echo "RESUMED backend: pid $PID, port ${PORTS_OF[$PID]}" ;;
  kill)
    kill -CONT "$PID" 2>/dev/null || true      # a paused process is killed just the same; resume first anyway
    kill -9 "$PID"
    for _ in $(seq 1 20); do [[ -e "/proc/$PID" ]] || break; sleep 0.1; done
    echo "KILLED backend: pid $PID (port ${PORTS_OF[$PID]})."
    echo "Now Ctrl-C the rest of the app and check its ports are free:"
    ss -ltnpH 2>/dev/null | awk -v p=",${PORTS_OF[$PID]}," '{n=split($4,a,":"); if (index(p, ","a[n]",")) print "  still listening:", $0}'
    ;;
esac
