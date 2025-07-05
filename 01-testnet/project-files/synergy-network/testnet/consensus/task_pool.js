/**
 * Task Pool Implementation
 * Core component of the Proof of Synergy consensus mechanism
 */

class TaskPool {
  constructor() {
    this.tasks = new Map(); // Map of task IDs to task objects
    this.pendingTasks = new Set(); // Set of task IDs that are pending assignment
    this.assignedTasks = new Map(); // Map of task IDs to cluster assignments
    this.completedTasks = new Map(); // Map of task IDs to completed task results
    this.taskTypes = new Set(['transaction', 'block', 'validation', 'computation', 'storage']); // Supported task types
    this.difficultyLevels = [1, 2, 5, 10, 20]; // Difficulty levels (points multiplier)
    this.nextTaskId = 1; // Next task ID to assign
  }

  /**
   * Create a new task
   * @param {string} type - Task type
   * @param {Object} data - Task data
   * @param {number} difficulty - Task difficulty (1-5)
   * @param {number} priority - Task priority (1-10)
   * @returns {Object} Created task
   */
  createTask(type, data, difficulty = 1, priority = 5) {
    // Validate task type
    if (!this.taskTypes.has(type)) {
      throw new Error(`Invalid task type: ${type}`);
    }
    
    // Validate difficulty
    if (difficulty < 1 || difficulty > 5) {
      throw new Error(`Invalid difficulty level: ${difficulty}`);
    }
    
    // Validate priority
    if (priority < 1 || priority > 10) {
      throw new Error(`Invalid priority level: ${priority}`);
    }
    
    // Generate task ID
    const taskId = `task-${this.nextTaskId++}`;
    
    // Create task object
    const task = {
      id: taskId,
      type,
      data,
      difficulty: this.difficultyLevels[difficulty - 1],
      priority,
      createdAt: Date.now(),
      status: 'pending'
    };
    
    // Store task
    this.tasks.set(taskId, task);
    this.pendingTasks.add(taskId);
    
    console.log(`Created task ${taskId} of type ${type} with difficulty ${difficulty}`);
    
    return task;
  }

  /**
   * Get available tasks for assignment
   * @param {number} limit - Maximum number of tasks to return
   * @returns {Array} Available tasks
   */
  getAvailableTasks(limit = 10) {
    const availableTasks = [];
    
    // Convert pending tasks to array
    const pendingTaskIds = Array.from(this.pendingTasks);
    
    // Get task objects
    for (const taskId of pendingTaskIds) {
      const task = this.tasks.get(taskId);
      if (task) {
        availableTasks.push(task);
      }
    }
    
    // Sort by priority (high to low) and creation time (oldest first)
    availableTasks.sort((a, b) => {
      if (a.priority !== b.priority) {
        return b.priority - a.priority;
      }
      return a.createdAt - b.createdAt;
    });
    
    // Return limited number of tasks
    return availableTasks.slice(0, limit);
  }

  /**
   * Mark a task as assigned to a cluster
   * @param {string} taskId - Task ID
   * @param {number} clusterId - Cluster ID
   * @returns {boolean} Success
   */
  assignTask(taskId, clusterId) {
    console.log(`Assigning task ${taskId} to cluster ${clusterId}`);
    
    // Check if task exists and is pending
    if (!this.pendingTasks.has(taskId)) {
      console.log(`Task ${taskId} is not pending assignment`);
      return false;
    }
    
    const task = this.tasks.get(taskId);
    if (!task) {
      console.log(`Task ${taskId} not found`);
      return false;
    }
    
    // Update task status
    task.status = 'assigned';
    task.assignedAt = Date.now();
    task.assignedTo = clusterId;
    
    // Move from pending to assigned
    this.pendingTasks.delete(taskId);
    this.assignedTasks.set(taskId, {
      clusterId,
      assignedAt: task.assignedAt
    });
    
    return true;
  }

  /**
   * Mark a task as completed
   * @param {string} taskId - Task ID
   * @param {Object} result - Task result
   * @param {number} clusterId - Cluster ID that completed the task
   * @returns {boolean} Success
   */
  completeTask(taskId, result, clusterId) {
    console.log(`Marking task ${taskId} as completed by cluster ${clusterId}`);
    
    // Check if task exists and is assigned
    const assignment = this.assignedTasks.get(taskId);
    if (!assignment) {
      console.log(`Task ${taskId} is not assigned`);
      return false;
    }
    
    // Check if completed by the assigned cluster
    if (assignment.clusterId !== clusterId) {
      console.log(`Task ${taskId} was assigned to cluster ${assignment.clusterId}, not ${clusterId}`);
      return false;
    }
    
    const task = this.tasks.get(taskId);
    if (!task) {
      console.log(`Task ${taskId} not found`);
      return false;
    }
    
    // Update task status
    task.status = 'completed';
    task.completedAt = Date.now();
    task.result = result;
    
    // Calculate completion time
    const completionTime = task.completedAt - task.assignedAt;
    
    // Move from assigned to completed
    this.assignedTasks.delete(taskId);
    this.completedTasks.set(taskId, {
      result,
      completedAt: task.completedAt,
      completionTime,
      clusterId
    });
    
    return true;
  }

  /**
   * Cancel a task
   * @param {string} taskId - Task ID
   * @param {string} reason - Cancellation reason
   * @returns {boolean} Success
   */
  cancelTask(taskId, reason) {
    console.log(`Cancelling task ${taskId}: ${reason}`);
    
    const task = this.tasks.get(taskId);
    if (!task) {
      console.log(`Task ${taskId} not found`);
      return false;
    }
    
    // Update task status
    task.status = 'cancelled';
    task.cancelledAt = Date.now();
    task.cancellationReason = reason;
    
    // Remove from pending or assigned collections
    this.pendingTasks.delete(taskId);
    this.assignedTasks.delete(taskId);
    
    return true;
  }

  /**
   * Create transaction tasks from pending transactions
   * @param {Array} transactions - Pending transactions
   * @returns {Array} Created tasks
   */
  createTransactionTasks(transactions) {
    const tasks = [];
    
    transactions.forEach(tx => {
      // Determine difficulty based on transaction complexity
      const difficulty = this.calculateTransactionDifficulty(tx);
      
      // Determine priority based on gas price or other factors
      const priority = this.calculateTransactionPriority(tx);
      
      // Create task
      const task = this.createTask('transaction', tx, difficulty, priority);
      tasks.push(task);
    });
    
    return tasks;
  }

  /**
   * Create block validation task
   * @param {Object} block - Block to validate
   * @returns {Object} Created task
   */
  createBlockValidationTask(block) {
    // Determine difficulty based on block size and complexity
    const difficulty = this.calculateBlockDifficulty(block);
    
    // Block validation is always high priority
    const priority = 10;
    
    // Create task
    return this.createTask('block', block, difficulty, priority);
  }

  /**
   * Calculate transaction difficulty
   * @param {Object} transaction - Transaction object
   * @returns {number} Difficulty level (1-5)
   */
  calculateTransactionDifficulty(transaction) {
    // In a real implementation, this would analyze transaction complexity
    // For now, use a simple heuristic based on data size
    const dataSize = JSON.stringify(transaction).length;
    
    if (dataSize > 10000) return 5;
    if (dataSize > 5000) return 4;
    if (dataSize > 1000) return 3;
    if (dataSize > 500) return 2;
    return 1;
  }

  /**
   * Calculate transaction priority
   * @param {Object} transaction - Transaction object
   * @returns {number} Priority level (1-10)
   */
  calculateTransactionPriority(transaction) {
    // In a real implementation, this would consider gas price, sender stake, etc.
    // For now, use a simple random value
    return Math.floor(Math.random() * 10) + 1;
  }

  /**
   * Calculate block difficulty
   * @param {Object} block - Block object
   * @returns {number} Difficulty level (1-5)
   */
  calculateBlockDifficulty(block) {
    // In a real implementation, this would analyze block complexity
    // For now, use a simple heuristic based on number of transactions
    const txCount = block.transactions ? block.transactions.length : 0;
    
    if (txCount > 1000) return 5;
    if (txCount > 500) return 4;
    if (txCount > 100) return 3;
    if (txCount > 50) return 2;
    return 1;
  }

  /**
   * Get task by ID
   * @param {string} taskId - Task ID
   * @returns {Object|null} Task or null if not found
   */
  getTask(taskId) {
    return this.tasks.get(taskId) || null;
  }

  /**
   * Get tasks by status
   * @param {string} status - Task status
   * @returns {Array} Tasks with the specified status
   */
  getTasksByStatus(status) {
    const tasks = [];
    
    for (const task of this.tasks.values()) {
      if (task.status === status) {
        tasks.push(task);
      }
    }
    
    return tasks;
  }

  /**
   * Get task statistics
   * @returns {Object} Task statistics
   */
  getStatistics() {
    const pendingCount = this.pendingTasks.size;
    const assignedCount = this.assignedTasks.size;
    const completedCount = this.completedTasks.size;
    
    // Calculate average completion time
    let totalCompletionTime = 0;
    let completedTasks = 0;
    
    for (const completion of this.completedTasks.values()) {
      totalCompletionTime += completion.completionTime;
      completedTasks++;
    }
    
    const averageCompletionTime = completedTasks > 0 ? totalCompletionTime / completedTasks : 0;
    
    // Count tasks by type
    const tasksByType = {};
    for (const task of this.tasks.values()) {
      if (!tasksByType[task.type]) {
        tasksByType[task.type] = 0;
      }
      tasksByType[task.type]++;
    }
    
    return {
      total: this.tasks.size,
      pending: pendingCount,
      assigned: assignedCount,
      completed: completedCount,
      cancelled: this.tasks.size - pendingCount - assignedCount - completedCount,
      averageCompletionTime,
      tasksByType
    };
  }
}

module.exports = TaskPool;
