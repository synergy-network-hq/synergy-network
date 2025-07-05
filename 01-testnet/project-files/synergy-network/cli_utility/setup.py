from setuptools import setup, find_packages

setup(
    name="synergy-network-cli",
    version="1.0.0",
    description="Command Line Interface for Synergy Network",
    author="Synergy Network Team",
    author_email="info@synergy-network.io",
    packages=find_packages(),
    install_requires=[
        "argparse>=1.4.0",
        "cmd2>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'synergy-cli=cli_app:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
