# DOMAIN

Purpose: Domain architecture entrypoint for Order management (governed).

## Read First

1. This file - domain context and navigation

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
DOMAIN.md                                          <- you are here
AGENTS.md                                          <- repo-specific agent instructions
domain-implementations.yml                         <- canonical implementation catalog (implementation_id routing)
governance-state.yml                               <- governance gates + pinned refs
```

## Canonical Artifacts

- [domain-implementations.yml](domain-implementations.yml)
- [governance-state.yml](governance-state.yml)

## Routing

`implementation_id` -> `domain-implementations.yml` -> `repo.url` + `repo.paths` + optional `repo.entrypoint` + optional `repo.git_ref`

## Upstream Inputs

- Prefer `inputs/workstreams/<WORKSTREAM_ID>/` because `WORKSTREAM_ID` is the
  selector/routing key for DA startup.

## Policy

- Treat selector inputs as authoritative (`WORKSTREAM_ID`, `implementation_id`).
- Fail-closed on inactive status by default.
