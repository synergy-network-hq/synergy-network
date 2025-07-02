# AGENTS.md

## Synergy Network Project — Agents Overview

### Purpose

The Synergy Network project employs an agent-based architecture to support modularity, scalability, security, and automation across all components (including CLI tools, browser extensions, on-chain modules, dApps, and external integrations). This document formalizes the concept of agents, their roles, responsibilities, and interaction patterns in the Synergy Network ecosystem.

---

## What is an Agent?

An **agent** is any logical or physical entity (module, process, external service, or user-controlled script) that autonomously or semi-autonomously performs discrete operations on behalf of a user, organization, or the network itself. Agents are central to Synergy Network’s design for automation, interoperability, and secure delegation.

Agents may operate:

- Within CLI tools (e.g., the Synergy Network Utility Tool)
- As browser extension background/content scripts
- As smart contract automata or protocol-level relayers
- In off-chain services (e.g., transaction relayers, monitoring bots, compliance automation)
- In user or developer automation scripts

---

## Agent Types and Responsibilities

| Agent Name       | Description                                               | Example Functions                                           |
|------------------|----------------------------------------------------------|------------------------------------------------------------|
| Wallet Agent     | Manages wallet creation, encryption, signing, storage    | Create/import wallets, sign transactions, manage keys       |
| Token Agent      | Handles all Synergy token operations                     | Mint, burn, transfer, manage metadata, enforce immutability |
| UMA Agent        | Universal Meta-Address generator and cross-chain handler | Generate addresses, validate formats, route transactions    |
| SNS Agent        | Manages Synergy Naming System logic                      | Register/update names, resolve names to addresses           |
| Bridge Agent     | Cross-chain asset relay and swap handler                 | Initiate/track atomic swaps, facilitate cross-chain sends   |
| dApp Agent       | dApp-level automation or delegated interaction           | Connect wallet, sign data, trigger user flows               |
| Extension Agent  | Browser extension processes/scripts                      | Inject provider, handle dApp integration, manage UI/UX      |
| Automation Agent | Monitoring, compliance, governance, on/off-chain bots    | Alerting, auto-moderation, compliance checks, DAO voting    |

---

## Agent Implementation Patterns

- **CLI Agents:** Implemented as modules/subcommands within the CLI, respecting least-privilege and user authentication.
- **Browser/Extension Agents:** Background/content scripts and UI components acting as user proxies for Synergy interaction.
- **On-chain Agents:** Smart contracts or protocol-level actors for automated state changes, validation, or compliance.
- **Off-chain Agents:** Daemons, bots, or services interacting via APIs or WebSockets.

Agents **must**:
- Log all privileged actions (without leaking secrets)
- Authenticate and authorize actions per agent type
- Fail securely (never proceed on ambiguous input)
- Support audit and traceability

---

## Creating or Updating Agents

1. Define the agent's role and boundaries in this file.
2. Implement as a separate, modular component (file, class, or process).
3. Document API, permissions, and security constraints in code and here.
4. Add tests for all agent-critical behaviors.
5. Update this document and reference AGENTS.md in PR/merge notes.

---

## Security and Compliance

All agents are subject to the Synergy Network’s [SECURITY.md](SECURITY.md) policy, including key management, encryption, and incident reporting. Agents that perform sensitive or external operations must undergo code review and security audit before deployment.

---

## Example Agent Usage

```sh
# Wallet agent creates a new wallet
synergy-util wallet create --output mywallet.json

# Token agent mints new tokens
synergy-util token mint TOKEN 1000 --wallet mywallet.json

# SNS agent registers a name
synergy-util sns register alice.syn --wallet mywallet.json

# UMA agent generates a cross-chain address
synergy-util uma generate --type eth --wallet mywallet.json
