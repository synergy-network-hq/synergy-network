import React from "react";
import Sidebar from "./components/Sidebar";
import MainContent from "./components/MainContent";
import "./App.css";

function App() {
  return (
    <div>
      <img id="backgroundGif" src="rainbow.gif" alt="Rainbow Background" />
      <div id="overlay"></div>
      <div className="container">
        <Sidebar />
        <MainContent />
      </div>
    </div>
  );
}

export default App;
