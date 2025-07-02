import React, { useState } from "react";
import { generateKeypair } from "../api/pqcCrypto";

export default function WalletCreate() {
  const [pub, setPub] = useState("");
  const [priv, setPriv] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onGenerate = async () => {
    setLoading(true);
    setError("");
    try {
      const result = await generateKeypair();
      setPub(result.public_key || result.publicKey || "No public key returned");
      setPriv(result.private_key || result.privateKey || "No private key returned");
    } catch (e) {
      setError(e.toString());
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Create Quantum-Safe Wallet</h2>
      <button onClick={onGenerate} disabled={loading}>
        {loading ? "Generating..." : "Generate Dilithium Keypair"}
      </button>
      {error && <div style={{ color: "red", marginTop: 16 }}>{error}</div>}
      {pub && (
        <div style={{ marginTop: 16 }}>
          <b>Public Key:</b>
          <pre style={{ wordBreak: "break-all" }}>{pub}</pre>
          <b>Private Key:</b>
          <pre style={{ wordBreak: "break-all" }}>{priv}</pre>
        </div>
      )}
    </div>
  );
}
