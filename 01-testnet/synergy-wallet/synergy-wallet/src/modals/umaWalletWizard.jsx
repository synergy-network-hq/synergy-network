import React, { useState } from "react";
import Modal from "./Modal";
import * as bip39 from "bip39";
import { generateDeterministicDilithiumKeypair } from "../utils/pqc";
import {
  generateBTCAddressFromMnemonic,
  generateETHWalletFromMnemonic,
  generateSOLWalletFromMnemonic,
} from "../utils/umaAddresses";
import { pubkeyToSynergyAddress } from "../utils/synergyAddress";
import { encryptSecret } from "../utils/crypto";
import { toHex } from "../utils/hexUtils";
import { useNavigate } from "react-router-dom";

const SEED_WORD_OPTIONS = [12, 24];
const DEFAULT_VERIFY_WORDS = 3;

const Steps = {
  MODE: 0,
  CREATE_CHOOSE_LENGTH: 1,
  CREATE_REVEAL: 2,
  CREATE_VERIFY: 3,
  IMPORT_CHOOSE_LENGTH: 4,
  IMPORT_ENTRY: 5,
  PASSWORD: 6,
  SNS: 7,
  COMPLETE: 8,
};

export default function UmaWalletWizard({ isOpen, onClose, onWalletCreated }) {
  const [step, setStep] = useState(Steps.MODE);
  const [mode, setMode] = useState("create");
  const [seedLength, setSeedLength] = useState(12);
  const [seedPhrase, setSeedPhrase] = useState([]);
  const [enteredSeedPhrase, setEnteredSeedPhrase] = useState(
    Array(12).fill("")
  );
  const [verifyIndexes, setVerifyIndexes] = useState([]);
  const [verifyInputs, setVerifyInputs] = useState([]);
  const [error, setError] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [sns, setSNS] = useState("");
  const [snsSkip, setSNSSkip] = useState(false);
  const [processing, setProcessing] = useState(false);

  const navigate = useNavigate();

  const totalSteps =
    mode === "create"
      ? [
        Steps.MODE,
        Steps.CREATE_CHOOSE_LENGTH,
        Steps.CREATE_REVEAL,
        Steps.CREATE_VERIFY,
        Steps.PASSWORD,
        Steps.SNS,
        Steps.COMPLETE,
      ]
      : [
        Steps.MODE,
        Steps.IMPORT_CHOOSE_LENGTH,
        Steps.IMPORT_ENTRY,
        Steps.PASSWORD,
        Steps.SNS,
        Steps.COMPLETE,
      ];
  const progress = totalSteps.indexOf(step) / (totalSteps.length - 1);

  function randomUniqueIndexes(n, max) {
    const set = new Set();
    while (set.size < n) set.add(Math.floor(Math.random() * max));
    return Array.from(set).sort((a, b) => a - b);
  }

  function handleModeSelect(m) {
    setMode(m);
    setStep(
      m === "create" ? Steps.CREATE_CHOOSE_LENGTH : Steps.IMPORT_CHOOSE_LENGTH
    );
    setError("");
  }

  function handleSeedLengthSelect(len) {
    setSeedLength(len);
    setSeedPhrase([]);
    setEnteredSeedPhrase(Array(len).fill(""));
    setError("");
    if (mode === "create") setStep(Steps.CREATE_REVEAL);
    else setStep(Steps.IMPORT_ENTRY);
  }

  function handleGenerateSeed() {
    const entropyBits = seedLength === 12 ? 128 : 256;
    const phrase = bip39.generateMnemonic(entropyBits);
    setSeedPhrase(phrase.split(" "));
    setStep(Steps.CREATE_REVEAL);
    setError("");
  }

  function handleRevealContinue() {
    setVerifyIndexes(randomUniqueIndexes(DEFAULT_VERIFY_WORDS, seedLength));
    setVerifyInputs(Array(DEFAULT_VERIFY_WORDS).fill(""));
    setStep(Steps.CREATE_VERIFY);
    setError("");
  }

  function handleVerifyContinue() {
    let correct = true;
    verifyIndexes.forEach((idx, i) => {
      if (
        (mode === "create" &&
          verifyInputs[i].trim().toLowerCase() !== seedPhrase[idx]) ||
        (mode === "import" &&
          verifyInputs[i].trim().toLowerCase() !==
          enteredSeedPhrase[idx].trim().toLowerCase())
      ) {
        correct = false;
      }
    });
    if (!correct) {
      setError("One or more words do not match. Please try again.");
      return;
    }
    setError("");
    setStep(Steps.PASSWORD);
  }

  function handleValidateImport() {
    const phrase = enteredSeedPhrase.join(" ").toLowerCase();
    if (!bip39.validateMnemonic(phrase)) {
      setError("Invalid BIP39 seed phrase.");
      return;
    }
    setSeedPhrase(enteredSeedPhrase.map((w) => w.trim().toLowerCase()));
    setVerifyIndexes(randomUniqueIndexes(DEFAULT_VERIFY_WORDS, seedLength));
    setVerifyInputs(Array(DEFAULT_VERIFY_WORDS).fill(""));
    setError("");
    setStep(Steps.CREATE_VERIFY);
  }

  function handlePasswordContinue() {
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== password2) {
      setError("Passwords do not match.");
      return;
    }
    setError("");
    setStep(Steps.SNS);
  }

  async function handleSNSContinue() {
    setError("");
    setProcessing(true);
    try {
      const seedBytes = bip39.mnemonicToSeedSync(seedPhrase.join(" ")); // 64-byte seed
      const { publicKey, privateKey } =
        await generateDeterministicDilithiumKeypair(new Uint8Array(seedBytes));
      const synergyAddress = await pubkeyToSynergyAddress(publicKey);
      const btc = generateBTCAddressFromMnemonic(seedPhrase.join(" "));
      const eth = generateETHWalletFromMnemonic(seedPhrase.join(" "));
      const sol = generateSOLWalletFromMnemonic(seedPhrase.join(" "));
      const mnemonicEnc = await encryptSecret(password, seedPhrase.join(" "));
      const pqcPrivateKeyEnc = await encryptSecret(password, toHex(privateKey));
      const pqcPublicKeyHex = toHex(publicKey);
      const walletObj = {
        id: "wlt_" + Date.now(),
        label: sns && !snsSkip ? `${sns}.syn` : "Synergy Wallet",
        synergyAddress,
        pqcPublicKey: pqcPublicKeyHex,
        pqcPrivateKeyEnc,
        mnemonicEnc,
        bitcoinAddress: btc.address,
        ethereumAddress: eth.address,
        solanaAddress: sol.address,
        networks: ["synergy", "bitcoin", "ethereum", "solana"],
        createdAt: new Date().toISOString(),
        backupStatus: "not_backed_up",
        sns: sns && !snsSkip ? sns : null,
      };
      if (onWalletCreated) onWalletCreated(walletObj);
      setStep(Steps.COMPLETE);
    } catch (err) {
      setError("Wallet creation failed: " + (err.message || err));
    }
    setProcessing(false);
  }

  function handleComplete() {
    setError("");
    if (onClose) onClose();
    navigate("/dashboard");
  }

  function renderProgressBar() {
    return (
      <div style={{ width: "100%", margin: "0 0 16px 0" }}>
        <div
          style={{
            height: 8,
            background: "#eee",
            borderRadius: 8,
            overflow: "hidden",
            position: "relative",
          }}
        >
          <div
            style={{
              width: `${Math.round(progress * 100)}%`,
              background: "#3070ea",
              height: "100%",
              transition: "width 0.4s",
            }}
          />
        </div>
        <div
          style={{
            textAlign: "right",
            fontSize: 12,
            color: "#999",
            marginTop: 2,
          }}
        >
          Step {totalSteps.indexOf(step) + 1} of {totalSteps.length}
        </div>
      </div>
    );
  }

  function renderModeStep() {
    return (
      <div>
        <h2>Welcome to Synergy Wallet</h2>
        <p>Create a new wallet or import an existing one.</p>
        <div style={{ display: "flex", gap: 20, margin: "24px 0" }}>
          <button onClick={() => handleModeSelect("create")}>
            Create New Wallet
          </button>
          <button onClick={() => handleModeSelect("import")}>
            Import Wallet
          </button>
        </div>
      </div>
    );
  }

  function renderChooseLengthStep() {
    return (
      <div>
        <h3>Choose your seed phrase length:</h3>
        <div style={{ display: "flex", gap: 20, margin: "24px 0" }}>
          {SEED_WORD_OPTIONS.map((opt) => (
            <button
              key={opt}
              onClick={() => {
                setSeedLength(opt);
                handleGenerateSeed();
              }}
              style={{ padding: "12px 28px" }}
            >
              {opt} words
            </button>
          ))}
        </div>
        <button onClick={() => setStep(Steps.MODE)} style={{ marginTop: 12 }}>
          Back
        </button>
      </div>
    );
  }

  function renderRevealStep() {
    return (
      <div>
        <h3>Your Recovery Phrase</h3>
        <p>Write down these {seedLength} words in order and keep them safe!</p>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 8,
            margin: "18px 0",
          }}
        >
          {seedPhrase.map((word, idx) => (
            <div
              key={idx}
              style={{
                width: "calc(25% - 8px)",
                padding: "8px",
                background: "#f9f9f9",
                borderRadius: 4,
                fontWeight: "bold",
                marginBottom: 4,
                textAlign: "left",
              }}
            >
              <span style={{ fontSize: 12, color: "#777", marginRight: 6 }}>
                {idx + 1}.
              </span>
              <span style={{ fontSize: 18 }}>{word}</span>
            </div>
          ))}
        </div>
        <button onClick={handleRevealContinue} style={{ marginTop: 12 }}>
          I have written down my phrase
        </button>
      </div>
    );
  }

  function renderImportChooseLengthStep() {
    return (
      <div>
        <h3>Import Wallet: Seed Phrase Length</h3>
        <div style={{ display: "flex", gap: 20, margin: "24px 0" }}>
          {SEED_WORD_OPTIONS.map((opt) => (
            <button
              key={opt}
              onClick={() => handleSeedLengthSelect(opt)}
              style={{ padding: "12px 28px" }}
            >
              {opt} words
            </button>
          ))}
        </div>
        <button onClick={() => setStep(Steps.MODE)} style={{ marginTop: 12 }}>
          Back
        </button>
      </div>
    );
  }

  function renderImportEntryStep() {
    return (
      <div>
        <h3>Enter your {seedLength}-word seed phrase</h3>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 8,
            margin: "18px 0",
          }}
        >
          {enteredSeedPhrase.map((word, idx) => (
            <div
              key={idx}
              style={{
                width: "calc(25% - 8px)",
                marginBottom: 6,
                display: "flex",
                alignItems: "center",
              }}
            >
              <span style={{ fontSize: 11, color: "#888", marginRight: 4 }}>
                {idx + 1}.
              </span>
              <input
                style={{ width: 60, padding: 4, fontSize: 15 }}
                type="text"
                autoComplete="off"
                value={word}
                onChange={(e) => {
                  const arr = [...enteredSeedPhrase];
                  arr[idx] = e.target.value.replace(/\s/g, "");
                  setEnteredSeedPhrase(arr);
                }}
              />
            </div>
          ))}
        </div>
        <button onClick={handleValidateImport} style={{ marginTop: 12 }}>
          Continue
        </button>
        <button
          onClick={() => setStep(Steps.IMPORT_CHOOSE_LENGTH)}
          style={{ marginTop: 8 }}
        >
          Back
        </button>
        {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
      </div>
    );
  }

  function renderVerifyStep() {
    const phraseArr = mode === "create" ? seedPhrase : enteredSeedPhrase;
    return (
      <div>
        <h3>Verify Your Seed Phrase</h3>
        <p>Enter the correct word for each position below:</p>
        <div style={{ display: "flex", gap: 20, margin: "20px 0" }}>
          {verifyIndexes.map((idx, i) => (
            <div key={idx}>
              <div style={{ fontSize: 12, color: "#888", marginBottom: 2 }}>
                Word #{idx + 1}
              </div>
              <input
                style={{ width: 80, padding: 5, fontSize: 16 }}
                type="text"
                autoComplete="off"
                value={verifyInputs[i]}
                onChange={(e) => {
                  const arr = [...verifyInputs];
                  arr[i] = e.target.value;
                  setVerifyInputs(arr);
                }}
              />
            </div>
          ))}
        </div>
        <button onClick={handleVerifyContinue} style={{ marginTop: 12 }}>
          Continue
        </button>
        <button
          onClick={() => {
            if (mode === "create") setStep(Steps.CREATE_REVEAL);
            else setStep(Steps.IMPORT_ENTRY);
          }}
          style={{ marginTop: 8 }}
        >
          Back
        </button>
        {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
      </div>
    );
  }

  function renderPasswordStep() {
    return (
      <div>
        <h3>Create a Wallet Password</h3>
        <p>
          Your password encrypts your wallet on this device. Do not forget it!
        </p>
        <input
          style={{ width: "100%", margin: "10px 0", padding: 8, fontSize: 16 }}
          type="password"
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <input
          style={{ width: "100%", margin: "10px 0", padding: 8, fontSize: 16 }}
          type="password"
          placeholder="Confirm password"
          value={password2}
          onChange={(e) => setPassword2(e.target.value)}
        />
        <button onClick={handlePasswordContinue} style={{ marginTop: 10 }}>
          Continue
        </button>
        <button
          onClick={() => {
            if (mode === "create") setStep(Steps.CREATE_VERIFY);
            else setStep(Steps.CREATE_VERIFY);
          }}
          style={{ marginTop: 8 }}
        >
          Back
        </button>
        {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
      </div>
    );
  }

  function renderSNSStep() {
    return (
      <div>
        <h3>Optional: Create an SNS Handle</h3>
        <input
          style={{ width: "100%", margin: "10px 0", padding: 8, fontSize: 16 }}
          type="text"
          placeholder="username.syn (optional)"
          value={sns}
          disabled={snsSkip}
          onChange={(e) => setSNS(e.target.value)}
        />
        <label style={{ display: "block", marginBottom: 16 }}>
          <input
            type="checkbox"
            checked={snsSkip}
            onChange={() => setSNSSkip(!snsSkip)}
          />
          Skip this step
        </label>
        <button onClick={handleSNSContinue} disabled={processing}>
          Finish
        </button>
        <button
          onClick={() => setStep(Steps.PASSWORD)}
          style={{ marginTop: 8 }}
        >
          Back
        </button>
        {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
      </div>
    );
  }

  function renderCompleteStep() {
    return (
      <div style={{ textAlign: "center", padding: 24 }}>
        <h2>Wallet Setup Complete!</h2>
        <p>
          You can view your wallet address and all details from the Settings
          page.
          <br />
          Redirecting to dashboard...
        </p>
        <button onClick={handleComplete} style={{ marginTop: 20 }}>
          Go to Dashboard Now
        </button>
      </div>
    );
  }

  if (!isOpen) return null;
  let stepUI = null;
  switch (step) {
    case Steps.MODE:
      stepUI = renderModeStep();
      break;
    case Steps.CREATE_CHOOSE_LENGTH:
      stepUI = renderChooseLengthStep();
      break;
    case Steps.CREATE_REVEAL:
      stepUI = renderRevealStep();
      break;
    case Steps.IMPORT_CHOOSE_LENGTH:
      stepUI = renderImportChooseLengthStep();
      break;
    case Steps.IMPORT_ENTRY:
      stepUI = renderImportEntryStep();
      break;
    case Steps.CREATE_VERIFY:
      stepUI = renderVerifyStep();
      break;
    case Steps.PASSWORD:
      stepUI = renderPasswordStep();
      break;
    case Steps.SNS:
      stepUI = renderSNSStep();
      break;
    case Steps.COMPLETE:
      stepUI = renderCompleteStep();
      break;
    default:
      stepUI = null;
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Universal Wallet Wizard">
      <div style={{ minWidth: 420, maxWidth: 500, padding: 20 }}>
        {renderProgressBar()}
        {stepUI}
        {processing && (
          <div style={{ marginTop: 12, color: "#999" }}>
            Creating wallet, please wait...
          </div>
        )}
        {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
      </div>
    </Modal>
  );
}
