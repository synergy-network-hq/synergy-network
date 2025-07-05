import React, { useState, useEffect } from 'react';
import { query_chain } from '../../../testnet_connector';

const ViewToken = () => {
  const [tokens, setTokens] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTokens() {
      const result = await query_chain();
      try {
        const body = result.split("\r\n\r\n")[1];
        const blocks = JSON.parse(body);
        const seen = {};

        const tokenTransfers = blocks.flatMap(block => block.transactions.filter(tx => tx.token_metadata));
        const clean = tokenTransfers.map(tx => {
          const meta = tx.token_metadata;
          const key = meta.symbol + meta.name;
          if (!seen[key]) {
            seen[key] = {
              symbol: meta.symbol,
              name: meta.name,
              supply: meta.supply,
              creator: tx.sender,
              decimals: meta.decimals || 0
            };
          }
          return seen[key];
        });

        setTokens(Object.values(seen));
      } catch (e) {
        console.error("❌ Failed to parse token data", e);
      } finally {
        setLoading(false);
      }
    }

    fetchTokens();
  }, []);

  return (
    <div className="view-token p-6 max-w-3xl mx-auto text-white">
      <h2 className="text-2xl font-bold mb-6">Tokens on Chain</h2>
      {loading && <p>Loading token data...</p>}
      {tokens.map((token, idx) => (
        <div key={idx} className="bg-black/40 rounded-lg p-4 mb-4 backdrop-blur-md">
          <p><strong>Name:</strong> {token.name}</p>
          <p><strong>Symbol:</strong> {token.symbol}</p>
          <p><strong>Total Supply:</strong> {token.supply}</p>
          <p><strong>Creator:</strong> {token.creator}</p>
          <p><strong>Decimals:</strong> {token.decimals}</p>
        </div>
      ))}
    </div>
  );
};

export default ViewToken;
