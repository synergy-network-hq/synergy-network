# CONTRIBUTING.md

## Contributing to Synergy Network

Thank you for your interest in contributing to the Synergy Network project!
This document describes the rules, standards, and workflow for contributing to the core network, utility tool, browser extension, dApps, and supporting modules.

---

## How to Contribute

1. **Fork the repository** and create a feature or bugfix branch based on `main`.
2. **Write clear, well-documented code** following the project's style guidelines (see below).
3. **Test your code** thoroughly with unit and integration tests.
4. **Write or update documentation** for any new features or APIs.
5. **Submit a pull request** (PR) with a detailed description of the changes and motivation.
6. **Participate in code review** by responding to comments and revising as needed.
7. **Update related documentation** (`README.md`, `MANPAGE.md`, `AGENTS.md`, etc.) as required.
8. **Sign the Contributor License Agreement (CLA)** if requested by the maintainers.

---

## Code Style

- **Rust:**
  - Follow [rustfmt](https://github.com/rust-lang/rustfmt) conventions.
  - Use idiomatic Rust patterns, error handling, and modularity.
- **Python:**
  - Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style.
  - Use docstrings, type hints, and explicit error handling.
- **JavaScript:**
  - Use ES6+ features, never TypeScript.
  - Avoid global variables, prefer modular code with `import`/`export`.
  - Use `prettier` or `eslint` if set up in the project.
- **Documentation:**
  - Write in clear, concise English.
  - Use Markdown for all project documentation.
  - Keep comments up to date with code.

---

## Commit Messages

- Use descriptive commit messages.
- Reference issues or PRs using `#number` where applicable.
- Example:
  `feat(wallet): add encrypted keystore import/export (#42)`

---

## Branching and Pull Requests

- **Branch naming:**
  - `feature/<topic>` for new features.
  - `bugfix/<topic>` for fixes.
  - `doc/<topic>` for documentation.
- **Pull Requests:**
  - Use draft PRs for early feedback.
  - PRs should address a single purpose.
  - Link related issues.
  - Ensure all tests pass before requesting review.
  - Assign reviewers or tag `@justinhutzler` if urgent.

---

## Issue Reporting

- Use the GitHub Issues tracker for all bugs, enhancement requests, and documentation needs.
- Provide detailed steps to reproduce, logs, and environment information.
- Mark critical security issues as **Security** (see [SECURITY.md](SECURITY.md)).

---

## Code of Conduct

All contributors are expected to follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/) and treat others with respect.

---

## Licensing

By contributing, you agree that your code will be licensed under the project’s license (see `LICENSE` file).

---

## Contact

For urgent issues or questions, contact the project maintainer:

- **Lead Maintainer:** Justin Hutzler (justinhutzler@protonmail.com)
- **Discord:** [Synergy Network Community](https://discord.gg/synergynetwork)

---

**Thank you for helping build Synergy Network!**
