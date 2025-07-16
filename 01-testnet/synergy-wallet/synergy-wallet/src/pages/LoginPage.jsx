import React, { useState } from "react";
import Modal from "../modals/Modal";
import "../styles/global.css";
import UmaWalletWizard from "../modals/umaWalletWizard";

export default function LoginPage({ onWalletCreatedOrImported }) {
  const [showWizard, setShowWizard] = useState(false);

  return (
    <div className="content inlineStyle91">
      <h1 className="inlineStyle92">Welcome to Synergy Wallet</h1>
      <div className="inlineStyle93">
        <button
          className="sidebar-button inlineStyle94"
          onClick={() => setShowWizard(true)}
        >
          Create New Wallet
        </button>
        <button
          className="sidebar-button inlineStyle94"
          onClick={() => setShowWizard(true)}
        >
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
