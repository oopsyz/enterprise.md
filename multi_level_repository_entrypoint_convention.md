# Proposal: Multi-Level Repository Entrypoint Convention

Status: Draft
Audience: standards/community contributors, platform/tool builders, enterprise architecture teams
Scope: Multi-repository human and agent collaboration across enterprise, solution, and domain levels

## 1. Problem

`AGENTS.md` is strong for repo-local behavior, but enterprise delivery spans multiple repositories and architecture levels.
At scale, teams need:

1. Level-aware entrypoints.
2. Deterministic cross-repository routing.
3. Explicit ownership, governance, and failure behavior.

## 2. Two-Layer Model (Separable)

This proposal defines two independent layers:

1. **Layer A: Entrypoint Convention**
   1. Purpose: human/agent navigation and context discovery.
   2. Tooling dependency: none.
2. **Layer B: Routing Catalog Specification (optional)**
   1. Purpose: deterministic machine routing between levels.
   2. Tooling dependency: orchestration/runtime only.

An organization can adopt Layer A without Layer B.

## 3. Layer A: Entrypoint Convention

### 3.1 Entrypoint Files

1. `AGENTS.md` (existing agents.md standard; unchanged).
2. `ENTERPRISE.md` (enterprise-level entrypoint).
3. `SOLUTION.md` (solution-level entrypoint).
4. `DOMAIN.md` (domain-level entrypoint).

### 3.2 Entrypoint Rules

1. `AGENTS.md` remains the repo-local behavior contract.
2. The level entrypoint for a repository SHOULD exist when that level is present.
3. Entrypoints SHOULD stay concise and link to canonical machine artifacts instead of duplicating mutable data.
4. Each entrypoint MUST include one deterministic parent link when a parent level exists.
5. Each entrypoint SHOULD include child links when child levels exist.
6. If no parent or child exists, entrypoint MUST state `Not applicable`.

### 3.3 Parent Link Format

Accepted parent link forms:

1. Absolute HTTPS URL to parent entrypoint file.
2. Repository-relative path when parent is in the same repository.
3. Stable repository identifier plus path (when URL is resolved at runtime).

Identifier note:

1. A stable repository identifier SHOULD be provider-qualified and durable (for example `github:example-org/ea-repo`).
2. Example parent reference: `github:example-org/ea-repo#/ENTERPRISE.md`.

### 3.4 Minimal Entrypoint Examples

#### ENTERPRISE.md (minimal)

```markdown
# ENTERPRISE

Purpose: Enterprise portfolio entrypoint.

## Parent
Not applicable

## Children
- [SOLUTION: BSS Modernization](https://github.com/example/solution-bss/blob/main/SOLUTION.md)

## Canonical Artifacts
- initiatives.yml
- domain-registry.yml
```

#### SOLUTION.md (minimal)

```markdown
# SOLUTION

Purpose: Solution architecture entrypoint.

## Parent
- [ENTERPRISE](https://github.com/example/ea-repo/blob/main/ENTERPRISE.md)

## Children
- [DOMAIN: Order](https://github.com/example/domain-order/blob/main/DOMAIN.md)

## Canonical Artifacts
- domain-workstreams.yml
- solution-index.yml
```

#### DOMAIN.md (minimal)

```markdown
# DOMAIN

Purpose: Domain architecture entrypoint.

## Parent
- [SOLUTION](https://github.com/example/solution-bss/blob/main/SOLUTION.md)

## Children
Not applicable

## Canonical Artifacts
- implementation-catalog.yml
```

## 4. Bootstrap Discovery (Core for Routed Profiles)

For routed profiles (Profile B/C), implementations MUST provide at least one deterministic enterprise-root bootstrap mechanism:

1. Explicit startup parameter.
2. Environment variable.
3. Well-known discovery endpoint.

Implementations MUST document which mechanism is authoritative.

## 5. Layer B: Routing Catalog Specification

Path placement is intentionally implementation-defined.
This standard defines file names and semantics, not fixed directories.

### 5.1 Canonical Catalog Set

| Catalog | Level | Selector | Resolves |
|---|---|---|---|
| `initiatives.yml` | Enterprise | `initiative_id` | `solution_repo_url` |
| `domain-workstreams.yml` | Solution | `workstream_id` | `domain_repo_url` |
| `implementation-catalog.yml` | Domain | `work_item_id` or `api_id` | implementation target/path |

Format note: YAML is canonical for catalogs in this proposal. JSON is allowed for compatibility where machine pipelines already emit JSON.

### 5.2 Versioning Contract

All catalogs MUST include:

1. `spec_name`
2. `spec_version`

Version rules:

1. `MAJOR`: breaking change.
2. `MINOR`: backward-compatible additive change.
3. `PATCH`: backward-compatible clarification/fix.

Runtime behavior:

1. Consumers MUST fail closed on unknown `MAJOR` versions.
2. Producers MUST provide migration notes when incrementing `MAJOR`.

### 5.3 Minimum Fields

#### initiatives.yml

```yaml
spec_name: multi-scale-routing
spec_version: "1.0.0"
initiatives:
  - initiative_id: init-example
    solution_repo_url: https://github.com/example/solution-repo
    status: active
```

#### domain-workstreams.yml

```yaml
spec_name: multi-scale-routing
spec_version: "1.0.0"
workstreams:
  - workstream_id: ws-init-example-order
    initiative_id: init-example
    domain_id: order
    domain_repo_url: https://github.com/example/order-domain-repo
    status: active
```

#### implementation-catalog.yml

```yaml
spec_name: multi-scale-routing
spec_version: "1.0.0"
work_items:
  - work_item_id: job-order-api-001
    api_id: ORDER_API
    repo_path: src/order
    status: active
```

### 5.4 Status Vocabulary (Normative)

Allowed values:

1. `active`
2. `approved`
3. `ready`
4. `in_progress`
5. `paused`
6. `completed`
7. `archived`
8. `deprecated`

Semantics:

1. `active`: routable.
2. `approved`: not routable by default; work has been authorized but not yet started.
3. `ready`: not routable by default; work is staged and ready to begin.
4. `in_progress`: routable; work is actively underway.
5. `paused`: non-routable by default; resumable by policy.
6. `completed`: read-only historical.
7. `archived`: historical, usually not in active selector views.
8. `deprecated`: read-only tombstone; never routable for write operations.

Routable by default: `active`, `in_progress`.

Implementations MAY extend the routable set to include `approved` and/or `ready` by explicit configuration.

### 5.5 Routing Policy

1. Fail closed on missing selector ID.
2. Fail closed on ambiguous selector ID.
3. Fail closed on non-routable status by default.

## 6. Compatibility and Alias Policy

Canonical keys:

1. `workstreams[]` + `workstream_id`
2. `work_items[]` + `work_item_id`

Migration policy:

1. Writers MUST emit canonical keys.
2. Readers SHOULD enforce canonical keys for deterministic behavior.
3. Legacy aliases are out of scope for this draft baseline.

## 7. Catalog Health Validation (Recommended CI)

Recommended CI checks:

1. Validate schema and required fields.
2. Verify selector uniqueness.
3. Verify status-policy compliance.
4. Verify referenced repository URLs are reachable with CI identity (or provider API equivalent).
5. Flag stale or inaccessible routing targets before runtime.

## 8. Ownership Model

| Artifact | Recommended owner | Primary purpose |
|---|---|---|
| `AGENTS.md` | repository owners | repo-local agent behavior contract |
| `ENTERPRISE.md` | EA | enterprise context entrypoint |
| `SOLUTION.md` | SA | solution context entrypoint |
| `DOMAIN.md` | DA | domain context entrypoint |
| `initiatives.yml` | EA/PMO | enterprise->solution routing |
| `domain-workstreams.yml` | SA | solution->domain routing |
| `implementation-catalog.yml` | DA | domain->implementation routing |
| governance state artifact | governance + level owners | stage gates and progress |

Override rule:

1. If roles are collapsed in one team/repository, ownership MUST be explicitly declared in the relevant entrypoint.

## 9. Conformance Profiles

### Profile A: Entrypoint-Only

Required:

1. `AGENTS.md`
2. At least one applicable level entrypoint (`ENTERPRISE.md`, `SOLUTION.md`, or `DOMAIN.md`)

### Profile B: Routed Automation

Required:

1. Profile A
2. deterministic bootstrap discovery mechanism
3. routing catalogs for level boundaries present:
   1. enterprise->solution: `initiatives.yml`
   2. solution->domain: `domain-workstreams.yml`
   3. domain->implementation: `implementation-catalog.yml` (or compatible JSON form)

### Profile C: Governed Enterprise

Required:

1. Profile B
2. domain governance registry (for example `domain-registry.yml`)
3. solution scope/index manifest (for example `solution-index.yml`)
4. governance state artifact with minimum fields:
   1. `spec_name`
   2. `spec_version`
   3. `layers` (dict keyed by cascade layer name, each with `status`)

Governance layer status values are separate from the routing status vocabulary in Section 5.4. Allowed governance layer statuses: `not_started`, `in_progress`, `proposed`, `approved`, `blocked`, `rejected`.

Minimal example:

```yaml
spec_name: governance-state
spec_version: "1.0.0"
layers:
  requirements:
    status: approved
    approved_by: product-owner
    approved_at: "2026-02-28T10:00:00Z"
  solution_architecture:
    status: in_progress
  domain_architecture:
    status: not_started
```

## 10. Conflict Resolution and Precedence

Precedence by concern:

1. Agent behavior/security constraints: `AGENTS.md` wins.
2. Routing and target resolution: routing catalogs win.
3. Narrative/context descriptions: level entrypoint (`ENTERPRISE.md`/`SOLUTION.md`/`DOMAIN.md`) wins.

If two artifacts conflict within the same concern domain:

1. Runtime MUST fail closed.
2. Runtime MUST emit a structured conflict error event.

## 11. Observability and Error Model (Companion Guidance, Non-Normative)

Minimum structured failure record SHOULD include:

1. `timestamp`
2. `level` (enterprise/solution/domain)
3. `selector_type`
4. `selector_id`
5. `artifact_path`
6. `error_code`
7. `message`

Recommended error codes:

1. `ERR_SELECTOR_MISSING`
2. `ERR_SELECTOR_AMBIGUOUS`
3. `ERR_SELECTOR_NOT_ROUTABLE`
4. `ERR_TARGET_UNREACHABLE`
5. `ERR_ACCESS_DENIED`
6. `ERR_PARENT_LINK_MISSING`
7. `ERR_CONFLICT`

## 12. Partial Adoption Patterns

### 12.1 Single-Level Repository

1. Use `AGENTS.md` plus one level entrypoint.
2. Routing catalogs are optional.

### 12.2 Two-Level (Solution + Domain)

1. Use `SOLUTION.md` and `DOMAIN.md`.
2. Use routing catalogs only for boundaries that exist.
3. `ENTERPRISE.md` and `initiatives.yml` are optional.

### 12.3 Three-Level (Enterprise + Solution + Domain)

1. Use full Layer A + Layer B for end-to-end deterministic routing.

## 13. Discovery and Traversal

Top-down routing:

1. `initiative_id` -> `initiatives.yml` -> solution repository
2. `workstream_id` -> `domain-workstreams.yml` -> domain repository
3. `work_item_id`/`api_id` -> `implementation-catalog.yml` -> implementation target

Bottom-up discovery:

1. Domain agent reads `DOMAIN.md` parent link to `SOLUTION.md`.
2. Solution agent reads `SOLUTION.md` parent link to `ENTERPRISE.md`.
3. Agents use shared IDs (`initiative_id`, `workstream_id`, `domain_id`) for lineage reconstruction.

## 14. Companion Guidance: Agent Context Engineering (Non-Normative)

Recommended harness/context practices:

1. Treat entrypoint files as maps, not encyclopedias.
2. Keep detailed knowledge in linked artifacts/docs.
3. Use progressive disclosure.
4. Add mechanical doc freshness checks in CI.

## 15. Compatibility with agents.md

This proposal is additive:

1. `AGENTS.md` remains the base standard and is not replaced.
2. `ENTERPRISE.md`/`SOLUTION.md`/`DOMAIN.md` extend navigation for multi-scale repositories.
3. Routing catalogs are optional outside routed profiles.

## 16. Reference Layout (Illustrative)

```text
<enterprise-repo>/
  AGENTS.md
  ENTERPRISE.md
  initiatives.yml
  domain-registry.yml

<solution-repo>/
  AGENTS.md
  SOLUTION.md
  domain-workstreams.yml
  solution-index.yml

<domain-repo>/
  AGENTS.md
  DOMAIN.md
  implementation-catalog.yml
  governance-state.yml
```

## 17. Reference Implementation Mapping (Non-Normative)

An implementation MAY map catalogs into architecture folders, for example:

1. `architecture/portfolio/initiatives.yml`
2. `architecture/solution/domain-workstreams.yml`
3. `implementation-catalog.json` or `implementation-catalog.yml`

An implementation MAY use environment bootstrap variables (for example `OPENARCHITECT_EA_REPO_URL`) as its concrete bootstrap mechanism.

## 18. Next Step

Submit as an extension proposal:

1. Core extension: multi-scale entrypoint convention.
2. Optional extension: routing catalog specification.
3. Companion extension: schema conformance profile and migration guidance.
4. Companion guidance: harness/context engineering practices.
