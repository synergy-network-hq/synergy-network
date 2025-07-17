import React, {useState} from "react";
import Modal from "../modals/Modal";
import UmaWalletWizard from "../modals/umaWalletWizard";
import logo from "./logo.png";
import "../styles/global.css";

const buttons = ["Dashboard", "Transactions", "Settings", "Help"];

export default function Sidebar({wallet, onWalletCreated, onLogout}) {
    const [showWizard, setShowWizard] = useState(false);

    return (
        <div className="sidebar">
            <img src={logo} alt="Synergy Logo" className="sidebar-logo" />
            <div className="sidebar-content">
                <h2 style={{fontWeight: 900, fontSize: 38}}>Synergy Wallet</h2>
                <hr className="top" />
                {buttons.map((label) => (
                    <button key={label} className="sidebar-button">
                        {label}
                    </button>
                ))}

                <hr className="bottom" />
                {wallet && (
                    <div style={{width: "100%", marginTop: 10}}>
                        <div style={{fontFamily: "Inter Medium", fontSize: 14, marginBottom: 3}}>Current Wallet:</div>
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
                                ? wallet.synergyAddress.slice(0, 11) + "..." + wallet.synergyAddress.slice(-3)
                                : "(no address)"}
                        </div>
                    </div>
                )}
            </div>

            <div className="sidebar-footer">
                {wallet && (
                    <button className="sidebar-button" style={{marginBottom: 16}} onClick={onLogout}>
                        Log Out
                    </button>
                )}
                <small>Synergy Network © 2025</small>
            </div>
        </div>
    );
}
