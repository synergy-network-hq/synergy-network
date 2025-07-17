# Dilithium WebAssembly Build

This directory contains the pq-crystals Dilithium-3 reference implementation compiled to WebAssembly using Emscripten.

## Building

Ensure the `emscripten` toolchain is installed and available as `emcc`.
Run the provided build script:

```bash
./build.sh
```

This produces `dilithium_wasm.js` and `dilithium_wasm.wasm` which can be loaded from JavaScript.

## Usage

Load `dilithium.js` as an ES module. It provides an async `initDilithium()` function that returns `{ keypair, sign, verify }` helpers using the WebAssembly module.

See `demo.html` for a browser example.
