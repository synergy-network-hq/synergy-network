// Renderer process for Synergy Network Utility

// DOM Elements
const navLinks = document.querySelectorAll(".nav-link");
const sections = document.querySelectorAll(".section");
const modalContainer = document.getElementById("modal-container");
const modalTitle = document.getElementById("modal-title");
const modalContent = document.getElementById("modal-content");
const modalClose = document.getElementById("modal-close");

// Dashboard elements
const walletSummary = document.getElementById("wallet-summary");
const tokenSummary = document.getElementById("token-summary");
const domainSummary = document.getElementById("domain-summary");
const currentNetwork = document.getElementById("current-network");

// Wallet elements
const createWalletBtn = document.getElementById("create-wallet-btn");
const importWalletBtn = document.getElementById("import-wallet-btn");
const refreshWalletsBtn = document.getElementById("refresh-wallets-btn");
const walletList = document.getElementById("wallet-list");
const walletDetails = document.getElementById("wallet-details");

// Token elements
const createTokenBtn = document.getElementById("create-token-btn");
const refreshTokensBtn = document.getElementById("refresh-tokens-btn");
const tokenList = document.getElementById("token-list");
const tokenDetails = document.getElementById("token-details");

// Naming elements
const domainSearch = document.getElementById("domain-search");
const checkDomainBtn = document.getElementById("check-domain-btn");
const refreshDomainsBtn = document.getElementById("refresh-domains-btn");
const domainList = document.getElementById("domain-list");
const domainDetails = document.getElementById("domain-details");

// Settings elements
const networkSelect = document.getElementById("network-select");
const themeSelect = document.getElementById("theme-select");
const dataDir = document.getElementById("data-dir");
const browseDataDir = document.getElementById("browse-data-dir");

// Navigation
navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
        e.preventDefault();

        const sectionId = link.getAttribute("data-section");
        navLinks.forEach((l) => l.classList.remove("active"));
        link.classList.add("active");

        sections.forEach((section) => {
            section.classList.remove("active");
            if (section.id === sectionId) {
                section.classList.add("active");
            }
        });
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

// Load initial data
async function loadDashboard() {
    try {
        // Load wallet summary
        const walletResponse = await window.api.walletList();
        if (walletResponse.success) {
            const wallets = walletResponse.wallets;
            walletSummary.innerHTML = `
        <p>Total Wallets: ${wallets.length}</p>
        <p>Default Wallet: ${wallets.find((w) => w.isDefault)?.name || "None"}</p>
      `;
        } else {
            walletSummary.innerHTML = `<p>Error loading wallets: ${walletResponse.error}</p>`;
        }

        // Load token summary
        const tokenResponse = await window.api.tokenList();
        if (tokenResponse.success) {
            const tokens = tokenResponse.tokens;
            tokenSummary.innerHTML = `
        <p>Total Tokens: ${tokens.length}</p>
        <p>Token Types:</p>
        <ul>
          ${countTokenTypes(tokens)}
        </ul>
      `;
        } else {
            tokenSummary.innerHTML = `<p>Error loading tokens: ${tokenResponse.error}</p>`;
        }

        // Load domain summary
        const domainResponse = await window.api.namingList();
        if (domainResponse.success) {
            const domains = domainResponse.domains;
            domainSummary.innerHTML = `
        <p>Total Domains: ${domains.length}</p>
        <p>Active Domains: ${domains.filter((d) => d.status === "registered").length}</p>
      `;
        } else {
            domainSummary.innerHTML = `<p>Error loading domains: ${domainResponse.error}</p>`;
        }
    } catch (error) {
        console.error("Error loading dashboard:", error);
    }
}

function countTokenTypes(tokens) {
    const types = {};
    tokens.forEach((token) => {
        types[token.type] = (types[token.type] || 0) + 1;
    });

    return Object.entries(types)
    .map(([type, count]) => `<li>${type}: ${count}</li>`)
    .join("");
}

// Wallet functions
async function loadWallets() {
    try {
        walletList.innerHTML = "Loading wallets...";
        const response = await window.api.walletList();
        if (response.success) {
            const wallets = response.wallets;
            if (wallets.length === 0) {
                walletList.innerHTML = "<p>No wallets found. Create a new wallet to get started.</p>";
                return;
            }
            walletList.innerHTML = "";
            wallets.forEach((wallet) => {
                const walletItem = document.createElement("div");
                walletItem.classList.add("list-item");
                walletItem.dataset.address = wallet.address;

                let defaultLabel = wallet.isDefault ? ' <span class="badge">Default</span>' : "";

                walletItem.innerHTML = `
          <div class="list-item-title">${wallet.name}${defaultLabel}</div>
          <div class="list-item-subtitle">${formatAddress(wallet.address)}</div>
        `;

                walletItem.addEventListener("click", () => {
                    document.querySelectorAll(".list-item").forEach((item) => item.classList.remove("active"));
                    walletItem.classList.add("active");
                    loadWalletDetails(wallet.address);
                });

                walletList.appendChild(walletItem);
            });

            if (wallets.length > 0) {
                walletList.querySelector(".list-item").classList.add("active");
                loadWalletDetails(wallets[0].address);
            }
        } else {
            walletList.innerHTML = `<p>Error loading wallets: ${response.error}</p>`;
        }
    } catch (error) {
        console.error("Error loading wallets:", error);
        walletList.innerHTML = "<p>Error loading wallets. Please try again.</p>";
    }
}

async function loadWalletDetails(address) {
    try {
        const response = await window.api.walletShow(address);
        if (response.success) {
            const wallet = response.wallet;
            walletDetails.querySelector(".details-content").innerHTML = `
        <div class="details-column">
          <p><strong>Name:</strong> ${wallet.name}</p>
          <p><strong>Address:</strong> ${formatAddress(wallet.address, true)}</p>
          <p><strong>Public Key:</strong> ${formatKey(wallet.publicKey)}</p>
        </div>
        <div class="details-column">
          <div class="action-buttons">
            <button class="action-btn" id="send-btn">Send</button>
            <button class="action-btn" id="receive-btn">Receive</button>
            <button class="action-btn" id="export-btn">Export</button>
          </div>
        </div>
      `;

            document.getElementById("send-btn").addEventListener("click", () => {
                showSendModal(wallet);
            });
            document.getElementById("receive-btn").addEventListener("click", () => {
                showReceiveModal(wallet);
            });
            document.getElementById("export-btn").addEventListener("click", () => {
                showExportModal(wallet);
            });
        } else {
            walletDetails.querySelector(".details-content").innerHTML = `
        <p>Error loading wallet details: ${response.error}</p>
      `;
        }
    } catch (error) {
        console.error("Error loading wallet details:", error);
        walletDetails.querySelector(".details-content").innerHTML = `
      <p>Error loading wallet details. Please try again.</p>
    `;
    }
}

function showCreateWalletModal() {
    const content = `
    <form id="create-wallet-form">
      <div class="form-group">
        <label for="wallet-name">Wallet Name</label>
        <input type="text" id="wallet-name" required placeholder="My Wallet">
      </div>
      <div class="form-group">
        <label for="wallet-password">Password</label>
        <input type="password" id="wallet-password" required placeholder="Enter a secure password">
      </div>
      <div class="form-group">
        <label for="wallet-confirm-password">Confirm Password</label>
        <input type="password" id="wallet-confirm-password" required placeholder="Confirm your password">
      </div>
      <div class="form-actions">
        <button type="button" id="cancel-create-wallet">Cancel</button>
        <button type="submit" class="primary-btn">Create Wallet</button>
      </div>
    </form>
  `;

    showModal("Create New Wallet", content);
    document.getElementById("cancel-create-wallet").addEventListener("click", hideModal);

    document.getElementById("create-wallet-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("wallet-name").value;
        const password = document.getElementById("wallet-password").value;
        const confirmPassword = document.getElementById("wallet-confirm-password").value;
        if (password !== confirmPassword) {
            alert("Passwords do not match");
            return;
        }
        try {
            const response = await window.api.walletCreate(name, password);
            if (response.success) {
                hideModal();
                loadWallets();
                loadDashboard();
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
    const content = `
    <form id="import-wallet-form">
      <div class="form-group">
        <label for="import-wallet-name">Wallet Name</label>
        <input type="text" id="import-wallet-name" required placeholder="My Imported Wallet">
      </div>
      <div class="form-group">
        <label for="import-type">Import Type</label>
        <select id="import-type">
          <option value="private-key">Private Key</option>
          <option value="mnemonic">Mnemonic Phrase</option>
        </select>
      </div>
      <div class="form-group" id="private-key-group">
        <label for="import-private-key">Private Key</label>
        <input type="text" id="import-private-key" placeholder="Enter private key (hex format)">
      </div>
      <div class="form-group hidden" id="mnemonic-group">
        <label for="import-mnemonic">Mnemonic Phrase</label>
        <textarea id="import-mnemonic" placeholder="Enter mnemonic phrase (12 or 24 words)"></textarea>
      </div>
      <div class="form-group">
        <label for="import-password">Password</label>
        <input type="password" id="import-password" required placeholder="Enter a secure password">
      </div>
      <div class="form-group">
        <label for="import-confirm-password">Confirm Password</label>
        <input type="password" id="import-confirm-password" required placeholder="Confirm your password">
      </div>
      <div class="form-actions">
        <button type="button" id="cancel-import-wallet">Cancel</button>
        <button type="submit" class="primary-btn">Import Wallet</button>
      </div>
    </form>
  `;

    showModal("Import Wallet", content);

    const importType = document.getElementById("import-type");
    const privateKeyGroup = document.getElementById("private-key-group");
    const mnemonicGroup = document.getElementById("mnemonic-group");

    importType.addEventListener("change", () => {
        if (importType.value === "private-key") {
            privateKeyGroup.classList.remove("hidden");
            mnemonicGroup.classList.add("hidden");
        } else {
            privateKeyGroup.classList.add("hidden");
            mnemonicGroup.classList.remove("hidden");
        }
    });

    document.getElementById("cancel-import-wallet").addEventListener("click", hideModal);

    document.getElementById("import-wallet-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("import-wallet-name").value;
        const type = document.getElementById("import-type").value;
        const privateKey = document.getElementById("import-private-key").value;
        const mnemonic = document.getElementById("import-mnemonic").value;
        const password = document.getElementById("import-password").value;
        const confirmPassword = document.getElementById("import-confirm-password").value;

        if (password !== confirmPassword) {
            alert("Passwords do not match");
            return;
        }
        try {
            let response;
            if (type === "private-key") {
                response = await window.api.walletImport(name, privateKey, password);
            } else {
                alert("Mnemonic import not implemented yet");
                return;
            }
            if (response.success) {
                hideModal();
                loadWallets();
                loadDashboard();
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

// Token functions
async function loadTokens() {
    try {
        tokenList.innerHTML = "Loading tokens...";
        const response = await window.api.tokenList();
        if (response.success) {
            const tokens = response.tokens;
            if (tokens.length === 0) {
                tokenList.innerHTML = "<p>No tokens found. Create a new token to get started.</p>";
                return;
            }
            tokenList.innerHTML = "";
            tokens.forEach((token) => {
                const tokenItem = document.createElement("div");
                tokenItem.classList.add("list-item");
                tokenItem.dataset.id = token.id;

                tokenItem.innerHTML = `
          <div class="list-item-title">${token.name} (${token.symbol})</div>
          <div class="list-item-subtitle">Supply: ${token.supply} | Type: ${token.type}</div>
        `;

                tokenItem.addEventListener("click", () => {
                    document.querySelectorAll(".list-item").forEach((item) => item.classList.remove("active"));
                    tokenItem.classList.add("active");
                    loadTokenDetails(token.id);
                });

                tokenList.appendChild(tokenItem);
            });

            if (tokens.length > 0) {
                tokenList.querySelector(".list-item").classList.add("active");
                loadTokenDetails(tokens[0].id);
            }
        } else {
            tokenList.innerHTML = `<p>Error loading tokens: ${response.error}</p>`;
        }
    } catch (error) {
        console.error("Error loading tokens:", error);
        tokenList.innerHTML = "<p>Error loading tokens. Please try again.</p>";
    }
}

async function loadTokenDetails(tokenId) {
    tokenDetails.querySelector(".details-content").innerHTML = `
    <p>Loading token details for ${tokenId}...</p>
  `;
    // Real logic can go here
}

function showCreateTokenModal() {
    const content = `
    <form id="create-token-form">
      <div class="form-group">
        <label for="token-name">Token Name</label>
        <input type="text" id="token-name" required placeholder="My Token">
      </div>
      <div class="form-group">
        <label for="token-symbol">Token Symbol</label>
        <input type="text" id="token-symbol" required placeholder="MTK">
      </div>
      <div class="form-group">
        <label for="token-type">Token Type</label>
        <select id="token-type">
          <option value="fungible">Fungible</option>
          <option value="non_fungible">Non-Fungible</option>
          <option value="semi_fungible">Semi-Fungible</option>
        </select>
      </div>
      <div class="form-group">
        <label for="token-initial-supply">Initial Supply</label>
        <input type="number" id="token-initial-supply" placeholder="0">
      </div>
      <div class="form-group">
        <label for="token-max-supply">Maximum Supply (leave empty for unlimited)</label>
        <input type="number" id="token-max-supply" placeholder="Optional">
      </div>
      <div class="form-group">
        <label for="token-decimals">Decimals</label>
        <input type="number" id="token-decimals" value="18">
      </div>
      <div class="form-actions">
        <button type="button" id="cancel-create-token">Cancel</button>
        <button type="submit" class="primary-btn">Create Token</button>
      </div>
    </form>
  `;

    showModal("Create New Token", content);
    document.getElementById("cancel-create-token").addEventListener("click", hideModal);

    document.getElementById("create-token-form").addEventListener("submit", async (e) => {
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
                loadDashboard();
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

// Naming
async function loadDomains() {
    try {
        domainList.innerHTML = "Loading domains...";
        const response = await window.api.namingList();
        if (response.success) {
            const domains = response.domains;
            if (domains.length === 0) {
                domainList.innerHTML = "<p>No domains found. Register a new domain to get started.</p>";
                return;
            }
            domainList.innerHTML = "";
            domains.forEach((domain) => {
                const domainItem = document.createElement("div");
                domainItem.classList.add("list-item");
                domainItem.dataset.name = domain.name;

                const expirationDate = domain.expirationDate
                    ? new Date(domain.expirationDate * 1000).toLocaleDateString()
                    : "N/A";

                domainItem.innerHTML = `
          <div class="list-item-title">${domain.name}</div>
          <div class="list-item-subtitle">Status: ${domain.status} | Expires: ${expirationDate}</div>
        `;

                domainItem.addEventListener("click", () => {
                    document.querySelectorAll(".list-item").forEach((item) => item.classList.remove("active"));
                    domainItem.classList.add("active");
                    loadDomainDetails(domain.name);
                });

                domainList.appendChild(domainItem);
            });

            if (domains.length > 0) {
                domainList.querySelector(".list-item").classList.add("active");
                loadDomainDetails(domains[0].name);
            }
        } else {
            domainList.innerHTML = `<p>Error loading domains: ${response.error}</p>`;
        }
    } catch (error) {
        console.error("Error loading domains:", error);
        domainList.innerHTML = "<p>Error loading domains. Please try again.</p>";
    }
}

async function loadDomainDetails(domainName) {
    domainDetails.querySelector(".details-content").innerHTML = `
    <p>Loading domain details for ${domainName}...</p>
  `;
}

async function checkDomainAvailability() {
    const domainName = domainSearch.value.trim();
    if (!domainName) {
        alert("Please enter a domain name");
        return;
    }
    try {
        const response = await window.api.namingCheck(domainName);
        if (response.success) {
            if (response.available) {
                showRegisterDomainModal(domainName);
            } else {
                alert(`Domain ${domainName} is not available: ${response.reason}`);
            }
        } else {
            alert(`Error checking domain: ${response.error}`);
        }
    } catch (error) {
        console.error("Error checking domain:", error);
        alert("Error checking domain. Please try again.");
    }
}

function showRegisterDomainModal(domainName) {
    const content = `
    <form id="register-domain-form">
      <div class="form-group">
        <label for="domain-name">Domain Name</label>
        <input type="text" id="domain-name" value="${domainName}" readonly>
      </div>
      <div class="form-group">
        <label for="registration-period">Registration Period (years)</label>
        <select id="registration-period">
          <option value="1">1 year</option>
          <option value="2">2 years</option>
          <option value="5">5 years</option>
          <option value="10">10 years</option>
        </select>
      </div>
      <div class="form-group">
        <label for="domain-password">Wallet Password</label>
        <input type="password" id="domain-password" required placeholder="Enter your wallet password">
      </div>
      <div class="form-actions">
        <button type="button" id="cancel-register-domain">Cancel</button>
        <button type="submit" class="primary-btn">Register Domain</button>
      </div>
    </form>
  `;

    showModal(`Register Domain: ${domainName}`, content);
    document.getElementById("cancel-register-domain").addEventListener("click", hideModal);

    document.getElementById("register-domain-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("domain-name").value;
        const period = document.getElementById("registration-period").value;
        const password = document.getElementById("domain-password").value;

        // Convert years to seconds
        const registrationPeriod = period * 365 * 24 * 60 * 60;
        try {
            const response = await window.api.namingRegister(name, registrationPeriod, password);
            if (response.success) {
                hideModal();
                loadDomains();
                loadDashboard();
                alert(`Domain "${name}" registered successfully!`);
            } else {
                alert(`Error registering domain: ${response.error}`);
            }
        } catch (error) {
            console.error("Error registering domain:", error);
            alert("Error registering domain. Please try again.");
        }
    });
}

// Utility
function formatAddress(address, full = false) {
    if (!address) return "";
    if (full) {
        return address;
    }
    return `${address.substring(0, 8)}...${address.substring(address.length - 8)}`;
}

function formatKey(key, full = false) {
    if (!key) return "";
    if (full) {
        return key;
    }
    return `${key.substring(0, 16)}...${key.substring(key.length - 16)}`;
}

// Event listeners
createWalletBtn.addEventListener("click", showCreateWalletModal);
importWalletBtn.addEventListener("click", showImportWalletModal);
refreshWalletsBtn.addEventListener("click", loadWallets);

createTokenBtn.addEventListener("click", showCreateTokenModal);
refreshTokensBtn.addEventListener("click", loadTokens);

checkDomainBtn.addEventListener("click", checkDomainAvailability);
refreshDomainsBtn.addEventListener("click", loadDomains);

themeSelect.addEventListener("change", (e) => {
    const theme = e.target.value;
    if (theme === "light") {
        document.body.classList.add("light-theme");
    } else {
        document.body.classList.remove("light-theme");
    }
});

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
    loadWallets();
    loadTokens();
    loadDomains();
});

// ============= UMA - NEW ============= //
// Example: Button or function to generate synergy PQ address
// You can create a new button in your UI or link it somewhere else.
async function generateUMAAddress() {
    try {
        const password = prompt("Enter an optional password to protect synergy seed:", "");
        const result = await window.api.umaGenerate(password || "");
        if (result.success) {
            alert(`UMA synergy address created: ${result.synergy_address}\nSaved in file: ${result.file}`);
        } else {
            alert(`Error generating UMA address: ${result.error}`);
        }
    } catch (error) {
        alert(`Exception: ${error}`);
    }
}

// Example: Derive chain address
async function deriveChainAddress() {
    const chainName = prompt("Enter chain name, e.g. ethereum, solana, tron", "ethereum");
    if (!chainName) return;
    try {
        const result = await window.api.umaDerive(chainName);
        if (result.success) {
            alert(`Derived address for ${result.chain_name}: ${result.chain_address}`);
        } else {
            alert(`Error deriving chain address: ${result.error}`);
        }
    } catch (error) {
        alert(`Exception: ${error}`);
    }
}

// Example: synergy name lookup
async function synergyNameLookup() {
    const synergyName = prompt("Enter synergy name to lookup, e.g. bob.syn", "bob.syn");
    if (!synergyName) return;
    try {
        const result = await window.api.snsLookup(synergyName);
        if (result.success) {
            alert(`Name: ${synergyName}\nAddress: ${result.synergy_addr}`);
        } else {
            alert(`Lookup error: ${result.error}`);
        }
    } catch (error) {
        alert(`Exception: ${error}`);
    }
}

// You might attach these to new buttons or an advanced tab in your GUI
// for demonstration. For example:
const maybeAdvancedSection = document.getElementById("dashboard");
if (maybeAdvancedSection) {
    const newBtnContainer = document.createElement("div");
    newBtnContainer.innerHTML = `
    <h3>Universal Meta Address (UMA) Tests</h3>
    <button id="gen-uma-btn">Generate UMA Address</button>
    <button id="derive-uma-btn">Derive Chain Address</button>
    <button id="lookup-sns-btn">Lookup Synergy Name</button>
  `;
    maybeAdvancedSection.appendChild(newBtnContainer);

    document.getElementById("gen-uma-btn").addEventListener("click", generateUMAAddress);
    document.getElementById("derive-uma-btn").addEventListener("click", deriveChainAddress);
    document.getElementById("lookup-sns-btn").addEventListener("click", synergyNameLookup);
}

// At the bottom or anywhere you'd like:

async function generateUMAAddress() {
  const password = prompt("Enter a password to encrypt synergy PQ private key (optional)", "");
  try {
    const result = await window.api.umaGenerate(password);
    if (result.success) {
      alert(`UMA synergy address created: ${result.synergy_address}\nSaved in: ${result.file}`);
    } else {
      alert("UMA generation error: " + result.error);
    }
  } catch (err) {
    alert("UMA generation exception: " + err);
  }
}

async function deriveChainAddress() {
  const chainName = prompt("Enter chain name (ethereum, solana, tron...)", "ethereum");
  if (!chainName) return;
  const password = prompt("If synergy seed is encrypted, enter password. Otherwise, leave blank", "");
  try {
    const result = await window.api.umaDerive(chainName, password);
    if (result.success) {
      alert(`Chain: ${result.chain_name}\nAddress: ${result.chain_address}`);
    } else {
      alert("Derive error: " + result.error);
    }
  } catch (err) {
    alert("Derive exception: " + err);
  }
}

async function synergyNameLookup() {
  const synergyName = prompt("Enter synergy name (myname.syn)");
  if (!synergyName) return;
  try {
    const res = await window.api.snsLookup(synergyName);
    if (res.success) {
      alert(`Name: ${synergyName}\nAddress: ${res.synergy_addr}`);
    } else {
      alert("Lookup error: " + res.error);
    }
  } catch (err) {
    alert("Lookup exception: " + err);
  }
}
