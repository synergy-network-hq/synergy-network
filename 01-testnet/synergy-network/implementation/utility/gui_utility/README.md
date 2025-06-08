# Synergy Network GUI Utility

This is the graphical user interface utility tool for the Synergy Network platform. It provides a user-friendly interface for managing wallets, tokens, and domain names on the Synergy Network.

## Features

- Wallet management (create, import, export, list)
- Token management (create, transfer, approve, mint, burn)
- Domain name management (register, renew, transfer, set records)
- Configuration management
- Dark mode interface with Synergy Network branding

## Installation

### Prerequisites

- Node.js v16.0.0 or higher
- npm v7.0.0 or higher
- Python 3.8 or higher (for the Python bridge)

### Installation Steps

1. Clone the repository or download the GUI utility
2. Navigate to the gui_utility directory
3. Install the required dependencies:

```bash
npm install
```

## Usage

To start the GUI utility:

```bash
npm start
```

This will launch the Electron application with the Synergy Network GUI.

## Building the Application

To build the application for distribution:

```bash
npm run build
```

This will create distributable packages in the `dist` directory for your current platform.

## Features Overview

### Wallet Management

- Create new wallets with password protection
- Import existing wallets using private keys or mnemonic phrases
- Export wallet private keys and mnemonic phrases
- View wallet balances and transaction history
- Send and receive SYN tokens

### Token Management

- Create new tokens with customizable parameters
- Transfer tokens between wallets
- Approve token spending for other addresses
- Mint additional tokens (if you're the token owner)
- Burn tokens to reduce supply
- View token details and balances

### Domain Name Management

- Register new .syn domain names
- Renew existing domain registrations
- Transfer domain ownership
- Set domain records and resolvers
- View domain details and expiration dates

## Configuration

The application settings can be configured through the Settings panel in the GUI:

- Network selection (mainnet, testnet, local)
- Theme selection (dark/light mode)
- Language selection
- Advanced RPC settings

## Troubleshooting

If you encounter any issues:

1. Ensure you have the correct Node.js and npm versions installed
2. Verify that all dependencies are installed correctly
3. Check the application logs (available from the Help menu)
4. Make sure you're connected to the correct network

## License

MIT
