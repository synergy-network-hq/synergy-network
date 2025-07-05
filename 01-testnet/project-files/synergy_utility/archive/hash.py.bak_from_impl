"""
Hash Module for Synergy Network

This module implements the hash functions used in the Synergy Network,
including SHA3-256 and BLAKE3 for various cryptographic operations.
"""

import hashlib
from typing import Union, Optional

try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False
    print("Warning: BLAKE3 library not available. Using fallback implementation.")

class HashFunctions:
    """Class providing hash functions for the Synergy Network."""
    
    @staticmethod
    def sha3_256(data: Union[bytes, str]) -> bytes:
        """
        Compute the SHA3-256 hash of data.
        
        Args:
            data: Input data (bytes or string)
        
        Returns:
            32-byte hash digest
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return hashlib.sha3_256(data).digest()
    
    @staticmethod
    def blake3_hash(data: Union[bytes, str], output_length: int = 32) -> bytes:
        """
        Compute the BLAKE3 hash of data.
        
        Args:
            data: Input data (bytes or string)
            output_length: Length of output in bytes (default: 32)
        
        Returns:
            Hash digest of specified length
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if BLAKE3_AVAILABLE:
            # Use native BLAKE3 implementation
            hasher = blake3.blake3(data)
            return hasher.digest(length=output_length)
        else:
            # Fallback to SHA3 with different lengths
            if output_length <= 32:
                # Use SHA3-256 and truncate if needed
                hash_value = hashlib.sha3_256(data).digest()
                return hash_value[:output_length]
            else:
                # For longer outputs, use multiple SHA3-256 hashes
                result = bytearray()
                counter = 0
                while len(result) < output_length:
                    # Add counter to data to get different hashes
                    counter_bytes = counter.to_bytes(4, byteorder='big')
                    hash_value = hashlib.sha3_256(data + counter_bytes).digest()
                    
                    # Add as much as needed
                    remaining = output_length - len(result)
                    result.extend(hash_value[:min(32, remaining)])
                    
                    counter += 1
                
                return bytes(result)
    
    @staticmethod
    def hash_transaction(tx_data: dict) -> bytes:
        """
        Compute the hash of a transaction.
        
        Args:
            tx_data: Transaction data as a dictionary
        
        Returns:
            32-byte hash digest
        """
        # Create a deterministic serialization of the transaction
        import json
        serialized = json.dumps(tx_data, sort_keys=True, separators=(',', ':')).encode('utf-8')
        
        # Use SHA3-256 for transaction hashing
        return HashFunctions.sha3_256(serialized)
    
    @staticmethod
    def hash_block(block_header: dict) -> bytes:
        """
        Compute the hash of a block header.
        
        Args:
            block_header: Block header data as a dictionary
        
        Returns:
            32-byte hash digest
        """
        # Create a deterministic serialization of the block header
        import json
        serialized = json.dumps(block_header, sort_keys=True, separators=(',', ':')).encode('utf-8')
        
        # Use SHA3-256 for block hashing
        return HashFunctions.sha3_256(serialized)
    
    @staticmethod
    def merkle_root(hashes: list) -> bytes:
        """
        Compute the Merkle root of a list of hashes.
        
        Args:
            hashes: List of hash digests (bytes)
        
        Returns:
            32-byte Merkle root hash
        """
        if not hashes:
            # Empty list, return zero hash
            return bytes(32)
        
        if len(hashes) == 1:
            # Single hash, return it
            return hashes[0]
        
        # Make sure we have an even number of hashes
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])  # Duplicate last hash
        
        # Compute next level of tree
        next_level = []
        for i in range(0, len(hashes), 2):
            # Concatenate adjacent hashes and hash them
            combined = hashes[i] + hashes[i+1]
            next_hash = HashFunctions.sha3_256(combined)
            next_level.append(next_hash)
        
        # Recurse to compute root of next level
        return HashFunctions.merkle_root(next_level)
    
    @staticmethod
    def kdf(password: Union[bytes, str], salt: bytes, length: int = 32) -> bytes:
        """
        Key derivation function for password-based keys.
        
        Args:
            password: Password (bytes or string)
            salt: Salt value
            length: Desired key length in bytes
        
        Returns:
            Derived key of specified length
        """
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        # Use Argon2id for password hashing
        try:
            from argon2 import low_level
            return low_level.hash_secret_raw(
                secret=password,
                salt=salt,
                time_cost=3,
                memory_cost=65536,
                parallelism=4,
                hash_len=length,
                type=low_level.Type.ID
            )
        except ImportError:
            # Fallback to PBKDF2 if Argon2 is not available
            import hashlib
            from Crypto.Protocol.KDF import PBKDF2
            
            return PBKDF2(
                password=password,
                salt=salt,
                dkLen=length,
                count=100000,
                prf=lambda p, s: hashlib.sha3_256(p + s).digest()
            )

# Example usage
if __name__ == "__main__":
    # Test SHA3-256
    message = "Hello, Synergy Network!"
    sha3_hash = HashFunctions.sha3_256(message)
    print(f"SHA3-256 hash of '{message}': {sha3_hash.hex()}")
    
    # Test BLAKE3
    blake3_hash = HashFunctions.blake3_hash(message)
    print(f"BLAKE3 hash of '{message}': {blake3_hash.hex()}")
    
    # Test transaction hashing
    tx = {
        "from": "sYnQsyn1abc123",
        "to": "sYnUsyn1def456",
        "value": 100,
        "nonce": 5,
        "data": "0x",
        "gas_limit": 21000,
        "gas_price": 1
    }
    tx_hash = HashFunctions.hash_transaction(tx)
    print(f"Transaction hash: {tx_hash.hex()}")
    
    # Test Merkle root
    hashes = [
        HashFunctions.sha3_256(f"Transaction {i}".encode())
        for i in range(7)
    ]
    merkle_root = HashFunctions.merkle_root(hashes)
    print(f"Merkle root of 7 transactions: {merkle_root.hex()}")
    
    # Test KDF
    password = "secure_password"
    salt = b"synergy_salt"
    derived_key = HashFunctions.kdf(password, salt)
    print(f"Derived key from password: {derived_key.hex()}")
