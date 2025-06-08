"""
Token Module for Synergy Network Utility

This module implements token functionality for the Synergy Network
wallet, token, and naming system utility.
"""

import os
import json
import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple
import sys

# Add parent directory to path to import from other packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementation.cryptography.pqc.hash import HashFunctions
from implementation.utility.common.config import get_config
from implementation.utility.core.wallet import Wallet, WalletManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("synergy.utility.token")

class TokenType:
    """Enumeration of token types in the Synergy Network."""
    FUNGIBLE = "fungible"
    NON_FUNGIBLE = "non_fungible"
    SEMI_FUNGIBLE = "semi_fungible"

class TokenPermission:
    """Enumeration of token permissions in the Synergy Network."""
    MINT = "mint"
    BURN = "burn"
    TRANSFER = "transfer"
    UPDATE_METADATA = "update_metadata"
    UPDATE_PERMISSIONS = "update_permissions"

class Token:
    """Class representing a token in the Synergy Network."""
    
    def __init__(
        self,
        token_id: str,
        name: str,
        symbol: str,
        token_type: str,
        owner: str,
        supply: int = 0,
        max_supply: int = None,
        decimals: int = 18,
        metadata: Dict[str, Any] = None,
        permissions: Dict[str, List[str]] = None,
        created_at: int = None,
        updated_at: int = None
    ):
        """
        Initialize a Token instance.
        
        Args:
            token_id: Unique token identifier
            name: Token name
            symbol: Token symbol
            token_type: Token type (fungible, non_fungible, semi_fungible)
            owner: Token owner address
            supply: Current token supply
            max_supply: Maximum token supply (None for unlimited)
            decimals: Number of decimal places
            metadata: Token metadata
            permissions: Token permissions
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.token_id = token_id
        self.name = name
        self.symbol = symbol
        self.token_type = token_type
        self.owner = owner
        self.supply = supply
        self.max_supply = max_supply
        self.decimals = decimals
        self.metadata = metadata or {}
        self.permissions = permissions or {
            TokenPermission.MINT: [owner],
            TokenPermission.BURN: [owner],
            TokenPermission.TRANSFER: ["*"],  # * means anyone
            TokenPermission.UPDATE_METADATA: [owner],
            TokenPermission.UPDATE_PERMISSIONS: [owner]
        }
        self.created_at = created_at or int(time.time())
        self.updated_at = updated_at or self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Token to dictionary.
        
        Returns:
            Dictionary representation of the token
        """
        return {
            "token_id": self.token_id,
            "name": self.name,
            "symbol": self.symbol,
            "token_type": self.token_type,
            "owner": self.owner,
            "supply": self.supply,
            "max_supply": self.max_supply,
            "decimals": self.decimals,
            "metadata": self.metadata,
            "permissions": self.permissions,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Token':
        """
        Create Token from dictionary.
        
        Args:
            data: Dictionary representation of the token
        
        Returns:
            Token instance
        """
        return cls(
            token_id=data["token_id"],
            name=data["name"],
            symbol=data["symbol"],
            token_type=data["token_type"],
            owner=data["owner"],
            supply=data.get("supply", 0),
            max_supply=data.get("max_supply"),
            decimals=data.get("decimals", 18),
            metadata=data.get("metadata", {}),
            permissions=data.get("permissions", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def has_permission(self, address: str, permission: str) -> bool:
        """
        Check if an address has a specific permission.
        
        Args:
            address: Address to check
            permission: Permission to check
        
        Returns:
            True if the address has the permission, False otherwise
        """
        if permission not in self.permissions:
            return False
        
        allowed_addresses = self.permissions[permission]
        
        # Check for wildcard permission
        if "*" in allowed_addresses:
            return True
        
        return address in allowed_addresses
    
    def grant_permission(self, address: str, permission: str) -> bool:
        """
        Grant a permission to an address.
        
        Args:
            address: Address to grant permission to
            permission: Permission to grant
        
        Returns:
            True if successful, False otherwise
        """
        if permission not in TokenPermission.__dict__.values():
            logger.error(f"Invalid permission: {permission}")
            return False
        
        if permission not in self.permissions:
            self.permissions[permission] = []
        
        if address not in self.permissions[permission]:
            self.permissions[permission].append(address)
            self.updated_at = int(time.time())
            return True
        
        return False
    
    def revoke_permission(self, address: str, permission: str) -> bool:
        """
        Revoke a permission from an address.
        
        Args:
            address: Address to revoke permission from
            permission: Permission to revoke
        
        Returns:
            True if successful, False otherwise
        """
        if permission not in self.permissions:
            return False
        
        if address in self.permissions[permission]:
            self.permissions[permission].remove(address)
            self.updated_at = int(time.time())
            return True
        
        return False
    
    def update_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Update token metadata.
        
        Args:
            metadata: New metadata
        
        Returns:
            True if successful, False otherwise
        """
        self.metadata.update(metadata)
        self.updated_at = int(time.time())
        return True
    
    def mint(self, amount: int, to_address: str = None) -> bool:
        """
        Mint new tokens.
        
        Args:
            amount: Amount to mint
            to_address: Address to mint to (defaults to owner)
        
        Returns:
            True if successful, False otherwise
        """
        if amount <= 0:
            logger.error("Mint amount must be positive")
            return False
        
        # Check max supply
        if self.max_supply is not None and self.supply + amount > self.max_supply:
            logger.error(f"Mint would exceed max supply: {self.max_supply}")
            return False
        
        # Update supply
        self.supply += amount
        self.updated_at = int(time.time())
        
        return True
    
    def burn(self, amount: int) -> bool:
        """
        Burn tokens.
        
        Args:
            amount: Amount to burn
        
        Returns:
            True if successful, False otherwise
        """
        if amount <= 0:
            logger.error("Burn amount must be positive")
            return False
        
        if amount > self.supply:
            logger.error(f"Burn amount exceeds supply: {self.supply}")
            return False
        
        # Update supply
        self.supply -= amount
        self.updated_at = int(time.time())
        
        return True

class TokenManager:
    """Class for managing tokens in the Synergy Network."""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize a TokenManager instance.
        
        Args:
            data_dir: Directory for token data (optional)
        """
        # Set data directory
        config = get_config()
        self.data_dir = data_dir or os.path.expanduser("~/.synergy/tokens")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load tokens
        self.tokens: Dict[str, Token] = {}
        self._load_tokens()
    
    def _load_tokens(self) -> None:
        """Load tokens from data directory."""
        try:
            # Get token files
            token_files = [
                os.path.join(self.data_dir, f)
                for f in os.listdir(self.data_dir)
                if f.endswith('.json')
            ]
            
            # Load tokens
            for token_file in token_files:
                try:
                    with open(token_file, 'r') as f:
                        data = json.load(f)
                    
                    token = Token.from_dict(data)
                    self.tokens[token.token_id] = token
                except Exception as e:
                    logger.error(f"Error loading token {token_file}: {e}")
        
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
    
    def _save_token(self, token: Token) -> bool:
        """
        Save token to file.
        
        Args:
            token: Token to save
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create filename from token ID
            filename = os.path.join(self.data_dir, f"{token.token_id}.json")
            
            # Save token to file
            with open(filename, 'w') as f:
                json.dump(token.to_dict(), f, indent=2)
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving token: {e}")
            return False
    
    def create_token(
        self,
        name: str,
        symbol: str,
        token_type: str,
        owner: str,
        initial_supply: int = 0,
        max_supply: int = None,
        decimals: int = 18,
        metadata: Dict[str, Any] = None
    ) -> Optional[Token]:
        """
        Create a new token.
        
        Args:
            name: Token name
            symbol: Token symbol
            token_type: Token type (fungible, non_fungible, semi_fungible)
            owner: Token owner address
            initial_supply: Initial token supply
            max_supply: Maximum token supply (None for unlimited)
            decimals: Number of decimal places
            metadata: Token metadata
        
        Returns:
            New Token instance or None if failed
        """
        try:
            # Validate token type
            if token_type not in [TokenType.FUNGIBLE, TokenType.NON_FUNGIBLE, TokenType.SEMI_FUNGIBLE]:
                logger.error(f"Invalid token type: {token_type}")
                return None
            
            # Generate token ID
            token_id = f"syn_{HashFunctions.sha3_256(f'{name}_{symbol}_{owner}_{time.time()}').hex()[:16]}"
            
            # Create token
            token = Token(
                token_id=token_id,
                name=name,
                symbol=symbol,
                token_type=token_type,
                owner=owner,
                supply=initial_supply,
                max_supply=max_supply,
                decimals=decimals,
                metadata=metadata
            )
            
            # Save token to file
            if not self._save_token(token):
                return None
            
            # Add to tokens
            self.tokens[token.token_id] = token
            
            return token
        
        except Exception as e:
            logger.error(f"Error creating token: {e}")
            return None
    
    def get_token(self, token_id: str) -> Optional[Token]:
        """
        Get a token by ID.
        
        Args:
            token_id: Token ID
        
        Returns:
            Token instance or None if not found
        """
        return self.tokens.get(token_id)
    
    def get_tokens(self) -> List[Token]:
        """
        Get all tokens.
        
        Returns:
            List of Token instances
        """
        return list(self.tokens.values())
    
    def get_tokens_by_owner(self, owner: str) -> List[Token]:
        """
        Get tokens by owner.
        
        Args:
            owner: Owner address
        
        Returns:
            List of Token instances
        """
        return [token for token in self.tokens.values() if token.owner == owner]
    
    def update_token(self, token: Token) -> bool:
        """
        Update a token.
        
        Args:
            token: Token to update
        
        Returns:
            True if successful, False otherwise
        """
        if token.token_id not in self.tokens:
            logger.error(f"Token not found: {token.token_id}")
            return False
        
        # Update token
        self.tokens[token.token_id] = token
        
        # Save token to file
        return self._save_token(token)
    
    def delete_token(self, token_id: str) -> bool:
        """
        Delete a token.
        
        Args:
            token_id: Token ID
        
        Returns:
            True if successful, False otherwise
        """
        if token_id not in self.tokens:
            logger.error(f"Token not found: {token_id}")
            return False
        
        # Delete token file
        try:
            filename = os.path.join(self.data_dir, f"{token_id}.json")
            os.remove(filename)
        except Exception as e:
            logger.error(f"Error deleting token file: {e}")
            return False
        
        # Remove from tokens
        del self.tokens[token_id]
        
        return True
    
    def mint_tokens(self, token_id: str, amount: int, to_address: str = None, from_address: str = None) -> bool:
        """
        Mint tokens.
        
        Args:
            token_id: Token ID
            amount: Amount to mint
            to_address: Address to mint to (defaults to owner)
            from_address: Address initiating the mint
        
        Returns:
            True if successful, False otherwise
        """
        token = self.get_token(token_id)
        
        if not token:
            logger.error(f"Token not found: {token_id}")
            return False
        
        # Check permission
        if from_address and not token.has_permission(from_address, TokenPermission.MINT):
            logger.error(f"Address {from_address} does not have mint permission")
            return False
        
        # Set default to_address
        if not to_address:
            to_address = token.owner
        
        # Mint tokens
        if not token.mint(amount, to_address):
            return False
        
        # Save token
        return self._save_token(token)
    
    def burn_tokens(self, token_id: str, amount: int, from_address: str = None) -> bool:
        """
        Burn tokens.
        
        Args:
            token_id: Token ID
            amount: Amount to burn
            from_address: Address initiating the burn
        
        Returns:
            True if successful, False otherwise
        """
        token = self.get_token(token_id)
        
        if not token:
            logger.error(f"Token not found: {token_id}")
            return False
        
        # Check permission
        if from_address and not token.has_permission(from_address, TokenPermission.BURN):
            logger.error(f"Address {from_address} does not have burn permission")
            return False
        
        # Burn tokens
        if not token.burn(amount):
            return False
        
        # Save token
        return self._save_token(token)
    
    def update_token_metadata(self, token_id: str, metadata: Dict[str, Any], from_address: str = None) -> bool:
        """
        Update token metadata.
        
        Args:
            token_id: Token ID
            metadata: New metadata
            from_address: Address initiating the update
        
        Returns:
            True if successful, False otherwise
        """
        token = self.get_token(token_id)
        
        if not token:
            logger.error(f"Token not found: {token_id}")
            return False
        
        # Check permission
        if from_address and not token.has_permission(from_address, TokenPermission.UPDATE_METADATA):
            logger.error(f"Address {from_address} does not have update_metadata permission")
            return False
        
        # Update metadata
        if not token.update_metadata(metadata):
            return False
        
        # Save token
        return self._save_token(token)
    
    def grant_token_permission(self, token_id: str, address: str, permission: str, from_address: str = None) -> bool:
        """
        Grant token permission.
        
        Args:
            token_id: Token ID
            address: Address to grant permission to
            permission: Permission to grant
            from_address: Address initiating the grant
        
        Returns:
            True if successful, False otherwise
        """
        token = self.get_token(token_id)
        
        if not token:
            logger.error(f"Token not found: {token_id}")
            return False
        
        # Check permission
        if from_address and not token.has_permission(from_address, TokenPermission.UPDATE_PERMISSIONS):
            logger.error(f"Address {from_address} does not have update_permissions permission")
            return False
        
        # Grant permission
        if not token.grant_permission(address, permission):
            return False
        
        # Save token
        return self._save_token(token)
    
    def revoke_token_permission(self, token_id: str, address: str, permission: str, from_address: str = None) -> bool:
        """
        Revoke token permission.
        
        Args:
            token_id: Token ID
            address: Address to revoke permission from
            permission: Permission to revoke
            from_address: Address initiating the revocation
        
        Returns:
            True if successful, False otherwise
        """
        token = self.get_token(token_id)
        
        if not token:
            logger.error(f"Token not found: {token_id}")
            return False
        
        # Check permission
        if from_address and not token.has_permission(from_address, TokenPermission.UPDATE_PERMISSIONS):
            logger.error(f"Address {from_address} does not have update_permissions permission")
            return False
        
        # Revoke permission
        if not token.revoke_permission(address, permission):
            return False
        
        # Save token
        return self._save_token(token)

class TokenTransaction:
    """Class for creating token transactions."""
    
    @staticmethod
    def create_token_transaction(
        wallet_manager: WalletManager,
        from_address: str,
        token_id: str,
        to_address: str,
        amount: int,
        password: str,
        gas_limit: int = None,
        gas_price: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a token transfer transaction.
        
        Args:
            wallet_manager: WalletManager instance
            from_address: Sender address
            token_id: Token ID
            to_address: Recipient address
            amount: Amount to transfer
            password: Wallet password
            gas_limit: Gas limit (optional)
            gas_price: Gas price (optional)
        
        Returns:
            Transaction data or None if failed
        """
        try:
            # Get wallet
            wallet = wallet_manager.get_wallet(from_address)
            
            if not wallet:
                logger.error(f"Wallet not found: {from_address}")
                return None
            
            # Get config
            config = get_config()
            
            # Set default gas values
            if gas_limit is None:
                gas_limit = config.get('tokens.default_gas_limit', 21000)
            
            if gas_price is None:
                gas_price = config.get('tokens.default_gas_price', 1)
            
            # Create transaction data
            tx_data = {
                "type": "token_transfer",
                "from": from_address,
                "token_id": token_id,
                "to": to_address,
                "amount": amount,
                "gas_limit": gas_limit,
                "gas_price": gas_price,
                "nonce": 0,  # This would be fetched from the network
                "timestamp": int(time.time())
            }
            
            # Sign transaction
            signature = wallet.sign_transaction(tx_data, password)
            
            if not signature:
                logger.error("Failed to sign transaction")
                return None
            
            # Add signature to transaction
            tx_data["signature"] = signature.hex()
            
            return tx_data
        
        except Exception as e:
            logger.error(f"Error creating token transaction: {e}")
            return None
    
    @staticmethod
    def create_token_mint_transaction(
        wallet_manager: WalletManager,
        from_address: str,
        token_id: str,
        to_address: str,
        amount: int,
        password: str,
        gas_limit: int = None,
        gas_price: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a token mint transaction.
        
        Args:
            wallet_manager: WalletManager instance
            from_address: Sender address
            token_id: Token ID
            to_address: Recipient address
            amount: Amount to mint
            password: Wallet password
            gas_limit: Gas limit (optional)
            gas_price: Gas price (optional)
        
        Returns:
            Transaction data or None if failed
        """
        try:
            # Get wallet
            wallet = wallet_manager.get_wallet(from_address)
            
            if not wallet:
                logger.error(f"Wallet not found: {from_address}")
                return None
            
            # Get config
            config = get_config()
            
            # Set default gas values
            if gas_limit is None:
                gas_limit = config.get('tokens.default_gas_limit', 21000)
            
            if gas_price is None:
                gas_price = config.get('tokens.default_gas_price', 1)
            
            # Create transaction data
            tx_data = {
                "type": "token_mint",
                "from": from_address,
                "token_id": token_id,
                "to": to_address,
                "amount": amount,
                "gas_limit": gas_limit,
                "gas_price": gas_price,
                "nonce": 0,  # This would be fetched from the network
                "timestamp": int(time.time())
            }
            
            # Sign transaction
            signature = wallet.sign_transaction(tx_data, password)
            
            if not signature:
                logger.error("Failed to sign transaction")
                return None
            
            # Add signature to transaction
            tx_data["signature"] = signature.hex()
            
            return tx_data
        
        except Exception as e:
            logger.error(f"Error creating token mint transaction: {e}")
            return None
    
    @staticmethod
    def create_token_burn_transaction(
        wallet_manager: WalletManager,
        from_address: str,
        token_id: str,
        amount: int,
        password: str,
        gas_limit: int = None,
        gas_price: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a token burn transaction.
        
        Args:
            wallet_manager: WalletManager instance
            from_address: Sender address
            token_id: Token ID
            amount: Amount to burn
            password: Wallet password
            gas_limit: Gas limit (optional)
            gas_price: Gas price (optional)
        
        Returns:
            Transaction data or None if failed
        """
        try:
            # Get wallet
            wallet = wallet_manager.get_wallet(from_address)
            
            if not wallet:
                logger.error(f"Wallet not found: {from_address}")
                return None
            
            # Get config
            config = get_config()
            
            # Set default gas values
            if gas_limit is None:
                gas_limit = config.get('tokens.default_gas_limit', 21000)
            
            if gas_price is None:
                gas_price = config.get('tokens.default_gas_price', 1)
            
            # Create transaction data
            tx_data = {
                "type": "token_burn",
                "from": from_address,
                "token_id": token_id,
                "amount": amount,
                "gas_limit": gas_limit,
                "gas_price": gas_price,
                "nonce": 0,  # This would be fetched from the network
                "timestamp": int(time.time())
            }
            
            # Sign transaction
            signature = wallet.sign_transaction(tx_data, password)
            
            if not signature:
                logger.error("Failed to sign transaction")
                return None
            
            # Add signature to transaction
            tx_data["signature"] = signature.hex()
            
            return tx_data
        
        except Exception as e:
            logger.error(f"Error creating token burn transaction: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Create token manager
    token_manager = TokenManager()
    
    # Create wallet manager
    wallet_manager = WalletManager()
    
    # Create a wallet
    password = "secure_password"
    wallet = wallet_manager.create_wallet("Token Owner", password)
    
    if wallet:
        print(f"Created wallet: {wallet.name}")
        print(f"Address: {wallet.address}")
        
        # Create a token
        token = token_manager.create_token(
            name="Synergy Test Token",
            symbol="STT",
            token_type=TokenType.FUNGIBLE,
            owner=wallet.address,
            initial_supply=1000000,
            max_supply=10000000,
            decimals=18,
            metadata={
                "description": "A test token for the Synergy Network",
                "website": "https://synergy-network.io",
                "logo": "https://synergy-network.io/logo.png"
            }
        )
        
        if token:
            print(f"\nCreated token: {token.name}")
            print(f"ID: {token.token_id}")
            print(f"Symbol: {token.symbol}")
            print(f"Supply: {token.supply}")
            
            # Mint tokens
            success = token_manager.mint_tokens(
                token_id=token.token_id,
                amount=500000,
                from_address=wallet.address
            )
            
            print(f"\nMinted tokens: {success}")
            print(f"New supply: {token_manager.get_token(token.token_id).supply}")
            
            # Create a token transaction
            tx_data = TokenTransaction.create_token_transfer_transaction(
                wallet_manager=wallet_manager,
                from_address=wallet.address,
                token_id=token.token_id,
                to_address="sYnQsyn1recipient00000000000000000000000000",
                amount=1000,
                password=password
            )
            
            if tx_data:
                print(f"\nCreated token transaction:")
                print(f"From: {tx_data['from']}")
                print(f"To: {tx_data['to']}")
                print(f"Amount: {tx_data['amount']}")
                print(f"Signature: {tx_data['signature'][:32]}...")
            else:
                print("\nFailed to create token transaction")
        else:
            print("\nFailed to create token")
    else:
        print("Failed to create wallet")
