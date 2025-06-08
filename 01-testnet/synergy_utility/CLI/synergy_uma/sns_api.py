"""
synergy_uma/sns_api.py

Example synergy naming system, storing name -> synergy address in memory
or in a JSON. In a real environment, you'd do on-chain calls or a real DB.
"""

SNS_STORAGE = {}  # ephemeral in-memory

def register_name(synergy_name: str, synergy_addr: str) -> dict:
    if synergy_name in SNS_STORAGE:
        return {"success": False, "error": f"{synergy_name} is already taken"}
    SNS_STORAGE[synergy_name] = synergy_addr
    return {"success": True, "registered_name": synergy_name, "address": synergy_addr}

def lookup_name(synergy_name: str) -> dict:
    addr = SNS_STORAGE.get(synergy_name)
    if not addr:
        return {"success": False, "error": "Name not found"}
    return {"success": True, "synergy_addr": addr}
