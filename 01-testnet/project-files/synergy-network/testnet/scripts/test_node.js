#!/usr/bin/env node

/**
 * Synergy Network Testnet Test Script
 * This script tests the functionality of a Synergy Network node
 */

const SynergyNode = require('../node/node');
const PQCrypto = require('../crypto/pqc_crypto');
const fs = require('fs');
const path = require('path');

// Set environment variables
process.env.NETWORK_TYPE = 'testnet';
process.env.NODE_ENV = 'development';

// Welcome message
console.log('\n\x1b[36m╔════════════════════════════════════════════════╗');
console.log('║                                                ║');
console.log('║          SYNERGY NETWORK TEST SUITE            ║');
console.log('║                                                ║');
console.log('╚════════════════════════════════════════════════╝\x1b[0m\n');

// Test results
const testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  skipped: 0
};

// Test suite
async function runTests() {
  try {
    console.log('Initializing test environment...\n');

    // Create test data directory
    const testDataDir = path.join(process.cwd(), 'test_data');
    if (!fs.existsSync(testDataDir)) {
      fs.mkdirSync(testDataDir, { recursive: true });
    }

    // Load configuration
    const config = JSON.parse(fs.readFileSync(path.join(__dirname, '../config/network_config.json'), 'utf8'));

    // Run tests
    await testCryptography(config);
    await testNodeStartup();
    await testConsensus();
    await testTransactions();
    await testValidatorClusters();
    await testSynergyPoints();

    // Print test results
    console.log('\n\x1b[36m╔════════════════════════════════════════════════╗');
    console.log('║                  TEST RESULTS                  ║');
    console.log('╚════════════════════════════════════════════════╝\x1b[0m\n');

    console.log(`Total tests: ${testResults.total}`);
    console.log(`\x1b[32mPassed: ${testResults.passed}\x1b[0m`);
    console.log(`\x1b[31mFailed: ${testResults.failed}\x1b[0m`);
    console.log(`\x1b[33mSkipped: ${testResults.skipped}\x1b[0m\n`);

    if (testResults.failed > 0) {
      console.log('\x1b[31mSome tests failed. Please check the logs for details.\x1b[0m');
      process.exit(1);
    } else {
      console.log('\x1b[32mAll tests passed successfully!\x1b[0m');
    }
  } catch (error) {
    console.error('Error running tests:', error);
    process.exit(1);
  }
}

// Test cryptography module
async function testCryptography(config) {
  console.log('\x1b[36m[TEST SUITE] Post-Quantum Cryptography\x1b[0m');

  try {
    // Initialize PQC module
    const pqc = new PQCrypto(config.cryptography);

    // Test key generation
    await test('Key pair generation', async () => {
      const keyPair = await pqc.generateKeyPair();
      return keyPair && keyPair.publicKey && keyPair.privateKey;
    });

    // Test address derivation
    await test('Address derivation', async () => {
      const keyPair = await pqc.generateKeyPair();
      const address = await pqc.deriveAddress(keyPair.publicKey);
      return address && address.startsWith(config.cryptography.addressPrefixTestnet);
    });

    // Test signing and verification
    await test('Signature creation and verification', async () => {
      const keyPair = await pqc.generateKeyPair();
      const message = 'Test message for signature verification';
      const signature = await pqc.sign(message, keyPair.privateKey);
      const isValid = await pqc.verify(message, signature, keyPair.publicKey);
      return isValid === true;
    });

    // Test KEM
    await test('Key encapsulation mechanism', async () => {
      const kemKeyPair = await pqc.generateKemKeyPair();
      const encapsulation = await pqc.encapsulate(kemKeyPair.publicKey);
      const sharedSecret = await pqc.decapsulate(encapsulation.ciphertext, kemKeyPair.privateKey);
      return sharedSecret && sharedSecret.length > 0;
    });

    // Test address validation
    await test('Address validation', async () => {
      const keyPair = await pqc.generateKeyPair();
      const address = await pqc.deriveAddress(keyPair.publicKey);
      const isValid = await pqc.validateAddress(address);
      return isValid === true;
    });

  } catch (error) {
    console.error('Error in cryptography tests:', error);
    testResults.failed++;
  }
}

// Test node startup
async function testNodeStartup() {
  console.log('\n\x1b[36m[TEST SUITE] Node Startup\x1b[0m');

  try {
    // Test node initialization
    await test('Node initialization', async () => {
      const node = new SynergyNode();
      return node !== null;
    });

    // Test node start
    await test('Node startup', async () => {
      const node = new SynergyNode();
      const result = await node.start();
      return result && result.status === 'running';
    });

  } catch (error) {
    console.error('Error in node startup tests:', error);
    testResults.failed++;
  }
}

// Test consensus mechanism
async function testConsensus() {
  console.log('\n\x1b[36m[TEST SUITE] Consensus Mechanism\x1b[0m');

  try {
    // Import consensus modules
    const PBFTConsensus = require('../consensus/pbft_consensus');
    const ValidatorCluster = require('../consensus/validator_cluster');
    const SynergyPoints = require('../consensus/synergy_points');

    // Initialize modules
    const synergyPoints = new SynergyPoints();
    const validatorCluster = new ValidatorCluster(synergyPoints);
    const pbftConsensus = new PBFTConsensus(validatorCluster);

    // Initialize test validators
    const testValidators = [];
    for (let i = 0; i < 5; i++) {
      const address = `sYnT${i}`.padEnd(20, '0');
      synergyPoints.initializeValidator(address, 1000 + i * 100);
      testValidators.push(address);
    }

    // Form clusters
    await test('Validator cluster formation', async () => {
      const clusters = validatorCluster.formClusters();
      return clusters && clusters.size > 0;
    });

    // Test consensus state
    await test('Consensus state initialization', async () => {
      const state = pbftConsensus.getConsensusState();
      return state && state.state === 'idle';
    });

    // Skip actual consensus test as it requires a full node
    console.log('\x1b[33m[SKIP] Full consensus test (requires running node)\x1b[0m');
    testResults.skipped++;

  } catch (error) {
    console.error('Error in consensus tests:', error);
    testResults.failed++;
  }
}

// Test transactions
async function testTransactions() {
  console.log('\n\x1b[36m[TEST SUITE] Transactions\x1b[0m');

  try {
    // Skip transaction tests as they require a running node
    console.log('\x1b[33m[SKIP] Transaction creation test (requires running node)\x1b[0m');
    console.log('\x1b[33m[SKIP] Transaction submission test (requires running node)\x1b[0m');
    console.log('\x1b[33m[SKIP] Transaction verification test (requires running node)\x1b[0m');
    testResults.skipped += 3;

  } catch (error) {
    console.error('Error in transaction tests:', error);
    testResults.failed++;
  }
}

// Test validator clusters
async function testValidatorClusters() {
  console.log('\n\x1b[36m[TEST SUITE] Validator Clusters\x1b[0m');

  try {
    // Import modules
    const ValidatorCluster = require('../consensus/validator_cluster');
    const SynergyPoints = require('../consensus/synergy_points');
    const TaskPool = require('../consensus/task_pool');

    // Initialize modules
    const synergyPoints = new SynergyPoints();
    const validatorCluster = new ValidatorCluster(synergyPoints);
    const taskPool = new TaskPool();

    // Initialize test validators
    const testValidators = [];
    for (let i = 0; i < 10; i++) {
      const address = `sYnT${i}`.padEnd(20, '0');
      synergyPoints.initializeValidator(address, 1000 + i * 100);
      testValidators.push(address);
    }

    // Test cluster formation
    await test('Cluster formation', async () => {
      const clusters = validatorCluster.formClusters();
      return clusters && clusters.size > 0;
    });

    // Test task assignment
    await test('Task assignment', async () => {
      // Create test tasks
      const tasks = [];
      for (let i = 0; i < 5; i++) {
        const task = taskPool.createTask('transaction', { id: `tx-${i}` }, 1, 5);
        tasks.push(task);
      }

      // Assign tasks
      const assignments = validatorCluster.assignTasks(tasks);
      return tasks.length > 0 && assignments.size > 0;
    });

    // Test cluster rotation
    await test('Cluster rotation', async () => {
      const beforeClusters = validatorCluster.getClusters();
      const afterClusters = validatorCluster.rotateClusters();
      return beforeClusters.length > 0 && afterClusters.size > 0;
    });

  } catch (error) {
    console.error('Error in validator cluster tests:', error);
    testResults.failed++;
  }
}

// Test synergy points
async function testSynergyPoints() {
  console.log('\n\x1b[36m[TEST SUITE] Synergy Points\x1b[0m');

  try {
    // Import module
    const SynergyPoints = require('../consensus/synergy_points');

    // Initialize module
    const synergyPoints = new SynergyPoints();

    // Test validator initialization
    await test('Validator initialization', async () => {
      const address = 'sYnTtest1';
      const points = synergyPoints.initializeValidator(address, 1000);
      return points === 1000;
    });

    // Test point awarding
    await test('Point awarding', async () => {
      const address = 'sYnTtest2';
      synergyPoints.initializeValidator(address, 1000);
      const newPoints = synergyPoints.awardPoints(address, 'task-1', 100, 'transaction');
      return newPoints === 1100;
    });

    // Test point penalization
    await test('Point penalization', async () => {
      const address = 'sYnTtest3';
      synergyPoints.initializeValidator(address, 1000);
      const newPoints = synergyPoints.penalize(address, 200, 'missed block');
      return newPoints === 800;
    });

    // Test decay application
    await test('Point decay', async () => {
      const address = 'sYnTtest4';
      synergyPoints.initializeValidator(address, 1000);
      synergyPoints.applyDecay();
      const points = synergyPoints.getPoints(address);
      return points < 1000; // Should be 990 with 1% decay
    });

    // Test leaderboard
    await test('Leaderboard generation', async () => {
      const leaderboard = synergyPoints.getLeaderboard();
      return Array.isArray(leaderboard) && leaderboard.length > 0;
    });

  } catch (error) {
    console.error('Error in synergy points tests:', error);
    testResults.failed++;
  }
}

// Test helper function
async function test(name, testFn) {
  testResults.total++;

  try {
    console.log(`[TEST] ${name}`);
    const result = await testFn();

    if (result) {
      console.log(`\x1b[32m[PASS] ${name}\x1b[0m`);
      testResults.passed++;
    } else {
      console.log(`\x1b[31m[FAIL] ${name}\x1b[0m`);
      testResults.failed++;
    }
  } catch (error) {
    console.log(`\x1b[31m[FAIL] ${name}: ${error.message}\x1b[0m`);
    testResults.failed++;
  }
}

// Run the tests
runTests().catch(error => {
  console.error('Error running test suite:', error);
  process.exit(1);
});
