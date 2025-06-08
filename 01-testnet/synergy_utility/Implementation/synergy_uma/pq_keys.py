"""
synergy_uma/pq_keys.py

Implements REAL post-quantum synergy key generation using the 'pqcrypto' library
(specifically Dilithium2 for signatures). Then, we define a synergy seed,
store it, and load it. Also includes basic local encryption for private keys.
"""

import os
import json
import base64
import hashlib
from typing import Optional

# For actual post-quantum signing we can use dilithium2 from pqcrypto.sign
# pip install pqcrypto
try:
    from pqcrypto.sign import dilithium2
except ImportError:
    raise ImportError("Please install pqcrypto (pip install pqcrypto) to use Dilithium2 post-quantum signatures.")

# For encryption:
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

SALT_SIZE = 16
KEY_SIZE = 32
NONCE_SIZE = 12

def generate_synergy_seed(password: str) -> dict:
    """
    Generates a synergy 'seed' using Dilithium2 keypair.
    Then we create a synergy meta-address from the public key.

    If a password is provided, we encrypt the private key with AES.
    """
    # Generate a new Dilithium2 keypair
    keypair = dilithium2.generate_keypair()
    # keypair: (public_key, secret_key)

    pub_bytes = keypair.public_key
    sec_bytes = keypair.secret_key

    synergy_address = compute_synergy_meta_address(pub_bytes)

    if password:
        # Encrypt secret key
        enc_data = encrypt_secret_key(sec_bytes, password)
        sec_storage = {
            "encrypted": True,
            "data": base64.b64encode(enc_data).decode()
        }
    else:
        # Store unencrypted (NOT recommended for production)
        sec_storage = {
            "encrypted": False,
            "data": base64.b64encode(sec_bytes).decode()
        }

    synergy_info = {
        "public_key": base64.b64encode(pub_bytes).decode(),
        "private_key": sec_storage,
        "synergy_address": synergy_address
    }
    return synergy_info


def compute_synergy_meta_address(public_key: bytes) -> str:
    """
    Convert a Dilithium2 public key into a synergy meta-address.
    We'll do a bech32-like or base58 approach. For demonstration, we:
    1. Hash the public key
    2. Take some bytes and encode them
    3. Add a prefix like 'sYnQ_'

    You can refine this to your actual synergy address standard.
    """
    h = hashlib.sha256(public_key).digest()
    # take 20 bytes
    truncated = h[:20]
    # base58 or base64, let's do base58. We'll do a minimal base58 function:
    encoded = base58_encode(truncated)
    return f"sYnQ_{encoded}"


def encrypt_secret_key(secret_key_bytes: bytes, password: str) -> bytes:
    """
    Encrypts the secret key with AES-GCM using a password-based key derivation.
    """
    salt = get_random_bytes(SALT_SIZE)
    # Derive a key from password
    derived_key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=100000)
    nonce = get_random_bytes(NONCE_SIZE)

    cipher = AES.new(derived_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(secret_key_bytes)

    # Store salt + nonce + tag + ciphertext
    return salt + nonce + tag + ciphertext


def decrypt_secret_key(enc_data: bytes, password: str) -> bytes:
    """
    Decrypts the secret key with AES-GCM using a password-based key derivation.
    """
    salt = enc_data[:SALT_SIZE]
    nonce = enc_data[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    tag = enc_data[SALT_SIZE + NONCE_SIZE:SALT_SIZE + NONCE_SIZE + 16]
    ciphertext = enc_data[SALT_SIZE + NONCE_SIZE + 16:]

    derived_key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=100000)
    cipher = AES.new(derived_key, AES.MODE_GCM, nonce=nonce)
    cipher.update(b"")  # we didn't add any additional data
    plain = cipher.decrypt_and_verify(ciphertext, tag)
    return plain


def load_synergy_info(filepath: str, password: Optional[str] = None) -> Optional[dict]:
    """
    Load synergy info from JSON, decrypt private key if needed.
    """
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Decrypt private key if encrypted
    priv_dict = data.get("private_key", {})
    if priv_dict.get("encrypted"):
        if not password:
            raise ValueError("Password is required to decrypt synergy seed.")
        enc_b = base64.b64decode(priv_dict["data"].encode())
        try:
            raw_sec = decrypt_secret_key(enc_b, password)
        except Exception as e:
            raise ValueError(f"Invalid password or corrupted data: {e}")
        data["private_key"]["data"] = base64.b64encode(raw_sec).decode()
        data["private_key"]["encrypted"] = False

    return data


def save_synergy_info(filepath: str, synergy_data: dict):
    with open(filepath, 'w') as f:
        json.dump(synergy_data, f, indent=2)


def base58_encode(b: bytes) -> str:
    """
    Minimal base58 encode for demonstration. You might prefer a library like 'base58'.
    """
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    num = int.from_bytes(b, "big")

    enc = ""
    while num > 0:
        num, idx = divmod(num, 58)
        enc = alphabet[idx] + enc

    # For leading 0 bytes, we add '1' per zero
    pad = 0
    for byte in b:
        if byte == 0:
            pad += 1
        else:
            break
    return ("1" * pad) + enc


def derive_subkey_for_chain(synergy_data: dict, chain_name: str, password: Optional[str] = None) -> dict:
    """
    Real approach: we have a PQ secret key (Dilithium). We want to generate
    sub-keys for EVM, Solana, Tron, etc. Typically that means a 'hybrid' approach:
    e.g., combine hash of PQ secret with a classical ECDSA or Ed25519 routine.

    For demonstration, let's do a simple hashing approach => yields a classical private key.
    """
    # We want the raw secret key bytes:
    priv_dict = synergy_data["private_key"]
    if priv_dict.get("encrypted"):
        return {"success": False, "error": "Private key still encrypted, password required."}

    raw_sec = base64.b64decode(priv_dict["data"].encode())

    # We'll create a classical private key by hashing raw_sec + chain_name
    import hashlib
    seed_for_chain = hashlib.sha256(raw_sec + chain_name.encode()).digest()

    # Then we can produce chain-specific addresses using chain_derivations
    from . import chain_derivations as cderiv

    if chain_name.lower() == "ethereum":
        eth_addr = cderiv.derive_ethereum_address(seed_for_chain)
        return {"success": True, "chain_name": chain_name, "chain_address": eth_addr}

    elif chain_name.lower() == "solana":
        sol_addr = cderiv.derive_solana_address(seed_for_chain)
        return {"success": True, "chain_name": chain_name, "chain_address": sol_addr}

    elif chain_name.lower() == "tron":
        tron_addr = cderiv.derive_tron_address(seed_for_chain)
        return {"success": True, "chain_name": chain_name, "chain_address": tron_addr}
    else:
        # Generic fallback
        hex_addr = seed_for_chain[:5].hex().upper()
        return {"success": True, "chain_name": chain_name, "chain_address": f"{chain_name.upper()}_{hex_addr}"}
