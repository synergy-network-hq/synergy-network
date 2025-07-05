# Existing code for wallet & token commands might be here
# class SynergyUtilityCLI(cmd.Cmd):
#     """Synergy Network Utility CLI"""

#     intro = """
#     ┌─────────────────────────────────────────────────────┐
#     │                                                     │
#     │  Synergy Network Utility - Command Line Interface   │
#     │                                                     │
#     │  Type 'help' or '?' to list commands.               │
#     │  Type 'exit' or 'quit' to exit.                     │
#     │                                                     │
#     └─────────────────────────────────────────────────────┘
#     """
#     prompt = "synergy> "

#     def __init__(self):
#         """Initialize the CLI."""
#         super().__init__()

#         # Initialize components
#         self.config = get_config()
#         self.wallet_manager = WalletManager()
#         self.token_manager = TokenManager()
#         self.naming_system = NamingSystem()

#         # Set active wallet
#         self.active_wallet = self.wallet_manager.get_default_wallet()

#         # Update prompt if active wallet
#         if self.active_wallet:
#             self.prompt = f"synergy ({self.active_wallet.name})> "
"""
cli_app.py

CLI entry point for Synergy Network Utility
- Real synergy PQC address generation (Dilithium2)
- chain derivation for ethereum/solana/tron
- synergy naming system

Ensure you pip install:
  pqcrypto
  eth_account
  solana
  tronpy
as desired to get full functionality.
"""

import argparse
import sys

from synergy_uma.pq_keys import (
    generate_synergy_seed,
    save_synergy_info,
    load_synergy_info,
    derive_subkey_for_chain
)
from synergy_uma.sns_api import (
    register_name,
    lookup_name
)

def main():
    parser = argparse.ArgumentParser(description="Synergy Network CLI Utility")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Example wallet subcommands
    wallet_parser = subparsers.add_parser("wallet", help="Wallet commands")
    wallet_sub = wallet_parser.add_subparsers(dest="wallet_command")

    w_create = wallet_sub.add_parser("create", help="Create a new wallet (example stub)")
    w_create.add_argument("--name", required=True)
    w_create.set_defaults(func=cmd_wallet_create)

    # Example UMA commands
    uma_parser = subparsers.add_parser("uma", help="Universal Meta Address commands")
    uma_sub = uma_parser.add_subparsers(dest="uma_command")

    gen_cmd = uma_sub.add_parser("generate", help="Generate synergy PQC address")
    gen_cmd.add_argument("--out", default="synergy_seed.json", help="Output file path")
    gen_cmd.add_argument("--password", default="", help="Password to encrypt private key")
    gen_cmd.set_defaults(func=cmd_uma_generate)

    derive_cmd = uma_sub.add_parser("derive", help="Derive chain address")
    derive_cmd.add_argument("--file", default="synergy_seed.json", help="Path to synergy seed file")
    derive_cmd.add_argument("--password", default="", help="Password if synergy seed is encrypted")
    derive_cmd.add_argument("--chain", required=True, help="e.g. ethereum, solana, tron")
    derive_cmd.set_defaults(func=cmd_uma_derive)

    # Synergy naming commands
    sns_parser = subparsers.add_parser("sns", help="Synergy naming system")
    sns_sub = sns_parser.add_subparsers(dest="sns_command")

    reg_cmd = sns_sub.add_parser("register", help="Register synergy name -> synergy address")
    reg_cmd.add_argument("--file", default="synergy_seed.json", help="Path to synergy seed file")
    reg_cmd.add_argument("--password", default="", help="Password if synergy seed is encrypted")
    reg_cmd.add_argument("--name", required=True, help="myname.syn")
    reg_cmd.set_defaults(func=cmd_sns_register)

    look_cmd = sns_sub.add_parser("lookup", help="Lookup synergy name")
    look_cmd.add_argument("synergy_name", help="the name to look up, e.g. bob.syn")
    look_cmd.set_defaults(func=cmd_sns_lookup)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


def cmd_wallet_create(args):
    print(f"[Wallet] create stub for name={args.name}")
    # Insert your real wallet code here

def cmd_uma_generate(args):
    synergy_data = generate_synergy_seed(args.password)
    save_synergy_info(args.out, synergy_data)
    print(f"[UMA] synergy address generated: {synergy_data['synergy_address']}")
    print(f"Saved synergy data in {args.out}")

def cmd_uma_derive(args):
    synergy_data = load_synergy_info(args.file, password=args.password)
    if not synergy_data:
        print(f"Error: synergy seed file {args.file} not found or password is invalid.")
        return
    result = derive_subkey_for_chain(synergy_data, args.chain, args.password)
    if not result["success"]:
        print("Error deriving subkey:", result["error"])
    else:
        print(f"[UMA] chain={result['chain_name']} -> address={result['chain_address']}")

def cmd_sns_register(args):
    synergy_data = load_synergy_info(args.file, password=args.password)
    if not synergy_data:
        print(f"Error: synergy seed file {args.file} not found or invalid password.")
        return
    synergy_addr = synergy_data["synergy_address"]
    reg_res = register_name(args.name, synergy_addr)
    if reg_res["success"]:
        print(f"[SNS] Registered {args.name} -> {synergy_addr}")
    else:
        print(f"[SNS] Registration failed: {reg_res['error']}")

def cmd_sns_lookup(args):
    res = lookup_name(args.synergy_name)
    if res["success"]:
        print(f"[SNS] {args.synergy_name} -> {res['synergy_addr']}")
    else:
        print(f"[SNS] Lookup failed: {res['error']}")

if __name__ == "__main__":
    main()
