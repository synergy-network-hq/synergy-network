const Web3 = require('web3');
const config = require('../config');

// Mock data for development - would be replaced with actual blockchain connection
const mockNetworkStats = {
  blocks: 1458732,
  transactions: 32567891,
  validators: 128,
  activeNodes: 512,
  blockTime: 2.5,
  tps: 4200,
  synPoints: 2467890,
  activeClusters: 12,
  lastBlock: Date.now()
};

const mockBlocks = [
  { number: 1458732, timestamp: Date.now() - 2000, validator: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', transactions: 156, size: '1.2 MB', hash: '0x8f7e...3a2b' },
  { number: 1458731, timestamp: Date.now() - 5000, validator: 'sYnQ8ab...7k2pqrs9', transactions: 142, size: '1.1 MB', hash: '0x6d5c...9e8f' },
  { number: 1458730, timestamp: Date.now() - 8000, validator: 'sYnQ3ef...2j5mnpq4', transactions: 168, size: '1.3 MB', hash: '0x2b3a...7e8f' },
  { number: 1458729, timestamp: Date.now() - 11000, validator: 'sYnQ9cd...4f7ghij6', transactions: 131, size: '1.0 MB', hash: '0x9e8f...5d6c' },
  { number: 1458728, timestamp: Date.now() - 14000, validator: 'sYnQ5gh...8d1efgh0', transactions: 149, size: '1.2 MB', hash: '0x4b5c...1a2b' },
];

const mockTransactions = [
  { hash: '0x8f7e...3a2b', from: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', to: 'sYnQ8ab...7k2pqrs9', amount: '125.5 SYN', status: 'Confirmed', timestamp: Date.now() - 15000, blockNumber: 1458732 },
  { hash: '0x6d5c...9e8f', from: 'sYnQ3ef...2j5mnpq4', to: 'sYnQ9cd...4f7ghij6', amount: '500.0 SYN', status: 'Confirmed', timestamp: Date.now() - 42000, blockNumber: 1458731 },
  { hash: '0x2b3a...7e8f', from: 'sYnQ5gh...8d1efgh0', to: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', amount: '75.25 SYN', status: 'Confirmed', timestamp: Date.now() - 60000, blockNumber: 1458730 },
  { hash: '0x9e8f...5d6c', from: 'sYnQ8ab...7k2pqrs9', to: 'sYnQ3ef...2j5mnpq4', amount: '1,000.0 SYN', status: 'Confirmed', timestamp: Date.now() - 120000, blockNumber: 1458729 },
  { hash: '0x4b5c...1a2b', from: 'sYnQ9cd...4f7ghij6', to: 'sYnQ5gh...8d1efgh0', amount: '250.75 SYN', status: 'Confirmed', timestamp: Date.now() - 180000, blockNumber: 1458728 },
];

const mockValidators = [
  { address: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', synergyPoints: 24567, staked: 500000, cluster: 2, status: 'Active', uptime: 99.8, blocksProduced: 1245, rewards: 12450 },
  { address: 'sYnQ8ab...7k2pqrs9', synergyPoints: 23812, staked: 450000, cluster: 5, status: 'Active', uptime: 99.5, blocksProduced: 1187, rewards: 11870 },
  { address: 'sYnQ3ef...2j5mnpq4', synergyPoints: 22945, staked: 400000, cluster: 1, status: 'Active', uptime: 99.2, blocksProduced: 1098, rewards: 10980 },
  { address: 'sYnQ9cd...4f7ghij6', synergyPoints: 21678, staked: 350000, cluster: 3, status: 'Active', uptime: 98.9, blocksProduced: 1032, rewards: 10320 },
  { address: 'sYnQ5gh...8d1efgh0', synergyPoints: 20543, staked: 300000, cluster: 4, status: 'Syncing', uptime: 97.5, blocksProduced: 978, rewards: 9780 },
];

const mockClusters = [
  { id: 1, validators: 12, totalSynergyPoints: 267890, tasksCompleted: 45678, status: 'Active' },
  { id: 2, validators: 10, totalSynergyPoints: 234567, tasksCompleted: 42345, status: 'Active' },
  { id: 3, validators: 11, totalSynergyPoints: 256789, tasksCompleted: 43456, status: 'Active' },
  { id: 4, validators: 9, totalSynergyPoints: 198765, tasksCompleted: 38765, status: 'Active' },
  { id: 5, validators: 13, totalSynergyPoints: 287654, tasksCompleted: 47654, status: 'Active' },
];

// Service for blockchain-related operations
class BlockchainService {
  constructor() {
    // In a real implementation, this would connect to the blockchain node
    // this.web3 = new Web3(config.nodeUrl);
    this.mockData = {
      networkStats: mockNetworkStats,
      blocks: mockBlocks,
      transactions: mockTransactions,
      validators: mockValidators,
      clusters: mockClusters
    };
  }

  /**
   * Get network statistics
   * @returns {Promise<Object>} Network statistics
   */
  async getNetworkStats() {
    // In a real implementation, this would fetch data from the blockchain
    return this.mockData.networkStats;
  }

  /**
   * Get blockchain status
   * @returns {Promise<Object>} Blockchain status
   */
  async getBlockchainStatus() {
    // In a real implementation, this would check the blockchain node status
    const timeSinceLastBlock = Date.now() - this.mockData.networkStats.lastBlock;
    const status = timeSinceLastBlock < 10000 ? 'Operational' : 'Degraded';
    
    return {
      status,
      lastBlockTime: this.mockData.networkStats.lastBlock,
      nodeVersion: '1.2.5',
      networkId: 'synergy-testnet',
      peers: 24,
      isSyncing: false
    };
  }

  /**
   * Get latest block
   * @returns {Promise<Object>} Latest block
   */
  async getLatestBlock() {
    // In a real implementation, this would fetch the latest block from the blockchain
    return this.mockData.blocks[0];
  }

  /**
   * Get block by number
   * @param {number} blockNumber - Block number
   * @returns {Promise<Object|null>} Block details or null if not found
   */
  async getBlockByNumber(blockNumber) {
    // In a real implementation, this would fetch the block from the blockchain
    const block = this.mockData.blocks.find(b => b.number.toString() === blockNumber.toString());
    return block || null;
  }

  /**
   * Get transaction by hash
   * @param {string} txHash - Transaction hash
   * @returns {Promise<Object|null>} Transaction details or null if not found
   */
  async getTransactionByHash(txHash) {
    // In a real implementation, this would fetch the transaction from the blockchain
    const transaction = this.mockData.transactions.find(tx => tx.hash === txHash);
    return transaction || null;
  }

  /**
   * Get address information
   * @param {string} address - Wallet address
   * @returns {Promise<Object|null>} Address information or null if not found
   */
  async getAddressInfo(address) {
    // In a real implementation, this would fetch address data from the blockchain
    // For now, we'll return mock data if the address matches one of our mock validators
    const isValidator = this.mockData.validators.some(v => v.address === address);
    
    return {
      address,
      balance: '12500.75',
      transactions: 45,
      firstSeen: Date.now() - 30 * 24 * 60 * 60 * 1000, // 30 days ago
      lastSeen: Date.now() - 2 * 60 * 1000, // 2 minutes ago
      isValidator,
      tokens: [
        { symbol: 'SYN', balance: '12500.75' }
      ]
    };
  }

  /**
   * Get validator information
   * @param {string} address - Validator address
   * @returns {Promise<Object|null>} Validator information or null if not found
   */
  async getValidatorInfo(address) {
    // In a real implementation, this would fetch validator data from the blockchain
    const validator = this.mockData.validators.find(v => v.address === address);
    return validator || null;
  }

  /**
   * Get validator list
   * @param {number} page - Page number
   * @param {number} limit - Results per page
   * @param {string} sortBy - Sort field
   * @param {string} order - Sort order ('asc' or 'desc')
   * @returns {Promise<Object>} Paginated validator list
   */
  async getValidatorList(page, limit, sortBy, order) {
    // In a real implementation, this would fetch validators from the blockchain
    const startIndex = (page - 1) * limit;
    const endIndex = page * limit;
    
    // Sort validators
    const sortedValidators = [...this.mockData.validators].sort((a, b) => {
      if (order === 'asc') {
        return a[sortBy] - b[sortBy];
      } else {
        return b[sortBy] - a[sortBy];
      }
    });
    
    const validators = sortedValidators.slice(startIndex, endIndex);
    
    return {
      validators,
      total: this.mockData.validators.length,
      page: parseInt(page),
      limit: parseInt(limit),
      totalPages: Math.ceil(this.mockData.validators.length / limit)
    };
  }

  /**
   * Get validator clusters
   * @returns {Promise<Array>} List of validator clusters
   */
  async getValidatorClusters() {
    // In a real implementation, this would fetch cluster data from the blockchain
    return this.mockData.clusters;
  }

  /**
   * Get synergy points leaderboard
   * @param {number} page - Page number
   * @param {number} limit - Results per page
   * @returns {Promise<Object>} Paginated leaderboard
   */
  async getSynergyPointsLeaderboard(page, limit) {
    // In a real implementation, this would fetch synergy points data from the blockchain
    const startIndex = (page - 1) * limit;
    const endIndex = page * limit;
    
    // Sort validators by synergy points
    const sortedValidators = [...this.mockData.validators].sort((a, b) => b.synergyPoints - a.synergyPoints);
    
    const leaderboard = sortedValidators.slice(startIndex, endIndex);
    
    return {
      leaderboard,
      total: this.mockData.validators.length,
      page: parseInt(page),
      limit: parseInt(limit),
      totalPages: Math.ceil(this.mockData.validators.length / limit)
    };
  }
}

module.exports = new BlockchainService();
