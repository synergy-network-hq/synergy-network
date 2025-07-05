#!/usr/bin/env python3
"""
Python Bridge for Synergy Network Utility GUI

This script serves as a bridge between the Electron GUI and the Python backend.
It handles commands from the GUI and returns JSON-formatted results.
"""

import os
import sys
import json
import argparse
import getpass
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path to import from other packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from implementation.utility.common.config import get_config
from implementation.utility.core.wallet import Wallet, WalletManager
from implementation.utility.core.token import Token, TokenManager, TokenType, TokenPermission, TokenTransaction
from implementation.utility.core.naming import Domain, NamingSystem, DomainStatus, NamingTransaction

# Initialize components
config = get_config()
wallet_manager = WalletManager()
token_manager = TokenManager()
naming_system = NamingSystem()

def handle_wallet_list() -> Dict[str, Any]:
    """Handle wallet list command."""
    try:
        wallets = wallet_manager.get_wallets()
        default_wallet = config.get('wallet.default_wallet')
        
        wallet_list = []
        for wallet in wallets:
            wallet_list.append({
                'name': wallet.name,
                'address': wallet.address,
                'isDefault': wallet.address == default_wallet
            })
        
        return {
            'success': True,
            'wallets': wallet_list
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def handle_wallet_create(name: str, password: str) -> Dict[str, Any]:
    """Handle wallet creation command."""
    try:
        wallet = wallet_manager.create_wallet(name, password)
        
        if not wallet:
            return {
                'success': False,
                'error': 'Failed to create wallet'
            }
        
        return {
            'success': True,
            'wallet': {
                'name': wallet.name,
                'address': wallet.address
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def handle_wallet_import(name: str, private_key: str, password: str) -> Dict[str, Any]:
    """Handle wallet import command."""
    try:
        private_key_bytes = bytes.fromhex(private_key)
        wallet = wallet_manager.import_wallet(name, private_key_bytes, password)
        
        if not wallet:
            return {
                'success': False,
                'error': 'Failed to import wallet'
            }
        
        return {
            'success': True,
            'wallet': {
                'name': wallet.name,
                'address': wallet.address
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def handle_wallet_show(address: str) -> Dict[str, Any]:
    """Handle wallet show command."""
    try:
        wallet = wallet_manager.get_wallet(address)
        
        if not wallet:
            return {
                'success': False,
                'error': f'Wallet not found: {address}'
            }
        
        return {
            'success': True,
            'wallet': {
                'name': wallet.name,
                'address': wallet.address,
                'publicKey': wallet.public_key
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def handle_token_list() -> Dict[str, Any]:
    """Handle token list command."""
    try:
        tokens = token_manager.get_tokens()
        
        token_list = []
        for token in tokens:
            token_list.append({
                'id': token.token_id,
                'name': token.name,
                'symbol': token.symbol,
                'type': token.token_type,
                'supply': token.supply,
                'maxSupply': token.max_supply,
                'owner': token.owner
            })
        
        return {
            'success': True,
            'tokens': token_list
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def handle_token_create(name: str, symbol: str, token_type: str, initial_supply: str, max_supply: str, decimals: str) -> Dict[str, Any]:
    """Handle token creation command."""
    try:
        # Get active wallet
        active_wallet = wallet_manager.get_default_wallet()
        
        if not active_wallet:
            return {
                'success': False,
                'error': 'No active wallet'
            }
        
        # Parse numeric values
        initial_supply_int = int(initial_supply) if initial_supply else 0
        max_supply_int = int(max_supply) if max_supply else None
        decimals_int = int(decimals) if decimals else 18
        
        # Create token
        token = token_manager.create_token(
            name=name,
            symbol=symbol,
            token_type=token_type,
            owner=active_wallet.address,
            initial_supply=initial_supply_int,
            max_supply=max_supply_int,
            decimals=decimals_int
        )
        
        if not token:
            return {
                'success': False,
                'error': 'Failed to create token'
            }
        
        return {
            'success': True,
            'token': {
                'id': token.token_id,
                'name': token.name,
                'symbol': token.symbol,
                'type': token.token_type,
                'supply': token.supply,
                'maxSupply': token.max_supply,
                'owner': token.owner
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def handle_token_mint(token_id: str, amount: str, to_address: str, password: str) -> Dict[str, Any]:
    """Handle token mint command."""
    try:
        # Get active wallet
        active_wallet = wallet_manager.get_default_wallet()
        
        if not active_wallet:
            return {
                'success': False,
                'error': 'No active wallet'
            }
        
        # Get token
        token = token_manager.get_token(token_id)
        
        if not token:
            return {
                'success': False,
                'error': f'Token not found: {token_id}'
            }
        
        # Check permission
        if not token.has_permission(active_wallet.address, TokenPermission.MINT):
            return {
                'success': False,
                'error': 'No permission to mint this token'
            }
        
        # Parse amount
        amount_int = int(amount)
        
        # Create mint transaction
        tx_data = TokenTransaction.create_token_mint_transaction(
            wallet_manager=wallet_manager,
            from_address=active_wallet.address,
            token_id=token_id,
            to_address=to_address or active_wallet.address,
            amount=amount_int,
            password=password
        )
        
        if not tx_data:
            return {
                'success': False,
                'error': 'Failed to create mint transaction'
            }
        
        # In offline mode, just mint directly
        success = token_manager.mint_tokens(
            token_id=token_id,
            amount=amount_int,
            to_address=to_address,
            from_address=active_wallet.address
        )
        
        if not success:
            return {
                'success': False,
                'error': 'Failed to mint tokens'
            }
        
        # Get updated token
        token = token_manager.get_token(token_id)
        
        return {
            'success': True,
            'token': {
                'id': token.token_id,
                'name': token.name,
                'symbol': token.symbol,
                'supply': token.supply
            },
            'transaction': {
                'type': tx_data['type'],
                'from': tx_data['from'],
                'to': tx_data['to'],
                'amount': tx_data['amount']
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def handle_naming_list() -> Dict[str, Any]:
    """Handle naming list command."""
    try:
        # Get active wallet
        active_wallet = wallet_manager.get_default_wallet()
        
        if active_wallet:
            # List domains owned by active wallet
            domains = naming_system.get_domains_by_owner(active_wallet.address)
        else:
            # List all domains
            domains = naming_system.get_domains()
        
        domain_list = []
        for domain in domains:
            domain_list.append({
                'name': domain.name,
                'owner': domain.owner,
                'status': domain.status,
                'registrationDate': domain.registration_date,
                'expirationDate': domain.expiration_date
            })
        
        return {
            'success': True,
            'domains': domain_list
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def handle_naming_check(domain_name: str) -> Dict[str, Any]:
    """Handle domain availability check command."""
    try:
        # Check availability
        available, reason = naming_system.check_domain_availability(domain_name)
        
        return {
            'success': True,
            'available': available,
            'reason': reason
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def handle_naming_register(domain_name: str, registration_period: str, password: str) -> Dict[str, Any]:
    """Handle domain registration command."""
    try:
        # Get active wallet
        active_wallet = wallet_manager.get_default_wallet()
        
        if not active_wallet:
            return {
                'success': False,
                'error': 'No active wallet'
            }
        
        # Check availability
        available, reason = naming_system.check_domain_availability(domain_name)
        
        if not available:
            return {
                'success': False,
                'error': f'Domain {domain_name} is not available: {reason}'
            }
        
        # Parse registration period
        registration_period_int = int(registration_period) if registration_period else None
        
        # Create registration transaction
        tx_data = NamingTransaction.create_domain_registration_transaction(
            wallet_manager=wallet_manager,
            from_address=active_wallet.address,
            domain_name=domain_name,
            registration_period=registration_period_int,
            records={
                'address': active_wallet.address
            },
            password=password
        )
        
        if not tx_data:
            return {
                'success': False,
                'error': 'Failed to create registration transaction'
            }
        
        # In offline mode, just register directly
        domain = naming_system.register_domain(
            name=domain_name,
            owner=active_wallet.address,
            registration_period=registration_period_int,
            records={
                'address': active_wallet.address
            }
        )
        
        if not domain:
            return {
                'success': False,
                'error': 'Failed to register domain'
            }
        
        return {
            'success': True,
            'domain': {
                'name': domain.name,
                'owner': domain.owner,
                'status': domain.status,
                'registrationDate': domain.registration_date,
                'expirationDate': domain.expiration_date
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Main entry point for the Python bridge."""
    parser = argparse.ArgumentParser(description='Python Bridge for Synergy Network Utility GUI')
    parser.add_argument('command', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')
    args = parser.parse_args()
    
    # Handle commands
    result = None
    
    if args.command == 'wallet_list':
        result = handle_wallet_list()
    elif args.command == 'wallet_create':
        if len(args.args) < 2:
            result = {'success': False, 'error': 'Missing arguments'}
        else:
            result = handle_wallet_create(args.args[0], args.args[1])
    elif args.command == 'wallet_import':
        if len(args.args) < 3:
            result = {'success': False, 'error': 'Missing arguments'}
        else:
            result = handle_wallet_import(args.args[0], args.args[1], args.args[2])
    elif args.command == 'wallet_show':
        if len(args.args) < 1:
            result = {'success': False, 'error': 'Missing arguments'}
        else:
            result = handle_wallet_show(args.args[0])
    elif args.command == 'token_list':
        result = handle_token_list()
    elif args.command == 'token_create':
        if len(args.args) < 3:
            result = {'success': False, 'error': 'Missing arguments'}
        else:
            initial_supply = args.args[3] if len(args.args) > 3 else None
            max_supply = args.args[4] if len(args.args) > 4 else None
            decimals = args.args[5] if len(args.args) > 5 else None
            result = handle_token_create(args.args[0], args.args[1], args.args[2], initial_supply, max_supply, decimals)
    elif args.command == 'token_mint':
        if len(args.args) < 4:
            result = {'success': False, 'error': 'Missing arguments'}
        else:
            result = handle_token_mint(args.args[0], args.args[1], args.args[2], args.args[3])
    elif args.command == 'naming_list':
        result = handle_naming_list()
    elif args.command == 'naming_check':
        if len(args.args) < 1:
            result = {'success': False, 'error': 'Missing arguments'}
        else:
            result = handle_naming_check(args.args[0])
    elif args.command == 'naming_register':
        if len(args.args) < 3:
            result = {'success': False, 'error': 'Missing arguments'}
        else:
            result = handle_naming_register(args.args[0], args.args[1], args.args[2])
    else:
        result = {'success': False, 'error': f'Unknown command: {args.command}'}
    
    # Print result as JSON
    print(json.dumps(result))

if __name__ == '__main__':
    main()
