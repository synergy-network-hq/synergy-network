import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import ReactDOM from 'react-dom/client';
import App from './App';
import dilithiumWasmModule from "./pqc/dilithium_wasm";
import { Buffer } from 'buffer';
import "./styles/global.css";

window.Buffer = Buffer;

// --- Dilithium Keygen Wrapper ---
// Adjust sizes for your actual Dilithium3 implementation
const PUBLIC_KEY_LEN = 1952;   // bytes for Dilithium3
const SECRET_KEY_LEN = 4032;   // bytes for Dilithium3

function generateKeypairFromSeed(seedBuffer) {
  const mod = window.dilithium;

  // Allocate seed in WASM heap
  const seedPtr = mod._malloc(seedBuffer.length);
  mod.HEAPU8.set(seedBuffer, seedPtr);

  // Allocate buffers for public/private key
  const pkPtr = mod._malloc(PUBLIC_KEY_LEN);
  const skPtr = mod._malloc(SECRET_KEY_LEN);

  // Call the function directly!
  mod._dilithium3_keypair(pkPtr, skPtr, seedPtr);

  // Read the keys
  const publicKey = new Uint8Array(mod.HEAPU8.buffer, pkPtr, PUBLIC_KEY_LEN);
  const privateKey = new Uint8Array(mod.HEAPU8.buffer, skPtr, SECRET_KEY_LEN);

  // Detach from WASM heap
  const pub = new Uint8Array(publicKey);
  const priv = new Uint8Array(privateKey);

  // Free WASM heap
  mod._free(seedPtr);
  mod._free(pkPtr);
  mod._free(skPtr);

  return { publicKey: pub, privateKey: priv };
}


// --- Load WASM, attach wrapper, then render app ---
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <div style={{
    color: "#fff",
    background: "#18112a",
    width: "100vw",
    height: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "1.5rem"
  }}>
    Loading Synergy cryptography engine…
  </div>
);

dilithiumWasmModule().then((mod) => {
  window.dilithium = mod;
  window.dilithium.generateKeypairFromSeed = generateKeypairFromSeed;
  console.log("Dilithium WASM loaded!", window.dilithium);

  root.render(
    <React.StrictMode>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </React.StrictMode>
  );
});
