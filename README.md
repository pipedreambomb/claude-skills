# Claude Code skills

A small marketplace of two Claude Code plugins, built for working in bursts and
switching contexts on purpose — rather than for pretending you don't.

## Install

```
/plugin marketplace add pipedreambomb/claude-skills
/plugin install quest-tracker
/plugin install phone
```

## quest-tracker

An always-visible tracker of what you're actually doing, in a tmux pane beside your
session. Three zones, and which one a thing lands in is the whole point:

- **quest steps** — the current job isn't done until these are
- **tangents** — real and wanted, but the job completes without them
- **background** — work genuinely running without you: subagents, long jobs

The assistant parks open loops as you create them, without being asked and without
breaking its train of thought, so the question you raised and moved on from is still
there when you come back. Entries are addressed the way the pane labels them — `q1`,
`q2.1`, `t1`, `b1` — and every command echoes the entry it touched so a mistake is
visible immediately.

```
quest add "the next step"          quest add -t "a tangent"
quest live q2                      quest done q2
quest tang q3                      quest num q3 2.1
```

The pane is a live view of a plain TSV ledger. A `SessionStart` hook opens the pane; a
`UserPromptSubmit` hook injects the current state into context, so the assistant is
working from the same list you're looking at.

Includes `/quests`, `/recap`, `/tangent` and `/signoff`.

**Requires tmux** for the pane. The context injection works without it.

## phone

Detects when you're driving a session from your phone over Remote Control, and changes
how the assistant replies: everything in the reply text (the phone client shows only
what follows the last tool call), the tracker carried inline since the panes are
invisible, replies kept short, and the tmux pane parked so it stops eating the width
your reply gets.

It switches itself on and off. Detection is local keystroke recency in tmux, sampled the
moment a prompt lands: typing at the terminal stamps the tmux client, while a prompt
over Remote Control arrives by the messaging socket and never touches it. A machine with
no tmux server — a cloud VM — always reads as remote, which is correct.

Pairs with quest-tracker, which supplies the tracker it carries.

## Design notes

Both plugins share an assumption worth stating: **the user must never have to remember
to turn something off.** Turning things on is the user's job; turning them off is the
assistant's. Every behaviour here ends on its own, and the source comments record the
failures that shaped that — including the detectors that looked right and weren't.

## Licence

MIT
