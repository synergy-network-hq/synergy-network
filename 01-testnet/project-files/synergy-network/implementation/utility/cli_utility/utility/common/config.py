"""
Configuration Module for Synergy Network Utility

This module provides configuration management for the Synergy Network
wallet, token, and naming system utility.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("synergy.utility.config")

class Config:
    """Class for managing utility configuration."""
    
    DEFAULT_CONFIG = {
        "network": {
            "mainnet": {
                "rpc_endpoint": "https://rpc.synergy-network.io",
                "explorer_endpoint": "https://explorer.synergy-network.io",
                "chain_id": "syn_mainnet_1"
            },
            "testnet": {
                "rpc_endpoint": "https://testnet-rpc.synergy-network.io",
                "explorer_endpoint": "https://testnet-explorer.synergy-network.io",
                "chain_id": "syn_testnet_1"
            },
            "local": {
                "rpc_endpoint": "http://localhost:9090",
                "explorer_endpoint": "http://localhost:8080",
                "chain_id": "syn_local_1"
            },
            "active_network": "testnet"
        },
        "wallet": {
            "default_wallet": None,
            "keystore_path": "~/.synergy/keystore",
            "address_format": "sYnQ"
        },
        "tokens": {
            "default_gas_limit": 21000,
            "default_gas_price": 1,
            "token_registry_address": "sYnQsyn1tokenregistry000000000000000000000"
        },
        "naming": {
            "sns_registry_address": "sYnQsyn1snsregistry0000000000000000000000",
            "default_domain": "syn",
            "registration_period": 31536000  # 1 year in seconds
        },
        "ui": {
            "theme": "dark",
            "language": "en",
            "currency": "USD"
        }
    }
    
    def __init__(self, config_dir: str = None):
        """
        Initialize a Config instance.
        
        Args:
            config_dir: Directory for configuration files
        """
        # Set config directory
        if config_dir:
            self.config_dir = os.path.expanduser(config_dir)
        else:
            self.config_dir = os.path.expanduser("~/.synergy")
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Set config file path
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Load or create config
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default.
        
        Returns:
            Configuration dictionary
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Update with any missing default values
                self._update_with_defaults(config)
                
                return config
            else:
                # Create default config
                self._save_config(self.DEFAULT_CONFIG)
                return self.DEFAULT_CONFIG.copy()
        
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.info("Using default configuration")
            return self.DEFAULT_CONFIG.copy()
    
    def _update_with_defaults(self, config: Dict[str, Any]) -> None:
        """
        Update configuration with missing default values.
        
        Args:
            config: Configuration to update
        """
        def update_dict(target, source):
            for key, value in source.items():
                if key not in target:
                    target[key] = value
                elif isinstance(value, dict) and isinstance(target.get(key), dict):
                    update_dict(target[key], value)
        
        update_dict(config, self.DEFAULT_CONFIG)
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (dot notation for nested keys)
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (dot notation for nested keys)
            value: Value to set
        
        Returns:
            True if successful, False otherwise
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the nested dictionary
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                config[k] = {}
            
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save the updated config
        return self._save_config(self.config)
    
    def get_active_network(self) -> Dict[str, Any]:
        """
        Get the active network configuration.
        
        Returns:
            Active network configuration
        """
        active_network = self.get('network.active_network', 'testnet')
        return self.get(f'network.{active_network}', {})
    
    def set_active_network(self, network: str) -> bool:
        """
        Set the active network.
        
        Args:
            network: Network name ('mainnet', 'testnet', or 'local')
        
        Returns:
            True if successful, False otherwise
        """
        if network not in ['mainnet', 'testnet', 'local']:
            logger.error(f"Invalid network: {network}")
            return False
        
        return self.set('network.active_network', network)
    
    def get_keystore_path(self) -> str:
        """
        Get the keystore path.
        
        Returns:
            Keystore path
        """
        path = self.get('wallet.keystore_path', '~/.synergy/keystore')
        return os.path.expanduser(path)
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to defaults.
        
        Returns:
            True if successful, False otherwise
        """
        self.config = self.DEFAULT_CONFIG.copy()
        return self._save_config(self.config)

# Singleton instance
_config_instance = None

def get_config(config_dir: str = None) -> Config:
    """
    Get the singleton Config instance.
    
    Args:
        config_dir: Directory for configuration files
    
    Returns:
        Config instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(config_dir)
    
    return _config_instance

# Example usage
if __name__ == "__main__":
    # Get config
    config = get_config()
    
    # Print active network
    active_network = config.get_active_network()
    print(f"Active network: {config.get('network.active_network')}")
    print(f"RPC endpoint: {active_network.get('rpc_endpoint')}")
    print(f"Chain ID: {active_network.get('chain_id')}")
    
    # Set a value
    config.set('ui.theme', 'light')
    print(f"Theme: {config.get('ui.theme')}")
    
    # Reset to defaults
    config.reset_to_defaults()
    print(f"Theme after reset: {config.get('ui.theme')}")
