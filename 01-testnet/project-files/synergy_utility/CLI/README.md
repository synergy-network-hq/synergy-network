# Synergy Network CLI Utility

This directory contains the Command Line Interface (CLI) utility for interacting with the Synergy Network.

## File Structure

```
cli_utility/
├── assets/                # Asset files for the CLI utility
├── synergy_uma/           # Universal Meta Address functionality
│   ├── __init__.py
│   ├── chain_derivations.py
│   ├── pq_keys.py
│   └── sns_api.py
├── utility/               # Core utility functionality
│   ├── __init__.py
│   ├── common/            # Common utilities
│   │   ├── __init__.py
│   │   └── config.py
│   └── core/              # Core functionality
│       ├── __init__.py
│       ├── naming.py
│       ├── token.py
│       └── wallet.py
├── __init__.py
├── cli_app.py             # Main CLI application
└── requirements.txt       # Python dependencies
```

## Installation

1. Ensure you have Python 3.8 or higher installed:
   ```
   python3 --version
   ```

2. Clone the repository and navigate to the cli_utility directory:
   ```
   git clone https://github.com/hootzluh/synergy_utility.git
   cd synergy_utility/cli_utility
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

The CLI utility provides a command-line interface for interacting with the Synergy Network. You can run the utility using the following command:

```
python cli_app.py [command] [options]
```

### Available Commands

- **Wallet Operations**
  ```
  python cli_app.py wallet create
  ```

- **Token Operations**
  ```
  python cli_app.py token create
  ```

- **Universal Meta Address Operations**
  ```
  python cli_app.py uma generate
  python cli_app.py uma derive
  ```

- **Synergy Naming System Operations**
  ```
  python cli_app.py sns register
  python cli_app.py sns lookup
  ```

For more detailed information about each command, use the `--help` option:

```
python cli_app.py --help
python cli_app.py wallet --help
```

## Examples

1. Create a new wallet:
   ```
   python cli_app.py wallet create
   ```

2. Generate a new Universal Meta Address:
   ```
   python cli_app.py uma generate
   ```

3. Look up a domain name in the Synergy Naming System:
   ```
   python cli_app.py sns lookup myname.syn
   ```

## Troubleshooting

If you encounter any issues with the CLI utility, please check the following:

1. Ensure you have the correct Python version installed
2. Verify that all dependencies are installed correctly
3. Check that you are using the correct command syntax

If problems persist, please report them to the Synergy Network team.
