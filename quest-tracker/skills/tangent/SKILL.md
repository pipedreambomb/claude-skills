---
name: tangent
description: Park a tangent on the quest tracker without leaving the current topic — or a quest step, when the current quest is not done without it. Use when the user says "park that", "note that down", "before I forget", "remind me to come back to", or invokes /tangent.
---

# Park a tangent

The user has just had a thought they do not want to lose, but they do **not** want to
switch to it now. Your job is to capture it and get out of the way.

## Do this

1. Run, via Bash:
   ```
   quest add -t "<the thought, condensed to a short phrase>"
   ```
   - Pick the zone. `-t` is the default and the right answer nearly always: a tangent is
     something real that the current quest finishes without. Drop the flag only when the
     quest genuinely is not done until this is; use `-b` only for work actually running
     without the user, such as a subagent or a long job.
   - Use the user's own words and vocabulary. Do not translate their phrasing into
     neutral corporate task-speak — they need to recognise it later at a glance.
   - Aim for under 60 characters. It is a memory hook, not a specification.
   - If `$ARGUMENTS` is empty, infer the thread from what they just said. If genuinely
     ambiguous, ask one short question — but prefer guessing and letting them edit.

2. Acknowledge in **one short line at most**, e.g. `Parked #7.` Then immediately carry on
   with whatever you were both doing before. Do not summarise the tangent back to them,
   do not offer to start on it, do not list the other open threads.

## Do not

- Do not derail. The entire value of this command is that using it costs nothing.
- Do not read the ledger back — it is already on screen in their tmux pane.
- Do not editorialise about how many threads are open.

$ARGUMENTS
