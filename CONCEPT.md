# Portable Agent Registry

*An Open Marketplace for Immutable, Portable AI Agent Packages*

Project Concept Document  •  August 2026

This is the founding concept for **this** repository. The local CLI that
defines the package format is [self-nomad](https://github.com/v-t-r-gg/self-nomad),
a separate product. Integration notes: [docs/product-boundary.md](docs/product-boundary.md).

## 1. Vision

A public registry where anyone can publish, discover, and install complete, versioned AI agent packages. Each package is a credential-free `self-nomad-pack-v1` snapshot of durable identity, curated memory, skills, and behavioral constraints. It is not a Git clone and it does not contain proposal receipts or working Git history. Packages travel between runtimes without credentials or session state. A reputation feed may later be published by the registry beside a package. It is not stored inside the snapshot.

The site functions as the Hugging Face of portable agent selves: open, searchable, machine-readable first, and designed for both human browsers and agent-to-agent discovery.

## 2. Problem

Today’s agent sharing landscape is fragmented and incomplete:

- Most marketplaces lock agents to a single platform (GPT Store, Copilot Agent Store, vendor-specific builders).
- Personality-focused sites exist (SOULHUB, agentsoul.market) but remain small and limited to lightweight persona files.
- Full agent packages that include memory and skills rarely travel cleanly between runtimes.
- Reputation is either absent or tied to a closed platform, so an agent that performs well in one environment carries no verifiable history elsewhere.
- Local-first and edge agents (phone, laptop, personal servers) lack a neutral place to publish and discover specialist packages.

## 3. Proposed Solution

Build an open registry whose unit of exchange is a `self-nomad-pack-v1` snapshot, not a Git clone and not the author's working history. A published agent package is a content-addressed, credential-free archive containing:

- Identity – `self.id`, `self.name`, and `self.description` from the tree, copied into the pack sidecar until a schema bump adds more fields
- Curated memory – only what the specialist profile allows. User profile and daily memory are omitted. Long-term memory is opt-in and, on current self-nomad, limited to `memory/PUBLISH.md`
- Skills and tool notes – declarations of capabilities
- Behavioral constraints – persona, instructions, and policy files that are part of the portable tree

Proposal records, intake receipts, and working Git history are not in the artifact. A registry that later wants an audit trail owns that feed itself. A reputation ledger is a later phase. It is not part of the 0.1.0 package.

## 4. Core Building Blocks

### 4.1 Self-Nomad Package Format

The registry adopts the self-nomad snapshot as its native package format. self-nomad is a local-first Python toolkit. On a trusted machine it keeps durable identity, curated memory, and skills under Git, and changes move through a typed proposal workflow. Credentials and runtime session data never enter the repository. That Git history stays local.

A published package is a `self-nomad-pack-v1` gzip tar produced by `self-nomad pack` (specialist profile by default). `self-nomad pack --check` and `self-nomad install` validate it. `self-nomad validate --strict` is the tree check those commands run. `self-nomad restore` copies mapped files into Hermes or OpenClaw. The indexable identity is `self.id`, `self.name`, `self.description`, and the pack sidecar until a self-nomad schema bump.

### 4.2 Portable Reputation Ledger

A later phase may publish a signed feed of verified outcomes next to a package. The feed is registry data. It is not a member of the snapshot. Records would include:

- Task category and success/failure
- Measured cost (tokens, latency, external spend)
- Human correction events
- Counterparty attestation (optional)

The ledger can begin as a simple signed feed mirrored by the registry and later evolve toward decentralized storage. Agents and humans query the ledger before installing or hiring a package.

## 5. Key Features

### Discovery

- Search by task, skill, domain, model family, or free-text description
- Filters for reputation score, number of verified runs, last update, license
- Machine-readable index (JSON/API) so other agents can discover packages without a browser

### Publishing

Phase 0 does not upload. A publisher runs `self-nomad pack` on a trusted machine and the registry stores the resulting `.snpack`. There is no web upload and no registry publish CLI in 0.1.0.

- Index fields come from `self-nomad pack --check --json`: profile, digest, skill names, and the sidecar identity
- Specialist profile is the default. Personal archives are not listed
- Proposal history is not versioned inside the package. Later registry phases may attach their own attestation feed

### Installation & Runtime Integration

- One-command restore into supported runtimes (Hermes, OpenClaw, and future adapters)
- Transactional apply with rollback on failure
- Clear separation: the package never contains API keys or owner credentials

### Reputation Surface

- Public score derived from verified outcome records
- Drill-down into individual attestations
- Ability for an agent or human to attach a new signed outcome after use

## 6. Target Users

#### Human Creators

Builders who tune agents for narrow, high-value tasks (invoice reconciliation, code review style, domain research, personal scheduling) and want those packages to travel beyond a single chat interface.

#### Human Consumers

Individuals and small teams who prefer to start from a proven specialist rather than prompting from scratch.

#### Local / Edge Agents

Phone- or laptop-resident agents that query the registry for the current best specialist for a sub-task, pull the package, and restore it locally or route work to it.

#### Platform Operators

Runtime providers that want a neutral source of high-quality, portable agent packages their users can import.

## 7. Market Context & Demand

Multiple agent marketplaces already operate. OpenAI’s GPT Store has over three million custom GPTs created and roughly 159,000 publicly listed. LobeHub lists more than 147,000 agents. Commercial marketplaces such as CustomAgent.app report thousands of listed agents and businesses served. Personality-focused sites (SOULHUB, agentsoul.market) demonstrate demand for portable personas even while remaining early-stage.

Enterprise and local-agent growth further increases the need. Hundreds of thousands of business agents already run in production. Forecasts show rapid expansion of the agentic AI market. Personal agents on devices continue to multiply, creating demand for packages that move cleanly between runtimes.

The open gap is a neutral registry of credential-free self-nomad snapshots (identity, allowed memory, and skills). Existing sites prove the desire to share and reuse. Reputation and public upload are later phases, not part of the snapshot.

## 8. Competitive Landscape

Current offerings fall into several categories:

- Platform-locked stores – GPT Store, Microsoft Agent Store, Salesforce AgentExchange. High reach, low portability.
- Personality marketplaces – SOULHUB, agentsoul.market. Focused on souls/personas, still small.
- Commercial agent marketplaces – CustomAgent.app, AgentBazaar. Emphasize hiring and monetization.
- Open infrastructure – Hugging Face Spaces + agents.md, various GitHub collections. Strong openness, weak specialization in full agent packages.

No current platform combines a self-nomad-style immutable package format, portable reputation, and an open discovery surface designed for both humans and agents.

## 9. Minimum Viable Product

Release 0.1.0 is a read-only catalog, not a marketplace:

- Pin self-nomad 1.1.0.
- Host 3–5 specialist `.snpack` files plus `index.json`.
- CI installs that self-nomad wheel and runs `self-nomad pack --check`, `self-nomad install` into a temp directory, and `self-nomad validate --strict`. It does not reimplement validation.
- A single static page lists the index.
- Download is the raw file URL. Install instructions point at `self-nomad install` and `self-nomad restore`.

No accounts, payments, web upload, remote MCP, reputation scores, or registry publish command. Search and a reputation feed are Phase 1 and later. The goal of 0.1.0 is to prove that a stranger can install a listed specialist pack and restore it.

## 10. Roadmap Sketch

- Phase 0 – Internal – Stabilize package contract with self-nomad, seed 10–20 high-quality packages, stand up read-only index.
- Phase 1 – Public MVP – Open publishing, search, download, basic reputation feed.
- Phase 2 – Agent-native discovery – Full API + MCP surface so local agents can query and pull packages autonomously.
- Phase 3 – Reputation depth – Richer attestation types, optional staking or skin-in-the-game signals, reputation graphs.
- Phase 4 – Ecosystem – Additional runtime adapters, optional monetization rails, federated mirrors.

## 11. Risks & Open Questions

- Cold-start – Early packages may be few. Mitigation: seed with strong internal and community packages; partner with existing self-nomad users.
- Quality & safety – Malicious or low-quality packages. Mitigation: validation on upload, community flagging, reputation as the primary filter.
- Format adoption – Other runtimes may not adopt the self-nomad package shape. Mitigation: keep the format simple and document clear adapters.
- Reputation gaming – Fake outcome records. Mitigation: start with signed, low-volume attestations; raise the cost of false claims over time.

## 12. Success Metrics (First Six Months)

- 50+ published packages from independent creators
- 500+ package installs / downloads
- At least one external runtime adapter beyond the initial set
- Measurable agent-to-agent discovery traffic via the API
- Positive qualitative feedback from local-agent builders

## 13. Immediate Next Steps

- Index the pack sidecar fields self-nomad 1.1.0 already emits (`self.id`, name, description, digest, skills, profile).
- Keep 0.1.0 a static index of specialist snapshots. Do not add upload or search in this release.
- Seed the index with packs produced by `self-nomad pack`.
- Point install docs at `self-nomad install` and `self-nomad restore`.

This registry turns the portable, immutable agent self into a first-class, discoverable object. It gives local and edge agents a neutral place to find specialists, and it gives creators a place to publish work that can outlive any single runtime.
