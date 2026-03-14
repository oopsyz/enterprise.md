# DOMAIN

Domain architecture repo entrypoint. Owns domain design baselines and routes to implementation repos via the domain implementations catalog.

## Read First

1. This file - domain context and navigation

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
DOMAIN.md                                          <- you are here
AGENTS.md                                          <- repo-specific agent instructions
domain-implementations.yml                         <- canonical implementation catalog
architecture/
`-- domains/
    `-- <domain-id>/
        |-- domain-design.md
        |-- domain-design.yml
        |-- component-specs.yml
        `-- interface-contracts.yml
inputs/
`-- workstreams/
    `-- <workstream-id>/
        |-- source.yml
        `-- artifacts/
```

## Canonical Artifacts

- `domain-implementations.yml` (implementation routing catalog)
- `architecture/domains/<domain-id>/*.yml` (domain design, component specs, interfaces)

## Routing

`implementation_id` -> `domain-implementations.yml` -> `repo.url` + `repo.paths` + optional `repo.entrypoint` + optional `repo.git_ref`

## Policy

- Treat selector inputs as authoritative (`implementation_id`).
- Fail-closed on inactive status by default.

