# Symphony Integration with enterprise.md

## Purpose

This document describes how [OpenAI Symphony](https://github.com/openai/symphony) fits into the enterprise.md multi-level routing convention. Symphony is a long-running automation daemon that orchestrates coding agents against issue tracker work items. The enterprise.md convention is a declarative multi-repository routing model that governs what gets built and where work is routed. They are complementary: the convention provides governance and routing; Symphony provides DEV-layer execution.

## Layer Mapping

The enterprise.md convention defines three architecture levels and one execution role:

| Level | Concern | Canonical Artifact | Owner |
| ------- | --------- | ------------------- | ------- |
| EA | Portfolio governance | `initiatives.yml` | Enterprise architect |
| SA | Solution decomposition, domain routing | `domain-workstreams.yml` | Solution architect |
| DA | Domain planning, implementation targeting | `domain-implementations.yml` | Domain architect |
| DEV | Code-level execution | Implementation repo artifacts | Developer / coding agent |

Symphony operates exclusively at the DEV layer. It runs inside the implementation repos that `domain-implementations.yml` points to — not inside domain repos, solution repos, or enterprise repos. Those higher layers are governance artifacts; they contain no application code.

## Where Symphony Runs

```text
DA domain repo (governance)              Implementation repos (code)
da/{domain}/                             next-ai-draw-io/
  domain-implementations.yml               WORKFLOW.md        <-- Symphony config
    - implementation_id: next-ai-draw-io    src/
      repo.url: .../next-ai-draw-io         ...
      status: active
    - implementation_id: some-service      some-service/
      repo.url: .../some-service             WORKFLOW.md      <-- Symphony config
      status: active                         src/
                                             ...
```

Each implementation repo listed in `domain-implementations.yml` can independently run its own Symphony instance. The domain repo declares *what* is being built. Symphony, running in each target repo, handles *how* coding agents execute against it.

## Demand Flow

The convention routes demand top-down through declarative artifacts. Symphony consumes demand at the bottom of this chain via an issue tracker.

```text
EA: initiatives.yml
 |  initiative_id selects solution_repo_url
 v
SA: domain-workstreams.yml
 |  workstream_id routes demand to a domain
 v
DA: domain-implementations.yml
 |  implementation_id resolves to repo_url
 v
Issue tracker (Linear, GitHub Issues, etc.)
 |  issues created against the implementation repo
 v
Symphony: WORKFLOW.md in implementation repo
 |  polls tracker, dispatches coding agents per issue
 v
Coding agent executes in isolated per-issue workspace
```

The bridge between convention artifacts and Symphony is the issue tracker. Convention artifacts express architectural intent; issues express actionable work items. The translation from one to the other can be:

- Manual: a PM or domain architect reads `domain-workstreams.yml` and creates issues
- Automated: a CI pipeline or intake agent reads convention artifacts and generates tracker issues
- Hybrid: convention artifacts inform planning; humans refine and file issues

Symphony does not need to read convention artifacts directly. It only needs issues in its configured tracker.

## Artifact Alignment

| enterprise.md Artifact | Symphony Artifact | Relationship |
| ------------------------ | ------------------- | ------------- |
| `domain-implementations.yml` | — | Points to repos where Symphony runs |
| `domain-workstreams.yml` | — | Demand signals that become tracker issues |
| — | `WORKFLOW.md` | Per-repo execution config; lives in implementation repo |
| `AGENTS.md` (DEV level) | `WORKFLOW.md` prompt body | Both define agent behavior; `AGENTS.md` is navigation, `WORKFLOW.md` is execution policy |
| `DOMAIN.md` | — | Domain context; Symphony does not read it directly |

### AGENTS.md and WORKFLOW.md

Both files guide agent behavior but at different scopes:

- `AGENTS.md` (convention): tells an agent *how to navigate* the repo — what to read first, what role to assume, what guardrails apply. It is a static navigation contract.
- `WORKFLOW.md` (Symphony): tells the orchestrator *how to run* agent sessions — polling config, concurrency limits, workspace hooks, prompt template per issue. It is a runtime execution contract.

They do not conflict. A Symphony-managed agent session can still read `AGENTS.md` as part of its prompt context. The `WORKFLOW.md` Liquid template can reference `AGENTS.md` content:

```md
---
agent:
  max_concurrent_agents: 5
codex:
  approval_policy: suggest
---

Read `AGENTS.md` first to understand repo conventions.

## Issue

**{{ issue.identifier }}**: {{ issue.title }}

{{ issue.description }}
```

## Topology Scenarios

### Single domain, multiple implementations

One domain architect governs several repos. Each runs its own Symphony instance.

```text
da/payments/domain-implementations.yml
  - payment-api/       → WORKFLOW.md (Symphony, Linear project: PAYMENTS-API)
  - payment-gateway/   → WORKFLOW.md (Symphony, Linear project: PAYMENTS-GW)
```

Each Symphony instance polls its own tracker project. The domain architect coordinates across them through `domain-implementations.yml` and the roadmap.

### Multiple workstreams, one implementation

Two SA-level workstreams route demand to the same domain and the same implementation repo. Symphony sees this as multiple issues in the same tracker project. It does not need to know which workstream generated which issue — that traceability lives in the convention artifacts and optionally in issue labels.

### No EA or SA layer

A standalone team with only DA and DEV layers. `domain-implementations.yml` still points to repos. Symphony still runs in those repos. The absence of higher layers does not affect Symphony's operation — it only needs a tracker and a `WORKFLOW.md`.

## What Symphony Does Not Replace

Symphony is an execution-layer runtime. It does not replace any convention-level concern:

| Concern | Handled by | Not by |
| --------- | ----------- | -------- |
| Portfolio prioritization | EA (`initiatives.yml`) | Symphony |
| Solution decomposition and routing | SA (`domain-workstreams.yml`) | Symphony |
| Domain planning and implementation targeting | DA (`domain-implementations.yml`) | Symphony |
| Repo navigation and agent onboarding | `AGENTS.md` at each level | Symphony |
| Cross-repo referential integrity | Convention validator | Symphony |
| Per-issue agent orchestration | Symphony | Convention artifacts |
| Workspace isolation and concurrency | Symphony | Convention artifacts |
| Retry, stall detection, reconciliation | Symphony | Convention artifacts |

## Integration Checklist

For a domain architect adding Symphony to an existing enterprise.md-governed implementation:

1. Confirm the repo is listed in `domain-implementations.yml` with `status: active`
2. Create `WORKFLOW.md` in the implementation repo root
3. Configure the tracker project in `WORKFLOW.md` front matter
4. Ensure `AGENTS.md` exists at the DEV level in the implementation repo (convention requirement)
5. Optionally reference `AGENTS.md` in the `WORKFLOW.md` prompt template
6. Start the Symphony daemon pointing at the repo

No changes to EA, SA, or DA artifacts are required. Symphony is additive at the DEV layer.

## Implementation Considerations

These are deployment-specific decisions, not convention-level concerns. The convention defines routing and governance; these items fall on the execution side of that boundary.

1. **Issue generation from convention artifacts.** An org may choose to build a pipeline (script, CI action, intake agent) that reads `domain-workstreams.yml` and creates tracker issues. This closes the gap between convention demand signals and Symphony's issue-driven model but is not required by the convention.

2. **Status feedback.** Symphony knows when an issue succeeds, fails, or stalls. An org may choose to write execution status back into `domain-implementations.yml` fields, or treat the tracker as the single source of execution truth. Either approach is convention-compliant.

3. **Multi-repo Symphony coordination.** When multiple implementation repos under the same domain all run Symphony, each instance operates independently. A domain-level orchestrator across them is an optional operational choice, not a convention requirement.
