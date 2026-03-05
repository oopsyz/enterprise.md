# SOLUTION

Purpose: Solution architecture entrypoint for BSS Modernization (governed).

## Read First

1. This file - solution context and navigation

## Parent

- [ENTERPRISE](https://github.com/acme/ea-repo/blob/main/ENTERPRISE.md)

## Critical File Contract

- Keep required section headings from this template.
- Do not rename or delete required sections.
- Keep this file concise: identity, routing semantics, and links.
- Put detailed/mutable operational values in canonical artifacts and link them here.
- If a required section has no content, keep it and write `Not applicable`.

## Knowledge Store Layout

```text
SOLUTION.md                                        <- you are here
AGENTS.md                                          <- repo-specific agent instructions
solution-index.yml                                 <- machine-authoritative scope manifest
domain-workstreams.yml                             <- workstream selector catalog (WORKSTREAM_ID routing)
```

## Canonical Artifacts

- [domain-workstreams.yml](domain-workstreams.yml)
- [solution-index.yml](solution-index.yml)

## Routing

`WORKSTREAM_ID` -> `domain-workstreams.yml` -> `domain_id` + `workstream_entrypoint` + `workstream_git_ref`

## SA Container Context

When running in an SA container (`OPENARCHITECT_CONTAINER_ROLE=sa`), startup routing can write:
- `.openarchitect/active-initiative.json`

## Scope

- Solution key: `bss-modernization`
- Owners: SA: `bss-architecture-team`, Domains: `order, billing`
