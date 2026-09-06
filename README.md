# Claude Code skills

A small marketplace of Claude Code plugins, built for working in bursts and
switching contexts on purpose — rather than for pretending you don't.

## Install

```
/plugin marketplace add pipedreambomb/claude-skills
/plugin install quest-tracker
/plugin install tldr
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

## phone mode (part of quest-tracker)

Detects when you're driving a session from a phone over Remote Control and changes how
replies are shaped: the tracker rides inline since the pane is invisible, replies stay
short, and the tmux pane is parked so it stops eating the width your reply gets.

It switches itself on and off. Detection is local keystroke recency in tmux, sampled the
moment a prompt lands: typing at the terminal stamps the tmux client, while a prompt over
Remote Control arrives by the messaging socket and never touches it. A machine with no
tmux server — a cloud VM — always reads as remote, which is correct.

It lives inside quest-tracker rather than beside it. The pane and the in-reply tracker are
one feature seen from two ends, and exactly one of them exists at a time; as a separate
plugin, the phone half had to assume the tracker half was installed.

## tldr

A Stop hook that won't let a long reply end without a TL;DR — and insists it goes at the
bottom. A summary at the bottom is already on screen when the reply arrives; one at the
top has scrolled away by the time you read it.

## merge

A `/merge` command for repositories where GitHub's **Auto-merge when ready** is
never offered. Auto-merge only appears on a pull request something is actually
blocking — a required check, a required review — so a repository with no branch
protection has nothing to block anything, and the checkbox in Claude Code's CI
status bar, which wraps it, stays greyed out forever.

It is not just a substitute, because it can do the one thing auto-merge cannot:
**read the pull request's comments before merging.**

A pull request can be green, unblocked, carrying a clean review, and still be one
you have already said no to. Your objection lives in an ordinary comment, and
nothing in the merge path reads comments. Worse, you often cannot escalate it into
something that does — GitHub won't let you request changes on your own pull
request, so in a solo repository where the automation opens everything under your
account, a comment is the only place your objection can live. The assistant is the
only thing in the chain that can find it. This skill makes it look.

The other half is that **you** invoke it. A skill description normally invites the
assistant to reach for it when the work matches; this one says the opposite, in as
many words, because a session that invokes it unasked has manufactured its own
consent — and a merge is not reversible by the person who finds out afterwards.

## Design notes

Both plugins share an assumption worth stating: **the user must never have to remember
to turn something off.** Turning things on is the user's job; turning them off is the
assistant's. Every behaviour here ends on its own, and the source comments record the
failures that shaped that — including the detectors that looked right and weren't.

## Licence

MIT
