# SOLUTION

Purpose: Solution architecture entrypoint for BSS Modernization (governed).

## Read First

1. This file - solution context and navigation

## Parent

- [ENTERPRISE](https://github.com/oopsyz/enterprise.md/blob/main/examples/governed/enterprise-repo/ENTERPRISE.md)

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

## Runtime Initiative Context (optional)

A routed runtime MAY materialize active initiative context as a machine-readable
handoff artifact (path and format are implementation-defined; for example
`.enterprise-md/active-initiative.json`).

## Scope

- Solution key: `bss-modernization`
- Owners: SA: `bss-architecture-team`, Domains: `order, billing`
