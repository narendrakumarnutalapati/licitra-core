# Security Policy

## Overview

LICITRA (Core) provides cryptographic runtime integrity for agentic AI systems.  
This repository implements a tamper-evident ledger using deterministic canonical JSON hashing and hash-chained events persisted in PostgreSQL.

Security is central to LICITRA’s purpose. This document describes:

- Supported versions
- Threat model boundaries
- Responsible disclosure process
- Known limitations

---

## Supported Versions

The following versions currently receive security updates:

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes     |
| < 0.1   | ❌ No      |

Security updates will be issued on the latest minor version of the current release line.

---

## Security Model

LICITRA provides **cryptographic integrity guarantees**, not behavioral guarantees.

### Guarantees

- Detection of mutation of committed event payloads
- Detection of deletion or reordering of committed events
- Detection of hash-chain corruption
- Deterministic verification of ledger integrity
- Multi-organization isolation (per-org chain independence)

### Non-Goals

LICITRA does **not**:

- Prevent prompt injection
- Prevent hallucinations
- Enforce model alignment
- Provide OS-level hardening
- Provide distributed consensus (not a blockchain)
- Prevent full system or database destruction

LICITRA detects silent mutation — it does not prevent privileged deletion.

---

## Threat Model

### In-Scope Threats

- Modification of stored event payloads
- Rewriting of previous hashes
- Event reordering
- Silent database row mutation
- Cross-organization contamination attempts

### Out-of-Scope Threats

- Root-level OS compromise
- Full database file deletion
- Kernel-level attacks
- SHA-256 cryptographic breaks
- Infrastructure takeover

---

## Cryptographic Assumptions

Security guarantees depend on:

- SHA-256 collision resistance
- Deterministic canonical JSON serialization
- Integrity of the verification algorithm

If SHA-256 is ever shown to be practically broken, the integrity guarantees of this system must be re-evaluated.

---

## Reporting a Vulnerability

If you discover a security vulnerability in LICITRA:

1. **Do NOT open a public issue.**
2. Email: **narendrakumar.nutalapati@gmail.com**
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Impact assessment
   - Suggested mitigation (if available)

You can expect:
- Acknowledgment within 72 hours
- Initial assessment within 7 days
- Coordinated disclosure timeline if confirmed

Please allow reasonable time for investigation and patching before public disclosure.

---

## Disclosure Policy

- Confirmed vulnerabilities will be patched in the latest supported version.
- Security advisories will be published via GitHub Security Advisories.
- CVE assignment will be requested when appropriate.

---

## Hardening Recommendations

For production deployments:

- Restrict database superuser access
- Enable PostgreSQL WAL archiving
- Use encrypted disk volumes
- Restrict network exposure of the verification endpoint
- Run backend behind a reverse proxy with TLS
- Enable structured audit logging

---

## Versioning & Future Security Roadmap

Planned future improvements:

- Merkle Mountain Range (MMR) scalability layer
- External anchoring (optional)
- Optional digital signatures for epoch roots
- Formal security specification publication

---

## Final Statement

LICITRA is a **cryptographic runtime integrity primitive**.

It guarantees that once an AI agent action is committed, its historical record cannot be altered without detection.

It does not claim to guarantee safe behavior — only verifiable history.
