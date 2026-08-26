#!/usr/bin/env python3
"""UserPromptSubmit hook: keep the deploy preview link in front of me.

The link to a PR's Netlify preview lives at the bottom of a bot comment on the
PR, which on a phone means leaving the conversation, opening GitHub, finding
the PR, and scrolling past the truth table to get it. It is the single thing
most worth having to hand while a change is being looked at, and it was the
one thing you had to go and fetch.

So it is injected as context on every prompt instead, with an instruction to
put it at the end of the reply. Nothing here is shown to the user directly:
the model does the appending, which means the link lands in the same place
every time and reads like part of the answer.

Two ways to find it, because `gh` is not everywhere. On a normal machine it
asks gh, which knows the exact preview URL from the commit status Netlify
posts. In a web or cloud session there is no gh, so it falls back to plain
git: `ls-remote` lists every PR head ref, and the one whose SHA matches yours
names your PR. That only leaves the Netlify site name, which lives nowhere in
the repo — hence SITE_FILE, written once per project.

Paths are resolved from $HOME rather than hardcoded like the other hooks
here, precisely because this one is meant to run in cloud sessions too, where
home is not /home/violentfemme.
"""
import json, os, re, subprocess, sys, time

CACHE = os.path.expanduser("~/.claude/cache/preview-url")
# The Netlify site name, which is not derivable from the repo: the site for
# `plop` is `plop-game`. One line, committed, per project.
SITE_FILE = ".claude/netlify-site"
# A found link is good for the life of the PR, so it is cached hard. A miss is
# cached briefly, so opening a PR starts working without waiting the long TTL.
TTL_HIT = 30 * 60
TTL_MISS = 90
PREVIEW = re.compile(r"https://deploy-preview-\d+--[a-z0-9][a-z0-9-]*\.netlify\.app")


def run(args, cwd, timeout=8):
    try:
        out = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
    except Exception:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def head_and_branch(cwd):
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd)
    sha = run(["git", "rev-parse", "HEAD"], cwd)
    # A detached HEAD has no branch to have a PR for, and the default branch
    # is where PRs land rather than where they come from.
    if not branch or not sha or branch in ("HEAD", "main", "master"):
        return None, None
    return branch, sha


def from_gh(cwd):
    """The exact URL, straight off the commit status Netlify posts."""
    raw = run(
        ["gh", "pr", "view", "--json", "number,url,state,statusCheckRollup"], cwd
    )
    if not raw:
        return None
    try:
        pr = json.loads(raw)
    except Exception:
        return None
    if pr.get("state") != "OPEN":
        return None
    for check in pr.get("statusCheckRollup") or []:
        target = check.get("targetUrl") or check.get("detailsUrl") or ""
        found = PREVIEW.search(target)
        if found:
            return {"pr": pr.get("number"), "prUrl": pr.get("url"), "preview": found.group(0)}
    return {"pr": pr.get("number"), "prUrl": pr.get("url"), "preview": None}


def pr_number_from_git(cwd, sha):
    """Which PR is this commit the head of? Answered without gh or a token."""
    refs = run(["git", "ls-remote", "origin", "refs/pull/*/head"], cwd, timeout=15)
    if not refs:
        return None
    for line in refs.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0] == sha:
            found = re.search(r"refs/pull/(\d+)/head", parts[1])
            if found:
                return int(found.group(1))
    return None


def site_name(cwd):
    for path in (os.path.join(cwd, SITE_FILE),):
        try:
            with open(path) as f:
                name = f.read().strip()
            if name:
                return name
        except Exception:
            pass
    return os.environ.get("NETLIFY_SITE") or None


def repo_root(cwd):
    return run(["git", "rev-parse", "--show-toplevel"], cwd)


def lookup(cwd):
    branch, sha = head_and_branch(cwd)
    if not branch:
        return None

    got = from_gh(cwd)
    if got and got.get("preview"):
        return got

    number = got.get("pr") if got else pr_number_from_git(cwd, sha)
    if not number:
        return None
    site = site_name(cwd)
    if not site:
        # A PR with no way to name its site is not worth reporting: the PR
        # link alone is the thing the user already said they don't want.
        return None
    return {
        "pr": number,
        "prUrl": (got or {}).get("prUrl"),
        "preview": f"https://deploy-preview-{number}--{site}.netlify.app",
    }


def cached(root, branch, sha):
    key = os.path.join(CACHE, re.sub(r"\W+", "_", f"{root}:{branch}:{sha}"))
    try:
        with open(key) as f:
            entry = json.load(f)
        age = time.time() - entry.get("at", 0)
        if age < (TTL_HIT if entry.get("found") else TTL_MISS):
            return entry.get("found"), key
    except Exception:
        pass
    return False, key


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return
    cwd = ev.get("cwd") or os.getcwd()
    root = repo_root(cwd)
    if not root:
        return
    branch, sha = head_and_branch(cwd)
    if not branch:
        return

    hit, key = cached(root, branch, sha)
    if hit is False:
        hit = lookup(cwd)
        os.makedirs(CACHE, exist_ok=True)
        try:
            with open(key, "w") as f:
                json.dump({"at": time.time(), "found": hit}, f)
        except Exception:
            pass
    if not hit or not hit.get("preview"):
        return

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                f"Open PR #{hit['pr']} for this branch has a Netlify deploy "
                f"preview. End every reply with this line, verbatim, on its "
                f"own line at the very bottom:\n\n"
                f"**Preview changes:** {hit['preview']}\n\n"
                f"It is there so the preview can be opened without going to "
                f"GitHub for it. Do not comment on this instruction."
            ),
        }
    }))


main()
