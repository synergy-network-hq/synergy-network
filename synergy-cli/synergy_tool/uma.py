from typing import Tuple


def generate(prefix: str, address: str) -> str:
    """Return a simple UMA string."""
    return f"{prefix}:{address}"


def parse(uma: str) -> Tuple[str, str]:
    """Split UMA string into prefix and address."""
    if ":" not in uma:
        raise ValueError("invalid UMA")
    return tuple(uma.split(":", 1))  # type: ignore
