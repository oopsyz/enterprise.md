# Brownfield Adoption Guide

This document provides a pragmatic adoption path for existing enterprise estates. It is non-normative guidance that complements the specification.

## When to Use This Guide

Use this guide when:

1. the organization already has multiple repositories
2. some repos are legacy or third-party managed
3. the architecture levels are unevenly documented
4. the team wants deterministic routing without a repo reorganization first

## Four-Step Adoption Path

### 1. Identify the Topmost Level Present

Determine the highest architecture level that actually exists in your operating model today:

1. enterprise plus solution plus domain
2. solution plus domain
3. a single domain-only repository

Adopt the convention from that highest real level downward. Do not create placeholder enterprise layers if the organization does not operate that way.

### 2. Add Entrypoints First

Create `AGENTS.md` plus the applicable level entrypoint before adding catalogs:

1. `ENTERPRISE.md` for enterprise context
2. `SOLUTION.md` for solution context
3. `DOMAIN.md` for domain context

Keep these entrypoints short. They should establish:

1. the architectural purpose of the repo
2. the canonical artifacts to read next
3. the ownership boundary for the repo

For Domain repos, make the bounded context explicit in `AGENTS.md`.

### 3. Add Catalogs Only for Boundaries That Exist

Do not adopt all catalogs at once unless the operating model needs them:

1. add `initiatives.yml` only when enterprise-to-solution routing exists
2. add `domain-workstreams.yml` only when solution-to-domain routing exists
3. add `domain-implementations.yml` only when selector-driven domain-to-implementation routing is needed

This keeps the initial rollout small while preserving the convention's fail-closed semantics.

### 4. Validate and Tighten Routing

Once the initial entrypoints and catalogs exist:

1. run `python skills/ea-convention/scripts/validate_convention.py --root .`
2. remove heuristic routing behavior from tooling and prompts
3. add CI so invalid selectors and broken references fail before runtime
4. add a separate Markdown link check for documentation integrity

The goal is to move from best-effort navigation to deterministic routing one boundary at a time.

## What To Do With Legacy Repositories

### External or Third-Party Repositories

If the implementation repo is not owned by the team, keep the authoritative routing in the Domain repo:

1. register the external target in `domain-implementations.yml`
2. use `repo.entrypoint` when the target repo does not implement this convention
3. use `repo.git_ref` when the architecture depends on a specific release, branch, or commit

This preserves deterministic navigation without requiring the external repo to adopt the convention.

### Repositories Without Entrypoints

If a target repo has no `AGENTS.md`, `ENTERPRISE.md`, `SOLUTION.md`, or `DOMAIN.md`:

1. do not infer ownership from the repo name alone
2. route to the exact file identified by the authoritative catalog
3. treat the owning higher-level artifact as the architecture contract until the target repo adopts local entrypoints

### Monorepos

If multiple implementations live in one repository:

1. keep `repo.url` omitted when the catalog lives in the same repo
2. use non-overlapping `repo.paths` to define deterministic implementation scope
3. set `repo.entrypoint` for the exact subtree the agent should open first

### Repositories With Partial Adoption

Some estates will mix adopted and non-adopted repos for a long time. In that case:

1. keep the canonical routing data in the adopted layer
2. avoid adding shadow registries in local team documents
3. prefer explicit pointers over broad migration programs

## Practical Rollout Pattern

A common brownfield rollout sequence is:

1. start with one Domain repo and one implementation target
2. add `domain-implementations.yml` and validate the traversal
3. add a Solution repo with `domain-workstreams.yml`
4. add enterprise-level routing only when portfolio-level resolution is needed

This sequence lets the organization prove value early without a large central migration.

## Exit Criteria For Initial Adoption

The first brownfield phase is complete when:

1. every adopted repo starts with `AGENTS.md` and the appropriate level entrypoint
2. every routed boundary in scope has a canonical catalog
3. validator failures block broken routing changes
4. agents can traverse from the starting selector to the target artifact without repo-name heuristics
