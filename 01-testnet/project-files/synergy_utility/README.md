# Synergy Utility Project Structure

```
synergy_utility_restructured
├── CLI
│   ├── README.md
│   ├── __init__.py
│   ├── assets
│   ├── cli_app.py
│   ├── requirements.txt
│   ├── setup.py
│   ├── synergy_uma
│   │   ├── __init__.py
│   │   ├── chain_derivations.py
│   │   ├── pq_keys.py
│   │   └── sns_api.py
│   └── utility
│       ├── __init__.py
│       ├── common
│       │   ├── __init__.py
│       │   └── config.py
│       └── core
│           ├── __init__.py
│           ├── blockchain
│           │   ├── __init__.py
│           │   └── block.py
│           ├── naming.py
│           ├── network
│           │   ├── __init__.py
│           │   └── p2p.py
│           ├── state
│           │   ├── __init__.py
│           │   └── state.py
│           ├── token.py
│           ├── transaction
│           │   ├── __init__.py
│           │   └── transaction.py
│           └── wallet.py
├── GUI
│   ├── README.md
│   ├── __init__.py
│   ├── assets
│   │   ├── metal.jpg
│   │   ├── sn-logo-dark.png
│   │   ├── sn-logo-light.png
│   │   ├── syn 2.icns
│   │   ├── syn.icns
│   │   └── syn.png
│   ├── index.html
│   ├── main.js
│   ├── package-lock.json
│   ├── package.json
│   ├── preload.js
│   ├── python_bridge.py
│   ├── renderer.js
│   ├── styles.css
│   ├── synergy_uma
│   │   ├── __init__.py
│   │   ├── chain_derivations.py
│   │   ├── pq_keys.py
│   │   └── sns_api.py
│   └── utility
│       ├── __init__.py
│       ├── common
│       │   ├── __init__.py
│       │   └── config.py
│       └── core
│           ├── __init__.py
│           ├── blockchain
│           │   ├── __init__.py
│           │   └── block.py
│           ├── naming.py
│           ├── network
│           │   ├── __init__.py
│           │   └── p2p.py
│           ├── state
│           │   ├── __init__.py
│           │   └── state.py
│           ├── token.py
│           ├── transaction
│           │   ├── __init__.py
│           │   └── transaction.py
│           └── wallet.py
├── Implementation
│   ├── consensus
│   │   ├── pbft_consensus.py
│   │   ├── synergy_points.py
│   │   ├── task_pool.py
│   │   └── validator_cluster.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── blockchain
│   │   │   ├── __init__.py
│   │   │   └── block.py
│   │   ├── network
│   │   │   ├── __init__.py
│   │   │   └── p2p.py
│   │   ├── state
│   │   │   ├── __init__.py
│   │   │   └── state.py
│   │   └── transaction
│   │       ├── __init__.py
│   │       └── transaction.py
│   ├── cryptography
│   │   └── pqc
│   │       ├── __init__.py
│   │       ├── address.py
│   │       ├── dilithium.py
│   │       ├── hash.py
│   │       └── kyber.py
│   └── utility
│       ├── core
│       │   ├── config.py
│       │   ├── naming.py
│       │   ├── token.py
│       │   └── wallet.py
│       └── setup.py
├── extra
│   ├── implementation_core___pycache__
│   │   ├── naming.cpython-312.pyc
│   │   ├── token.cpython-312.pyc
│   │   └── wallet.cpython-312.pyc
│   ├── implementation_utility_cli_utility
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── cli_app.py
│   │   ├── requirements.txt
│   │   ├── synergy_uma
│   │   │   ├── __init__.py
│   │   │   ├── chain_derivations.py
│   │   │   ├── pq_keys.py
│   │   │   └── sns_api.py
│   │   └── utility
│   │       ├── __init__.py
│   │       ├── common
│   │       │   ├── __init__.py
│   │       │   └── config.py
│   │       └── core
│   │           ├── __init__.py
│   │           ├── __pycache__
│   │           │   ├── __init__.cpython-312.pyc
│   │           │   └── wallet.cpython-312.pyc
│   │           ├── naming.py
│   │           ├── token.py
│   │           └── wallet.py
│   ├── implementation_utility_gui
│   │   ├── assets
│   │   │   └── syn.icns
│   │   ├── index.html
│   │   ├── main.js
│   │   ├── package.json
│   │   ├── preload.js
│   │   ├── python_bridge.py
│   │   ├── renderer.js
│   │   └── styles.css
│   ├── implementation_utility_gui_utility
│   │   ├── README.md
│   │   ├── assets
│   │   │   ├── syn 2.icns
│   │   │   ├── syn.icns
│   │   │   └── syn.png
│   │   ├── index.html
│   │   ├── main.js
│   │   ├── package-lock.json
│   │   ├── package.json
│   │   ├── preload.js
│   │   ├── python_bridge.py
│   │   ├── renderer.js
│   │   ├── styles.css
│   │   └── synergy_uma
│   │       ├── chain_derivations.py
│   │       ├── pq_keys.py
│   │       └── sns_api.py
│   └── misc
└── shared
    ├── __init__.py
    ├── common
    │   ├── __init__.py
    │   └── config.py
    ├── consensus
    │   ├── __init__.py
    │   ├── pbft_consensus.py
    │   ├── synergy_points.py
    │   ├── task_pool.py
    │   └── validator_cluster.py
    ├── core
    │   ├── __init__.py
    │   ├── blockchain
    │   │   ├── __init__.py
    │   │   └── block.py
    │   ├── naming.py
    │   ├── network
    │   │   ├── __init__.py
    │   │   └── p2p.py
    │   ├── state
    │   │   ├── __init__.py
    │   │   └── state.py
    │   ├── token.py
    │   ├── transaction
    │   │   ├── __init__.py
    │   │   └── transaction.py
    │   └── wallet.py
    ├── cryptography
    │   ├── __init__.py
    │   └── pqc
    │       ├── __init__.py
    │       ├── address.py
    │       ├── dilithium.py
    │       ├── hash.py
    │       └── kyber.py
    └── synergy_uma
        ├── __init__.py
        ├── chain_derivations.py
        ├── pq_keys.py
        └── sns_api.py
```
