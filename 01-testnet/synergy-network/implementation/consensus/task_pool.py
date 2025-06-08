"""
Task Pool Module for Synergy Network

This module implements the Task Pool component of the Proof of Synergy consensus mechanism.
Task pools manage computational tasks that are assigned to validator clusters.
"""

import uuid
import time
import enum
import json
from typing import List, Dict, Any, Optional, Tuple

class TaskType(enum.Enum):
    """Enum representing different types of tasks in the Synergy Network."""
    TRANSACTION_VALIDATION = 1
    DATA_PROCESSING = 2
    FILE_STORAGE = 3
    AI_COMPUTATION = 4
    CROSS_CHAIN_VERIFICATION = 5

class TaskStatus(enum.Enum):
    """Enum representing the status of a task."""
    PENDING = 1
    ASSIGNED = 2
    PROCESSING = 3
    COMPLETED = 4
    VERIFIED = 5
    FAILED = 6
    EXPIRED = 7

class ResourceRequirements:
    """Class representing the resource requirements for a task."""
    
    def __init__(
        self,
        min_cpu: int = 1,
        min_memory: int = 512,  # MB
        min_storage: int = 0,   # MB
        min_bandwidth: int = 0, # KB/s
        gpu_required: bool = False,
        special_hardware: List[str] = None
    ):
        self.min_cpu = min_cpu
        self.min_memory = min_memory
        self.min_storage = min_storage
        self.min_bandwidth = min_bandwidth
        self.gpu_required = gpu_required
        self.special_hardware = special_hardware or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ResourceRequirements to dictionary."""
        return {
            "min_cpu": self.min_cpu,
            "min_memory": self.min_memory,
            "min_storage": self.min_storage,
            "min_bandwidth": self.min_bandwidth,
            "gpu_required": self.gpu_required,
            "special_hardware": self.special_hardware
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceRequirements':
        """Create ResourceRequirements from dictionary."""
        return cls(
            min_cpu=data.get("min_cpu", 1),
            min_memory=data.get("min_memory", 512),
            min_storage=data.get("min_storage", 0),
            min_bandwidth=data.get("min_bandwidth", 0),
            gpu_required=data.get("gpu_required", False),
            special_hardware=data.get("special_hardware", [])
        )

class Task:
    """Class representing a task in the Synergy Network."""
    
    def __init__(
        self,
        task_id: str = None,
        data: bytes = None,
        complexity: float = 1.0,
        reward: int = 10,
        task_type: TaskType = TaskType.TRANSACTION_VALIDATION,
        status: TaskStatus = TaskStatus.PENDING,
        assigned_cluster: str = None,
        result: bytes = None,
        deadline: int = None,
        creation_time: int = None
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.data = data or b''
        self.complexity = complexity
        self.reward = reward
        self.task_type = task_type
        self.status = status
        self.assigned_cluster = assigned_cluster
        self.result = result
        self.creation_time = creation_time or int(time.time())
        self.deadline = deadline or (self.creation_time + 300)  # Default: 5 minutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Task to dictionary."""
        return {
            "task_id": self.task_id,
            "data": self.data.hex() if self.data else None,
            "complexity": self.complexity,
            "reward": self.reward,
            "task_type": self.task_type.name,
            "status": self.status.name,
            "assigned_cluster": self.assigned_cluster,
            "result": self.result.hex() if self.result else None,
            "creation_time": self.creation_time,
            "deadline": self.deadline
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task from dictionary."""
        return cls(
            task_id=data.get("task_id"),
            data=bytes.fromhex(data["data"]) if data.get("data") else None,
            complexity=data.get("complexity", 1.0),
            reward=data.get("reward", 10),
            task_type=TaskType[data["task_type"]] if "task_type" in data else TaskType.TRANSACTION_VALIDATION,
            status=TaskStatus[data["status"]] if "status" in data else TaskStatus.PENDING,
            assigned_cluster=data.get("assigned_cluster"),
            result=bytes.fromhex(data["result"]) if data.get("result") else None,
            deadline=data.get("deadline"),
            creation_time=data.get("creation_time")
        )
    
    def is_expired(self) -> bool:
        """Check if the task has expired."""
        return int(time.time()) > self.deadline
    
    def update_status(self, new_status: TaskStatus) -> None:
        """Update the status of the task."""
        self.status = new_status

class TaskPool:
    """Class representing a pool of tasks in the Synergy Network."""
    
    def __init__(
        self,
        pool_id: str = None,
        task_type: TaskType = TaskType.TRANSACTION_VALIDATION,
        priority: int = 1,
        requirements: ResourceRequirements = None,
        creation_time: int = None,
        expiration_time: int = None
    ):
        self.pool_id = pool_id or str(uuid.uuid4())
        self.task_type = task_type
        self.priority = priority
        self.tasks: List[Task] = []
        self.requirements = requirements or ResourceRequirements()
        self.creation_time = creation_time or int(time.time())
        self.expiration_time = expiration_time or (self.creation_time + 3600)  # Default: 1 hour
    
    def add_task(self, task: Task) -> None:
        """Add a task to the pool."""
        if task.task_type != self.task_type:
            raise ValueError(f"Task type {task.task_type} does not match pool type {self.task_type}")
        self.tasks.append(task)
    
    def get_pending_tasks(self, limit: int = 10) -> List[Task]:
        """Get pending tasks from the pool."""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING][:limit]
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def update_task_status(self, task_id: str, new_status: TaskStatus) -> bool:
        """Update the status of a task."""
        task = self.get_task_by_id(task_id)
        if task:
            task.update_status(new_status)
            return True
        return False
    
    def assign_task_to_cluster(self, task_id: str, cluster_id: str) -> bool:
        """Assign a task to a cluster."""
        task = self.get_task_by_id(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.assigned_cluster = cluster_id
            task.status = TaskStatus.ASSIGNED
            return True
        return False
    
    def set_task_result(self, task_id: str, result: bytes) -> bool:
        """Set the result of a task."""
        task = self.get_task_by_id(task_id)
        if task:
            task.result = result
            task.status = TaskStatus.COMPLETED
            return True
        return False
    
    def clean_expired_tasks(self) -> int:
        """Clean expired tasks from the pool."""
        expired_count = 0
        for task in self.tasks:
            if task.is_expired() and task.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.PROCESSING]:
                task.status = TaskStatus.EXPIRED
                expired_count += 1
        return expired_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TaskPool to dictionary."""
        return {
            "pool_id": self.pool_id,
            "task_type": self.task_type.name,
            "priority": self.priority,
            "tasks": [task.to_dict() for task in self.tasks],
            "requirements": self.requirements.to_dict(),
            "creation_time": self.creation_time,
            "expiration_time": self.expiration_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskPool':
        """Create TaskPool from dictionary."""
        pool = cls(
            pool_id=data.get("pool_id"),
            task_type=TaskType[data["task_type"]] if "task_type" in data else TaskType.TRANSACTION_VALIDATION,
            priority=data.get("priority", 1),
            requirements=ResourceRequirements.from_dict(data.get("requirements", {})),
            creation_time=data.get("creation_time"),
            expiration_time=data.get("expiration_time")
        )
        
        if "tasks" in data:
            for task_data in data["tasks"]:
                pool.tasks.append(Task.from_dict(task_data))
        
        return pool

class TaskPoolManager:
    """Class for managing multiple task pools."""
    
    def __init__(self):
        self.pools: Dict[str, TaskPool] = {}
    
    def create_pool(
        self,
        task_type: TaskType,
        priority: int = 1,
        requirements: ResourceRequirements = None
    ) -> TaskPool:
        """Create a new task pool."""
        pool = TaskPool(task_type=task_type, priority=priority, requirements=requirements)
        self.pools[pool.pool_id] = pool
        return pool
    
    def get_pool(self, pool_id: str) -> Optional[TaskPool]:
        """Get a pool by its ID."""
        return self.pools.get(pool_id)
    
    def get_pools_by_type(self, task_type: TaskType) -> List[TaskPool]:
        """Get all pools of a specific type."""
        return [pool for pool in self.pools.values() if pool.task_type == task_type]
    
    def add_task(self, task: Task, pool_id: str = None) -> Tuple[bool, str]:
        """Add a task to a specific pool or create a new pool if needed."""
        if pool_id and pool_id in self.pools:
            pool = self.pools[pool_id]
            if pool.task_type == task.task_type:
                pool.add_task(task)
                return True, pool_id
            else:
                return False, f"Task type {task.task_type} does not match pool type {pool.task_type}"
        
        # If no pool_id or pool not found, find a matching pool or create a new one
        matching_pools = self.get_pools_by_type(task.task_type)
        if matching_pools:
            # Add to the highest priority pool
            pool = max(matching_pools, key=lambda p: p.priority)
            pool.add_task(task)
            return True, pool.pool_id
        else:
            # Create a new pool
            pool = self.create_pool(task.task_type)
            pool.add_task(task)
            return True, pool.pool_id
    
    def get_pending_tasks_by_type(self, task_type: TaskType, limit: int = 10) -> List[Task]:
        """Get pending tasks of a specific type."""
        tasks = []
        for pool in self.get_pools_by_type(task_type):
            tasks.extend(pool.get_pending_tasks(limit - len(tasks)))
            if len(tasks) >= limit:
                break
        return tasks[:limit]
    
    def clean_expired_tasks(self) -> int:
        """Clean expired tasks from all pools."""
        total_expired = 0
        for pool in self.pools.values():
            total_expired += pool.clean_expired_tasks()
        return total_expired
    
    def save_to_file(self, filename: str) -> None:
        """Save all pools to a file."""
        data = {pool_id: pool.to_dict() for pool_id, pool in self.pools.items()}
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'TaskPoolManager':
        """Load pools from a file."""
        manager = cls()
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                for pool_id, pool_data in data.items():
                    manager.pools[pool_id] = TaskPool.from_dict(pool_data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Return empty manager if file doesn't exist or is invalid
        return manager


# Example usage
if __name__ == "__main__":
    # Create a task pool manager
    manager = TaskPoolManager()
    
    # Create a task pool for transaction validation
    tx_pool = manager.create_pool(
        task_type=TaskType.TRANSACTION_VALIDATION,
        priority=2,
        requirements=ResourceRequirements(min_cpu=2, min_memory=1024)
    )
    
    # Create a task pool for data processing
    data_pool = manager.create_pool(
        task_type=TaskType.DATA_PROCESSING,
        priority=1,
        requirements=ResourceRequirements(min_cpu=4, min_memory=2048, gpu_required=True)
    )
    
    # Create some tasks
    for i in range(5):
        tx_task = Task(
            data=f"transaction_{i}".encode(),
            complexity=1.0,
            reward=10,
            task_type=TaskType.TRANSACTION_VALIDATION
        )
        manager.add_task(tx_task, tx_pool.pool_id)
    
    for i in range(3):
        data_task = Task(
            data=f"data_processing_{i}".encode(),
            complexity=2.5,
            reward=25,
            task_type=TaskType.DATA_PROCESSING
        )
        manager.add_task(data_task, data_pool.pool_id)
    
    # Get pending tasks
    tx_tasks = manager.get_pending_tasks_by_type(TaskType.TRANSACTION_VALIDATION, 10)
    data_tasks = manager.get_pending_tasks_by_type(TaskType.DATA_PROCESSING, 10)
    
    print(f"Transaction tasks: {len(tx_tasks)}")
    print(f"Data processing tasks: {len(data_tasks)}")
    
    # Assign a task to a cluster
    if tx_tasks:
        tx_pool.assign_task_to_cluster(tx_tasks[0].task_id, "cluster_123")
        print(f"Assigned task {tx_tasks[0].task_id} to cluster_123")
    
    # Save to file
    manager.save_to_file("task_pools.json")
    print("Saved task pools to task_pools.json")
    
    # Load from file
    loaded_manager = TaskPoolManager.load_from_file("task_pools.json")
    print(f"Loaded {len(loaded_manager.pools)} pools from file")
