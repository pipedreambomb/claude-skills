#!/bin/bash
# Claude Code cloud environment setup script (v2).
# Paste into the environment dialog's "Setup script" field at claude.ai/code.
#
# v1 registered a marketplace in ~/.claude/settings.json and nothing loaded: the
# cloud harness owns that file (see launcher-settings.json and its own stop-hook-*
# scripts alongside it). So place the plugins instead of registering them --
# a directory in ~/.claude/skills/ with a .claude-plugin/plugin.json loads as a
# skills-dir plugin, hooks included, with no settings entry needed.
#
# Every plugin in the repo is copied, rather than a list kept in step by hand.
# The list drifted: preview-link shipped and never reached a cloud session,
# because adding a plugin and remembering to add it here are two jobs and only
# the first one is obvious. Anything with a .claude-plugin/plugin.json is a
# plugin and travels.
#
# Runs as root on Ubuntu 24.04, before Claude Code launches, and the filesystem
# is snapshotted afterwards -- so this cost is paid once, not per session.
#
# Every command is || true: a non-zero exit fails the whole session.

set -u
SKILLS="${HOME}/.claude/skills"
mkdir -p "$SKILLS" || true

git clone --depth 1 https://github.com/pipedreambomb/claude-skills \
  /opt/claude-skills 2>&1 || true

if [ -d /opt/claude-skills ]; then
  for plugin in /opt/claude-skills/*/; do
    [ -f "${plugin}.claude-plugin/plugin.json" ] || continue
    cp -r "$plugin" "$SKILLS/" 2>/dev/null || true
  done
  cp /opt/claude-skills/quest-tracker/bin/quest /usr/local/bin/quest 2>/dev/null || true
  chmod +x /usr/local/bin/quest "$SKILLS"/*/bin/* "$SKILLS"/*/scripts/* 2>/dev/null || true
fi

{
  echo "cloud-setup v2 ran at $(date -Is)"
  echo "HOME=$HOME  user=$(id -un)"
  echo "skills dir:"; ls -1 "$SKILLS" 2>&1 | sed 's/^/  /'
  for plugin in /opt/claude-skills/*/; do
    name="$(basename "$plugin")"
    [ -f "${plugin}.claude-plugin/plugin.json" ] || continue
    echo "$name plugin.json: $([ -f "$SKILLS/$name/.claude-plugin/plugin.json" ] && echo yes || echo NO)"
  done
  echo "quest runs: $(quest list 2>&1 | head -2)"
} > "${HOME}/.claude/cloud-setup.log" 2>&1 || true

exit 0
