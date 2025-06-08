use synergy_testnet::{ContractExecutor, ContractMetadata};

#[test]
fn test_contract_deployment_and_execution() {
    let mut executor = ContractExecutor::new();

    let metadata = ContractMetadata {
        name: "TestContract".to_string(),
        version: "0.1.0".to_string(),
        abi_hash: "fakehash123".to_string(),
    };

    let wasm_code = vec![0x00, 0x61, 0x73, 0x6d]; // WASM magic header
    let address = "sYnQ-CONTRACT-abc123".to_string();

    executor.deploy_contract(address.clone(), wasm_code.clone(), metadata.clone()).unwrap();

    let result = executor.execute_contract(&address, b"input-bytes");
    assert!(result.is_ok());

    println!("✅ Contract deployed and simulated execution succeeded.");
}
