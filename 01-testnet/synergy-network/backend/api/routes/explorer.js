const express = require('express');
const router = express.Router();
const explorerController = require('../controllers/explorer');

// GET recent blocks
router.get('/blocks/recent', explorerController.getRecentBlocks);

// GET recent transactions
router.get('/transactions/recent', explorerController.getRecentTransactions);

// GET block details
router.get('/block/:blockNumber', explorerController.getBlockDetails);

// GET transaction details
router.get('/transaction/:txHash', explorerController.getTransactionDetails);

// GET address details
router.get('/address/:address', explorerController.getAddressDetails);

// GET search (blocks, transactions, addresses)
router.get('/search', explorerController.search);

// GET network statistics
router.get('/stats', explorerController.getNetworkStats);

// GET validator details
router.get('/validator/:address', explorerController.getValidatorDetails);

// GET validator list
router.get('/validators', explorerController.getValidatorList);

// GET token metrics
router.get('/token-metrics', explorerController.getTokenMetrics);

module.exports = router;
