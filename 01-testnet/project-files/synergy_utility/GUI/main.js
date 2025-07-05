const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const Store = require("electron-store");

const store = new Store({
  name: "synergy-config",
  defaults: {
    windowSize: {
      width: 1200, height: 900,
      theme: "dark",
    },
  }
});

let mainWindow;
const pythonPath = process.platform === "win32" ? "python" : "python3";
const scriptPath = path.join(__dirname, "python_bridge.py");

function createWindow() {

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 900,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      enableRemoteModule: false,
    },
    icon: path.join(__dirname, "assets", "syn.png"),
    show: false,
  });

  mainWindow.loadFile(path.join(__dirname, "index.html"));
  mainWindow.once("ready-to-show", () => mainWindow.show());
  mainWindow.on("close", () => store.set("windowSize", mainWindow.getBounds()));
  mainWindow.on("closed", () => (mainWindow = null));
}

app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

async function runPythonScript(command, args = []) {
  return new Promise((resolve, reject) => {
    const cmdArgs = [scriptPath, command, ...args];
    const pythonProcess = spawn(pythonPath, cmdArgs);

    let stdoutData = "";
    let stderrData = "";

    pythonProcess.stdout.on("data", (data) => (stdoutData += data.toString()));
    pythonProcess.stderr.on("data", (data) => (stderrData += data.toString()));

    pythonProcess.on("close", (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdoutData);
          resolve(result);
        } catch (err) {
          resolve({ success: false, error: "JSON parse error" });
        }
      } else {
        resolve({ success: false, error: stderrData || `Exited with code ${code}` });
      }
    });

    pythonProcess.on("error", (error) => {
      resolve({ success: false, error: error.message });
    });
  });
}

// IPC Wallets
ipcMain.handle("wallet:list", () => runPythonScript("wallet_list"));
ipcMain.handle("wallet:create", (event, name, password) => runPythonScript("wallet_create", [name, password]));
ipcMain.handle("wallet:import", (event, name, pk, password) => runPythonScript("wallet_import", [name, pk, password]));
ipcMain.handle("wallet:show", (event, address) => runPythonScript("wallet_show", [address]));

// IPC Tokens
ipcMain.handle("token:list", () => runPythonScript("token_list"));
ipcMain.handle("token:create", (event, name, symbol, tokenType, initialSupply, maxSupply, decimals) =>
  runPythonScript("token_create", [name, symbol, tokenType, initialSupply, maxSupply, decimals])
);
ipcMain.handle("token:mint", (event, tokenId, amount, toAddress, password) =>
  runPythonScript("token_mint", [tokenId, amount, toAddress, password])
);

// IPC Naming
ipcMain.handle("naming:list", () => runPythonScript("naming_list"));
ipcMain.handle("naming:check", (event, domainName) => runPythonScript("naming_check", [domainName]));
ipcMain.handle("naming:register", (event, domainName, registrationPeriod, password) =>
  runPythonScript("naming_register", [domainName, registrationPeriod, password])
);

// UMA
ipcMain.handle("uma:generate", (event, password) => runPythonScript("uma_generate", [password || ""]));
ipcMain.handle("uma:derive", (event, chainName, password) => runPythonScript("uma_derive", [chainName, password]));

// SNS
ipcMain.handle("sns:lookup", (event, synergyName) => runPythonScript("sns_lookup", [synergyName]));
