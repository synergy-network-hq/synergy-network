import React, { useState, useEffect } from 'react';
import { query_chain } from '../../../testnet_connector';

const ViewWallet = () => {
  const [wallets, setWallets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchChain() {
      const result = await query_chain();
      try {
        const body = result.split("\r\n\r\n")[1];
        const blocks = JSON.parse(body);
        const accounts = {};

        blocks.forEach(block => {
          block.transactions.forEach(tx => {
            accounts[tx.sender] = accounts[tx.sender] || { balance: 0, address: tx.sender };
            accounts[tx.receiver] = accounts[tx.receiver] || { balance: 0, address: tx.receiver };
            accounts[tx.sender].balance -= tx.amount;
            accounts[tx.receiver].balance += tx.amount;
          });
        });

        const list = Object.values(accounts).map(acc => ({
          ...acc,
          balance: acc.balance + " SYN"
        }));

        setWallets(list);
      } catch (e) {
        console.error("❌ Failed to parse chain response", e);
      } finally {
        setLoading(false);
      }
    }

    fetchChain();
  }, []);

  return (
    <div className="view-wallet p-6 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-white mb-6">Wallets on Chain</h2>
      {loading && <p className="text-white">Loading chain data...</p>}
      {wallets.map((wallet, index) => (
        <div key={index} className="border rounded-lg p-4 bg-black/40 backdrop-blur-lg text-white mb-4">
          <p><strong>Address:</strong> {wallet.address}</p>
          <p><strong>Balance:</strong> {wallet.balance}</p>
        </div>
      ))}
    </div>
  );
};

export default ViewWallet;
