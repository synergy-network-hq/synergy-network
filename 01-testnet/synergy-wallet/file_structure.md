synergy-network-wallet/
├── sdk/
│   ├── javascript/
│   │   └── synergy.js
│   ├── python/
│   │   └── synergy.py
│   └── README.md
├── metamask-snap/
│   ├── src/
│   │   └── index.js
│   ├── snap.manifest.json
│   └── package.json
├── synergy-wallet-app/
│   ├── desktop/
│   ├── extension/
│   ├── mobile/
│   └── shared/
├── api/
│   ├── uma-resolver.js
│   ├── sns-resolver.js
│   └── (etc.)
└── README.md



====================================================

synergy-wallet/
├── public/
│   ├── index.html
│   └── synergy_logo.png
├── src/
│   ├── api/
│   │   ├── synergyRpc.js           # Synergy testnet RPC functions (to build)
│   │   └── pqcCrypto.js            # JS<->Pyodide bridge (to build)
│   ├── components/
│   │   ├── WalletCreate.js         # Wallet creation/import UI (to build)
│   │   ├── WalletView.js           # Dashboard (to build)
│   │   ├── SendToken.js            # Send tokens UI (to build)
│   │   ├── ReceiveToken.js         # Receive tokens UI (to build)
│   │   ├── SNSManage.js            # SNS management UI (to build)
│   │   ├── UMASection.js           # UMA UI (to build)
│   │   ├── Settings.js             # Settings page (to build)
│   │   └── LoadingSpinner.js       # Loading spinner (to build)
│   ├── context/
│   │   └── WalletProvider.js       # React wallet context (to build)
│   ├── py/
│   │   └── pqc.py                  # Python PQC logic (you just added)
│   ├── utils/
│   │   ├── addressFormat.js        # Bech32m address utils (to build)
│   │   ├── bip39.js                # BIP39 utils (to build)
│   │   └── storage.js              # Encrypted storage (to build)
│   ├── App.js                      # Main app (to build)
│   ├── index.js                    # React entry (to build)
│   └── styles/
│       └── main.css                # Styles (to build)
├── package.json
├── README.md
├── .env
└── requirements-pyodide.txt        # [NEW] Python dependencies for Pyodide (add this)


Key Modules/Files Explained
1. src/api/synergyRpc.js
Handles real RPC requests to the Synergy testnet:

getBalance(address)

sendTransaction(signedTx)

registerSNS(name, address)

resolveSNS(name)

registerUMA(prefix, address)

resolveUMA(prefix, address)

Uses fetch/axios; all calls hit https://rpc.testnet.synergy-network.io

Returns real network data (no stubs!)

2. src/api/pqcCrypto.js
Implements Dilithium-3 (or Kyber) keypair generation and signing

Mnemonic-based backup if hybrid wallet is desired

Key serialization/deserialization for backup/import/export

3. src/utils/addressFormat.js
Bech32m encoding/decoding for Synergy addresses

Handles random selection of sYnQ or sYnU prefix (per Synergy spec)

Ensures 41-character, error-detecting, QR-friendly addresses

4. src/utils/storage.js
Encrypted local storage of wallet/keys (AES/Fernet via password, or Web Crypto)

Never stores unencrypted private keys in browser localStorage/sessionStorage

5. src/components/
Modular React UIs for creating/importing wallet, showing balances, sending/receiving tokens, registering SNS, copying UMA, etc.

App Workflow Overview
Create/import wallet (via PQC keygen or mnemonic)

Wallet state loaded (into context/provider, never left in plain JS variables)

Main dashboard:

Show real Synergy address, balance (queried from network), QR code

Send/receive tokens using signed, real transactions (RPC)

Manage SNS (register/resolve), UMA meta-addresses

Export/backup keys (encrypted)

Settings (theme, logout, dev tools, etc.)

Tech Stack & Key Dependencies
React (create-react-app or Vite recommended)

pqcrypto.js (or WebAssembly) for Dilithium-3/Kyber (may require bridge to Python/rust WASM)

bech32 (for address formatting)

axios/fetch (for RPC)

qrcode.react (for QR code display)

react-router-dom (for navigation)

crypto-js or Web Crypto API (for storage encryption)

Security Best Practices
Never store private keys unencrypted.

PQC keys are always generated and handled in-browser, never sent to server.

Transaction signing always occurs locally.

No sensitive info in logs or network calls.
