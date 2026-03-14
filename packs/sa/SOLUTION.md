# SOLUTION

Solution architecture repo entrypoint. Owns the SA baseline and routes domain workstreams to domain repos.

## Read First

1. This file - solution context and navigation

## Parent

- [ENTERPRISE](https://github.com/example-org/ea-repo/blob/main/ENTERPRISE.md)

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
architecture/
|-- solution/
|   |-- architecture-design.yml
|   |-- interface-contracts.yml
|   `-- domain-workstreams.yml                     <- workstream selector catalog
`-- requirements/
    `-- requirements.yml
```

## Canonical Artifacts

- `solution-index.yml` (machine-authoritative solution scope and repo mapping)
- `architecture/solution/domain-workstreams.yml` (workstream routing selector)

## Routing

`WORKSTREAM_ID` -> `architecture/solution/domain-workstreams.yml` -> `workstream_repo_url` + `workstream_entrypoint`

## Scope

- Solution key: `<solution-key>`
- Owners: SA: `<sa-team>`, Domains: `<domain-list>`

