import React, { useState } from "react";
import Modal from "../modals/Modal";
import UmaWalletWizard from "../modals/umaWalletWizard";
import logo from "./logo.png";
import "../styles/global.css";

const buttons = [
  "Dashboard",
  "Transactions",
  "Settings",
  "Help"
];

export default function Sidebar({ wallet, onWalletCreated, onLogout }) {
  const [showWizard, setShowWizard] = useState(false);

  return (
    <div className="sidebar">
      <img src={logo} alt="Synergy Logo" className="sidebar-logo" />
      <div className="sidebar-content">
        <h1 style={{ fontWeight: 900, fontSize: 38 }}>Synergy Wallet</h1>
        <hr className="top" />
        {buttons.map(label => (
          <button key={label} className="sidebar-button">{label}</button>
        ))}
        <button className="sidebar-button" onClick={() => setShowWizard(true)}>
          + Create New Wallet
        </button>
        <hr className="bottom" />
        {wallet && (
          <div style={{ width: "100%", marginTop: 10 }}>
            <div style={{ fontFamily: "Inter Medium", fontSize: 14, marginBottom: 3 }}>
              Current Wallet:
            </div>
            <div style={{
              fontFamily: "monospace",
              fontSize: 13,
              background: "#251844cc",
              borderRadius: 7,
              padding: "6px 10px",
              letterSpacing: "0.5px",
              marginBottom: 4,
              wordBreak: "break-all"
            }}>
              {typeof wallet?.synergyAddress === "string"
                ? wallet.synergyAddress.slice(0, 11) + "..." + wallet.synergyAddress.slice(-3)
                : "(no address)"}
            </div>
          </div>
        )}
      </div>
      <Modal
        isOpen={showWizard}
        onClose={() => setShowWizard(false)}
        title="Create New Wallet"
      >
        <UmaWalletWizard
          isOpen={showWizard}
          onClose={() => setShowWizard(false)}
          onWalletCreated={walletObj => {
            setShowWizard(false);
            if (onWalletCreated) onWalletCreated(walletObj);
          }}
        />
      </Modal>
      <div className="sidebar-footer">
        {wallet && (
          <button
            className="sidebar-button"
            style={{ marginBottom: 16 }}
            onClick={onLogout}
          >
            Log Out
          </button>
        )}
        <small>Synergy Network © 2025</small>
      </div>
    </div>
  );
}
