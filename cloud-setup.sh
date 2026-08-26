#!/bin/bash
# Claude Code cloud environment setup script.
# Paste into the environment dialog's "Setup script" field at claude.ai/code.
#
# Installs the tldr Stop hook at USER level, so it applies to every cloud session
# in this environment regardless of which repo it clones.
#
# quest-tracker is deliberately NOT installed. The ledger is a file on the laptop;
# a cloud sandbox has no path to it, so it would get a fresh empty one -- unable to
# show the real quest, and writing entries nobody will ever read. Worse, its Stop
# hook blocks any turn that did not consult the ledger, which in the cloud is a
# wasted round trip on every substantive turn, enforcing a pane that isn't there. Runs as root on Ubuntu 24.04, before Claude Code launches, and the
# filesystem is snapshotted afterwards -- so this cost is paid once, not per session.
#
# Every command is || true: a non-zero exit fails the whole session.

set -u
CLAUDE_HOME="${HOME}/.claude"
mkdir -p "$CLAUDE_HOME/hooks" || true

# The repo is public, so no credentials and no GitHub proxy scoping applies.
git clone --depth 1 https://github.com/pipedreambomb/claude-skills \
  /opt/claude-skills 2>&1 || true

if [ -d /opt/claude-skills ]; then
  python3 - <<'PY' || true
import json, os
home = os.path.join(os.environ["HOME"], ".claude")
path = os.path.join(home, "settings.json")
try:
    cfg = json.load(open(path))
except Exception:
    cfg = {}

cfg.setdefault("extraKnownMarketplaces", {})["pipedreambomb-claude-skills"] = {
    "source": {"source": "github", "repo": "pipedreambomb/claude-skills"}
}
# Every hook ships inside its plugin, so enabling the plugin is all that is
# needed -- no hand-written hook paths pointing at files that may not exist.
cfg.setdefault("enabledPlugins", {})["tldr@pipedreambomb-claude-skills"] = True
cfg["enabledPlugins"].pop("quest-tracker@pipedreambomb-claude-skills", None)
json.dump(cfg, open(path, "w"), indent=2)
print("wrote", path)
PY
fi

# A marker the first cloud session can read back, so "did this run?" is answerable
# without guessing.
{
  echo "cloud-setup ran at $(date -Is)"
  echo "HOME=$HOME  user=$(id -un)"
  echo "repo cloned: $([ -d /opt/claude-skills ] && echo yes || echo NO)"
  echo "settings.json: $([ -f "$CLAUDE_HOME/settings.json" ] && echo yes || echo NO)"
} > "$CLAUDE_HOME/cloud-setup.log" 2>&1 || true

exit 0
