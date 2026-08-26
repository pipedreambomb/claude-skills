#!/usr/bin/env python3
"""Stop hook: require a short TL;DR at the bottom of long responses.

The reader is left at the point the terminal stopped, so a summary at the *bottom*
saves scrolling up and re-scanning; a top-of-message summary is off-screen and
useless for that. The instruction in ~/.claude/CLAUDE.md is what normally puts
it there — this only catches the misses, so it should almost never fire.

Blocks the turn from ending, which sends the model back for one more message.
That extra message is the appended TL;DR, and lands exactly where it's wanted.

Two failure modes, because a bloated TL;DR is its own defeat: missing entirely,
and too long to skim. MAX_WORDS sits above the 40 in CLAUDE.md so the written
rule governs the grace band and the hook only catches real overruns.

Counts prose only: fenced code blocks are skipped, since scanning a code block
is not the problem being solved and its length says nothing about the prose.
"""
import json, os, re, sys

MIN_WORDS = int(os.environ.get("TLDR_MIN_WORDS", "150"))
MAX_WORDS = int(os.environ.get("TLDR_MAX_WORDS", "45"))
FENCE = re.compile(r"```.*?```", re.S)
# Line-anchored, so prose *about* TL;DRs doesn't count as having one. Leading
# markdown (**, >, #, -) is allowed since that is how the real marker is written.
HAS_TLDR = re.compile(r"^[\s>*_#-]*tl\s*;?\s*dr\b", re.I | re.M)
# Background jobs end on one of these, which already is the bottom-line summary.
STATUS_LINE = re.compile(r"^\s*(result|failed|needs input)\s*:", re.I | re.M)
# The quest tracker, when a reply carries one, sits BELOW the TL;DR -- the user
# asked for that on 2026-08-26, because a tracker wedged between the prose and the
# summary splits the response in two. It is a fixed block, not prose the reader has
# to skim, so it counts toward neither the "is this long enough to need a TL;DR"
# test nor the TL;DR's own word cap. Matched on the markers the compact rendering
# always opens with.
TRACKER = re.compile(r"^\s*(?:\*\*⚔|\*tangents\*|\*background\*|---\s*$\n+\s*\*\*⚔)",
                     re.M)


def strip_tracker(text):
    """Everything from the tracker block onward, removed."""
    m = TRACKER.search(text)
    return text[:m.start()] if m else text
TAIL_BYTES = 2_000_000


def last_response(path):
    """Text of the most recent assistant message in the main conversation."""
    with open(path, "rb") as f:
        f.seek(0, 2)
        f.seek(-min(f.tell(), TAIL_BYTES), 2)
        lines = f.read().decode("utf-8", "replace").splitlines()

    for line in reversed(lines):
        if '"assistant"' not in line and '"user"' not in line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        # Subagent and injected entries are not what the user is reading.
        if ev.get("isSidechain") or ev.get("isMeta"):
            continue

        content = ev.get("message", {}).get("content")
        if ev.get("type") == "user":
            # A real user turn bounds the search; tool results do not.
            blocks = content if isinstance(content, list) else []
            if not any(b.get("type") == "tool_result" for b in blocks
                       if isinstance(b, dict)):
                return ""
            continue
        if ev.get("type") != "assistant":
            continue

        if isinstance(content, str):
            return content
        text = "".join(
            b.get("text", "") for b in content or []
            if isinstance(b, dict) and b.get("type") == "text"
        )
        if text.strip():
            return text
    return ""


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return

    # Set once this hook has already blocked; without it the turn never ends.
    if ev.get("stop_hook_active"):
        return

    path = ev.get("transcript_path")
    if not path or not os.path.exists(path):
        return

    try:
        text = last_response(path)
    except Exception:
        return
    if not text:
        return

    # A status line is already the one-line summary. Asking for a TL;DR as well
    # gets the same sentence printed twice, which is what it exists to avoid.
    if STATUS_LINE.search(text):
        return

    # Last marker wins: the TL;DR goes at the bottom, and an earlier heading or
    # aside must not swallow the whole message into the word count.
    found = (list(HAS_TLDR.finditer(text)) or [None])[-1]
    if found:
        tail = strip_tracker(text[found.start():])
        n = len(tail.split())
        if n <= MAX_WORDS:
            return
        return block(
            f"That TL;DR is {n} words against a {MAX_WORDS}-word cap. Reply with "
            "nothing but a tighter one — same conclusion, under the cap. Anything "
            "that won't fit belonged in the body, so drop it rather than compress "
            "it into an unreadable sentence."
        )

    if len(FENCE.sub(" ", strip_tracker(text)).split()) < MIN_WORDS:
        return
    block(
        "That response was long and had no TL;DR. Reply with nothing but a TL;DR "
        f"of it — {MAX_WORDS} words at most, the conclusion and anything needing "
        "a decision. Do not redo the work, re-explain, or apologise for the "
        "omission."
    )


main()
