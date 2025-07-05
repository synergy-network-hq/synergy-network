# Synergy Network

A next-generation blockchain platform featuring Proof of Synergy consensus and Post-Quantum Cryptography.

## Project Structure

- **tokenomics/** - Token economics configuration with 10 billion SYN supply
- **web_portal/** - React-based web portal with ICO pre-sale functionality
- **backend/** - Express.js backend services for the web portal
- **testnet/** - Testnet environment with Proof of Synergy consensus

## Quick Start Guide

### Prerequisites

- Node.js v16+ and npm
- Git

### Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/synergy-network.git
cd synergy-network
```

2. Install dependencies for all components:
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

### Running the Testnet Node

1. Start a testnet node:
```bash
cd testnet
node scripts/start_node.js --testnet --data-dir ./data
```

2. Run the test suite to verify functionality:
```bash
cd testnet
node scripts/test_node.js
```

### Running the Web Portal and Backend

1. Start the backend server:
```bash
cd backend
npm start
```

2. In a separate terminal, start the web portal:
```bash
cd web_portal
npm start
```

3. Access the web portal at http://localhost:3000

## Testing the ICO Pre-sale

1. Ensure both the backend and web portal are running
2. Navigate to http://localhost:3000/ico-presale
3. Connect your wallet (for testing, you can use the "Connect" button which will simulate a wallet connection)
4. Enter the amount of SYN tokens you want to purchase
5. Complete the transaction

## Exploring the Blockchain

1. Navigate to http://localhost:3000/explorer
2. View recent blocks, transactions, and validator information
3. Search for specific blocks, transactions, or addresses

## Components Overview

### Token Economics

- Total Supply: 10,000,000,000 SYN
- Distribution: 50% validator rewards, 20% ecosystem development, 15% public sale, 10% team/advisors, 5% reserve
- ICO Pre-sale: Multiple price tiers with KYC requirements

### Web Portal

- Home Page: Project overview and key features
- ICO Pre-sale: Token purchase interface with price tiers
- Dashboard: Network statistics and performance metrics
- Explorer: Block, transaction, and validator explorer
- Wallet: Interface for managing SYN tokens
- Documentation: Comprehensive project documentation

### Backend Services

- Blockchain API: Network stats, block/transaction data, validator information
- ICO API: ICO details, participation, KYC management
- Wallet API: Balance checking, transaction sending, staking
- Explorer API: Block/transaction browsing, search capabilities

### Testnet Environment

- Node Implementation: Core blockchain node with P2P networking
- Consensus Mechanism: Proof of Synergy with PBFT, Synergy Points, and Validator Clusters
- Cryptography: Post-Quantum Cryptography with Dilithium and Kyber

## Troubleshooting

If you encounter any issues, please check the following:

1. Ensure all dependencies are installed correctly
2. Check that the correct Node.js version is being used
3. Verify that no other services are running on the required ports
4. Check the console for error messages

For more detailed information, please refer to the full documentation in the `docs/` directory.
