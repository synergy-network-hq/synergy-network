// Renderer process for Synergy Network Utility

// DOM Elements
const networkStatusText = document.getElementById("network-status-text");
const statusIndicator = document.querySelector(".status-indicator");
const currentNetwork = document.getElementById("current-network");
const navLinks = document.querySelectorAll(".nav-link");
const sections = document.querySelectorAll(".section");
const modalContainer = document.getElementById("modal-container");
const modalTitle = document.getElementById("modal-title");
const modalContent = document.getElementById("modal-content");
const modalClose = document.getElementById("modal-close");
const themeSelect = document.getElementById("theme-select");
const logo = document.getElementById("logo");
const logoLight = document.getElementById("logo-light");

// Dashboard elements
const walletSummary = document.getElementById("wallet-summary");
const tokenSummary = document.getElementById("token-summary");
const domainSummary = document.getElementById("domain-summary");


// Section action buttons
const createWalletAction = document.getElementById("create-wallet-action");
const importWalletAction = document.getElementById("import-wallet-action");
const refreshWalletsBtn = document.getElementById("refresh-wallets-btn");
const walletList = document.getElementById("wallet-list");
const walletDetails = document.getElementById("wallet-details");

const createTokenAction = document.getElementById("create-token-action");
const refreshTokensBtn = document.getElementById("refresh-tokens-btn");
const tokenList = document.getElementById("token-list");
const tokenDetails = document.getElementById("token-details");

const domainSearch = document.getElementById("domain-search");
const checkDomainBtn = document.getElementById("check-domain-btn");
const refreshDomainsBtn = document.getElementById("refresh-domains-btn");
const domainList = document.getElementById("domain-list");
const domainDetails = document.getElementById("domain-details");

const generateUmaAction = document.getElementById("generate-uma-action");
const deriveAddressAction = document.getElementById("derive-address-action");
const refreshUmaBtn = document.getElementById("refresh-uma-btn");
const umaList = document.getElementById("uma-list");
const umaDetails = document.getElementById("uma-details");

// Settings elements
const networkSelect = document.getElementById("network-select");
const dataDir = document.getElementById("data-dir");
const browseDataDir = document.getElementById("browse-data-dir");
const saveNetworkSettings = document.getElementById("save-network-settings");
const saveAppearanceSettings = document.getElementById("save-appearance-settings");
const saveAdvancedSettings = document.getElementById("save-advanced-settings");
const disconnectWallet = document.getElementById("disconnect-wallet");
const signOut = document.getElementById("sign-out");

// Theme handling
function setTheme(theme) {
  if (theme === 'light') {
    document.body.classList.add('light-theme');
    logo?.classList.add('hidden');
    logoLight?.classList.remove('hidden');
  } else {
    document.body.classList.remove('light-theme');
    logo?.classList.remove('hidden');
    logoLight?.classList.add('hidden');
  }
  localStorage.setItem('theme', theme);
}

// Initialize theme
const savedTheme = localStorage.getItem('theme') || 'dark';
if (themeSelect) {
  themeSelect.value = savedTheme;
  setTheme(savedTheme);
}


themeSelect?.addEventListener('change', (e) => {
  setTheme(e.target.value);
});

// Navigation
function navigateTo(sectionId) {
  navLinks.forEach((l) => {
    if (l.getAttribute("data-section") === sectionId) {
      l.classList.add("active");
    } else {
      l.classList.remove("active");
    }
  });

  sections.forEach((section) => {
    if (section.id === sectionId) {
      section.classList.add("active");
    } else {
      section.classList.remove("active");
    }
  });
}

navLinks.forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    const sectionId = link.getAttribute("data-section");
    navigateTo(sectionId);
  });
});

// Dashboard navigation button handlers
document.getElementById("nav-wallet-btn")?.addEventListener("click", () => navigateTo("wallet"));
document.getElementById("nav-tokens-btn")?.addEventListener("click", () => navigateTo("tokens"));
document.getElementById("nav-naming-btn")?.addEventListener("click", () => navigateTo("naming"));
document.getElementById("nav-uma-btn")?.addEventListener("click", () => navigateTo("uma"));
document.getElementById("nav-settings-btn")?.addEventListener("click", () => navigateTo("settings"));

// Section action button handlers
createWalletAction?.addEventListener("click", showCreateWalletModal);
importWalletAction?.addEventListener("click", showImportWalletModal);
refreshWalletsBtn?.addEventListener("click", loadWallets);

createTokenAction?.addEventListener("click", showCreateTokenModal);
refreshTokensBtn?.addEventListener("click", loadTokens);

checkDomainBtn?.addEventListener("click", checkDomain);
refreshDomainsBtn?.addEventListener("click", loadDomains);

generateUmaAction?.addEventListener("click", showGenerateUmaModal);
deriveAddressAction?.addEventListener("click", showDeriveAddressModal);
refreshUmaBtn?.addEventListener("click", loadUmas);

// Settings button handlers
saveNetworkSettings?.addEventListener("click", saveNetworkSettingsHandler);
saveAppearanceSettings?.addEventListener("click", saveAppearanceSettingsHandler);
saveAdvancedSettings?.addEventListener("click", saveAdvancedSettingsHandler);
disconnectWallet?.addEventListener("click", disconnectWalletHandler);
signOut?.addEventListener("click", signOutHandler);

// Home button handlers
document.querySelectorAll(".home-btn").forEach(button => {
  button.addEventListener("click", () => {
    navigateTo("dashboard");
  });
});


// Modal functions
function showModal(title, content) {
  modalTitle.textContent = title;
  modalContent.innerHTML = content;
  modalContainer.classList.remove("hidden");
}

function hideModal() {
  modalContainer.classList.add("hidden");
}

modalClose.addEventListener("click", hideModal);
modalContainer.addEventListener("click", (e) => {
  if (e.target === modalContainer) {
    hideModal();
  }
});

// Helper functions
function formatAddress(address, full = false) {
  if (!address) return "N/A";
  if (full) return address;
  return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
}

function formatKey(key, full = false) {
  if (!key) return "N/A";
  if (full) return key;
  return `${key.substring(0, 10)}...${key.substring(key.length - 4)}`;
}

// Modal templates
function showCreateWalletModal() {
  showModal("Create New Wallet", `
    <form id="create-wallet-form">
      <div class="form-group">
        <label for="wallet-name">Wallet Name</label>
        <input type="text" id="wallet-name" placeholder="My Wallet" required>
      </div>
      <div class="form-group">
        <label for="wallet-password">Password</label>
        <input type="password" id="wallet-password" placeholder="Secure password" required>
      </div>
      <div class="form-group">
        <label for="wallet-confirm-password">Confirm Password</label>
        <input type="password" id="wallet-confirm-password" placeholder="Confirm password" required>
      </div>
      <div class="form-group">
        <button type="submit" class="primary-btn">Create Wallet</button>
      </div>
    </form>
  `);

  document.getElementById("create-wallet-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("wallet-name").value;
    const password = document.getElementById("wallet-password").value;
    const confirmPassword = document.getElementById("wallet-confirm-password").value;

    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    try {
      const response = await window.api.walletCreate(name, password);
      if (response.success) {
        hideModal();
        loadWallets();
        alert(`Wallet "${name}" created successfully!`);
      } else {
        alert(`Error creating wallet: ${response.error}`);
      }
    } catch (error) {
      console.error("Error creating wallet:", error);
      alert("Error creating wallet. Please try again.");
    }
  });
}

function showImportWalletModal() {
  showModal("Import Wallet", `
    <form id="import-wallet-form">
      <div class="form-group">
        <label for="import-wallet-name">Wallet Name</label>
        <input type="text" id="import-wallet-name" placeholder="My Imported Wallet" required>
      </div>
      <div class="form-group">
        <label for="import-private-key">Private Key</label>
        <input type="text" id="import-private-key" placeholder="Enter private key" required>
      </div>
      <div class="form-group">
        <label for="import-wallet-password">Password</label>
        <input type="password" id="import-wallet-password" placeholder="Secure password" required>
      </div>
      <div class="form-group">
        <button type="submit" class="primary-btn">Import Wallet</button>
      </div>
    </form>
  `);

  document.getElementById("import-wallet-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("import-wallet-name").value;
    const privateKey = document.getElementById("import-private-key").value;
    const password = document.getElementById("import-wallet-password").value;

    try {
      const response = await window.api.walletImport(name, privateKey, password);
      if (response.success) {
        hideModal();
        loadWallets();
        alert(`Wallet "${name}" imported successfully!`);
      } else {
        alert(`Error importing wallet: ${response.error}`);
      }
    } catch (error) {
      console.error("Error importing wallet:", error);
      alert("Error importing wallet. Please try again.");
    }
  });
}

function showCreateTokenModal() {
  showModal("Create New Token", `
    <form id="create-token-form">
      <div class="form-group">
        <label for="token-name">Token Name</label>
        <input type="text" id="token-name" placeholder="My Token" required>
      </div>
      <div class="form-group">
        <label for="token-symbol">Token Symbol</label>
        <input type="text" id="token-symbol" placeholder="MTK" required maxlength="5">
      </div>
      <div class="form-group">
        <label for="token-type">Token Type</label>
        <select id="token-type" required>
          <option value="fungible">Fungible</option>
          <option value="non-fungible">Non-Fungible</option>
        </select>
      </div>
      <div class="form-group">
        <label for="token-initial-supply">Initial Supply</label>
        <input type="number" id="token-initial-supply" placeholder="1000" required min="0">
      </div>
      <div class="form-group">
        <label for="token-max-supply">Maximum Supply</label>
        <input type="number" id="token-max-supply" placeholder="1000000" required min="0">
      </div>
      <div class="form-group">
        <label for="token-decimals">Decimals</label>
        <input type="number" id="token-decimals" placeholder="18" required min="0" max="18">
      </div>
      <div class="form-group">
        <button type="submit" class="primary-btn">Create Token</button>
      </div>
    </form>
  `);

  document.getElementById("create-token-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("token-name").value;
    const symbol = document.getElementById("token-symbol").value;
    const tokenType = document.getElementById("token-type").value;
    const initialSupply = document.getElementById("token-initial-supply").value;
    const maxSupply = document.getElementById("token-max-supply").value;
    const decimals = document.getElementById("token-decimals").value;

    try {
      const response = await window.api.tokenCreate(name, symbol, tokenType, initialSupply, maxSupply, decimals);
      if (response.success) {
        hideModal();
        loadTokens();
        alert(`Token "${name}" created successfully!`);
      } else {
        alert(`Error creating token: ${response.error}`);
      }
    } catch (error) {
      console.error("Error creating token:", error);
      alert("Error creating token. Please try again.");
    }
  });
}

function showRegisterNameModal() {
  showModal("Register Domain Name", `
    <form id="register-name-form">
      <div class="form-group">
        <label for="domain-name">Domain Name</label>
        <div class="input-with-suffix">
          <input type="text" id="domain-name" placeholder="mydomain" required>
          <span class="input-suffix">.syn</span>
        </div>
      </div>
      <div class="form-group">
        <label for="registration-period">Registration Period</label>
        <select id="registration-period" required>
          <option value="1">1 Year</option>
          <option value="2">2 Years</option>
          <option value="5">5 Years</option>
          <option value="10">10 Years</option>
        </select>
      </div>
      <div class="form-group">
        <label for="registration-password">Password</label>
        <input type="password" id="registration-password" placeholder="Wallet password" required>
      </div>
      <div class="form-group">
        <button type="submit" class="primary-btn">Register Domain</button>
      </div>
    </form>
  `);

  document.getElementById("register-name-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const domainName = document.getElementById("domain-name").value + ".syn";
    const registrationPeriod = document.getElementById("registration-period").value;
    const password = document.getElementById("registration-password").value;

    try {
      const response = await window.api.namingRegister(domainName, registrationPeriod, password);
      if (response.success) {
        hideModal();
        loadDomains();
        alert(`Domain "${domainName}" registered successfully!`);
      } else {
        alert(`Error registering domain: ${response.error}`);
      }
    } catch (error) {
      console.error("Error registering domain:", error);
      alert("Error registering domain. Please try again.");
    }
  });
}

function showGenerateUmaModal() {
  showModal("Generate Universal Meta Address", `
    <form id="generate-uma-form">
      <div class="form-group">
        <label for="uma-password">Password (Optional)</label>
        <input type="password" id="uma-password" placeholder="Secure password">
      </div>
      <div class="form-group">
        <button type="submit" class="primary-btn">Generate UMA</button>
      </div>
    </form>
  `);

  document.getElementById("generate-uma-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const password = document.getElementById("uma-password").value || "";

    try {
      const response = await window.api.umaGenerate(password);
      if (response.success) {
        hideModal();
        loadUmas();
        showModal("UMA Generated Successfully", `
          <div class="success-message">
            <p>Your Universal Meta Address has been generated and saved.</p>
            <p><strong>Synergy Address:</strong> ${response.synergy_address}</p>
            <p><strong>Saved to:</strong> ${response.file}</p>
            <p class="warning">Keep your password safe! It's required to access your UMA.</p>
          </div>
        `);
      } else {
        alert(`Error generating UMA: ${response.error}`);
      }
    } catch (error) {
      console.error("Error generating UMA:", error);
      alert("Error generating UMA. Please try again.");
    }
  });
}

function showDeriveAddressModal() {
  showModal("Derive Chain Address", `
    <form id="derive-address-form">
      <div class="form-group">
        <label for="chain-name">Blockchain</label>
        <select id="chain-name" required>
          <option value="ethereum">Ethereum</option>
          <option value="bitcoin">Bitcoin</option>
          <option value="solana">Solana</option>
          <option value="polkadot">Polkadot</option>
        </select>
      </div>
      <div class="form-group">
        <label for="derive-password">Password</label>
        <input type="password" id="derive-password" placeholder="UMA password" required>
      </div>
      <div class="form-group">
        <button type="submit" class="primary-btn">Derive Address</button>
      </div>
    </form>
  `);

  document.getElementById("derive-address-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const chainName = document.getElementById("chain-name").value;
    const password = document.getElementById("derive-password").value;

    try {
      const response = await window.api.umaDerive(chainName, password);
      if (response.success) {
        hideModal();
        showModal("Address Derived Successfully", `
          <div class="success-message">
            <p><strong>Chain:</strong> ${chainName}</p>
            <p><strong>Derived Address:</strong> ${response.address}</p>
          </div>
        `);
      } else {
        alert(`Error deriving address: ${response.error}`);
      }
    } catch (error) {
      console.error("Error deriving address:", error);
      alert("Error deriving address. Please try again.");
    }
  });
}

function showVerifyUmaModal() {
  showModal("Verify Universal Meta Address", `
    <form id="verify-uma-form">
      <div class="form-group">
        <label for="verify-address">Synergy Address</label>
        <input type="text" id="verify-address" placeholder="Enter Synergy address" required>
      </div>
      <div class="form-group">
        <label for="verify-signature">Signature</label>
        <input type="text" id="verify-signature" placeholder="Enter signature" required>
      </div>
      <div class="form-group">
        <label for="verify-message">Message</label>
        <textarea id="verify-message" placeholder="Enter message" required></textarea>
      </div>
      <div class="form-group">
        <button type="submit" class="primary-btn">Verify</button>
      </div>
    </form>
  `);

  document.getElementById("verify-uma-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    // Verification logic would go here
    alert("Verification feature coming soon!");
    hideModal();
  });
}

// Load Wallet handler
async function loadWallets() {
  try {
    const result = await window.api.walletList();
    if (result.success && Array.isArray(result.wallets)) {
      if (walletList) {
        walletList.innerHTML = ""; // Clear previous
        result.wallets.forEach((w) => {
          const item = document.createElement("div");
          item.classList.add("list-item");
          item.textContent = `${w.name} (${w.address})`;
          walletList.appendChild(item);
        });
      }

      if (walletSummary) {
        walletSummary.textContent = `${result.wallets.length} wallet(s) loaded`;
      }
    } else {
      if (walletList) {
        walletList.innerHTML = "<p>Error loading wallets</p>";
      }
    }
  } catch (error) {
    console.error("Error loading wallets:", error);
    if (walletList) {
      walletList.innerHTML = "<p>Error loading wallets</p>";
    }
  }
}


// Load Tokens handler
async function loadTokens() {
  try {
    const result = await window.api.tokenList();
    if (result.success && Array.isArray(result.tokens)) {
      if (tokenList) {
        tokenList.innerHTML = ""; // Clear previous
        result.tokens.forEach((t) => {
          const item = document.createElement("div");
          item.classList.add("list-item");
          item.textContent = `${t.name} (${t.symbol})`;
          tokenList.appendChild(item);
        });
      }
    } else {
      if (tokenList) {
        tokenList.innerHTML = "<p>Error loading tokens</p>";
      }
    }
  } catch (error) {
    console.error("Error loading tokens:", error);
    if (tokenList) {
      tokenList.innerHTML = "<p>Error loading tokens</p>";
    }
  }
}

// Load Domains handler
async function loadDomains() {
  try {
    const result = await window.api.namingList();
    if (result.success && Array.isArray(result.domains)) {
      if (domainList) {
        domainList.innerHTML = ""; // Clear previous
        result.domains.forEach((d) => {
          const item = document.createElement("div");
          item.classList.add("list-item");
          item.textContent = `${d.name}`;
          domainList.appendChild(item);
        });
      }
    } else {
      if (domainList) {
        domainList.innerHTML = "<p>Error loading domains</p>";
      }
    }
  } catch (error) {
    console.error("Error loading domains:", error);
    if (domainList) {
      domainList.innerHTML = "<p>Error loading domains</p>";
    }
  }
}

// Check Domain handler
async function checkDomain() {
  const domain = domainSearch.value;
  if (!domain) {
    alert("Please enter a domain name to check.");
    return;
  }

  try {
    const result = await window.api.namingCheck(domain + ".syn");
    if (result.success) {
      alert(`Domain "${domain}.syn" is ${result.available ? 'available' : 'not available'}.`);
    } else {
      alert(`Error checking domain: ${result.error}`);
    }
  } catch (error) {
    console.error("Error checking domain:", error);
    alert("Error checking domain. Please try again.");
  }
}


// Load UMAs handler
async function loadUmas() {
  try {
    const result = await window.api.umaList();
    if (result.success && Array.isArray(result.umas)) {
      if (umaList) {
        umaList.innerHTML = ""; // Clear previous
        result.umas.forEach((u) => {
          const item = document.createElement("div");
          item.classList.add("list-item");
          item.textContent = `${u.synergy_address}`;
          umaList.appendChild(item);
        });
      }
    } else {
      if (umaList) {
        umaList.innerHTML = "<p>Error loading UMAs</p>";
      }
    }
  } catch (error) {
    console.error("Error loading UMAs:", error);
    if (umaList) {
      umaList.innerHTML = "<p>Error loading UMAs</p>";
    }
  }
}


// Settings handlers
function saveNetworkSettingsHandler() {
  const network = networkSelect?.value;
  if (network) {
    localStorage.setItem('network', network);
    if (currentNetwork) {
      currentNetwork.textContent = network.toUpperCase();
    }
    alert(`Network settings saved! Active network: ${network}`);
  } else {
    alert("Network select element not found.");
  }
}

function saveAppearanceSettingsHandler() {
  const theme = themeSelect?.value;
  if (theme) {
    setTheme(theme);
    alert('Appearance settings saved!');
  } else {
    alert("Theme select element not found.");
  }
}

function saveAdvancedSettingsHandler() {
  const directory = dataDir?.value;
  if (directory) {
    localStorage.setItem('dataDir', directory);
    alert('Advanced settings saved!');
  } else {
    alert("Data directory element not found.");
  }
}

function disconnectWalletHandler() {
  // Wallet disconnection logic would go here
  alert('Wallet disconnected successfully!');
}

function signOutHandler() {
  // Sign out logic would go here
  alert('Signed out successfully!');
}

async function checkNetworkStatus() {
  const current = localStorage.getItem("network") || "testnet";

  // Dynamic RPC endpoints per network
  const rpcUrls = {
    testnet: "http://localhost:8545",
    // mainnet: "https://rpc.synergynetwork.org", // ← Enable when mainnet launches
    // devnet: "http://localhost:8546", // Optional if needed later
  };

  const rpcUrl = rpcUrls[current];

  if (!rpcUrl) {
    console.warn(`No RPC URL defined for network: ${current}`);
    setNetworkStatus("offline");
    return;
  }

  try {
    const response = await fetch(rpcUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "synergy_status", // ✅ Replaced method name here
        params: [],
        id: 1,
      }),
    });

    const data = await response.json();
    console.log("✅ Network RPC response:", data);

    if (data && data.result === "ok") {
      setNetworkStatus("online");
    } else {
      setNetworkStatus("offline");
    }
  } catch (err) {
    console.error("❌ Network status check failed:", err);
    setNetworkStatus("offline");
  }
}

function setNetworkStatus(status) {
  if (status === "online") {
    if (networkStatusText && statusIndicator) {
      networkStatusText.textContent = "ONLINE";
      statusIndicator.classList.remove("offline", "connecting");
      statusIndicator.classList.add("online");
    }
  } else if (status === "connecting") {
    if (networkStatusText && statusIndicator) {
      networkStatusText.textContent = "CONNECTING...";
      statusIndicator.classList.remove("online", "offline");
      statusIndicator.classList.add("connecting");
    }
  } else {
    if (networkStatusText && statusIndicator) {
      networkStatusText.textContent = "OFFLINE";
      statusIndicator.classList.remove("online", "connecting");
      statusIndicator.classList.add("offline");
    }
  }
}

// Load data functions (Simplified for now)
async function loadDashboard() {
  console.log("Loading dashboard...");
  // Implement dashboard data loading if needed
}


// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();

  // Set network from localStorage or default to testnet
  const savedNetwork = localStorage.getItem('network') || 'testnet';
  if (networkSelect) {
    networkSelect.value = savedNetwork;
  }
  if (currentNetwork) {
    currentNetwork.textContent = savedNetwork.toUpperCase();
  }


  // Set data directory from localStorage or default
  const savedDataDir = localStorage.getItem('dataDir') || '~/.synergy';
  if (dataDir) {
    dataDir.value = savedDataDir;
  }


  // Start network status checking
  setNetworkStatus("connecting");
  checkNetworkStatus();
  setInterval(checkNetworkStatus, 5000); // Poll every 5s
});

// Floating Network Status Animation - Single Flip
function refreshNetworkStatus(element) {
  if (element.classList.contains("flipping")) return; // prevent multi-trigger

  const originalContent = element.innerHTML;

  element.classList.add("flipping");
  element.innerHTML = `
    <div class="status-content">
      <div style="font-size: 14px;">Refreshing Network Connection...</div>
    </div>
  `;

  setTimeout(() => {
    element.innerHTML = `
      <div class="status-content">
        <div class="status-dot"></div>
        <div>
          <div>Network: TESTNET</div>
          <div>Status: Online</div>
        </div>
      </div>
    `; // Note: This hardcoded content should ideally be dynamic based on actual status
    element.classList.remove("flipping");
  }, 2000);
}
