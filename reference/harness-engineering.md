# Harness Engineering

So instead of treating AGENTS.md as the encyclopedia, we treat it as the **table of contents**.

The repository's knowledge base lives in a structured `docs/` directory treated as the system of record. A short AGENTS.md (roughly 100 lines) is injected into context and serves primarily as a map, with pointers to deeper sources of truth elsewhere.

## In-Repository Knowledge Store Layout

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   ├── core-beliefs.md
│   └── ...
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   ├── new-user-onboarding.md
│   └── ...
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   ├── uv-llms.txt
│   └── ...
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

## Design and Architecture

Design documentation is catalogued and indexed, including verification status and a set of core beliefs that define agent-first operating principles. Architecture documentation provides a top-level map of domains and package layering. A quality document grades each product domain and architectural layer, tracking gaps over time.

## Plans as First-Class Artifacts

Plans are treated as first-class artifacts. Ephemeral lightweight plans are used for small changes, while complex work is captured in execution plans with progress and decision logs that are checked into the repository. Active plans, completed plans, and known technical debt are all versioned and co-located, allowing agents to operate without relying on external context.

This enables **progressive disclosure**: agents start with a small, stable entry point and are taught where to look next, rather than being overwhelmed up front.

## Mechanical Enforcement

We enforce this mechanically. Dedicated linters and CI jobs validate that the knowledge base is up to date, cross-linked, and structured correctly. A recurring "doc-gardening" agent scans for stale or obsolete documentation that does not reflect the real code behavior and opens fix-up pull requests.

For OpenArchitect entrypoint files, treat `ENTERPRISE.md`, `SOLUTION.md`, and `DOMAIN.md` as template-governed contracts. Keep their section structure stable and place mutable operational values in canonical linked artifacts (for example selector manifests and architecture YAML files) to avoid drift.
