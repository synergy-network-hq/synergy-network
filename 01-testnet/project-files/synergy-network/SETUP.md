# Synergy Network Setup Guide

This document provides detailed instructions for setting up and running the Synergy Network project.

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Node.js**: v16.0.0 or higher
- **NPM**: v7.0.0 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: Minimum 10GB free disk space
- **Network**: Stable internet connection

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/synergy-network.git
cd synergy-network
```

### 2. Install Dependencies

You can install all dependencies at once using the root package.json:

```bash
npm run install-all
```

Or install each component separately:

```bash
# Install testnet dependencies
cd testnet
npm install
cd ..

# Install backend dependencies
cd backend
npm install
cd ..

# Install web portal dependencies
cd web_portal
npm install
cd ..
```

## Running the Components

### Starting the Testnet Node

```bash
npm run start-testnet
```

This will start a Synergy Network node in testnet mode. The node provides:
- JSON-RPC API on port 8545
- WebSocket API on port 8546
- Explorer interface on port 8080

You can interact with the node using the console commands:
- `help` - Show available commands
- `status` - Show node status
- `peers` - Show connected peers
- `blocks` - Show recent blocks
- `transactions` - Show pending transactions
- `validators` - Show active validators
- `exit` or `quit` - Shutdown node

### Starting the Backend Services

```bash
npm run start-backend
```

This will start the backend server on port 5000, providing APIs for:
- Blockchain data
- ICO participation
- Wallet functionality
- Explorer services

### Starting the Web Portal

```bash
npm run start-web
```

This will start the web portal on port 3000. You can access it at http://localhost:3000

### Starting All Services Together

```bash
npm run start-all
```

This will start both the backend services and web portal concurrently.

## Testing

### Running the Test Suite

```bash
npm run test
```

This will run the comprehensive test suite for the Synergy Network testnet, testing:
- Post-Quantum Cryptography
- Node Startup
- Consensus Mechanism
- Validator Clusters
- Synergy Points

## Directory Structure

```
synergy_network/
├── tokenomics/            # Token economics configuration
├── web_portal/            # React-based web portal
│   ├── public/            # Static files
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── assets/        # Images and other assets
│   │   ├── utils/         # Utility functions
│   │   └── services/      # API services
├── backend/               # Express.js backend
│   ├── api/               # API routes and controllers
│   │   ├── routes/        # Route definitions
│   │   └── controllers/   # Controller functions
│   ├── services/          # Business logic
│   ├── models/            # Data models
│   ├── utils/             # Utility functions
│   └── config/            # Configuration files
├── testnet/               # Testnet environment
│   ├── node/              # Node implementation
│   ├── consensus/         # Consensus mechanism
│   ├── crypto/            # Cryptography module
│   ├── config/            # Configuration files
│   └── scripts/           # Utility scripts
└── docs/                  # Documentation
```

## Configuration

### Network Configuration

The network configuration is stored in `testnet/config/network_config.json`. Key parameters include:

- `network.chainId`: Chain ID for the network
- `network.blockTime`: Target block time in seconds
- `tokenomics.totalSupply`: Total supply of SYN tokens (10 billion)
- `consensus.synergyPointsInitial`: Initial synergy points for validators
- `cryptography.signatureScheme`: Post-quantum signature scheme

### Backend Configuration

The backend configuration is stored in `.env` files. Create a `.env` file in the `backend` directory with the following content:

```
PORT=5000
NODE_ENV=development
```

### Web Portal Configuration

The web portal configuration is stored in `.env` files. Create a `.env` file in the `web_portal` directory with the following content:

```
REACT_APP_API_URL=http://localhost:5000/api
PORT=3000
```

## Troubleshooting

### Common Issues

#### Node.js Version Issues

If you encounter errors related to Node.js version, ensure you're using v16.0.0 or higher:

```bash
node -v
```

If needed, upgrade Node.js or use a version manager like nvm.

#### Port Conflicts

If you encounter port conflicts, ensure no other services are running on ports 3000, 5000, 8545, 8546, or 8080.

You can change the ports in the configuration files if needed.

#### Connection Issues

If the web portal cannot connect to the backend, ensure:
1. The backend server is running
2. The REACT_APP_API_URL in the web portal's .env file is correct
3. No firewall or network issues are blocking the connection

## Support

If you encounter any issues not covered in this guide, please:
1. Check the console output for error messages
2. Review the logs in the respective component directories
3. Consult the full documentation in the `docs/` directory
