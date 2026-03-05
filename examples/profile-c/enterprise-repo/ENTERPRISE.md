# ENTERPRISE

Purpose: Enterprise portfolio entrypoint for Acme Corp (governed).

## Read First

1. This file - enterprise context and navigation

## Parent

Not applicable

## Critical File Contract

- Keep required section headings from this template.
- Do not rename or delete required sections.
- Keep this file concise: identity, routing semantics, and links.
- Put detailed/mutable operational values in canonical artifacts and link them here.
- If a required section has no content, keep it and write `Not applicable`.

## Knowledge Store Layout

```text
ENTERPRISE.md                             <- you are here
AGENTS.md                                 <- repo-specific agent instructions
initiatives.yml                           <- selector catalog (INITIATIVE_ID routing)
domain-registry.yml                       <- domain governance registry
```

## Canonical Artifacts

- [initiatives.yml](initiatives.yml)
- [domain-registry.yml](domain-registry.yml)

## Routing

`INITIATIVE_ID` -> `initiatives.yml` -> `solution_repo_url` + `solution_entrypoint`

## Policy

- Active-only routing; fail-closed on non-active status.
- Resolve solution targets from `initiatives.yml` (canonical routing source).
