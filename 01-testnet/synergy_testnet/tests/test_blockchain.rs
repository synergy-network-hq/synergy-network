use synergy_testnet::block::BlockChain;


#[test]
fn test_blockchain_add_and_retrieve_block() {
    let mut chain = BlockChain::new();
    chain.genesis();

    let block = Block::new(
        1,
        vec![],
        chain.last().unwrap().hash.clone(),
        "test-validator".to_string(),
        0,
    );

    chain.add_block(block.clone());

    assert_eq!(chain.last().unwrap().block_index, 1);
    println!("✅ Block successfully added and retrieved.");
}
