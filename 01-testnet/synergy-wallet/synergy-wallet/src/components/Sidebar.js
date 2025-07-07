import React from "react";
import logo from "./logo.png"; // Adjust path if using public/

const buttons = [
  "Dashboard",
  "Transactions",
  "Settings",
  "Help"
];

export default function Sidebar() {
  return (
    <div className="sidebar">
      <img src={logo} alt="Synergy Wallet Logo" className="sidebar-logo" />
      <div className="sidebar-content">
        <h2>Synergy Wallet</h2>
        <h2>Dashboard</h2>
        <hr></hr>
          {buttons.map(label => (
            <button key={label} className="button">{label}</button>
          ))}
          <hr></hr>
      </div>
      <div className="sidebar-footer">
        <button className="button">Logout</button>
        <p>Version 1.0.0</p>
        <p>&copy; 2025 Synergy Network</p>
      </div>
    </div>
  );
}
