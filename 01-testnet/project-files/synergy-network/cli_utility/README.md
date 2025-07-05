# Synergy Network CLI Utility

This is the command-line interface utility tool for the Synergy Network platform. It provides functionality for managing wallets, tokens, and domain names on the Synergy Network.

## Features

- Wallet management (create, import, export, list)
- Token management (create, transfer, approve, mint, burn)
- Domain name management (register, renew, transfer, set records)
- Configuration management

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. Clone the repository or download the CLI utility
2. Navigate to the cli_utility directory
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

To start the CLI utility:

```bash
python cli_app.py
```

### Command Line Arguments

- `--config`: Path to config file
- `--network`: Network to connect to (mainnet, testnet, local)
- `--wallet`: Wallet to use

### Available Commands

Once in the CLI interface, you can use the following commands:

#### General Commands

- `help` - Show available commands
- `exit` or `quit` - Exit the program
- `config` - View or modify configuration

#### Wallet Commands

- `wallet list` - List all wallets
- `wallet create <name>` - Create a new wallet
- `wallet import <name> <private_key>` - Import wallet from private key
- `wallet import_mnemonic <name> <mnemonic>` - Import wallet from mnemonic
- `wallet export <address>` - Export wallet private key
- `wallet export_mnemonic <address>` - Export wallet mnemonic
- `wallet show [address]` - Show wallet details
- `wallet set_default <address>` - Set default wallet
- `wallet rename <address> <new_name>` - Rename wallet
- `wallet delete <address>` - Delete wallet

#### Token Commands

- `token list` - List all tokens
- `token create <name> <symbol> <supply> <decimals> <type>` - Create a new token
- `token transfer <token_id> <to_address> <amount>` - Transfer tokens
- `token approve <token_id> <spender_address> <amount>` - Approve token spending
- `token mint <token_id> <amount>` - Mint tokens
- `token burn <token_id> <amount>` - Burn tokens
- `token show <token_id>` - Show token details

#### Domain Commands

- `domain list` - List all domains owned by the active wallet
- `domain register <name> <duration>` - Register a new domain
- `domain renew <name> <duration>` - Renew domain
- `domain transfer <name> <to_address>` - Transfer domain
- `domain set_resolver <name> <resolver_address>` - Set domain resolver
- `domain set_record <name> <key> <value>` - Set domain record
- `domain show <name>` - Show domain details

## Configuration

The CLI utility uses a configuration file to store settings. You can view and modify the configuration using the `config` command:

- `config show` - Show current configuration
- `config set <key> <value>` - Set configuration value
- `config reset` - Reset configuration to defaults

## Troubleshooting

If you encounter any issues:

1. Ensure you have the correct Python version installed
2. Verify that all dependencies are installed correctly
3. Check the configuration settings
4. Make sure you're connected to the correct network

## License

MIT
