import React from "react";

export default function Dashboard({ wallet, onLogout }) {
  return (
    <div className="container">
      <div className="content">
        <section className="section dashboard-card">
          <h1 className="h1" style={{ marginBottom: 18 }}>Wallet Dashboard</h1>
          <div className="field" style={{ marginBottom: 22 }}>
            <strong>Synergy Address:</strong>
            <div className="address-box" style={{
              background: "#241133",
              borderRadius: 8,
              padding: "7px 14px",
              fontSize: 16,
              fontFamily: "monospace",
              display: "flex",
              alignItems: "center",
              marginTop: 6,
              maxWidth: 480
            }}>
              <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {wallet?.synergyAddress}
              </span>
              <button
                className="copy-btn"
                style={{
                  marginLeft: 8,
                  padding: 7,
                  background: "none",
                  border: "none",
                  display: "flex",
                  alignItems: "center",
                  cursor: "pointer"
                }}
                title="Copy address"
                onClick={() => navigator.clipboard.writeText(wallet?.synergyAddress)}
              >
                {/* SVG clipboard icon (Material/Feather/Lucide style) */}
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="#ccc" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15V5a2 2 0 0 1 2-2h10" />
                </svg>
              </button>
            </div>
          </div>
          <div className="field" style={{ marginBottom: 24 }}>
            <strong>PQC Public Key:</strong>
            <div className="pubkey-box" style={{
              background: "#221c36",
              borderRadius: 8,
              padding: "7px 11px",
              fontFamily: "monospace",
              fontSize: 12,
              marginTop: 5,
              maxHeight: 80,
              overflow: "auto"
            }}>
              {wallet?.publicKey}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
