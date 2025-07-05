const walletService = require('../../services/wallet');

// Controller for wallet-related endpoints

/**
 * Get wallet balance
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getWalletBalance = async (req, res, next) => {
  try {
    const { address } = req.params;
    const balance = await walletService.getWalletBalance(address);
    
    if (balance === null) {
      return res.status(404).json({ error: 'Address not found' });
    }
    
    res.json({ address, balance });
  } catch (error) {
    next(error);
  }
};

/**
 * Get transaction history for a wallet
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getTransactionHistory = async (req, res, next) => {
  try {
    const { address } = req.params;
    const { page = 1, limit = 20 } = req.query;
    
    const transactions = await walletService.getTransactionHistory(address, page, limit);
    res.json(transactions);
  } catch (error) {
    next(error);
  }
};

/**
 * Create new wallet
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.createWallet = async (req, res, next) => {
  try {
    const wallet = await walletService.createWallet();
    res.status(201).json(wallet);
  } catch (error) {
    next(error);
  }
};

/**
 * Send transaction
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.sendTransaction = async (req, res, next) => {
  try {
    const { fromAddress, toAddress, amount, privateKey, gasPrice } = req.body;
    
    if (!fromAddress || !toAddress || !amount || !privateKey) {
      return res.status(400).json({ error: 'Missing required parameters' });
    }
    
    const transaction = await walletService.sendTransaction(
      fromAddress,
      toAddress,
      amount,
      privateKey,
      gasPrice
    );
    
    res.status(201).json(transaction);
  } catch (error) {
    if (error.message.includes('insufficient funds')) {
      return res.status(400).json({ error: 'Insufficient funds' });
    }
    next(error);
  }
};

/**
 * Get staking information
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getStakingInfo = async (req, res, next) => {
  try {
    const { address } = req.params;
    const stakingInfo = await walletService.getStakingInfo(address);
    
    res.json(stakingInfo);
  } catch (error) {
    next(error);
  }
};

/**
 * Stake tokens
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.stakeTokens = async (req, res, next) => {
  try {
    const { address, amount, privateKey } = req.body;
    
    if (!address || !amount || !privateKey) {
      return res.status(400).json({ error: 'Missing required parameters' });
    }
    
    const result = await walletService.stakeTokens(address, amount, privateKey);
    res.status(201).json(result);
  } catch (error) {
    if (error.message.includes('insufficient funds')) {
      return res.status(400).json({ error: 'Insufficient funds' });
    }
    if (error.message.includes('minimum stake')) {
      return res.status(400).json({ error: error.message });
    }
    next(error);
  }
};

/**
 * Unstake tokens
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.unstakeTokens = async (req, res, next) => {
  try {
    const { address, amount, privateKey } = req.body;
    
    if (!address || !amount || !privateKey) {
      return res.status(400).json({ error: 'Missing required parameters' });
    }
    
    const result = await walletService.unstakeTokens(address, amount, privateKey);
    res.status(201).json(result);
  } catch (error) {
    if (error.message.includes('insufficient staked tokens')) {
      return res.status(400).json({ error: error.message });
    }
    if (error.message.includes('cooldown period')) {
      return res.status(400).json({ error: error.message });
    }
    next(error);
  }
};

/**
 * Get staking rewards
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getStakingRewards = async (req, res, next) => {
  try {
    const { address } = req.params;
    const rewards = await walletService.getStakingRewards(address);
    
    res.json(rewards);
  } catch (error) {
    next(error);
  }
};

/**
 * Get Synergy Naming System (SNS) entries for an address
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getSnsEntries = async (req, res, next) => {
  try {
    const { address } = req.params;
    const entries = await walletService.getSnsEntries(address);
    
    res.json(entries);
  } catch (error) {
    next(error);
  }
};

/**
 * Register SNS name
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.registerSnsName = async (req, res, next) => {
  try {
    const { name, address, duration, privateKey } = req.body;
    
    if (!name || !address || !duration || !privateKey) {
      return res.status(400).json({ error: 'Missing required parameters' });
    }
    
    const result = await walletService.registerSnsName(name, address, duration, privateKey);
    res.status(201).json(result);
  } catch (error) {
    if (error.message.includes('already registered')) {
      return res.status(400).json({ error: error.message });
    }
    if (error.message.includes('insufficient funds')) {
      return res.status(400).json({ error: 'Insufficient funds' });
    }
    next(error);
  }
};

/**
 * Check SNS name availability
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.checkSnsNameAvailability = async (req, res, next) => {
  try {
    const { name } = req.params;
    const available = await walletService.checkSnsNameAvailability(name);
    
    res.json({ name, available });
  } catch (error) {
    next(error);
  }
};
