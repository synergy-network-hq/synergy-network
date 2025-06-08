# Synergy Network Testnet

## 🚀 Overview

The **Synergy Network Testnet** is a custom blockchain implementation featuring the novel **Proof of Synergy (PoSy)** consensus mechanism. This testnet serves as the proving ground for interoperability, validator behaviors, wallet generation, and token metadata validation prior to mainnet launch.

---

## 🔧 Features

- ✅ Custom Rust blockchain runtime
- ✅ PoSy consensus algorithm with validator clustering
- ✅ Bech32m address formatting with SNS/UMA integration
- ✅ JSON-RPC API with HTTP POST support
- ✅ RocksDB-based persistent storage
- ✅ Secure key signing using Dilithium-3 PQC

---

## 📦 Prerequisites

Install the required system and Rust toolchain dependencies:

```bash
sudo apt install build-essential libssl-dev pkg-config
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add wasm32-unknown-unknown
```

---

## 🛠️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/synergy-testnet.git
cd synergy-testnet
```

### 2. Build the Node Binary

```bash
cargo build --release --bin synergy-testnet
```

### 3. Start the Local Node

```bash
bash scripts/start-testnet.sh
```

- Genesis: `config/genesis.json`
- Config: `config/network-config.toml`
- Logs saved to `data/logs/testnet.out`

### 4. Stop the Node

```bash
bash scripts/stop-testnet.sh
```

---

## 🌐 Running Additional Nodes

To start a new node and connect it to an existing testnet:

1. Copy the full repository to a second machine.
2. Update `config/network-config.toml` with:
   - A unique `listen.p2p` IP and port
   - `bootnodes` pointing to your initial node's public IP
3. Sync both nodes by running `start-testnet.sh` on each.
4. Use consistent `genesis.json` on all nodes.

---

## 📚 Repository Structure

```
synergy-testnet/
├── config/              # Genesis, network config, token metadata
├── src/                 # Blockchain logic, consensus, RPC
├── scripts/             # Start/stop shell scripts
├── docs/                # Markdown documentation
├── dependencies/        # Dependency templates or packages
├── tests/               # Test cases
```

---

## 🧪 JSON-RPC Endpoint (Manual)

Send raw HTTP POST requests to:

```
http://localhost:8545/broadcast
```

Payload format:

```json
{
  "sender": "sYnQ1...",
  "receiver": "sYnU1...",
  "amount": 1000,
  "nonce": 1,
  "signature": "abc123..."
}
```

---

## 🤝 Contributing

We welcome PRs! Please fork, commit with clarity, and submit a pull request. For bugs or roadmap input, open a GitHub issue.

---

## 📜 License

This project is MIT licensed — see the [LICENSE](../LICENSE) file for full terms.
