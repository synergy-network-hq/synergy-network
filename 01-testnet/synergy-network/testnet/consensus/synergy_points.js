/**
 * Synergy Points System Implementation
 * Core component of the Proof of Synergy consensus mechanism
 */

class SynergyPoints {
  constructor() {
    this.validators = new Map(); // Map of validator addresses to their synergy points
    this.history = new Map(); // Map to store points history for each validator
    this.tasks = new Map(); // Map to store task completion history
    this.decayFactor = 0.99; // Daily decay factor for points (1% decay)
    this.maxPoints = 100000; // Maximum points a validator can have
    this.initialPoints = 1000; // Initial points for new validators
  }

  /**
   * Initialize a validator with initial synergy points
   * @param {string} address - Validator address
   * @param {number} initialPoints - Initial points to assign (optional)
   * @returns {number} Assigned points
   */
  initializeValidator(address, initialPoints = this.initialPoints) {
    console.log(`Initializing validator ${address} with ${initialPoints} synergy points`);
    
    if (this.validators.has(address)) {
      console.log(`Validator ${address} already initialized`);
      return this.validators.get(address);
    }
    
    // Set initial points
    this.validators.set(address, initialPoints);
    
    // Initialize history
    this.history.set(address, [{
      timestamp: Date.now(),
      action: 'initialize',
      points: initialPoints,
      total: initialPoints
    }]);
    
    // Initialize task completion
    this.tasks.set(address, []);
    
    return initialPoints;
  }

  /**
   * Award points to a validator for task completion
   * @param {string} address - Validator address
   * @param {string} taskId - Task identifier
   * @param {number} points - Points to award
   * @param {string} taskType - Type of task completed
   * @returns {number} New total points
   */
  awardPoints(address, taskId, points, taskType) {
    console.log(`Awarding ${points} points to validator ${address} for task ${taskId}`);
    
    if (!this.validators.has(address)) {
      console.log(`Validator ${address} not initialized, initializing now`);
      this.initializeValidator(address);
    }
    
    // Check if task already completed
    const validatorTasks = this.tasks.get(address);
    if (validatorTasks.some(task => task.taskId === taskId)) {
      console.log(`Task ${taskId} already completed by validator ${address}`);
      return this.validators.get(address);
    }
    
    // Get current points
    let currentPoints = this.validators.get(address);
    
    // Calculate new points, capped at maximum
    let newPoints = Math.min(currentPoints + points, this.maxPoints);
    
    // Update points
    this.validators.set(address, newPoints);
    
    // Record task completion
    validatorTasks.push({
      taskId,
      taskType,
      points,
      timestamp: Date.now()
    });
    
    // Record in history
    const history = this.history.get(address);
    history.push({
      timestamp: Date.now(),
      action: 'award',
      taskId,
      taskType,
      points,
      total: newPoints
    });
    
    return newPoints;
  }

  /**
   * Penalize a validator for misbehavior
   * @param {string} address - Validator address
   * @param {number} points - Points to deduct
   * @param {string} reason - Reason for penalty
   * @returns {number} New total points
   */
  penalize(address, points, reason) {
    console.log(`Penalizing validator ${address} by ${points} points for ${reason}`);
    
    if (!this.validators.has(address)) {
      console.log(`Validator ${address} not initialized, cannot penalize`);
      return 0;
    }
    
    // Get current points
    let currentPoints = this.validators.get(address);
    
    // Calculate new points, minimum 0
    let newPoints = Math.max(currentPoints - points, 0);
    
    // Update points
    this.validators.set(address, newPoints);
    
    // Record in history
    const history = this.history.get(address);
    history.push({
      timestamp: Date.now(),
      action: 'penalize',
      reason,
      points: -points,
      total: newPoints
    });
    
    return newPoints;
  }

  /**
   * Apply daily decay to all validators' points
   * @returns {Map} Updated validators map
   */
  applyDecay() {
    console.log(`Applying daily decay factor of ${this.decayFactor} to all validators`);
    
    for (const [address, points] of this.validators.entries()) {
      // Calculate new points after decay
      const newPoints = Math.floor(points * this.decayFactor);
      
      // Update points
      this.validators.set(address, newPoints);
      
      // Record in history
      const history = this.history.get(address);
      history.push({
        timestamp: Date.now(),
        action: 'decay',
        factor: this.decayFactor,
        points: newPoints - points,
        total: newPoints
      });
    }
    
    return this.validators;
  }

  /**
   * Get points for a specific validator
   * @param {string} address - Validator address
   * @returns {number} Current points
   */
  getPoints(address) {
    if (!this.validators.has(address)) {
      return 0;
    }
    
    return this.validators.get(address);
  }

  /**
   * Get points history for a specific validator
   * @param {string} address - Validator address
   * @returns {Array} Points history
   */
  getHistory(address) {
    if (!this.history.has(address)) {
      return [];
    }
    
    return this.history.get(address);
  }

  /**
   * Get task completion history for a specific validator
   * @param {string} address - Validator address
   * @returns {Array} Task completion history
   */
  getTaskHistory(address) {
    if (!this.tasks.has(address)) {
      return [];
    }
    
    return this.tasks.get(address);
  }

  /**
   * Get all validators sorted by points
   * @returns {Array} Sorted validators
   */
  getLeaderboard() {
    const validators = [];
    
    for (const [address, points] of this.validators.entries()) {
      validators.push({ address, points });
    }
    
    // Sort by points in descending order
    validators.sort((a, b) => b.points - a.points);
    
    return validators;
  }

  /**
   * Get top N validators by points
   * @param {number} n - Number of validators to return
   * @returns {Array} Top N validators
   */
  getTopValidators(n) {
    return this.getLeaderboard().slice(0, n);
  }

  /**
   * Calculate synergy score based on points and other factors
   * @param {string} address - Validator address
   * @returns {number} Synergy score
   */
  calculateSynergyScore(address) {
    if (!this.validators.has(address)) {
      return 0;
    }
    
    const points = this.validators.get(address);
    const tasks = this.tasks.get(address).length;
    const history = this.history.get(address);
    
    // Calculate activity factor based on recent history
    const now = Date.now();
    const recentActivity = history.filter(h => now - h.timestamp < 7 * 24 * 60 * 60 * 1000).length;
    const activityFactor = Math.min(recentActivity / 10, 1); // Cap at 1
    
    // Calculate score based on points, tasks completed, and activity
    const score = (points / this.maxPoints) * 0.7 + // 70% weight to points
                 (tasks / 100) * 0.2 + // 20% weight to tasks completed (capped at 100)
                 activityFactor * 0.1; // 10% weight to recent activity
    
    return Math.min(score, 1); // Normalized between 0 and 1
  }
}

module.exports = SynergyPoints;
