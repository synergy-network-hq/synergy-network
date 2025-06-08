// Preload script for Synergy Network Utility
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Wallet operations
  walletList: () => ipcRenderer.invoke('wallet:list'),
  walletCreate: (walletName, password) => ipcRenderer.invoke('wallet:create', walletName, password),
  walletImport: (name, privateKey, password) => ipcRenderer.invoke('wallet:import', name, privateKey, password),
  walletShow: (address) => ipcRenderer.invoke('wallet:show', address),

  // Token operations
  tokenList: () => ipcRenderer.invoke('token:list'),
  tokenCreate: (name, symbol, tokenType, initialSupply, maxSupply, decimals) =>
    ipcRenderer.invoke('token:create', name, symbol, tokenType, initialSupply, maxSupply, decimals),
  tokenMint: (tokenId, amount, toAddress, password) =>
    ipcRenderer.invoke('token:mint', tokenId, amount, toAddress, password),

  // Naming system operations
  namingList: () => ipcRenderer.invoke('naming:list'),
  namingCheck: (domainName) => ipcRenderer.invoke('naming:check', domainName),
  namingRegister: (domainName, registrationPeriod, password) =>
    ipcRenderer.invoke('naming:register', domainName, registrationPeriod, password),

  // UMA operations
  umaGenerate: (password) => ipcRenderer.invoke('uma:generate', password),
  umaDerive: (chainName, password) => ipcRenderer.invoke('uma:derive', chainName, password),

  // SNS lookup
  snsLookup: (synergyName) => ipcRenderer.invoke('sns:lookup', synergyName)
});
