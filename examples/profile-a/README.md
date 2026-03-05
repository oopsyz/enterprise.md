# Profile A: Entrypoint-Only

This example shows the minimum adoption: `AGENTS.md` plus level entrypoints with deterministic upstream parent links. No routing catalogs or tooling required.

## Layout

```
enterprise-repo/
  AGENTS.md
  ENTERPRISE.md

solution-repo/
  AGENTS.md
  SOLUTION.md

domain-repo/
  AGENTS.md
  DOMAIN.md
```

## When to Use

- Teams exploring multi-repo navigation without automation.
- Organizations that want agent-readable context across levels.
- First step before adopting routing catalogs (Profile B).
