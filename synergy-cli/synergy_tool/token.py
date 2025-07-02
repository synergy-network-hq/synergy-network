import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

TOKENS_DB = os.path.join(os.path.dirname(__file__), "tokens.json")


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
