import React, { useState } from "react";
import Modal from "../modals/Modal";
import "../styles/global.css";
import UmaWalletWizard from "../modals/umaWalletWizard";

export default function LoginPage({ onWalletCreatedOrImported }) {
  const [showWizard, setShowWizard] = useState(false);

  return (
    <div className="content" style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center"
    }}>
      <h1 style={{
        fontFamily: "Inter Black, Inter, sans-serif",
        fontWeight: 900,
        fontSize: 38,
        marginBottom: 30,
        color: "#fff",
        textShadow: "2px 2px 6px #000"
      }}>
        Welcome to Synergy Wallet
      </h1>
      <div style={{ display: "flex", gap: 32 }}>
        <button className="sidebar-button"
          style={{ fontFamily: "Inter Bold", fontWeight: 700, fontSize: 19 }}
          onClick={() => setShowWizard(true)}>
          Create New Wallet
        </button>
        <button className="sidebar-button"
          style={{ fontFamily: "Inter Bold", fontWeight: 700, fontSize: 19 }}
          onClick={() => setShowWizard(true)}>
          Import/Recover Wallet
        </button>
      </div>
        <UmaWalletWizard
          isOpen={showWizard}
          onClose={() => setShowWizard(false)}
          onWalletCreated={onWalletCreatedOrImported}
        />

    </div>
  );
}
