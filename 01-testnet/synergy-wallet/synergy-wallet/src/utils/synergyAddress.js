import { bech32m } from 'bech32';

const PREFIXES = ['sYnQ', 'sYnW', 'sYnZ', 'sYnX'];

function sha256(buf) {
  return window.crypto.subtle.digest('SHA-256', buf);
}

function randomPrefix() {
  // Pick a prefix at random
  const idx = Math.floor(Math.random() * PREFIXES.length);
  return PREFIXES[idx];
}

export async function pubkeyToSynergyAddress(pubkey, prefix) {
  // If no prefix specified, pick random
  const chosenPrefix = prefix || randomPrefix();
  const hash = await sha256(pubkey);
  const words = bech32m.toWords(new Uint8Array(hash));
  return bech32m.encode(chosenPrefix, words);
}
