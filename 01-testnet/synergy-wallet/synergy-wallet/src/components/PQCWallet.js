import React, { useState } from 'react';
import { initDilithium } from '../pqc/dilithium';
import { toHex, fromHex } from '../utils/hexUtils';
import { pubkeyToSynergyAddress } from '../utils/synergyAddress';

export default function PQCWallet() {
  const [dilithium, setDilithium] = useState(null);
  const [publicKey, setPublicKey] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [address, setAddress] = useState('');
  const [message, setMessage] = useState('');
  const [signature, setSignature] = useState('');
  const [verifyResult, setVerifyResult] = useState('');
  const [tokens, setTokens] = useState({});

  React.useEffect(() => {
    (async () => {
      const d = await initDilithium();
      setDilithium(d);
    })();
  }, []);

  const handleGenerate = async () => {
    if (!dilithium) return;
    const { publicKey, secretKey } = await dilithium.keypair();
    setPublicKey(toHex(publicKey));
    setSecretKey(toHex(secretKey));
    const addr = await pubkeyToSynergyAddress(publicKey);
    setAddress(addr);
    refreshTokens(addr);
    setSignature('');
    setVerifyResult('');
  };

  const handleSign = async () => {
    if (!dilithium || !secretKey) return;
    const sig = await dilithium.sign(
      new TextEncoder().encode(message),
      fromHex(secretKey)
    );
    setSignature(toHex(sig));
  };

  const handleVerify = async () => {
    if (!dilithium || !publicKey || !signature) return;
    const valid = await dilithium.verify(
      new TextEncoder().encode(message),
      fromHex(signature),
      fromHex(publicKey)
    );
    setVerifyResult(valid ? '✅ Signature valid!' : '❌ Invalid signature');
  };

  const refreshTokens = async (addr = address) => {
    if (!addr) return;
    try {
      const data = await fetch('/token_ledger.json').then(r => r.json());
      setTokens(data[addr] || {});
    } catch (e) {
      setTokens({});
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '40px auto', fontFamily: 'monospace' }}>
      <h1>Synergy Wallet PQC Test</h1>
      <h2>Create Quantum-Safe Wallet</h2>
      <button onClick={handleGenerate}>Generate Dilithium Keypair</button>
      {publicKey && (
        <div>
          <h3>Public Key:</h3>
          <textarea value={publicKey} readOnly rows={3} cols={80} />
          <h3>Secret Key:</h3>
          <textarea value={secretKey} readOnly rows={5} cols={90} />
          <h3>Synergy Address:</h3>
          <input type="text" value={address} readOnly style={{ width: 400 }} />
          <button onClick={() => refreshTokens()}>Refresh Tokens</button>
          {Object.keys(tokens).length > 0 ? (
            <div>
              <h3>Token Balances:</h3>
              <ul>
                {Object.entries(tokens).map(([sym, amt]) => (
                  <li key={sym}>{sym}: {amt}</li>
                ))}
              </ul>
            </div>
          ) : (
            <p>No tokens</p>
          )}
        </div>
      )}
      <div style={{ marginTop: 30 }}>
        <h2>Sign & Verify</h2>
        <input
          type="text"
          value={message}
          placeholder="Message to sign"
          onChange={e => setMessage(e.target.value)}
          style={{ width: 400 }}
        />
        <br />
        <button onClick={handleSign}>Sign Message</button>
        <br />
        {signature && (
          <div>
            <h3>Signature:</h3>
            <textarea value={signature} readOnly rows={5} cols={90} />
          </div>
        )}
        <button onClick={handleVerify} disabled={!signature}>Verify Signature</button>
        {verifyResult && <div><strong>{verifyResult}</strong></div>}
      </div>
    </div>
  );
}
