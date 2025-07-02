import React from "react";
import CustomTitleBar from "./components/CustomTitleBar";
import Background from "./components/Background";
import './styles/App.css'
import "./styles/WindowBorder.css";
import Sidebar from "./components/Sidebar";

function App() {
  return (
    <div className="window-border">
        <CustomTitleBar />
        <Sidebar />
    </div>
  );
}

export default App;
