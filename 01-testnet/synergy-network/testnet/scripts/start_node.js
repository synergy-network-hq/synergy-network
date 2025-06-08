#!/usr/bin/env node

/**
 * Synergy Network Testnet Node Startup Script
 * This script initializes and starts a Synergy Network node
 */

const SynergyNode = require('../node/node');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Parse command line arguments
const args = process.argv.slice(2);
const options = parseArgs(args);

// Set environment variables
process.env.NETWORK_TYPE = options.testnet ? 'testnet' : 'mainnet';
process.env.NODE_ENV = options.production ? 'production' : 'development';

// Welcome message
console.log('\n\x1b[36m╔════════════════════════════════════════════════╗');
console.log('║                                                ║');
console.log('║             SYNERGY NETWORK NODE               ║');
console.log('║                                                ║');
console.log('╚════════════════════════════════════════════════╝\x1b[0m\n');

console.log(`Network: ${process.env.NETWORK_TYPE}`);
console.log(`Environment: ${process.env.NODE_ENV}`);
console.log(`Data directory: ${options.dataDir}`);
console.log(`Log level: ${options.logLevel}\n`);

// Create data directory if it doesn't exist
if (!fs.existsSync(options.dataDir)) {
  console.log(`Creating data directory: ${options.dataDir}`);
  fs.mkdirSync(options.dataDir, { recursive: true });
}

// Initialize and start node
async function startNode() {
  try {
    console.log('Initializing Synergy Network node...');

    // Create node instance
    const node = new SynergyNode();

    // Start node
    const result = await node.start();

    console.log(`\nNode started successfully!`);
    console.log(`Node ID: ${result.nodeId}`);
    console.log(`Address: ${result.address}`);
    console.log(`Status: ${result.status}`);

    // Handle graceful shutdown
    setupShutdownHandlers(node);

    return node;
  } catch (error) {
    console.error('Failed to start node:', error);
    process.exit(1);
  }
}

// Parse command line arguments
function parseArgs(args) {
  const options = {
    dataDir: path.join(process.cwd(), 'data'),
    logLevel: 'info',
    testnet: true,
    production: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--data-dir' && i + 1 < args.length) {
      options.dataDir = args[++i];
    } else if (arg === '--log-level' && i + 1 < args.length) {
      options.logLevel = args[++i];
    } else if (arg === '--testnet') {
      options.testnet = true;
    } else if (arg === '--mainnet') {
      options.testnet = false;
    } else if (arg === '--production') {
      options.production = true;
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    }
  }

  return options;
}

// Print help message
function printHelp() {
  console.log(`
Usage: node start_node.js [options]

Options:
  --data-dir <path>   Set data directory (default: ./data)
  --log-level <level> Set log level: error, warn, info, debug (default: info)
  --testnet           Run on testnet (default)
  --mainnet           Run on mainnet
  --production        Run in production mode
  --help, -h          Show this help message
  `);
}

// Set up shutdown handlers
function setupShutdownHandlers(node) {
  const shutdown = async () => {
    console.log('\nShutting down node...');
    // In a real implementation, this would gracefully stop the node
    // await node.stop();
    process.exit(0);
  };

  // Handle Ctrl+C
  process.on('SIGINT', shutdown);

  // Handle termination signal
  process.on('SIGTERM', shutdown);

  // Handle uncaught exceptions
  process.on('uncaughtException', (error) => {
    console.error('Uncaught exception:', error);
    shutdown();
  });

  // Set up interactive console
  if (process.stdin.isTTY) {
    console.log('\nPress Ctrl+C to shutdown');

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: 'synergy> '
    });

    rl.prompt();

    rl.on('line', async (line) => {
      const cmd = line.trim();

      if (cmd === 'exit' || cmd === 'quit') {
        await shutdown();
      } else if (cmd === 'help') {
        console.log(`
Available commands:
  help                 Show this help message
  status               Show node status
  peers                Show connected peers
  blocks               Show recent blocks
  transactions         Show pending transactions
  validators           Show active validators
  exit, quit           Shutdown node
        `);
      } else if (cmd === 'status') {
        // In a real implementation, this would show actual node status
        console.log('Node is running');
      } else if (cmd === 'peers') {
        // In a real implementation, this would show actual peers
        console.log('Connected to 3 peers');
      } else if (cmd === 'blocks') {
        // In a real implementation, this would show actual blocks
        console.log('Recent blocks: 1458732, 1458731, 1458730');
      } else if (cmd === 'transactions') {
        // In a real implementation, this would show actual transactions
        console.log('5 pending transactions');
      } else if (cmd === 'validators') {
        // In a real implementation, this would show actual validators
        console.log('5 active validators');
      } else if (cmd) {
        console.log(`Unknown command: ${cmd}`);
        console.log('Type "help" for available commands');
      }

      rl.prompt();
    });
  }
}

// Start the node
startNode().catch(error => {
  console.error('Error starting node:', error);
  process.exit(1);
});
