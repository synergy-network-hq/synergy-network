import click
import json
from . import wallet, sns, syntoken, uma, cross


@click.group()
def cli():
    """Synergy Network Utility Tool"""


@cli.group(name="wallet")
def wallet_cmd():
    """Wallet operations"""


@wallet_cmd.command("create")
@click.option("--path", default="wallet.json")
@click.option("--password", prompt=True, hide_input=True)
def wallet_create(path, password):
    info = wallet.create_wallet(password, path)
    click.echo(f"Created wallet {info['address']}")
    click.echo(f"Mnemonic: {info['mnemonic']}")


@wallet_cmd.command("address")
@click.option("--path", default="wallet.json")
@click.option("--password", prompt=True, hide_input=True)
def wallet_address(path, password):
    info = wallet.load_wallet(path, password)
    click.echo(f"Synergy: {info['address']}")
    click.echo(f"BTC: {wallet.btc_address(info['mnemonic'])}")
    click.echo(f"ETH: {wallet.eth_address(info['mnemonic'])}")
    click.echo(f"SOL: {wallet.sol_address(info['mnemonic'])}")


@cli.group(name="sns")
def sns_cmd():
    """SNS operations"""


@sns_cmd.command("register")
@click.argument("name")
@click.option("--path", default="wallet.json")
@click.option("--password", prompt=True, hide_input=True)
def sns_register(name, path, password):
    info = wallet.load_wallet(path, password)
    sns.register(name, info["address"])
    click.echo(f"Registered {name} -> {info['address']}")


@sns_cmd.command("resolve")
@click.argument("name")
def sns_resolve(name):
    addr = sns.resolve(name)
    if addr:
        click.echo(addr)
    else:
        click.echo("Name not found")


@cli.group(name="token")
def token_cmd():
    """Token operations"""


@token_cmd.command("create")
@click.argument("name")
@click.argument("symbol")
@click.option("--mutable/--immutable", default=True)
def token_create(name, symbol, mutable):
    t = token.create(name, symbol, mutable)
    click.echo(f"Created token {t.symbol}")


@token_cmd.command("mint")
@click.argument("symbol")
@click.argument("amount", type=int)
def token_mint(symbol, amount):
    token.mint(symbol, amount)
    click.echo("Minted")


@token_cmd.command("burn")
@click.argument("symbol")
@click.argument("amount", type=int)
def token_burn(symbol, amount):
    token.burn(symbol, amount)
    click.echo("Burned")


@token_cmd.command("deposit")
@click.argument("symbol")
@click.argument("address")
@click.argument("amount", type=int)
def token_deposit(symbol, address, amount):
    token.deposit(symbol, address, amount)
    click.echo("Deposited")


@token_cmd.command("balance")
@click.argument("address")
def token_balance(address):
    bal = token.balance_of(address)
    click.echo(json.dumps(bal))


@token_cmd.command("info")
@click.argument("symbol")
def token_info(symbol):
    info = token.info(symbol)
    if info:
        click.echo(info)
    else:
        click.echo("Token not found")


@cli.group(name="uma")
def uma_cmd():
    """UMA operations"""


@uma_cmd.command("generate")
@click.argument("prefix")
@click.argument("address")
def uma_generate(prefix, address):
    click.echo(uma.generate(prefix, address))


@uma_cmd.command("parse")
@click.argument("uma_str")
def uma_parse(uma_str):
    prefix, addr = uma.parse(uma_str)
    click.echo(f"prefix={prefix} address={addr}")


@cli.group(name="cross")
def cross_cmd():
    """Cross-chain operations"""


@cross_cmd.command("send")
@click.argument("chain")
@click.argument("address")
@click.argument("amount", type=int)
def cross_send(chain, address, amount):
    tx = cross.send(chain, address, amount)
    click.echo(f"sent: {tx}")


if __name__ == "__main__":
    cli()
