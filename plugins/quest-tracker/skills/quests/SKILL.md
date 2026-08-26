---
name: quests
description: Work the quest tracker — see what is open, pick one up, close, drop, reword, or move something between the quest line, tangents and background. Use when the user asks what is open, wants to resume something they parked, or invokes /quests.
---

# Work the ledger

The ledger lives in a plain TSV file. Manage it with the `quest` CLI via Bash.

Entries are addressed by the label the pane shows: `q1`, `q2.1` for quest steps, `t1` for
tangents, `b1` for background. A bare `1` is ambiguous — q1 and t1 are different entries —
so never accept one without knowing the zone. Every command echoes the text of what it
touched; check it matches what the user meant before moving on.

| Intent | Command |
|---|---|
| See everything open | `quest list` |
| What the pane's labels mean | `quest labels` |
| Park something new | `quest add "<phrase>"` |
| Start working one | `quest live <id>` |
| It's answered | `quest done <id>` |
| Not interested any more | `quest drop <id>` |
| Reword it | `quest edit <id> "<new phrase>"` |
| Put it back on the pile | `quest reopen <id>` |
| Tidy away closed items | `quest archive` |
| Move it to the main line | `quest main <id>` |
| Move it to tangents | `quest tang <id>` |
| Move it to background | `quest bg <id>` |
| Number a step in the outline | `quest num <id> 2.1` |
| Rename the whole quest | `quest quest "<title>"` |

Several ids at once are fine: `quest done 3 5 6`.

## How to respond

Read `$ARGUMENTS` for intent.

- **Bare `/tangents`** — run `quest list`, then present the open threads as a short
  numbered list. Nothing else. No preamble, no commentary on the volume of work.
- **They name a thread to resume** — mark it `live`, then just start on it. Do not first
  recap the whole ledger.
- **They're closing things out** — mark them and reply with a single line
  (`Closed 2, 5, 7.`). Then stop.
- **The list has got long** — you may offer *once*, in one sentence, to walk it with them
  four at a time and triage. Never push it twice.

## Tone

This list is compensation, not accusation. A long list means the user's head
is generating a lot, which is the point. Never imply they should have fewer open threads,
never use words like "backlog", "overdue", "outstanding", or "still". If something has been
open a long time, that is not a failure and does not need remarking on.
