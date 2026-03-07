# AGENTS

## Identity

This repository hosts the **Multi-Level Repository Navigation and Routing Convention** - a standards proposal extending `AGENTS.md` to enterprise-scale, multi-repository delivery.

## Navigation

- [README.md](README.md) - overview, quick start, contributing
- [multi_level_repository_navigation_and_routing_convention.md](multi_level_repository_navigation_and_routing_convention.md) - full proposal specification
- [templates/](templates/) - starter templates for adoption (entrypoints, catalogs, AGENTS roles, industry baselines)
- [examples/](examples/) - working examples for each conformance profile
- [reference/codex-app-integration/](reference/codex-app-integration/) - Codex-oriented implementation notes

## Key Concepts

This proposal defines:

1. **Level entrypoints**: `ENTERPRISE.md`, `SOLUTION.md`, `DOMAIN.md` - extend `AGENTS.md` for multi-repo navigation.
2. **Routing catalogs**: `initiatives.yml`, `domain-workstreams.yml`, `implementation-catalog.yml` - deterministic machine routing between levels.
3. **Conformance profiles**: A (entrypoint-only), B (routed automation), C (governed enterprise).

## Behavior

- This is a specification repository, not a runtime system.
- Do not modify example files as if they were live configuration.
- When referencing the proposal, link to the canonical file, not to inline quotes.
- Treat section numbers as stable identifiers within a spec version.
