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
- The user has ADHD and veers between topics on purpose. Do NOT discourage this and do NOT nag about focus.
- THERE MUST ALWAYS BE A QUEST. It is the first thing to get right, before any entry.
  Infer it from what is actually being worked on -- that is nearly always obvious from
  the last few messages -- and set it with `quest quest "<title>"`. Reset it with the
  same command whenever the job changes. Only if you genuinely cannot tell, set
  `quest quest "unknown"`: the user will see that in the pane and say what it is. An
  empty title is never acceptable; a wrong guess is cheap and visible, silence is not.
- Three zones, and which one a thing lands in matters. The FIRST test is engagement:
  a thing is a tangent only while the user is NOT working on it yet. The moment they
  pick it up it is the quest, or a step of it -- move it with `quest main <id>`, or
  reset the quest title if the whole job has changed. Only for things not yet being
  worked on does the second test apply: does the current quest finish without this?
    `quest add "<text>"`     a quest step — the quest is not done until this is.
    `quest add -t "<text>"`  a tangent — real and wanted, but the quest completes without it.
    `quest add -b "<text>"`  background — work actually running without the user, i.e. subagents
                             and long jobs. Nothing else belongs here; closed threads are not
                             background.
  For something not yet being worked on, default to -t when unsure: inflating the main
  line is what makes the pane untrustworthy. But never park what is being worked on right
  now as a tangent -- that is what makes it wrong.
  Move things later with `quest main|tang|bg <id>`, and number steps with `quest num <id> 2.1`.
- When the user opens a question or idea and then moves on WITHOUT it being answered, silently
  add it. Do not announce it, do not ask permission, do not break your train of thought to
  mention it. The user's own words, one *starred* span marking the phrase that would have been
  the title, up to about seven words, ending in a full stop (grouping headings take no stop).
- Add at most 2 per turn. Only genuinely open loops, not asides you answered in the same reply.
- `quest done <id>` when you answer one — but only when it is actually finished; verify rather
  than assume. `quest drop <id>` when the user says it is irrelevant. `quest live <id>` when
  they pick one up (one live at a time). `quest quest "<title>"` when the whole job changes.
- OPEN A STEP WHEN THE WORK STARTS, not when it finishes. `quest add` then `quest
  done` in the same turn is the commonest way this tracker goes dead: the user
  never sees the entry, so an hour of finished work leaves the pane looking
  frozen, which is indistinguishable from the tracker being broken. The moment a
  job is picked up, add it and `quest live` it. Close it on a LATER turn.
- RECONCILE THE TRACKER EVERY TURN, before you reply. Not when you remember, not when
  the user asks -- every turn, as part of answering. Run `quest list`, then ask of what
  just happened: did I finish a step (`quest done`)? Did something become pointless
  (`quest drop`)? Did the user start on something (`quest live`, or `quest main` if it
  was a tangent)? Did the job itself change (`quest quest "<title>"`)? Did a new open
  loop appear (`quest add`)? A tracker that lags the work is worse than none, because
  the user cannot tell stale from settled and has to re-derive it -- which is the exact
  cost it exists to remove. It goes out of date silently, so the check must be
  unconditional.
- Never read the tracker back to the user unprompted. It is always on screen in their tmux pane.
  Mentioning it costs them the attention the pane exists to save.
TXT
echo "</quest-tracker>"
