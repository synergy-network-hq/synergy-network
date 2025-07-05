const explorerService = require('../../services/explorer');

// Controller for explorer-related endpoints

/**
 * Get recent blocks
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getRecentBlocks = async (req, res, next) => {
  try {
    const { limit = 10 } = req.query;
    const blocks = await explorerService.getRecentBlocks(limit);
    res.json(blocks);
  } catch (error) {
    next(error);
  }
};

/**
 * Get recent transactions
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getRecentTransactions = async (req, res, next) => {
  try {
    const { limit = 10 } = req.query;
    const transactions = await explorerService.getRecentTransactions(limit);
    res.json(transactions);
  } catch (error) {
    next(error);
  }
};

/**
 * Get block details
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getBlockDetails = async (req, res, next) => {
  try {
    const { blockNumber } = req.params;
    const block = await explorerService.getBlockDetails(blockNumber);
    
    if (!block) {
      return res.status(404).json({ error: 'Block not found' });
    }
    
    res.json(block);
  } catch (error) {
    next(error);
  }
};

/**
 * Get transaction details
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getTransactionDetails = async (req, res, next) => {
  try {
    const { txHash } = req.params;
    const transaction = await explorerService.getTransactionDetails(txHash);
    
    if (!transaction) {
      return res.status(404).json({ error: 'Transaction not found' });
    }
    
    res.json(transaction);
  } catch (error) {
    next(error);
  }
};

/**
 * Get address details
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getAddressDetails = async (req, res, next) => {
  try {
    const { address } = req.params;
    const addressDetails = await explorerService.getAddressDetails(address);
    
    if (!addressDetails) {
      return res.status(404).json({ error: 'Address not found or has no activity' });
    }
    
    res.json(addressDetails);
  } catch (error) {
    next(error);
  }
};

/**
 * Search for blocks, transactions, addresses
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.search = async (req, res, next) => {
  try {
    const { query } = req.query;
    
    if (!query) {
      return res.status(400).json({ error: 'Search query is required' });
    }
    
    const results = await explorerService.search(query);
    res.json(results);
  } catch (error) {
    next(error);
  }
};

/**
 * Get network statistics
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getNetworkStats = async (req, res, next) => {
  try {
    const stats = await explorerService.getNetworkStats();
    res.json(stats);
  } catch (error) {
    next(error);
  }
};

/**
 * Get validator details
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getValidatorDetails = async (req, res, next) => {
  try {
    const { address } = req.params;
    const validator = await explorerService.getValidatorDetails(address);
    
    if (!validator) {
      return res.status(404).json({ error: 'Validator not found' });
    }
    
    res.json(validator);
  } catch (error) {
    next(error);
  }
};

/**
 * Get validator list
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getValidatorList = async (req, res, next) => {
  try {
    const { page = 1, limit = 20, sortBy = 'synergyPoints', order = 'desc' } = req.query;
    const validators = await explorerService.getValidatorList(page, limit, sortBy, order);
    res.json(validators);
  } catch (error) {
    next(error);
  }
};

/**
 * Get token metrics
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getTokenMetrics = async (req, res, next) => {
  try {
    const metrics = await explorerService.getTokenMetrics();
    res.json(metrics);
  } catch (error) {
    next(error);
  }
};
