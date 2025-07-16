// src/utils/umaAddresses.js

import { mnemonicToSeedSync } from '@scure/bip39';
import { HDKey } from '@scure/bip32';
import { publicToAddress, toChecksumAddress } from "ethereumjs-util";
import { Buffer } from 'buffer';
import { derivePath as solDerivePath } from "ed25519-hd-key";
import { Keypair } from "@solana/web3.js";

// ---- Bitcoin (BIP44) ----
export function generateBTCAddressFromMnemonic(mnemonic, path = "m/44'/0'/0'/0/0") {
  const seed = mnemonicToSeedSync(mnemonic);
  const hdkey = HDKey.fromMasterSeed(seed);
  const child = hdkey.derive(path);

  // Bitcoin address (p2pkh): RIPEMD160(SHA256(pubkey))
  // Use @noble/secp256k1 to get the compressed public key
  const pubkey = child.publicKey; // Uint8Array
  // Minimal p2pkh address encoding in browser:
  const ripemd160 = require('ripemd160');
  const sha256 = require('js-sha256');
  const pubkeyHash = new ripemd160().update(Buffer.from(sha256.arrayBuffer(pubkey))).digest();
  // prepend version byte (0x00 for mainnet), append checksum, then base58 encode
  const bs58check = require('bs58check');
  const payload = Buffer.concat([Buffer.from([0x00]), Buffer.from(pubkeyHash)]);
  const address = bs58check.encode(payload);

  return {
    address,
    pubkey: Buffer.from(pubkey).toString('hex'),
    chain: 'bitcoin',
    derivationPath: path,
  };
}

// ---- Ethereum (BIP44, EIP-55) ----
export function generateETHWalletFromMnemonic(mnemonic, path = "m/44'/60'/0'/0/0") {
  const seed = mnemonicToSeedSync(mnemonic);
  const hdkey = HDKey.fromMasterSeed(seed);
  const child = hdkey.derive(path);

  // Public key must be uncompressed, remove first byte (0x04)
  let pubkey = child.publicKey;
  if (pubkey[0] === 0x04 && pubkey.length === 65) {
    pubkey = pubkey.slice(1);
  }
  const ethAddressBuffer = publicToAddress(Buffer.from(pubkey), true); // true = ethereum
  const address = toChecksumAddress("0x" + ethAddressBuffer.toString("hex"));

  return {
    address,
    pubkey: Buffer.from(pubkey).toString('hex'),
    chain: 'ethereum',
    derivationPath: path,
  };
}

// ---- Solana (BIP44, ed25519, m/44'/501'/0'/0') ----
export function generateSOLWalletFromMnemonic(mnemonic, path = "m/44'/501'/0'/0'") {
  const seed = mnemonicToSeedSync(mnemonic);
  const derived = solDerivePath(path, Buffer.from(seed).toString("hex"));
  const keypair = Keypair.fromSeed(derived.key);
  return {
    address: keypair.publicKey.toBase58(),
    pubkey: keypair.publicKey.toBase58(),
    chain: 'solana',
    derivationPath: path,
  };
}
