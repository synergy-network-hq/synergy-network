"""
Wallet Module for Synergy Network Utility

This module implements wallet functionality for the Synergy Network
wallet, token, and naming system utility.
"""

import os
import json
import time
import uuid
import getpass
import logging
from typing import Dict, List, Any, Optional, Tuple
import sys

# Add parent directory to path to import from other packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementation.cryptography.pqc.dilithium import DilithiumSigner, DilithiumKeys, DilithiumKeyManager
from implementation.cryptography.pqc.address import AddressGenerator
from implementation.cryptography.pqc.hash import HashFunctions
from implementation.utility.common.config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("synergy.utility.wallet")

class Wallet:
    """Class representing a wallet in the Synergy Network."""
    
    def __init__(
        self,
        name: str,
        address: str,
        public_key: str,
        encrypted_private_key: str = None,
        keystore_path: str = None
    ):
        """
        Initialize a Wallet instance.
        
        Args:
            name: Wallet name
            address: Wallet address
            public_key: Public key (hex string)
            encrypted_private_key: Encrypted private key (optional)
            keystore_path: Path to keystore directory (optional)
        """
        self.name = name
        self.address = address
        self.public_key = public_key
        self.encrypted_private_key = encrypted_private_key
        
        # Set keystore path
        config = get_config()
        self.keystore_path = keystore_path or config.get_keystore_path()
        
        # Create keystore directory if it doesn't exist
        os.makedirs(self.keystore_path, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Wallet to dictionary.
        
        Returns:
            Dictionary representation of the wallet
        """
        return {
            "name": self.name,
            "address": self.address,
            "public_key": self.public_key,
            "encrypted_private_key": self.encrypted_private_key
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], keystore_path: str = None) -> 'Wallet':
        """
        Create Wallet from dictionary.
        
        Args:
            data: Dictionary representation of the wallet
            keystore_path: Path to keystore directory (optional)
        
        Returns:
            Wallet instance
        """
        return cls(
            name=data["name"],
            address=data["address"],
            public_key=data["public_key"],
            encrypted_private_key=data.get("encrypted_private_key"),
            keystore_path=keystore_path
        )
    
    def save_to_file(self) -> str:
        """
        Save wallet to file.
        
        Returns:
            Path to saved wallet file
        """
        # Create filename from address
        filename = os.path.join(self.keystore_path, f"{self.address}.json")
        
        # Save wallet to file
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return filename
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'Wallet':
        """
        Load wallet from file.
        
        Args:
            filename: Path to wallet file
        
        Returns:
            Wallet instance
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data, keystore_path=os.path.dirname(filename))
    
    def unlock(self, password: str) -> Optional[bytes]:
        """
        Unlock wallet with password.
        
        Args:
            password: Wallet password
        
        Returns:
            Private key bytes or None if failed
        """
        if not self.encrypted_private_key:
            logger.error("No encrypted private key available")
            return None
        
        try:
            # Decrypt private key
            from Crypto.Cipher import AES
            from Crypto.Protocol.KDF import scrypt
            
            # Extract components from encrypted key
            encrypted_data = bytes.fromhex(self.encrypted_private_key)
            salt = encrypted_data[:16]
            nonce = encrypted_data[16:32]
            tag = encrypted_data[32:48]
            ciphertext = encrypted_data[48:]
            
            # Generate key from password
            key = scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)
            
            # Decrypt private key
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            private_key = cipher.decrypt_and_verify(ciphertext, tag)
            
            return private_key
        
        except Exception as e:
            logger.error(f"Error unlocking wallet: {e}")
            return None
    
    def sign_transaction(self, transaction_data: Dict[str, Any], password: str) -> Optional[bytes]:
        """
        Sign a transaction with the wallet's private key.
        
        Args:
            transaction_data: Transaction data
            password: Wallet password
        
        Returns:
            Signature bytes or None if failed
        """
        # Unlock wallet
        private_key = self.unlock(password)
        
        if not private_key:
            return None
        
        try:
            # Hash transaction data
            tx_hash = HashFunctions.hash_transaction(transaction_data)
            
            # Sign transaction hash
            signature = DilithiumSigner.sign(tx_hash, private_key)
            
            return signature
        
        except Exception as e:
            logger.error(f"Error signing transaction: {e}")
            return None
    
    def sign_message(self, message: str, password: str) -> Optional[bytes]:
        """
        Sign a message with the wallet's private key.
        
        Args:
            message: Message to sign
            password: Wallet password
        
        Returns:
            Signature bytes or None if failed
        """
        # Unlock wallet
        private_key = self.unlock(password)
        
        if not private_key:
            return None
        
        try:
            # Hash message
            message_hash = HashFunctions.sha3_256(message)
            
            # Sign message hash
            signature = DilithiumSigner.sign(message_hash, private_key)
            
            return signature
        
        except Exception as e:
            logger.error(f"Error signing message: {e}")
            return None

class WalletManager:
    """Class for managing wallets in the Synergy Network."""
    
    def __init__(self, keystore_path: str = None):
        """
        Initialize a WalletManager instance.
        
        Args:
            keystore_path: Path to keystore directory (optional)
        """
        # Set keystore path
        config = get_config()
        self.keystore_path = keystore_path or config.get_keystore_path()
        
        # Create keystore directory if it doesn't exist
        os.makedirs(self.keystore_path, exist_ok=True)
        
        # Load wallets
        self.wallets: Dict[str, Wallet] = {}
        self._load_wallets()
    
    def _load_wallets(self) -> None:
        """Load wallets from keystore directory."""
        try:
            # Get wallet files
            wallet_files = [
                os.path.join(self.keystore_path, f)
                for f in os.listdir(self.keystore_path)
                if f.endswith('.json')
            ]
            
            # Load wallets
            for wallet_file in wallet_files:
                try:
                    wallet = Wallet.load_from_file(wallet_file)
                    self.wallets[wallet.address] = wallet
                except Exception as e:
                    logger.error(f"Error loading wallet {wallet_file}: {e}")
        
        except Exception as e:
            logger.error(f"Error loading wallets: {e}")
    
    def create_wallet(self, name: str, password: str, address_type: str = "quantum") -> Optional[Wallet]:
        """
        Create a new wallet.
        
        Args:
            name: Wallet name
            password: Wallet password
            address_type: Address type ('quantum' or 'universal')
        
        Returns:
            New Wallet instance or None if failed
        """
        try:
            # Generate key pair
            key_manager = DilithiumKeyManager()
            keys = key_manager.generate_keys()
            
            # Generate address
            prefix = "sYnQ" if address_type == "quantum" else "sYnU"
            address = AddressGenerator.generate_address(keys.public_key, prefix)
            
            # Encrypt private key
            from Crypto.Cipher import AES
            from Crypto.Protocol.KDF import scrypt
            from Crypto.Random import get_random_bytes
            
            # Generate key from password
            salt = get_random_bytes(16)
            key = scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)
            
            # Encrypt private key
            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(keys.private_key)
            
            # Combine components
            encrypted_data = salt + cipher.nonce + tag + ciphertext
            encrypted_private_key = encrypted_data.hex()
            
            # Create wallet
            wallet = Wallet(
                name=name,
                address=address,
                public_key=keys.public_key.hex(),
                encrypted_private_key=encrypted_private_key,
                keystore_path=self.keystore_path
            )
            
            # Save wallet to file
            wallet.save_to_file()
            
            # Add to wallets
            self.wallets[wallet.address] = wallet
            
            # Set as default wallet if first wallet
            if len(self.wallets) == 1:
                config = get_config()
                config.set('wallet.default_wallet', wallet.address)
            
            return wallet
        
        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            return None
    
    def import_wallet(self, name: str, private_key: bytes, password: str, address_type: str = "quantum") -> Optional[Wallet]:
        """
        Import a wallet from private key.
        
        Args:
            name: Wallet name
            private_key: Private key bytes
            password: Wallet password
            address_type: Address type ('quantum' or 'universal')
        
        Returns:
            Imported Wallet instance or None if failed
        """
        try:
            # Generate public key from private key
            public_key = DilithiumSigner.derive_public_key(private_key)
            
            # Generate address
            prefix = "sYnQ" if address_type == "quantum" else "sYnU"
            address = AddressGenerator.generate_address(public_key, prefix)
            
            # Encrypt private key
            from Crypto.Cipher import AES
            from Crypto.Protocol.KDF import scrypt
            from Crypto.Random import get_random_bytes
            
            # Generate key from password
            salt = get_random_bytes(16)
            key = scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)
            
            # Encrypt private key
            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(private_key)
            
            # Combine components
            encrypted_data = salt + cipher.nonce + tag + ciphertext
            encrypted_private_key = encrypted_data.hex()
            
            # Create wallet
            wallet = Wallet(
                name=name,
                address=address,
                public_key=public_key.hex(),
                encrypted_private_key=encrypted_private_key,
                keystore_path=self.keystore_path
            )
            
            # Save wallet to file
            wallet.save_to_file()
            
            # Add to wallets
            self.wallets[wallet.address] = wallet
            
            return wallet
        
        except Exception as e:
            logger.error(f"Error importing wallet: {e}")
            return None
    
    def import_wallet_from_mnemonic(self, name: str, mnemonic: str, password: str, address_type: str = "quantum") -> Optional[Wallet]:
        """
        Import a wallet from mnemonic phrase.
        
        Args:
            name: Wallet name
            mnemonic: Mnemonic phrase
            password: Wallet password
            address_type: Address type ('quantum' or 'universal')
        
        Returns:
            Imported Wallet instance or None if failed
        """
        try:
            # Generate seed from mnemonic
            from mnemonic import Mnemonic
            mnemo = Mnemonic("english")
            seed = mnemo.to_seed(mnemonic)
            
            # Generate private key from seed
            private_key = HashFunctions.sha3_256(seed)
            
            # Import wallet with private key
            return self.import_wallet(name, private_key, password, address_type)
        
        except Exception as e:
            logger.error(f"Error importing wallet from mnemonic: {e}")
            return None
    
    def export_wallet_to_mnemonic(self, address: str, password: str) -> Optional[str]:
        """
        Export a wallet to mnemonic phrase.
        
        Args:
            address: Wallet address
            password: Wallet password
        
        Returns:
            Mnemonic phrase or None if failed
        """
        try:
            # Get wallet
            wallet = self.get_wallet(address)
            
            if not wallet:
                logger.error(f"Wallet not found: {address}")
                return None
            
            # Unlock wallet
            private_key = wallet.unlock(password)
            
            if not private_key:
                logger.error("Failed to unlock wallet")
                return None
            
            # Generate mnemonic from private key
            from mnemonic import Mnemonic
            mnemo = Mnemonic("english")
            entropy = private_key[:16]  # Use first 16 bytes as entropy
            mnemonic = mnemo.to_mnemonic(entropy)
            
            return mnemonic
        
        except Exception as e:
            logger.error(f"Error exporting wallet to mnemonic: {e}")
            return None
    
    def get_wallet(self, address: str) -> Optional[Wallet]:
        """
        Get a wallet by address.
        
        Args:
            address: Wallet address
        
        Returns:
            Wallet instance or None if not found
        """
        return self.wallets.get(address)
    
    def get_wallets(self) -> List[Wallet]:
        """
        Get all wallets.
        
        Returns:
            List of Wallet instances
        """
        return list(self.wallets.values())
    
    def get_default_wallet(self) -> Optional[Wallet]:
        """
        Get the default wallet.
        
        Returns:
            Default Wallet instance or None if not set
        """
        config = get_config()
        default_wallet = config.get('wallet.default_wallet')
        
        if default_wallet:
            return self.get_wallet(default_wallet)
        
        # If no default wallet is set but we have wallets, use the first one
        wallets = self.get_wallets()
        if wallets:
            return wallets[0]
        
        return None
    
    def set_default_wallet(self, address: str) -> bool:
        """
        Set the default wallet.
        
        Args:
            address: Wallet address
        
        Returns:
            True if successful, False otherwise
        """
        if address not in self.wallets:
            logger.error(f"Wallet not found: {address}")
            return False
        
        config = get_config()
        return config.set('wallet.default_wallet', address)
    
    def rename_wallet(self, address: str, new_name: str) -> bool:
        """
        Rename a wallet.
        
        Args:
            address: Wallet address
            new_name: New wallet name
        
        Returns:
            True if successful, False otherwise
        """
        wallet = self.get_wallet(address)
        
        if not wallet:
            logger.error(f"Wallet not found: {address}")
            return False
        
        wallet.name = new_name
        wallet.save_to_file()
        
        return True
    
    def delete_wallet(self, address: str) -> bool:
        """
        Delete a wallet.
        
        Args:
            address: Wallet address
        
        Returns:
            True if successful, False otherwise
        """
        wallet = self.get_wallet(address)
        
        if not wallet:
            logger.error(f"Wallet not found: {address}")
            return False
        
        # Delete wallet file
        try:
            filename = os.path.join(self.keystore_path, f"{address}.json")
            os.remove(filename)
        except Exception as e:
            logger.error(f"Error deleting wallet file: {e}")
            return False
        
        # Remove from wallets
        del self.wallets[address]
        
        # Update default wallet if needed
        config = get_config()
        if config.get('wallet.default_wallet') == address:
            wallets = self.get_wallets()
            if wallets:
                config.set('wallet.default_wallet', wallets[0].address)
            else:
                config.set('wallet.default_wallet', None)
        
        return True
    
    def change_password(self, address: str, old_password: str, new_password: str) -> bool:
        """
        Change wallet password.
        
        Args:
            address: Wallet address
            old_password: Old password
            new_password: New password
        
        Returns:
            True if successful, False otherwise
        """
        wallet = self.get_wallet(address)
        
        if not wallet:
            logger.error(f"Wallet not found: {address}")
            return False
        
        # Unlock wallet
        private_key = wallet.unlock(old_password)
        
        if not private_key:
            logger.error("Failed to unlock wallet")
            return False
        
        try:
            # Encrypt private key with new password
            from Crypto.Cipher import AES
            from Crypto.Protocol.KDF import scrypt
            from Crypto.Random import get_random_bytes
            
            # Generate key from password
            salt = get_random_bytes(16)
            key = scrypt(new_password.encode(), salt, 32, N=2**14, r=8, p=1)
            
            # Encrypt private key
            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(private_key)
            
            # Combine components
            encrypted_data = salt + cipher.nonce + tag + ciphertext
            wallet.encrypted_private_key = encrypted_data.hex()
            
            # Save wallet to file
            wallet.save_to_file()
            
            return True
        
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Create wallet manager
    wallet_manager = WalletManager()
    
    # Create a wallet
    password = "secure_password"
    wallet = wallet_manager.create_wallet("My Wallet", password)
    
    if wallet:
        print(f"Created wallet: {wallet.name}")
        print(f"Address: {wallet.address}")
        print(f"Public key: {wallet.public_key}")
        
        # Test unlocking
        private_key = wallet.unlock(password)
        print(f"Unlocked: {private_key is not None}")
        
        # Test signing
        tx_data = {
            "from": wallet.address,
            "to": "sYnQsyn1recipient00000000000000000000000000",
            "amount": 100,
            "nonce": 1
        }
        
        signature = wallet.sign_transaction(tx_data, password)
        print(f"Signed transaction: {signature is not None}")
        
        # Get all wallets
        wallets = wallet_manager.get_wallets()
        print(f"Number of wallets: {len(wallets)}")
        
        # Get default wallet
        default_wallet = wallet_manager.get_default_wallet()
        print(f"Default wallet: {default_wallet.name if default_wallet else None}")
        
        # Export to mnemonic
        mnemonic = wallet_manager.export_wallet_to_mnemonic(wallet.address, password)
        print(f"Mnemonic: {mnemonic}")
        
        # Import from mnemonic
        imported_wallet = wallet_manager.import_wallet_from_mnemonic("Imported Wallet", mnemonic, password)
        print(f"Imported wallet: {imported_wallet.name if imported_wallet else None}")
    else:
        print("Failed to create wallet")
