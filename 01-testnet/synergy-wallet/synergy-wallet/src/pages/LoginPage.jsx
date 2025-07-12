import React, { useState } from "react";
import Modal from "../modals/Modal";
import CreateWalletWizard from "../modals/CreateWalletWizard";
import ImportWalletWizard from "../modals/ImportWalletWizard";

export default function LoginPage({ onWalletCreatedOrImported }) {
  const [showCreate, setShowCreate] = useState(false);
  const [showImport, setShowImport] = useState(false);

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
          onClick={() => setShowCreate(true)}>
          Create New Wallet
        </button>
        <button className="sidebar-button"
          style={{ fontFamily: "Inter Bold", fontWeight: 700, fontSize: 19 }}
          onClick={() => setShowImport(true)}>
          Import/Recover Wallet
        </button>
      </div>
      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Create New Wallet">
        <CreateWalletWizard
          onComplete={wallet => {
            setShowCreate(false);
            onWalletCreatedOrImported(wallet);
          }}
          onCancel={() => setShowCreate(false)}
        />
      </Modal>
      <Modal isOpen={showImport} onClose={() => setShowImport(false)} title="Import/Recover Wallet">
        <ImportWalletWizard
          onComplete={wallet => {
            setShowImport(false);
            onWalletCreatedOrImported(wallet);
          }}
          onCancel={() => setShowImport(false)}
        />
      </Modal>
    </div>
  );
}
