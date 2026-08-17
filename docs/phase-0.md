# Phase 0 — contract, seeds, read-only index

Phase 0 is the smallest honest registry: prove the package contract, do not
pretend there is a marketplace.

## In scope

- Keep [CONCEPT.md](../CONCEPT.md) as the product north star.
- Pin a self-nomad release and document the validate command this repo will
  invoke.
- Collect 3–5 specialist seed packages produced as credential-free snapshots
  (after self-nomad ships export).
- Publish a static machine-readable index (JSON) and a one-page listing.
- Run self-nomad validation in CI on every seed.

## Out of scope

- Account systems, payments, or reputation scoring
- Web upload
- Agent-native remote MCP
- Reimplementing self-nomad validation
- Treating a live personal clone as a publishable package

## Blocked on self-nomad

Export/import snapshot commands and the publish profile in ADR 0007. Until
those exist, seeds are hand-validated trees only, not installable packages.

## Next phase

Phase 1 (public publish / search / download) starts only after:

- self-nomad snapshot export and import are released
- seeds restore cleanly into Hermes and OpenClaw
- untrusted-snapshot validation has been run on those seeds
