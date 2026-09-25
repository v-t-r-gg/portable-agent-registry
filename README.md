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

A registry install/export loop, when it exists, will call self-nomad primitives
(validate, snapshot export, snapshot import, runtime restore). It will not
reimplement validation or turn the CLI into a marketplace client.

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

CI installs self-nomad 1.1.0 and runs those checks. It does not reimplement validation.

## License

MIT. See [LICENSE](LICENSE).
