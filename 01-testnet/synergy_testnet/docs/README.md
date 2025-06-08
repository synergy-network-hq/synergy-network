Synergy Network Testnet

🚀 Overview

The Synergy Network Testnet is a custom blockchain built in Rust, powered by the novel Proof of Synergy (PoSy) consensus mechanism. It serves as the proving ground for validator clustering, interoperability, UMA/SNS integration, post-quantum security, and governance testing prior to mainnet launch.

🔧 Features

✅ Custom Rust blockchain runtime

✅ Proof of Synergy (PoSy) consensus with validator clustering logic

✅ Bech32m address format with support for UMA (Universal Meta Address) and SNS (Synergy Naming System)

✅ JSON-RPC 2.0 interface on localhost:8545 with multiple live methods

✅ Post-quantum cryptography using Dilithium-3 (CRYSTALS standard)

✅ Full dashboard integration with live testnet metrics

✅ CLI commands: start, init, mine, status

📦 Prerequisites

sudo apt install build-essential libssl-dev pkg-config
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustup target add wasm32-unknown-unknown

🛠️ Getting Started

1. Clone the Repository

git clone https://github.com/hootzluh/synergy-testnet.git
cd synergy-testnet

2. Build the Node

cargo build --release --bin synergy-testnet

3. Initialize Configuration

cargo run -- init

This generates:

config/genesis.json

config/network-config.toml

Default token metadata and consensus configs

4. Start the Node

cargo run -- start

This starts the RPC server and launches the PoSy consensus engine.

5. Mine a Block (Manual)

After submitting a transaction:

cargo run -- mine

🌐 JSON-RPC Usage

RPC is available at:

http://localhost:8545

Example: Submit Transaction

curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "tx": {
      "sender": "sYnQ1abc...",
      "receiver": "sYnQ1xyz...",
      "amount": 100,
      "nonce": 1,
      "signature": "sig123"
    }
  }'

Example: Mine a Block

curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"synergy_mineBlock","params":[],"id":1}'

🌌 Repository Structure

synergy-testnet/
├── config/         # Genesis, network, consensus, token metadata
├── src/            # Blockchain, consensus, transaction logic
├── scripts/        # Helper bash scripts (start/stop)
├── docs/           # Developer documentation
├── dependencies/   # Optional 3rd-party libraries
├── tests/          # Unit + integration tests

🚪 Stop the Node

bash scripts/stop-testnet.sh

🌎 Running Additional Nodes

Copy repo to a new machine

Edit config/network-config.toml:

Unique listen.p2p port

Add a bootnodes entry pointing to your main node

Use the same genesis.json

Run: cargo run -- start

🤝 Contributing

Open PRs or issues via GitHub. Please clearly describe features, bugs, or patches. Follow Rust formatting and logic style conventions.

📜 License

MIT License — see the LICENSE file.
