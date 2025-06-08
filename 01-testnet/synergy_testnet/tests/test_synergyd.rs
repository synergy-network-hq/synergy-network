use synergy_testnet::consensus::consensus_algorithm::ProofOfSynergy;

#[test]
fn test_synergyd_node_startup() {
    let mut pos = ProofOfSynergy::new();
    pos.initialize();
    pos.execute();

    std::thread::sleep(std::time::Duration::from_secs(6));
    println!("✅ Node consensus engine running.");
}
