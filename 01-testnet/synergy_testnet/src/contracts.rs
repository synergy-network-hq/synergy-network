use std::collections::HashMap;

/// A deployed smart contract instance
#[derive(Debug, Clone)]
pub struct Contract {
    pub address: String,
    pub code: Vec<u8>, // Raw WASM bytecode
    pub metadata: ContractMetadata,
}

/// Metadata describing the smart contract (supports ABI metadata, versioning, hash refs)
#[derive(Debug, Clone)]
pub struct ContractMetadata {
    pub name: String,
    pub version: String,
    pub abi_hash: String,
}

/// Registry for deployed contracts and executor handler
#[derive(Debug)]
pub struct ContractExecutor {
    pub contracts: HashMap<String, Contract>,
}

impl ContractExecutor {
    pub fn new() -> Self {
        ContractExecutor {
            contracts: HashMap::new(),
        }
    }

    /// Deploys a WASM contract to the in-memory registry
    pub fn deploy_contract(&mut self, address: String, code: Vec<u8>, metadata: ContractMetadata) -> Result<(), String> {
        if self.contracts.contains_key(&address) {
            return Err(format!("Contract already exists at address {}", address));
        }

        let contract = Contract {
            address: address.clone(),
            code,
            metadata,
        };

        self.contracts.insert(address.clone(), contract);
        println!("✅ Contract deployed at address: {}", address);
        Ok(())
    }

    /// Executes a contract from the registry with given input data
    pub fn execute_contract(&self, address: &str, input_data: &[u8]) -> Result<String, String> {
        let contract = self.contracts.get(address).ok_or_else(|| "Contract not found.".to_string())?;

        // Placeholder: Real WASM engine integration required
        println!("⚙️ Executing contract '{}' (v{})", contract.metadata.name, contract.metadata.version);
        println!("WASM code size: {} bytes", contract.code.len());
        println!("Received input: 0x{}", hex::encode(input_data));

        Ok(format!("Execution completed for contract '{}'. No return value.", contract.metadata.name))
    }

    /// Lists all registered contract addresses
    pub fn list_contracts(&self) -> Vec<String> {
        self.contracts.keys().cloned().collect()
    }

    /// Retrieves metadata for a specific contract address
    pub fn get_metadata(&self, address: &str) -> Option<&ContractMetadata> {
        self.contracts.get(address).map(|c| &c.metadata)
    }
}
