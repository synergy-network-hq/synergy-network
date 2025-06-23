import json
import os
from typing import Optional

SNS_DB = os.path.join(os.path.dirname(__file__), "sns.json")
RESERVED = {"admin", "root", "synergy"}


def _load() -> dict:
    if os.path.exists(SNS_DB):
        with open(SNS_DB) as f:
            return json.load(f)
    return {}


def _save(db: dict) -> None:
    with open(SNS_DB, "w") as f:
        json.dump(db, f, indent=2)


def register(name: str, address: str) -> None:
    if not name.endswith(".syn"):
        raise ValueError("name must end with .syn")
    label = name.split(".")[0]
    if label in RESERVED:
        raise ValueError("reserved name")
    db = _load()
    if name in db:
        raise ValueError("name already registered")
    db[name] = address
    _save(db)


def resolve(name: str) -> Optional[str]:
    return _load().get(name)
