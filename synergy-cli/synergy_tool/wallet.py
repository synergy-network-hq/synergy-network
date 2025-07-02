import os
import json
import base64
import hashlib
from typing import Dict

from cryptography.fernet import Fernet
from bip_utils import (
    Bip39MnemonicGenerator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
    SolAddr,
    Bip32Slip10Secp256k1,
)
from bech32 import bech32_encode, convertbits
from eth_account import Account

Account.enable_unaudited_hdwallet_features()

SYNERGY_COIN = 1234
SYNERGY_PREFIX = "sYnQ"


def _fernet(password: str) -> Fernet:
    key = hashlib.sha256(password.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def generate_mnemonic() -> str:
    return Bip39MnemonicGenerator().FromWordsNumber(12).ToStr()


def _derive_priv_key_custom(seed: bytes, path: str) -> bytes:
    master = Bip32Slip10Secp256k1.FromSeed(seed)
    child = master.DerivePath(path)
    return child.PrivateKey().Raw().ToBytes()


def synergy_address_from_pubkey(pubkey_bytes: bytes) -> str:
    data = convertbits(pubkey_bytes, 8, 5)
    return bech32_encode(SYNERGY_PREFIX, data)


def create_wallet(password: str, path: str) -> Dict:
    mnemonic = generate_mnemonic()
    seed = Bip39SeedGenerator(mnemonic).Generate()
    priv = _derive_priv_key_custom(seed, "m/44'/1234'/0'/0/0")
    pub_key = Account.from_key(priv)._key_obj.public_key.to_bytes()
    address = synergy_address_from_pubkey(pub_key)
    keystore = {"mnemonic": mnemonic, "address": address}
    f = _fernet(password)
    enc = f.encrypt(json.dumps(keystore).encode()).decode()
    with open(path, "w") as fh:
        json.dump({"keystore": enc}, fh)
    return keystore


def load_wallet(path: str, password: str) -> Dict:
    with open(path) as fh:
        enc = json.load(fh)["keystore"]
    f = _fernet(password)
    data = f.decrypt(enc.encode())
    return json.loads(data)


def btc_address(mnemonic: str) -> str:
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44_mst = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
    acct = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    return acct.PublicKey().ToAddress()


def eth_address(mnemonic: str) -> str:
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44_mst = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
    acct = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    return acct.PublicKey().ToAddress()


def sol_address(mnemonic: str) -> str:
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44_mst = Bip44.FromSeed(seed, Bip44Coins.SOLANA)
    acct = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    return SolAddr.EncodeKey(acct.PublicKey().RawCompressed().ToBytes())
