---
name: phone
description: Phone mode — the user is driving this session from their phone via Remote Control and cannot see the tmux panes, above all the quest tracker. Turns itself ON when a prompt arrives from the phone and OFF the moment they type locally again; it never relies on them remembering either. Use when the hook injects <phone-mode>, when the user runs /phone or /phone off, or when they say they are on their phone.
---

# Phone

The user is on their phone. The tmux panes — above all the quest tracker — are invisible
to them, so what the panes normally carry has to ride in the replies instead.

**Design rule for everything here: the user must never need to remember to turn it off,
and never has to remember to turn it on either.** Once someone has moved on, the thing
they left running is no longer in their head, and the thing they meant to start never got
started. Both ends are the assistant's job. Every behaviour below begins and ends on its
own.

## How it switches itself on and off

`hooks/phone-mode.py`, on SessionStart and every UserPromptSubmit, via
`bin/phone-presence`. Sending a prompt from the terminal means pressing Enter inside
tmux, which stamps that client's `#{client_activity}`; a prompt arriving over Remote
Control enters the process by its messaging socket and never touches the tmux client, so
the stamp stops advancing for as long as the user is away.

The window is minutes and deliberately generous — see `bin/phone-presence` for why erring
toward "terminal" is the cheap direction to be wrong in. The sample is **only valid at
submit time**, so the hook caches the verdict for the turn in
`$XDG_RUNTIME_DIR/claude-phone/where`. Read that; never re-sample.

A machine with no tmux server running — a cloud VM, for instance — reads as "phone",
which is correct: such a session is always driven remotely.

`/phone` still works as a manual override, for when the user is at the terminal but about
to walk away. `/phone off` or "I'm back" cancels it.

## While phone mode is on

1. **Everything you want them to read must be in the reply text.** The phone client shows
   only the text following the last tool call, so never end a turn with a tool call after
   your prose, and never let a tool call carry a point the reply does not also make in
   full. Both halves of that were learnt the hard way: a report written above a final
   tool call and never seen, and a notification body carrying an answer the reply then
   never repeated.
2. **Send no notification.** The reply waits for them. Anything else rebuilds the
   interruption the mode exists to avoid.
3. **Put the tracker at the end of EVERY reply. No throttle, no cooldown.** Repetition is
   the function, not a side effect to minimise. The user is not using it to recall what
   just happened — they remember that. They are using it so everything *older* stays in
   front of them instead of being re-derived each time. A tracker seen intermittently is
   worse than none, because its absence cannot be trusted to mean "nothing changed".

   Two rules that look sensible are both wrong here. A time-based cooldown couples to how
   fast the user types, so a quick exchange shows the tracker least — exactly when it is
   moving most. Showing it only when its content *changes* is worse still: the entries
   most needed in front of them are the old ones they have stopped thinking about, and
   those are by definition not changing.
4. **Render it compactly, as markdown — never a fenced code block.** On a phone a fence
   is monospace, wraps at about thirty characters, cannot reflow, and carries a copy
   button; one entry can eat half the screen. Plain markdown reflows to the device at
   roughly a third of the height:

   ```
   **⚔ Quest title**
   **›q1** the live step
   **q2** another step
   *tangents* · **t1** something parked
   ```

   Keep labels exactly as the pane names them (`q1`, `q2.1`, `t1`, `b1`) — they are how
   the user addresses entries and must match `quest list`. The entry text is the user's
   own words; leave it verbatim.
5. **The tmux quest pane is parked for the duration**, by `bin/phone-pane hide`. Remote
   Control mirrors the PTY, so the columns that pane eats come out of the width the reply
   gets on a phone screen — and its content is riding in the reply anyway. The pane and
   the reply block are the same thing in two places, so exactly one exists at a time:
   whichever is where the user is.
6. Keep replies short. Phone screens are narrow.

## The pane always comes back

`bin/phone-pane show` runs when a locally-typed prompt arrives, on SessionEnd, and
whenever presence cannot be determined — ambiguity restores it, because a wrongly-parked
pane is the costlier error. It rebuilds the pane at its recorded width in its original
window and refuses to add a second if something already put one back. A session that dies
hard never fires SessionEnd, which is why the first and third paths exist.

## Requires

The quest-tracker plugin, for the tracker this carries into replies, and tmux for
presence detection. Without tmux the mode simply never activates on a local machine; in a
cloud session it activates always, which is correct.
