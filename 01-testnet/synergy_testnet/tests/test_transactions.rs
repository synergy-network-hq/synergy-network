use synergy_testnet::block::BlockChain;
use synergy_testnet::transaction::Transaction;

#[test]
fn test_transaction_in_block() {
    let tx = Transaction::new(
        "sYnQ1sender".to_string(),
        "sYnQ1receiver".to_string(),
        50,
        1,
        "valid-sig".to_string(),
    );

    let mut chain = BlockChain::new();
    chain.genesis();

    let block = Block::new(
        1,
        vec![tx.clone()],
        chain.last().unwrap().hash.clone(),
        "validator-123".to_string(),
        0,
    );

    assert_eq!(block.transactions.len(), 1);
    assert_eq!(block.transactions[0].amount, 50);
    println!("✅ Transaction successfully included in block.");
}
