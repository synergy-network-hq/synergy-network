"""
Block Module for Synergy Network

This module implements the block structure and related functionality
for the Synergy Network blockchain.
"""

import time
import json
from typing import Dict, List, Any, Optional, Union
import sys
import os

# Add parent directory to path to import from cryptography package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementation.cryptography.pqc.hash import HashFunctions

class BlockHeader:
    """Class representing a block header in the Synergy Network."""
    
    def __init__(
        self,
        version: int = 1,
        previous_hash: bytes = None,
        merkle_root: bytes = None,
        timestamp: int = None,
        height: int = 0,
        validator_signature: bytes = None,
        validator_cluster_id: str = None,
        synergy_points: Dict[str, int] = None,
        difficulty: int = 1,
        nonce: bytes = None
    ):
        """
        Initialize a BlockHeader instance.
        
        Args:
            version: Block version number
            previous_hash: Hash of the previous block
            merkle_root: Merkle root of transactions
            timestamp: Block creation timestamp
            height: Block height in the chain
            validator_signature: Signature of the validator that created the block
            validator_cluster_id: ID of the validator cluster that created the block
            synergy_points: Dictionary mapping validator IDs to Synergy Points
            difficulty: Block difficulty target
            nonce: Nonce value for the block
        """
        self.version = version
        self.previous_hash = previous_hash or bytes(32)  # Default to zero hash
        self.merkle_root = merkle_root or bytes(32)  # Default to zero hash
        self.timestamp = timestamp or int(time.time())
        self.height = height
        self.validator_signature = validator_signature
        self.validator_cluster_id = validator_cluster_id
        self.synergy_points = synergy_points or {}
        self.difficulty = difficulty
        self.nonce = nonce or bytes(32)  # Default to zero bytes
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert BlockHeader to dictionary.
        
        Returns:
            Dictionary representation of the block header
        """
        return {
            "version": self.version,
            "previous_hash": self.previous_hash.hex(),
            "merkle_root": self.merkle_root.hex(),
            "timestamp": self.timestamp,
            "height": self.height,
            "validator_signature": self.validator_signature.hex() if self.validator_signature else None,
            "validator_cluster_id": self.validator_cluster_id,
            "synergy_points": self.synergy_points,
            "difficulty": self.difficulty,
            "nonce": self.nonce.hex()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BlockHeader':
        """
        Create BlockHeader from dictionary.
        
        Args:
            data: Dictionary representation of the block header
        
        Returns:
            BlockHeader instance
        """
        return cls(
            version=data.get("version", 1),
            previous_hash=bytes.fromhex(data["previous_hash"]) if "previous_hash" in data else None,
            merkle_root=bytes.fromhex(data["merkle_root"]) if "merkle_root" in data else None,
            timestamp=data.get("timestamp"),
            height=data.get("height", 0),
            validator_signature=bytes.fromhex(data["validator_signature"]) if data.get("validator_signature") else None,
            validator_cluster_id=data.get("validator_cluster_id"),
            synergy_points=data.get("synergy_points", {}),
            difficulty=data.get("difficulty", 1),
            nonce=bytes.fromhex(data["nonce"]) if "nonce" in data else None
        )
    
    def get_hash(self) -> bytes:
        """
        Compute the hash of the block header.
        
        Returns:
            32-byte hash digest
        """
        # Create a dictionary representation without the signature
        header_dict = self.to_dict()
        header_dict.pop("validator_signature", None)
        
        # Use the hash function from the cryptography package
        return HashFunctions.hash_block(header_dict)
    
    def serialize(self) -> bytes:
        """
        Serialize the block header to bytes.
        
        Returns:
            Serialized block header
        """
        return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')

class Block:
    """Class representing a block in the Synergy Network."""
    
    def __init__(
        self,
        header: BlockHeader = None,
        transactions: List[Dict[str, Any]] = None
    ):
        """
        Initialize a Block instance.
        
        Args:
            header: Block header
            transactions: List of transactions
        """
        self.header = header or BlockHeader()
        self.transactions = transactions or []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Block to dictionary.
        
        Returns:
            Dictionary representation of the block
        """
        return {
            "header": self.header.to_dict(),
            "transactions": self.transactions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """
        Create Block from dictionary.
        
        Args:
            data: Dictionary representation of the block
        
        Returns:
            Block instance
        """
        return cls(
            header=BlockHeader.from_dict(data["header"]),
            transactions=data.get("transactions", [])
        )
    
    def serialize(self) -> bytes:
        """
        Serialize the block to bytes.
        
        Returns:
            Serialized block
        """
        return json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'Block':
        """
        Deserialize bytes to a Block.
        
        Args:
            data: Serialized block
        
        Returns:
            Block instance
        """
        block_dict = json.loads(data.decode('utf-8'))
        return cls.from_dict(block_dict)
    
    def get_hash(self) -> bytes:
        """
        Compute the hash of the block.
        
        Returns:
            32-byte hash digest
        """
        return self.header.get_hash()
    
    def calculate_merkle_root(self) -> bytes:
        """
        Calculate the Merkle root of the block's transactions.
        
        Returns:
            32-byte Merkle root hash
        """
        # If no transactions, return zero hash
        if not self.transactions:
            return bytes(32)
        
        # Calculate transaction hashes
        tx_hashes = []
        for tx in self.transactions:
            tx_hash = HashFunctions.hash_transaction(tx)
            tx_hashes.append(tx_hash)
        
        # Calculate Merkle root
        merkle_root = HashFunctions.merkle_root(tx_hashes)
        
        # Update header's Merkle root
        self.header.merkle_root = merkle_root
        
        return merkle_root
    
    def add_transaction(self, transaction: Dict[str, Any]) -> bool:
        """
        Add a transaction to the block.
        
        Args:
            transaction: Transaction data
        
        Returns:
            True if transaction was added, False otherwise
        """
        # Add transaction to list
        self.transactions.append(transaction)
        
        # Recalculate Merkle root
        self.calculate_merkle_root()
        
        return True
    
    def verify(self) -> bool:
        """
        Verify the block's integrity.
        
        Returns:
            True if the block is valid, False otherwise
        """
        # Verify Merkle root
        calculated_root = self.calculate_merkle_root()
        if calculated_root != self.header.merkle_root:
            return False
        
        # Verify block hash meets difficulty requirement
        block_hash = self.get_hash()
        # Simple difficulty check: number of leading zero bytes
        leading_zeros = 0
        for byte in block_hash:
            if byte == 0:
                leading_zeros += 1
            else:
                break
        
        return leading_zeros >= self.header.difficulty

class GenesisBlock:
    """Class for generating the Genesis block of the Synergy Network."""
    
    @staticmethod
    def create() -> Block:
        """
        Create the Genesis block.
        
        Returns:
            Genesis Block instance
        """
        # Create block header
        header = BlockHeader(
            version=1,
            previous_hash=bytes(32),  # Zero hash
            timestamp=int(time.time()),
            height=0,
            difficulty=1
        )
        
        # Create Genesis block
        genesis = Block(header=header)
        
        # Add a coinbase transaction
        coinbase_tx = {
            "type": "coinbase",
            "timestamp": header.timestamp,
            "outputs": [
                {
                    "address": "sYnQsyn1synergy0000000000000000000000000000000",
                    "amount": 10000000000  # Initial supply: 10 billion SYN
                }
            ],
            "data": "Synergy Network Genesis Block - " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(header.timestamp))
        }
        
        genesis.add_transaction(coinbase_tx)
        
        return genesis

class BlockBuilder:
    """Class for building blocks in the Synergy Network."""
    
    def __init__(
        self,
        previous_block: Block,
        validator_id: str,
        cluster_id: str,
        synergy_points: Dict[str, int] = None
    ):
        """
        Initialize a BlockBuilder instance.
        
        Args:
            previous_block: Previous block in the chain
            validator_id: ID of the validator building the block
            cluster_id: ID of the validator cluster
            synergy_points: Dictionary mapping validator IDs to Synergy Points
        """
        self.previous_block = previous_block
        self.validator_id = validator_id
        self.cluster_id = cluster_id
        
        # Create new block header
        self.header = BlockHeader(
            version=1,
            previous_hash=previous_block.get_hash(),
            timestamp=int(time.time()),
            height=previous_block.header.height + 1,
            validator_cluster_id=cluster_id,
            synergy_points=synergy_points or {},
            difficulty=previous_block.header.difficulty  # For simplicity, keep same difficulty
        )
        
        # Create new block
        self.block = Block(header=self.header)
    
    def add_transaction(self, transaction: Dict[str, Any]) -> bool:
        """
        Add a transaction to the block.
        
        Args:
            transaction: Transaction data
        
        Returns:
            True if transaction was added, False otherwise
        """
        return self.block.add_transaction(transaction)
    
    def sign_block(self, private_key: bytes) -> bool:
        """
        Sign the block with the validator's private key.
        
        Args:
            private_key: Validator's private key
        
        Returns:
            True if block was signed, False otherwise
        """
        # Import the Dilithium signer
        from implementation.cryptography.pqc.dilithium import DilithiumSigner
        
        # Calculate block hash
        block_hash = self.block.get_hash()
        
        # Sign the block hash
        signature = DilithiumSigner.sign(block_hash, private_key)
        
        # Set the signature in the header
        self.block.header.validator_signature = signature
        
        return True
    
    def finalize(self) -> Block:
        """
        Finalize the block.
        
        Returns:
            Finalized Block instance
        """
        # Recalculate Merkle root
        self.block.calculate_merkle_root()
        
        return self.block

# Example usage
if __name__ == "__main__":
    # Create Genesis block
    genesis = GenesisBlock.create()
    print("Genesis Block:")
    print(f"Height: {genesis.header.height}")
    print(f"Hash: {genesis.get_hash().hex()}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(genesis.header.timestamp))}")
    print(f"Transactions: {len(genesis.transactions)}")
    
    # Create a block builder
    builder = BlockBuilder(
        previous_block=genesis,
        validator_id="validator_1",
        cluster_id="cluster_1",
        synergy_points={"validator_1": 100, "validator_2": 75, "validator_3": 50}
    )
    
    # Add some transactions
    builder.add_transaction({
        "type": "transfer",
        "from": "sYnQsyn1user1000000000000000000000000000000000",
        "to": "sYnQsyn1user2000000000000000000000000000000000",
        "amount": 100,
        "fee": 1,
        "nonce": 1,
        "timestamp": int(time.time())
    })
    
    builder.add_transaction({
        "type": "transfer",
        "from": "sYnQsyn1user2000000000000000000000000000000000",
        "to": "sYnQsyn1user3000000000000000000000000000000000",
        "amount": 50,
        "fee": 1,
        "nonce": 2,
        "timestamp": int(time.time())
    })
    
    # Finalize the block
    block = builder.finalize()
    
    print("\nNew Block:")
    print(f"Height: {block.header.height}")
    print(f"Previous Hash: {block.header.previous_hash.hex()}")
    print(f"Hash: {block.get_hash().hex()}")
    print(f"Merkle Root: {block.header.merkle_root.hex()}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(block.header.timestamp))}")
    print(f"Transactions: {len(block.transactions)}")
    
    # Serialize and deserialize
    serialized = block.serialize()
    deserialized = Block.deserialize(serialized)
    
    print("\nDeserialized Block:")
    print(f"Height: {deserialized.header.height}")
    print(f"Hash: {deserialized.get_hash().hex()}")
    print(f"Transactions: {len(deserialized.transactions)}")
    
    # Verify blocks match
    print(f"\nHashes match: {block.get_hash() == deserialized.get_hash()}")
