# setup.py (at synergy_project level)
import setuptools

setuptools.setup(
    name="synergy-cli-utility",
    version="0.1.0",
    description="Synergy Network CLI Utility",
    author="Your Name",
    packages=setuptools.find_packages(),
    install_requires=[
        "argparse",
        "pqcrypto",
        "pycryptodome",
        "eth_account",
        "solana",
        "tronpy"
    ],
    entry_points={
        "console_scripts": [
            "synergy=cli_utility.cli_app:main"
        ]
    },
    python_requires=">=3.7",
)
