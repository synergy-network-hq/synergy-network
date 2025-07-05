const express = require('express');
const router = express.Router();
const walletController = require('../controllers/wallet');

// GET wallet balance
router.get('/balance/:address', walletController.getWalletBalance);

// GET transaction history for a wallet
router.get('/transactions/:address', walletController.getTransactionHistory);

// POST create new wallet
router.post('/create', walletController.createWallet);

// POST send transaction
router.post('/send', walletController.sendTransaction);

// GET staking information
router.get('/staking/:address', walletController.getStakingInfo);

// POST stake tokens
router.post('/stake', walletController.stakeTokens);

// POST unstake tokens
router.post('/unstake', walletController.unstakeTokens);

// GET staking rewards
router.get('/rewards/:address', walletController.getStakingRewards);

// GET Synergy Naming System (SNS) entries for an address
router.get('/sns/:address', walletController.getSnsEntries);

// POST register SNS name
router.post('/sns/register', walletController.registerSnsName);

// GET check SNS name availability
router.get('/sns/available/:name', walletController.checkSnsNameAvailability);

module.exports = router;
