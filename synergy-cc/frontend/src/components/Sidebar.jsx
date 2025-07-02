import React from "react";
import "../styles/Sidebar.css";
import "../styles/GlassButton.css";

function Sidebar() {
  return (
    <div className="sidebar">
      <button className="glass-btn" title="Stats">
        <span>Network Statistics</span>
      </button>
      <button className="glass-btn" title="Search">
        <span role="img" aria-label="search">🔍</span>
      </button>
      <button className="glass-btn" title="Settings">
        <span role="img" aria-label="settings">⚙️</span>
      </button>
      {/* Add more glass buttons as needed */}
    </div>
  );
}

export default Sidebar;
