# Portable Agent Registry

An open marketplace concept for **immutable, portable AI agent packages**.

This repository is the registry product. It is **not** [self-nomad](https://github.com/v-t-r-gg/self-nomad).
self-nomad stays a standalone local-first CLI. This project consumes that
toolkit to validate, index, and later host credential-free snapshots.

## Relationship to self-nomad

| Product | Job |
| --- | --- |
| [self-nomad](https://github.com/v-t-r-gg/self-nomad) | Govern and move one agent's self on a trusted machine |
| This repository | Discover, host, and distribute many untrusted packages |

Publish is a checked file dropped into this tree by a human pull request.
Install calls self-nomad. This repository does not reimplement validation
and it does not accept a web upload.

See [docs/product-boundary.md](docs/product-boundary.md).

## Status

**0.1.0** — read-only catalog. No accounts, payments, web upload, remote MCP,
or reputation scores.

- Founding concept: [CONCEPT.md](CONCEPT.md)
- Boundary: [docs/product-boundary.md](docs/product-boundary.md)
- Phase 0: [docs/phase-0.md](docs/phase-0.md)
- Index format: [docs/index-format.md](docs/index-format.md)
- Listing: [site/index.html](site/index.html)
- Machine-readable index: [index.json](index.json)

Install a listed pack with self-nomad, not with a registry client:

```bash
self-nomad pack --check packages/demo-echo/1.0.0/demo-echo.snpack
self-nomad install packages/demo-echo/1.0.0/demo-echo.snpack --to ./echo
self-nomad --repo ./echo validate --strict
self-nomad --repo ./echo restore --adapter hermes --to "$HERMES_HOME" --yes
self-nomad --repo ./echo restore --adapter openclaw --to "$OPENCLAW_WORKSPACE" --yes
```

CI installs self-nomad 1.4.0 from the git tag and runs those checks. It does not reimplement validation. Seed packs were built with 1.1.0; `self_nomad_min` stays 1.1.0. Tag `v0.1.0` is not rewritten.

## Pull and publish

self-nomad 1.4.0 can move a pack. This registry still has no upload API.

Pull a `.snpack` path or URL. `hub pull` runs `pack --check` before `install`:

```bash
self-nomad hub pull packages/demo-echo/1.0.0/demo-echo.snpack --to ./echo
```

Name lookup reads a local index (`SELF_NOMAD_INDEX_URL` as a `file://` URL). Relative `pack` paths resolve next to that file. They are not resolved against the raw GitHub URL of `index.json`. Pass the archive URL itself when you are not in a checkout.

Publish writes a file. It does not upload, and it refuses a personal-profile pack unless `--yes-personal` is set:

```bash
self-nomad --repo ./agent hub publish --drop ./agent.snpack
```

Open a pull request that adds that file under `packages/<name>/<version>/` and updates `index.json`. Do not commit a working Git clone. CI runs `pack --check` again.

## License

MIT. See [LICENSE](LICENSE).
