#!/usr/bin/env bash
# Emitted on stdout -> injected into Claude's context.
#
# The Stop hook alone ships enforcement without the rule. That works on the one
# machine where the rule happens to sit in ~/.claude/CLAUDE.md, and nowhere else:
# a cloud session gets the plugin without the dotfiles, so the hook arrives as a
# blocker with no spec. The model then reverse-engineers the convention from
# rejection messages — badly, because those messages state the word cap and not
# the placement, which is the half that matters.
#
# So the rule travels with the hook, the way quest-tracker's does. Its own
# docstring says it "should almost never fire"; that is only true if something
# says this first.
set -uo pipefail
cat <<'TXT'
<tldr>
End any response over ~100 words with a **TL;DR** — **40 words maximum**, one or two
sentences carrying the conclusion and anything awaiting a decision. Not a description
of what you did ("I investigated the hook"), but the finding itself ("no colour setting
exists; the only lever is terminal-side").

**Bottom, never top.** The terminal leaves the reader sitting at the end of the output,
so a summary there is already on screen; one at the top has scrolled off and saves
nothing. The whole point is to not scroll up and re-scan to recover the gist.

**Put it last.** The hook counts every word from the TL;DR marker to the end of the
message, so anything you add below it — a tracker, a sign-off, a status line — spends
the same budget. A summary at the top is worse still: it charges the entire body to the
count, which reads as a wildly over-long TL;DR and hides the real mistake, which was
the placement.

Caveats, counts and second findings go in the body. A TL;DR that itself needs skimming
has failed at the one job it has — if cutting it to 40 words loses something, that
something was never the headline. Nor should it recycle the body's sentences: state the
conclusion, not a recap of the structure.

**Write exactly one.** Never pair it with a background-job `result:` / `failed:` /
`needs input:` line — that line is already the one-line bottom summary, so printing both
says the same sentence twice in a row. When the job convention calls for a status line,
write only that.

A Stop hook backstops this at 150 words and blocks the turn from ending without one,
costing a round trip and printing the summary twice on screen. Writing it inline is
free, and reads better than one bolted on afterwards.
</tldr>
TXT
