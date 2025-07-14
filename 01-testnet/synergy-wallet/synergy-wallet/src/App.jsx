import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import LoginPage from "./pages/LoginPage";
import UmaWalletWizard from "./modals/umaWalletWizard";
import "./styles/global.css";

function App() {
  const [wallet, setWallet] = useState(() => {
    const stored = localStorage.getItem("synergyWallet");
    return stored ? JSON.parse(stored) : null;
  });
  const [showWizard, setShowWizard] = useState(false);

  const handleLoginAction = () => setShowWizard(true);

  const handleWalletReady = (walletObj) => {
    setWallet(walletObj);
    localStorage.setItem("synergyWallet", JSON.stringify(walletObj));
    setShowWizard(false);
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
              <UmaWalletWizard
                isOpen={showWizard}
                onClose={() => setShowWizard(false)}
                onWalletCreated={handleWalletReady}
              />
            </>
          ) : (
            <>
              <Dashboard wallet={wallet} />
              <UmaWalletWizard
                isOpen={showWizard}
                onClose={() => setShowWizard(false)}
                onWalletCreated={handleWalletReady}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
