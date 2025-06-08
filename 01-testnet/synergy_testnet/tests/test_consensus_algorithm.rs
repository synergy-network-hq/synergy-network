use synergy_testnet::gitProofOfSynergy;

#[test]
fn test_proof_of_synergy_execution() {
    let mut pos = ProofOfSynergy::new();
    pos.initialize();
    pos.execute();

    // Let consensus run briefly (in real use you'd check state changes)
    std::thread::sleep(std::time::Duration::from_secs(6));
    println!("✅ ProofOfSynergy execute ran without panic.");
}
