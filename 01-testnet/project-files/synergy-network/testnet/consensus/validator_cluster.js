/**
 * Validator Cluster Implementation
 * Core component of the Proof of Synergy consensus mechanism
 */

class ValidatorCluster {
  constructor(synergyPoints) {
    this.synergyPoints = synergyPoints;
    this.clusters = new Map(); // Map of cluster IDs to validator clusters
    this.validatorToClusters = new Map(); // Map of validator addresses to their cluster assignments
    this.taskAssignments = new Map(); // Map of task IDs to cluster assignments
    this.clusterPerformance = new Map(); // Map of cluster IDs to performance metrics
    this.nextClusterId = 1; // Next cluster ID to assign
    this.minClusterSize = 3; // Minimum validators per cluster
    this.maxClusterSize = 15; // Maximum validators per cluster
    this.targetClusterSize = 10; // Target validators per cluster
  }

  /**
   * Form validator clusters based on synergy points
   * @returns {Map} Formed clusters
   */
  formClusters() {
    console.log('Forming validator clusters');
    
    // Get all validators sorted by synergy points
    const validators = this.synergyPoints.getLeaderboard();
    
    if (validators.length === 0) {
      console.log('No validators available for clustering');
      return this.clusters;
    }
    
    // Clear existing clusters
    this.clusters.clear();
    this.validatorToClusters.clear();
    
    // Calculate number of clusters based on validator count and target size
    const numClusters = Math.max(1, Math.ceil(validators.length / this.targetClusterSize));
    console.log(`Forming ${numClusters} clusters from ${validators.length} validators`);
    
    // Initialize clusters
    for (let i = 0; i < numClusters; i++) {
      const clusterId = this.nextClusterId++;
      this.clusters.set(clusterId, {
        id: clusterId,
        validators: [],
        tasks: [],
        totalSynergyPoints: 0,
        tasksCompleted: 0,
        performance: 1.0,
        formationTime: Date.now(),
        status: 'active'
      });
    }
    
    // Distribute validators among clusters
    // We'll use a "snake draft" pattern to ensure even distribution of high-point validators
    const clusterIds = Array.from(this.clusters.keys());
    let direction = 1; // 1 for forward, -1 for backward
    let currentIndex = 0;
    
    validators.forEach((validator, index) => {
      // Get current cluster
      const clusterId = clusterIds[currentIndex];
      const cluster = this.clusters.get(clusterId);
      
      // Add validator to cluster
      cluster.validators.push(validator.address);
      cluster.totalSynergyPoints += validator.points;
      
      // Map validator to cluster
      this.validatorToClusters.set(validator.address, clusterId);
      
      // Update index for next assignment
      if (direction === 1) {
        currentIndex++;
        if (currentIndex >= clusterIds.length) {
          currentIndex = clusterIds.length - 1;
          direction = -1;
        }
      } else {
        currentIndex--;
        if (currentIndex < 0) {
          currentIndex = 0;
          direction = 1;
        }
      }
    });
    
    // Initialize performance metrics for each cluster
    for (const [clusterId, cluster] of this.clusters.entries()) {
      this.clusterPerformance.set(clusterId, {
        tasksAssigned: 0,
        tasksCompleted: 0,
        successRate: 1.0,
        averageCompletionTime: 0,
        lastEvaluationTime: Date.now()
      });
    }
    
    console.log(`Formed ${this.clusters.size} clusters`);
    return this.clusters;
  }

  /**
   * Assign tasks to validator clusters
   * @param {Array} tasks - Array of tasks to assign
   * @returns {Map} Task assignments
   */
  assignTasks(tasks) {
    console.log(`Assigning ${tasks.length} tasks to validator clusters`);
    
    if (this.clusters.size === 0) {
      console.log('No clusters available for task assignment');
      return this.taskAssignments;
    }
    
    // Get clusters sorted by performance and capacity
    const sortedClusters = this.getSortedClusters();
    
    // Assign each task to a cluster
    tasks.forEach(task => {
      // Find best cluster for this task
      const cluster = this.findBestClusterForTask(task, sortedClusters);
      
      if (!cluster) {
        console.log(`No suitable cluster found for task ${task.id}`);
        return;
      }
      
      // Assign task to cluster
      console.log(`Assigning task ${task.id} to cluster ${cluster.id}`);
      
      const clusterData = this.clusters.get(cluster.id);
      clusterData.tasks.push(task.id);
      
      // Record assignment
      this.taskAssignments.set(task.id, {
        clusterId: cluster.id,
        task,
        assignedAt: Date.now(),
        status: 'assigned',
        completedAt: null,
        result: null
      });
      
      // Update performance metrics
      const performance = this.clusterPerformance.get(cluster.id);
      performance.tasksAssigned++;
    });
    
    return this.taskAssignments;
  }

  /**
   * Find the best cluster for a given task
   * @param {Object} task - Task to assign
   * @param {Array} sortedClusters - Clusters sorted by performance
   * @returns {Object|null} Best cluster or null if none found
   */
  findBestClusterForTask(task, sortedClusters) {
    // For now, we'll use a simple round-robin assignment
    // In a real implementation, this would consider task type, cluster specialization, etc.
    
    // Find clusters that are not overloaded
    const availableClusters = sortedClusters.filter(cluster => {
      const clusterData = this.clusters.get(cluster.id);
      return clusterData.tasks.length < clusterData.validators.length * 2; // Max 2 tasks per validator
    });
    
    if (availableClusters.length === 0) {
      return null;
    }
    
    // Return the highest-performing available cluster
    return availableClusters[0];
  }

  /**
   * Get clusters sorted by performance and capacity
   * @returns {Array} Sorted clusters
   */
  getSortedClusters() {
    const clusterArray = [];
    
    for (const [clusterId, cluster] of this.clusters.entries()) {
      const performance = this.clusterPerformance.get(clusterId);
      
      clusterArray.push({
        id: clusterId,
        size: cluster.validators.length,
        totalPoints: cluster.totalSynergyPoints,
        tasksAssigned: cluster.tasks.length,
        successRate: performance.successRate,
        score: this.calculateClusterScore(clusterId)
      });
    }
    
    // Sort by score in descending order
    clusterArray.sort((a, b) => b.score - a.score);
    
    return clusterArray;
  }

  /**
   * Calculate performance score for a cluster
   * @param {number} clusterId - Cluster ID
   * @returns {number} Performance score
   */
  calculateClusterScore(clusterId) {
    const cluster = this.clusters.get(clusterId);
    const performance = this.clusterPerformance.get(clusterId);
    
    if (!cluster || !performance) {
      return 0;
    }
    
    // Calculate score based on success rate, capacity, and total synergy points
    const successRateFactor = performance.successRate;
    const capacityFactor = 1 - (cluster.tasks.length / (cluster.validators.length * 2));
    const pointsFactor = Math.min(cluster.totalSynergyPoints / 10000, 1); // Cap at 10,000 points
    
    const score = (successRateFactor * 0.5) + // 50% weight to success rate
                 (capacityFactor * 0.3) + // 30% weight to available capacity
                 (pointsFactor * 0.2); // 20% weight to total synergy points
    
    return score;
  }

  /**
   * Mark a task as completed by a cluster
   * @param {string} taskId - Task ID
   * @param {Object} result - Task result
   * @returns {boolean} Success
   */
  completeTask(taskId, result) {
    console.log(`Marking task ${taskId} as completed`);
    
    // Get task assignment
    const assignment = this.taskAssignments.get(taskId);
    if (!assignment) {
      console.log(`Task ${taskId} not found in assignments`);
      return false;
    }
    
    // Update assignment
    assignment.status = 'completed';
    assignment.completedAt = Date.now();
    assignment.result = result;
    
    // Update cluster
    const clusterId = assignment.clusterId;
    const cluster = this.clusters.get(clusterId);
    
    if (!cluster) {
      console.log(`Cluster ${clusterId} not found`);
      return false;
    }
    
    // Remove task from active tasks
    const taskIndex = cluster.tasks.indexOf(taskId);
    if (taskIndex !== -1) {
      cluster.tasks.splice(taskIndex, 1);
    }
    
    // Update performance metrics
    cluster.tasksCompleted++;
    
    const performance = this.clusterPerformance.get(clusterId);
    performance.tasksCompleted++;
    performance.successRate = performance.tasksCompleted / performance.tasksAssigned;
    
    // Calculate average completion time
    const completionTime = assignment.completedAt - assignment.assignedAt;
    if (performance.averageCompletionTime === 0) {
      performance.averageCompletionTime = completionTime;
    } else {
      performance.averageCompletionTime = 
        (performance.averageCompletionTime * (performance.tasksCompleted - 1) + completionTime) / 
        performance.tasksCompleted;
    }
    
    // Award synergy points to validators in the cluster
    this.awardPointsForTaskCompletion(taskId, clusterId, assignment.task);
    
    return true;
  }

  /**
   * Award synergy points to validators in a cluster for task completion
   * @param {string} taskId - Task ID
   * @param {number} clusterId - Cluster ID
   * @param {Object} task - Task object
   */
  awardPointsForTaskCompletion(taskId, clusterId, task) {
    const cluster = this.clusters.get(clusterId);
    
    if (!cluster) {
      console.log(`Cluster ${clusterId} not found`);
      return;
    }
    
    // Calculate base points based on task difficulty
    const basePoints = task.difficulty || 10;
    
    // Award points to each validator in the cluster
    cluster.validators.forEach(validatorAddress => {
      // Award points based on validator's contribution
      // For now, we'll award equal points to all validators
      this.synergyPoints.awardPoints(
        validatorAddress,
        taskId,
        basePoints,
        task.type
      );
    });
  }

  /**
   * Rotate validator clusters
   * @returns {Map} Updated clusters
   */
  rotateClusters() {
    console.log('Rotating validator clusters');
    
    // In a real implementation, this would:
    // 1. Evaluate cluster performance
    // 2. Dissolve underperforming clusters
    // 3. Reassign validators based on synergy points
    // 4. Form new clusters as needed
    
    // For this implementation, we'll simply re-form all clusters
    return this.formClusters();
  }

  /**
   * Get all clusters
   * @returns {Array} All clusters
   */
  getClusters() {
    const clusters = [];
    
    for (const [clusterId, cluster] of this.clusters.entries()) {
      const performance = this.clusterPerformance.get(clusterId);
      
      clusters.push({
        id: clusterId,
        validators: cluster.validators,
        tasks: cluster.tasks,
        totalSynergyPoints: cluster.totalSynergyPoints,
        tasksCompleted: cluster.tasksCompleted,
        performance: performance.successRate,
        formationTime: cluster.formationTime,
        status: cluster.status
      });
    }
    
    return clusters;
  }

  /**
   * Get a specific cluster
   * @param {number} clusterId - Cluster ID
   * @returns {Object|null} Cluster or null if not found
   */
  getCluster(clusterId) {
    const cluster = this.clusters.get(clusterId);
    
    if (!cluster) {
      return null;
    }
    
    const performance = this.clusterPerformance.get(clusterId);
    
    return {
      id: clusterId,
      validators: cluster.validators,
      tasks: cluster.tasks,
      totalSynergyPoints: cluster.totalSynergyPoints,
      tasksCompleted: cluster.tasksCompleted,
      performance: performance.successRate,
      formationTime: cluster.formationTime,
      status: cluster.status
    };
  }

  /**
   * Get cluster for a specific validator
   * @param {string} validatorAddress - Validator address
   * @returns {Object|null} Cluster or null if not found
   */
  getValidatorCluster(validatorAddress) {
    const clusterId = this.validatorToClusters.get(validatorAddress);
    
    if (!clusterId) {
      return null;
    }
    
    return this.getCluster(clusterId);
  }

  /**
   * Get active validators across all clusters
   * @returns {Array} Active validators
   */
  getActiveValidators() {
    const validators = new Set();
    
    for (const cluster of this.clusters.values()) {
      cluster.validators.forEach(validator => validators.add(validator));
    }
    
    return Array.from(validators);
  }
}

module.exports = ValidatorCluster;
