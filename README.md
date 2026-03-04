# enterprise.md

A proposal for multi-level repository entrypoint conventions that extend `AGENTS.md` to enterprise-scale, multi-repository delivery.

## Status

**Draft** — open for feedback.

## Problem

`AGENTS.md` works well for single-repository agent behavior, but enterprise delivery spans multiple repositories across architecture levels (enterprise, solution, domain). Teams need level-aware entrypoints, deterministic cross-repository routing, and explicit ownership and governance.

## What This Proposes

Two independent, separable layers:

| Layer | Purpose | Requires tooling? |
|---|---|---|
| **Layer A: Entrypoint Convention** | Human/agent navigation via `ENTERPRISE.md`, `SOLUTION.md`, `DOMAIN.md` | No |
| **Layer B: Routing Catalog Specification** | Deterministic machine routing between levels via YAML catalogs | Orchestration/runtime only |

Organizations can adopt Layer A without Layer B.

## Conformance Profiles

| Profile | What you need |
|---|---|
| **A: Entrypoint-Only** | `AGENTS.md` + at least one level entrypoint |
| **B: Routed Automation** | Profile A + bootstrap discovery + routing catalogs |
| **C: Governed Enterprise** | Profile B + governance registry + governance state artifact |

See [examples/](examples/) for working samples of each profile.

## Quick Start

1. Read the [full proposal](multi_level_repository_entrypoint_convention.md).
2. Pick a conformance profile that fits your organization.
3. Copy the matching example from [examples/](examples/) into your repositories.
4. Customize entrypoints and catalogs for your actual repos and teams.

## Repository Contents

```
README.md                                          — this file
AGENTS.md                                          — agent navigation for this repo
multi_level_repository_entrypoint_convention.md    — the full proposal
examples/
  profile-a/                                       — entrypoint-only example
  profile-b/                                       — routed automation example
  profile-c/                                       — governed enterprise example
```

## Contributing

This proposal is in draft. Feedback is welcome via issues or pull requests.

## Compatibility

This proposal is additive to `AGENTS.md`. It does not replace or modify the existing standard.
