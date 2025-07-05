# Synergy Network GUI Utility

This directory contains the Graphical User Interface (GUI) utility for interacting with the Synergy Network.

## File Structure

```
gui_utility/
├── assets/                # Asset files for the GUI utility
│   ├── metal.jpg          # Background texture
│   ├── sn-logo-dark.png   # Dark mode logo
│   ├── sn-logo-light.png  # Light mode logo
│   └── syn.icns           # Application icon
├── synergy_uma/           # Universal Meta Address functionality
│   ├── __init__.py
│   ├── chain_derivations.py
│   ├── pq_keys.py
│   └── sns_api.py
├── utility/               # Core utility functionality
│   ├── __init__.py
│   ├── common/            # Common utilities
│   │   ├── __init__.py
│   │   └── config.py
│   └── core/              # Core functionality
│       ├── __init__.py
│       ├── naming.py
│       ├── token.py
│       └── wallet.py
├── __init__.py
├── index.html             # Main HTML file
├── main.js                # Electron main process
├── package.json           # Node.js dependencies
├── preload.js             # Electron preload script
├── python_bridge.py       # Python bridge for backend functionality
├── renderer.js            # Electron renderer process
└── styles.css             # CSS styles
```

## Installation

1. Ensure you have Node.js 14 or higher and Python 3.8 or higher installed:
   ```
   node --version
   python3 --version
   ```

2. Clone the repository and navigate to the gui_utility directory:
   ```
   git clone https://github.com/hootzluh/synergy_utility.git
   cd synergy_utility/gui_utility
   ```

3. Install the required Node.js dependencies:
   ```
   npm install
   ```

4. Install the required Python dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

The GUI utility provides a graphical interface for interacting with the Synergy Network. You can run the utility using the following command:

```
npm start
```

This will launch the Electron application with the Synergy Network GUI.

### Features

The GUI utility provides the following features:

- **Wallet Functions**
  - Create and manage wallets
  - Import and export wallet keys
  - View wallet balances and transactions

- **Token Functions**
  - Create and manage tokens
  - Mint and burn tokens
  - Transfer tokens between wallets

- **Synergy Naming System**
  - Register domain names on the Synergy Network
  - Look up registered domain names
  - Manage domain name registrations

- **Universal Meta Address Functions**
  - Generate post-quantum cryptography keys
  - Derive chain-specific addresses
  - Manage cross-chain identities

## Building for Distribution

To build the application for distribution, use the following command:

```
npm run build
```

This will create distributable packages for your platform in the `dist` directory.

## Troubleshooting

If you encounter any issues with the GUI utility, please check the following:

1. Ensure you have the correct Node.js and Python versions installed
2. Verify that all dependencies are installed correctly
3. Check the console output for any error messages

If problems persist, please report them to the Synergy Network team.
