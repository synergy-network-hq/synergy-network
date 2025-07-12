import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import LoginPage from "./pages/LoginPage";
import CreateWalletWizard from "./modals/CreateWalletWizard";
import ImportWalletWizard from "./modals/ImportWalletWizard";
import "./styles/global.css";

function App() {
  const [wallet, setWallet] = useState(() => {
    const stored = localStorage.getItem("synergyWallet");
    return stored ? JSON.parse(stored) : null;
  });
  console.log("Loaded wallet from storage:", wallet);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);

  // Handler for login actions
  const handleLoginAction = (action) => {
    if (action === "create") setShowCreateModal(true);
    if (action === "import") setShowImportModal(true);
  };

  // Handler for wallet creation/import
  const handleWalletReady = (walletObj) => {
    setWallet(walletObj);
    localStorage.setItem("synergyWallet", JSON.stringify(walletObj));
    setShowCreateModal(false);
    setShowImportModal(false);
  };

  const handleLogout = () => {
    setWallet(null);
    localStorage.removeItem("synergyWallet");
  };

  return (
    <div>
      <div id="overlay"></div>
      <div className="container">
        {wallet && <Sidebar wallet={wallet} onLogout={handleLogout} />}
        <div className="content">
          {!wallet ? (
            <>
              <LoginPage
                onAction={handleLoginAction}
                onWalletCreatedOrImported={handleWalletReady}
              />
              {showCreateModal && (
                <CreateWalletWizard
                  open={showCreateModal}
                  onClose={() => setShowCreateModal(false)}
                  onComplete={handleWalletReady}
                />
              )}
              {showImportModal && (
                <ImportWalletWizard
                  open={showImportModal}
                  onClose={() => setShowImportModal(false)}
                  onComplete={handleWalletReady}
                />
              )}
            </>
          ) : (
            <>
              <Dashboard wallet={wallet} />
              {showCreateModal && (
                <CreateWalletWizard
                  open={showCreateModal}
                  onClose={() => setShowCreateModal(false)}
                  onComplete={handleWalletReady}
                />
              )}
              {showImportModal && (
                <ImportWalletWizard
                  open={showImportModal}
                  onClose={() => setShowImportModal(false)}
                  onComplete={handleWalletReady}
                />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
