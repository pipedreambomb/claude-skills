---
name: recap
description: Recap where this session was actually going - the overall arc, the half-finished thoughts, and the single best place to pick back up. Use when the user asks "where were we", "what was I doing", "what did we half-finish", or invokes /recap.
---

# Where were we

Produce a short narrative recap. This is different from `/quests`, which is just the list.
Here the user wants the *shape* of the session back.

## Gather

1. `quest list` via Bash — the explicitly parked threads.
2. Re-read the conversation so far for threads that were opened and drifted away from
   without ever being parked.
3. If in a git repo, a quick `git status --short` and `git log --oneline -8` for what
   actually got done.

## Write, in this order and nothing more

**Where we were heading** — two or three sentences on the through-line. Not a list of
topics: the actual thing being pursued underneath them.

**Half-finished** — up to five bullets. For each: the thread, and specifically what state
it stalled in (a question never answered, a decision never made, code written but not run).
The stall state is the useful part; "we discussed X" is not.

**Best place to restart** — exactly one suggestion, with the reason it's the right one
(cheapest to re-enter, or everything else depends on it). One line.

## Rules

- Under 250 words total. If it doesn't fit, cut the half-finished list, not the arc.
- Anything you find in step 2 that isn't already on the ledger, add it with `quest add`
  before you write. That's the whole point of doing this pass.
- Do not moralise about scope, focus, or how much is open.

$ARGUMENTS
