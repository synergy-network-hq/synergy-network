const Web3 = require('web3');
const config = require('../config');

// Mock data for development - would be replaced with actual blockchain connection
const mockWallets = {
  'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3': {
    balance: '12500.75',
    transactions: [
      { type: 'Received', amount: '500 SYN', from: 'sYnQ8ab...7k2pqrs9', to: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', date: '2025-03-12 14:32:15', status: 'Confirmed', hash: '0x8f7e...3a2b' },
      { type: 'Sent', amount: '250 SYN', from: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', to: 'sYnQ3ef...2j5mnpq4', date: '2025-03-11 09:15:42', status: 'Confirmed', hash: '0x6d5c...9e8f' },
      { type: 'Received', amount: '1000 SYN', from: 'sYnQ9cd...4f7ghij6', to: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', date: '2025-03-10 18:23:05', status: 'Confirmed', hash: '0x2b3a...7e8f' },
      { type: 'Sent', amount: '125 SYN', from: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', to: 'sYnQ5gh...8d1efgh0', date: '2025-03-08 11:05:37', status: 'Confirmed', hash: '0x9e8f...5d6c' },
      { type: 'Staking Reward', amount: '45.75 SYN', from: 'Network', to: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', date: '2025-03-07 00:00:00', status: 'Confirmed', hash: '0x4b5c...1a2b' }
    ],
    staking: {
      staked: '5000',
      rewards: '45.75',
      nextReward: '1.5',
      nextRewardTime: Date.now() + 23 * 60 * 60 * 1000, // 23 hours from now
      apy: '11%'
    },
    sns: [
      { name: 'alice.syn', expiryDate: '2026-03-15', renewable: true },
      { name: 'mycompany.syn', expiryDate: '2026-05-22', renewable: true }
    ]
  },
  'sYnQ8ab...7k2pqrs9': {
    balance: '8750.25',
    transactions: [
      { type: 'Sent', amount: '500 SYN', from: 'sYnQ8ab...7k2pqrs9', to: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', date: '2025-03-12 14:32:15', status: 'Confirmed', hash: '0x8f7e...3a2b' },
      { type: 'Received', amount: '1000 SYN', from: 'sYnQ3ef...2j5mnpq4', to: 'sYnQ8ab...7k2pqrs9', date: '2025-03-09 16:45:23', status: 'Confirmed', hash: '0x7d8e...2c3b' }
    ],
    staking: {
      staked: '2500',
      rewards: '22.50',
      nextReward: '0.75',
      nextRewardTime: Date.now() + 12 * 60 * 60 * 1000, // 12 hours from now
      apy: '11%'
    },
    sns: [
      { name: 'bob.syn', expiryDate: '2026-01-10', renewable: true }
    ]
  }
};

// Mock SNS registry
const mockSnsRegistry = {
  'alice.syn': { owner: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', expiryDate: '2026-03-15', registered: '2025-03-15' },
  'bob.syn': { owner: 'sYnQ8ab...7k2pqrs9', expiryDate: '2026-01-10', registered: '2025-01-10' },
  'mycompany.syn': { owner: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', expiryDate: '2026-05-22', registered: '2025-05-22' }
};

// Service for wallet-related operations
class WalletService {
  constructor() {
    // In a real implementation, this would connect to the blockchain node
    // this.web3 = new Web3(config.nodeUrl);
    this.mockData = {
      wallets: mockWallets,
      snsRegistry: mockSnsRegistry
    };
  }

  /**
   * Get wallet balance
   * @param {string} address - Wallet address
   * @returns {Promise<string|null>} Wallet balance or null if not found
   */
  async getWalletBalance(address) {
    // In a real implementation, this would fetch balance from the blockchain
    const wallet = this.mockData.wallets[address];
    return wallet ? wallet.balance : null;
  }

  /**
   * Get transaction history for a wallet
   * @param {string} address - Wallet address
   * @param {number} page - Page number
   * @param {number} limit - Results per page
   * @returns {Promise<Object>} Paginated transaction history
   */
  async getTransactionHistory(address, page, limit) {
    // In a real implementation, this would fetch transactions from the blockchain
    const wallet = this.mockData.wallets[address];
    
    if (!wallet) {
      return {
        transactions: [],
        total: 0,
        page: parseInt(page),
        limit: parseInt(limit),
        totalPages: 0
      };
    }
    
    const startIndex = (page - 1) * limit;
    const endIndex = page * limit;
    const transactions = wallet.transactions.slice(startIndex, endIndex);
    
    return {
      transactions,
      total: wallet.transactions.length,
      page: parseInt(page),
      limit: parseInt(limit),
      totalPages: Math.ceil(wallet.transactions.length / limit)
    };
  }

  /**
   * Create new wallet
   * @returns {Promise<Object>} New wallet details
   */
  async createWallet() {
    // In a real implementation, this would generate a new wallet on the blockchain
    const address = `sYnQ${Math.random().toString(36).substring(2, 6)}...${Math.random().toString(36).substring(2, 9)}`;
    const privateKey = `0x${Math.random().toString(16).substring(2, 66)}`;
    
    // Initialize new wallet in mock data
    this.mockData.wallets[address] = {
      balance: '0',
      transactions: [],
      staking: {
        staked: '0',
        rewards: '0',
        nextReward: '0',
        nextRewardTime: null,
        apy: '11%'
      },
      sns: []
    };
    
    return {
      address,
      privateKey,
      balance: '0',
      message: 'New wallet created successfully. Keep your private key secure!'
    };
  }

  /**
   * Send transaction
   * @param {string} fromAddress - Sender address
   * @param {string} toAddress - Recipient address
   * @param {string} amount - Amount to send
   * @param {string} privateKey - Sender's private key
   * @param {string} gasPrice - Gas price (optional)
   * @returns {Promise<Object>} Transaction result
   */
  async sendTransaction(fromAddress, toAddress, amount, privateKey, gasPrice = '0.002') {
    // In a real implementation, this would send a transaction on the blockchain
    
    // Check if sender wallet exists
    const senderWallet = this.mockData.wallets[fromAddress];
    if (!senderWallet) {
      throw new Error('Sender wallet not found');
    }
    
    // Check if sender has sufficient funds
    const senderBalance = parseFloat(senderWallet.balance);
    const sendAmount = parseFloat(amount);
    const gasFee = parseFloat(gasPrice);
    
    if (senderBalance < sendAmount + gasFee) {
      throw new Error('Insufficient funds');
    }
    
    // Generate transaction hash
    const txHash = `0x${Math.random().toString(16).substr(2, 40)}`;
    
    // Create transaction record
    const timestamp = new Date();
    const transaction = {
      type: 'Sent',
      amount: `${amount} SYN`,
      from: fromAddress,
      to: toAddress,
      date: timestamp.toISOString().replace('T', ' ').substring(0, 19),
      status: 'Confirmed',
      hash: txHash
    };
    
    // Update sender's balance and transaction history
    senderWallet.balance = (senderBalance - sendAmount - gasFee).toFixed(2);
    senderWallet.transactions.unshift(transaction);
    
    // Update recipient's wallet if it exists
    if (this.mockData.wallets[toAddress]) {
      const recipientWallet = this.mockData.wallets[toAddress];
      const recipientBalance = parseFloat(recipientWallet.balance);
      
      recipientWallet.balance = (recipientBalance + sendAmount).toFixed(2);
      recipientWallet.transactions.unshift({
        type: 'Received',
        amount: `${amount} SYN`,
        from: fromAddress,
        to: toAddress,
        date: timestamp.toISOString().replace('T', ' ').substring(0, 19),
        status: 'Confirmed',
        hash: txHash
      });
    }
    
    return {
      hash: txHash,
      from: fromAddress,
      to: toAddress,
      amount: `${amount} SYN`,
      fee: `${gasPrice} SYN`,
      status: 'Confirmed',
      timestamp: timestamp.getTime(),
      blockNumber: Math.floor(Math.random() * 1000000) + 1458000
    };
  }

  /**
   * Get staking information
   * @param {string} address - Wallet address
   * @returns {Promise<Object>} Staking information
   */
  async getStakingInfo(address) {
    // In a real implementation, this would fetch staking data from the blockchain
    const wallet = this.mockData.wallets[address];
    
    if (!wallet) {
      return {
        address,
        staked: '0',
        rewards: '0',
        nextReward: '0',
        nextRewardTime: null,
        apy: '11%'
      };
    }
    
    return {
      address,
      ...wallet.staking
    };
  }

  /**
   * Stake tokens
   * @param {string} address - Wallet address
   * @param {string} amount - Amount to stake
   * @param {string} privateKey - Wallet's private key
   * @returns {Promise<Object>} Staking result
   */
  async stakeTokens(address, amount, privateKey) {
    // In a real implementation, this would stake tokens on the blockchain
    
    // Check if wallet exists
    const wallet = this.mockData.wallets[address];
    if (!wallet) {
      throw new Error('Wallet not found');
    }
    
    // Check if wallet has sufficient funds
    const balance = parseFloat(wallet.balance);
    const stakeAmount = parseFloat(amount);
    
    if (balance < stakeAmount) {
      throw new Error('Insufficient funds');
    }
    
    // Check minimum stake requirement
    if (stakeAmount < 100) {
      throw new Error('Minimum stake amount is 100 SYN');
    }
    
    // Update wallet balance and staking info
    wallet.balance = (balance - stakeAmount).toFixed(2);
    
    const currentStaked = parseFloat(wallet.staking.staked);
    wallet.staking.staked = (currentStaked + stakeAmount).toFixed(2);
    
    // Calculate next reward time if not already staking
    if (currentStaked === 0) {
      wallet.staking.nextRewardTime = Date.now() + 24 * 60 * 60 * 1000; // 24 hours from now
      wallet.staking.nextReward = (stakeAmount * 0.0003).toFixed(2); // 11% APY / 365 days
    } else {
      // Recalculate next reward based on new total
      wallet.staking.nextReward = ((currentStaked + stakeAmount) * 0.0003).toFixed(2);
    }
    
    return {
      address,
      amountStaked: `${stakeAmount} SYN`,
      totalStaked: wallet.staking.staked,
      nextReward: wallet.staking.nextReward,
      nextRewardTime: wallet.staking.nextRewardTime,
      apy: wallet.staking.apy,
      transactionHash: `0x${Math.random().toString(16).substr(2, 40)}`
    };
  }

  /**
   * Unstake tokens
   * @param {string} address - Wallet address
   * @param {string} amount - Amount to unstake
   * @param {string} privateKey - Wallet's private key
   * @returns {Promise<Object>} Unstaking result
   */
  async unstakeTokens(address, amount, privateKey) {
    // In a real implementation, this would unstake tokens on the blockchain
    
    // Check if wallet exists
    const wallet = this.mockData.wallets[address];
    if (!wallet) {
      throw new Error('Wallet not found');
    }
    
    // Check if wallet has sufficient staked tokens
    const stakedAmount = parseFloat(wallet.staking.staked);
    const unstakeAmount = parseFloat(amount);
    
    if (stakedAmount < unstakeAmount) {
      throw new Error('Insufficient staked tokens');
    }
    
    // Update wallet staking info
    wallet.staking.staked = (stakedAmount - unstakeAmount).toFixed(2);
    
    // Simulate 7-day cooldown period
    const cooldownEndTime = Date.now() + 7 * 24 * 60 * 60 * 1000; // 7 days from now
    
    return {
      address,
      amountUnstaked: `${unstakeAmount} SYN`,
      remainingStaked: wallet.staking.staked,
      cooldownEndTime,
      cooldownEndDate: new Date(cooldownEndTime).toISOString().split('T')[0],
      message: 'Tokens will be returned to your wallet after the 7-day cooldown period',
      transactionHash: `0x${Math.random().toString(16).substr(2, 40)}`
    };
  }

  /**
   * Get staking rewards
   * @param {string} address - Wallet address
   * @returns {Promise<Object>} Staking rewards
   */
  async getStakingRewards(address) {
    // In a real implementation, this would fetch rewards from the blockchain
    const wallet = this.mockData.wallets[address];
    
    if (!wallet) {
      return {
        address,
        totalRewards: '0',
        pendingRewards: '0',
        claimedRewards: '0',
        rewardHistory: []
      };
    }
    
    // Mock reward history
    const rewardHistory = wallet.transactions
      .filter(tx => tx.type === 'Staking Reward')
      .map(tx => ({
        amount: tx.amount,
        timestamp: new Date(tx.date).getTime(),
        transactionHash: tx.hash
      }));
    
    return {
      address,
      totalRewards: wallet.staking.rewards,
      pendingRewards: wallet.staking.nextReward,
      claimedRewards: wallet.staking.rewards,
      nextRewardTime: wallet.staking.nextRewardTime,
      rewardHistory
    };
  }

  /**
   * Get Synergy Naming System (SNS) entries for an address
   * @param {string} address - Wallet address
   * @returns {Promise<Array>} SNS entries
   */
  async getSnsEntries(address) {
    // In a real implementation, this would fetch SNS entries from the blockchain
    const wallet = this.mockData.wallets[address];
    
    if (!wallet || !wallet.sns) {
      return [];
    }
    
    return wallet.sns;
  }

  /**
   * Register SNS name
   * @param {string} name - SNS name to register
   * @param {string} address - Wallet address
   * @param {number} duration - Registration duration in years
   * @param {string} privateKey - Wallet's private key
   * @returns {Promise<Object>} Registration result
   */
  async registerSnsName(name, address, duration, privateKey) {
    // In a real implementation, this would register an SNS name on the blockchain
    
    // Check if wallet exists
    const wallet = this.mockData.wallets[address];
    if (!wallet) {
      throw new Error('Wallet not found');
    }
    
    // Check if name is already registered
    if (this.mockData.snsRegistry[name]) {
      throw new Error('Name is already registered');
    }
    
    // Calculate registration cost
    const baseCost = 10; // 10 SYN per year
    const totalCost = baseCost * duration;
    
    // Check if wallet has sufficient funds
    const balance = parseFloat(wallet.balance);
    if (balance < totalCost) {
      throw new Error('Insufficient funds');
    }
    
    // Update wallet balance
    wallet.balance = (balance - totalCost).toFixed(2);
    
    // Calculate expiry date
    const now = new Date();
    const expiryDate = new Date(now);
    expiryDate.setFullYear(expiryDate.getFullYear() + duration);
    const expiryDateStr = expiryDate.toISOString().split('T')[0];
    
    // Register name
    this.mockData.snsRegistry[name] = {
      owner: address,
      expiryDate: expiryDateStr,
      registered: now.toISOString().split('T')[0]
    };
    
    // Add to wallet's SNS entries
    if (!wallet.sns) {
      wallet.sns = [];
    }
    
    wallet.sns.push({
      name,
      expiryDate: expiryDateStr,
      renewable: true
    });
    
    return {
      name,
      owner: address,
      expiryDate: expiryDateStr,
      duration: `${duration} year${duration > 1 ? 's' : ''}`,
      cost: `${totalCost} SYN`,
      transactionHash: `0x${Math.random().toString(16).substr(2, 40)}`
    };
  }

  /**
   * Check SNS name availability
   * @param {string} name - SNS name to check
   * @returns {Promise<boolean>} Whether the name is available
   */
  async checkSnsNameAvailability(name) {
    // In a real implementation, this would check the blockchain
    return !this.mockData.snsRegistry[name];
  }
}

module.exports = new WalletService();
