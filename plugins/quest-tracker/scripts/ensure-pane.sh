#!/usr/bin/env bash
# Split off a narrow right-hand tmux pane running the live ledger, if one
# isn't already running in this window. Silent no-op outside tmux.
set -uo pipefail
[ -z "${TMUX:-}" ] && exit 0
command -v tmux >/dev/null 2>&1 || exit 0
[ "${QUEST_TRACKER_AUTOPANE:-1}" = "0" ] && exit 0

# Only interactive sessions get a pane. `claude -p` and `claude rc` (which spawns an
# inner --print session) run headless: nobody is looking at the pane, and splitting the
# user's window from under them is exactly what they didn't ask for. Walk up the process
# tree to the claude CLI and read its argv rather than trusting a hook field.
is_headless() {
  local pid=$PPID depth=0 exe args
  while [ "$pid" -gt 1 ] && [ "$depth" -lt 12 ]; do
    exe=$(readlink "/proc/$pid/exe" 2>/dev/null)
    args=$(tr '\0' '\n' < "/proc/$pid/cmdline" 2>/dev/null)
    # Only argv belonging to the claude CLI itself counts -- a `-p` further up the tree
    # (a wrapper script, an unrelated pager) says nothing about this session.
    case "$exe$args" in
      *claude*)
        while IFS= read -r arg; do
          case "$arg" in
            --print|-p|rc) return 0 ;;
          esac
        done <<< "$args"
        ;;
    esac
    pid=$(awk '/^PPid:/{print $2}' "/proc/$pid/status" 2>/dev/null)
    [ -n "$pid" ] || break
    depth=$((depth + 1))
  done
  return 1
}
is_headless && exit 0

WIDTH="${QUEST_PANE_WIDTH:-37}"
BIN="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}/bin"

# already open in this window?
if tmux list-panes -F '#{pane_current_command} #{pane_start_command}' 2>/dev/null | grep -qE 'quest-pane|tangent-pane'; then
  exit 0
fi

tmux split-window -h -l "$WIDTH" -d \
  "cd $(printf '%q' "${CLAUDE_PROJECT_DIR:-$PWD}") && CLAUDE_PROJECT_DIR=$(printf '%q' "${CLAUDE_PROJECT_DIR:-$PWD}") $(printf '%q' "$BIN/quest-pane")" 2>/dev/null || true
tmux select-pane -L 2>/dev/null || true
exit 0
