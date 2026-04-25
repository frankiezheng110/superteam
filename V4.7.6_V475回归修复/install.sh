#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v claude >/dev/null 2>&1; then
  echo "[superteam] error: 'claude' was not found in PATH" >&2
  exit 1
fi

echo "[superteam] validating plugin..."
claude plugin validate "$ROOT_DIR"

BIN_DIR="${HOME}/.claude/bin"
mkdir -p "$BIN_DIR"

LAUNCHER="$BIN_DIR/claude-superteam"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
exec claude --plugin-dir "$ROOT_DIR" "\$@"
EOF
chmod +x "$LAUNCHER"

echo
echo "[superteam] installed launcher: $LAUNCHER"

# V4.6.0: merge hooks into user-level ~/.claude/settings.json
SETTINGS_TARGET="${HOME}/.claude/settings.json"
HOOK_TEMPLATE="$ROOT_DIR/hooks/hooks_settings_template.json"
MERGE_SCRIPT="$ROOT_DIR/hooks/install_merge.py"

if [ -f "$HOOK_TEMPLATE" ]; then
  echo
  echo "[superteam] merging V4.6.0 hooks into $SETTINGS_TARGET ..."
  python3 "$MERGE_SCRIPT" "$HOOK_TEMPLATE" "$SETTINGS_TARGET" || {
    echo "[superteam] hook merge failed" >&2
    exit 1
  }
  echo "[superteam] running matrix self-check ..."
  python3 "$ROOT_DIR/hooks/matrix_selfcheck.py" || {
    echo "[superteam] matrix self-check failed — hook files and matrix are out of sync" >&2
    exit 1
  }
fi

echo "[superteam] usage:"
echo "  cd <target-repo>"
echo "  claude-superteam"
echo
echo "[superteam] if '$BIN_DIR' is not in PATH, add it first."
