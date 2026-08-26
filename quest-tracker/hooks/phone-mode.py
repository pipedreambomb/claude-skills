#!/usr/bin/env python3
"""Turn phone mode on by itself when a prompt arrives from a phone.

Nobody remembers to type /phone. By the time you are on your phone you are away
from the terminal, and the reason you wanted phone mode is that you have already
stopped thinking about it. So it detects the situation instead of asking.

DETECTION. Local keystroke recency, sampled the moment a prompt lands. Submitting
from the terminal means pressing Enter inside tmux, which bumps that client's
#{client_activity}; a prompt arriving over Remote Control enters the process by
its messaging socket and never touches the tmux client, so the stamp stops
advancing. See bin/phone-presence for why the window is minutes, not seconds.

The sample is only valid at prompt-submit time -- seconds later the delta has
grown by however long the model has been working -- so the verdict is cached for
the turn and read from there by anything that needs it afterwards.

A NOTE FOR ANYONE EXTENDING THIS. An earlier version keyed off
CLAUDE_CODE_BRIDGE_SESSION_ID, taking it to mean Remote Control was on. It does
not: that variable is set for every backgrounded conversation, so every background
job concluded it was talking to a phone. If you are tempted by it, don't.

Also parks the quest-tracker tmux pane while the user is remote: Remote Control
mirrors the PTY, so the columns that pane eats come out of the width the reply
gets on a phone screen, and its content rides in the reply instead. Restored the
moment a local keystroke lands, and on SessionEnd.

Silent on every failure. A broken notifier must never block a turn.
"""
import json, os, subprocess, sys, time

ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(ROOT, "bin")
STATE_DIR = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "claude-phone")
VERDICT = os.path.join(STATE_DIR, "where")
LOG = os.path.join(STATE_DIR, "presence.log")

RULES = """<phone-mode>
This prompt arrived from the user's phone over Remote Control -- this terminal has
not been touched in minutes -- so they cannot see the tmux panes, above all the
quest tracker, which has been parked for the duration. They did not type /phone;
this turned itself on, and it will turn itself off the moment they type locally.

- Everything you want them to read must be in the REPLY TEXT. The phone client
  shows only the text following the last tool call, so never end a turn with a
  tool call after your prose, and never let a tool call carry a point the reply
  does not also make in full.
- Send no notification. The reply waits for them; that is the point.
- ORDER, and it is not negotiable: quest tracker FIRST, then the TL;DR as the very
  last thing in the reply. The tldr Stop hook treats everything after "TL;DR:" as
  the TL;DR, so a tracker printed below it blows the word cap and the turn gets
  blocked. Tracker, then TL;DR, then stop.
- Reconcile the tracker BEFORE you start writing, never part-way through. If the
  Stop hook blocks the turn for a missing TL;DR, the continuation must add ONLY the
  TL;DR -- do not re-run `quest list` and do not print the tracker again. Doing so
  emits it twice with a stray tool call stranded between the two copies, which is
  what the user saw on 2026-08-26.
- End the reply with the quest tracker, as compact markdown -- never a fenced code
  block, which on a phone is monospace, wraps at about thirty characters and
  cannot reflow. Every reply, with no throttle: the entries they most need in
  front of them are the old ones they have stopped thinking about, so showing it
  only when it changes is exactly backwards.
- Keep replies short. Phone screens are narrow.
</phone-mode>"""


def run(cmd):
    try:
        out = subprocess.run(cmd, timeout=10, capture_output=True, text=True)
        return out.stdout.strip(), out.stderr.strip()
    except Exception:
        return "", ""


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        ev = {}
    event = ev.get("hook_event_name", "")
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
    except Exception:
        pass

    if event == "SessionEnd":
        run([os.path.join(BIN, "phone-pane"), "show"])
        return

    where, detail = run([os.path.join(BIN, "phone-presence")])
    where = where or "unknown"
    try:
        with open(LOG, "a") as f:
            f.write("%s %s %-8s %s\n" % (int(time.time()), event, where, detail))
        with open(VERDICT, "w") as f:
            f.write(where + "\n")
    except Exception:
        pass

    if where == "phone":
        run([os.path.join(BIN, "phone-pane"), "hide"])
        print(RULES)
    else:
        # At the terminal, or undeterminable -- in which case give the pane back,
        # since a wrongly-parked pane is the costlier error.
        run([os.path.join(BIN, "phone-pane"), "show"])


main()
