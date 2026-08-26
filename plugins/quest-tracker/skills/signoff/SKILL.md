---
name: signoff
description: End-of-session wrap-up. Reconciles the quest tracker against what actually happened, saves durable learnings to memory silently, suggests any skill worth running on this conversation, and ends by pushing the single next action. Use when the user runs /signoff or says they're wrapping up / done for now / signing off.
---

# Signoff

The user runs this as the last thing in a session — a deliberate pause
before they walk away. Three passes, in order, all of them short. Two
of the three produce no visible output at all.

**The tracker pane is the list.** It is on screen permanently, so
signoff does not reprint it, summarise it, or count it. Reprinting is
what made the list feel oppressive rather than useful. Signoff's job
is to leave the pane *true* and to name one next action.

## 1. Reconcile the tracker — silent

Walk the ledger (`tangent list`) against what actually happened this
session and correct it. No narration, no "I closed #3".

- `tangent done <id>` for anything genuinely finished. Verify rather
  than assume — check the file, the commit, the service.
- `tangent add` / `tangent add -t` for loops opened this session and
  never closed. Same rules as always: the user's own words, one
  `*starred*` span, up to about seven words, full stop on leaves.
- `tangent main` / `tangent tang` / `tangent bg` for anything now in
  the wrong zone, and `tangent num` if the outline needs it.
- Update the quest title with `tangent quest` if the work has moved
  on. A stale title is what makes every later triage decision wrong.

Detail that will not fit in seven words goes in the `open-loose-ends`
memory, keyed by ledger id — the ledger is the index, the memory is
the detail. Never let the two disagree.

## 2. Feed learnings back — silent

Look for anything durable that isn't already captured: corrections and
confirmed approaches (`feedback`), decisions and constraints
(`project`/`user`/`reference`). Write or update the files and
`MEMORY.md` yourself.

**Report nothing.** Memories are for future sessions, not for the user
to read at signoff. Mention one only if it changes what the user should
do next.

CLAUDE.md is the exception — it's checked into a repo, so propose the
literal line and let the user decide.

## 3. Offer one skill, if one genuinely fits

Look back over the session for a pattern another skill handles better
than a human remembering to ask. Suggest **at most one**, with the
concrete reason from this conversation — not a menu.

The usual candidate is `/hookify`: if the user corrected the same
behaviour more than once, or something went wrong that a
PreToolUse/PostToolUse hook would have caught, say so and name the
behaviour. Skip this pass entirely when nothing fits; a suggestion
every time trains the user to ignore it.

## 4. Push one thing

End by naming **the single next action** — the item that unblocks the
most, or the cheapest one that has been sitting longest — and offer to
do it now. One item, not a ranked list.

If it is genuinely blocked on the user, say exactly what you need from
them: their decision, their hardware, their hands on a file you cannot
edit.

**No valediction while the tracker has open quest steps.** No "night",
no "speak soon". But do not lecture about the open ones either — the
pane already says how many there are, and the user does
not need the count read aloud. When the quest steps are clear, say so
plainly and sign off.
