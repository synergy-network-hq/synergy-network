import React from "react";
import "../styles/global.css";

export default function Dashboard({ wallet, onLogout }) {
  return (
    <div className="container">
      <div className="content">
        <section className="section dashboard-card">
          <h1 className="h1 inlineStyle84">Wallet Dashboard</h1>
          {wallet && (
            <div style={{ width: "100%", marginTop: 10 }}>
              <div
                style={{
                  fontFamily: "monospace",
                  fontSize: 13,
                  background: "#251844cc",
                  borderRadius: 7,
                  padding: "6px 10px",
                  letterSpacing: "0.5px",
                  marginBottom: 4,
                  wordBreak: "break-all",
                }}
              >
                {typeof wallet?.synergyAddress === "string"
                  ? wallet.synergyAddress.slice(0, 11) +
                    "..." +
                    wallet.synergyAddress.slice(-3)
                  : "(no address)"}
              </div>
            </div>
          )}
          <div className="field inlineStyle85">
            <strong>Synergy Address:</strong>
            <div className="address-box inlineStyle86">
              <span className="inlineStyle87">{wallet?.synergyAddress}</span>
              <button
                className="copy-btn inlineStyle14"
                title="Copy address"
                onClick={() =>
                  navigator.clipboard.writeText(wallet?.synergyAddress)
                }
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  fill="none"
                  stroke="#ccc"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  viewBox="0 0 24 24"
                >
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15V5a2 2 0 0 1 2-2h10" />
                </svg>
              </button>
            </div>
          </div>
          <div className="field inlineStyle28">
            <strong>Bitcoin Address:</strong>
            <div className="address-box inlineStyle88">
              {wallet?.bitcoinAddress}
            </div>
          </div>
          <div className="field inlineStyle28">
            <strong>Ethereum Address:</strong>
            <div className="address-box inlineStyle88">
              {wallet?.ethereumAddress}
            </div>
          </div>
          <div className="field inlineStyle28">
            <strong>Solana Address:</strong>
            <div className="address-box inlineStyle88">
              {wallet?.solanaAddress}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
