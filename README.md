# enterprise.md

A proposed standard for multi-level repository navigation and routing conventions that extend `AGENTS.md` to enterprise-scale, multi-repository delivery.

## Status

**Draft** - open for feedback.

Classification: **Proposed Standard**.

## Referencing This Proposal

Use this repository as the canonical reference when citing the convention from other projects.

Recommended reference text:

`Multi-Level Repository Navigation and Routing Convention (Proposed Standard, Draft)`

Canonical specification:

- [multi_level_repository_navigation_and_routing_convention.md](multi_level_repository_navigation_and_routing_convention.md)

## Problem

`AGENTS.md` works well for single-repository agent behavior, but enterprise delivery spans multiple repositories across architecture levels (enterprise, solution, domain). Teams need level-aware entrypoints, deterministic cross-repository routing, and explicit ownership and governance.

## What This Proposes

Two independent, separable layers:

| Layer | Purpose | Requires tooling? |
|---|---|---|
| **Layer A: Entrypoint Convention** | Human/agent navigation via `ENTERPRISE.md`, `SOLUTION.md`, `DOMAIN.md` | No |
| **Layer B: Routing Catalog Specification** | Deterministic machine routing between levels via YAML catalogs and workstream context | Orchestration/runtime only |

Organizations can adopt Layer A without Layer B.

## Positioning

`enterprise.md` is not a competing AI assistant, IDE, or coding agent.

It is a proposed convention layer that existing tools can implement or follow in order to operate more effectively in enterprise multi-repository environments.

In practical terms, the proposal defines:

1. a navigation standard for repository-level and architecture-level entrypoints
2. a deterministic routing standard for moving between enterprise, solution, domain, and implementation contexts
3. a shared artifact-based context model for isolated sessions or threads
4. a fail-closed governance model for enterprise-safe automation

This means the relationship is:

1. tools such as Codex, Claude Code, Cursor, and Copilot provide AI execution surfaces
2. `enterprise.md` provides the repository and routing convention those tools can use across multi-repo delivery

Short form:

`enterprise.md` is the multi-repo coordination standard, not the coding assistant.

## Conformance Profiles

| Profile | What you need |
|---|---|
| **A: Entrypoint-Only** | `AGENTS.md` + at least one level entrypoint |
| **B: Routed Automation** | Profile A + bootstrap discovery + routing catalogs for boundaries that exist |
| **C: Governed Enterprise** | Profile B + governance registry + governance state artifact |

See [examples/](examples/) for working samples of each profile.

Format note: YAML is canonical for routing catalogs. JSON is an optional schema-equivalent compatibility projection.

## Quick Start

1. Read the [full proposal](multi_level_repository_navigation_and_routing_convention.md).
2. Pick a conformance profile that fits your organization.
3. Copy the relevant starter files from [templates/](templates/) into your repositories.
4. Replace placeholder values with your organization's data.
5. See [examples/](examples/) for complete working samples at each profile level.

## Repository Contents

```text
README.md                                          -- this file
AGENTS.md                                          -- agent navigation for this repo
multi_level_repository_navigation_and_routing_convention.md    -- the full proposal
templates/                                         -- starter templates for adoption
  ENTERPRISE.md.template                           -- enterprise entrypoint
  SOLUTION.md.template                             -- solution entrypoint
  DOMAIN.md.template                               -- domain entrypoint
  AGENTS.{ea,sa,da,dev}.md.template                -- role-specific AGENTS.md
  initiatives.yml.template                         -- enterprise routing catalog
  domain-workstreams.yml.template                  -- solution routing catalog
  implementation-catalog.yml.template              -- domain-to-implementation routing catalog
  domain-registry.yml.template                     -- domain governance registry
  solution-index.yml.template                      -- solution scope manifest
  initiative-pipeline.yml.template                 -- portfolio pipeline source
  industry/
    domain-registry.telco.yml.template             -- telco ODA component baseline
examples/
  profile-a/                                       -- entrypoint-only example
  profile-b/                                       -- routed automation example
  profile-c/                                       -- governed enterprise example
reference/
  harness-engineering.md                           -- reference note
  machine-access-contract.md                       -- optional contract for querying canonical routing catalogs
```

## Contributing

This proposal is in draft. Feedback is welcome via issues or pull requests.

## License

This repository is licensed under Apache 2.0. See [LICENSE](LICENSE).

## Compatibility

This proposal is additive to `AGENTS.md`. It does not replace or modify the existing standard.
