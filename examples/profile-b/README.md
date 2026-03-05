# Profile B: Routed Automation

This example adds deterministic routing catalogs on top of Profile A. Agents and orchestration tools can resolve cross-repository targets by selector ID.

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
  implementation-catalog.yml
```

## What's New Over Profile A

- `initiatives.yml` -- routes `initiative_id` to solution repositories
- `domain-workstreams.yml` -- routes `workstream_id` to domain repositories
- `implementation-catalog.yml` -- routes `work_item_id`/`api_id` to implementation targets when selector-driven domain->implementation routing is used
- Bootstrap discovery mechanism (for example environment variable `EA_REPO_URL`)

## When to Use

- Organizations with automated agent orchestration across repositories.
- Teams that need deterministic, fail-closed routing between architecture levels.
