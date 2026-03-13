# AGENTS

## Identity

This repository hosts the **Multi-Level Repository Navigation and Routing Convention** - a standards proposal extending `AGENTS.md` to enterprise-scale, multi-repository delivery.

## Navigation

- [README.md](README.md) - overview, quick start, contributing
- [enterprise_repo_convention.md](enterprise_repo_convention.md) - full proposal specification
- [templates/](templates/) - starter templates for adoption (entrypoints, catalogs, AGENTS roles, industry baselines)
- [examples/](examples/) - working examples for each conformance profile

## Key Concepts

This proposal defines:

1. **Level entrypoints**: `ENTERPRISE.md`, `SOLUTION.md`, `DOMAIN.md` - extend `AGENTS.md` for multi-repo navigation.
2. **Routing catalogs**: `initiatives.yml`, `domain-workstreams.yml`, `domain-implementations.yml` - deterministic machine routing between levels.
3. **Conformance profiles**: A (entrypoint-only), B (routed automation), C (governed enterprise).

## Mandatory Entrypoints

- Instruction: Always read `README.md` (mandatory entrypoint for this repository).
- Exception note: This repository intentionally has no root `DOMAIN.md`; `README.md` is the visitor-friendly entrypoint here.

## Behavior

- This is a specification repository, not a runtime system.
- Do not modify example files as if they were live configuration.
- When referencing the proposal, link to the canonical file, not to inline quotes.
- Treat section numbers as stable identifiers within a spec version.
