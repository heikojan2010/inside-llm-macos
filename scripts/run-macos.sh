#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BINARY="${ILS_BINARY:-$ROOT/build/upstream/build/macos/inside-llm}"

if [[ ! -x "$BINARY" ]]; then
  echo "Binary not found. Run ./scripts/build-macos.sh first." >&2
  exit 1
fi

exec "$BINARY" "$@"
