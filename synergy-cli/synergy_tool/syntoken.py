import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
TOKENS_DB = BASE_DIR / "synergy-cli" / "synergy_tool" / "tokens.json"
LEDGER_PATH = BASE_DIR / "01-testnet" / "synergy-wallet" / "synergy-wallet" / "public" / "token_ledger.json"


@dataclass
class Token:
    name: str
    symbol: str
    is_mutable: bool
    supply: int = 0


def _load() -> dict:
    if os.path.exists(TOKENS_DB):
        with open(TOKENS_DB) as f:
            return json.load(f)
    return {}


def _save(db: dict) -> None:
    with open(TOKENS_DB, "w") as f:
        json.dump(db, f, indent=2)


def create(name: str, symbol: str, is_mutable: bool) -> Token:
    db = _load()
    if symbol in db:
        raise ValueError("token already exists")
    token = Token(name, symbol, is_mutable)
    db[symbol] = asdict(token)
    _save(db)
    return token


def mint(symbol: str, amount: int) -> None:
    db = _load()
    token = db.get(symbol)
    if not token:
        raise ValueError("unknown token")
    token["supply"] += amount
    db[symbol] = token
    _save(db)


def burn(symbol: str, amount: int) -> None:
    db = _load()
    token = db.get(symbol)
    if not token:
        raise ValueError("unknown token")
    if token["supply"] < amount:
        raise ValueError("insufficient supply")
    token["supply"] -= amount
    db[symbol] = token
    _save(db)


def info(symbol: str) -> Optional[dict]:
    return _load().get(symbol)

def _load_ledger() -> Dict[str, Dict[str, int]]:
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH) as f:
            return json.load(f)
    return {}


def _save_ledger(data: Dict[str, Dict[str, int]]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "w") as f:
        json.dump(data, f, indent=2)


def deposit(symbol: str, address: str, amount: int) -> None:
    db = _load()
    token = db.get(symbol)
    if not token:
        raise ValueError("unknown token")
    if token["supply"] < amount:
        raise ValueError("insufficient supply")
    token["supply"] -= amount
    db[symbol] = token
    _save(db)

    ledger = _load_ledger()
    acct = ledger.get(address, {})
    acct[symbol] = acct.get(symbol, 0) + amount
    ledger[address] = acct
    _save_ledger(ledger)


def balance_of(address: str) -> Dict[str, int]:
    ledger = _load_ledger()
    return ledger.get(address, {})
