# DOMAIN

Purpose: Domain architecture entrypoint for Order management.

## Read First

1. This file - domain context and navigation

## Parent

- [ENTERPRISE](https://github.com/oopsyz/enterprise.md/blob/main/examples/core/enterprise-repo/ENTERPRISE.md)

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
domain-implementations.yml                         <- canonical implementation catalog (implementation_id routing)
```

## Canonical Artifacts

- [domain-implementations.yml](domain-implementations.yml)

## Routing

`implementation_id` -> `domain-implementations.yml` -> `repo.url` + `repo.paths` + optional `repo.entrypoint` + optional `repo.git_ref`

## Upstream Inputs

Not applicable

## Policy

- Treat selector inputs as authoritative (`WORKSTREAM_ID`, `implementation_id`).
- Fail-closed on inactive status by default.
