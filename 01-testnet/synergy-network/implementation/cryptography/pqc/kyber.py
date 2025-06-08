"""
Kyber Module for Synergy Network

This module implements the CRYSTALS-Kyber key encapsulation mechanism (KEM)
for the Synergy Network's Post-Quantum Cryptography layer.
"""

import os
import hashlib
import json
import base64
from typing import Dict, Tuple, Any, Optional, Union, List

try:
    # Try to import the pqcrypto library if available
    from pqcrypto.kem import kyber768
    NATIVE_IMPLEMENTATION = True
except ImportError:
    # Fallback to a simulated implementation
    NATIVE_IMPLEMENTATION = False
    print("Warning: Using simulated Kyber implementation. For production use, install pqcrypto.")

class KyberKeys:
    """Class representing a key pair for the Kyber KEM."""
    
    def __init__(self, public_key: bytes, secret_key: bytes):
        """
        Initialize a KyberKeys instance.
        
        Args:
            public_key: The public key bytes
            secret_key: The secret key bytes
        """
        self.public_key = public_key
        self.secret_key = secret_key
    
    def to_dict(self) -> Dict[str, str]:
        """
        Convert keys to a dictionary with base64-encoded strings.
        
        Returns:
            Dictionary with base64-encoded keys
        """
        return {
            "public_key": base64.b64encode(self.public_key).decode('utf-8'),
            "secret_key": base64.b64encode(self.secret_key).decode('utf-8')
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'KyberKeys':
        """
        Create KyberKeys from a dictionary with base64-encoded strings.
        
        Args:
            data: Dictionary with base64-encoded keys
        
        Returns:
            KyberKeys instance
        """
        return cls(
            public_key=base64.b64decode(data["public_key"]),
            secret_key=base64.b64decode(data["secret_key"])
        )
    
    def save_to_file(self, filename_prefix: str, password: Optional[str] = None) -> Tuple[str, str]:
        """
        Save keys to files.
        
        Args:
            filename_prefix: Prefix for the filenames
            password: Optional password to encrypt the secret key
        
        Returns:
            Tuple of (public_key_filename, secret_key_filename)
        """
        public_key_filename = f"{filename_prefix}.pub"
        secret_key_filename = f"{filename_prefix}.sec"
        
        # Save public key
        with open(public_key_filename, 'wb') as f:
            f.write(self.public_key)
        
        # Save secret key (optionally encrypted)
        if password:
            from Crypto.Cipher import AES
            from Crypto.Protocol.KDF import scrypt
            from Crypto.Random import get_random_bytes
            
            # Generate key from password
            salt = get_random_bytes(16)
            key = scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)
            
            # Encrypt secret key
            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(self.secret_key)
            
            # Save encrypted secret key
            with open(secret_key_filename, 'wb') as f:
                f.write(salt)
                f.write(cipher.nonce)
                f.write(tag)
                f.write(ciphertext)
        else:
            # Save unencrypted secret key
            with open(secret_key_filename, 'wb') as f:
                f.write(self.secret_key)
        
        return public_key_filename, secret_key_filename
    
    @classmethod
    def load_from_file(cls, filename_prefix: str, password: Optional[str] = None) -> 'KyberKeys':
        """
        Load keys from files.
        
        Args:
            filename_prefix: Prefix for the filenames
            password: Optional password to decrypt the secret key
        
        Returns:
            KyberKeys instance
        """
        public_key_filename = f"{filename_prefix}.pub"
        secret_key_filename = f"{filename_prefix}.sec"
        
        # Load public key
        with open(public_key_filename, 'rb') as f:
            public_key = f.read()
        
        # Load secret key (optionally encrypted)
        with open(secret_key_filename, 'rb') as f:
            secret_key_data = f.read()
        
        if password:
            from Crypto.Cipher import AES
            from Crypto.Protocol.KDF import scrypt
            
            # Extract components
            salt = secret_key_data[:16]
            nonce = secret_key_data[16:32]
            tag = secret_key_data[32:48]
            ciphertext = secret_key_data[48:]
            
            # Generate key from password
            key = scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)
            
            # Decrypt secret key
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            secret_key = cipher.decrypt_and_verify(ciphertext, tag)
        else:
            # Unencrypted secret key
            secret_key = secret_key_data
        
        return cls(public_key=public_key, secret_key=secret_key)

class KyberKEM:
    """Class for key encapsulation using the Kyber KEM."""
    
    @staticmethod
    def generate_keypair() -> KyberKeys:
        """
        Generate a new Kyber key pair.
        
        Returns:
            KyberKeys instance with the generated key pair
        """
        if NATIVE_IMPLEMENTATION:
            # Use the native implementation
            public_key, secret_key = kyber768.keypair()
            return KyberKeys(public_key=public_key, secret_key=secret_key)
        else:
            # Simulated implementation (NOT SECURE, FOR TESTING ONLY)
            # In a real implementation, this would use a proper Kyber library
            secret_key = os.urandom(32)
            public_key = hashlib.sha256(secret_key).digest() + os.urandom(32)
            return KyberKeys(public_key=public_key, secret_key=secret_key)
    
    @staticmethod
    def encapsulate(public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Encapsulate a shared secret using a Kyber public key.
        
        Args:
            public_key: The public key bytes
        
        Returns:
            Tuple of (ciphertext, shared_secret)
        """
        if NATIVE_IMPLEMENTATION:
            # Use the native implementation
            ciphertext, shared_secret = kyber768.encap(public_key)
            return ciphertext, shared_secret
        else:
            # Simulated implementation (NOT SECURE, FOR TESTING ONLY)
            # In a real implementation, this would use a proper Kyber library
            shared_secret = os.urandom(32)
            ciphertext = hashlib.sha256(shared_secret + public_key).digest() + os.urandom(1024)
            return ciphertext, shared_secret
    
    @staticmethod
    def decapsulate(ciphertext: bytes, secret_key: bytes) -> bytes:
        """
        Decapsulate a shared secret using a Kyber secret key.
        
        Args:
            ciphertext: The ciphertext bytes
            secret_key: The secret key bytes
        
        Returns:
            Shared secret bytes
        """
        if NATIVE_IMPLEMENTATION:
            # Use the native implementation
            return kyber768.decap(ciphertext, secret_key)
        else:
            # Simulated implementation (NOT SECURE, FOR TESTING ONLY)
            # In a real implementation, this would use a proper Kyber library
            # This is just a placeholder that returns a deterministic value based on inputs
            return hashlib.sha256(ciphertext + secret_key).digest()

class HybridEncryption:
    """Class for hybrid encryption using Kyber KEM and symmetric encryption."""
    
    @staticmethod
    def encrypt(message: Union[bytes, str], recipient_public_key: bytes) -> Dict[str, str]:
        """
        Encrypt a message using Kyber KEM and AES-GCM.
        
        Args:
            message: The message to encrypt (bytes or string)
            recipient_public_key: The recipient's Kyber public key
        
        Returns:
            Dictionary with base64-encoded ciphertext and metadata
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Encapsulate a shared secret
        ciphertext, shared_secret = KyberKEM.encapsulate(recipient_public_key)
        
        # Use the shared secret for symmetric encryption
        from Crypto.Cipher import AES
        from Crypto.Random import get_random_bytes
        
        # Generate nonce
        nonce = get_random_bytes(12)
        
        # Create cipher and encrypt
        cipher = AES.new(shared_secret, AES.MODE_GCM, nonce=nonce)
        encrypted_data, tag = cipher.encrypt_and_digest(message)
        
        # Return all components
        return {
            "kyber_ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "encrypted_data": base64.b64encode(encrypted_data).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "tag": base64.b64encode(tag).decode('utf-8')
        }
    
    @staticmethod
    def decrypt(encrypted_data: Dict[str, str], recipient_secret_key: bytes) -> bytes:
        """
        Decrypt a message using Kyber KEM and AES-GCM.
        
        Args:
            encrypted_data: Dictionary with base64-encoded ciphertext and metadata
            recipient_secret_key: The recipient's Kyber secret key
        
        Returns:
            Decrypted message bytes
        """
        # Decode components
        kyber_ciphertext = base64.b64decode(encrypted_data["kyber_ciphertext"])
        encrypted_message = base64.b64decode(encrypted_data["encrypted_data"])
        nonce = base64.b64decode(encrypted_data["nonce"])
        tag = base64.b64decode(encrypted_data["tag"])
        
        # Decapsulate the shared secret
        shared_secret = KyberKEM.decapsulate(kyber_ciphertext, recipient_secret_key)
        
        # Use the shared secret for symmetric decryption
        from Crypto.Cipher import AES
        
        # Create cipher and decrypt
        cipher = AES.new(shared_secret, AES.MODE_GCM, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(encrypted_message, tag)
        
        return decrypted_data

class KyberKeyManager:
    """Class for managing Kyber keys for the Synergy Network."""
    
    def __init__(self, keys_dir: str = "keys"):
        """
        Initialize a KyberKeyManager instance.
        
        Args:
            keys_dir: Directory to store keys
        """
        self.keys_dir = keys_dir
        os.makedirs(keys_dir, exist_ok=True)
    
    def generate_encryption_keys(self, entity_id: str, password: Optional[str] = None) -> KyberKeys:
        """
        Generate encryption keys for an entity.
        
        Args:
            entity_id: ID of the entity
            password: Optional password to encrypt the secret key
        
        Returns:
            Generated KyberKeys
        """
        keys = KyberKEM.generate_keypair()
        filename_prefix = os.path.join(self.keys_dir, f"kyber_{entity_id}")
        keys.save_to_file(filename_prefix, password)
        return keys
    
    def load_encryption_keys(self, entity_id: str, password: Optional[str] = None) -> KyberKeys:
        """
        Load encryption keys for an entity.
        
        Args:
            entity_id: ID of the entity
            password: Optional password to decrypt the secret key
        
        Returns:
            Loaded KyberKeys
        """
        filename_prefix = os.path.join(self.keys_dir, f"kyber_{entity_id}")
        return KyberKeys.load_from_file(filename_prefix, password)

# Example usage
if __name__ == "__main__":
    # Generate a key pair
    print("Generating Kyber key pair...")
    keys = KyberKEM.generate_keypair()
    
    # Print key information
    print(f"Public key size: {len(keys.public_key)} bytes")
    print(f"Secret key size: {len(keys.secret_key)} bytes")
    
    # Encapsulate a shared secret
    print("\nEncapsulating shared secret...")
    ciphertext, shared_secret = KyberKEM.encapsulate(keys.public_key)
    print(f"Ciphertext size: {len(ciphertext)} bytes")
    print(f"Shared secret size: {len(shared_secret)} bytes")
    
    # Decapsulate the shared secret
    print("\nDecapsulating shared secret...")
    decapsulated_secret = KyberKEM.decapsulate(ciphertext, keys.secret_key)
    print(f"Decapsulated secret size: {len(decapsulated_secret)} bytes")
    print(f"Secrets match: {shared_secret == decapsulated_secret}")
    
    # Test hybrid encryption
    message = "This is a secret message for Synergy Network!"
    print(f"\nEncrypting message: '{message}'")
    encrypted = HybridEncryption.encrypt(message, keys.public_key)
    
    print("Encrypted data:")
    for key, value in encrypted.items():
        print(f"  {key}: {value[:20]}...")
    
    # Decrypt the message
    print("\nDecrypting message...")
    decrypted = HybridEncryption.decrypt(encrypted, keys.secret_key)
    print(f"Decrypted message: '{decrypted.decode('utf-8')}'")
    
    # Save and load keys
    print("\nSaving keys to files...")
    key_manager = KyberKeyManager()
    keys.save_to_file("test_kyber")
    
    print("Loading keys from files...")
    loaded_keys = KyberKeys.load_from_file("test_kyber")
    
    # Test with loaded keys
    print("\nTesting with loaded keys...")
    decapsulated_secret = KyberKEM.decapsulate(ciphertext, loaded_keys.secret_key)
    print(f"Secrets match with loaded keys: {shared_secret == decapsulated_secret}")
    
    # Test with password protection
    print("\nSaving keys with password protection...")
    password = "secure_password"
    keys.save_to_file("test_kyber_encrypted", password)
    
    print("Loading keys with password...")
    loaded_keys = KyberKeys.load_from_file("test_kyber_encrypted", password)
    
    # Test with loaded encrypted keys
    print("\nTesting with loaded encrypted keys...")
    decapsulated_secret = KyberKEM.decapsulate(ciphertext, loaded_keys.secret_key)
    print(f"Secrets match with loaded encrypted keys: {shared_secret == decapsulated_secret}")
