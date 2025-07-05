"""
Naming System Module for Synergy Network Utility

This module implements the Synergy Naming System (SNS) functionality for the Synergy Network
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
logger = logging.getLogger("synergy.utility.naming")

class DomainStatus:
    """Enumeration of domain statuses in the Synergy Naming System."""
    AVAILABLE = "available"
    REGISTERED = "registered"
    RESERVED = "reserved"
    EXPIRED = "expired"
    GRACE_PERIOD = "grace_period"

class Domain:
    """Class representing a domain in the Synergy Naming System."""
    
    def __init__(
        self,
        name: str,
        owner: str = None,
        resolver: str = None,
        records: Dict[str, Any] = None,
        registration_date: int = None,
        expiration_date: int = None,
        status: str = DomainStatus.AVAILABLE
    ):
        """
        Initialize a Domain instance.
        
        Args:
            name: Domain name
            owner: Domain owner address
            resolver: Resolver address
            records: Domain records
            registration_date: Registration timestamp
            expiration_date: Expiration timestamp
            status: Domain status
        """
        self.name = name
        self.owner = owner
        self.resolver = resolver
        self.records = records or {}
        self.registration_date = registration_date
        self.expiration_date = expiration_date
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Domain to dictionary.
        
        Returns:
            Dictionary representation of the domain
        """
        return {
            "name": self.name,
            "owner": self.owner,
            "resolver": self.resolver,
            "records": self.records,
            "registration_date": self.registration_date,
            "expiration_date": self.expiration_date,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Domain':
        """
        Create Domain from dictionary.
        
        Args:
            data: Dictionary representation of the domain
        
        Returns:
            Domain instance
        """
        return cls(
            name=data["name"],
            owner=data.get("owner"),
            resolver=data.get("resolver"),
            records=data.get("records", {}),
            registration_date=data.get("registration_date"),
            expiration_date=data.get("expiration_date"),
            status=data.get("status", DomainStatus.AVAILABLE)
        )
    
    def is_expired(self) -> bool:
        """
        Check if the domain is expired.
        
        Returns:
            True if expired, False otherwise
        """
        if self.status == DomainStatus.AVAILABLE:
            return False
        
        if not self.expiration_date:
            return False
        
        return int(time.time()) > self.expiration_date
    
    def update_status(self) -> None:
        """Update domain status based on expiration date."""
        if self.status == DomainStatus.AVAILABLE:
            return
        
        if not self.expiration_date:
            return
        
        current_time = int(time.time())
        
        if current_time > self.expiration_date:
            # Domain is expired
            grace_period = 30 * 24 * 60 * 60  # 30 days in seconds
            
            if current_time > self.expiration_date + grace_period:
                self.status = DomainStatus.EXPIRED
            else:
                self.status = DomainStatus.GRACE_PERIOD
        else:
            self.status = DomainStatus.REGISTERED
    
    def set_record(self, record_type: str, value: Any) -> bool:
        """
        Set a domain record.
        
        Args:
            record_type: Record type
            value: Record value
        
        Returns:
            True if successful, False otherwise
        """
        self.records[record_type] = value
        return True
    
    def get_record(self, record_type: str) -> Optional[Any]:
        """
        Get a domain record.
        
        Args:
            record_type: Record type
        
        Returns:
            Record value or None if not found
        """
        return self.records.get(record_type)
    
    def delete_record(self, record_type: str) -> bool:
        """
        Delete a domain record.
        
        Args:
            record_type: Record type
        
        Returns:
            True if successful, False otherwise
        """
        if record_type in self.records:
            del self.records[record_type]
            return True
        
        return False

class NamingSystem:
    """Class for managing the Synergy Naming System."""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize a NamingSystem instance.
        
        Args:
            data_dir: Directory for domain data (optional)
        """
        # Set data directory
        config = get_config()
        self.data_dir = data_dir or os.path.expanduser("~/.synergy/domains")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load domains
        self.domains: Dict[str, Domain] = {}
        self._load_domains()
        
        # Get configuration
        self.default_domain = config.get('naming.default_domain', 'syn')
        self.registration_period = config.get('naming.registration_period', 31536000)  # 1 year in seconds
    
    def _load_domains(self) -> None:
        """Load domains from data directory."""
        try:
            # Get domain files
            domain_files = [
                os.path.join(self.data_dir, f)
                for f in os.listdir(self.data_dir)
                if f.endswith('.json')
            ]
            
            # Load domains
            for domain_file in domain_files:
                try:
                    with open(domain_file, 'r') as f:
                        data = json.load(f)
                    
                    domain = Domain.from_dict(data)
                    domain.update_status()  # Update status based on expiration date
                    self.domains[domain.name] = domain
                except Exception as e:
                    logger.error(f"Error loading domain {domain_file}: {e}")
        
        except Exception as e:
            logger.error(f"Error loading domains: {e}")
    
    def _save_domain(self, domain: Domain) -> bool:
        """
        Save domain to file.
        
        Args:
            domain: Domain to save
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create filename from domain name
            filename = os.path.join(self.data_dir, f"{domain.name.replace('.', '_')}.json")
            
            # Save domain to file
            with open(filename, 'w') as f:
                json.dump(domain.to_dict(), f, indent=2)
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving domain: {e}")
            return False
    
    def check_domain_availability(self, name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a domain is available.
        
        Args:
            name: Domain name
        
        Returns:
            Tuple of (available, reason)
        """
        # Add default domain suffix if not present
        if '.' not in name:
            name = f"{name}.{self.default_domain}"
        
        # Check if domain exists
        if name in self.domains:
            domain = self.domains[name]
            domain.update_status()
            
            if domain.status in [DomainStatus.REGISTERED, DomainStatus.RESERVED, DomainStatus.GRACE_PERIOD]:
                return False, f"Domain is {domain.status}"
            
            if domain.status == DomainStatus.EXPIRED:
                return True, None
        
        # Check for reserved names
        reserved_names = ["synergy", "admin", "system", "network", "blockchain", "token", "wallet", "sns"]
        name_parts = name.split('.')
        
        if name_parts[0] in reserved_names:
            return False, "Domain name is reserved"
        
        # Check for invalid characters
        valid_chars = "abcdefghijklmnopqrstuvwxyz0123456789-"
        
        for part in name_parts:
            if not part:
                return False, "Domain name cannot have empty parts"
            
            if part[0] == '-' or part[-1] == '-':
                return False, "Domain name parts cannot start or end with a hyphen"
            
            if not all(c in valid_chars for c in part):
                return False, "Domain name can only contain letters, numbers, and hyphens"
        
        return True, None
    
    def register_domain(
        self,
        name: str,
        owner: str,
        resolver: str = None,
        records: Dict[str, Any] = None,
        registration_period: int = None
    ) -> Optional[Domain]:
        """
        Register a domain.
        
        Args:
            name: Domain name
            owner: Owner address
            resolver: Resolver address (optional)
            records: Domain records (optional)
            registration_period: Registration period in seconds (optional)
        
        Returns:
            Registered Domain instance or None if failed
        """
        try:
            # Add default domain suffix if not present
            if '.' not in name:
                name = f"{name}.{self.default_domain}"
            
            # Check availability
            available, reason = self.check_domain_availability(name)
            
            if not available:
                logger.error(f"Domain {name} is not available: {reason}")
                return None
            
            # Set registration period
            if registration_period is None:
                registration_period = self.registration_period
            
            # Set timestamps
            current_time = int(time.time())
            registration_date = current_time
            expiration_date = current_time + registration_period
            
            # Create domain
            domain = Domain(
                name=name,
                owner=owner,
                resolver=resolver,
                records=records or {},
                registration_date=registration_date,
                expiration_date=expiration_date,
                status=DomainStatus.REGISTERED
            )
            
            # Save domain to file
            if not self._save_domain(domain):
                return None
            
            # Add to domains
            self.domains[domain.name] = domain
            
            return domain
        
        except Exception as e:
            logger.error(f"Error registering domain: {e}")
            return None
    
    def renew_domain(self, name: str, period: int = None) -> bool:
        """
        Renew a domain.
        
        Args:
            name: Domain name
            period: Renewal period in seconds (optional)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add default domain suffix if not present
            if '.' not in name:
                name = f"{name}.{self.default_domain}"
            
            # Check if domain exists
            if name not in self.domains:
                logger.error(f"Domain {name} not found")
                return False
            
            domain = self.domains[name]
            domain.update_status()
            
            # Set renewal period
            if period is None:
                period = self.registration_period
            
            # Set new expiration date
            current_time = int(time.time())
            
            if domain.status == DomainStatus.EXPIRED:
                # Domain is expired, start from current time
                domain.expiration_date = current_time + period
            else:
                # Domain is not expired, add to current expiration date
                domain.expiration_date = max(domain.expiration_date, current_time) + period
            
            # Update status
            domain.status = DomainStatus.REGISTERED
            
            # Save domain to file
            return self._save_domain(domain)
        
        except Exception as e:
            logger.error(f"Error renewing domain: {e}")
            return False
    
    def transfer_domain(self, name: str, new_owner: str) -> bool:
        """
        Transfer a domain to a new owner.
        
        Args:
            name: Domain name
            new_owner: New owner address
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add default domain suffix if not present
            if '.' not in name:
                name = f"{name}.{self.default_domain}"
            
            # Check if domain exists
            if name not in self.domains:
                logger.error(f"Domain {name} not found")
                return False
            
            domain = self.domains[name]
            domain.update_status()
            
            # Check if domain is transferable
            if domain.status not in [DomainStatus.REGISTERED, DomainStatus.GRACE_PERIOD]:
                logger.error(f"Domain {name} is not transferable (status: {domain.status})")
                return False
            
            # Transfer domain
            domain.owner = new_owner
            
            # Save domain to file
            return self._save_domain(domain)
        
        except Exception as e:
            logger.error(f"Error transferring domain: {e}")
            return False
    
    def set_domain_resolver(self, name: str, resolver: str) -> bool:
        """
        Set domain resolver.
        
        Args:
            name: Domain name
            resolver: Resolver address
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add default domain suffix if not present
            if '.' not in name:
                name = f"{name}.{self.default_domain}"
            
            # Check if domain exists
            if name not in self.domains:
                logger.error(f"Domain {name} not found")
                return False
            
            domain = self.domains[name]
            domain.update_status()
            
            # Check if domain is active
            if domain.status not in [DomainStatus.REGISTERED, DomainStatus.GRACE_PERIOD]:
                logger.error(f"Domain {name} is not active (status: {domain.status})")
                return False
            
            # Set resolver
            domain.resolver = resolver
            
            # Save domain to file
            return self._save_domain(domain)
        
        except Exception as e:
            logger.error(f"Error setting domain resolver: {e}")
            return False
    
    def set_domain_record(self, name: str, record_type: str, value: Any) -> bool:
        """
        Set domain record.
        
        Args:
            name: Domain name
            record_type: Record type
            value: Record value
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add default domain suffix if not present
            if '.' not in name:
                name = f"{name}.{self.default_domain}"
            
            # Check if domain exists
            if name not in self.domains:
                logger.error(f"Domain {name} not found")
                return False
            
            domain = self.domains[name]
            domain.update_status()
            
            # Check if domain is active
            if domain.status not in [DomainStatus.REGISTERED, DomainStatus.GRACE_PERIOD]:
                logger.error(f"Domain {name} is not active (status: {domain.status})")
                return False
            
            # Set record
            domain.set_record(record_type, value)
            
            # Save domain to file
            return self._save_domain(domain)
        
        except Exception as e:
            logger.error(f"Error setting domain record: {e}")
            return False
    
    def get_domain_record(self, name: str, record_type: str) -> Optional[Any]:
        """
        Get domain record.
        
        Args:
            name: Domain name
            record_type: Record type
        
        Returns:
            Record value or None if not found
        """
        try:
            # Add default domain suffix if not present
            if '.' not in name:
                name = f"{name}.{self.default_domain}"
            
            # Check if domain exists
            if name not in self.domains:
                logger.error(f"Domain {name} not found")
                return None
            
            domain = self.domains[name]
            domain.update_status()
            
            # Check if domain is active
            if domain.status not in [DomainStatus.REGISTERED, DomainStatus.GRACE_PERIOD]:
                logger.error(f"Domain {name} is not active (status: {domain.status})")
                return None
            
            # Get record
            return domain.get_record(record_type)
        
        except Exception as e:
            logger.error(f"Error getting domain record: {e}")
            return None
    
    def delete_domain_record(self, name: str, record_type: str) -> bool:
        """
        Delete domain record.
        
        Args:
            name: Domain name
            record_type: Record type
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add default domain suffix if not present
            if '.' not in name:
                name = f"{name}.{self.default_domain}"
            
            # Check if domain exists
            if name not in self.domains:
                logger.error(f"Domain {name} not found")
                return False
            
            domain = self.domains[name]
            domain.update_status()
            
            # Check if domain is active
            if domain.status not in [DomainStatus.REGISTERED, DomainStatus.GRACE_PERIOD]:
                logger.error(f"Domain {name} is not active (status: {domain.status})")
                return False
            
            # Delete record
            if not domain.delete_record(record_type):
                return False
            
            # Save domain to file
            return self._save_domain(domain)
        
        except Exception as e:
            logger.error(f"Error deleting domain record: {e}")
            return False
    
    def get_domain(self, name: str) -> Optional[Domain]:
        """
        Get a domain by name.
        
        Args:
            name: Domain name
        
        Returns:
            Domain instance or None if not found
        """
        # Add default domain suffix if not present
        if '.' not in name:
            name = f"{name}.{self.default_domain}"
        
        # Check if domain exists
        if name not in self.domains:
            return None
        
        domain = self.domains[name]
        domain.update_status()
        
        return domain
    
    def get_domains(self) -> List[Domain]:
        """
        Get all domains.
        
        Returns:
            List of Domain instances
        """
        # Update all domain statuses
        for domain in self.domains.values():
            domain.update_status()
        
        return list(self.domains.values())
    
    def get_domains_by_owner(self, owner: str) -> List[Domain]:
        """
        Get domains by owner.
        
        Args:
            owner: Owner address
        
        Returns:
            List of Domain instances
        """
        # Update all domain statuses
        for domain in self.domains.values():
            domain.update_status()
        
        return [domain for domain in self.domains.values() if domain.owner == owner]
    
    def resolve_name(self, name: str) -> Optional[str]:
        """
        Resolve a domain name to an address.
        
        Args:
            name: Domain name
        
        Returns:
            Address or None if not found
        """
        try:
            # Add default domain suffix if not present
            if '.' not in name:
                name = f"{name}.{self.default_domain}"
            
            # Check if domain exists
            if name not in self.domains:
                logger.error(f"Domain {name} not found")
                return None
            
            domain = self.domains[name]
            domain.update_status()
            
            # Check if domain is active
            if domain.status not in [DomainStatus.REGISTERED, DomainStatus.GRACE_PERIOD]:
                logger.error(f"Domain {name} is not active (status: {domain.status})")
                return None
            
            # Get address record
            address = domain.get_record("address")
            
            if not address:
                # Use owner address as fallback
                address = domain.owner
            
            return address
        
        except Exception as e:
            logger.error(f"Error resolving name: {e}")
            return None
    
    def reverse_resolve(self, address: str) -> Optional[str]:
        """
        Reverse resolve an address to a domain name.
        
        Args:
            address: Address
        
        Returns:
            Domain name or None if not found
        """
        try:
            # Update all domain statuses
            for domain in self.domains.values():
                domain.update_status()
            
            # Find domains with matching address record
            matching_domains = [
                domain for domain in self.domains.values()
                if (domain.get_record("address") == address or domain.owner == address)
                and domain.status in [DomainStatus.REGISTERED, DomainStatus.GRACE_PERIOD]
            ]
            
            if not matching_domains:
                return None
            
            # Sort by registration date (oldest first)
            matching_domains.sort(key=lambda d: d.registration_date or 0)
            
            # Return the primary domain (oldest)
            return matching_domains[0].name
        
        except Exception as e:
            logger.error(f"Error reverse resolving: {e}")
            return None

class NamingTransaction:
    """Class for creating naming system transactions."""
    
    @staticmethod
    def create_domain_registration_transaction(
        wallet_manager: WalletManager,
        from_address: str,
        domain_name: str,
        resolver: str = None,
        records: Dict[str, Any] = None,
        registration_period: int = None,
        password: str = None,
        gas_limit: int = None,
        gas_price: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a domain registration transaction.
        
        Args:
            wallet_manager: WalletManager instance
            from_address: Sender address
            domain_name: Domain name
            resolver: Resolver address (optional)
            records: Domain records (optional)
            registration_period: Registration period in seconds (optional)
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
            
            # Set default registration period
            if registration_period is None:
                registration_period = config.get('naming.registration_period', 31536000)
            
            # Create transaction data
            tx_data = {
                "type": "domain_registration",
                "from": from_address,
                "domain_name": domain_name,
                "resolver": resolver,
                "records": records or {},
                "registration_period": registration_period,
                "gas_limit": gas_limit,
                "gas_price": gas_price,
                "nonce": 0,  # This would be fetched from the network
                "timestamp": int(time.time())
            }
            
            # Sign transaction if password provided
            if password:
                signature = wallet.sign_transaction(tx_data, password)
                
                if not signature:
                    logger.error("Failed to sign transaction")
                    return None
                
                # Add signature to transaction
                tx_data["signature"] = signature.hex()
            
            return tx_data
        
        except Exception as e:
            logger.error(f"Error creating domain registration transaction: {e}")
            return None
    
    @staticmethod
    def create_domain_renewal_transaction(
        wallet_manager: WalletManager,
        from_address: str,
        domain_name: str,
        renewal_period: int = None,
        password: str = None,
        gas_limit: int = None,
        gas_price: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a domain renewal transaction.
        
        Args:
            wallet_manager: WalletManager instance
            from_address: Sender address
            domain_name: Domain name
            renewal_period: Renewal period in seconds (optional)
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
            
            # Set default renewal period
            if renewal_period is None:
                renewal_period = config.get('naming.registration_period', 31536000)
            
            # Create transaction data
            tx_data = {
                "type": "domain_renewal",
                "from": from_address,
                "domain_name": domain_name,
                "renewal_period": renewal_period,
                "gas_limit": gas_limit,
                "gas_price": gas_price,
                "nonce": 0,  # This would be fetched from the network
                "timestamp": int(time.time())
            }
            
            # Sign transaction if password provided
            if password:
                signature = wallet.sign_transaction(tx_data, password)
                
                if not signature:
                    logger.error("Failed to sign transaction")
                    return None
                
                # Add signature to transaction
                tx_data["signature"] = signature.hex()
            
            return tx_data
        
        except Exception as e:
            logger.error(f"Error creating domain renewal transaction: {e}")
            return None
    
    @staticmethod
    def create_domain_transfer_transaction(
        wallet_manager: WalletManager,
        from_address: str,
        domain_name: str,
        to_address: str,
        password: str = None,
        gas_limit: int = None,
        gas_price: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a domain transfer transaction.
        
        Args:
            wallet_manager: WalletManager instance
            from_address: Sender address
            domain_name: Domain name
            to_address: Recipient address
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
                "type": "domain_transfer",
                "from": from_address,
                "domain_name": domain_name,
                "to": to_address,
                "gas_limit": gas_limit,
                "gas_price": gas_price,
                "nonce": 0,  # This would be fetched from the network
                "timestamp": int(time.time())
            }
            
            # Sign transaction if password provided
            if password:
                signature = wallet.sign_transaction(tx_data, password)
                
                if not signature:
                    logger.error("Failed to sign transaction")
                    return None
                
                # Add signature to transaction
                tx_data["signature"] = signature.hex()
            
            return tx_data
        
        except Exception as e:
            logger.error(f"Error creating domain transfer transaction: {e}")
            return None
    
    @staticmethod
    def create_domain_update_transaction(
        wallet_manager: WalletManager,
        from_address: str,
        domain_name: str,
        resolver: str = None,
        records: Dict[str, Any] = None,
        password: str = None,
        gas_limit: int = None,
        gas_price: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a domain update transaction.
        
        Args:
            wallet_manager: WalletManager instance
            from_address: Sender address
            domain_name: Domain name
            resolver: Resolver address (optional)
            records: Domain records (optional)
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
                "type": "domain_update",
                "from": from_address,
                "domain_name": domain_name,
                "resolver": resolver,
                "records": records or {},
                "gas_limit": gas_limit,
                "gas_price": gas_price,
                "nonce": 0,  # This would be fetched from the network
                "timestamp": int(time.time())
            }
            
            # Sign transaction if password provided
            if password:
                signature = wallet.sign_transaction(tx_data, password)
                
                if not signature:
                    logger.error("Failed to sign transaction")
                    return None
                
                # Add signature to transaction
                tx_data["signature"] = signature.hex()
            
            return tx_data
        
        except Exception as e:
            logger.error(f"Error creating domain update transaction: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Create naming system
    naming_system = NamingSystem()
    
    # Create wallet manager
    wallet_manager = WalletManager()
    
    # Create a wallet
    password = "secure_password"
    wallet = wallet_manager.create_wallet("Domain Owner", password)
    
    if wallet:
        print(f"Created wallet: {wallet.name}")
        print(f"Address: {wallet.address}")
        
        # Check domain availability
        domain_name = "example.syn"
        available, reason = naming_system.check_domain_availability(domain_name)
        
        print(f"\nDomain {domain_name} available: {available}")
        if not available:
            print(f"Reason: {reason}")
        
        if available:
            # Register domain
            domain = naming_system.register_domain(
                name=domain_name,
                owner=wallet.address,
                records={
                    "address": wallet.address,
                    "email": "admin@example.syn",
                    "url": "https://example.syn"
                }
            )
            
            if domain:
                print(f"\nRegistered domain: {domain.name}")
                print(f"Owner: {domain.owner}")
                print(f"Registration date: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(domain.registration_date))}")
                print(f"Expiration date: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(domain.expiration_date))}")
                print(f"Status: {domain.status}")
                
                # Resolve domain
                address = naming_system.resolve_name(domain_name)
                print(f"\nResolved {domain_name} to: {address}")
                
                # Reverse resolve
                name = naming_system.reverse_resolve(wallet.address)
                print(f"Reverse resolved {wallet.address} to: {name}")
                
                # Create a domain transaction
                tx_data = NamingTransaction.create_domain_update_transaction(
                    wallet_manager=wallet_manager,
                    from_address=wallet.address,
                    domain_name=domain_name,
                    records={
                        "address": wallet.address,
                        "email": "updated@example.syn",
                        "url": "https://updated.example.syn"
                    },
                    password=password
                )
                
                if tx_data:
                    print(f"\nCreated domain update transaction:")
                    print(f"From: {tx_data['from']}")
                    print(f"Domain: {tx_data['domain_name']}")
                    print(f"Signature: {tx_data.get('signature', 'Not signed')[:32]}...")
                else:
                    print("\nFailed to create domain update transaction")
            else:
                print("\nFailed to register domain")
    else:
        print("Failed to create wallet")
