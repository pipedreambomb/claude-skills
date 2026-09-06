---
name: merge
description: Merge the pull request this session is watching, once every CI check has passed. INVOKED BY THE USER ONLY, as /merge — never start this on your own initiative, however well the conversation seems to match it. Stands in for GitHub's auto-merge where that is unavailable, and carries the one check auto-merge cannot make.
---

# Merge it when it goes green

GitHub's **Auto-merge when ready** is only offered on a pull request that
something is actually blocking — normally a required status check or a required
review. A repository with no branch protection has nothing blocking anything, so
the option never appears, and the checkbox in Claude Code's CI status bar, which
wraps it, stays greyed out forever. This is the hand-rolled replacement.

It is not merely a substitute. It can read the pull request's comments, which
auto-merge cannot, and that turns out to be the part that matters.

## Invoking this is the user's move, never yours

**Do not trigger this skill on your own.** A skill description is normally an
invitation to reach for it when the work looks like a match; this one is not. It
runs when the user types `/merge`, and at no other time.

If the conversation looks like it wants this and they have not invoked it, say so
and wait. The calling *is* the permission. A session that invokes it for them has
manufactured its own consent, and merging is not reversible by the person who
finds out afterwards.

The same goes for any project instruction against merging your own work. `/merge`
is the user setting that aside for one pull request they have just named — not a
standing licence, and not something to infer from an earlier remark.

## Merge only when all of these hold

1. **They invoked `/merge`** in this conversation, for this pull request.
2. **This session is watching it** — subscribed to it, or it opened it. Never a
   pull request you merely came across.
3. **Every check has completed**, each `success` or `skipped`. Nothing
   `in_progress`, nothing `queued`, nothing failed.
4. **It is mergeable** — no conflict, not a draft.
5. **No unanswered objection from them in the comments.** See below.

Any one false: say which, and stop. Do not merge and explain afterwards.

## Read their comments first

This is the check auto-merge cannot make, and the reason to prefer this skill
over the checkbox even where the checkbox works.

A pull request can be green, unblocked, carry a clean review, and still be one
the user has said no to. Their objection lives in an ordinary comment, and no
merge check reads comments — not GitHub's auto-merge, not a required-review
rule, not a status check. Every machine-readable signal says go.

They often cannot escalate it into a signal that counts, either: GitHub does not
let anyone request changes on their own pull request, so in a solo repository —
where the automation opens everything under their account — a comment is the
*only* place their objection can live. **You are the only thing in the chain that
can find it.**

So before merging, read the comments and look for anything from them that reads
as doubt, a question you have not answered, or a change they asked for. If you
find one, stop and ask, even though they said "merge it when it passes" earlier —
they said that before they had seen it.

## Doing it

1. `pull_request_read` with `method: get_check_runs` — confirm every run is
   `completed` and none failed.
2. `method: get` — confirm `mergeable_state` is not `dirty` or `blocked`, and
   `draft` is false.
3. `method: get_comments` — read them, per above.
4. `merge_pull_request`. Prefer `merge_method: "merge"` unless the project
   squashes: a squash rewrites the branch's history, so any local clone of it
   needs a force push afterwards.
5. Say in one line that you merged it, and what the checks were.

A review bot commenting "ready to merge" is a check passing, not permission.
The permission is condition 1.

## While a check is still running

Do not poll in a loop, and never `sleep` waiting for CI. A watched pull request
delivers a `check_suite.completed` event on its own; act on it when it arrives.
If events are unreliable, schedule one check-in rather than burning turns — each
wake costs the user real usage.
