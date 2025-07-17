
import React, { useState } from "react";
import { generateMnemonic } from "@scure/bip39";
import { wordlist } from "@scure/bip39/wordlists/english";
import { initDilithium } from "../pqc/dilithium.js";
import { pubkeyToSynergyAddress } from "../utils/synergyAddress";
import "../styles/main.css";

function toHex(uint8arr) {
  if (!uint8arr) return "";
  return Array.from(uint8arr)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export default function PQCWallet() {
  const [step, setStep] = useState(1);
  const [mnemonic, setMnemonic] = useState("");
  const [mnemonicInput, setMnemonicInput] = useState(Array(12).fill(""));
  const [mnemonicError, setMnemonicError] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [walletInfo, setWalletInfo] = useState(null);
  const [processing, setProcessing] = useState(false);

  // Step 1: Generate and display mnemonic
  const handleGenerateMnemonic = () => {
    const phrase = generateMnemonic(wordlist, 128); // 12 words
    setMnemonic(phrase);
    setStep(2);
  };

  // Step 2: User confirms mnemonic
  const handleMnemonicInputChange = (i, value) => {
    const updated = [...mnemonicInput];
    updated[i] = value.trim();
    setMnemonicInput(updated);
  };

  const handleCheckMnemonic = (e) => {
    e.preventDefault();
    if (mnemonicInput.join(" ").trim() === mnemonic.trim()) {
      setMnemonicError("");
      setStep(3);
    } else {
      setMnemonicError("Incorrect phrase! Please check the word order and spelling.");
    }
  };

  // Step 3: Set password
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 8) {
      setPasswordError("Password must be at least 8 characters.");
      return;
    }
    if (password !== passwordConfirm) {
      setPasswordError("Passwords do not match.");
      return;
    }
    setPasswordError("");
    setProcessing(true);
    try {
      const pqc = await initDilithium();
      const kp = await pqc.keypair();
      const synergyAddress = await pubkeyToSynergyAddress(kp.publicKey);
      setWalletInfo({
        mnemonic,
        publicKey: toHex(kp.publicKey),
        synergyAddress,
      });
      setStep(4);
    } catch (err) {
      setPasswordError("Failed to create wallet: " + err.message);
    }
    setProcessing(false);
  };

  // --- UI Render ---
  return (
    <div className="inlineStyle32">
      {step === 1 && (
        <div className="inlineStyle3">
          <h1 className="inlineStyle33">Create a New Synergy Wallet</h1>
          <button className="btn inlineStyle34" onClick={handleGenerateMnemonic}>
            Generate My 12-Word Recovery Phrase
          </button>
          <p className="inlineStyle35">
            A recovery phrase lets you restore your wallet if your device is lost or stolen.<br />
            Never share it with anyone. <strong>You are your own bank.</strong>
          </p>
        </div>
      )}
      {step === 2 && (
        <div>
          <h2 className="inlineStyle36">Your Recovery Phrase</h2>
          <div className="inlineStyle37">
            <span className="inlineStyle38">{mnemonic}</span>
          </div>
          <div className="inlineStyle39">
            <span>⚠️ Write these 12 words down, in order. They won't be shown again!</span>
          </div>
          <button
            className="btn inlineStyle40"
            onClick={() => {
              setMnemonicInput(Array(12).fill(""));
              setStep(2.5);
            }}
          >
            I have recorded the phrase
          </button>
        </div>
      )}
      {step === 2.5 && (
        <form onSubmit={handleCheckMnemonic}>
          <h2 className="inlineStyle41">Confirm Your Recovery Phrase</h2>
          <p className="inlineStyle42">
            Enter each word in the correct position to confirm you've written it down:
          </p>
          <div className="inlineStyle43">
            {Array(12)
              .fill()
              .map((_, i) => (
                <input
                  key={i}
                  type="text"
                  value={mnemonicInput[i]}
                  onChange={(e) => handleMnemonicInputChange(i, e.target.value)}
                  required
                  autoFocus={i === 0}
                  className="inlineStyle44"
                />
              ))}
          </div>
          {mnemonicError && <div className="inlineStyle45">{mnemonicError}</div>}
          <button type="submit" className="btn inlineStyle46">
            Confirm Phrase
          </button>
        </form>
      )}
      {step === 3 && (
        <form onSubmit={handlePasswordSubmit}>
          <h2 className="inlineStyle47">Set a Wallet Password</h2>
          <p className="inlineStyle48">
            This password encrypts your wallet locally. It does <strong>not</strong> replace your
            recovery phrase.<br />
            <strong>Minimum 8 characters.</strong>
          </p>
          <input
            type="password"
            placeholder="Create password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="inlineStyle49"
            required
            minLength={8}
          />
          <input
            type="password"
            placeholder="Confirm password"
            value={passwordConfirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            className="inlineStyle50"
            required
            minLength={8}
          />
          {passwordError && <div className="inlineStyle51">{passwordError}</div>}
          <button type="submit" disabled={processing} className="btn inlineStyle40">
            {processing ? "Creating Wallet..." : "Create Wallet"}
          </button>
        </form>
      )}
      {step === 4 && walletInfo && (
        <div>
          <h2 className="inlineStyle47">Your Wallet is Ready</h2>
          <div className="inlineStyle52">
            <div>
              <strong>PQC Public Key:</strong> <br />
              {walletInfo.publicKey}
            </div>
            <div className="inlineStyle53">
              <strong>Synergy Address:</strong> <br />
              {walletInfo.synergyAddress}
            </div>
          </div>
          <div className="inlineStyle54">
            Keep your recovery phrase and password safe. You’ll need the phrase to restore your wallet.
          </div>
        </div>
      )}
    </div>
  );
}
