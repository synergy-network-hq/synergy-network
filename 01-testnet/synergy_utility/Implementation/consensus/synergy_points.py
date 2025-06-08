"""
Synergy Points Module for Synergy Network

This module implements the Synergy Points system of the Proof of Synergy consensus mechanism.
Synergy Points are awarded to validators based on their contributions to the network.
"""

import time
import math
import json
from typing import Dict, List, Any, Optional, Tuple

class SynergyPointsCalculator:
    """Class for calculating and managing Synergy Points."""
    
    def __init__(
        self,
        base_points_per_task: int = 10,
        max_efficiency_multiplier: float = 2.0,
        max_consistency_multiplier: float = 1.5,
        decay_rate: float = 0.05,  # 5% per epoch
        epoch_duration: int = 86400  # 24 hours in seconds
    ):
        self.base_points_per_task = base_points_per_task
        self.max_efficiency_multiplier = max_efficiency_multiplier
        self.max_consistency_multiplier = max_consistency_multiplier
        self.decay_rate = decay_rate
        self.epoch_duration = epoch_duration
        
        # Store validator metrics
        self.validator_metrics: Dict[str, Dict[str, Any]] = {}
    
    def calculate_task_points(
        self,
        task_complexity: float,
        completion_time: float,
        baseline_time: float,
        validator_id: str
    ) -> int:
        """
        Calculate Synergy Points for a completed task.
        
        Args:
            task_complexity: Complexity factor of the task (1.0 is standard)
            completion_time: Actual time taken to complete the task
            baseline_time: Expected time to complete the task
            validator_id: ID of the validator who completed the task
        
        Returns:
            Number of Synergy Points awarded
        """
        # Calculate efficiency multiplier
        if completion_time <= 0:
            efficiency_multiplier = self.max_efficiency_multiplier
        else:
            efficiency_multiplier = min(
                baseline_time / completion_time,
                self.max_efficiency_multiplier
            )
        
        # Calculate consistency multiplier
        consistency_multiplier = self._get_consistency_multiplier(validator_id)
        
        # Calculate total points
        points = int(
            self.base_points_per_task * 
            task_complexity * 
            efficiency_multiplier * 
            consistency_multiplier
        )
        
        # Update validator metrics
        self._update_validator_metrics(validator_id, points)
        
        return points
    
    def _get_consistency_multiplier(self, validator_id: str) -> float:
        """
        Calculate the consistency multiplier for a validator.
        
        Args:
            validator_id: ID of the validator
        
        Returns:
            Consistency multiplier (1.0 to max_consistency_multiplier)
        """
        if validator_id not in self.validator_metrics:
            return 1.0
        
        consecutive_tasks = self.validator_metrics[validator_id].get("consecutive_successful_tasks", 0)
        
        # Formula: 1 + (consecutive_tasks / 100), capped at max_consistency_multiplier
        multiplier = 1.0 + (consecutive_tasks / 100.0)
        return min(multiplier, self.max_consistency_multiplier)
    
    def _update_validator_metrics(self, validator_id: str, points: int) -> None:
        """
        Update metrics for a validator.
        
        Args:
            validator_id: ID of the validator
            points: Points awarded for the current task
        """
        if validator_id not in self.validator_metrics:
            self.validator_metrics[validator_id] = {
                "total_points": 0,
                "tasks_completed": 0,
                "consecutive_successful_tasks": 0,
                "last_active_time": int(time.time()),
                "points_history": []
            }
        
        metrics = self.validator_metrics[validator_id]
        metrics["total_points"] += points
        metrics["tasks_completed"] += 1
        metrics["consecutive_successful_tasks"] += 1
        metrics["last_active_time"] = int(time.time())
        
        # Store points history (last 100 tasks)
        metrics["points_history"].append({
            "timestamp": int(time.time()),
            "points": points
        })
        
        if len(metrics["points_history"]) > 100:
            metrics["points_history"].pop(0)
    
    def record_task_failure(self, validator_id: str) -> None:
        """
        Record a task failure for a validator.
        
        Args:
            validator_id: ID of the validator
        """
        if validator_id not in self.validator_metrics:
            self.validator_metrics[validator_id] = {
                "total_points": 0,
                "tasks_completed": 0,
                "consecutive_successful_tasks": 0,
                "last_active_time": int(time.time()),
                "points_history": []
            }
        
        # Reset consecutive successful tasks
        self.validator_metrics[validator_id]["consecutive_successful_tasks"] = 0
        self.validator_metrics[validator_id]["last_active_time"] = int(time.time())
    
    def apply_points_decay(self, current_time: int = None) -> Dict[str, int]:
        """
        Apply decay to Synergy Points for all validators.
        
        Args:
            current_time: Current timestamp (defaults to current time)
        
        Returns:
            Dictionary mapping validator IDs to their decayed points
        """
        if current_time is None:
            current_time = int(time.time())
        
        decayed_points = {}
        
        for validator_id, metrics in self.validator_metrics.items():
            last_active_time = metrics.get("last_active_time", 0)
            total_points = metrics.get("total_points", 0)
            
            # Calculate number of epochs since last activity
            elapsed_time = current_time - last_active_time
            epochs = elapsed_time / self.epoch_duration
            
            if epochs <= 0:
                # No decay needed
                decayed_points[validator_id] = total_points
                continue
            
            # Apply exponential decay
            new_points = int(total_points * math.pow(1 - self.decay_rate, epochs))
            
            # Update total points
            self.validator_metrics[validator_id]["total_points"] = new_points
            decayed_points[validator_id] = new_points
        
        return decayed_points
    
    def get_validator_points(self, validator_id: str) -> int:
        """
        Get the current Synergy Points for a validator.
        
        Args:
            validator_id: ID of the validator
        
        Returns:
            Current Synergy Points
        """
        if validator_id not in self.validator_metrics:
            return 0
        
        return self.validator_metrics[validator_id].get("total_points", 0)
    
    def get_validator_metrics(self, validator_id: str) -> Dict[str, Any]:
        """
        Get all metrics for a validator.
        
        Args:
            validator_id: ID of the validator
        
        Returns:
            Dictionary of validator metrics
        """
        if validator_id not in self.validator_metrics:
            return {
                "total_points": 0,
                "tasks_completed": 0,
                "consecutive_successful_tasks": 0,
                "last_active_time": 0,
                "points_history": []
            }
        
        return self.validator_metrics[validator_id]
    
    def get_top_validators(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get the top validators by Synergy Points.
        
        Args:
            limit: Maximum number of validators to return
        
        Returns:
            List of (validator_id, points) tuples, sorted by points
        """
        validators = [
            (validator_id, metrics.get("total_points", 0))
            for validator_id, metrics in self.validator_metrics.items()
        ]
        
        # Sort by points (descending)
        validators.sort(key=lambda x: x[1], reverse=True)
        
        return validators[:limit]
    
    def distribute_block_rewards(
        self,
        block_reward: int,
        participating_validators: List[str]
    ) -> Dict[str, int]:
        """
        Distribute block rewards based on Synergy Points.
        
        Args:
            block_reward: Total reward for the block
            participating_validators: List of validator IDs that participated
        
        Returns:
            Dictionary mapping validator IDs to their rewards
        """
        if not participating_validators:
            return {}
        
        # Get points for participating validators
        validator_points = {}
        total_points = 0
        
        for validator_id in participating_validators:
            points = self.get_validator_points(validator_id)
            validator_points[validator_id] = points
            total_points += points
        
        # If no points, distribute equally
        if total_points == 0:
            equal_share = block_reward // len(participating_validators)
            return {validator_id: equal_share for validator_id in participating_validators}
        
        # Distribute proportionally to points
        rewards = {}
        remaining_reward = block_reward
        
        for validator_id, points in validator_points.items():
            # Calculate proportional reward
            reward = int(block_reward * (points / total_points))
            rewards[validator_id] = reward
            remaining_reward -= reward
        
        # Distribute any remaining reward (due to integer division) to the highest point validator
        if remaining_reward > 0:
            top_validator = max(validator_points.items(), key=lambda x: x[1])[0]
            rewards[top_validator] += remaining_reward
        
        return rewards
    
    def save_to_file(self, filename: str) -> None:
        """
        Save calculator state to a file.
        
        Args:
            filename: Path to save the file
        """
        data = {
            "config": {
                "base_points_per_task": self.base_points_per_task,
                "max_efficiency_multiplier": self.max_efficiency_multiplier,
                "max_consistency_multiplier": self.max_consistency_multiplier,
                "decay_rate": self.decay_rate,
                "epoch_duration": self.epoch_duration
            },
            "validator_metrics": self.validator_metrics
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'SynergyPointsCalculator':
        """
        Load calculator state from a file.
        
        Args:
            filename: Path to the file
        
        Returns:
            Loaded SynergyPointsCalculator instance
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
                config = data.get("config", {})
                calculator = cls(
                    base_points_per_task=config.get("base_points_per_task", 10),
                    max_efficiency_multiplier=config.get("max_efficiency_multiplier", 2.0),
                    max_consistency_multiplier=config.get("max_consistency_multiplier", 1.5),
                    decay_rate=config.get("decay_rate", 0.05),
                    epoch_duration=config.get("epoch_duration", 86400)
                )
                
                calculator.validator_metrics = data.get("validator_metrics", {})
                
                return calculator
        
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default calculator if file doesn't exist or is invalid
            return cls()


# Example usage
if __name__ == "__main__":
    # Create a Synergy Points Calculator
    calculator = SynergyPointsCalculator()
    
    # Simulate task completions for some validators
    validators = ["validator_1", "validator_2", "validator_3"]
    
    for i in range(20):
        # Validator 1: Completes tasks quickly
        points1 = calculator.calculate_task_points(
            task_complexity=1.0,
            completion_time=8,
            baseline_time=10,
            validator_id="validator_1"
        )
        
        # Validator 2: Average performance
        points2 = calculator.calculate_task_points(
            task_complexity=1.0,
            completion_time=10,
            baseline_time=10,
            validator_id="validator_2"
        )
        
        # Validator 3: Slower performance, but handles complex tasks
        if i % 3 == 0:
            # Occasionally fails a task
            calculator.record_task_failure("validator_3")
        else:
            points3 = calculator.calculate_task_points(
                task_complexity=2.0,
                completion_time=15,
                baseline_time=10,
                validator_id="validator_3"
            )
    
    # Print current points
    for validator_id in validators:
        points = calculator.get_validator_points(validator_id)
        metrics = calculator.get_validator_metrics(validator_id)
        print(f"{validator_id}: {points} points, {metrics['tasks_completed']} tasks completed")
    
    # Apply decay
    print("\nAfter decay (simulating 2 epochs):")
    # Simulate time passing (2 epochs)
    current_time = int(time.time()) + calculator.epoch_duration * 2
    decayed_points = calculator.apply_points_decay(current_time)
    
    for validator_id, points in decayed_points.items():
        print(f"{validator_id}: {points} points")
    
    # Distribute block rewards
    block_reward = 100
    rewards = calculator.distribute_block_rewards(block_reward, validators)
    
    print("\nBlock reward distribution:")
    for validator_id, reward in rewards.items():
        print(f"{validator_id}: {reward} tokens")
    
    # Get top validators
    top_validators = calculator.get_top_validators()
    
    print("\nTop validators:")
    for validator_id, points in top_validators:
        print(f"{validator_id}: {points} points")
    
    # Save to file
    calculator.save_to_file("synergy_points.json")
    print("\nSaved calculator state to synergy_points.json")
    
    # Load from file
    loaded_calculator = SynergyPointsCalculator.load_from_file("synergy_points.json")
    print("Loaded calculator state from file")
    
    # Verify loaded state
    for validator_id in validators:
        original_points = calculator.get_validator_points(validator_id)
        loaded_points = loaded_calculator.get_validator_points(validator_id)
        print(f"{validator_id}: Original={original_points}, Loaded={loaded_points}")
