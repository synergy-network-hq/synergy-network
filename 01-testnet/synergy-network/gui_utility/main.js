// main.js
const {app, BrowserWindow, ipcMain} = require("electron");
const path = require("path");
const fs = require("fs");
const {spawn} = require("child_process");
const Store = require("electron-store");

const store = new Store({
    name: "synergy-config",
    defaults: {
        windowSize: {width: 1200, height: 800},
        theme: "dark",
    },
});

let mainWindow;
const pythonPath = process.platform === "win32" ? "python" : "python3";
const scriptPath = path.join(__dirname, "python_bridge.py");

function createWindow() {
    const {width, height} = store.get("windowSize");
    mainWindow = new BrowserWindow({
        width,
        height,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            preload: path.join(__dirname, "preload.js"),
        },
        icon: path.join(__dirname, "assets", "syn.png"),
        show: false,
    });

    mainWindow.loadFile(path.join(__dirname, "index.html"));
    mainWindow.once("ready-to-show", () => {
        mainWindow.show();
    });
    mainWindow.on("close", () => {
        store.set("windowSize", mainWindow.getBounds());
    });
    mainWindow.on("closed", () => {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    createWindow();
    app.on("activate", () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
        app.quit();
    }
});

async function runPythonScript(command, args = []) {
    return new Promise((resolve, reject) => {
        const cmdArgs = [scriptPath, command, ...args];
        const pythonProcess = spawn(pythonPath, cmdArgs);

        let stdoutData = "";
        let stderrData = "";

        pythonProcess.stdout.on("data", (data) => {
            stdoutData += data.toString();
        });
        pythonProcess.stderr.on("data", (data) => {
            stderrData += data.toString();
        });

        pythonProcess.on("close", (code) => {
            if (code === 0) {
                try {
                    const result = JSON.parse(stdoutData);
                    resolve(result);
                } catch (err) {
                    resolve({success: false, error: "JSON parse error"});
                }
            } else {
                resolve({success: false, error: stderrData || `Process exited with code ${code}`});
            }
        });

        pythonProcess.on("error", (error) => {
            resolve({success: false, error: error.message});
        });
    });
}

// Existing wallet
ipcMain.handle("wallet:list", async () => runPythonScript("wallet_list"));
ipcMain.handle("wallet:create", async (event, name, password) => runPythonScript("wallet_create", [name, password]));
ipcMain.handle("wallet:import", async (event, name, pk, password) =>
    runPythonScript("wallet_import", [name, pk, password])
);
ipcMain.handle("wallet:show", async (event, address) => runPythonScript("wallet_show", [address]));

// Existing token
ipcMain.handle("token:list", async () => runPythonScript("token_list"));
ipcMain.handle("token:create", async (event, name, symbol, tokenType, initialSupply, maxSupply, decimals) => {
    return runPythonScript("token_create", [name, symbol, tokenType, initialSupply, maxSupply, decimals]);
});
ipcMain.handle("token:mint", async (event, tokenId, amount, toAddress, password) => {
    return runPythonScript("token_mint", [tokenId, amount, toAddress, password]);
});

// Existing naming
ipcMain.handle("naming:list", async () => runPythonScript("naming_list"));
ipcMain.handle("naming:check", async (event, domainName) => runPythonScript("naming_check", [domainName]));
ipcMain.handle("naming:register", async (event, domainName, registrationPeriod, password) => {
    return runPythonScript("naming_register", [domainName, registrationPeriod, password]);
});

// NEW UMA
ipcMain.handle("uma:generate", async (event, password) => {
    return runPythonScript("uma_generate", [password || ""]);
});

ipcMain.handle("uma:derive", async (event, chainName, password) => {
    if (!password) password = "";
    return runPythonScript("uma_derive", [chainName, password]);
});

// synergy naming lookup
ipcMain.handle("sns:lookup", async (event, synergyName) => {
    return runPythonScript("sns_lookup", [synergyName]);
});
