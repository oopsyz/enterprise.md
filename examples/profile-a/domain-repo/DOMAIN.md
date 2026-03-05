# DOMAIN

Purpose: Domain architecture entrypoint for Order management.

## Read First

1. This file - domain context and navigation

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
DOMAIN.md                                          <- you are here
AGENTS.md                                          <- repo-specific agent instructions
```

## Canonical Artifacts

Not applicable (Profile A - entrypoint-only)

## Routing

Not applicable

## Upstream Inputs

Not applicable

## Policy

- Treat selector inputs as authoritative (`WORKSTREAM_ID`, `WORK_ITEM_ID`).
- Fail-closed on inactive status by default.
