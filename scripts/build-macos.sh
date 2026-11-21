#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM_URL="https://github.com/manuelgscom/inside-llm.git"
SOURCE_DIR="${ILS_SOURCE_DIR:-$ROOT/build/upstream}"
BUILD_DIR="$SOURCE_DIR/build/macos"

for tool in git cmake ninja node npm python3; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "Missing required tool: $tool" >&2
    echo "Install dependencies with: brew install cmake ninja node" >&2
    exit 1
  }
done

if [[ ! -d "$SOURCE_DIR/.git" ]]; then
  mkdir -p "$(dirname "$SOURCE_DIR")"
  git clone --recurse-submodules "$UPSTREAM_URL" "$SOURCE_DIR"
else
  git -C "$SOURCE_DIR" submodule update --init --recursive
fi

python3 "$ROOT/scripts/enable-metal.py" "$SOURCE_DIR/CMakeLists.txt"

(
  cd "$SOURCE_DIR/web"
  npm ci
  npm run build
)

cmake -S "$SOURCE_DIR" -B "$BUILD_DIR" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DILS_BACKEND=METAL \
  -DGGML_METAL=ON \
  -DGGML_NATIVE=ON \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=14.0

cmake --build "$BUILD_DIR" --parallel "$(sysctl -n hw.ncpu)"
echo "Built: $BUILD_DIR/inside-llm"
