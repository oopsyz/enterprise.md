# Codex App Integration Notes

This folder captures how the `enterprise.md` convention fits a Codex-style product experience.

It is intentionally separate from the core standard:

1. the standard defines the navigation and routing convention
2. these notes describe one practical implementation model on top of Codex

## Contents

- [ecosystem-positioning.md](ecosystem-positioning.md) - standards positioning and ecosystem diagram
- [official-codex-surfaces-and-fit.md](official-codex-surfaces-and-fit.md) - how the convention maps to official Codex surfaces
- [worker-container-to-codex-mapping.md](worker-container-to-codex-mapping.md) - how the current `worker_container` approach maps into a Codex-based experience
- [codex-threads-context-and-progressive-disclosure.md](codex-threads-context-and-progressive-disclosure.md) - how isolated Codex threads can still coordinate through canonical Git artifacts
- [resolve-codex-git-target-contract.md](resolve-codex-git-target-contract.md) - a proposed resolver contract for Codex-facing deterministic routing

## Core Position

The convention is implementable in a Codex-style app, but it should be treated as a navigation and routing layer on top of Codex, not as a change to Codex's reasoning model.

## Progressive Disclosure Summary

`enterprise.md` applies progressive disclosure to multi-repo AI workflows. Instead of loading all enterprise, solution, domain, and implementation context into one place, it reveals only the next correct layer of information at each step: first the correct architecture level, then the correct repository, then the correct entrypoint, and only then the deeper canonical artifacts needed for the task. `AGENTS.md`, `ENTERPRISE.md`, `SOLUTION.md`, and `DOMAIN.md` provide human and agent navigation at the right level of abstraction, while selector catalogs such as `initiatives.yml`, `domain-workstreams.yml`, and `implementation-catalog.yml` provide deterministic machine routing when deeper traversal is required. This allows isolated Codex threads to coordinate through shared Git artifacts without requiring shared in-memory thread context, while preserving clarity, auditability, and fail-closed behavior.

## Reusable Positioning Copy

### Design-Doc Version

`enterprise.md` applies progressive disclosure to multi-repo AI workflows. Instead of loading all enterprise, solution, domain, and implementation context into one place, it reveals only the next correct layer of information at each step: first the correct architecture level, then the correct repository, then the correct entrypoint, and only then the deeper canonical artifacts needed for the task. `AGENTS.md`, `ENTERPRISE.md`, `SOLUTION.md`, and `DOMAIN.md` provide human and agent navigation at the right level of abstraction, while selector catalogs such as `initiatives.yml`, `domain-workstreams.yml`, and `implementation-catalog.yml` provide deterministic machine routing when deeper traversal is required. This allows isolated Codex threads to coordinate through shared Git artifacts without requiring shared in-memory thread context, while preserving clarity, auditability, and fail-closed behavior.

### Marketing Version

`enterprise.md` gives AI teams a clean way to work across enterprise, solution, domain, and implementation repos without dumping everything into one giant context. It progressively reveals only the next level that matters: the right layer, the right repo, the right entrypoint, and then the exact canonical artifacts needed to continue. The result is a multi-repo workflow that stays deterministic, auditable, and understandable for both humans and AI.

### Tagline Version

`enterprise.md` brings progressive disclosure to multi-repo AI work: the right level, the right repo, the right entrypoint, at the right time.
