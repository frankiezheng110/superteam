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
echo "[superteam] usage:"
echo "  cd <target-repo>"
echo "  claude-superteam"
echo
echo "[superteam] if '$BIN_DIR' is not in PATH, add it first."
