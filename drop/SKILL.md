---
name: drop
description: Open a Linux window George can drag any file onto — images, documents, archives — or paste an image into with Ctrl+V, then read what lands. Use when he wants to hand over a screenshot or file, when a paste arrived as `<img src="blob:...">` text with no image, or when he names this skill.
---

# Handing Claude a file on Crostini

ChromeOS and the container keep **separate clipboards**. ChromeOS pushes its one across
only when a **Linux window takes focus**, and the ChromeOS Terminal is an hterm web app,
so it never triggers that. Measured 2026-09-19:

- Launching a window changes nothing — the clipboard stayed byte-identical.
- One click handed the image over immediately.
- It is **one-shot per focus**: an earlier click does not hold a channel open. Every new
  copy needs its own focus event.

Clicking into this window to paste *is* the hand-off. **Dragging skips the clipboard
entirely** and is the better route — a `.md` and a `.zip` went through untouched on the
first try.

**A paste that arrives as `<img src="blob:chrome-untrusted://media-app/…">` with no image
is a diagnosis, not a mystery:** it was a *text* paste. Search+V and Ctrl+Shift+V are the
Terminal's own paste and only ever send characters. Nothing was wrong with the copy.

## Steps

1. **Launch it**, unless already running.

   ```
   pgrep -f 'bin/drop$' >/dev/null || DISPLAY=:0 setsid nohup ~/.local/bin/drop >>/tmp/drop.log 2>&1 < /dev/null &
   ```

   **`setsid` is load-bearing.** `nohup … &` alone leaves the window in the tool call's
   process group, and it is reaped when that call ends — so the window reports as open,
   then is gone by the time George reaches for it. This wasted a round trip twice on
   2026-09-19, the second time losing a screenshot he had dropped onto a window that no
   longer existed. `setsid` puts it in its own session so it outlives the shell. Verify
   with a *separate* Bash call, not the one that launched it; within the launching call
   it is always alive.

   **The `$` anchor is the whole point.** The running window's command line is exactly
   `python3 /home/violentfemme/.local/bin/drop`, so anchoring on `bin/drop$` matches it
   and nothing else. Any looser pattern — including the `[d]rop` bracket trick — matches
   *your own shell's command line*, because that line contains the words you are
   searching for. This misfired three times on 2026-09-19: twice killing the wrong
   process (once the session's own shell, mid-file-move), and once reporting the window
   as open to George when it was not there at all. He replied: *"no it isn't open."*
   Never report the window's state from a pattern you have not anchored.

2. **Tell George in one line:** drag the file onto the window, or click it and press
   **Ctrl+V** — not Ctrl+Shift+V, not Search+V.

3. **Wait for something to land.** Poll `~/drops/` for a file newer than when the window
   opened, up to ~90s, every few seconds. `/tmp/drop.log` prints each path as it saves.

4. **Read it.** `~/drops/latest` points at the newest — a plain name, since anything can
   land there. Then answer whatever he opened it for.

5. **Leave the window open** unless he says otherwise.

## When nothing lands

```
xclip -selection clipboard -t TARGETS -o
```

`image/png` present means the hand-off worked and the problem is downstream. Only
`UTF8_STRING` means it never crossed — he has not focused the window since copying.

## Do not

- Do not suggest a different terminal emulator. George, 2026-09-19: *"don't be silly. i
  have to use the terminal emulator chrome os gives me."*
- Do not suggest sharing a ChromeOS folder with Linux. "Share with Linux" appears only on
  folders, never on files, and nothing is shared here but `fonts`.
- Do not ask him to describe what he is looking at. Open it and look.

## Known and deliberately unfixed

A **1px white line** sits at the very top of the window. It is not the headerbar — that is
styled dark and verified so by screenshot. It is sommelier drawing its own frame edge
outside the window's own surface, so no GTK CSS reaches it. George, 2026-09-19, having
seen the styled version: *"still like a 1px white bar. i don't really want to spend any
more time on this."* Leave it alone.

## Photographing the window

There is no screenshot tool in the container and root-window capture fails under
sommelier (`gdk_pixbuf_get_from_surface: assertion 'width > 0 && height > 0' failed`).
A window can capture *its own* surface, which is how the design above was checked without
asking George for screenshots:

```python
pb = Gdk.pixbuf_get_from_window(w.get_window(), 0, 0, width, height)
```

Allow ~5s before grabbing if the window has just resized, or the capture comes back blank.

Do not turn `set_show_close_button` back on. Under this GTK theme the window controls it
adds render with no visible icon, so they are invisible until hovered. George, 2026-09-19:
*"there's a problem where it has a bunch of invisible until you hover over them buttons."*
The custom ✕ in the header is the only window control, and Escape also closes.
