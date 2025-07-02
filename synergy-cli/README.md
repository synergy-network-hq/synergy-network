# Synergy Network Utility Tool

The **Synergy Network Utility Tool** is a Python based command line interface that demonstrates wallet, token, UMA and SNS operations for the Synergy Network.  It is intentionally lightweight but showcases a modular architecture so more features can be added in the future.  No graphical interface is provided.

## Features

- BIP‑39/44 wallet generation and import
- Encrypted keystore file using `cryptography.Fernet`
- Bech32m Synergy addresses (`sYnQ` prefix)
- Cross‑chain address derivation for Bitcoin, Ethereum and Solana
- Simple local SNS registry stored in `sns.json`
- Placeholder token and cross‑chain commands for demonstration
- `click` based CLI with the following command groups:
  - `wallet` – create, import, export and show addresses
  - `sns` – register and resolve names
  - `token` – create and manage demo tokens
  - `uma` – generate and parse universal meta‑addresses
  - `cross` – mock cross‑chain transfers

## Usage Examples

```
python -m synergy_tool.cli wallet create --path mywallet.json
python -m synergy_tool.cli wallet address --path mywallet.json
python -m synergy_tool.cli sns register alice --path mywallet.json
python -m synergy_tool.cli sns resolve alice
```

This repository is for demonstration purposes only and should not be used for production wallets.
