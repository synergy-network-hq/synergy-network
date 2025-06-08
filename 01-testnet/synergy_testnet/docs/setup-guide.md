# Synergy Network Testnet Setup Guide

This guide walks you through setting up and running a node for the Synergy Network Testnet.

---

## 🛠️ Prerequisites

Ensure the following software is installed:

* Ubuntu 20.04+ (native, WSL2, or compatible Linux)
* Git
* Rust toolchain (installed via rustup)

Install dependencies:

```bash
sudo apt install build-essential libssl-dev pkg-config
```

Install Rust:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustup target add wasm32-unknown-unknown
```

---

## 🚀 Setup Instructions

### 1. Clone the Testnet Repository

```bash
git clone https://github.com/hootzluh/synergy-testnet.git
cd synergy-testnet
```

### 2. Build the Project

```bash
cargo build --release --bin synergy-testnet
```

### 3. Initialize Config Files

```bash
cargo run -- init
```

Creates:

* `config/genesis.json`
* `config/network-config.toml`
* `config/consensus-config.toml`
* `config/token_metadata.json`

### 4. Start the Node

```bash
cargo run -- start
```

* Starts the RPC server on `localhost:8545`
* Begins PoSy consensus execution
* Node will listen for P2P and RPC traffic as configured

### 5. Submit a Transaction

Use a `curl` command or RPC client:

```bash
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "tx": {
      "sender": "sYnQ1sender...",
      "receiver": "sYnQ1receiver...",
      "amount": 100,
      "nonce": 1,
      "signature": "sig..."
    }
  }'
```

### 6. Manually Mine a Block

```bash
cargo run -- mine
```

Or via RPC:

```bash
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"synergy_mineBlock","params":[],"id":1}'
```

### 7. Check Node Status

```bash
cargo run -- status
```

Shows whether the RPC is reachable and the current block height.

### 8. Stop the Node

```bash
bash scripts/stop-testnet.sh
```

---

## 🔧 Running a Secondary Node

To run a second Synergy Testnet node:

1. Copy the full repo to another machine
2. In `config/network-config.toml`:

   * Set a unique `listen.p2p` port
   * Add the main node to `bootnodes`
3. Use identical `genesis.json` across nodes
4. Run:

```bash
cargo run -- start
```

---

## 🔧 Testing & Development

Run unit + integration tests:

```bash
cargo test
```

Check formatting:

```bash
cargo fmt
```

Lint code:

```bash
cargo clippy
```

---

## 📂 Directory Summary

```
synergy-testnet/
├── config/           # Network, consensus, token metadata, genesis
├── src/              # Core blockchain and consensus logic
├── scripts/          # Utility start/stop scripts
├── docs/             # Markdown documentation
├── dependencies/     # Optional 3rd party deps
├── tests/            # All test cases
```

---

## 🤝 Support

Need help? Reach out to the Synergy Network dev team or open a GitHub issue in the testnet repo.
