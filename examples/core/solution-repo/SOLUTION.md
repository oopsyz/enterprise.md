# SOLUTION

Purpose: Solution architecture entrypoint for BSS Modernization.

## Read First

1. This file - solution context and navigation

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
SOLUTION.md                                        <- you are here
AGENTS.md                                          <- repo-specific agent instructions
domain-workstreams.yml                             <- workstream selector catalog (WORKSTREAM_ID routing)
```

## Canonical Artifacts

- [domain-workstreams.yml](domain-workstreams.yml)

## Routing

`WORKSTREAM_ID` -> `domain-workstreams.yml` -> `domain_id` + `workstream_entrypoint` + `workstream_git_ref`

## SA Container Context

Not applicable

## Scope

- Solution key: `bss-modernization`
- Owners: SA: `bss-architecture-team`
