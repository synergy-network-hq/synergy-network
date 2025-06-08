"""
State Module for Synergy Network

This module implements the state management system for the Synergy Network blockchain,
handling account balances, nonces, smart contracts, and validator information.
"""

import json
import copy
from typing import Dict, List, Any, Optional, Set, Tuple
import sys
import os

# Add parent directory to path to import from other packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementation.cryptography.pqc.address import AddressGenerator

class Account:
    """Class representing an account in the Synergy Network state."""
    
    def __init__(
        self,
        address: str,
        balance: int = 0,
        nonce: int = 0,
        code: str = None,
        storage: Dict[str, Any] = None,
        is_validator: bool = False,
        validator_data: Dict[str, Any] = None
    ):
        """
        Initialize an Account instance.
        
        Args:
            address: Account address
            balance: Account balance in SYN tokens
            nonce: Account nonce (transaction count)
            code: Smart contract code (if contract account)
            storage: Smart contract storage (if contract account)
            is_validator: Whether the account is a validator
            validator_data: Validator-specific data
        """
        self.address = address
        self.balance = balance
        self.nonce = nonce
        self.code = code
        self.storage = storage or {}
        self.is_validator = is_validator
        self.validator_data = validator_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Account to dictionary.
        
        Returns:
            Dictionary representation of the account
        """
        return {
            "address": self.address,
            "balance": self.balance,
            "nonce": self.nonce,
            "code": self.code,
            "storage": self.storage,
            "is_validator": self.is_validator,
            "validator_data": self.validator_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        """
        Create Account from dictionary.
        
        Args:
            data: Dictionary representation of the account
        
        Returns:
            Account instance
        """
        return cls(
            address=data["address"],
            balance=data.get("balance", 0),
            nonce=data.get("nonce", 0),
            code=data.get("code"),
            storage=data.get("storage", {}),
            is_validator=data.get("is_validator", False),
            validator_data=data.get("validator_data", {})
        )
    
    def is_contract(self) -> bool:
        """
        Check if the account is a smart contract.
        
        Returns:
            True if the account is a contract, False otherwise
        """
        return self.code is not None and len(self.code) > 0

class StateDB:
    """Class for managing the state database of the Synergy Network."""
    
    def __init__(self):
        """Initialize a StateDB instance."""
        self.accounts: Dict[str, Account] = {}
        self.validators: Set[str] = set()
        self.total_supply: int = 0
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.clusters: Dict[str, Dict[str, Any]] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert StateDB to dictionary.
        
        Returns:
            Dictionary representation of the state
        """
        return {
            "accounts": {addr: account.to_dict() for addr, account in self.accounts.items()},
            "validators": list(self.validators),
            "total_supply": self.total_supply,
            "tasks": self.tasks,
            "clusters": self.clusters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateDB':
        """
        Create StateDB from dictionary.
        
        Args:
            data: Dictionary representation of the state
        
        Returns:
            StateDB instance
        """
        state = cls()
        
        # Load accounts
        accounts_data = data.get("accounts", {})
        for addr, account_data in accounts_data.items():
            state.accounts[addr] = Account.from_dict(account_data)
        
        # Load validators
        state.validators = set(data.get("validators", []))
        
        # Load total supply
        state.total_supply = data.get("total_supply", 0)
        
        # Load tasks
        state.tasks = data.get("tasks", {})
        
        # Load clusters
        state.clusters = data.get("clusters", {})
        
        return state
    
    def get_account(self, address: str) -> Account:
        """
        Get an account by address, creating it if it doesn't exist.
        
        Args:
            address: Account address
        
        Returns:
            Account instance
        """
        if address not in self.accounts:
            self.accounts[address] = Account(address=address)
        
        return self.accounts[address]
    
    def get_balance(self, address: str) -> int:
        """
        Get an account's balance.
        
        Args:
            address: Account address
        
        Returns:
            Account balance
        """
        return self.get_account(address).balance
    
    def set_balance(self, address: str, balance: int) -> bool:
        """
        Set an account's balance.
        
        Args:
            address: Account address
            balance: New balance
        
        Returns:
            True if successful, False otherwise
        """
        if balance < 0:
            return False
        
        account = self.get_account(address)
        
        # Update total supply
        self.total_supply = self.total_supply - account.balance + balance
        
        # Update account balance
        account.balance = balance
        
        return True
    
    def transfer(self, from_address: str, to_address: str, amount: int) -> bool:
        """
        Transfer tokens between accounts.
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            amount: Amount to transfer
        
        Returns:
            True if successful, False otherwise
        """
        if amount <= 0:
            return False
        
        from_account = self.get_account(from_address)
        
        if from_account.balance < amount:
            return False
        
        to_account = self.get_account(to_address)
        
        # Update balances
        from_account.balance -= amount
        to_account.balance += amount
        
        return True
    
    def get_nonce(self, address: str) -> int:
        """
        Get an account's nonce.
        
        Args:
            address: Account address
        
        Returns:
            Account nonce
        """
        return self.get_account(address).nonce
    
    def increment_nonce(self, address: str) -> int:
        """
        Increment an account's nonce.
        
        Args:
            address: Account address
        
        Returns:
            New nonce value
        """
        account = self.get_account(address)
        account.nonce += 1
        return account.nonce
    
    def create_contract(self, address: str, code: str, initial_storage: Dict[str, Any] = None) -> bool:
        """
        Create a smart contract account.
        
        Args:
            address: Contract address
            code: Contract code
            initial_storage: Initial contract storage
        
        Returns:
            True if successful, False otherwise
        """
        if not AddressGenerator.validate_address(address):
            return False
        
        account = self.get_account(address)
        
        # Check if account already has code
        if account.code:
            return False
        
        # Set contract code and storage
        account.code = code
        account.storage = initial_storage or {}
        
        return True
    
    def get_contract_storage(self, address: str, key: str) -> Any:
        """
        Get a value from contract storage.
        
        Args:
            address: Contract address
            key: Storage key
        
        Returns:
            Storage value
        """
        account = self.get_account(address)
        
        if not account.is_contract():
            return None
        
        return account.storage.get(key)
    
    def set_contract_storage(self, address: str, key: str, value: Any) -> bool:
        """
        Set a value in contract storage.
        
        Args:
            address: Contract address
            key: Storage key
            value: Storage value
        
        Returns:
            True if successful, False otherwise
        """
        account = self.get_account(address)
        
        if not account.is_contract():
            return False
        
        account.storage[key] = value
        return True
    
    def register_validator(self, address: str, validator_data: Dict[str, Any]) -> bool:
        """
        Register an account as a validator.
        
        Args:
            address: Validator address
            validator_data: Validator-specific data
        
        Returns:
            True if successful, False otherwise
        """
        account = self.get_account(address)
        
        # Update validator status
        account.is_validator = True
        account.validator_data = validator_data
        
        # Add to validators set
        self.validators.add(address)
        
        return True
    
    def unregister_validator(self, address: str) -> bool:
        """
        Unregister a validator.
        
        Args:
            address: Validator address
        
        Returns:
            True if successful, False otherwise
        """
        if address not in self.validators:
            return False
        
        account = self.get_account(address)
        
        # Update validator status
        account.is_validator = False
        
        # Remove from validators set
        self.validators.remove(address)
        
        return True
    
    def get_validators(self) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get all validators.
        
        Returns:
            List of (address, validator_data) tuples
        """
        validators_list = []
        
        for address in self.validators:
            account = self.get_account(address)
            validators_list.append((address, account.validator_data))
        
        return validators_list
    
    def add_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """
        Add a task to the state.
        
        Args:
            task_id: Task ID
            task_data: Task data
        
        Returns:
            True if successful, False otherwise
        """
        if task_id in self.tasks:
            return False
        
        self.tasks[task_id] = task_data
        return True
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """
        Update a task in the state.
        
        Args:
            task_id: Task ID
            task_data: Updated task data
        
        Returns:
            True if successful, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        self.tasks[task_id] = task_data
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from the state.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if successful, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        del self.tasks[task_id]
        return True
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task from the state.
        
        Args:
            task_id: Task ID
        
        Returns:
            Task data or None if not found
        """
        return self.tasks.get(task_id)
    
    def add_cluster(self, cluster_id: str, cluster_data: Dict[str, Any]) -> bool:
        """
        Add a validator cluster to the state.
        
        Args:
            cluster_id: Cluster ID
            cluster_data: Cluster data
        
        Returns:
            True if successful, False otherwise
        """
        if cluster_id in self.clusters:
            return False
        
        self.clusters[cluster_id] = cluster_data
        return True
    
    def update_cluster(self, cluster_id: str, cluster_data: Dict[str, Any]) -> bool:
        """
        Update a validator cluster in the state.
        
        Args:
            cluster_id: Cluster ID
            cluster_data: Updated cluster data
        
        Returns:
            True if successful, False otherwise
        """
        if cluster_id not in self.clusters:
            return False
        
        self.clusters[cluster_id] = cluster_data
        return True
    
    def remove_cluster(self, cluster_id: str) -> bool:
        """
        Remove a validator cluster from the state.
        
        Args:
            cluster_id: Cluster ID
        
        Returns:
            True if successful, False otherwise
        """
        if cluster_id not in self.clusters:
            return False
        
        del self.clusters[cluster_id]
        return True
    
    def get_cluster(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a validator cluster from the state.
        
        Args:
            cluster_id: Cluster ID
        
        Returns:
            Cluster data or None if not found
        """
        return self.clusters.get(cluster_id)
    
    def save_to_file(self, filename: str) -> bool:
        """
        Save the state to a file.
        
        Args:
            filename: Path to save the file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    @classmethod
    def load_from_file(cls, filename: str) -> Optional['StateDB']:
        """
        Load the state from a file.
        
        Args:
            filename: Path to the file
        
        Returns:
            StateDB instance or None if failed
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return None

class StateManager:
    """Class for managing state transitions in the Synergy Network."""
    
    def __init__(self, state: StateDB = None):
        """
        Initialize a StateManager instance.
        
        Args:
            state: Initial state
        """
        self.state = state or StateDB()
        self.snapshots: List[Dict[str, Any]] = []
    
    def apply_transaction(self, transaction) -> bool:
        """
        Apply a transaction to the state.
        
        Args:
            transaction: Transaction to apply
        
        Returns:
            True if successful, False otherwise
        """
        # Import transaction types
        from implementation.core.transaction.transaction import TransactionType
        
        # Take snapshot before applying transaction
        self.create_snapshot()
        
        try:
            # Process based on transaction type
            if transaction.tx_type == TransactionType.TRANSFER:
                return self._apply_transfer(transaction)
            
            elif transaction.tx_type == TransactionType.COINBASE:
                return self._apply_coinbase(transaction)
            
            elif transaction.tx_type == TransactionType.CONTRACT_DEPLOY:
                return self._apply_contract_deploy(transaction)
            
            elif transaction.tx_type == TransactionType.CONTRACT_CALL:
                return self._apply_contract_call(transaction)
            
            elif transaction.tx_type == TransactionType.VALIDATOR_REGISTER:
                return self._apply_validator_register(transaction)
            
            elif transaction.tx_type == TransactionType.VALIDATOR_UNREGISTER:
                return self._apply_validator_unregister(transaction)
            
            elif transaction.tx_type == TransactionType.STAKE:
                return self._apply_stake(transaction)
            
            elif transaction.tx_type == TransactionType.UNSTAKE:
                return self._apply_unstake(transaction)
            
            elif transaction.tx_type == TransactionType.TASK_SUBMIT:
                return self._apply_task_submit(transaction)
            
            elif transaction.tx_type == TransactionType.TASK_RESULT:
                return self._apply_task_result(transaction)
            
            else:
                # Unknown transaction type
                self.revert_to_snapshot()
                return False
        
        except Exception:
            # Revert state on error
            self.revert_to_snapshot()
            return False
    
    def _apply_transfer(self, transaction) -> bool:
        """
        Apply a transfer transaction to the state.
        
        Args:
            transaction: Transfer transaction
        
        Returns:
            True if successful, False otherwise
        """
        # Verify sender has enough balance
        sender_balance = self.state.get_balance(transaction.from_address)
        if sender_balance < transaction.amount + transaction.fee:
            return False
        
        # Transfer amount to recipient
        if not self.state.transfer(transaction.from_address, transaction.to_address, transaction.amount):
            return False
        
        # Transfer fee to fee recipient (for now, just burn it)
        if not self.state.transfer(transaction.from_address, "sYnQsyn1feerecipient00000000000000000000000", transaction.fee):
            return False
        
        # Increment sender's nonce
        self.state.increment_nonce(transaction.from_address)
        
        return True
    
    def _apply_coinbase(self, transaction) -> bool:
        """
        Apply a coinbase transaction to the state.
        
        Args:
            transaction: Coinbase transaction
        
        Returns:
            True if successful, False otherwise
        """
        # Add new tokens to recipient
        recipient = self.state.get_account(transaction.to_address)
        recipient.balance += transaction.amount
        
        # Update total supply
        self.state.total_supply += transaction.amount
        
        return True
    
    def _apply_contract_deploy(self, transaction) -> bool:
        """
        Apply a contract deployment transaction to the state.
        
        Args:
            transaction: Contract deployment transaction
        
        Returns:
            True if successful, False otherwise
        """
        # Verify sender has enough balance for fee
        sender_balance = self.state.get_balance(transaction.from_address)
        if sender_balance < transaction.amount + transaction.fee:
            return False
        
        # Generate contract address (simplified)
        contract_address = "sYnQsyn1contract" + transaction.tx_id[:20]
        
        # Create contract account
        if not self.state.create_contract(
            contract_address,
            transaction.data.get("bytecode", ""),
            transaction.data.get("params", {})
        ):
            return False
        
        # Transfer initial balance to contract
        if transaction.amount > 0:
            if not self.state.transfer(transaction.from_address, contract_address, transaction.amount):
                return False
        
        # Transfer fee to fee recipient
        if not self.state.transfer(transaction.from_address, "sYnQsyn1feerecipient00000000000000000000000", transaction.fee):
            return False
        
        # Increment sender's nonce
        self.state.increment_nonce(transaction.from_address)
        
        return True
    
    def _apply_contract_call(self, transaction) -> bool:
        """
        Apply a contract call transaction to the state.
        
        Args:
            transaction: Contract call transaction
        
        Returns:
            True if successful, False otherwise
        """
        # Verify sender has enough balance
        sender_balance = self.state.get_balance(transaction.from_address)
        if sender_balance < transaction.amount + transaction.fee:
            return False
        
        # Verify target is a contract
        contract = self.state.get_account(transaction.to_address)
        if not contract.is_contract():
            return False
        
        # Transfer amount to contract
        if transaction.amount > 0:
            if not self.state.transfer(transaction.from_address, transaction.to_address, transaction.amount):
                return False
        
        # Transfer fee to fee recipient
        if not self.state.transfer(transaction.from_address, "sYnQsyn1feerecipient00000000000000000000000", transaction.fee):
            return False
        
        # Increment sender's nonce
        self.state.increment_nonce(transaction.from_address)
        
        # Execute contract method (simplified)
        # In a real implementation, this would involve running the contract code
        method = transaction.data.get("method", "")
        params = transaction.data.get("params", {})
        
        # For now, just record the call in contract storage
        calls = contract.storage.get("calls", [])
        calls.append({
            "method": method,
            "params": params,
            "caller": transaction.from_address,
            "value": transaction.amount
        })
        contract.storage["calls"] = calls
        
        return True
    
    def _apply_validator_register(self, transaction) -> bool:
        """
        Apply a validator registration transaction to the state.
        
        Args:
            transaction: Validator registration transaction
        
        Returns:
            True if successful, False otherwise
        """
        # Verify sender has enough balance
        sender_balance = self.state.get_balance(transaction.from_address)
        if sender_balance < transaction.amount + transaction.fee:
            return False
        
        # Stake tokens
        stake_address = "sYnQsyn1stakingcontract000000000000000000000"
        if not self.state.transfer(transaction.from_address, stake_address, transaction.amount):
            return False
        
        # Transfer fee to fee recipient
        if not self.state.transfer(transaction.from_address, "sYnQsyn1feerecipient00000000000000000000000", transaction.fee):
            return False
        
        # Register validator
        validator_data = {
            "public_key": transaction.data.get("public_key", ""),
            "network_address": transaction.data.get("network_address", ""),
            "resources": transaction.data.get("resources", {}),
            "stake_amount": transaction.amount,
            "registration_time": transaction.timestamp
        }
        
        if not self.state.register_validator(transaction.from_address, validator_data):
            return False
        
        # Increment sender's nonce
        self.state.increment_nonce(transaction.from_address)
        
        return True
    
    def _apply_validator_unregister(self, transaction) -> bool:
        """
        Apply a validator unregistration transaction to the state.
        
        Args:
            transaction: Validator unregistration transaction
        
        Returns:
            True if successful, False otherwise
        """
        # Verify sender is a validator
        if transaction.from_address not in self.state.validators:
            return False
        
        # Verify sender has enough balance for fee
        sender_balance = self.state.get_balance(transaction.from_address)
        if sender_balance < transaction.fee:
            return False
        
        # Transfer fee to fee recipient
        if not self.state.transfer(transaction.from_address, "sYnQsyn1feerecipient00000000000000000000000", transaction.fee):
            return False
        
        # Unregister validator
        if not self.state.unregister_validator(transaction.from_address):
            return False
        
        # Return staked tokens (simplified)
        account = self.state.get_account(transaction.from_address)
        stake_amount = account.validator_data.get("stake_amount", 0)
        
        if stake_amount > 0:
            stake_address = "sYnQsyn1stakingcontract000000000000000000000"
            staking_account = self.state.get_account(stake_address)
            
            if staking_account.balance >= stake_amount:
                if not self.state.transfer(stake_address, transaction.from_address, stake_amount):
                    return False
        
        # Increment sender's nonce
        self.state.increment_nonce(transaction.from_address)
        
        return True
    
    def _apply_task_submit(self, transaction) -> bool:
        """
        Apply a task submission transaction to the state.
        
        Args:
            transaction: Task submission transaction
        
        Returns:
            True if successful, False otherwise
        """
        # Verify sender has enough balance
        sender_balance = self.state.get_balance(transaction.from_address)
        if sender_balance < transaction.amount + transaction.fee:
            return False
        
        # Transfer fee to fee recipient
        if not self.state.transfer(transaction.from_address, "sYnQsyn1feerecipient00000000000000000000000", transaction.fee):
            return False
        
        # Lock reward amount
        task_escrow = "sYnQsyn1taskescrow0000000000000000000000000000"
        if not self.state.transfer(transaction.from_address, task_escrow, transaction.amount):
            return False
        
        # Add task to state
        task_data = {
            "submitter": transaction.from_address,
            "task_type": transaction.data.get("task_type", ""),
            "task_data": transaction.data.get("task_data", {}),
            "reward": transaction.amount,
            "deadline": transaction.data.get("deadline", 0),
            "status": "pending",
            "submission_time": transaction.timestamp
        }
        
        if not self.state.add_task(transaction.tx_id, task_data):
            return False
        
        # Increment sender's nonce
        self.state.increment_nonce(transaction.from_address)
        
        return True
    
    def _apply_task_result(self, transaction) -> bool:
        """
        Apply a task result transaction to the state.
        
        Args:
            transaction: Task result transaction
        
        Returns:
            True if successful, False otherwise
        """
        # Verify sender has enough balance for fee
        sender_balance = self.state.get_balance(transaction.from_address)
        if sender_balance < transaction.fee:
            return False
        
        # Verify task exists
        task_id = transaction.data.get("task_id", "")
        task = self.state.get_task(task_id)
        
        if not task:
            return False
        
        # Verify task is pending
        if task.get("status", "") != "pending":
            return False
        
        # Transfer fee to fee recipient
        if not self.state.transfer(transaction.from_address, "sYnQsyn1feerecipient00000000000000000000000", transaction.fee):
            return False
        
        # Update task status
        task["status"] = "completed"
        task["result"] = transaction.data.get("result", {})
        task["completion_time"] = transaction.timestamp
        task["completed_by"] = transaction.from_address
        
        if not self.state.update_task(task_id, task):
            return False
        
        # Transfer reward to task completer
        task_escrow = "sYnQsyn1taskescrow0000000000000000000000000000"
        reward = task.get("reward", 0)
        
        if reward > 0:
            if not self.state.transfer(task_escrow, transaction.from_address, reward):
                return False
        
        # Increment sender's nonce
        self.state.increment_nonce(transaction.from_address)
        
        return True
    
    def _apply_stake(self, transaction) -> bool:
        """
        Apply a staking transaction to the state.
        
        Args:
            transaction: Staking transaction
        
        Returns:
            True if successful, False otherwise
        """
        # Verify sender has enough balance
        sender_balance = self.state.get_balance(transaction.from_address)
        if sender_balance < transaction.amount + transaction.fee:
            return False
        
        # Transfer fee to fee recipient
        if not self.state.transfer(transaction.from_address, "sYnQsyn1feerecipient00000000000000000000000", transaction.fee):
            return False
        
        # Transfer stake to staking contract
        stake_address = "sYnQsyn1stakingcontract000000000000000000000"
        if not self.state.transfer(transaction.from_address, stake_address, transaction.amount):
            return False
        
        # Update validator stake if applicable
        if transaction.from_address in self.state.validators:
            account = self.state.get_account(transaction.from_address)
            current_stake = account.validator_data.get("stake_amount", 0)
            account.validator_data["stake_amount"] = current_stake + transaction.amount
        
        # Increment sender's nonce
        self.state.increment_nonce(transaction.from_address)
        
        return True
    
    def _apply_unstake(self, transaction) -> bool:
        """
        Apply an unstaking transaction to the state.
        
        Args:
            transaction: Unstaking transaction
        
        Returns:
            True if successful, False otherwise
        """
        # Verify sender has enough balance for fee
        sender_balance = self.state.get_balance(transaction.from_address)
        if sender_balance < transaction.fee:
            return False
        
        # Transfer fee to fee recipient
        if not self.state.transfer(transaction.from_address, "sYnQsyn1feerecipient00000000000000000000000", transaction.fee):
            return False
        
        # Verify unstake amount
        unstake_amount = transaction.data.get("amount", 0)
        if unstake_amount <= 0:
            return False
        
        # If validator, check against validator stake
        if transaction.from_address in self.state.validators:
            account = self.state.get_account(transaction.from_address)
            current_stake = account.validator_data.get("stake_amount", 0)
            
            if unstake_amount > current_stake:
                return False
            
            # Update validator stake
            account.validator_data["stake_amount"] = current_stake - unstake_amount
        
        # Transfer from staking contract to sender
        stake_address = "sYnQsyn1stakingcontract000000000000000000000"
        staking_account = self.state.get_account(stake_address)
        
        if staking_account.balance < unstake_amount:
            return False
        
        if not self.state.transfer(stake_address, transaction.from_address, unstake_amount):
            return False
        
        # Increment sender's nonce
        self.state.increment_nonce(transaction.from_address)
        
        return True
    
    def create_snapshot(self) -> int:
        """
        Create a snapshot of the current state.
        
        Returns:
            Snapshot ID (index)
        """
        snapshot = json.dumps(self.state.to_dict())
        self.snapshots.append(snapshot)
        return len(self.snapshots) - 1
    
    def revert_to_snapshot(self, snapshot_id: int = None) -> bool:
        """
        Revert to a previous snapshot.
        
        Args:
            snapshot_id: Snapshot ID to revert to (defaults to last snapshot)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.snapshots:
            return False
        
        if snapshot_id is None:
            snapshot_id = len(self.snapshots) - 1
        
        if snapshot_id < 0 or snapshot_id >= len(self.snapshots):
            return False
        
        snapshot = self.snapshots[snapshot_id]
        self.state = StateDB.from_dict(json.loads(snapshot))
        
        # Remove all snapshots after this one
        self.snapshots = self.snapshots[:snapshot_id]
        
        return True
    
    def commit(self) -> None:
        """Commit the current state and clear snapshots."""
        self.snapshots = []
    
    def get_state(self) -> StateDB:
        """
        Get the current state.
        
        Returns:
            Current StateDB instance
        """
        return self.state
    
    def set_state(self, state: StateDB) -> None:
        """
        Set the current state.
        
        Args:
            state: New state
        """
        self.state = state
        self.snapshots = []

# Example usage
if __name__ == "__main__":
    # Create a state manager
    state_manager = StateManager()
    
    # Create some accounts
    alice = "sYnQsyn1alice00000000000000000000000000000000"
    bob = "sYnQsyn1bob0000000000000000000000000000000000"
    
    # Set initial balances
    state_manager.state.set_balance(alice, 1000)
    state_manager.state.set_balance(bob, 500)
    
    print("Initial State:")
    print(f"Alice balance: {state_manager.state.get_balance(alice)}")
    print(f"Bob balance: {state_manager.state.get_balance(bob)}")
    
    # Create a mock transaction
    from implementation.core.transaction.transaction import Transaction, TransactionType
    
    tx = Transaction(
        tx_type=TransactionType.TRANSFER,
        from_address=alice,
        to_address=bob,
        amount=200,
        fee=10,
        nonce=0
    )
    
    # Apply transaction
    success = state_manager.apply_transaction(tx)
    
    print(f"\nTransaction applied: {success}")
    print("Updated State:")
    print(f"Alice balance: {state_manager.state.get_balance(alice)}")
    print(f"Bob balance: {state_manager.state.get_balance(bob)}")
    
    # Create a snapshot
    snapshot_id = state_manager.create_snapshot()
    
    # Apply another transaction
    tx2 = Transaction(
        tx_type=TransactionType.TRANSFER,
        from_address=bob,
        to_address=alice,
        amount=50,
        fee=5,
        nonce=0
    )
    
    success = state_manager.apply_transaction(tx2)
    
    print(f"\nSecond transaction applied: {success}")
    print("Updated State:")
    print(f"Alice balance: {state_manager.state.get_balance(alice)}")
    print(f"Bob balance: {state_manager.state.get_balance(bob)}")
    
    # Revert to snapshot
    state_manager.revert_to_snapshot(snapshot_id)
    
    print("\nReverted to snapshot:")
    print(f"Alice balance: {state_manager.state.get_balance(alice)}")
    print(f"Bob balance: {state_manager.state.get_balance(bob)}")
    
    # Save state to file
    state_manager.state.save_to_file("state.json")
    print("\nState saved to file")
    
    # Load state from file
    loaded_state = StateDB.load_from_file("state.json")
    print("\nState loaded from file:")
    print(f"Alice balance: {loaded_state.get_balance(alice)}")
    print(f"Bob balance: {loaded_state.get_balance(bob)}")
    print(f"Total supply: {loaded_state.total_supply}")
