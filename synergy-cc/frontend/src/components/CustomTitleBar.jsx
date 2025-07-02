import React from "react";
import "../styles/CustomTitleBar.css";

function CustomTitleBar() {
  const handleClose = () => {
    if (window.electronAPI && window.electronAPI.closeWindow) {
      window.electronAPI.closeWindow();
    }
  };

  return (
    <div className="custom-title-bar">
      <button className="close-btn" title="Close window" onClick={handleClose}>
        ×
      </button>
    </div>
  );
}

export default CustomTitleBar;
