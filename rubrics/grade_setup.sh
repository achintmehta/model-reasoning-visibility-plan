#!/usr/bin/env bash
# grade_setup.sh — make a fresh copy of one app for grading, knowing only its blind id.
#
#   grade_setup.sh [options] <blind id>
#
# Options (each also has an environment variable, so it can be set once per session):
#   --root DIR    a folder of runs in the blind layout, DIR/<task>/runs/<id>/; repeatable
#                 (GRADING_ROOTS, folders separated by ':')
#   --index FILE  "<id><TAB><run folder>" lines, for ids that are not folder names: re-grade
#                 ids and calibration copies; a relative run folder is read from FILE's
#                 folder; lines starting with # are skipped (GRADING_INDEX)
#   --work DIR    where copies go (GRADING_WORK; default ~/grading-work). The copy is
#                 DIR/<blind id>/app. Never under /mnt: PGlite and npm misbehave there.
#
# What it does, in order (rubric README "Before each app"; protocol §5.3; plan §4.5):
#   1. Finds the run. Its path is never printed or recorded: the output names the blind id
#      and the task (which card to use), nothing else about the run.
#   2. Checks that your Node is the run's (its environment.txt); stops with the nvm command if not.
#   3. Copies the run's app/ to DIR/<blind id>/app, without node_modules and .git. The archived
#      run is never changed, except that a lockfile saved by step 5 goes into its log folder.
#   4. Removes the database the app shipped with: every PGlite data folder (one that holds
#      PG_VERSION), and any parent that is left empty. Each removal is logged, beside the
#      lines of the app's code that call new PGlite(...), so you can check the two agree.
#   5. Installs the dependencies in every folder of the app that has a package.json (a
#      workspace member is installed by its workspace root):
#        - npm ci, from that folder's package-lock.json if the run has one;
#        - otherwise npm ci from the grading lockfile an earlier grading saved
#          (<log folder>/grading-lock[.<folder>].json);
#        - otherwise npm install, whose lockfile is then saved there, so every later grading
#          installs the same tree. npm's `before` date must then match the run's.
#      The install output is the evidence for L0. Nothing is retried and no flag is added:
#      A0 is yours to run (npm install --legacy-peer-deps after ERESOLVE; npm install after
#      EUSAGE, a lockfile out of step with its package.json; npm install --no-save <name>@latest
#      after ETARGET, a declared dependency whose range no version before the `before` date matches;
#      the same install with --ignore-scripts when the folder's own preinstall, install, postinstall
#      or prepare script failed), and the summary gives the command.
#   6. Checks the declared launch without running it (launch_check.js): follows npm run dev
#      through every command it runs and warns about what would stop it: a command that is not
#      installed (sh: X: not found), npx fetching a tool, node naming a missing file, a script
#      that does not exist, vite started where there is no page. It decides nothing: L1 and L2
#      are still judged by running the declared command.
#   7. Writes GRADER-ENV.txt (your Node, npm, `before` date, lockfile hashes, OS, browser) and
#      grade-setup.log (everything printed) beside the copy, keeps both with your results
#      (<GRADING_RESULTS>/setup/<blind id>/<when>/, with a0.log for the output of any A0 command
#      the summary prints; a setup that stops early is kept there too), and, when GRADING_RESULTS names
#      your results folder, a blank score sheet there (<blind id>.score.json).
#
# Output: the seven steps above, numbered, each finding on a tagged line: [ OK ] passed, [FAIL]
# failed (an install failure decides L0), [WARN] worth a note, [ DO ] a command for you to run,
# [INFO] for reference; npm's own output is indented under its folder. A SUMMARY at the end
# repeats the verdicts, the warnings, any A0 command and what to do next. Colours on a terminal
# only (NO_COLOR=1 turns them off); the log files are plain text.
#
# Exit status: 0 ready; 3 the copy is ready but an install failed (L0 fails); 1 stopped
# before the copy was ready; 2 usage.
set -uo pipefail

TASKS=(kanban-board message-board)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOTS=()
IFS=: read -r -a _roots <<<"${GRADING_ROOTS:-}"
for r in "${_roots[@]}"; do [ -n "$r" ] && ROOTS+=("$r"); done
INDEX="${GRADING_INDEX:-}"
WORK_BASE="${GRADING_WORK:-$HOME/grading-work}"
ID=""
LOG=""

usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; exit 2; }
SAVE=""; SAVELOG=""; A0X=""; A0SFX=""

# ---- output -------------------------------------------------------------------------------------
# Every line the grader should act on carries a tag:  [ OK ] passed   [FAIL] failed (decides L0)
# [WARN] note it in the sheet   [ DO ] a command for you to run   [INFO] for reference.
# Colours on a terminal only (NO_COLOR=1 turns them off); the log files get plain text.
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_OK=$'\e[1;32m'; C_FAIL=$'\e[1;31m'; C_WARN=$'\e[1;33m'; C_DO=$'\e[1;36m'; C_INFO=$'\e[34m'
  C_HEAD=$'\e[1;4m'; C_DIM=$'\e[2m'; C_OFF=$'\e[0m'
else
  C_OK=""; C_FAIL=""; C_WARN=""; C_DO=""; C_INFO=""; C_HEAD=""; C_DIM=""; C_OFF=""
fi
WARNS=(); TODOS=(); SUMMARY=()
emit() {   # emit <plain line> [<coloured line>]: plain to the logs, coloured to the terminal
  local f
  for f in "$LOG" "$SAVELOG"; do [ -n "$f" ] && printf '%s\n' "$1" >> "$f"; done
  printf '%s\n' "${2:-$1}"
}
tag()     { local c="$1" t="$2"; shift 2; emit "  [$t] $*" "  ${c}[$t]${C_OFF} $*"; }
ok()      { tag "$C_OK" " OK " "$@"; }
bad()     { tag "$C_FAIL" "FAIL" "$@"; }
warn()    { tag "$C_WARN" "WARN" "$@"; WARNS+=("$*"); }
info()    { tag "$C_INFO" "INFO" "$@"; }
todo()    { tag "$C_DO" " DO " "$@"; TODOS+=("$*"); }
say()     { emit "         $*"; }
section() { emit "" ""; emit "[$1] $2" "${C_HEAD}[$1] $2${C_OFF}"; }
sum()     { SUMMARY+=("$1|$2"); }    # sum <OK|FAIL|WARN> <text>: a line of the final summary
die()     { { emit "" ""; tag "$C_FAIL" STOP "$*"; emit "  Nothing is ready: fix this and run grade_setup.sh again."; } >&2; exit 1; }
if ! pwd -P >/dev/null 2>&1 || [ ! -d "$(pwd -P 2>/dev/null)" ]; then
  # A shell left in a folder that has since been removed (an earlier copy of this app, say)
  # makes npm print nothing for its settings; start from the home folder instead.
  cd "$HOME" || exit 2
  printf '  [WARN] your shell'"'"'s current folder no longer exists; working from %s (run cd ~ in your shell)\n' "$HOME"
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --root)  [ $# -ge 2 ] || usage; ROOTS+=("$2"); shift 2 ;;
    --index) [ $# -ge 2 ] || usage; INDEX="$2"; shift 2 ;;
    --work)  [ $# -ge 2 ] || usage; WORK_BASE="$2"; shift 2 ;;
    -h|--help) usage ;;
    -*) echo "grade_setup.sh: unknown option $1" >&2; usage ;;
    *) [ -z "$ID" ] || usage; ID="$1"; shift ;;
  esac
done
[ -n "$ID" ] || usage
# grading-shell.sh's grade_setup.sh function moves your shell into the folder named here, so it
# must never point at an earlier app: clear it first, write it only once this copy is ready.
LAST="$WORK_BASE/.last-setup"; rm -f "$LAST" 2>/dev/null
[[ "$ID" =~ ^[A-Za-z0-9_-]+$ ]] || die "a blind id has only letters, digits, - and _: '$ID'"
# Keep this setup's log, the grader environment and any A0 output with the results, where they
# are committed with the score sheets: <results>/setup/<blind id>/<when>/. The copy in
# GRADING_WORK is scratch and goes when the id is set up again.
if [ -n "${GRADING_RESULTS:-}" ]; then
  SAVE="$GRADING_RESULTS/setup/$ID/$(date +%Y%m%d-%H%M%S)"
  if mkdir -p "$SAVE" 2>/dev/null; then
    SAVELOG="$SAVE/grade-setup.log"
    A0X="set -x && "; A0SFX=" 2>&1 | tee -a '$SAVE/a0.log'"
  else
    printf '  [WARN] cannot create %s; this setup is logged only beside the copy\n' "$SAVE" >&2
    SAVE=""
  fi
fi
[ ${#ROOTS[@]} -gt 0 ] || [ -n "$INDEX" ] || die "no runs to look in: give --root (GRADING_ROOTS) or --index (GRADING_INDEX)"
command -v node >/dev/null && command -v npm >/dev/null || die "node and npm must be on the PATH (nvm use <the study's Node>)"
command -v python3 >/dev/null || die "python3 is needed"

# ---- 1. find the run ------------------------------------------------------------------------
cands=()
if [ -n "$INDEX" ]; then
  [ -f "$INDEX" ] || die "index file not found: $INDEX"
  idir="$(cd "$(dirname "$INDEX")" && pwd)"
  while IFS=$'\t' read -r k p _; do
    [ "$k" = "$ID" ] && [ -n "$p" ] || continue
    case "$p" in /*) ;; *) p="$idir/$p" ;; esac
    cands+=("$p")
  done < <(grep -v '^[[:space:]]*#' "$INDEX" | tr -d '\r')
fi
for r in "${ROOTS[@]}"; do
  [ -d "$r" ] || die "root not found: $r"
  for p in "$r"/*/runs/"$ID"; do [ -d "$p" ] && cands+=("$p"); done
done
runs=()
while IFS= read -r p; do [ -n "$p" ] && runs+=("$p"); done < <(
  for p in "${cands[@]}"; do [ -d "$p/app" ] && (cd "$p" && pwd -P); done | sort -u)
if [ ${#runs[@]} -eq 0 ]; then
  [ ${#cands[@]} -gt 0 ] && die "blind id $ID is listed, but its run holds no app/ folder"
  die "no run with blind id $ID in the roots (${ROOTS[*]:-none}) or the index (${INDEX:-none})"
fi
[ ${#runs[@]} -eq 1 ] || die "blind id $ID matches ${#runs[@]} different runs; ids are never reused, so check the roots and the index"
RUN="${runs[0]}"
TASK=unknown
for t in "${TASKS[@]}"; do case "/$RUN/" in */"$t"/*) TASK="$t" ;; esac; done

envs=()
for f in "$RUN"/*/logs/environment.txt; do
  case "$f" in "$RUN/app/"*) continue ;; esac
  [ -f "$f" ] && envs+=("$f")
done
[ ${#envs[@]} -le 1 ] || die "the run for $ID has ${#envs[@]} log folders with an environment.txt; expected one"
ENVF="${envs[0]:-}"
LOGS="${ENVF:+$(dirname "$ENVF")}"

# ---- 2. Node must be the run's ----------------------------------------------------------------
want=""; [ -n "$ENVF" ] && want="$(awk '/^node:/ { print $2; exit }' "$ENVF")"
have="$(node --version 2>/dev/null || echo none)"
if [ -n "$want" ] && [ "$want" != "$have" ]; then
  die "Node mismatch: the run was made with $want, you have $have.
    nvm install $want && nvm use $want     # then run grade_setup.sh again"
fi

# ---- 3. copy the app out ------------------------------------------------------------------------
mkdir -p "$WORK_BASE" || die "cannot create $WORK_BASE"
WORK_BASE="$(cd "$WORK_BASE" && pwd -P)"
case "$WORK_BASE/" in /mnt/*) die "the work folder $WORK_BASE is under /mnt; use a folder on the Linux filesystem (--work or GRADING_WORK)" ;; esac
WORK="$WORK_BASE/$ID"
[ -e "$WORK" ] && die "$WORK already exists. Every grading starts from a fresh copy; if this one was never graded, remove it (rm -rf '$WORK') and run again"
mkdir -p "$WORK/app" || die "cannot create $WORK"
LOG="$WORK/grade-setup.log"
APP="$WORK/app"
emit "== grade_setup.sh  blind id $ID  ·  task $TASK  ·  card $TASK.rubric.md  ·  $(date '+%F %T') ==" \
     "${C_HEAD}== grade_setup.sh  blind id $ID  ·  task $TASK  ·  card $TASK.rubric.md  ·  $(date '+%F %T') ==${C_OFF}"
section 1/7 "Find the run"
ok "found the run for blind id $ID: task $TASK (use $TASK.rubric.md)"
sum OK "run found: task $TASK"
section 2/7 "Node is the run's"
if [ -n "$want" ]; then
  ok "Node $have, the same as the run"; sum OK "Node $have, as the run"
else
  warn "the run records no Node version; using $have"; sum WARN "the run records no Node version"
fi
section 3/7 "Fresh copy of the app"
if ! tar -C "$RUN/app" --exclude=node_modules --exclude=.git -cf - . | tar -C "$APP" -xf -; then
  die "copying the app failed"
fi
ok "copied the app to $APP (without node_modules and .git)"
sum OK "fresh copy made"

# ---- 4. remove the database the app shipped with ---------------------------------------------
section 4/7 "Remove the database the app shipped with"
dbout="$(mktemp)"
python3 - "$APP" > "$dbout" 2>&1 <<'PY'
import os, re, shutil, sys
app = os.path.realpath(sys.argv[1])
PRUNE = {"node_modules", ".git"}
CODE = (".js", ".mjs", ".cjs", ".ts", ".mts", ".cts", ".jsx", ".tsx")

def size(path):
    total = 0
    for d, _, files in os.walk(path):
        for f in files:
            try:
                total += os.lstat(os.path.join(d, f)).st_size
            except OSError:
                pass
    return total

found, calls = [], []
for d, dirs, files in os.walk(app):
    dirs[:] = sorted(x for x in dirs if x not in PRUNE)
    if "PG_VERSION" in files:
        found.append(d)
        dirs[:] = []                       # the data folder's own base/<n>/PG_VERSION are inside it
        continue
    for f in sorted(files):
        if f.endswith(CODE):
            p = os.path.join(d, f)
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    for n, line in enumerate(fh, 1):
                        if re.search(r"new\s+PGlite\s*\(|PGlite\.create\s*\(", line):
                            calls.append(f"{os.path.relpath(p, app)}:{n}: {line.strip()[:160]}")
            except OSError:
                pass

rel = lambda p: os.path.relpath(p, app)
print("INFO\tthe code calls PGlite at:" if calls else "INFO\tno new PGlite(...) or PGlite.create(...) found in the app's code")
for c in calls[:12]:
    print("CALL\t  " + c)
if len(calls) > 12:
    print(f"CALL\t  ... and {len(calls) - 12} more")
if not found:
    print("OK\tno PGlite data folder shipped with the app: nothing to remove")
for d in found:
    if d == app:
        print("WARN\tthe app folder itself holds PG_VERSION; nothing removed. Note this.")
        continue
    kb = size(d) / 1024
    shutil.rmtree(d)
    print(f"OK\tremoved the shipped database folder {rel(d)}/  ({kb:,.0f} KB)")
    parent = os.path.dirname(d)
    while parent != app and parent.startswith(app + os.sep) and not os.listdir(parent):
        os.rmdir(parent)
        print(f"OK\tremoved the folder it left empty: {rel(parent)}/")
        parent = os.path.dirname(parent)
PY
dbrc=$?
dbwarn=0
while IFS=$'\t' read -r t text; do
  case "$t" in
    OK) ok "$text" ;; INFO) info "$text" ;; WARN) warn "$text"; dbwarn=1 ;; *) say "$text" ;;
  esac
done < "$dbout"
rm -f "$dbout"
[ "$dbrc" -eq 0 ] || die "removing the shipped database failed"
if [ "$dbwarn" -eq 1 ]; then sum WARN "shipped database: see the warning above"
elif grep -q "removed the shipped database" "$LOG"; then sum OK "shipped database removed"
else sum OK "no shipped database to remove"; fi

# ---- 5. install, in every folder with a package.json ------------------------------------------
# Plan from the copy as the run left it, before any install script can add files.
mapfile -t PLAN < <(python3 - "$APP" <<'PY'
import glob, json, os, sys
app = os.path.realpath(sys.argv[1])
PRUNE = {"node_modules", ".git"}
folders = []
for d, dirs, files in os.walk(app):
    dirs[:] = sorted(x for x in dirs if x not in PRUNE)
    if "package.json" in files:
        folders.append(os.path.relpath(d, app))
member_of = {}
for f in folders:
    try:
        with open(os.path.join(app, f, "package.json"), encoding="utf-8") as fh:
            ws = json.load(fh).get("workspaces")
    except (OSError, ValueError, AttributeError):
        continue
    if isinstance(ws, dict):
        ws = ws.get("packages")
    if not isinstance(ws, list):
        continue
    for pat in ws:
        if not isinstance(pat, str) or pat.startswith("!"):
            continue
        for m in glob.glob(os.path.join(app, f, pat), recursive=True):
            r = os.path.relpath(os.path.realpath(m), app)
            if r in folders and r != f:
                member_of.setdefault(r, f)
folders.sort(key=lambda r: (0 if r == "." else r.count(os.sep) + 1, r))
for f in folders:
    print(f"{f}\t{member_of.get(f, '')}")
PY
)

lockname() { if [ "$1" = . ]; then echo grading-lock.json; else echo "grading-lock.${1//\//__}.json"; fi; }

FOLDERS=(); SRC=(); need_before=0
section 5/7 "Install the dependencies (this decides L0)"
if [ ${#PLAN[@]} -eq 0 ]; then
  warn "no package.json anywhere in the app: nothing to install"
fi
for line in "${PLAN[@]}"; do
  rel="${line%%$'\t'*}"; ws="${line#*$'\t'}"
  if [ -n "$ws" ]; then
    info "$rel/ is a workspace member of $ws/, installed with it"
    continue
  fi
  FOLDERS+=("$rel")
  if [ -f "$APP/$rel/package-lock.json" ] || [ -f "$APP/$rel/npm-shrinkwrap.json" ]; then
    SRC+=(run)
  elif [ -n "$LOGS" ] && [ -f "$LOGS/$(lockname "$rel")" ]; then
    cp "$LOGS/$(lockname "$rel")" "$APP/$rel/package-lock.json" || die "cannot copy the grading lockfile for $rel"
    SRC+=(grading)
  else
    SRC+=(none); need_before=1
  fi
done

# npm's `before` date decides what a lockfile-less install resolves to: it must be the run's.
run_before=""; [ -n "$ENVF" ] && run_before="$(awk -F': ' '/^npm_before:/ { sub(/^npm_before: */, ""); sub(/ *#.*/, ""); print; exit }' "$ENVF")"
my_before="$(npm config get before 2>/dev/null)"
same_before="$(node -e '
  const t = s => (!s || s === "null" || s === "unset" || s === "undefined") ? null : Date.parse(s.replace(/\s*\(.*\)\s*$/, ""));
  const a = t(process.argv[1]), b = t(process.argv[2]);
  console.log(a === null && b === null ? "yes" : (a !== null && b !== null && a === b ? "yes" : "no"));
' "$run_before" "$my_before")"
if [ "$same_before" != yes ]; then
  if [ "$need_before" -eq 1 ]; then
    rm -rf "$WORK"
    LOG=""
    die "npm's before date differs from the run's (run: ${run_before:-not recorded}; yours: ${my_before:-none: npm config get before printed nothing}), and this app needs an install without a lockfile.
    Set the study's date (npm config set before <the date>) and run grade_setup.sh again."
  fi
  info "npm's before date ($my_before) differs from the run's; every folder installs from a lockfile, so it has no effect"
fi

if [ ${#FOLDERS[@]} -gt 0 ]; then
  fl=""; for f in "${FOLDERS[@]}"; do fl="$fl ${f}/,"; done
  info "folders with their own package.json:${fl%,}. This script installs each of them itself, one after another, below (spec task 1.4: \"its package.json files\"): you never run npm install in them, and an install script of the app's own is not relied on to do it."
fi
RESULTS=(); fail=0
declare -A WHY NOTE   # per failed folder: what stopped it, and a note ready for L0
for i in "${!FOLDERS[@]}"; do
  rel="${FOLDERS[$i]}"; src="${SRC[$i]}"
  case "$src" in
    run)     cmd=(npm ci --no-audit --no-fund);      why="from the run's own lockfile" ;;
    grading) cmd=(npm ci --no-audit --no-fund);      why="from the lockfile an earlier grading saved" ;;
    *)       cmd=(npm install --no-audit --no-fund); why="no lockfile: resolved by npm's before date" ;;
  esac
  emit "" ""
  emit "  -- folder $rel/: ${cmd[*]}   ($why)" "  ${C_HEAD}-- folder $rel/${C_OFF}: ${cmd[*]}   ${C_DIM}($why)${C_OFF}"
  out="$(mktemp)"
  (cd "$APP/$rel" && NPM_CONFIG_UPDATE_NOTIFIER=false "${cmd[@]}") 2>&1 | tee "$out" | while IFS= read -r l; do
    case "$l" in
      "npm error"*|"npm ERR"*) emit "       | $l" "       ${C_DIM}|${C_OFF} ${C_FAIL}$l${C_OFF}" ;;
      "npm warn"*|"npm WARN"*) emit "       | $l" "       ${C_DIM}|${C_OFF} ${C_WARN}$l${C_OFF}" ;;
      "") ;;
      *) emit "       | $l" "       ${C_DIM}| $l${C_OFF}" ;;
    esac
  done
  rc="${PIPESTATUS[0]}"
  if [ "$rc" -eq 0 ]; then
    RESULTS+=("$rel: ok")
    nwarn="$(grep -c -i '^npm warn' "$out")"; wtxt=""
    [ "${nwarn:-0}" -gt 0 ] && wtxt=" ($nwarn npm warnings, which do not count)"
    ok "$rel/: installed without an error$wtxt"
    if [ "$src" = none ]; then
      if [ -n "$LOGS" ] && cp "$APP/$rel/package-lock.json" "$LOGS/$(lockname "$rel")" 2>/dev/null; then
        ok "saved this install's lockfile for later gradings ($(lockname "$rel") in the run's log folder)"
      else
        warn "could not save this install's lockfile beside the run; a later grading will install afresh. Note this."
      fi
    fi
  else
    fail=1
    # The line that says what went wrong: the shell's own message for a failed script, otherwise
    # npm's first error line after its code.
    errline="$(grep -v -e '^npm ' -e '^> ' -e '^[[:space:]]*$' "$out" | grep -i -E "error|can't|cannot|not found|no such|denied|failed" | tail -1)"
    [ -n "$errline" ] || errline="$(grep '^npm error' "$out" | grep -v -E '^npm error (code|path|command|A complete log|errno|syscall)' | head -1 | sed 's/^npm error //')"
    errline="${errline:0:220}"
    if grep -q -e "allow-scripts is not allowed in project-scoped installs" -e EALLOWSCRIPTS "$out"; then
      # Grader-side (README, "Grader-side problems"): an npm inside the app's own script refused
      # the allow-scripts setting it inherited from your npm configuration. Not the app's fault.
      rm -rf "$WORK"; LOG=""
      die "grader-side problem in ${rel}/: your npm configuration sets allow-scripts, which an npm run by the app's own script refuses (EALLOWSCRIPTS). This is not the app's fault and decides nothing.
    Remove the setting (README, \"Grader-side problems\": npm config delete allow-scripts --location=user, or delete the line from ~/.npmrc), then run grade_setup.sh $ID again."
    elif grep -q ERESOLVE "$out"; then
      WHY[$rel]="a dependency conflict npm refuses (ERESOLVE)"
      NOTE[$rel]="A0: ${rel}/ install stopped on ERESOLVE (a dependency conflict npm refuses); re-ran with npm install --legacy-peer-deps."
      RESULTS+=("$rel: FAILED (exit $rc, ERESOLVE). A0, for the rest of the card: (cd '$APP/$rel' && ${A0X}npm install --legacy-peer-deps)${A0SFX}")
    elif grep -q "EUSAGE" "$out" && grep -q "are in sync" "$out"; then
      WHY[$rel]="the lockfile does not match package.json (EUSAGE)"
      NOTE[$rel]="A0: npm ci in ${rel}/ stopped on EUSAGE (the lockfile does not match package.json); re-ran with npm install."
      RESULTS+=("$rel: FAILED (exit $rc, EUSAGE: the lockfile does not match package.json). A0, for the rest of the card: (cd '$APP/$rel' && ${A0X}npm install)${A0SFX}")
    elif grep -q "ETARGET" "$out"; then
      # A version of a package that exists, but none published before the `before` date matches
      # the range asked for. A0 only for a dependency the app's own package.json declares.
      spec="$(grep -o -m1 'No matching version found for [^ ]*' "$out" | sed 's/^No matching version found for //')"
      pkg="${spec%@*}"
      where="$(cd "$APP/$rel" && node -e '
        const fs = require("fs"), path = require("path"), n = process.argv[1];
        const has = f => { try { const j = JSON.parse(fs.readFileSync(f, "utf8"));
          return ["dependencies", "devDependencies", "optionalDependencies"].some(s => j[s] && Object.prototype.hasOwnProperty.call(j[s], n)); } catch (e) { return false; } };
        if (has("package.json")) { console.log("."); process.exit(0); }
        const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) {
          if (!e.isDirectory() || e.name === "node_modules" || e.name.startsWith(".")) continue;
          const sub = path.join(d, e.name);
          if (has(path.join(sub, "package.json"))) { console.log(sub); process.exit(0); }
          walk(sub); } };
        walk(".");' "$pkg" 2>/dev/null)"
      WHY[$rel]="no published version matches ${spec:-a declared dependency} (ETARGET)"
      NOTE[$rel]="A0 ETARGET: in ${rel}/ no version published before the before date matches $spec; re-ran with npm install --no-save $pkg@latest."
      if [ -z "$pkg" ] || [ -z "$where" ]; then
        NOTE[$rel]="${rel}/: install stopped on ETARGET ($spec), a package no package.json of the app declares. No A0: L0 and every later item fail."
        RESULTS+=("$rel: FAILED (exit $rc, ETARGET: ${spec:-a version that does not exist}, which no package.json of the app declares; no A0)")
      elif [ "$where" = "." ]; then
        RESULTS+=("$rel: FAILED (exit $rc, ETARGET: no published version matches $spec). A0, for the rest of the card: (cd '$APP/$rel' && ${A0X}npm install --no-save '$pkg@latest')${A0SFX}. If that stops on ETARGET for another package, add it to the same command: npm install --no-save '$pkg@latest' '<that package>@latest'")
      else
        RESULTS+=("$rel: FAILED (exit $rc, ETARGET: no published version matches $spec, declared by the workspace member $where). A0, for the rest of the card: (cd '$APP/$rel' && ${A0X}npm install --no-save -w '$where' '$pkg@latest')${A0SFX}. If that stops on ETARGET for another package, add it to the same command")
      fi
    elif life="$(cd "$APP/$rel" && node -e '
        // Did the install stop in a lifecycle script of the package.json in this folder?
        const fs = require("fs"), out = fs.readFileSync(process.argv[1], "utf8");
        let s = {}; try { s = JSON.parse(fs.readFileSync("package.json", "utf8")).scripts || {}; } catch (e) {}
        for (const k of ["preinstall", "install", "postinstall", "prepare"])
          if (typeof s[k] === "string" && out.includes("npm error command sh -c " + s[k])) { console.log(k + "\t" + s[k]); process.exit(0); }
        process.exit(1);' "$out" 2>/dev/null)"; then
      # The app's own install script failed (README, "Before each app"): A0 re-runs the same
      # install without the folder's lifecycle scripts; its dependencies are still installed.
      script="${life#*$'\t'}"; life="${life%%$'\t'*}"
      others=""; for f in "${FOLDERS[@]}"; do [ "$f" = "$rel" ] || others="$others ${f}/,"; done; others="${others%,}"
      WHY[$rel]="the app's own \"$life\" script failed${errline:+: $errline}"
      NOTE[$rel]="A0: in ${rel}/ the app's own \"$life\" script ($script) failed${errline:+: $errline}; re-ran the install with --ignore-scripts.${others:+ The other folders (${others# }) are installed on their own by grade_setup.sh.}"
      RESULTS+=("$rel: FAILED (exit $rc, the app's own \"$life\" script failed). A0, for the rest of the card: (cd '$APP/$rel' && ${A0X}${cmd[*]} --ignore-scripts)${A0SFX}")
    else
      code="$(grep -o -m1 'npm error code [A-Za-z0-9_]*' "$out" | sed 's/^npm error code //')"
      WHY[$rel]="${code:+$code: }${errline:-see the npm output above}"
      NOTE[$rel]="${rel}/: install stopped (${code:-exit $rc})${errline:+: $errline}. No A0: L0 and every later item fail."
      RESULTS+=("$rel: FAILED (exit $rc${code:+, $code}). No A0 for this error: L0 fails, and so does every item after it (README, \"Before each app\")")
    fi
    # Show it now: what failed, and the A0 command if there is one.
    r="${RESULTS[${#RESULTS[@]}-1]}"
    case "$r" in
      *"A0, for the rest of the card: "*)
        r0="${r%%. A0, for the rest of the card: *}"
        bad "${r0/: FAILED (/\/: install stopped (}. L0 fails; A0 lets the rest of the card be graded"
        a0="${r#*A0, for the rest of the card: }"; a0tip=""
        case "$a0" in *". If that stops"*) a0tip="If that${a0#*. If that}"; a0="${a0%%. If that stops*}" ;; esac
        a0="${a0//\/app\/.\'/\/app\'}"
        info "why: ${WHY[$rel]}"
        case "${WHY[$rel]}" in *"own \""*"\" script failed"*)
          info "the A0 below installs ${rel}/'s own dependencies only, without its scripts. ${others:+The other folders (${others# }) are installed on their own by this script: see their results below.}" ;; esac
        todo "A0: run this whole line:"
        emit "         $a0" "         ${C_DO}$a0${C_OFF}"
        [ -z "$a0tip" ] || info "$a0tip"
        info "for L0's notes: ${NOTE[$rel]}" ;;
      *) bad "${r/: FAILED (/\/: install stopped (}"
         info "why: ${WHY[$rel]}"
         info "for L0's notes: ${NOTE[$rel]}" ;;
    esac
  fi
  rm -f "$out"
done

# ---- 6. the grader's environment ---------------------------------------------------------------
# The browsers run on Windows (README, "Browser"), where this script cannot see them: only
# GRADER_BROWSER records them.
browser="${GRADER_BROWSER:-}"
{
  echo "blind_id: $ID"
  echo "task: $TASK"
  echo "set_up_at: $(date -Is)"
  echo "grader: ${GRADER:-$(whoami)}"
  echo "node: $(node --version)"
  echo "npm: $(npm --version)"
  echo "npm_before: $my_before"
  for i in "${!FOLDERS[@]}"; do
    rel="${FOLDERS[$i]}"
    h="$(sha256sum "$APP/$rel/package-lock.json" 2>/dev/null | cut -c1-16)"
    echo "lockfile_sha256[$rel]: ${h:-none}"
  done
  echo "os: $(uname -srm)"
  echo "browser: ${browser:-not recorded (set GRADER_BROWSER, for example 'A: Firefox 143.0; B, C: Edge 141.0')}"
} > "$WORK/GRADER-ENV.txt"
[ -n "$SAVE" ] && cp "$WORK/GRADER-ENV.txt" "$SAVE/"
# The install's verdict for the summary.
nok=0; noa0=0; for r in "${RESULTS[@]}"; do case "$r" in *": ok") nok=$((nok+1)) ;; esac; done
# One line per folder, so the summary shows what was installed where.
perf=""
for r in "${RESULTS[@]}"; do
  f="${r%%:*}"
  case "$r" in
    *": ok") perf="$perf · ${f}/ installed" ;;
    *"A0, for the rest"*) perf="$perf · ${f}/ FAILED (A0 below)" ;;
    *) perf="$perf · ${f}/ FAILED (no A0)" ;;
  esac
done
if [ ${#RESULTS[@]} -eq 0 ]; then
  sum WARN "install: nothing to install"
elif [ "$fail" -eq 0 ]; then
  sum OK "install: all ${#RESULTS[@]} folder(s) installed without an error  ->  L0 passes"
else
  noa0=0; for r in "${RESULTS[@]}"; do case "$r" in *FAILED*) case "$r" in *"A0, for the rest"*) ;; *) noa0=1 ;; esac ;; esac; done
  if [ "$noa0" -eq 1 ]; then
    sum FAIL "install: $nok of ${#RESULTS[@]} folder(s) installed; an error with no A0  ->  L0 fails, and so does every item after it"
  else
    sum FAIL "install: $nok of ${#RESULTS[@]} folder(s) installed  ->  L0 fails; run the A0 command(s) below, then grade the rest"
  fi
fi
[ -z "$perf" ] || sum INFO "each folder installed by this script on its own:${perf# ·}"

# ---- 6. launch pre-check (read only; decides nothing) ------------------------------------------
section 6/7 "Launch pre-check (decides nothing: run the declared command as usual)"
lc_top=""; for rel in "${FOLDERS[@]}"; do lc_top="$rel"; break; done
if [ -z "$lc_top" ]; then
  info "no package.json, so no launch to check"
elif [ "$fail" -ne 0 ]; then
  info "skipped until the install is complete; after any A0, run: node \$R/launch_check.js '$APP/$lc_top' '$APP'"
  sum INFO "launch pre-check skipped (install incomplete); after A0: node \$R/launch_check.js '$APP/$lc_top' '$APP'"
else
  lc_n=0
  while IFS=$'\t' read -r lc_t lc_text; do
    case "$lc_t" in
      WARN) warn "$lc_text"; lc_n=$((lc_n+1)) ;;
      INFO) info "$lc_text" ;;
    esac
  done < <(NPM_GLOBAL_BIN="$(npm prefix -g 2>/dev/null)/bin" node "$SCRIPT_DIR/launch_check.js" "$APP/$lc_top" "$APP" 2>&1)
  if [ "$lc_n" -eq 0 ]; then
    ok "nothing found that would stop npm run dev"
    sum OK "launch pre-check: nothing found that would stop npm run dev"
  else
    say "Run npm run dev all the same: L1 and L2 are judged on what it does. If it stops as"
    say "warned, try the accommodations in order (README, \"Accommodations\")."
    sum WARN "launch pre-check: $lc_n problem(s) that may stop npm run dev (see Warnings); run it all the same"
  fi
fi

section 7/7 "Records"
ok "grader environment -> $WORK/GRADER-ENV.txt"
[ -n "$browser" ] || warn "no browser version recorded: set GRADER_BROWSER (for example 'A: Firefox 143.0; B, C: Edge 141.0')"

# ---- records, then the summary --------------------------------------------------------------
top=""
for rel in "${FOLDERS[@]}"; do top="$rel"; break; done
ok "this log -> $LOG"
if [ -n "$SAVE" ]; then
  ok "both kept with your results -> $SAVE (an A0 command writes its output there too, as a0.log)"
else
  warn "GRADING_RESULTS is not set, so this log is kept only in the scratch copy"
fi
nextdir="$APP"; [ -n "$top" ] && [ "$top" != . ] && nextdir="$APP/$top"
printf '%s\t%s\n' "$ID" "$nextdir" > "$LAST" 2>/dev/null || true
if [ -n "${GRADING_RESULTS:-}" ] && [ "$TASK" != unknown ]; then
  if sheet="$(python3 "$SCRIPT_DIR/score_sheet.py" new "$TASK" "$ID" --dir "$GRADING_RESULTS" 2>&1)"; then
    ok "blank score sheet -> $sheet"; sum OK "blank score sheet made"
  else
    case "$sheet" in
      *"already exists"*) info "a score sheet for $ID already exists, so none was made; it is kept as it is"
                          sum OK "score sheet already exists (kept)" ;;
      *) warn "no score sheet made: $sheet"; sum WARN "no score sheet made" ;;
    esac
  fi
else
  warn "no score sheet made (set GRADING_RESULTS to your results folder; or: score_sheet.py new $TASK $ID)"
  sum WARN "no score sheet made"
fi

emit "" ""
emit "== SUMMARY  blind id $ID  ·  $TASK ==" "${C_HEAD}== SUMMARY  blind id $ID  ·  $TASK ==${C_OFF}"
for line in "${SUMMARY[@]}"; do
  t="${line%%|*}"; text="${line#*|}"
  case "$t" in
    OK) ok "$text" ;; FAIL) tag "$C_FAIL" "FAIL" "$text" ;; INFO) tag "$C_INFO" "INFO" "$text" ;; *) tag "$C_WARN" "WARN" "$text" ;;
  esac
done
if [ ${#WARNS[@]} -gt 0 ]; then
  emit "" ""; emit "  Warnings (say in the notes if they bear on a score):" "  ${C_WARN}Warnings${C_OFF} (say in the notes if they bear on a score):"
  for w in "${WARNS[@]}"; do emit "    - $w"; done
fi
if [ "$noa0" -eq 1 ]; then
  emit "" ""; emit "  What to do:" "  ${C_DO}What to do:${C_OFF}"
  for r in "${RESULTS[@]}"; do
    case "$r" in *FAILED*) case "$r" in *"A0, for the rest"*) ;; *)
      f="${r%%:*}"; emit "    - ${f}/: ${WHY[$f]}"
      emit "      L0 notes: ${NOTE[$f]}" "      ${C_DIM}L0 notes:${C_OFF} ${NOTE[$f]}" ;; esac ;; esac
  done
  emit "    No A0 covers that error, so no launch is needed (an A0 elsewhere would not change it):"
  emit "    1. fill the sheet: L0 and every later item fail; L0's notes name the error(s) above"
  emit "    2. python3 \$R/api_probe.py $TASK 0 $ID --no-backend --out \"\$GRADING_RESULTS/probe\""
  emit "    3. python3 \$R/score_sheet.py check \"\$GRADING_RESULTS/$ID.score.json\", then the next id"
  [ "$fail" -eq 0 ] || exit 3
fi
if [ ${#RESULTS[@]} -gt 0 ] && [ "$fail" -ne 0 ]; then
  emit "" ""; emit "  To do before the launch:" "  ${C_DO}To do before the launch:${C_OFF}"
  for r in "${RESULTS[@]}"; do
    case "$r" in
      *"A0, for the rest of the card: "*) a0="${r#*A0, for the rest of the card: }"
        a0="${a0%%. If that stops*}"; a0="${a0//\/app\/.\'/\/app\'}"; f="${r%%:*}"
        emit "    - ${f}/: ${WHY[$f]}"
        emit "      A0 (run this whole line):  $a0" "      ${C_DO}A0${C_OFF} (run this whole line):  ${C_DO}$a0${C_OFF}"
        emit "      L0 notes (L0 still fails):  ${NOTE[$f]}" "      ${C_DIM}L0 notes${C_OFF} (L0 still fails):  ${NOTE[$f]}" ;;
      *FAILED*) emit "    - ${r%%:*}/: no A0. Score L0 and every later item fail (README, \"Before each app\"); run the probe with --no-backend" ;;
    esac
  done
fi
emit "" ""; emit "  Next:" "  ${C_HEAD}Next:${C_OFF}"
emit "    1. ss -ltnp                      # nothing may listen on the app's ports"
if [ -n "$top" ]; then
  if [ "$top" = . ]; then
    emit "    2. cd '$nextdir' && npm run dev   # the declared command, at the project root"
  else
    emit "    2. cd '$nextdir' && npm run dev   # the top folder has no package.json; check from the app (and its README) that $top/ is the project root"
  fi
  emit "       the project root's scripts:" "       ${C_DIM}the project root's scripts:${C_OFF}"
  (cd "$APP/$top" && node -e '
    const p = require("./package.json"), s = p.scripts || {};
    const k = Object.keys(s);
    if (!k.length) console.log("it has no scripts");
    for (const n of k) console.log("npm run " + n + "   # " + s[n]);
    if (!("dev" in s)) console.log("no dev script here (README, \"No root dev script\")");
  ' 2>&1) | while IFS= read -r l; do emit "         $l" "         ${C_DIM}$l${C_OFF}"; done
fi
[ "$fail" -eq 0 ] || exit 3
exit 0
