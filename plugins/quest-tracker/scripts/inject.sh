#!/usr/bin/env bash
# Emitted on stdout -> injected into Claude's context.
set -uo pipefail
BIN="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}/bin"
n="$("$BIN/quest" count 2>/dev/null || echo 0)"
LEDGER="$("$BIN/quest" path 2>/dev/null)"
AGE="$(stat -c %Y "$LEDGER" 2>/dev/null || echo 0)"
echo "<quest-tracker>"
if [ "$n" != "0" ]; then
  echo "The user's pane looks EXACTLY like this (snapshot, revision $AGE):"
  echo
  # The pane itself, colour stripped. Anything else risks handing the model a different
  # numbering from the one on the user's screen, which is how two sessions end up
  # confidently discussing different lists.
  "$BIN/quest" render 64 | sed 's/\x1b\[[0-9;]*m//g'
  echo
else
  echo "Nothing currently tracked."
fi
cat <<'TXT'
Rules for this tracker (it is the user's working memory, treat it as load-bearing):
- Refer to entries the way the pane labels them: q1, q2.1 (quest steps), t1 (tangents), b1
  (background). "#1" is ambiguous — there is a q1 AND a t1 — so never use a bare number, and
  if the user does, ask which zone rather than guessing. Every command takes these labels:
  `quest done q1`, `quest tang q3`, `quest edit t2 "..."`. Raw ledger ids still work but are
  not what the user sees. Each command echoes the text of the entry it acted on: READ IT
  BACK. If it is not what you meant to touch, undo it at once with `quest reopen <id>`.
- THE LIST ABOVE IS A SNAPSHOT, not live. Other sessions share this ledger and edit it while
  you work, and the user's tmux pane always shows the truth. Before closing anything, before
  claiming what step something is, and before telling the user what is open, run `quest list`
  and use THAT. Never argue from the snapshot — if it disagrees with the pane, the pane wins.
- The user may veer between topics on purpose. Do NOT discourage this and do NOT nag about focus.
- Three zones, and which one a thing lands in matters. The test is: does the current quest
  finish without this?
    `quest add "<text>"`     a quest step — the quest is not done until this is.
    `quest add -t "<text>"`  a tangent — real and wanted, but the quest completes without it.
    `quest add -b "<text>"`  background — work actually running without the user, i.e. subagents
                             and long jobs. Nothing else belongs here; closed threads are not
                             background.
  Default to -t when unsure: inflating the main line is what makes the pane untrustworthy.
  Move things later with `quest main|tang|bg <id>`, and number steps with `quest num <id> 2.1`.
- When the user opens a question or idea and then moves on WITHOUT it being answered, silently
  add it. Do not announce it, do not ask permission, do not break your train of thought to
  mention it. The user's own words, one *starred* span marking the phrase that would have been
  the title, up to about seven words, ending in a full stop (grouping headings take no stop).
- Add at most 2 per turn. Only genuinely open loops, not asides you answered in the same reply.
- `quest done <id>` when you answer one — but only when it is actually finished; verify rather
  than assume. `quest drop <id>` when the user says it is irrelevant. `quest live <id>` when
  they pick one up (one live at a time). `quest quest "<title>"` when the whole job changes.
- Never read the tracker back to the user unprompted. It is always on screen in their tmux pane.
  Mentioning it costs them the attention the pane exists to save.
TXT
echo "</quest-tracker>"
