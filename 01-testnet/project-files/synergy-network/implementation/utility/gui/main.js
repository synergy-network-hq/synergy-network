const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const Store = require('electron-store');

// Initialize config store
const store = new Store({
  name: 'synergy-config',
  defaults: {
    windowSize: { width: 1200, height: 800 },
    theme: 'dark'
  }
});

// Keep a global reference of the window object
let mainWindow;

// Path to Python executable and scripts
const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
const scriptPath = path.join(__dirname, '..', '..', '..', 'implementation');

// Create the browser window
function createWindow() {
  const { width, height } = store.get('windowSize');
  
  mainWindow = new BrowserWindow({
    width,
    height,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets', 'icon.png'),
    show: false
  });

  // Load the index.html file
  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Save window size on close
  mainWindow.on('close', () => {
    store.set('windowSize', mainWindow.getBounds());
  });

  // Emitted when the window is closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Create window when Electron has finished initialization
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC handlers for wallet operations
ipcMain.handle('wallet:list', async () => {
  return runPythonScript('wallet_list');
});

ipcMain.handle('wallet:create', async (event, name, password) => {
  return runPythonScript('wallet_create', [name, password]);
});

ipcMain.handle('wallet:import', async (event, name, privateKey, password) => {
  return runPythonScript('wallet_import', [name, privateKey, password]);
});

ipcMain.handle('wallet:show', async (event, address) => {
  return runPythonScript('wallet_show', [address]);
});

// IPC handlers for token operations
ipcMain.handle('token:list', async () => {
  return runPythonScript('token_list');
});

ipcMain.handle('token:create', async (event, name, symbol, tokenType, initialSupply, maxSupply, decimals) => {
  return runPythonScript('token_create', [name, symbol, tokenType, initialSupply, maxSupply, decimals]);
});

ipcMain.handle('token:mint', async (event, tokenId, amount, toAddress, password) => {
  return runPythonScript('token_mint', [tokenId, amount, toAddress, password]);
});

// IPC handlers for naming system operations
ipcMain.handle('naming:list', async () => {
  return runPythonScript('naming_list');
});

ipcMain.handle('naming:check', async (event, domainName) => {
  return runPythonScript('naming_check', [domainName]);
});

ipcMain.handle('naming:register', async (event, domainName, registrationPeriod, password) => {
  return runPythonScript('naming_register', [domainName, registrationPeriod, password]);
});

// Helper function to run Python scripts
async function runPythonScript(command, args = []) {
  return new Promise((resolve, reject) => {
    // Path to the Python bridge script
    const bridgeScript = path.join(scriptPath, 'utility', 'gui', 'python_bridge.py');
    
    // Create command array
    const cmdArgs = [bridgeScript, command, ...args];
    
    // Spawn Python process
    const pythonProcess = spawn(pythonPath, cmdArgs);
    
    let stdoutData = '';
    let stderrData = '';
    
    // Collect stdout data
    pythonProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });
    
    // Collect stderr data
    pythonProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
    });
    
    // Handle process completion
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdoutData);
          resolve(result);
        } catch (error) {
          resolve({ success: false, error: 'Failed to parse result' });
        }
      } else {
        resolve({ success: false, error: stderrData || `Process exited with code ${code}` });
      }
    });
    
    // Handle process errors
    pythonProcess.on('error', (error) => {
      resolve({ success: false, error: error.message });
    });
  });
}
