"""
Transaction Module for Synergy Network

This module implements the transaction structure and related functionality
for the Synergy Network blockchain.
"""

import time
import json
import uuid
from typing import Dict, List, Any, Optional, Union
import sys
import os

# Add parent directory to path to import from cryptography package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementation.cryptography.pqc.hash import HashFunctions
from implementation.cryptography.pqc.dilithium import DilithiumSigner
from implementation.cryptography.pqc.address import AddressGenerator

class TransactionType:
    """Enumeration of transaction types in the Synergy Network."""
    TRANSFER = "transfer"
    COINBASE = "coinbase"
    CONTRACT_DEPLOY = "contract_deploy"
    CONTRACT_CALL = "contract_call"
    VALIDATOR_REGISTER = "validator_register"
    VALIDATOR_UNREGISTER = "validator_unregister"
    STAKE = "stake"
    UNSTAKE = "unstake"
    TASK_SUBMIT = "task_submit"
    TASK_RESULT = "task_result"

class TransactionStatus:
    """Enumeration of transaction statuses in the Synergy Network."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Transaction:
    """Class representing a transaction in the Synergy Network."""
    
    def __init__(
        self,
        tx_type: str,
        from_address: str = None,
        to_address: str = None,
        amount: int = 0,
        fee: int = 0,
        nonce: int = 0,
        data: Union[str, Dict[str, Any]] = None,
        timestamp: int = None,
        signature: bytes = None,
        tx_id: str = None
    ):
        """
        Initialize a Transaction instance.
        
        Args:
            tx_type: Type of transaction
            from_address: Sender address
            to_address: Recipient address
            amount: Amount of SYN tokens
            fee: Transaction fee
            nonce: Sender's nonce
            data: Additional transaction data
            timestamp: Transaction creation timestamp
            signature: Transaction signature
            tx_id: Transaction ID
        """
        self.tx_type = tx_type
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.fee = fee
        self.nonce = nonce
        self.data = data or {}
        self.timestamp = timestamp or int(time.time())
        self.signature = signature
        self.tx_id = tx_id or str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Transaction to dictionary.
        
        Returns:
            Dictionary representation of the transaction
        """
        return {
            "tx_id": self.tx_id,
            "tx_type": self.tx_type,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "fee": self.fee,
            "nonce": self.nonce,
            "data": self.data,
            "timestamp": self.timestamp,
            "signature": self.signature.hex() if self.signature else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """
        Create Transaction from dictionary.
        
        Args:
            data: Dictionary representation of the transaction
        
        Returns:
            Transaction instance
        """
        return cls(
            tx_type=data["tx_type"],
            from_address=data.get("from_address"),
            to_address=data.get("to_address"),
            amount=data.get("amount", 0),
            fee=data.get("fee", 0),
            nonce=data.get("nonce", 0),
            data=data.get("data", {}),
            timestamp=data.get("timestamp"),
            signature=bytes.fromhex(data["signature"]) if data.get("signature") else None,
            tx_id=data.get("tx_id")
        )
    
    def serialize(self) -> bytes:
        """
        Serialize the transaction to bytes.
        
        Returns:
            Serialized transaction
        """
        return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'Transaction':
        """
        Deserialize bytes to a Transaction.
        
        Args:
            data: Serialized transaction
        
        Returns:
            Transaction instance
        """
        tx_dict = json.loads(data.decode('utf-8'))
        return cls.from_dict(tx_dict)
    
    def get_hash(self) -> bytes:
        """
        Compute the hash of the transaction.
        
        Returns:
            32-byte hash digest
        """
        # Create a dictionary representation without the signature
        tx_dict = self.to_dict()
        tx_dict.pop("signature", None)
        
        # Use the hash function from the cryptography package
        return HashFunctions.hash_transaction(tx_dict)
    
    def sign(self, private_key: bytes) -> bool:
        """
        Sign the transaction with the sender's private key.
        
        Args:
            private_key: Sender's private key
        
        Returns:
            True if transaction was signed, False otherwise
        """
        # Calculate transaction hash
        tx_hash = self.get_hash()
        
        # Sign the transaction hash
        self.signature = DilithiumSigner.sign(tx_hash, private_key)
        
        return True
    
    def verify_signature(self, public_key: bytes) -> bool:
        """
        Verify the transaction signature.
        
        Args:
            public_key: Sender's public key
        
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.signature:
            return False
        
        # Calculate transaction hash
        tx_hash = self.get_hash()
        
        # Verify the signature
        return DilithiumSigner.verify(tx_hash, self.signature, public_key)
    
    def verify(self, state) -> bool:
        """
        Verify the transaction's validity.
        
        Args:
            state: Current blockchain state
        
        Returns:
            True if transaction is valid, False otherwise
        """
        # Coinbase transactions don't need verification
        if self.tx_type == TransactionType.COINBASE:
            return True
        
        # Verify sender address is valid
        if not AddressGenerator.validate_address(self.from_address):
            return False
        
        # Verify recipient address is valid (if present)
        if self.to_address and not AddressGenerator.validate_address(self.to_address):
            return False
        
        # Verify amount is positive
        if self.amount < 0:
            return False
        
        # Verify fee is positive
        if self.fee < 0:
            return False
        
        # Verify sender has enough balance
        sender_balance = state.get_balance(self.from_address)
        if sender_balance < self.amount + self.fee:
            return False
        
        # Verify nonce is correct
        expected_nonce = state.get_nonce(self.from_address) + 1
        if self.nonce != expected_nonce:
            return False
        
        # Verify signature (would need public key from state)
        # This is a simplified version
        return True

class TransactionPool:
    """Class for managing pending transactions in the Synergy Network."""
    
    def __init__(self):
        """Initialize a TransactionPool instance."""
        self.pending_transactions: Dict[str, Transaction] = {}
        self.confirmed_transactions: Dict[str, Transaction] = {}
        self.rejected_transactions: Dict[str, Transaction] = {}
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Add a transaction to the pool.
        
        Args:
            transaction: Transaction to add
        
        Returns:
            True if transaction was added, False otherwise
        """
        # Check if transaction already exists
        if transaction.tx_id in self.pending_transactions:
            return False
        
        if transaction.tx_id in self.confirmed_transactions:
            return False
        
        # Add to pending transactions
        self.pending_transactions[transaction.tx_id] = transaction
        
        return True
    
    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        """
        Get a transaction by ID.
        
        Args:
            tx_id: Transaction ID
        
        Returns:
            Transaction instance or None if not found
        """
        # Check pending transactions
        if tx_id in self.pending_transactions:
            return self.pending_transactions[tx_id]
        
        # Check confirmed transactions
        if tx_id in self.confirmed_transactions:
            return self.confirmed_transactions[tx_id]
        
        # Check rejected transactions
        if tx_id in self.rejected_transactions:
            return self.rejected_transactions[tx_id]
        
        return None
    
    def get_pending_transactions(self, limit: int = 100) -> List[Transaction]:
        """
        Get pending transactions.
        
        Args:
            limit: Maximum number of transactions to return
        
        Returns:
            List of pending transactions
        """
        # Sort by fee (highest first)
        sorted_txs = sorted(
            self.pending_transactions.values(),
            key=lambda tx: tx.fee,
            reverse=True
        )
        
        return sorted_txs[:limit]
    
    def mark_as_confirmed(self, tx_id: str) -> bool:
        """
        Mark a transaction as confirmed.
        
        Args:
            tx_id: Transaction ID
        
        Returns:
            True if transaction was marked as confirmed, False otherwise
        """
        if tx_id not in self.pending_transactions:
            return False
        
        # Move from pending to confirmed
        tx = self.pending_transactions.pop(tx_id)
        self.confirmed_transactions[tx_id] = tx
        
        return True
    
    def mark_as_rejected(self, tx_id: str, reason: str = None) -> bool:
        """
        Mark a transaction as rejected.
        
        Args:
            tx_id: Transaction ID
            reason: Reason for rejection
        
        Returns:
            True if transaction was marked as rejected, False otherwise
        """
        if tx_id not in self.pending_transactions:
            return False
        
        # Move from pending to rejected
        tx = self.pending_transactions.pop(tx_id)
        self.rejected_transactions[tx_id] = tx
        
        # Add rejection reason to transaction data
        if reason:
            tx.data["rejection_reason"] = reason
        
        return True
    
    def remove_transaction(self, tx_id: str) -> bool:
        """
        Remove a transaction from the pool.
        
        Args:
            tx_id: Transaction ID
        
        Returns:
            True if transaction was removed, False otherwise
        """
        # Check pending transactions
        if tx_id in self.pending_transactions:
            del self.pending_transactions[tx_id]
            return True
        
        # Check confirmed transactions
        if tx_id in self.confirmed_transactions:
            del self.confirmed_transactions[tx_id]
            return True
        
        # Check rejected transactions
        if tx_id in self.rejected_transactions:
            del self.rejected_transactions[tx_id]
            return True
        
        return False
    
    def clear_expired_transactions(self, max_age: int = 3600) -> int:
        """
        Clear expired transactions from the pool.
        
        Args:
            max_age: Maximum age of transactions in seconds
        
        Returns:
            Number of transactions cleared
        """
        current_time = int(time.time())
        expired_count = 0
        
        # Check pending transactions
        for tx_id, tx in list(self.pending_transactions.items()):
            if current_time - tx.timestamp > max_age:
                self.pending_transactions.pop(tx_id)
                tx.data["expiration_reason"] = "timeout"
                self.rejected_transactions[tx_id] = tx
                expired_count += 1
        
        return expired_count
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the transaction pool.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "pending": len(self.pending_transactions),
            "confirmed": len(self.confirmed_transactions),
            "rejected": len(self.rejected_transactions),
            "total": len(self.pending_transactions) + len(self.confirmed_transactions) + len(self.rejected_transactions)
        }

class TransactionBuilder:
    """Class for building transactions in the Synergy Network."""
    
    @staticmethod
    def create_transfer(
        from_address: str,
        to_address: str,
        amount: int,
        fee: int,
        nonce: int,
        data: Dict[str, Any] = None
    ) -> Transaction:
        """
        Create a transfer transaction.
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            amount: Amount of SYN tokens
            fee: Transaction fee
            nonce: Sender's nonce
            data: Additional transaction data
        
        Returns:
            Transfer Transaction instance
        """
        return Transaction(
            tx_type=TransactionType.TRANSFER,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            fee=fee,
            nonce=nonce,
            data=data or {}
        )
    
    @staticmethod
    def create_coinbase(
        to_address: str,
        amount: int,
        block_height: int
    ) -> Transaction:
        """
        Create a coinbase transaction.
        
        Args:
            to_address: Recipient address (validator)
            amount: Block reward amount
            block_height: Height of the block
        
        Returns:
            Coinbase Transaction instance
        """
        return Transaction(
            tx_type=TransactionType.COINBASE,
            to_address=to_address,
            amount=amount,
            data={"block_height": block_height}
        )
    
    @staticmethod
    def create_contract_deploy(
        from_address: str,
        bytecode: str,
        amount: int,
        fee: int,
        nonce: int,
        contract_params: Dict[str, Any] = None
    ) -> Transaction:
        """
        Create a contract deployment transaction.
        
        Args:
            from_address: Deployer address
            bytecode: Contract bytecode
            amount: Initial contract balance
            fee: Transaction fee
            nonce: Sender's nonce
            contract_params: Contract initialization parameters
        
        Returns:
            Contract Deploy Transaction instance
        """
        return Transaction(
            tx_type=TransactionType.CONTRACT_DEPLOY,
            from_address=from_address,
            amount=amount,
            fee=fee,
            nonce=nonce,
            data={
                "bytecode": bytecode,
                "params": contract_params or {}
            }
        )
    
    @staticmethod
    def create_contract_call(
        from_address: str,
        to_address: str,
        amount: int,
        fee: int,
        nonce: int,
        method: str,
        params: Dict[str, Any] = None
    ) -> Transaction:
        """
        Create a contract call transaction.
        
        Args:
            from_address: Caller address
            to_address: Contract address
            amount: Amount to send to contract
            fee: Transaction fee
            nonce: Sender's nonce
            method: Contract method to call
            params: Method parameters
        
        Returns:
            Contract Call Transaction instance
        """
        return Transaction(
            tx_type=TransactionType.CONTRACT_CALL,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            fee=fee,
            nonce=nonce,
            data={
                "method": method,
                "params": params or {}
            }
        )
    
    @staticmethod
    def create_validator_register(
        from_address: str,
        stake_amount: int,
        fee: int,
        nonce: int,
        public_key: str,
        network_address: str,
        resources: Dict[str, Any] = None
    ) -> Transaction:
        """
        Create a validator registration transaction.
        
        Args:
            from_address: Validator address
            stake_amount: Amount to stake
            fee: Transaction fee
            nonce: Sender's nonce
            public_key: Validator's public key
            network_address: Validator's network address
            resources: Validator's resource capabilities
        
        Returns:
            Validator Register Transaction instance
        """
        return Transaction(
            tx_type=TransactionType.VALIDATOR_REGISTER,
            from_address=from_address,
            amount=stake_amount,
            fee=fee,
            nonce=nonce,
            data={
                "public_key": public_key,
                "network_address": network_address,
                "resources": resources or {}
            }
        )
    
    @staticmethod
    def create_task_submit(
        from_address: str,
        task_type: str,
        fee: int,
        nonce: int,
        task_data: Dict[str, Any],
        reward: int,
        deadline: int = None
    ) -> Transaction:
        """
        Create a task submission transaction.
        
        Args:
            from_address: Submitter address
            task_type: Type of task
            fee: Transaction fee
            nonce: Sender's nonce
            task_data: Task data
            reward: Reward for completing the task
            deadline: Task deadline timestamp
        
        Returns:
            Task Submit Transaction instance
        """
        current_time = int(time.time())
        
        return Transaction(
            tx_type=TransactionType.TASK_SUBMIT,
            from_address=from_address,
            amount=reward,  # Reward is locked in the transaction
            fee=fee,
            nonce=nonce,
            data={
                "task_type": task_type,
                "task_data": task_data,
                "deadline": deadline or (current_time + 3600)  # Default: 1 hour
            }
        )

# Example usage
if __name__ == "__main__":
    # Create a transfer transaction
    transfer_tx = TransactionBuilder.create_transfer(
        from_address="sYnQsyn1user1000000000000000000000000000000000",
        to_address="sYnQsyn1user2000000000000000000000000000000000",
        amount=100,
        fee=1,
        nonce=1
    )
    
    print("Transfer Transaction:")
    print(f"ID: {transfer_tx.tx_id}")
    print(f"Type: {transfer_tx.tx_type}")
    print(f"From: {transfer_tx.from_address}")
    print(f"To: {transfer_tx.to_address}")
    print(f"Amount: {transfer_tx.amount}")
    print(f"Fee: {transfer_tx.fee}")
    print(f"Hash: {transfer_tx.get_hash().hex()}")
    
    # Create a transaction pool
    pool = TransactionPool()
    
    # Add transaction to pool
    pool.add_transaction(transfer_tx)
    
    # Create a coinbase transaction
    coinbase_tx = TransactionBuilder.create_coinbase(
        to_address="sYnQsyn1validator1000000000000000000000000000",
        amount=50,
        block_height=1
    )
    
    # Add to pool
    pool.add_transaction(coinbase_tx)
    
    # Get pending transactions
    pending_txs = pool.get_pending_transactions()
    print(f"\nPending Transactions: {len(pending_txs)}")
    
    # Mark as confirmed
    pool.mark_as_confirmed(transfer_tx.tx_id)
    
    # Get stats
    stats = pool.get_stats()
    print("\nTransaction Pool Stats:")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Serialize and deserialize
    serialized = transfer_tx.serialize()
    deserialized = Transaction.deserialize(serialized)
    
    print("\nDeserialized Transaction:")
    print(f"ID: {deserialized.tx_id}")
    print(f"Hash: {deserialized.get_hash().hex()}")
    
    # Verify transactions match
    print(f"\nHashes match: {transfer_tx.get_hash() == deserialized.get_hash()}")
