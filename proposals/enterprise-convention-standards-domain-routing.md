# Proposal: Governed Standards-Provider Routing

**Status:** Accepted for integration
**Proposer:** `oa_engine`
**Date:** 2026-07-16
**Target owner:** `enterprise.md`, the canonical owner of the Multi-Level
Repository Navigation and Routing Convention
**Related decision:** ADR-0032, Self-Contained Dispatch Workspaces

## Summary

Extend the enterprise repository convention so automation can
deterministically locate a company's governed architecture standards and
pattern corpus without introducing a second repository-location authority.

The proposal represents a standards provider as an explicit governed
registry-entry subtype in `domain-registry.yml`. An initiative selection is
authoritative when initiative context exists. In an initiative-free
deployment, a resolver invocation may select a provider directly or use the
enterprise default. The selected entry supplies its existing repository URL
and Git ref plus a standards entrypoint and machine-readable pattern-index
reference.

The proposal extends the convention's routing contract and introduces two
small supporting convention artifacts: a versioned pattern index authored by
the standards-provider owner and a versioned resolution receipt emitted by a
conforming resolver. It does not standardize any particular engine's dispatch
manifest, workspace layout, design-artifact schema, persistence mechanism, or
content-attestation mechanism.

## Problem

The convention already routes:

```text
initiative
  -> solution repository
  -> domain repository
  -> implementation repository
```

Architecture and development agents also need company-approved standards,
policies, reference architectures, and patterns. Today a tool must discover
those inputs through machine-local paths, environment variables, or
project-specific configuration. Those mechanisms are not portable,
commit-addressable, or governed by the existing routing chain.

The absence is especially visible when:

- the implementation repository is separate from the enterprise repository;
- an enterprise maintains different standards portfolios for different
  initiatives or business units;
- work runs on a remote agent without the dispatcher's local filesystem; or
- a later review must establish exactly which standards version informed a
  design.

## Design principles

1. **One authority per location fact.** Standards routing extends the existing
   convention; it does not create a parallel repository registry.
2. **Standards providers are governed registry entries.** A standards or
   industry-knowledge repository participates through `domain-registry.yml`
   without being forced to claim DA bounded-context semantics, including when
   its content happens to live in the EA repository.
3. **Governed initiative selection.** When initiative context exists, its
   standards selection is authoritative and runtime overrides are rejected.
   Without initiative context, an explicit resolver selection may override the
   enterprise default.
4. **Refs become immutable at execution time.** Catalogs may name governed Git
   refs such as `main`; consuming runtimes resolve and record an immutable
   commit SHA before use.
5. **Fail closed when required.** If an automation declares standards as a
   required input and no valid standards source resolves, it must not silently
   continue without standards.
6. **Versioned migration.** Existing catalogs remain valid as
   `domain-registry` 1.x artifacts, but this extension is a deliberate
   `domain-registry` 2.0 contract because standards-only rows are unsafe for
   1.x consumers. Migration and fail-closed version behavior are defined
   below.

## Proposed catalog fields

The names below are proposed as a concrete minimal contract. The convention
owner may adjust naming while preserving the semantics and integrity rules.

### `domain-registry.yml`

`domain-registry.yml` advances to `spec_version: "2.0.0"`. Every 2.x registry
row has a required `entry_type` discriminator:

| `entry_type` | Meaning | Workstream target | Standards source |
| --- | --- | --- | --- |
| `domain` | DA bounded context only | yes | no |
| `standards_provider` | Governed standards source only | no | yes |
| `both` | DA bounded context that also publishes standards | yes | yes |

This discriminator prevents a standards-only entry from masquerading as a DA
domain merely because it has a `domain_id` inside the existing `domains`
collection. The collection and stable identifier names remain unchanged for
backward-compatible registry addressing, but validator and resolver semantics
are subtype-aware:

- `domain-workstreams.yml[].domain_id` may reference only `entry_type: domain`
  or `entry_type: both`;
- standards selection may reference only `entry_type: standards_provider` or
  `entry_type: both`; and
- a 2.x row without `entry_type` is invalid.

The major version is intentional. A 1.x consumer treats every `domains[]`
entry as a workstream-addressable bounded domain and cannot safely interpret a
standards-only row. Per the convention version contract, 1.x consumers MUST
fail closed on the unknown 2.x major rather than accept or misroute it.

A row that provides governed standards carries a single nested
`standards_provider` object. This is deliberately **not** the
existing nested `standards` object on a domain row — that object declares the
frameworks and policies a domain *is itself governed by*; `standards_provider`
declares that this domain *supplies* standards/patterns to others. Keeping
them as two distinct nested objects avoids two conflicting meanings of
"standards" on one row (rev. finding 5).

| Field (under `standards_provider`) | Type | Meaning |
| --- | --- | --- |
| `enterprise_default` | boolean, optional | `true` designates this provider as the enterprise fallback; omitted means `false`. |
| `entrypoint` | non-empty string | Repository-relative standards navigation entrypoint; see the contract below. |
| `pattern_index_ref` | non-empty string | Repository-relative path to the default machine-readable pattern index (see "Pattern-index contract"). |

Object presence indicates standards-provider capability; there is no
`enabled` switch. If `standards_provider` is present, `entrypoint` and
`pattern_index_ref` are required; `enterprise_default` is optional and
defaults to `false`. Routability is controlled by `entry_type` and the row's
`status`.

**Subtype semantics (rev. finding 6).** An `entry_type:
standards_provider` row is not a bounded context in the DA sense. It supplies
reference content and does not carry domain-owned runtime invariants,
interfaces, implementations, or DA design gates. It uses
`standards_provider.entrypoint` and omits `domain_entrypoint`. An `entry_type:
both` row satisfies the complete existing `DOMAIN.md` bounded-context contract
and adds `standards_provider` independently.

Example:

```yaml
domains:
  - domain_id: architecture-standards
    name: Architecture Standards and Patterns
    owner: enterprise-architecture
    entry_type: standards_provider
    domain_repo_url: https://github.com/example/enterprise-standards.git
    domain_git_ref: main
    status: active
    standards_provider:
      enterprise_default: true
      entrypoint: STANDARDS.md
      pattern_index_ref: architecture/patterns/index.yml
```

If standards content lives inside the EA repository, the row uses the EA
repository URL normally — this remains one registry authority; colocating the
content does not create a special EA-repository lookup rule:

```yaml
domains:
  - domain_id: architecture-standards
    name: Architecture Standards and Patterns
    owner: enterprise-architecture
    entry_type: standards_provider
    domain_repo_url: https://github.com/example/enterprise-architecture.git
    domain_git_ref: main
    status: active
    standards_provider:
      enterprise_default: true
      entrypoint: architecture/standards/STANDARDS.md
      pattern_index_ref: architecture/standards/patterns/index.yml
```

### Standards entrypoint contract

`standards_provider.entrypoint` is a governed navigation document, not the
machine routing target for individual patterns. The pattern index is the
machine contract. The entrypoint provides human and agent context and MUST:

- exist at the selected repository and resolved commit;
- identify the provider purpose and owner;
- link to the provider's default
  `standards_provider.pattern_index_ref`;
- explain that approved alternate indexes may be selected by an
  initiative-owned selection or by an explicit resolver only when there is no
  initiative context, and that the resolution receipt identifies the actual
  effective index;
- explain publication/approval ownership for the corpus; and
- identify escalation contact or process for disputed or missing guidance.

Recommended headings are `Purpose`, `Ownership`, `Pattern Index`,
`Publication Policy`, and `Escalation`.

Repository instruction behavior remains unchanged:

1. a standards-provider repository MUST contain a root `AGENTS.md`;
2. after opening the provider repository, a consumer reads that `AGENTS.md`
   first;
3. it then reads `standards_provider.entrypoint` for standards navigation;
4. `AGENTS.md` remains the repository behavior/instruction authority;
5. the standards entrypoint supplies governed content and navigation but may
   not override repository instructions; and
6. a conflict is reported to the provider owner rather than resolved through
   implicit precedence.

Repository `AGENTS.md` SHOULD link to the standards entrypoint for human
discoverability, but deterministic machine navigation comes from the registry
field and does not depend on that link.

**Routable status (rev. finding 7, normative).** A standards provider is
routable only when its row `status` is `active`. This is intentionally
stricter than the convention's general `active`+`in_progress` routability:
standards that inform a design must be published and stable, not
in-progress. An `in_progress` provider is not resolvable as a standards
source.

### `initiatives.yml`

Add these optional properties to an initiative row:

| Field | Type | Meaning |
| --- | --- | --- |
| `standards_domain_id` | non-empty string | Selects the applicable standards-provider domain. |
| `pattern_index_ref` | non-empty string | Optional repository-relative override of that domain's default pattern index. |

Example:

```yaml
initiatives:
  - initiative_id: init-bss-modernization
    name: BSS Modernization
    solution_repo_url: https://github.com/example/bss-modernization.git
    solution_entrypoint: SOLUTION.md
    solution_git_ref: main
    status: active
    owner: sa-team-a
    standards_domain_id: telco-architecture-standards
    pattern_index_ref: portfolios/telco/patterns/index.yml
```

## Resolution algorithm

The convention supports deployments **with or without** an initiative — a
Solution+Domain deployment need not have `initiatives.yml` (rev. finding 1).
Initiative context is derived from the governed work binding, not from a
caller-controlled option: when the work item, solution, or dispatch is bound
to an initiative, the consumer MUST supply that initiative to the resolver and
the resolver MUST NOT permit the caller to suppress it. Standards resolution
therefore has an initiative-independent path only for work that is genuinely
not initiative-bound:

1. **If initiative context exists**, reject any explicit resolver
   `standards_domain_id` or `pattern_index_ref`. Select the initiative's
   `standards_domain_id` when present; otherwise select the enterprise default.
   The initiative catalog remains the governed authority for that work.
2. **If no initiative context exists and the resolver supplies an explicit
   `standards_domain_id`**, select that provider. An explicit
   `pattern_index_ref` is permitted only with this initiative-free explicit
   selection.
3. **Otherwise** (no initiative context and no explicit provider),
   select the single active row whose `standards_provider.enterprise_default`
   is `true`. This path works standalone, with no `initiatives.yml`.
4. Verify the selected row has `entry_type: standards_provider|both`, contains
   `standards_provider`, and has `status: active`.
5. Resolve the repository from `domain_repo_url` and the governed ref from
   `domain_git_ref`.
6. Resolve the provider navigation entrypoint from
   `standards_provider.entrypoint`.
7. Determine the effective pattern index:
   1. under initiative context, use the initiative's `pattern_index_ref` when
      present, otherwise the selected provider's default;
   2. without initiative context, use an explicit resolver
      `pattern_index_ref` when supplied with an explicit provider, otherwise
      the selected provider's default.
8. Resolve `domain_git_ref` to an immutable commit SHA before consuming the
   index or referenced documents.
9. If a consumer requires standards and any required step is unresolved,
   ambiguous, inactive, or invalid, **fail closed**.

The normative precedence is:

```text
with initiative context:
  initiative standards_domain_id -> enterprise default
  initiative pattern_index_ref -> selected provider default pattern_index_ref
  explicit runtime overrides -> rejected

without initiative context:
  explicit standards_domain_id -> enterprise default
  explicit pattern_index_ref -> selected provider default pattern_index_ref
```

### Resolution receipt (rev. finding 2)

To make the reproducibility goal a contract rather than an aspiration, a
successful resolution MUST emit a minimal **resolution receipt** recording the
standards source selected for the work:

| Field | Meaning |
| --- | --- |
| `spec_name` | constant `standards-resolution-receipt` |
| `spec_version` | semantic contract version, initially `"1.0.0"` |
| `initiative_context` | boolean indicating whether governed initiative context was supplied |
| `selection_source` | `explicit`, `initiative`, or `default` |
| `initiative_id` | governing initiative whenever initiative context exists, including when that initiative falls back to the enterprise default; otherwise omitted |
| `index_selection_source` | `explicit`, `initiative`, or `provider_default` |
| `standards_domain_id` | the selected provider domain |
| `domain_repo_url` | its repository |
| `standards_entrypoint` | the effective provider entrypoint |
| `pattern_index_ref` | the effective index path |
| `resolved_commit_sha` | the immutable SHA `domain_git_ref` resolved to |
| `resolved_at` | ISO 8601 UTC resolution timestamp |

When `initiative_context` is `true`, `initiative_id` is required even when
`selection_source` is `default`; when it is `false`, `initiative_id` is
omitted. This makes initiative-default fallback provenance schema-enforceable.

This receipt is the convention's boundary of the reproducibility claim: it
records *what was resolved*. How a consumer subsequently copies, mounts,
caches, materializes, or cryptographically attests the referenced content
remains outside this proposal (the consuming runtime's concern). The earlier
"prove which standards informed a design" goal is scoped to this receipt — not
extended to full content attestation.

**Ownership and lifecycle.** The convention owns the receipt schema and
conformance rules. The resolver component that performs standards resolution
MUST construct and return the receipt to its caller on success; validation-only
tools MAY emit it to stdout or a caller-supplied output path. Durable
persistence is consumer-owned and is not required for convention conformance.
A resolver conforms when it applies the precedence and validation rules,
resolves the immutable commit, and returns a schema-valid receipt. A failed
resolution emits a typed error and no successful receipt.

## Pattern-index contract (rev. finding 3)

Routing to a "machine-readable" index is not interoperable unless consumers
know its shape. This proposal defines a **minimal** index envelope so the
routing extension is usable; richer pattern-document semantics remain a
separate, independently versioned specification.

- The index file named by `pattern_index_ref` is YAML or JSON with media type
  `application/yaml` or `application/json`.
- It carries the convention header `spec_name: pattern-index` and semantic
  `spec_version`, initially `"1.0.0"`, plus a required `patterns` array.
- Each `patterns` entry has: `pattern_id` (non-empty string, unique in the
  index), `path` (repository-relative, no traversal), and `title` (string).
  Additional per-entry fields are permitted but not required by this contract.

```yaml
spec_name: pattern-index
spec_version: "1.0.0"
patterns:
  - pattern_id: strangler-fig
    path: architecture/patterns/strangler-fig.md
    title: Strangler Fig Migration
```

An index whose `spec_version` a consumer does not support, or that fails this
minimal shape, is treated as `ERR_PATTERN_INDEX_INVALID` — fail closed, never
a best-effort parse. The full schema of an individual pattern document is out
of scope here (see Non-goals).

**Ownership and lifecycle.** The standards-provider owner authors, approves,
versions, and publishes the index and its referenced documents in the provider
repository. Consumers treat the resolved commit as immutable input. The
convention owns only the minimum interoperable index schema and routing
semantics, not the provider's editorial workflow.

## Referential-integrity and validation rules

The convention validator should enforce:

1. `entry_type` is one of `domain`, `standards_provider`, or `both`.
2. A workstream `domain_id` references only a `domain` or `both` row.
3. A selected `standards_domain_id` references only a `standards_provider` or
   `both` row with a `standards_provider` object.
4. A row with `standards_provider.enterprise_default: true` has entry type
   `standards_provider` or `both`.
5. At most one active registry row is the enterprise default.
6. A standards-provider row has `domain_repo_url`, `domain_git_ref`, and
   `standards_provider.entrypoint` plus
   `standards_provider.pattern_index_ref`.
7. An initiative or explicit `pattern_index_ref` is invalid without a
   resolvable provider selection.
8. `standards_provider` object presence requires `entrypoint` and
   `pattern_index_ref`; it has no disabled form. `enterprise_default` is
   optional and defaults to `false`. A `domain` row does not carry the object.
9. Paths are repository-relative, contain no traversal outside the repository,
   and resolve at the governed ref when repository access is available.
10. A standards provider is routable only when `status: active` (stricter than
   general routability; see "Routable status").
11. The effective pattern index conforms to the Pattern-index contract
   (`spec_name` and supported `spec_version`; each entry well-formed).
12. A standards-only provider omits `domain_entrypoint`; a provider that is
    also a bounded domain satisfies the existing `domain_entrypoint` contract.
13. The standards entrypoint exists and satisfies its minimum navigation
    contract, including a link to the provider default index and explanation of
    approved overrides.
14. The provider repository contains a root `AGENTS.md`.
15. Explicit provider or index overrides are rejected whenever initiative
    context exists.
16. The resolution receipt records `selection_source`,
    `index_selection_source`, and `initiative_id` whenever initiative context
    exists.
17. A consumer does not omit or suppress initiative context for work whose
    governed binding identifies an initiative.

Suggested validator errors:

| Code | Meaning |
| --- | --- |
| `ERR_STANDARDS_DOMAIN_NOT_FOUND` | The selected `standards_domain_id` has no matching domain. |
| `ERR_STANDARDS_DOMAIN_NOT_ELIGIBLE` | The selected row is not a standards-provider subtype or is not `active`. |
| `ERR_WORKSTREAM_TARGET_NOT_DOMAIN` | A workstream targets a standards-only registry entry. |
| `ERR_STANDARDS_DEFAULT_AMBIGUOUS` | More than one active enterprise default exists. |
| `ERR_STANDARDS_ENTRYPOINT_INVALID` | The entrypoint is missing, unsafe, or violates its minimum contract. |
| `ERR_STANDARDS_INSTRUCTIONS_MISSING` | The provider repository has no root `AGENTS.md`. |
| `ERR_STANDARDS_OVERRIDE_NOT_AUTHORIZED` | An explicit provider or index override was supplied under initiative context. |
| `ERR_STANDARDS_INITIATIVE_CONTEXT_REQUIRED` | Governed work is initiative-bound, but the resolver invocation omitted or suppressed that context. |
| `ERR_PATTERN_INDEX_MISSING` | No effective pattern index can be resolved. |
| `ERR_PATTERN_INDEX_INVALID` | The index path is unsafe, does not resolve at the governed ref, or violates the Pattern-index contract. |

## Schema and tooling changes requested

If accepted, the convention owner would update:

- `enterprise_repo_convention.md`;
- `schemas/domain-registry.schema.json`;
- `schemas/initiatives.schema.json`;
- **the initiative generation source and generator** — update
  `skills/ea-convention/templates/initiative-pipeline.yml.template`, add or
  update its schema, and require every selector generator to carry
  `standards_domain_id` / `pattern_index_ref` through to `initiatives.yml`.
  The canonical repository currently has the pipeline template but no bundled
  selector generator, so acceptance needs either a canonical generator or a
  normative pass-through rule plus a conformance fixture; otherwise an
  initiative standards selection can disappear on regeneration
  (rev. finding 4);
- a `schemas/pattern-index.schema.json` for the minimal index envelope above;
- a `schemas/standards-resolution-receipt.schema.json`;
- a `STANDARDS.md` template or equivalent standards-entrypoint template;
- corresponding YAML templates and examples;
- `skills/ea-convention/scripts/validate_convention.py`;
- `skills/ea-convention/SKILL.md` routing and validation guidance; and
- any generated or translated specification surfaces maintained by the
  convention repository.

The convention owner should choose the appropriate semantic-version change.
Consumers must not treat these properties as canonical before an accepted
version is published.

## Non-goals

This proposal does not define:

- a role-kit or workspace directory such as `.openarchitect/role-kit/`;
- dispatch-manifest fields such as `required_dispatch_inputs`;
- design-output fields such as `pattern_refs`;
- the schema or approval lifecycle of individual pattern documents beyond the
  minimal index envelope;
- approval workflows for individual pattern documents;
- content-addressed preservation or runtime attestation; or
- a requirement that every initiative use a standards domain.

Those contracts belong to the consuming runtime or to a separate future
convention proposal.

## Versioning, compatibility, and migration

This extension publishes the following coordinated artifact versions:

| Artifact | Version | Compatibility effect |
| --- | --- | --- |
| `domain-registry` | `2.0.0` | Breaking: every row requires `entry_type`, and standards-provider rows become valid registry entries. |
| `initiatives` | `1.1.0` | Additive: initiative rows may declare `standards_domain_id` and `pattern_index_ref`. |
| `pattern-index` | `1.0.0` | New artifact contract. |
| `standards-resolution-receipt` | `1.0.0` | New resolver-output contract. |

The valid release combinations are:

| `domain-registry` | `initiatives` | Standards-routing behavior |
| --- | --- | --- |
| `1.x` | `1.0.x` | Existing domain routing only. Standards resolution is unavailable. |
| `1.x` | `1.1.x` | Valid only while no initiative uses the standards-selection fields. If either field is present or standards are required, fail closed because a 1.x registry cannot identify a standards provider. |
| `2.x` | `1.0.x` | Enterprise-default resolution is available. Initiative context may fall back to that default, but cannot select a provider or index because the initiative schema has no such fields. Initiative-free explicit selection is also available. |
| `2.x` | `1.1.x` | Full enterprise-default, initiative-owned, and initiative-free explicit resolution defined by this proposal. |

Any successful standards resolution additionally requires a compatible
`pattern-index` 1.x artifact and emits a
`standards-resolution-receipt` 1.x artifact. Consumers MUST reject unknown
major versions of either contract. An `initiatives` 1.1.x standards selection
therefore requires a `domain-registry` 2.x artifact; it is never interpreted
against a 1.x registry.

### 1.x to 2.0 migration

1. Copy the existing 1.x registry and change its header to:

   ```yaml
   spec_name: domain-registry
   spec_version: "2.0.0"
   ```

2. Add `entry_type: domain` to every existing bounded-domain row.
3. Validate that every existing workstream target resolves to a `domain` or
   `both` row.
4. Add standards-provider rows only after all registry consumers used in that
   environment declare 2.x support.
5. For a bounded domain that also publishes standards, change its type to
   `both` and add `standards_provider`.
6. Update initiative-pipeline and generated `initiatives.yml` artifacts with
   optional provider selections.
7. Roll out 2.x-aware validators/resolvers before publishing the 2.0 registry
   as the active catalog.

There is no mixed-major interpretation:

- a 1.x registry contains bounded-domain rows only and cannot carry
  `entry_type` or standards-provider rows as canonical fields;
- a 2.x registry requires `entry_type` on every row;
- consumers supporting only 1.x MUST fail closed on a 2.x registry, as required
  by the convention's versioning contract; and
- a 2.x consumer MAY read a 1.x registry as domain-only input for migration,
  but it cannot resolve standards from it and must fail if standards are
  required.

Enterprises adopting the extension first migrate the registry and consumers,
then register a standards-provider entry and optionally designate it as the
enterprise default. Initiatives may select another provider, while two-level
deployments may pass an explicit `standards_domain_id` without creating an
initiative.

## Acceptance criteria

The proposal is complete when:

1. The canonical specification defines the fields, precedence, and ownership.
2. `domain-registry` 2.0 requires `entry_type`, and 1.x consumers demonstrably
   fail closed on the unknown major.
3. Catalog, pattern-index, and resolution-receipt schemas validate the new
   contracts.
4. Templates demonstrate a standalone enterprise default, a provider that is
   also a bounded domain, and an initiative-owned selection.
5. The initiative-pipeline source and every supported selector-generation path
   preserve the initiative standards fields.
6. The validator rejects workstreams targeting standards-only entries and
   enforces all other cross-catalog integrity rules above.
7. Tests cover 1.x-to-2.0 migration, old-consumer fail-closed behavior,
   the release compatibility matrix, initiative-free explicit provider
   selection, rejection of explicit provider and index overrides under
   initiative context, rejection of suppressed initiative context for bound
   work, no-initiative default resolution, initiative-owned selection, missing
   provider, ineligible provider, workstream subtype rejection, multiple
   defaults, `in_progress` rejection, missing root `AGENTS.md`,
   missing/invalid entrypoint and index, provider-safe index precedence, unsafe
   paths, receipt provenance, receipt generation, and generated selector
   preservation.
8. The accepted convention version and migration guidance are published.

## Requested decision

Please decide whether governed standards and pattern corpora should participate
in the enterprise routing convention as standards-provider registry entries
with:

- an explicit `domain|standards_provider|both` registry subtype;
- initiative-owned selection when initiative context exists, with explicit
  runtime overrides rejected;
- initiative-free explicit resolver selection;
- one optional enterprise default;
- a governed standards entrypoint plus versioned pattern index;
- a versioned resolver receipt; and
- fail-closed referential-integrity rules for consumers that declare standards
  as required.

If the field shape is changed during review, preserve those semantics so
runtime consumers can resolve one governed source without inventing a parallel
location authority.
