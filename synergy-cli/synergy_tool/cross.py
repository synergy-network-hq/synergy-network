from typing import Dict


TRANSFERS = []


def send(chain: str, address: str, amount: int) -> Dict:
    tx = {"chain": chain, "address": address, "amount": amount}
    TRANSFERS.append(tx)
    return tx
