const blockchainService = require('../../services/blockchain');

// Controller for blockchain-related endpoints

/**
 * Get network statistics
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getNetworkStats = async (req, res, next) => {
  try {
    const stats = await blockchainService.getNetworkStats();
    res.json(stats);
  } catch (error) {
    next(error);
  }
};

/**
 * Get blockchain status
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getBlockchainStatus = async (req, res, next) => {
  try {
    const status = await blockchainService.getBlockchainStatus();
    res.json(status);
  } catch (error) {
    next(error);
  }
};

/**
 * Get latest block
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getLatestBlock = async (req, res, next) => {
  try {
    const block = await blockchainService.getLatestBlock();
    res.json(block);
  } catch (error) {
    next(error);
  }
};

/**
 * Get block by number
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getBlockByNumber = async (req, res, next) => {
  try {
    const { blockNumber } = req.params;
    const block = await blockchainService.getBlockByNumber(blockNumber);
    
    if (!block) {
      return res.status(404).json({ error: 'Block not found' });
    }
    
    res.json(block);
  } catch (error) {
    next(error);
  }
};

/**
 * Get transaction by hash
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getTransactionByHash = async (req, res, next) => {
  try {
    const { txHash } = req.params;
    const transaction = await blockchainService.getTransactionByHash(txHash);
    
    if (!transaction) {
      return res.status(404).json({ error: 'Transaction not found' });
    }
    
    res.json(transaction);
  } catch (error) {
    next(error);
  }
};

/**
 * Get address information
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getAddressInfo = async (req, res, next) => {
  try {
    const { address } = req.params;
    const addressInfo = await blockchainService.getAddressInfo(address);
    
    if (!addressInfo) {
      return res.status(404).json({ error: 'Address not found' });
    }
    
    res.json(addressInfo);
  } catch (error) {
    next(error);
  }
};

/**
 * Get validator information
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getValidatorInfo = async (req, res, next) => {
  try {
    const { address } = req.params;
    const validatorInfo = await blockchainService.getValidatorInfo(address);
    
    if (!validatorInfo) {
      return res.status(404).json({ error: 'Validator not found' });
    }
    
    res.json(validatorInfo);
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
    const validators = await blockchainService.getValidatorList(page, limit, sortBy, order);
    res.json(validators);
  } catch (error) {
    next(error);
  }
};

/**
 * Get validator clusters
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getValidatorClusters = async (req, res, next) => {
  try {
    const clusters = await blockchainService.getValidatorClusters();
    res.json(clusters);
  } catch (error) {
    next(error);
  }
};

/**
 * Get synergy points leaderboard
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getSynergyPointsLeaderboard = async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const leaderboard = await blockchainService.getSynergyPointsLeaderboard(page, limit);
    res.json(leaderboard);
  } catch (error) {
    next(error);
  }
};
