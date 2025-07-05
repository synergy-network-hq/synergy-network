const express = require('express');
const router = express.Router();
const blockchainController = require('../controllers/blockchain');

// GET network stats (blocks, transactions, validators, etc.)
router.get('/stats', blockchainController.getNetworkStats);

// GET blockchain status
router.get('/status', blockchainController.getBlockchainStatus);

// GET current block number
router.get('/block/latest', blockchainController.getLatestBlock);

// GET block by number
router.get('/block/:blockNumber', blockchainController.getBlockByNumber);

// GET transaction by hash
router.get('/transaction/:txHash', blockchainController.getTransactionByHash);

// GET address information
router.get('/address/:address', blockchainController.getAddressInfo);

// GET validator information
router.get('/validator/:address', blockchainController.getValidatorInfo);

// GET validator list
router.get('/validators', blockchainController.getValidatorList);

// GET validator clusters
router.get('/validator-clusters', blockchainController.getValidatorClusters);

// GET synergy points leaderboard
router.get('/synergy-points', blockchainController.getSynergyPointsLeaderboard);

module.exports = router;
