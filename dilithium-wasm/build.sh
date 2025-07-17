#!/usr/bin/env bash
set -euo pipefail

EMCC=${EMCC:-emcc}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/src"
OUT_DIR="${SCRIPT_DIR}/dist"

if [ ! -d "${OUT_DIR}" ]; then
  mkdir -p "${OUT_DIR}"
fi
if [ ! -d "${SRC_DIR}" ]; then
  echo "Source directory not found: ${SRC_DIR}"
  exit 1
fi

CFILES=(
  sign.c
  packing.c
  polyvec.c
  poly.c
  ntt.c
  reduce.c
  rounding.c
  symmetric-shake.c
  fips202.c
)
SOURCES=()
for f in "${CFILES[@]}"; do
  SOURCES+=("${SRC_DIR}/${f}")
done
SOURCES+=("${SCRIPT_DIR}/wasm_randombytes.c")
SOURCES+=("${SCRIPT_DIR}/wasm_wrapper.c")

for src in "${SOURCES[@]}"; do
  if [ ! -f "${src}" ]; then
    echo "Source file not found: ${src}"
    exit 1
  fi
done

if [ ! -x "$(command -v ${EMCC})" ]; then
  echo "Emscripten (emcc) is not installed or not in PATH."
  exit 1
fi

echo "Compiling sources to WebAssembly..."

$EMCC -O3 -DDILITHIUM_MODE=3 \
  "${SOURCES[@]}" -I"${SRC_DIR}" \
  -s EXPORTED_RUNTIME_METHODS='["ccall","cwrap","getValue","setValue","UTF8ToString","stringToUTF8","HEAPU8","HEAPU32"]' \
  -s EXPORTED_FUNCTIONS='["_dilithium3_keypair","_dilithium3_keypair_from_seed","_dilithium3_sign","_dilithium3_verify","_malloc","_free", "_dilithium3_keypair_from_seed"]' \
  -s MODULARIZE=1 \
  -s ENVIRONMENT=web \
  -s EXPORT_NAME="DilithiumModule" \
  -s INITIAL_MEMORY=67108864 \
  -s ALLOW_MEMORY_GROWTH=1 \
  -s TOTAL_STACK=33554432 \
  -s ASSERTIONS=1 \
  -s NO_FILESYSTEM=1 \
  -o "${OUT_DIR}/dilithium_wasm.js"

if [ ! -f "${OUT_DIR}/dilithium_wasm.js" ]; then
  echo "Build failed: Output file not created."
  exit 1
fi

echo "Build successful: ${OUT_DIR}/dilithium_wasm.js and .wasm"
