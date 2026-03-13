# Governed Profile

This example adds governance registries and state artifacts on top of the Core profile. It enables stage-gated delivery with explicit approval tracking across architecture layers.

## Layout

```yaml
enterprise-repo/
  AGENTS.md
  ENTERPRISE.md
  initiatives.yml
  domain-registry.yml

solution-repo/
  AGENTS.md
  SOLUTION.md
  domain-workstreams.yml
  solution-index.yml

domain-repo/
  AGENTS.md
  DOMAIN.md
  domain-implementations.yml
  governance-state.yml
```

## What's New Over Core

- `domain-registry.yml` — enterprise-level domain governance registry
- `solution-index.yml` — solution scope and index manifest
- `governance-state.yml` — per-domain governance state with layer statuses

## When to Use

- Enterprises requiring formal stage gates (requirements, architecture, implementation).
- Organizations with compliance or audit requirements for delivery governance.
- Teams that need to track approval status across architecture cascade layers.
