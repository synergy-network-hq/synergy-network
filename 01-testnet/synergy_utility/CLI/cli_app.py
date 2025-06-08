import argparse
import sys

# Updated imports for new project structure
from utility.core.wallet import Wallet, WalletManager
from utility.core.token import Token, TokenManager
from utility.core.naming import NamingService
from synergy_uma.pq_keys import generate_synergy_seed
from synergy_uma.chain_derivations import derive_ethereum_address
from synergy_uma.sns_api import register_name, lookup_name

def main():
    parser = argparse.ArgumentParser(
        description="Synergy Network CLI Utility Tool",
        add_help=False
    )
    # Top-level subparsers
    subparsers = parser.add_subparsers(dest="command")

    # Wallet commands
    wallet_parser = subparsers.add_parser(
        "wallet",
        help="Wallet operations",
        description="Create, list, or manage synergy wallets."
    )
    wallet_sub = wallet_parser.add_subparsers(dest="wallet_command")

    w_create = wallet_sub.add_parser(
        "create",
        help="Create a new wallet",
        description="Generates a new synergy wallet."
    )
    w_create.set_defaults(func=wallet_create)

    # Token commands
    token_parser = subparsers.add_parser(
        "token",
        help="Token operations",
        description="Create or manage synergy tokens."
    )
    token_sub = token_parser.add_subparsers(dest="token_command")

    t_create = token_sub.add_parser(
        "create",
        help="Create a new token",
        description="Creates a new token on synergy."
    )
    t_create.set_defaults(func=token_create)

    # UMA commands
    uma_parser = subparsers.add_parser(
        "uma",
        help="Universal Meta Address commands",
        description="Manage synergy PQ addresses and chain derivations."
    )
    uma_sub = uma_parser.add_subparsers(dest="uma_command")

    gen_cmd = uma_sub.add_parser(
        "generate",
        help="Generate synergy PQC address",
        description="Generates a new synergy PQC keypair."
    )
    gen_cmd.set_defaults(func=uma_generate)

    derive_cmd = uma_sub.add_parser(
        "derive",
        help="Derive chain address",
        description="Derives a chain-specific address from synergy seed."
    )
    derive_cmd.set_defaults(func=uma_derive)

    # Synergy naming system (SNS) commands
    sns_parser = subparsers.add_parser(
        "sns",
        help="Synergy Naming System",
        description="Register or lookup synergy domain names."
    )
    sns_sub = sns_parser.add_subparsers(dest="sns_command")

    reg_cmd = sns_sub.add_parser(
        "register",
        help="Register synergy name",
        description="Registers a synergy name."
    )
    reg_cmd.set_defaults(func=sns_register)

    look_cmd = sns_sub.add_parser(
        "lookup",
        help="Lookup synergy name",
        description="Looks up a registered synergy name."
    )
    look_cmd.set_defaults(func=sns_lookup)

    args, unknown = parser.parse_known_args()

    if not args.command:
        print_welcome_screen(parser)
        sys.exit(0)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

def print_welcome_screen(parser):
    print(r"""
 ┌────────────────────────────────────────────────────────┐
 │                                                        │
 │            Synergy Network - CLI Utility Tool          │
 │                                                        │
 │   Type 'synergy <command> --help' for usage details.   │
 │   Type 'synergy --help' to see help.                   │
 │   Type 'exit' or 'ctrl-c' to quit.                     │
 │                                                        │
 └────────────────────────────────────────────────────────┘
""")
    print("Available commands:\n")
    for action in parser._subparsers._group_actions:
        if action.dest == "command":
            for choice, subparser in action.choices.items():
                help_text = getattr(subparser, 'help', '') or getattr(subparser, 'description', '')
                print(f"  {choice:<10} {help_text}")

    print("\nExamples:\n  synergy wallet create\n  synergy token create\n  synergy uma generate\n  synergy sns register\n")

# Implementations (now referencing real utility/core functions)
def wallet_create(args):
    wallet = WalletManager.create_wallet()
    print(f"[CLI] Created wallet: {wallet}")

def token_create(args):
    token = TokenManager.create_token()
    print(f"[CLI] Created token: {token}")

def uma_generate(args):
    synergy_data = generate_synergy_seed(password="")
    print(f"[CLI] Generated UMA: {synergy_data['synergy_address']}")

def uma_derive(args):
    # Example deriving Ethereum address from UMA
    synergy_data = generate_synergy_seed(password="")
    private_key_bytes = synergy_data['private_key']['data'].encode()
    eth_address = derive_ethereum_address(private_key_bytes)
    print(f"[CLI] Derived Ethereum address: {eth_address}")

def sns_register(args):
    synergy_data = generate_synergy_seed(password="")
    result = register_name("myname.syn", synergy_data["synergy_address"])
    print(f"[CLI] SNS register result: {result}")

def sns_lookup(args):
    result = lookup_name("myname.syn")
    print(f"[CLI] SNS lookup result: {result}")

if __name__ == "__main__":
    main()
