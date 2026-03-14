# Core Profile

This example is the baseline conformance profile. It combines Layer A entrypoints with deterministic routing catalogs so agents and orchestration tools can resolve cross-repository targets by selector ID.

## Layout

```text
enterprise-repo/
  AGENTS.md
  ENTERPRISE.md
  initiatives.yml

solution-repo/
  AGENTS.md
  SOLUTION.md
  domain-workstreams.yml

domain-repo/
  AGENTS.md
  DOMAIN.md
  domain-implementations.yml
```

## What This Adds Beyond Layer A

- `initiatives.yml` -- routes `initiative_id` to solution repositories
- `domain-workstreams.yml` -- routes `workstream_id` to domain workstream context (`domain_id` + workstream entrypoint/ref)
- `domain-implementations.yml` -- routes `implementation_id` to repo location and optional implementation entrypoint/ref when selector-driven domain->implementation routing is used
- Bootstrap discovery mechanism (for example environment variable `EA_REPO_URL`)

## When to Use

- Organizations with automated agent orchestration across repositories.
- Teams that need deterministic, fail-closed routing between architecture levels.
