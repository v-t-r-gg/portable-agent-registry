# Phase 0 — contract, seeds, read-only index

Phase 0 is the smallest honest registry: prove the package contract, do not
pretend there is a marketplace.

## In scope

- Keep [CONCEPT.md](../CONCEPT.md) as the product north star.
- Pin self-nomad 1.1.0.
- Host 3–5 specialist `.snpack` files produced by `self-nomad pack`.
- Publish `index.json` ([index-format.md](index-format.md)) and a one-page static listing.
- CI installs the pinned self-nomad wheel and runs `self-nomad pack --check`,
  `self-nomad install` into a temp directory, and `self-nomad validate --strict`.

## Out of scope

- Account systems, payments, or reputation scoring
- Web upload
- Agent-native remote MCP
- Reimplementing self-nomad validation
- Treating a live personal clone as a publishable package

## Blocked on self-nomad

`pack`, `pack --check`, and `install` exist as of self-nomad 1.0.0 and are
hardened in 1.1.0. The remaining work is seed packs plus CI that consumes
those commands. It is not missing export/import commands.

## Next phase

Phase 1 (public publish / search / download) starts only after 0.1.0:

- the pinned self-nomad release is 1.1.0
- seed packs restore into Hermes and OpenClaw
- CI has run `pack --check`, `install`, and `validate --strict` on those seeds

Phase 1 is not part of this repository's 0.1.0 tree.
