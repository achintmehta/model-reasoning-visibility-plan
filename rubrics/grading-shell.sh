# grading-shell.sh: source this once per grading session (GRADING-COMMANDS.md, part B):
#
#     source "$R/grading-shell.sh"
#
# It defines a shell function with the script's own name, so you keep typing
#
#     grade_setup.sh <blind id>
#
# and, once the copy is ready, your shell is moved into the app's project root (the folder the
# summary's "Next" step names), so that `npm run dev` cannot start an earlier app by mistake.
# A script cannot change its caller's folder by itself; this function does it for it.
# If grade_setup.sh stops before the copy is ready, your shell stays where it was.

grade_setup.sh() {
  command grade_setup.sh "$@"
  local rc=$? id="" dir="" line="" work="${GRADING_WORK:-$HOME/grading-work}" skip=""
  for a in "$@"; do
    if [ -n "$skip" ]; then [ "$skip" = work ] && work="$a"; skip=""; continue; fi
    case "$a" in --work) skip=work ;; --root|--index) skip=other ;; -*) ;; *) id="$a" ;; esac
  done
  local last="$work/.last-setup"
  if [ "$rc" -eq 0 ] || [ "$rc" -eq 3 ]; then
    line="$(cat "$last" 2>/dev/null)"
    if [ -n "$line" ] && [ "${line%%$'\t'*}" = "$id" ]; then
      dir="${line#*$'\t'}"
      if [ -d "$dir" ] && cd "$dir"; then
        printf '\n  [ OK ] your shell is now in %s (blind id %s)\n' "$PWD" "$id"
      fi
    fi
  fi
  return "$rc"
}
