import DilithiumModule from './dilithium_wasm.js';

// Constants for Dilithium3 (match your WASM exports)
const PK_LEN = 1472;
const SK_LEN = 3504;
const SIG_MAX_LEN = 2701;

export async function initDilithium() {
  // Load the WASM module and set up helpers
  const mod = await DilithiumModule({
    locateFile: (path) =>
      path.endsWith('.wasm') ? '/pqc/dilithium_wasm.wasm' : path,
  });

  // -- Memory Helpers --
  function allocArray(data) {
    // Accept Buffer, Array, or Uint8Array (convert to Uint8Array)
    if (typeof Buffer !== "undefined" && Buffer.isBuffer(data)) {
      data = new Uint8Array(data);
    } else if (Array.isArray(data)) {
      data = Uint8Array.from(data);
    }
    if (!(data instanceof Uint8Array)) {
      throw new Error("Data must be Uint8Array");
    }
    const ptr = mod._malloc(data.length);
    if (ptr === 0) throw new Error("WASM malloc failed!");
    mod.HEAPU8.set(data, ptr);
    return ptr;
  }

  function freeArray(ptr) {
    if (ptr !== 0) mod._free(ptr);
  }

  // -- Keypair generation (random) --
  async function keypair() {
    const pkPtr = mod._malloc(PK_LEN);
    const skPtr = mod._malloc(SK_LEN);
    if (pkPtr === 0 || skPtr === 0) {
      freeArray(pkPtr);
      freeArray(skPtr);
      throw new Error("Failed to allocate memory for keypair");
    }
    try {
      const result = mod._dilithium3_keypair(pkPtr, skPtr);
      if (result !== 0) throw new Error(`Keypair generation failed: ${result}`);
      const pk = new Uint8Array(mod.HEAPU8.subarray(pkPtr, pkPtr + PK_LEN));
      const sk = new Uint8Array(mod.HEAPU8.subarray(skPtr, skPtr + SK_LEN));
      return { publicKey: pk, secretKey: sk };
    } finally {
      freeArray(pkPtr);
      freeArray(skPtr);
    }
  }

  // -- Deterministic keypair generation from 32-byte seed --
  function generateKeypairFromSeed(seed) {
    // Accept Buffer, Array, or Uint8Array (convert to Uint8Array)
    if (typeof Buffer !== "undefined" && Buffer.isBuffer(seed)) {
      seed = new Uint8Array(seed);
    } else if (Array.isArray(seed)) {
      seed = Uint8Array.from(seed);
    }
    if (!(seed instanceof Uint8Array)) {
      throw new Error("Seed must be Uint8Array");
    }
    if (seed.length !== 32) {
      throw new Error("Seed buffer must be 32 bytes for Dilithium3 deterministic keygen.");
    }

    const seedPtr = mod._malloc(32);
    const pkPtr = mod._malloc(PK_LEN);
    const skPtr = mod._malloc(SK_LEN);
    mod.HEAPU8.set(seed, seedPtr);

    try {
      // If your WASM supports deterministic keygen, call _dilithium3_keypair_with_seed:
      if (typeof mod._dilithium3_keypair_with_seed === "function") {
        const result = mod._dilithium3_keypair_with_seed(pkPtr, skPtr, seedPtr);
        if (result !== 0) throw new Error(`Deterministic keypair failed: ${result}`);
      } else if (typeof mod._dilithium3_keypair === "function" && arguments.length === 2) {
        // If only random keygen is supported, this will NOT be deterministic!
        mod._dilithium3_keypair(pkPtr, skPtr);
      } else {
        throw new Error("No deterministic Dilithium3 keypair function in WASM.");
      }
      const pk = new Uint8Array(mod.HEAPU8.subarray(pkPtr, pkPtr + PK_LEN));
      const sk = new Uint8Array(mod.HEAPU8.subarray(skPtr, skPtr + SK_LEN));
      return { publicKey: pk, privateKey: sk };
    } finally {
      freeArray(seedPtr);
      freeArray(pkPtr);
      freeArray(skPtr);
    }
  }

  // -- Signing --
  function sign(message, secretKey) {
    if (!(message instanceof Uint8Array)) {
      message = new TextEncoder().encode(String(message));
    }
    if (!(secretKey instanceof Uint8Array)) {
      secretKey = new Uint8Array(secretKey);
    }
    if (secretKey.length !== SK_LEN) {
      throw new Error(`Secret key must be ${SK_LEN} bytes`);
    }

    const msgPtr = allocArray(message);
    const skPtr = allocArray(secretKey);
    const sigPtr = mod._malloc(SIG_MAX_LEN);
    const sigLenPtr = mod._malloc(4);

    try {
      mod.HEAPU32[sigLenPtr >> 2] = SIG_MAX_LEN;
      const result = mod._dilithium3_sign(sigPtr, sigLenPtr, msgPtr, message.length, skPtr);
      if (result !== 0) throw new Error(`Sign failed: ${result}`);
      const sigLen = mod.HEAPU32[sigLenPtr >> 2];
      if (sigLen > SIG_MAX_LEN) throw new Error(`Signature too long: ${sigLen}`);
      return new Uint8Array(mod.HEAPU8.subarray(sigPtr, sigPtr + sigLen));
    } finally {
      freeArray(msgPtr);
      freeArray(skPtr);
      freeArray(sigPtr);
      freeArray(sigLenPtr);
    }
  }

  // -- Verification --
  function verify(message, signature, publicKey) {
    if (!(message instanceof Uint8Array)) {
      message = new TextEncoder().encode(String(message));
    }
    if (!(signature instanceof Uint8Array)) {
      signature = new Uint8Array(signature);
    }
    if (!(publicKey instanceof Uint8Array)) {
      publicKey = new Uint8Array(publicKey);
    }
    if (publicKey.length !== PK_LEN) {
      throw new Error(`Public key must be ${PK_LEN} bytes`);
    }
    const msgPtr = allocArray(message);
    const sigPtr = allocArray(signature);
    const pkPtr = allocArray(publicKey);

    try {
      const result = mod._dilithium3_verify(sigPtr, signature.length, msgPtr, message.length, pkPtr);
      return result === 0;
    } finally {
      freeArray(msgPtr);
      freeArray(sigPtr);
      freeArray(pkPtr);
    }
  }

  // Export all functions needed elsewhere
  return {
    keypair,
    generateKeypairFromSeed,
    sign,
    verify,
    PK_LEN,
    SK_LEN,
    SIG_MAX_LEN
  };
}
