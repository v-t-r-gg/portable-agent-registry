# Product boundary

This registry and [self-nomad](https://github.com/v-t-r-gg/self-nomad) are
separate products that share a package contract.

The contract is recorded in self-nomad as
[ADR 0007](https://github.com/v-t-r-gg/self-nomad/blob/main/docs/decisions/0007-publishable-package-profile.md)
(publishable package profile). This document is the registry-side reading of
the same decisions.

## What this repository owns

- Discovery, hosting, search, download URLs
- A machine-readable index of validated packages
- Reputation or attestation feeds, if they are built
- Web UI and agent-facing APIs
- Seeding and curation of specialist packages

## What self-nomad owns

- The portable tree format (`self-nomad.yaml` and referenced artifacts)
- Structural validation, secret scanning, and path rules
- Local proposal governance (materialize → validate → approve → apply)
- Runtime adapters (Hermes, OpenClaw, later others)
- Local snapshot commands: `self-nomad pack`, `self-nomad pack --check`,
  `self-nomad install`, and `self-nomad restore`
- `self-nomad validate --strict`

## How integration works

The registry **consumes** self-nomad. It does not vendor a second validator.

1. A publisher runs `self-nomad --repo ./agent hub publish --drop ./agent.snpack`
   (or `pack`, then `pack --check`). That writes a specialist snapshot after
   the check. It is not a Git clone. A personal pack is refused unless
   `--yes-personal` is set. Nothing is uploaded.
2. A human adds that file under `packages/<name>/<version>/` and updates
   `index.json`. Registry CI runs `self-nomad pack --check`, `install` into
   a temp directory, and `validate --strict`.
3. A consumer runs `self-nomad hub pull ARCHIVE --to NEW_REPO` (check, then
   install) or `self-nomad install`, then `restore`.

self-nomad does not host, search, or authenticate to this index. The optional
`hub` extra only moves an already-checked archive. With self-nomad 1.4.1, a
relative `pack` path is joined to the directory of `SELF_NOMAD_INDEX_URL`.
`..` is refused. The catalog URL is
`https://raw.githubusercontent.com/v-t-r-gg/portable-agent-registry/main/index.json`.

## Publish profile (constraints on packages we will index)

- The unit of exchange is a **validated tree snapshot**, not the author's
  working Git history (history retains deleted content).
- Specialist packages must not include `user_profile` or daily memory by
  default. Long-term memory is allow-listed facts only, not a personal dump.
- Credentials, sessions, and runtime databases are never portable.
- Proposal records and intake receipts stay on the operator machine. This
  registry does not require them in the package.
- Schema version 1 is current. License, authors, package version, and tags
  wait for an explicit self-nomad schema decision.

## Phase 0 implication

`pack` and `install` exist. Phase 0 is a static index of specialist seed
packs plus CI that calls self-nomad. Do not stand up a public upload service
in this phase.
