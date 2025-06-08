// Service for ICO-related operations

// Mock data for development - would be replaced with actual database and blockchain connection
const mockIcoDetails = {
  totalSupply: '10,000,000,000 SYN',
  icoAllocation: '500,000,000 SYN (5%)',
  raised: '12,500,000',
  goal: '25,000,000',
  startDate: 'March 15, 2025',
  endDate: 'April 15, 2025',
  minPurchase: '500 SYN',
  maxPurchase: '1,000,000 SYN',
  tiers: [
    { name: 'Private Round', price: '$0.008', allocation: '200,000,000 SYN', status: 'Completed' },
    { name: 'Seed Round', price: '$0.012', allocation: '150,000,000 SYN', status: 'Completed' },
    { name: 'Public Pre-sale', price: '$0.018', allocation: '150,000,000 SYN', status: 'Active' }
  ],
  kycRequired: true,
  kycThreshold: 10000, // KYC required for purchases above 10,000 SYN
  paymentMethods: ['ETH', 'BTC', 'USDT', 'USDC']
};

const mockParticipants = [
  { address: 'sYnQ1zxy8qhj4j59xp5lwkwpd5qws9aygz8pl9m3kmjx3', amount: '25000 SYN', contribution: '$450', paymentMethod: 'ETH', timestamp: Date.now() - 2 * 24 * 60 * 60 * 1000, status: 'Confirmed', kycStatus: 'Approved' },
  { address: 'sYnQ8ab...7k2pqrs9', amount: '50000 SYN', contribution: '$900', paymentMethod: 'BTC', timestamp: Date.now() - 3 * 24 * 60 * 60 * 1000, status: 'Confirmed', kycStatus: 'Approved' },
  { address: 'sYnQ3ef...2j5mnpq4', amount: '5000 SYN', contribution: '$90', paymentMethod: 'USDT', timestamp: Date.now() - 4 * 24 * 60 * 60 * 1000, status: 'Confirmed', kycStatus: 'Not Required' },
  { address: 'sYnQ9cd...4f7ghij6', amount: '100000 SYN', contribution: '$1800', paymentMethod: 'ETH', timestamp: Date.now() - 5 * 24 * 60 * 60 * 1000, status: 'Confirmed', kycStatus: 'Approved' },
  { address: 'sYnQ5gh...8d1efgh0', amount: '7500 SYN', contribution: '$135', paymentMethod: 'USDC', timestamp: Date.now() - 6 * 24 * 60 * 60 * 1000, status: 'Confirmed', kycStatus: 'Not Required' }
];

const mockDistributionSchedule = [
  { phase: 'ICO Completion', percentage: '30%', date: 'April 16, 2025', status: 'Pending' },
  { phase: 'Testnet Launch', percentage: '20%', date: 'May 15, 2025', status: 'Pending' },
  { phase: 'Mainnet Launch', percentage: '50%', date: 'July 1, 2025', status: 'Pending' }
];

const mockKycRequirements = {
  threshold: 10000, // SYN tokens
  requiredDocuments: [
    { type: 'Government ID', description: 'Passport, Driver\'s License, or National ID Card' },
    { type: 'Proof of Address', description: 'Utility bill or bank statement (not older than 3 months)' },
    { type: 'Selfie with ID', description: 'A photo of yourself holding your ID document' }
  ],
  restrictedCountries: ['United States', 'China', 'North Korea', 'Iran', 'Syria'],
  processingTime: '24-48 hours'
};

// Conversion rates (in production would use real-time rates)
const mockConversionRates = {
  ETH: 3000, // 1 ETH = $3000
  BTC: 60000, // 1 BTC = $60000
  USDT: 1,
  USDC: 1
};

class IcoService {
  constructor() {
    this.mockData = {
      icoDetails: mockIcoDetails,
      participants: mockParticipants,
      distributionSchedule: mockDistributionSchedule,
      kycRequirements: mockKycRequirements,
      conversionRates: mockConversionRates
    };
  }

  /**
   * Get ICO details
   * @returns {Promise<Object>} ICO details
   */
  async getIcoDetails() {
    // In a real implementation, this would fetch data from the database
    return this.mockData.icoDetails;
  }

  /**
   * Get ICO statistics
   * @returns {Promise<Object>} ICO statistics
   */
  async getIcoStats() {
    // In a real implementation, this would calculate statistics from the database
    const totalParticipants = this.mockData.participants.length;
    const totalRaised = this.mockData.icoDetails.raised;
    const totalAllocated = this.mockData.participants.reduce((sum, p) => {
      return sum + parseInt(p.amount.replace(/,/g, ''));
    }, 0);
    
    return {
      totalParticipants,
      totalRaised: `$${totalRaised}`,
      totalAllocated: `${totalAllocated.toLocaleString()} SYN`,
      percentageCompleted: (parseInt(totalRaised.replace(/,/g, '')) / parseInt(this.mockData.icoDetails.goal.replace(/,/g, ''))) * 100,
      currentTier: this.mockData.icoDetails.tiers.find(tier => tier.status === 'Active'),
      averageContribution: `$${Math.round(parseInt(totalRaised.replace(/,/g, '')) / totalParticipants).toLocaleString()}`
    };
  }

  /**
   * Get price tiers
   * @returns {Promise<Array>} Price tiers
   */
  async getPriceTiers() {
    // In a real implementation, this would fetch tiers from the database
    return this.mockData.icoDetails.tiers;
  }

  /**
   * Get user's ICO participation
   * @param {string} address - User's wallet address
   * @returns {Promise<Object|null>} Participation details or null if not found
   */
  async getUserParticipation(address) {
    // In a real implementation, this would fetch from the database
    const participation = this.mockData.participants.find(p => p.address === address);
    return participation || null;
  }

  /**
   * Participate in ICO
   * @param {string} address - User's wallet address
   * @param {number} amount - Amount in payment currency
   * @param {string} paymentMethod - Payment method (ETH, BTC, USDT, USDC)
   * @param {string} signature - Transaction signature
   * @returns {Promise<Object>} Participation result
   */
  async participateInIco(address, amount, paymentMethod, signature) {
    // In a real implementation, this would verify the transaction and update the database
    
    // Validate payment method
    if (!this.mockData.icoDetails.paymentMethods.includes(paymentMethod)) {
      throw new Error(`Invalid payment method. Supported methods: ${this.mockData.icoDetails.paymentMethods.join(', ')}`);
    }
    
    // Calculate SYN tokens based on payment amount and method
    const usdValue = amount * this.mockData.conversionRates[paymentMethod];
    const currentPrice = 0.018; // Current price tier
    const synTokens = Math.floor(usdValue / currentPrice);
    
    // Check minimum purchase
    const minPurchase = parseInt(this.mockData.icoDetails.minPurchase.replace(/,/g, ''));
    if (synTokens < minPurchase) {
      throw new Error(`Minimum purchase is ${minPurchase} SYN tokens`);
    }
    
    // Check maximum purchase
    const maxPurchase = parseInt(this.mockData.icoDetails.maxPurchase.replace(/,/g, ''));
    if (synTokens > maxPurchase) {
      throw new Error(`Maximum purchase is ${maxPurchase} SYN tokens per wallet`);
    }
    
    // Check if KYC is required
    const kycRequired = synTokens >= this.mockData.icoDetails.kycThreshold;
    const kycStatus = kycRequired ? 'Required' : 'Not Required';
    
    // Create participation record
    const participation = {
      address,
      amount: `${synTokens.toLocaleString()} SYN`,
      contribution: `$${usdValue.toLocaleString()}`,
      paymentMethod,
      timestamp: Date.now(),
      status: 'Pending',
      kycStatus,
      transactionHash: `0x${Math.random().toString(16).substr(2, 40)}`
    };
    
    // In a real implementation, this would be saved to the database
    this.mockData.participants.push(participation);
    
    return {
      ...participation,
      message: kycRequired ? 'KYC verification required before tokens are distributed' : 'Tokens will be distributed according to the distribution schedule'
    };
  }

  /**
   * Get token distribution schedule
   * @returns {Promise<Array>} Distribution schedule
   */
  async getDistributionSchedule() {
    // In a real implementation, this would fetch from the database
    return this.mockData.distributionSchedule;
  }

  /**
   * Get KYC requirements
   * @returns {Promise<Object>} KYC requirements
   */
  async getKycRequirements() {
    // In a real implementation, this would fetch from the database
    return this.mockData.kycRequirements;
  }

  /**
   * Submit KYC information
   * @param {string} address - User's wallet address
   * @param {string} fullName - User's full name
   * @param {string} dateOfBirth - User's date of birth
   * @param {string} nationality - User's nationality
   * @param {string} idType - Type of ID document
   * @param {string} idNumber - ID document number
   * @param {Array} documentImages - Array of document image URLs
   * @returns {Promise<Object>} KYC submission result
   */
  async submitKyc(address, fullName, dateOfBirth, nationality, idType, idNumber, documentImages) {
    // In a real implementation, this would validate and store KYC data
    
    // Check if user has participated in ICO
    const participation = this.mockData.participants.find(p => p.address === address);
    if (!participation) {
      throw new Error('Address has not participated in the ICO');
    }
    
    // Check if KYC is required
    if (participation.kycStatus === 'Not Required') {
      throw new Error('KYC is not required for this address');
    }
    
    // Check if KYC is already approved
    if (participation.kycStatus === 'Approved') {
      throw new Error('KYC is already approved for this address');
    }
    
    // Check if country is restricted
    if (this.mockData.kycRequirements.restrictedCountries.includes(nationality)) {
      throw new Error(`Citizens from ${nationality} are not eligible to participate in the ICO`);
    }
    
    // Update KYC status
    participation.kycStatus = 'Pending';
    
    // In a real implementation, this would be saved to the database
    
    return {
      address,
      status: 'Pending',
      submissionTime: Date.now(),
      estimatedProcessingTime: this.mockData.kycRequirements.processingTime,
      message: 'Your KYC submission has been received and is being processed'
    };
  }

  /**
   * Get KYC status
   * @param {string} address - User's wallet address
   * @returns {Promise<Object|null>} KYC status or null if not found
   */
  async getKycStatus(address) {
    // In a real implementation, this would fetch from the database
    const participation = this.mockData.participants.find(p => p.address === address);
    
    if (!participation) {
      return null;
    }
    
    return {
      address,
      status: participation.kycStatus,
      lastUpdated: participation.timestamp,
      message: participation.kycStatus === 'Approved' 
        ? 'Your KYC is approved. Tokens will be distributed according to the schedule.' 
        : participation.kycStatus === 'Rejected'
          ? 'Your KYC was rejected. Please contact support for more information.'
          : participation.kycStatus === 'Pending'
            ? 'Your KYC is being processed. This usually takes 24-48 hours.'
            : 'KYC not required for your participation level.'
    };
  }
}

module.exports = new IcoService();
