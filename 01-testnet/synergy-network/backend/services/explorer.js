const Web3 = require('web3');
const config = require('../config');

// Mock data for development - would be replaced with actual blockchain connection
const mockBlocks = [
  { number: 1458732, timestamp: Date.now() - 2000, validator: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', transactions: 156, size: '1.2 MB', hash: '0x8f7e...3a2b', gasUsed: '45%', difficulty: '3.2T', totalDifficulty: '12.5P' },
  { number: 1458731, timestamp: Date.now() - 5000, validator: 'sYnQ8ab...7k2pqrs9', transactions: 142, size: '1.1 MB', hash: '0x6d5c...9e8f', gasUsed: '38%', difficulty: '3.2T', totalDifficulty: '12.5P' },
  { number: 1458730, timestamp: Date.now() - 8000, validator: 'sYnQ3ef...2j5mnpq4', transactions: 168, size: '1.3 MB', hash: '0x2b3a...7e8f', gasUsed: '52%', difficulty: '3.2T', totalDifficulty: '12.5P' },
  { number: 1458729, timestamp: Date.now() - 11000, validator: 'sYnQ9cd...4f7ghij6', transactions: 131, size: '1.0 MB', hash: '0x9e8f...5d6c', gasUsed: '35%', difficulty: '3.2T', totalDifficulty: '12.5P' },
  { number: 1458728, timestamp: Date.now() - 14000, validator: 'sYnQ5gh...8d1efgh0', transactions: 149, size: '1.2 MB', hash: '0x4b5c...1a2b', gasUsed: '41%', difficulty: '3.2T', totalDifficulty: '12.5P' },
  { number: 1458727, timestamp: Date.now() - 17000, validator: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', transactions: 163, size: '1.3 MB', hash: '0x3a4b...5c6d', gasUsed: '48%', difficulty: '3.2T', totalDifficulty: '12.5P' },
  { number: 1458726, timestamp: Date.now() - 20000, validator: 'sYnQ8ab...7k2pqrs9', transactions: 145, size: '1.1 MB', hash: '0x2a3b...4c5d', gasUsed: '39%', difficulty: '3.2T', totalDifficulty: '12.5P' },
  { number: 1458725, timestamp: Date.now() - 23000, validator: 'sYnQ3ef...2j5mnpq4', transactions: 171, size: '1.4 MB', hash: '0x1a2b...3c4d', gasUsed: '53%', difficulty: '3.2T', totalDifficulty: '12.5P' },
  { number: 1458724, timestamp: Date.now() - 26000, validator: 'sYnQ9cd...4f7ghij6', transactions: 138, size: '1.1 MB', hash: '0x0a1b...2c3d', gasUsed: '37%', difficulty: '3.2T', totalDifficulty: '12.5P' },
  { number: 1458723, timestamp: Date.now() - 29000, validator: 'sYnQ5gh...8d1efgh0', transactions: 152, size: '1.2 MB', hash: '0xf1e2...d3c4', gasUsed: '42%', difficulty: '3.2T', totalDifficulty: '12.5P' },
];

const mockTransactions = [
  { hash: '0x8f7e...3a2b', from: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', to: 'sYnQ8ab...7k2pqrs9', amount: '125.5 SYN', status: 'Confirmed', timestamp: Date.now() - 15000, blockNumber: 1458732, gasUsed: '21000', gasPrice: '0.002', fee: '0.042', type: 'Transfer' },
  { hash: '0x6d5c...9e8f', from: 'sYnQ3ef...2j5mnpq4', to: 'sYnQ9cd...4f7ghij6', amount: '500.0 SYN', status: 'Confirmed', timestamp: Date.now() - 42000, blockNumber: 1458731, gasUsed: '21000', gasPrice: '0.002', fee: '0.042', type: 'Transfer' },
  { hash: '0x2b3a...7e8f', from: 'sYnQ5gh...8d1efgh0', to: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', amount: '75.25 SYN', status: 'Confirmed', timestamp: Date.now() - 60000, blockNumber: 1458730, gasUsed: '21000', gasPrice: '0.002', fee: '0.042', type: 'Transfer' },
  { hash: '0x9e8f...5d6c', from: 'sYnQ8ab...7k2pqrs9', to: 'sYnQ3ef...2j5mnpq4', amount: '1,000.0 SYN', status: 'Confirmed', timestamp: Date.now() - 120000, blockNumber: 1458729, gasUsed: '21000', gasPrice: '0.002', fee: '0.042', type: 'Transfer' },
  { hash: '0x4b5c...1a2b', from: 'sYnQ9cd...4f7ghij6', to: 'sYnQ5gh...8d1efgh0', amount: '250.75 SYN', status: 'Confirmed', timestamp: Date.now() - 180000, blockNumber: 1458728, gasUsed: '21000', gasPrice: '0.002', fee: '0.042', type: 'Transfer' },
  { hash: '0x3a4b...5c6d', from: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', to: 'System', amount: '5000.0 SYN', status: 'Confirmed', timestamp: Date.now() - 240000, blockNumber: 1458727, gasUsed: '35000', gasPrice: '0.002', fee: '0.070', type: 'Stake' },
  { hash: '0x2a3b...4c5d', from: 'System', to: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', amount: '45.75 SYN', status: 'Confirmed', timestamp: Date.now() - 300000, blockNumber: 1458726, gasUsed: '15000', gasPrice: '0.002', fee: '0.030', type: 'Reward' },
  { hash: '0x1a2b...3c4d', from: 'sYnQ8ab...7k2pqrs9', to: 'SNS Registry', amount: '10.0 SYN', status: 'Confirmed', timestamp: Date.now() - 360000, blockNumber: 1458725, gasUsed: '45000', gasPrice: '0.002', fee: '0.090', type: 'SNS Registration' },
  { hash: '0x0a1b...2c3d', from: 'sYnQ3ef...2j5mnpq4', to: 'ICO Contract', amount: '5000.0 SYN', status: 'Confirmed', timestamp: Date.now() - 420000, blockNumber: 1458724, gasUsed: '30000', gasPrice: '0.002', fee: '0.060', type: 'ICO Participation' },
  { hash: '0xf1e2...d3c4', from: 'sYnQ9cd...4f7ghij6', to: 'Governance', amount: '100.0 SYN', status: 'Confirmed', timestamp: Date.now() - 480000, blockNumber: 1458723, gasUsed: '40000', gasPrice: '0.002', fee: '0.080', type: 'Vote' },
];

const mockAddresses = {
  'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3': {
    balance: '12500.75',
    transactions: 45,
    firstSeen: Date.now() - 30 * 24 * 60 * 60 * 1000, // 30 days ago
    lastSeen: Date.now() - 2 * 60 * 1000, // 2 minutes ago
    isValidator: true,
    tokens: [{ symbol: 'SYN', balance: '12500.75' }],
    staked: '5000',
    synergyPoints: 24567,
    snsNames: ['alice.syn', 'mycompany.syn']
  },
  'sYnQ8ab...7k2pqrs9': {
    balance: '8750.25',
    transactions: 32,
    firstSeen: Date.now() - 25 * 24 * 60 * 60 * 1000, // 25 days ago
    lastSeen: Date.now() - 5 * 60 * 1000, // 5 minutes ago
    isValidator: true,
    tokens: [{ symbol: 'SYN', balance: '8750.25' }],
    staked: '2500',
    synergyPoints: 23812,
    snsNames: ['bob.syn']
  }
};

const mockValidators = [
  { address: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', synergyPoints: 24567, staked: 500000, cluster: 2, status: 'Active', uptime: 99.8, blocksProduced: 1245, rewards: 12450 },
  { address: 'sYnQ8ab...7k2pqrs9', synergyPoints: 23812, staked: 450000, cluster: 5, status: 'Active', uptime: 99.5, blocksProduced: 1187, rewards: 11870 },
  { address: 'sYnQ3ef...2j5mnpq4', synergyPoints: 22945, staked: 400000, cluster: 1, status: 'Active', uptime: 99.2, blocksProduced: 1098, rewards: 10980 },
  { address: 'sYnQ9cd...4f7ghij6', synergyPoints: 21678, staked: 350000, cluster: 3, status: 'Active', uptime: 98.9, blocksProduced: 1032, rewards: 10320 },
  { address: 'sYnQ5gh...8d1efgh0', synergyPoints: 20543, staked: 300000, cluster: 4, status: 'Syncing', uptime: 97.5, blocksProduced: 978, rewards: 9780 },
];

const mockNetworkStats = {
  blocks: 1458732,
  transactions: 32567891,
  validators: 128,
  activeNodes: 512,
  blockTime: 2.5,
  tps: 4200,
  synPoints: 2467890,
  activeClusters: 12,
  lastBlock: Date.now(),
  difficulty: '3.2T',
  stakingAPY: '11%',
  circulatingSupply: '2,500,000,000 SYN',
  totalSupply: '10,000,000,000 SYN'
};

const mockTokenMetrics = {
  price: '$0.018',
  marketCap: '$45,000,000',
  volume24h: '$3,250,000',
  circulatingSupply: '2,500,000,000 SYN',
  totalSupply: '10,000,000,000 SYN',
  stakingRatio: '35%',
  stakingAPY: '11%',
  validators: 128,
  holders: 5678
};

// Service for explorer-related operations
class ExplorerService {
  constructor() {
    // In a real implementation, this would connect to the blockchain node
    // this.web3 = new Web3(config.nodeUrl);
    this.mockData = {
      blocks: mockBlocks,
      transactions: mockTransactions,
      addresses: mockAddresses,
      validators: mockValidators,
      networkStats: mockNetworkStats,
      tokenMetrics: mockTokenMetrics
    };
  }

  /**
   * Get recent blocks
   * @param {number} limit - Number of blocks to return
   * @returns {Promise<Array>} Recent blocks
   */
  async getRecentBlocks(limit) {
    // In a real implementation, this would fetch blocks from the blockchain
    return this.mockData.blocks.slice(0, limit);
  }

  /**
   * Get recent transactions
   * @param {number} limit - Number of transactions to return
   * @returns {Promise<Array>} Recent transactions
   */
  async getRecentTransactions(limit) {
    // In a real implementation, this would fetch transactions from the blockchain
    return this.mockData.transactions.slice(0, limit);
  }

  /**
   * Get block details
   * @param {number} blockNumber - Block number
   * @returns {Promise<Object|null>} Block details or null if not found
   */
  async getBlockDetails(blockNumber) {
    // In a real implementation, this would fetch the block from the blockchain
    const block = this.mockData.blocks.find(b => b.number.toString() === blockNumber.toString());
    
    if (!block) {
      return null;
    }
    
    // Get transactions for this block
    const transactions = this.mockData.transactions.filter(tx => tx.blockNumber.toString() === blockNumber.toString());
    
    return {
      ...block,
      transactions
    };
  }

  /**
   * Get transaction details
   * @param {string} txHash - Transaction hash
   * @returns {Promise<Object|null>} Transaction details or null if not found
   */
  async getTransactionDetails(txHash) {
    // In a real implementation, this would fetch the transaction from the blockchain
    const transaction = this.mockData.transactions.find(tx => tx.hash === txHash);
    return transaction || null;
  }

  /**
   * Get address details
   * @param {string} address - Wallet address
   * @returns {Promise<Object|null>} Address details or null if not found
   */
  async getAddressDetails(address) {
    // In a real implementation, this would fetch address data from the blockchain
    const addressData = this.mockData.addresses[address];
    
    if (!addressData) {
      return null;
    }
    
    // Get transactions for this address
    const transactions = this.mockData.transactions.filter(tx => 
      tx.from === address || tx.to === address
    ).slice(0, 10); // Limit to 10 most recent
    
    return {
      ...addressData,
      recentTransactions: transactions
    };
  }

  /**
   * Search for blocks, transactions, addresses
   * @param {string} query - Search query
   * @returns {Promise<Object>} Search results
   */
  async search(query) {
    // In a real implementation, this would search the blockchain
    const results = {
      blocks: [],
      transactions: [],
      addresses: [],
      validators: []
    };
    
    // Search blocks
    if (/^\d+$/.test(query)) {
      const blockNumber = parseInt(query);
      const block = this.mockData.blocks.find(b => b.number === blockNumber);
      if (block) {
        results.blocks.push(block);
      }
    }
    
    // Search transactions
    const txResult = this.mockData.transactions.find(tx => tx.hash.includes(query));
    if (txResult) {
      results.transactions.push(txResult);
    }
    
    // Search addresses
    Object.keys(this.mockData.addresses).forEach(addr => {
      if (addr.includes(query)) {
        results.addresses.push({
          address: addr,
          ...this.mockData.addresses[addr]
        });
      }
    });
    
    // Search validators
    const validatorResult = this.mockData.validators.find(v => v.address.includes(query));
    if (validatorResult) {
      results.validators.push(validatorResult);
    }
    
    return results;
  }

  /**
   * Get network statistics
   * @returns {Promise<Object>} Network statistics
   */
  async getNetworkStats() {
    // In a real implementation, this would fetch stats from the blockchain
    return this.mockData.networkStats;
  }

  /**
   * Get validator details
   * @param {string} address - Validator address
   * @returns {Promise<Object|null>} Validator details or null if not found
   */
  async getValidatorDetails(address) {
    // In a real implementation, this would fetch validator data from the blockchain
    const validator = this.mockData.validators.find(v => v.address === address);
    
    if (!validator) {
      return null;
    }
    
    // Get blocks produced by this validator
    const blocksProduced = this.mockData.blocks.filter(b => b.validator === address);
    
    return {
      ...validator,
      recentBlocks: blocksProduced.slice(0, 5)
    };
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
   * Get token metrics
   * @returns {Promise<Object>} Token metrics
   */
  async getTokenMetrics() {
    // In a real implementation, this would fetch metrics from the blockchain and market data
    return this.mockData.tokenMetrics;
  }
}

module.exports = new ExplorerService();
