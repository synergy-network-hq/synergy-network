const { app, BrowserWindow } = require('electron');
const path = require('path');
const { ipcMain } = require('electron');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 900,
    frame: false,               // <-- REMOVE native frame/title bar
    transparent: false,         // keep false unless you want a transparent background (not needed for glass buttons)
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, "preload.js"), // (we'll use this for close)
    }
  });
  // During dev, load the React dev server (Vite default: 5173)
  win.loadURL('http://localhost:5173');
  // For production, load the local HTML:
  // win.loadFile(path.join(__dirname, 'frontend/dist/index.html'));
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });

ipcMain.on('close-window', () => {
  const wins = BrowserWindow.getAllWindows();
  if (wins.length > 0) wins[0].close();
});
