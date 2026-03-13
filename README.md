# Multi-Level Repository Navigation and Routing Convention

A proposed standard for multi-level repository navigation and deterministic routing conventions that extend `AGENTS.md` to enterprise-scale, multi-repository delivery.

This repository intentionally uses `README.md` as the primary visitor-facing entrypoint. It does not define a root `DOMAIN.md`.

If you use Claude Code, note that Claude Code natively uses `CLAUDE.md` as its project instruction file. Compatibility with this proposal is therefore achieved by bridging from `CLAUDE.md` into the `AGENTS.md` and level-entrypoint flow defined here.

## Status

**Draft** - open for feedback.

Classification: **Proposed Standard**.

## Referencing This Proposal

Use this repository as the canonical reference when citing the convention from other projects.

Recommended reference text:

`Multi-Level Repository Navigation and Routing Convention (Proposed Standard, Draft)`

Canonical specification:

- [enterprise_repo_convention.md](enterprise_repo_convention.md)

## Problem

`AGENTS.md` works well for single-repository agent behavior, but enterprise delivery spans multiple repositories across architecture levels (enterprise, solution, domain). Teams need level-aware entrypoints, deterministic cross-repository routing, and explicit ownership and governance.

## What This Proposes

Two independent, separable layers:

| Layer | Purpose | Requires tooling? |
|---|---|---|
| **Layer A: Entrypoint Convention** | Human/agent navigation via `ENTERPRISE.md`, `SOLUTION.md`, `DOMAIN.md` | No |
| **Layer B: Routing Catalog Specification** | Deterministic machine routing between levels via YAML catalogs and workstream context | Yes - any tool-capable consumer such as an agent, script, IDE integration, or orchestration runtime |

Organizations can adopt Layer A without Layer B, but conformance profiles start at routed adoption.

The proposal is built around progressive disclosure:

1. Entry points provide concise navigation and context.
2. Canonical catalogs carry deterministic routing data.
3. Detailed design and implementation context stays in linked artifacts.

## Positioning

`ENTERPRISE.md` is not a competing AI assistant, IDE, or coding agent.

It is a proposed convention layer that existing tools can implement or follow in order to operate more effectively in enterprise multi-repository environments.

In practical terms, the proposal defines:

1. a navigation standard for repository-level and architecture-level entrypoints
2. a deterministic routing standard for moving between enterprise, solution, domain, and implementation contexts
3. a shared artifact-based context model for isolated sessions or threads
4. a fail-closed governance model for enterprise-safe automation

This means the relationship is:

1. tools such as Codex, Claude Code, Cursor, and Copilot provide AI execution surfaces
2. `ENTERPRISE.md` provides the repository and routing convention those tools can use across multi-repo delivery

Short form:

`ENTERPRISE.md` is the multi-repo coordination standard, not the coding assistant.

## Key Rules

1. `AGENTS.md` remains the repo-local behavior contract. See the [`AGENTS.md` convention](https://github.com/agentsmd/agents.md) for background.
2. Agents MUST start with `AGENTS.md`, and `AGENTS.md` MUST instruct agents to always read the repository's level entrypoint.
3. `ENTERPRISE.md`, `SOLUTION.md`, and `DOMAIN.md` are navigation entrypoints, not duplicated data stores.
4. Upstream links are explicit by level: `SOLUTION.md` and `DOMAIN.md` link to `ENTERPRISE.md` when the enterprise level exists.
5. `DOMAIN.md` does not use `SOLUTION.md` as a required parent link because solution-to-domain relationships are many-to-many and belong in routing catalogs or handoff artifacts. For example, a shared "identity" domain may serve both a "customer portal" solution and an "internal tools" solution simultaneously.
6. YAML is canonical for routing catalogs.
7. Routing fails closed on missing selectors, ambiguous selectors, and non-routable statuses by default.
8. Implementations must not fall back to repo-name heuristics or keyword inference for core routing.

## Conformance Profiles

| Profile | What you need |
|---|---|
| **Core** | Layer A + deterministic bootstrap discovery for the topmost level present + routing catalogs for boundaries that exist |
| **Governed** | Core + governance registry, solution scope manifest, and governance state artifact |

See [examples/](examples/) for working samples of each profile.

Format note: YAML is canonical for routing catalogs.

## Routing Model

Canonical catalogs and selectors:

| Catalog | Level | Selector | Resolves |
|---|---|---|---|
| `initiatives.yml` | Enterprise | `initiative_id` | solution repository + `solution_entrypoint` |
| `domain-workstreams.yml` | Solution | `workstream_id` | `domain_id` + workstream context + repo target |
| `domain-implementations.yml` | Domain | `implementation_id` | repo location |

Default routable statuses are `active` and `in_progress`.

Core and Governed implementations must provide at least one deterministic bootstrap mechanism for the topmost level present:

1. Explicit startup parameter.
2. Environment variable.
3. Well-known discovery endpoint.

## Quick Start

1. Read the [full proposal](enterprise_repo_convention.md).
2. Decide whether you need Layer A only or a routed conformance profile.
3. Copy the relevant starter files from [templates/](templates/) into your repositories.
4. Define the bootstrap discovery mechanism if you are adopting the Core or Governed profile (e.g., an `ENTERPRISE_REPO_URL` environment variable, a startup parameter, or a well-known endpoint like `https://config.example.com/enterprise-catalog`).
5. Replace placeholder values with your organization's data and keep routing data in the canonical YAML catalogs.
6. See [examples/](examples/) for complete working samples at each profile level.

## Repository Contents

```text
.
|-- README.md                                      # this file
|-- LICENSE                                        # Apache 2.0 license
|-- AGENTS.md                                      # agent navigation for this repo
|-- enterprise_repo_convention.md                  # the full proposal
|-- CHANGELOG.md                                   # project-level release history
|-- CONTRIBUTING.md                                # contribution workflow
|-- CODE_OF_CONDUCT.md                             # community behavior expectations
|-- SECURITY.md                                    # private security reporting guidance
|-- GOVERNANCE.md                                  # maintainer decision model and versioning
|-- releases/                                      # release notes drafts
|-- .github/                                       # issue templates, PR template, CI, CODEOWNERS
|-- templates/
|   |-- README.md                                  # template usage guide
|   |-- ENTERPRISE.md.template                     # enterprise entrypoint
|   |-- SOLUTION.md.template                       # solution entrypoint
|   |-- DOMAIN.md.template                         # domain entrypoint
|   |-- AGENTS.{ea,sa,da,dev}.md.template          # role-specific AGENTS.md
|   |-- CLAUDE.{ea,sa,da,dev}.md.template          # role-specific CLAUDE.md bridge templates
|   |-- initiatives.yml.template                   # enterprise routing catalog
|   |-- domain-workstreams.yml.template            # solution routing catalog
|   |-- domain-implementations.yml.template        # domain-to-implementation routing catalog
|   |-- domain-registry.yml.template               # domain governance registry
|   |-- solution-index.yml.template                # solution scope manifest
|   |-- initiative-pipeline.yml.template           # portfolio pipeline source
|   `-- industry/
|       `-- domain-registry.telco.yml.template     # telco ODA component baseline
|-- examples/
|   |-- core/                                      # core routed example
|   `-- governed/                                  # governed enterprise example
`-- reference/
    |-- harness-engineering.md                     # reference note
    `-- machine-access-contract.md                 # optional contract for querying canonical routing catalogs
```

## Ownership Model

Recommended default owners:

| Artifact | Owner |
|---|---|
| `AGENTS.md` | Repository owners |
| `ENTERPRISE.md` | EA |
| `SOLUTION.md` | SA |
| `DOMAIN.md` | DA |
| `initiatives.yml` | EA/PMO |
| `domain-workstreams.yml` | SA |
| `domain-implementations.yml` | DA |

If roles are collapsed in one team or repository, ownership MUST be explicitly declared in the relevant entrypoint.

## Contributing

This proposal is in draft. Feedback is welcome via issues or pull requests.

When opening an issue, please indicate which layer (A or B) or conformance profile (`Core`/`Governed`) your feedback relates to. For pull requests, keep changes focused on one section of the proposal at a time.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflow and review expectations, [GOVERNANCE.md](GOVERNANCE.md) for decision-making and versioning, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

## License

This repository is licensed under Apache 2.0. See [LICENSE](LICENSE).

## Compatibility

This proposal is additive to `AGENTS.md`. It does not replace or modify the existing standard.

For Claude Code environments, repositories should bridge from `CLAUDE.md` into the same repository navigation flow defined by this proposal, with `AGENTS.md` and the applicable level entrypoint remaining the canonical cross-tool convention.
