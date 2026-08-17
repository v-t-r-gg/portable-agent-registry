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

Phase 0: **spec and contract**. No public publish/search service yet.

- Founding concept: [CONCEPT.md](CONCEPT.md)
- Current work: [docs/phase-0.md](docs/phase-0.md)

## License

MIT. See [LICENSE](LICENSE).
