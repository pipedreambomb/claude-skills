#!/usr/bin/env python3
"""Stop hook: refuse to end a turn in which the quest ledger was never consulted.

Written 2026-08-26, after the user pointed out the tracker was "permanently
stale". It was: the ledger had gone 35 minutes and six substantial turns without
a write, while the injected rules said RECONCILE EVERY TURN in capitals.

The rules were not the problem. Enforcement was. The TL;DR rule works because a
Stop hook blocks the turn; the quest rule was a paragraph inside a
UserPromptSubmit injection, which costs exactly nothing to skip. A model that
means to reconcile and doesn't gets no signal, so the ledger decays silently --
and a silently decaying tracker is worse than none, because the user cannot tell
stale from settled.

The bar is deliberately low: running `quest` AT ALL counts, `quest list`
included. The requirement is that the question was asked, not that something was
written. Most turns genuinely change nothing, and forcing a write would inflate
the ledger instead of keeping it honest.
"""
import json, os, re, sys

# `quest list`, `bin/quest done q1`, `~/.claude/.../quest add -t "..."`.
# The haystack is the tool input serialised as JSON, so a command at the very
# start of its field is preceded by a quote, not whitespace -- leave that out of
# the prefix class and `{"command": "quest done q1"}` silently fails to match,
# which is a hook that never fires on exactly the calls it is watching for.
QUEST = re.compile(r"""(?:^|[\s;&|(`"'=])(?:[\w./~-]*/)?quest(?:\s|$|\\)""")
# Below this, with no tool calls at all, the turn was an aside -- an
# acknowledgement or a one-line answer. Blocking those is pure friction.
CHATTER_WORDS = 30
TAIL_BYTES = 2_000_000


def turn_events(path):
    """Events since the last real user message, oldest first.

    A user entry carrying only tool_result blocks is the harness returning
    output mid-turn, not the user speaking, so it does not bound the turn.
    """
    with open(path, "rb") as f:
        f.seek(0, 2)
        f.seek(-min(f.tell(), TAIL_BYTES), 2)
        lines = f.read().decode("utf-8", "replace").splitlines()

    out = []
    for line in reversed(lines):
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("isSidechain") or ev.get("isMeta"):
            continue
        if ev.get("type") == "user":
            content = ev.get("message", {}).get("content")
            blocks = content if isinstance(content, list) else []
            if not any(isinstance(b, dict) and b.get("type") == "tool_result"
                       for b in blocks):
                break
        out.append(ev)
    out.reverse()
    return out


def scan(events):
    """(quest was invoked, any tool ran, words of assistant prose)."""
    saw_quest = tools = False
    words = 0
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for b in ev.get("message", {}).get("content") or []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text":
                words += len(b.get("text", "").split())
            elif b.get("type") == "tool_use":
                tools = True
                blob = json.dumps(b.get("input") or {})
                if QUEST.search(blob):
                    saw_quest = True
    return saw_quest, tools, words


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return
    if ev.get("stop_hook_active"):
        return

    path = ev.get("transcript_path")
    if not path or not os.path.exists(path):
        return
    try:
        events = turn_events(path)
    except Exception:
        return
    if not events:
        return

    saw_quest, tools, words = scan(events)
    if saw_quest:
        return
    if not tools and words < CHATTER_WORDS:
        return

    print(json.dumps({"decision": "block", "reason": (
        "You did not touch the quest ledger this turn. Run `quest list` now and "
        "reconcile it against what just happened: close what finished (`quest "
        "done <id>`), drop what became pointless, mark what the user picked up "
        "(`quest live <id>`), reset the title if the job changed (`quest quest "
        '"<title>"`), and add at most two genuinely open loops. Then reply with '
        "ONLY the TL;DR and the tracker -- do not redo the work, re-explain, or "
        "apologise. If nothing changed, `quest list` alone satisfies this."
    )}))


main()
