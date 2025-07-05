"""
Dilithium Module for Synergy Network

This module implements the CRYSTALS-Dilithium digital signature scheme
for the Synergy Network's Post-Quantum Cryptography layer.
"""

import os
import hashlib
import json
import base64
from typing import Dict, Tuple, Any, Optional, Union, List

try:
    # Try to import the pqcrypto library if available
    from pqcrypto.sign import dilithium3
    NATIVE_IMPLEMENTATION = True
except ImportError:
    # Fallback to a simulated implementation
    NATIVE_IMPLEMENTATION = False
    print("Warning: Using simulated Dilithium implementation. For production use, install pqcrypto.")

class DilithiumKeys:
    """Class representing a key pair for the Dilithium signature scheme."""
    
    def __init__(self, public_key: bytes, private_key: bytes):
        """
        Initialize a DilithiumKeys instance.
        
        Args:
            public_key: The public key bytes
            private_key: The private key bytes
        """
        self.public_key = public_key
        self.private_key = private_key
    
    def to_dict(self) -> Dict[str, str]:
        """
        Convert keys to a dictionary with base64-encoded strings.
        
        Returns:
            Dictionary with base64-encoded keys
        """
        return {
            "public_key": base64.b64encode(self.public_key).decode('utf-8'),
            "private_key": base64.b64encode(self.private_key).decode('utf-8')
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'DilithiumKeys':
        """
        Create DilithiumKeys from a dictionary with base64-encoded strings.
        
        Args:
            data: Dictionary with base64-encoded keys
        
        Returns:
            DilithiumKeys instance
        """
        return cls(
            public_key=base64.b64decode(data["public_key"]),
            private_key=base64.b64decode(data["private_key"])
        )
    
    def save_to_file(self, filename_prefix: str, password: Optional[str] = None) -> Tuple[str, str]:
        """
        Save keys to files.
        
        Args:
            filename_prefix: Prefix for the filenames
            password: Optional password to encrypt the private key
        
        Returns:
            Tuple of (public_key_filename, private_key_filename)
        """
        public_key_filename = f"{filename_prefix}.pub"
        private_key_filename = f"{filename_prefix}.priv"
        
        # Save public key
        with open(public_key_filename, 'wb') as f:
            f.write(self.public_key)
        
        # Save private key (optionally encrypted)
        if password:
            from Crypto.Cipher import AES
            from Crypto.Protocol.KDF import scrypt
            from Crypto.Random import get_random_bytes
            
            # Generate key from password
            salt = get_random_bytes(16)
            key = scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)
            
            # Encrypt private key
            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(self.private_key)
            
            # Save encrypted private key
            with open(private_key_filename, 'wb') as f:
                f.write(salt)
                f.write(cipher.nonce)
                f.write(tag)
                f.write(ciphertext)
        else:
            # Save unencrypted private key
            with open(private_key_filename, 'wb') as f:
                f.write(self.private_key)
        
        return public_key_filename, private_key_filename
    
    @classmethod
    def load_from_file(cls, filename_prefix: str, password: Optional[str] = None) -> 'DilithiumKeys':
        """
        Load keys from files.
        
        Args:
            filename_prefix: Prefix for the filenames
            password: Optional password to decrypt the private key
        
        Returns:
            DilithiumKeys instance
        """
        public_key_filename = f"{filename_prefix}.pub"
        private_key_filename = f"{filename_prefix}.priv"
        
        # Load public key
        with open(public_key_filename, 'rb') as f:
            public_key = f.read()
        
        # Load private key (optionally encrypted)
        with open(private_key_filename, 'rb') as f:
            private_key_data = f.read()
        
        if password:
            from Crypto.Cipher import AES
            from Crypto.Protocol.KDF import scrypt
            
            # Extract components
            salt = private_key_data[:16]
            nonce = private_key_data[16:32]
            tag = private_key_data[32:48]
            ciphertext = private_key_data[48:]
            
            # Generate key from password
            key = scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)
            
            # Decrypt private key
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            private_key = cipher.decrypt_and_verify(ciphertext, tag)
        else:
            # Unencrypted private key
            private_key = private_key_data
        
        return cls(public_key=public_key, private_key=private_key)

class DilithiumSigner:
    """Class for signing and verifying messages using the Dilithium signature scheme."""
    
    @staticmethod
    def generate_keypair() -> DilithiumKeys:
        """
        Generate a new Dilithium key pair.
        
        Returns:
            DilithiumKeys instance with the generated key pair
        """
        if NATIVE_IMPLEMENTATION:
            # Use the native implementation
            public_key, private_key = dilithium3.keypair()
            return DilithiumKeys(public_key=public_key, private_key=private_key)
        else:
            # Simulated implementation (NOT SECURE, FOR TESTING ONLY)
            # In a real implementation, this would use a proper Dilithium library
            private_key = os.urandom(32)
            public_key = hashlib.sha256(private_key).digest() + os.urandom(32)
            return DilithiumKeys(public_key=public_key, private_key=private_key)
    
    @staticmethod
    def sign(message: Union[bytes, str], private_key: bytes) -> bytes:
        """
        Sign a message using a Dilithium private key.
        
        Args:
            message: The message to sign (bytes or string)
            private_key: The private key bytes
        
        Returns:
            Signature bytes
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        if NATIVE_IMPLEMENTATION:
            # Use the native implementation
            return dilithium3.sign(message, private_key)
        else:
            # Simulated implementation (NOT SECURE, FOR TESTING ONLY)
            # In a real implementation, this would use a proper Dilithium library
            h = hashlib.sha256(message + private_key).digest()
            return h + os.urandom(2048)  # Simulate Dilithium signature size
    
    @staticmethod
    def verify(message: Union[bytes, str], signature: bytes, public_key: bytes) -> bool:
        """
        Verify a signature using a Dilithium public key.
        
        Args:
            message: The message that was signed (bytes or string)
            signature: The signature bytes
            public_key: The public key bytes
        
        Returns:
            True if the signature is valid, False otherwise
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        if NATIVE_IMPLEMENTATION:
            # Use the native implementation
            try:
                dilithium3.verify(message, signature, public_key)
                return True
            except Exception:
                return False
        else:
            # Simulated implementation (NOT SECURE, FOR TESTING ONLY)
            # In a real implementation, this would use a proper Dilithium library
            h = hashlib.sha256(message + public_key[:32]).digest()
            return h == signature[:32]  # Simple check for testing
    
    @staticmethod
    def batch_verify(
        messages: List[Union[bytes, str]],
        signatures: List[bytes],
        public_keys: List[bytes]
    ) -> List[bool]:
        """
        Verify multiple signatures in batch.
        
        Args:
            messages: List of messages
            signatures: List of signatures
            public_keys: List of public keys
        
        Returns:
            List of booleans indicating validity of each signature
        """
        if len(messages) != len(signatures) or len(messages) != len(public_keys):
            raise ValueError("Number of messages, signatures, and public keys must be equal")
        
        results = []
        for i in range(len(messages)):
            results.append(DilithiumSigner.verify(messages[i], signatures[i], public_keys[i]))
        
        return results

class DilithiumKeyManager:
    """Class for managing Dilithium keys for the Synergy Network."""
    
    def __init__(self, keys_dir: str = "keys"):
        """
        Initialize a DilithiumKeyManager instance.
        
        Args:
            keys_dir: Directory to store keys
        """
        self.keys_dir = keys_dir
        os.makedirs(keys_dir, exist_ok=True)
    
    def generate_network_keys(self, node_id: str, password: Optional[str] = None) -> DilithiumKeys:
        """
        Generate network keys for a node.
        
        Args:
            node_id: ID of the node
            password: Optional password to encrypt the private key
        
        Returns:
            Generated DilithiumKeys
        """
        keys = DilithiumSigner.generate_keypair()
        filename_prefix = os.path.join(self.keys_dir, f"node_{node_id}")
        keys.save_to_file(filename_prefix, password)
        return keys
    
    def load_network_keys(self, node_id: str, password: Optional[str] = None) -> DilithiumKeys:
        """
        Load network keys for a node.
        
        Args:
            node_id: ID of the node
            password: Optional password to decrypt the private key
        
        Returns:
            Loaded DilithiumKeys
        """
        filename_prefix = os.path.join(self.keys_dir, f"node_{node_id}")
        return DilithiumKeys.load_from_file(filename_prefix, password)
    
    def generate_user_keys(self, user_id: str, password: Optional[str] = None) -> DilithiumKeys:
        """
        Generate user keys.
        
        Args:
            user_id: ID of the user
            password: Optional password to encrypt the private key
        
        Returns:
            Generated DilithiumKeys
        """
        keys = DilithiumSigner.generate_keypair()
        filename_prefix = os.path.join(self.keys_dir, f"user_{user_id}")
        keys.save_to_file(filename_prefix, password)
        return keys
    
    def load_user_keys(self, user_id: str, password: Optional[str] = None) -> DilithiumKeys:
        """
        Load user keys.
        
        Args:
            user_id: ID of the user
            password: Optional password to decrypt the private key
        
        Returns:
            Loaded DilithiumKeys
        """
        filename_prefix = os.path.join(self.keys_dir, f"user_{user_id}")
        return DilithiumKeys.load_from_file(filename_prefix, password)
    
    def derive_address(self, public_key: bytes, prefix: Optional[str] = None) -> str:
        """
        Derive a Synergy Network address from a public key.
        
        Args:
            public_key: The public key bytes
            prefix: Optional address prefix ('sYnQ' or 'sYnU')
        
        Returns:
            Synergy Network address
        """
        from .address import AddressGenerator
        return AddressGenerator.generate_address(public_key, prefix)

# Example usage
if __name__ == "__main__":
    # Generate a key pair
    print("Generating Dilithium key pair...")
    keys = DilithiumSigner.generate_keypair()
    
    # Print key information
    print(f"Public key size: {len(keys.public_key)} bytes")
    print(f"Private key size: {len(keys.private_key)} bytes")
    
    # Sign a message
    message = "Hello, Synergy Network!"
    print(f"\nSigning message: '{message}'")
    signature = DilithiumSigner.sign(message, keys.private_key)
    print(f"Signature size: {len(signature)} bytes")
    
    # Verify the signature
    print("\nVerifying signature...")
    is_valid = DilithiumSigner.verify(message, signature, keys.public_key)
    print(f"Signature valid: {is_valid}")
    
    # Test with a modified message
    modified_message = "Hello, Modified Message!"
    print(f"\nVerifying with modified message: '{modified_message}'")
    is_valid = DilithiumSigner.verify(modified_message, signature, keys.public_key)
    print(f"Signature valid: {is_valid}")
    
    # Save and load keys
    print("\nSaving keys to files...")
    key_manager = DilithiumKeyManager()
    keys.save_to_file("test_dilithium")
    
    print("Loading keys from files...")
    loaded_keys = DilithiumKeys.load_from_file("test_dilithium")
    
    print("Verifying with loaded keys...")
    is_valid = DilithiumSigner.verify(message, signature, loaded_keys.public_key)
    print(f"Signature valid: {is_valid}")
    
    # Test with password protection
    print("\nSaving keys with password protection...")
    password = "secure_password"
    keys.save_to_file("test_dilithium_encrypted", password)
    
    print("Loading keys with password...")
    loaded_keys = DilithiumKeys.load_from_file("test_dilithium_encrypted", password)
    
    print("Verifying with loaded keys...")
    is_valid = DilithiumSigner.verify(message, signature, loaded_keys.public_key)
    print(f"Signature valid: {is_valid}")
