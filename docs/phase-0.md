# Phase 0 — contract, seeds, read-only index

Phase 0 is the smallest honest registry: prove the package contract, do not
pretend there is a marketplace.

## In scope

- Keep [CONCEPT.md](../CONCEPT.md) as the product north star.
- Pin self-nomad 1.4.1 in CI (1.1.0 remains the minimum; seed packs are not rebuilt; tags `v0.1.0` and `v1.1.0` are not rewritten).
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

## Checked file drop

self-nomad `hub publish` writes a specialist `.snpack` after `pack --check`. A human commits that file under `packages/` and updates `index.json`. `hub pull` on the archive path or URL checks again before install. There is no upload API. A personal pack is not accepted here unless the publisher passed `--yes-personal`, and this catalog still lists only the three specialist seeds.

## Next phase

The 0.1.0 gate was a static catalog, a 1.1.1 CI pin, and seed checks. CI now installs self-nomad 1.4.1. The three seed digests and `self_nomad_min` 1.1.0 are unchanged. Operators set `SELF_NOMAD_INDEX_URL` to `https://raw.githubusercontent.com/v-t-r-gg/portable-agent-registry/main/index.json`.

Phase 1 (accounts, web upload, search, reputation) is not this tree.
