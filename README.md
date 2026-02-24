# licitra-core (private)

Core implementation repository for LICITRA.

- FastAPI backend + PostgreSQL ledger
- Per-organization hash-chain logging (SHA-256)
- Deterministic canonical JSON hashing
- Verification endpoints
- Rollback v0 (circuit breaker)

NOTE: Keep secrets out of git (.env is ignored). Use .env.example as template.
