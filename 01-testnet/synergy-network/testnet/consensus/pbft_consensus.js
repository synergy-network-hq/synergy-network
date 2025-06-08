/**
 * Practical Byzantine Fault Tolerance (PBFT) Consensus Implementation
 * Adapted for Synergy Network's Proof of Synergy mechanism
 */

class PBFTConsensus {
  constructor(validatorCluster) {
    this.validatorCluster = validatorCluster;
    this.messages = new Map(); // Map to store consensus messages
    this.prepareMessages = new Map(); // Map to store prepare messages
    this.commitMessages = new Map(); // Map to store commit messages
    this.viewNumber = 0; // Current view number
    this.sequenceNumber = 0; // Current sequence number
    this.state = 'idle'; // Current state of the consensus
    this.currentProposer = null; // Current block proposer
    this.currentProposal = null; // Current block proposal
    this.preparedProposals = new Set(); // Set of prepared proposals
    this.committedProposals = new Set(); // Set of committed proposals
    this.timeout = 10000; // Timeout for consensus phases (in ms)
    this.timeoutHandles = new Map(); // Map to store timeout handles
  }

  /**
   * Start consensus for a new block proposal
   * @param {string} proposer - Address of the proposer
   * @param {Object} proposal - Block proposal
   * @param {Array} validators - List of validators in the cluster
   * @returns {Promise<Object>} Consensus result
   */
  async startConsensus(proposer, proposal, validators) {
    console.log(`Starting PBFT consensus for proposal from ${proposer}`);
    
    // Reset state for new consensus round
    this.resetConsensusState();
    
    // Set current proposer and proposal
    this.currentProposer = proposer;
    this.currentProposal = proposal;
    this.sequenceNumber++;
    this.state = 'pre-prepare';
    
    // Broadcast pre-prepare message
    this.broadcastPrePrepare(proposer, proposal, validators);
    
    // Set timeout for pre-prepare phase
    this.setPhaseTimeout('pre-prepare');
    
    // Return promise that resolves when consensus is reached
    return new Promise((resolve, reject) => {
      this.consensusPromise = { resolve, reject };
    });
  }
  
  /**
   * Reset consensus state for a new round
   */
  resetConsensusState() {
    // Clear all message collections
    this.messages.clear();
    this.prepareMessages.clear();
    this.commitMessages.clear();
    
    // Clear all timeout handles
    this.timeoutHandles.forEach(handle => clearTimeout(handle));
    this.timeoutHandles.clear();
    
    // Reset state
    this.state = 'idle';
    this.currentProposer = null;
    this.currentProposal = null;
  }
  
  /**
   * Broadcast pre-prepare message to all validators in the cluster
   * @param {string} proposer - Address of the proposer
   * @param {Object} proposal - Block proposal
   * @param {Array} validators - List of validators in the cluster
   */
  broadcastPrePrepare(proposer, proposal, validators) {
    console.log('Broadcasting pre-prepare message');
    
    const prePrepareMessage = {
      type: 'pre-prepare',
      viewNumber: this.viewNumber,
      sequenceNumber: this.sequenceNumber,
      proposer,
      proposal,
      timestamp: Date.now()
    };
    
    // In a real implementation, this would be signed by the proposer
    // and broadcast to all validators in the cluster
    
    // For simulation, we'll process it locally
    validators.forEach(validator => {
      if (validator !== proposer) {
        this.handlePrePrepare(prePrepareMessage, validator);
      }
    });
  }
  
  /**
   * Handle pre-prepare message
   * @param {Object} message - Pre-prepare message
   * @param {string} validator - Address of the validator
   */
  handlePrePrepare(message, validator) {
    console.log(`Validator ${validator} received pre-prepare message`);
    
    // Validate message
    if (message.viewNumber !== this.viewNumber) {
      console.log(`Invalid view number: ${message.viewNumber}, expected: ${this.viewNumber}`);
      return;
    }
    
    if (message.sequenceNumber !== this.sequenceNumber) {
      console.log(`Invalid sequence number: ${message.sequenceNumber}, expected: ${this.sequenceNumber}`);
      return;
    }
    
    // Store message
    const messageId = `${message.type}-${message.viewNumber}-${message.sequenceNumber}`;
    this.messages.set(messageId, message);
    
    // Send prepare message
    this.sendPrepare(validator, message.proposal);
  }
  
  /**
   * Send prepare message
   * @param {string} validator - Address of the validator
   * @param {Object} proposal - Block proposal
   */
  sendPrepare(validator, proposal) {
    console.log(`Validator ${validator} sending prepare message`);
    
    const prepareMessage = {
      type: 'prepare',
      viewNumber: this.viewNumber,
      sequenceNumber: this.sequenceNumber,
      validator,
      proposalHash: this.hashProposal(proposal),
      timestamp: Date.now()
    };
    
    // In a real implementation, this would be signed by the validator
    // and broadcast to all validators in the cluster
    
    // For simulation, we'll process it locally
    this.handlePrepare(prepareMessage);
  }
  
  /**
   * Handle prepare message
   * @param {Object} message - Prepare message
   */
  handlePrepare(message) {
    console.log(`Received prepare message from ${message.validator}`);
    
    // Validate message
    if (message.viewNumber !== this.viewNumber) {
      console.log(`Invalid view number: ${message.viewNumber}, expected: ${this.viewNumber}`);
      return;
    }
    
    if (message.sequenceNumber !== this.sequenceNumber) {
      console.log(`Invalid sequence number: ${message.sequenceNumber}, expected: ${this.sequenceNumber}`);
      return;
    }
    
    // Store message
    const messageId = `${message.type}-${message.validator}-${message.viewNumber}-${message.sequenceNumber}`;
    this.prepareMessages.set(messageId, message);
    
    // Check if we have enough prepare messages
    this.checkPrepareConsensus();
  }
  
  /**
   * Check if we have reached consensus in the prepare phase
   */
  checkPrepareConsensus() {
    const validators = this.validatorCluster.getActiveValidators();
    const requiredPrepares = Math.floor(validators.length * 2 / 3) + 1;
    
    // Count prepare messages for current proposal
    const proposalHash = this.hashProposal(this.currentProposal);
    const prepareCount = Array.from(this.prepareMessages.values())
      .filter(msg => msg.proposalHash === proposalHash)
      .length;
    
    console.log(`Prepare count: ${prepareCount}, required: ${requiredPrepares}`);
    
    if (prepareCount >= requiredPrepares) {
      console.log('Prepare consensus reached');
      
      // Mark proposal as prepared
      this.preparedProposals.add(proposalHash);
      
      // Move to commit phase
      this.state = 'commit';
      
      // Clear prepare phase timeout
      if (this.timeoutHandles.has('pre-prepare')) {
        clearTimeout(this.timeoutHandles.get('pre-prepare'));
        this.timeoutHandles.delete('pre-prepare');
      }
      
      // Broadcast commit messages
      this.broadcastCommit(validators, proposalHash);
      
      // Set timeout for commit phase
      this.setPhaseTimeout('commit');
    }
  }
  
  /**
   * Broadcast commit message to all validators in the cluster
   * @param {Array} validators - List of validators in the cluster
   * @param {string} proposalHash - Hash of the proposal
   */
  broadcastCommit(validators, proposalHash) {
    console.log('Broadcasting commit messages');
    
    validators.forEach(validator => {
      const commitMessage = {
        type: 'commit',
        viewNumber: this.viewNumber,
        sequenceNumber: this.sequenceNumber,
        validator,
        proposalHash,
        timestamp: Date.now()
      };
      
      // In a real implementation, this would be signed by the validator
      // and broadcast to all validators in the cluster
      
      // For simulation, we'll process it locally
      this.handleCommit(commitMessage);
    });
  }
  
  /**
   * Handle commit message
   * @param {Object} message - Commit message
   */
  handleCommit(message) {
    console.log(`Received commit message from ${message.validator}`);
    
    // Validate message
    if (message.viewNumber !== this.viewNumber) {
      console.log(`Invalid view number: ${message.viewNumber}, expected: ${this.viewNumber}`);
      return;
    }
    
    if (message.sequenceNumber !== this.sequenceNumber) {
      console.log(`Invalid sequence number: ${message.sequenceNumber}, expected: ${this.sequenceNumber}`);
      return;
    }
    
    // Store message
    const messageId = `${message.type}-${message.validator}-${message.viewNumber}-${message.sequenceNumber}`;
    this.commitMessages.set(messageId, message);
    
    // Check if we have enough commit messages
    this.checkCommitConsensus();
  }
  
  /**
   * Check if we have reached consensus in the commit phase
   */
  checkCommitConsensus() {
    const validators = this.validatorCluster.getActiveValidators();
    const requiredCommits = Math.floor(validators.length * 2 / 3) + 1;
    
    // Count commit messages for current proposal
    const proposalHash = this.hashProposal(this.currentProposal);
    const commitCount = Array.from(this.commitMessages.values())
      .filter(msg => msg.proposalHash === proposalHash)
      .length;
    
    console.log(`Commit count: ${commitCount}, required: ${requiredCommits}`);
    
    if (commitCount >= requiredCommits) {
      console.log('Commit consensus reached');
      
      // Mark proposal as committed
      this.committedProposals.add(proposalHash);
      
      // Move to finalize phase
      this.state = 'finalize';
      
      // Clear commit phase timeout
      if (this.timeoutHandles.has('commit')) {
        clearTimeout(this.timeoutHandles.get('commit'));
        this.timeoutHandles.delete('commit');
      }
      
      // Finalize consensus
      this.finalizeConsensus();
    }
  }
  
  /**
   * Finalize consensus and resolve promise
   */
  finalizeConsensus() {
    console.log('Finalizing consensus');
    
    // Prepare result
    const result = {
      success: true,
      proposal: this.currentProposal,
      proposer: this.currentProposer,
      viewNumber: this.viewNumber,
      sequenceNumber: this.sequenceNumber,
      timestamp: Date.now()
    };
    
    // Resolve consensus promise
    if (this.consensusPromise) {
      this.consensusPromise.resolve(result);
      this.consensusPromise = null;
    }
    
    // Reset state for next round
    this.resetConsensusState();
  }
  
  /**
   * Set timeout for consensus phase
   * @param {string} phase - Consensus phase
   */
  setPhaseTimeout(phase) {
    console.log(`Setting timeout for ${phase} phase`);
    
    // Clear existing timeout if any
    if (this.timeoutHandles.has(phase)) {
      clearTimeout(this.timeoutHandles.get(phase));
    }
    
    // Set new timeout
    const handle = setTimeout(() => {
      console.log(`Timeout for ${phase} phase`);
      this.handlePhaseTimeout(phase);
    }, this.timeout);
    
    this.timeoutHandles.set(phase, handle);
  }
  
  /**
   * Handle timeout for consensus phase
   * @param {string} phase - Consensus phase
   */
  handlePhaseTimeout(phase) {
    console.log(`Handling timeout for ${phase} phase`);
    
    // Increment view number
    this.viewNumber++;
    
    // Reject consensus promise
    if (this.consensusPromise) {
      this.consensusPromise.reject(new Error(`Timeout in ${phase} phase`));
      this.consensusPromise = null;
    }
    
    // Reset state for next round
    this.resetConsensusState();
  }
  
  /**
   * Hash a proposal for message verification
   * @param {Object} proposal - Block proposal
   * @returns {string} Hash of the proposal
   */
  hashProposal(proposal) {
    // In a real implementation, this would compute a cryptographic hash
    // For simulation, we'll use a simple string representation
    return `hash-${proposal.number}-${proposal.timestamp}`;
  }
  
  /**
   * Get current consensus state
   * @returns {Object} Current consensus state
   */
  getConsensusState() {
    return {
      state: this.state,
      viewNumber: this.viewNumber,
      sequenceNumber: this.sequenceNumber,
      currentProposer: this.currentProposer,
      prepareCount: this.prepareMessages.size,
      commitCount: this.commitMessages.size,
      preparedProposals: this.preparedProposals.size,
      committedProposals: this.committedProposals.size
    };
  }
}

module.exports = PBFTConsensus;
