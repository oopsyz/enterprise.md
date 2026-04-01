# ENTERPRISE.md: Multi-Level Repository Navigation and Routing Convention

A proposed standard for multi-level repository navigation and deterministic routing conventions that extend `AGENTS.md` to enterprise-scale, multi-repository delivery.

中文版本： [README.zh-CN.md](README.zh-CN.md)

## Read The Specification

The canonical specification for this proposal is:

- [enterprise_repo_convention.md](enterprise_repo_convention.md)

This repository intentionally uses `README.md` as the primary visitor-facing entrypoint. It does not define a root `DOMAIN.md`.

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
4. explicit role semantics for `ea`, `sa`, `da`, and `dev`
5. a fail-closed governance model for enterprise-safe automation

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
7. Routing fails closed on missing selectors, ambiguous selectors, non-routable statuses, and unresolved normative references by default.
8. Implementations must not fall back to repo-name heuristics or keyword inference for core routing.
9. `dev` is an implementation execution role anchored at the domain layer, not a separate architecture level; see the spec for detailed `da`/`dev` ownership and traversal rules.

## Conformance Profiles

`Core` checklist:

1. `AGENTS.md` plus the applicable level entrypoints exist.
2. A deterministic bootstrap discovery mechanism exists for the topmost level present.
3. `initiatives.yml` exists when enterprise and solution levels both exist.
4. `domain-workstreams.yml` exists when solution and domain levels both exist.
5. `domain-implementations.yml` exists when selector-driven domain-to-implementation routing is in scope.

`Governed` checklist:

1. All `Core` requirements are satisfied.
2. A domain governance registry exists, for example `domain-registry.yml`.
3. When a domain registry entry includes `domain_repo_url`, it also includes `domain_entrypoint`.
4. A solution scope or index manifest exists, for example `solution-index.yml`.
5. A governance state artifact exists with `spec_name`, `spec_version`, and `layers`.

Routed adoption means deterministic selector-based resolution at each architecture boundary that exists in the operating model. Absent boundaries do not require placeholder catalogs.

Examples:

1. [examples/core/README.md](examples/core/README.md)
2. [examples/governed/README.md](examples/governed/README.md)

Format note: YAML is canonical for routing catalogs.

## Routing Model

Canonical catalogs and selectors:

| Catalog | Level | Selector | Resolves |
|---|---|---|---|
| `initiatives.yml` | Enterprise | `initiative_id` | solution repository + `solution_entrypoint` |
| `domain-workstreams.yml` | Solution | `workstream_id` | `domain_id` + workstream context + repo target |
| `domain-implementations.yml` | Domain | `implementation_id` | repo location + optional entrypoint/ref |

Default routable statuses are `active` and `in_progress`.

Core and Governed implementations must provide at least one deterministic bootstrap mechanism for the topmost level present:

1. Explicit startup parameter.
2. Environment variable.
3. Well-known discovery endpoint.

Catalog examples are maintained in the canonical spec to avoid drift:

- [enterprise_repo_convention.md](enterprise_repo_convention.md) Section 5.1

Example traversal:

1. Start in `AGENTS.md`.
2. Open the level entrypoint named there.
3. Resolve the next boundary through the canonical catalog, not through repo-name search.
4. Open the resolved target entrypoint and re-anchor on that repository's local `AGENTS.md`.

## Quick Start

1. Read the [full proposal](enterprise_repo_convention.md).
2. Decide whether you need Layer A only or a routed conformance profile.
3. Get starter files from [skills/ea-convention/templates/](skills/ea-convention/templates/) or use the `ea-convention` skill to scaffold them automatically.
4. Validate your catalog files using the `ea-convention` skill's validator (for example: `python skills/ea-convention/scripts/validate_convention.py --root .`) or run schema checks against the authoritative schemas under `skills/ea-convention/references/`.
5. Define the bootstrap discovery mechanism if you are adopting the Core or Governed profile (e.g., an `ENTERPRISE_REPO_URL` environment variable, a startup parameter, or a well-known endpoint like `https://config.example.com/enterprise-catalog`).
6. Replace placeholder values with your organization's data and keep routing data in the canonical YAML catalogs.
7. See [examples/core/README.md](examples/core/README.md) and [examples/governed/README.md](examples/governed/README.md) for complete working samples.
8. For existing estates, use the brownfield guide: [reference/brownfield-adoption.md](reference/brownfield-adoption.md).

Domain repository note:

1. In a Domain repo, `AGENTS.md` should make the bounded-context boundary explicit. A short pattern is: `You are operating strictly inside the <Domain Name> bounded context. Never modify or reference artifacts owned by another domain without escalation through the authoritative routing or governance artifacts.`

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
|-- skills/
|   `-- ea-convention/                             # ea-convention skill (manage, validate, scaffold)
|       |-- SKILL.md                               # skill definition and operations
|       |-- scripts/
|       |   `-- validate_convention.py             # schema + lint validator
|       |-- references/                            # JSON schemas for canonical artifacts
|       `-- templates/
|           |-- ENTERPRISE.md.template             # enterprise entrypoint
|           |-- SOLUTION.md.template               # solution entrypoint
|           |-- DOMAIN.md.template                 # domain entrypoint
|           |-- AGENTS.{ea,sa,da,dev}.md.template  # role-specific AGENTS.md
|           |-- CLAUDE.{ea,sa,da,dev}.md.template  # role-specific CLAUDE.md bridge templates
|           |-- initiatives.yml.template           # enterprise routing catalog
|           |-- domain-workstreams.yml.template    # solution routing catalog
|           |-- domain-implementations.yml.template # domain-to-implementation routing catalog
|           |-- domain-registry.yml.template       # domain governance registry
|           |-- solution-index.yml.template        # solution scope manifest
|           |-- initiative-pipeline.yml.template   # portfolio pipeline source
|           `-- industry/
|               `-- domain-registry.telco.yml.template # telco ODA component baseline
|-- examples/
|   |-- core/                                      # core routed example
|   `-- governed/                                  # governed enterprise example
`-- reference/
    |-- brownfield-adoption.md                    # incremental adoption path for existing repo estates
    |-- harness-engineering.md                     # reference note
    |-- operational-guidance.md                    # non-normative CI, observability, and layout guidance
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

For Claude Code environments, Claude Code natively uses `CLAUDE.md` as its project instruction file. Compatibility with this proposal is achieved by bridging from `CLAUDE.md` into the same repository navigation flow defined by this proposal, with `AGENTS.md` and the applicable level entrypoint remaining the canonical cross-tool convention.
