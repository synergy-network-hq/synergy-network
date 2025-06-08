"""
Validator Cluster Module for Synergy Network

This module implements the Validator Cluster component of the Proof of Synergy consensus mechanism.
Validator clusters are dynamically formed groups of validators that collaborate on tasks.
"""

import uuid
import time
import enum
import random
import json
from typing import List, Dict, Any, Optional, Set, Tuple

class ValidatorStatus(enum.Enum):
    """Enum representing the status of a validator."""
    ACTIVE = 1
    INACTIVE = 2
    PENALIZED = 3
    SLASHED = 4

class ClusterStatus(enum.Enum):
    """Enum representing the status of a validator cluster."""
    FORMING = 1
    ACTIVE = 2
    DISSOLVING = 3
    RESHUFFLING = 4

class ResourceCapabilities:
    """Class representing the resource capabilities of a validator."""
    
    def __init__(
        self,
        cpu: int = 2,
        memory: int = 1024,  # MB
        storage: int = 10240, # MB (10GB)
        bandwidth: int = 1024, # KB/s (1MB/s)
        gpu: bool = False,
        special_hardware: List[str] = None
    ):
        self.cpu = cpu
        self.memory = memory
        self.storage = storage
        self.bandwidth = bandwidth
        self.gpu = gpu
        self.special_hardware = special_hardware or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ResourceCapabilities to dictionary."""
        return {
            "cpu": self.cpu,
            "memory": self.memory,
            "storage": self.storage,
            "bandwidth": self.bandwidth,
            "gpu": self.gpu,
            "special_hardware": self.special_hardware
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceCapabilities':
        """Create ResourceCapabilities from dictionary."""
        return cls(
            cpu=data.get("cpu", 2),
            memory=data.get("memory", 1024),
            storage=data.get("storage", 10240),
            bandwidth=data.get("bandwidth", 1024),
            gpu=data.get("gpu", False),
            special_hardware=data.get("special_hardware", [])
        )
    
    def meets_requirements(self, requirements) -> bool:
        """Check if capabilities meet the given requirements."""
        if self.cpu < requirements.min_cpu:
            return False
        if self.memory < requirements.min_memory:
            return False
        if self.storage < requirements.min_storage:
            return False
        if self.bandwidth < requirements.min_bandwidth:
            return False
        if requirements.gpu_required and not self.gpu:
            return False
        
        # Check if all required special hardware is available
        for hw in requirements.special_hardware:
            if hw not in self.special_hardware:
                return False
        
        return True

class ValidatorInfo:
    """Class representing information about a validator."""
    
    def __init__(
        self,
        node_id: str,
        public_key: str,
        resources: ResourceCapabilities = None,
        synergy_points: int = 0,
        availability: float = 1.0,
        last_active_timestamp: int = None,
        status: ValidatorStatus = ValidatorStatus.ACTIVE,
        network_address: str = None,
        stake_amount: int = 0
    ):
        self.node_id = node_id
        self.public_key = public_key
        self.resources = resources or ResourceCapabilities()
        self.synergy_points = synergy_points
        self.availability = availability
        self.last_active_timestamp = last_active_timestamp or int(time.time())
        self.status = status
        self.network_address = network_address
        self.stake_amount = stake_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ValidatorInfo to dictionary."""
        return {
            "node_id": self.node_id,
            "public_key": self.public_key,
            "resources": self.resources.to_dict(),
            "synergy_points": self.synergy_points,
            "availability": self.availability,
            "last_active_timestamp": self.last_active_timestamp,
            "status": self.status.name,
            "network_address": self.network_address,
            "stake_amount": self.stake_amount
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidatorInfo':
        """Create ValidatorInfo from dictionary."""
        return cls(
            node_id=data["node_id"],
            public_key=data["public_key"],
            resources=ResourceCapabilities.from_dict(data.get("resources", {})),
            synergy_points=data.get("synergy_points", 0),
            availability=data.get("availability", 1.0),
            last_active_timestamp=data.get("last_active_timestamp"),
            status=ValidatorStatus[data["status"]] if "status" in data else ValidatorStatus.ACTIVE,
            network_address=data.get("network_address"),
            stake_amount=data.get("stake_amount", 0)
        )
    
    def update_availability(self, new_availability: float) -> None:
        """Update the availability of the validator."""
        self.availability = max(0.0, min(1.0, new_availability))
    
    def update_last_active(self) -> None:
        """Update the last active timestamp to current time."""
        self.last_active_timestamp = int(time.time())
    
    def add_synergy_points(self, points: int) -> None:
        """Add Synergy Points to the validator."""
        self.synergy_points += points
    
    def deduct_synergy_points(self, points: int) -> None:
        """Deduct Synergy Points from the validator."""
        self.synergy_points = max(0, self.synergy_points - points)
    
    def is_active(self) -> bool:
        """Check if the validator is active."""
        return self.status == ValidatorStatus.ACTIVE

class ClusterPerformance:
    """Class representing performance metrics for a validator cluster."""
    
    def __init__(
        self,
        tasks_completed: int = 0,
        tasks_verified: int = 0,
        tasks_failed: int = 0,
        average_completion_time: float = 0.0,
        reward_earned: int = 0
    ):
        self.tasks_completed = tasks_completed
        self.tasks_verified = tasks_verified
        self.tasks_failed = tasks_failed
        self.average_completion_time = average_completion_time
        self.reward_earned = reward_earned
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ClusterPerformance to dictionary."""
        return {
            "tasks_completed": self.tasks_completed,
            "tasks_verified": self.tasks_verified,
            "tasks_failed": self.tasks_failed,
            "average_completion_time": self.average_completion_time,
            "reward_earned": self.reward_earned
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClusterPerformance':
        """Create ClusterPerformance from dictionary."""
        return cls(
            tasks_completed=data.get("tasks_completed", 0),
            tasks_verified=data.get("tasks_verified", 0),
            tasks_failed=data.get("tasks_failed", 0),
            average_completion_time=data.get("average_completion_time", 0.0),
            reward_earned=data.get("reward_earned", 0)
        )
    
    def record_task_completion(self, completion_time: float, reward: int) -> None:
        """Record a completed task."""
        if self.tasks_completed == 0:
            self.average_completion_time = completion_time
        else:
            # Update running average
            self.average_completion_time = (
                (self.average_completion_time * self.tasks_completed + completion_time) / 
                (self.tasks_completed + 1)
            )
        
        self.tasks_completed += 1
        self.reward_earned += reward
    
    def record_task_verification(self) -> None:
        """Record a verified task."""
        self.tasks_verified += 1
    
    def record_task_failure(self) -> None:
        """Record a failed task."""
        self.tasks_failed += 1

class ValidatorCluster:
    """Class representing a cluster of validators in the Synergy Network."""
    
    def __init__(
        self,
        cluster_id: str = None,
        validators: List[ValidatorInfo] = None,
        assigned_tasks: List[str] = None,
        formation_timestamp: int = None,
        reshuffle_timestamp: int = None,
        status: ClusterStatus = ClusterStatus.FORMING,
        performance: ClusterPerformance = None,
        min_validators: int = 7,
        max_validators: int = 15
    ):
        self.cluster_id = cluster_id or str(uuid.uuid4())
        self.validators = validators or []
        self.assigned_tasks = assigned_tasks or []
        self.formation_timestamp = formation_timestamp or int(time.time())
        # Default reshuffle after 10,000 blocks (approx. 8 hours at 3s block time)
        self.reshuffle_timestamp = reshuffle_timestamp or (self.formation_timestamp + 28800)
        self.status = status
        self.performance = performance or ClusterPerformance()
        self.min_validators = min_validators
        self.max_validators = max_validators
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ValidatorCluster to dictionary."""
        return {
            "cluster_id": self.cluster_id,
            "validators": [v.to_dict() for v in self.validators],
            "assigned_tasks": self.assigned_tasks,
            "formation_timestamp": self.formation_timestamp,
            "reshuffle_timestamp": self.reshuffle_timestamp,
            "status": self.status.name,
            "performance": self.performance.to_dict(),
            "min_validators": self.min_validators,
            "max_validators": self.max_validators
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidatorCluster':
        """Create ValidatorCluster from dictionary."""
        validators = [ValidatorInfo.from_dict(v) for v in data.get("validators", [])]
        
        return cls(
            cluster_id=data.get("cluster_id"),
            validators=validators,
            assigned_tasks=data.get("assigned_tasks", []),
            formation_timestamp=data.get("formation_timestamp"),
            reshuffle_timestamp=data.get("reshuffle_timestamp"),
            status=ClusterStatus[data["status"]] if "status" in data else ClusterStatus.FORMING,
            performance=ClusterPerformance.from_dict(data.get("performance", {})),
            min_validators=data.get("min_validators", 7),
            max_validators=data.get("max_validators", 15)
        )
    
    def add_validator(self, validator: ValidatorInfo) -> bool:
        """Add a validator to the cluster."""
        if len(self.validators) >= self.max_validators:
            return False
        
        # Check if validator is already in the cluster
        for v in self.validators:
            if v.node_id == validator.node_id:
                return False
        
        self.validators.append(validator)
        return True
    
    def remove_validator(self, node_id: str) -> bool:
        """Remove a validator from the cluster."""
        for i, validator in enumerate(self.validators):
            if validator.node_id == node_id:
                self.validators.pop(i)
                return True
        return False
    
    def assign_task(self, task_id: str) -> bool:
        """Assign a task to the cluster."""
        if task_id in self.assigned_tasks:
            return False
        
        self.assigned_tasks.append(task_id)
        return True
    
    def complete_task(self, task_id: str, completion_time: float, reward: int) -> bool:
        """Mark a task as completed."""
        if task_id not in self.assigned_tasks:
            return False
        
        self.performance.record_task_completion(completion_time, reward)
        self.assigned_tasks.remove(task_id)
        return True
    
    def verify_task(self, task_id: str) -> None:
        """Record a task verification."""
        self.performance.record_task_verification()
    
    def fail_task(self, task_id: str) -> bool:
        """Mark a task as failed."""
        if task_id not in self.assigned_tasks:
            return False
        
        self.performance.record_task_failure()
        self.assigned_tasks.remove(task_id)
        return True
    
    def is_active(self) -> bool:
        """Check if the cluster is active."""
        return self.status == ClusterStatus.ACTIVE
    
    def should_reshuffle(self, current_time: int = None) -> bool:
        """Check if the cluster should be reshuffled."""
        if current_time is None:
            current_time = int(time.time())
        
        return current_time >= self.reshuffle_timestamp
    
    def has_minimum_validators(self) -> bool:
        """Check if the cluster has the minimum required validators."""
        active_validators = sum(1 for v in self.validators if v.is_active())
        return active_validators >= self.min_validators
    
    def get_active_validators(self) -> List[ValidatorInfo]:
        """Get all active validators in the cluster."""
        return [v for v in self.validators if v.is_active()]
    
    def distribute_rewards(self, total_reward: int) -> Dict[str, int]:
        """Distribute rewards to validators based on Synergy Points."""
        active_validators = self.get_active_validators()
        if not active_validators:
            return {}
        
        # Calculate total Synergy Points in the cluster
        total_points = sum(v.synergy_points for v in active_validators)
        if total_points == 0:
            # Equal distribution if no points
            reward_per_validator = total_reward // len(active_validators)
            return {v.node_id: reward_per_validator for v in active_validators}
        
        # 70% distributed based on Synergy Points, 30% equally
        individual_reward_pool = int(total_reward * 0.7)
        collaboration_reward_pool = total_reward - individual_reward_pool
        
        # Calculate collaboration bonus (equal for all)
        collaboration_bonus = collaboration_reward_pool // len(active_validators)
        
        # Calculate individual rewards based on points
        rewards = {}
        for validator in active_validators:
            point_share = validator.synergy_points / total_points
            individual_reward = int(individual_reward_pool * point_share)
            rewards[validator.node_id] = individual_reward + collaboration_bonus
        
        return rewards

class ClusterManager:
    """Class for managing validator clusters."""
    
    def __init__(self):
        self.clusters: Dict[str, ValidatorCluster] = {}
        self.validators: Dict[str, ValidatorInfo] = {}
        self.validator_to_cluster: Dict[str, str] = {}  # Maps validator ID to cluster ID
    
    def register_validator(self, validator: ValidatorInfo) -> bool:
        """Register a validator with the manager."""
        if validator.node_id in self.validators:
            # Update existing validator
            self.validators[validator.node_id] = validator
            return True
        
        self.validators[validator.node_id] = validator
        return True
    
    def get_validator(self, node_id: str) -> Optional[ValidatorInfo]:
        """Get a validator by its ID."""
        return self.validators.get(node_id)
    
    def get_active_validators(self) -> List[ValidatorInfo]:
        """Get all active validators."""
        return [v for v in self.validators.values() if v.is_active()]
    
    def get_validators_by_capability(self, requirements) -> List[ValidatorInfo]:
        """Get validators that meet the given requirements."""
        return [
            v for v in self.get_active_validators() 
            if v.resources.meets_requirements(requirements)
        ]
    
    def create_cluster(
        self,
        validator_ids: List[str] = None,
        min_validators: int = 7,
        max_validators: int = 15
    ) -> Optional[ValidatorCluster]:
        """Create a new validator cluster."""
        cluster = ValidatorCluster(min_validators=min_validators, max_validators=max_validators)
        
        if validator_ids:
            for node_id in validator_ids:
                validator = self.get_validator(node_id)
                if validator and validator.is_active():
                    # Check if validator is already in a cluster
                    if node_id in self.validator_to_cluster:
                        continue
                    
                    cluster.add_validator(validator)
                    self.validator_to_cluster[node_id] = cluster.cluster_id
        
        if cluster.has_minimum_validators():
            cluster.status = ClusterStatus.ACTIVE
            self.clusters[cluster.cluster_id] = cluster
            return cluster
        
        return None
    
    def form_cluster_by_requirements(
        self,
        requirements,
        min_validators: int = 7,
        max_validators: int = 15
    ) -> Optional[ValidatorCluster]:
        """Form a cluster of validators that meet the given requirements."""
        eligible_validators = self.get_validators_by_capability(requirements)
        
        # Filter out validators already in clusters
        available_validators = [
            v for v in eligible_validators 
            if v.node_id not in self.validator_to_cluster
        ]
        
        if len(available_validators) < min_validators:
            return None
        
        # Select random validators up to max_validators
        selected_validators = random.sample(
            available_validators, 
            min(len(available_validators), max_validators)
        )
        
        # Create cluster with selected validators
        cluster = ValidatorCluster(min_validators=min_validators, max_validators=max_validators)
        
        for validator in selected_validators:
            cluster.add_validator(validator)
            self.validator_to_cluster[validator.node_id] = cluster.cluster_id
        
        cluster.status = ClusterStatus.ACTIVE
        self.clusters[cluster.cluster_id] = cluster
        return cluster
    
    def get_cluster(self, cluster_id: str) -> Optional[ValidatorCluster]:
        """Get a cluster by its ID."""
        return self.clusters.get(cluster_id)
    
    def get_validator_cluster(self, node_id: str) -> Optional[ValidatorCluster]:
        """Get the cluster a validator belongs to."""
        cluster_id = self.validator_to_cluster.get(node_id)
        if cluster_id:
            return self.get_cluster(cluster_id)
        return None
    
    def assign_task_to_cluster(self, task_id: str, cluster_id: str) -> bool:
        """Assign a task to a cluster."""
        cluster = self.get_cluster(cluster_id)
        if cluster and cluster.is_active():
            return cluster.assign_task(task_id)
        return False
    
    def find_cluster_for_task(self, requirements) -> Optional[str]:
        """Find a suitable cluster for a task with the given requirements."""
        # Get active clusters
        active_clusters = [c for c in self.clusters.values() if c.is_active()]
        
        # Filter clusters by capability
        suitable_clusters = []
        for cluster in active_clusters:
            # Check if at least 2/3 of validators meet requirements
            capable_validators = sum(
                1 for v in cluster.validators 
                if v.is_active() and v.resources.meets_requirements(requirements)
            )
            
            if capable_validators >= (2 * len(cluster.validators) // 3):
                suitable_clusters.append(cluster)
        
        if not suitable_clusters:
            return None
        
        # Select cluster with fewest assigned tasks
        return min(suitable_clusters, key=lambda c: len(c.assigned_tasks)).cluster_id
    
    def reshuffle_clusters(self) -> int:
        """Reshuffle clusters that have reached their reshuffle time."""
        reshuffled_count = 0
        current_time = int(time.time())
        
        clusters_to_reshuffle = [
            c for c in self.clusters.values() 
            if c.is_active() and c.should_reshuffle(current_time)
        ]
        
        for cluster in clusters_to_reshuffle:
            # Mark cluster as reshuffling
            cluster.status = ClusterStatus.RESHUFFLING
            
            # Remove validator-to-cluster mappings
            for validator in cluster.validators:
                if validator.node_id in self.validator_to_cluster:
                    del self.validator_to_cluster[validator.node_id]
            
            # If cluster has no assigned tasks, dissolve it
            if not cluster.assigned_tasks:
                cluster.status = ClusterStatus.DISSOLVING
                reshuffled_count += 1
            else:
                # Otherwise, keep it in reshuffling state until tasks are completed
                pass
        
        return reshuffled_count
    
    def check_cluster_health(self) -> Dict[str, Any]:
        """Check the health of all clusters."""
        total_clusters = len(self.clusters)
        active_clusters = sum(1 for c in self.clusters.values() if c.is_active())
        forming_clusters = sum(1 for c in self.clusters.values() if c.status == ClusterStatus.FORMING)
        reshuffling_clusters = sum(1 for c in self.clusters.values() if c.status == ClusterStatus.RESHUFFLING)
        dissolving_clusters = sum(1 for c in self.clusters.values() if c.status == ClusterStatus.DISSOLVING)
        
        return {
            "total_clusters": total_clusters,
            "active_clusters": active_clusters,
            "forming_clusters": forming_clusters,
            "reshuffling_clusters": reshuffling_clusters,
            "dissolving_clusters": dissolving_clusters,
            "total_validators": len(self.validators),
            "active_validators": len(self.get_active_validators()),
            "clustered_validators": len(self.validator_to_cluster)
        }
    
    def save_to_file(self, filename: str) -> None:
        """Save all clusters and validators to a file."""
        data = {
            "clusters": {cluster_id: cluster.to_dict() for cluster_id, cluster in self.clusters.items()},
            "validators": {node_id: validator.to_dict() for node_id, validator in self.validators.items()},
            "validator_to_cluster": self.validator_to_cluster
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'ClusterManager':
        """Load clusters and validators from a file."""
        manager = cls()
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
                # Load validators first
                for node_id, validator_data in data.get("validators", {}).items():
                    manager.validators[node_id] = ValidatorInfo.from_dict(validator_data)
                
                # Load clusters
                for cluster_id, cluster_data in data.get("clusters", {}).items():
                    manager.clusters[cluster_id] = ValidatorCluster.from_dict(cluster_data)
                
                # Load validator to cluster mappings
                manager.validator_to_cluster = data.get("validator_to_cluster", {})
        
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Return empty manager if file doesn't exist or is invalid
        
        return manager


# Example usage
if __name__ == "__main__":
    # Create a cluster manager
    manager = ClusterManager()
    
    # Register some validators
    for i in range(20):
        # Create validators with different capabilities
        if i < 10:
            # Standard validators
            resources = ResourceCapabilities(
                cpu=2 + i % 3,
                memory=1024 * (1 + i % 3),
                storage=10240 * (1 + i % 2),
                bandwidth=1024 * (1 + i % 2)
            )
        else:
            # High-performance validators
            resources = ResourceCapabilities(
                cpu=4 + i % 4,
                memory=4096 * (1 + i % 2),
                storage=51200 * (1 + i % 2),
                bandwidth=5120 * (1 + i % 2),
                gpu=(i % 3 == 0)
            )
        
        validator = ValidatorInfo(
            node_id=f"node_{i}",
            public_key=f"pk_{i}",
            resources=resources,
            synergy_points=100 + i * 10,
            network_address=f"192.168.1.{100 + i}",
            stake_amount=10000 + i * 1000
        )
        
        manager.register_validator(validator)
    
    # Create a cluster with specific validators
    cluster1 = manager.create_cluster(
        validator_ids=["node_0", "node_1", "node_2", "node_3", "node_4", "node_5", "node_6"]
    )
    
    print(f"Created cluster: {cluster1.cluster_id} with {len(cluster1.validators)} validators")
    
    # Create a cluster based on requirements
    from task_pool import ResourceRequirements
    
    requirements = ResourceRequirements(
        min_cpu=4,
        min_memory=4096,
        min_storage=51200,
        gpu_required=True
    )
    
    cluster2 = manager.form_cluster_by_requirements(requirements)
    
    if cluster2:
        print(f"Created cluster: {cluster2.cluster_id} with {len(cluster2.validators)} validators")
    else:
        print("Could not form cluster with the given requirements")
    
    # Assign tasks to clusters
    if cluster1:
        manager.assign_task_to_cluster("task_1", cluster1.cluster_id)
        manager.assign_task_to_cluster("task_2", cluster1.cluster_id)
        print(f"Assigned tasks to cluster: {cluster1.cluster_id}")
    
    # Check cluster health
    health = manager.check_cluster_health()
    print("Cluster Health:")
    for key, value in health.items():
        print(f"  {key}: {value}")
    
    # Save to file
    manager.save_to_file("clusters.json")
    print("Saved clusters to clusters.json")
    
    # Load from file
    loaded_manager = ClusterManager.load_from_file("clusters.json")
    print(f"Loaded {len(loaded_manager.clusters)} clusters from file")
