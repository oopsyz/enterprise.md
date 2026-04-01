# DA Domain Identity Convention — Ratified

Status: **Ratified**
Accepted into: `enterprise_repo_convention.md` Section 5.3 (field rules) and Section 5.7 (DA Runtime Identity and Workstream Semantics)
Option adopted: **Ratified upstream** — use domain-scoped repository targeting semantics

## Origin

This document originated as a proposal to remove ambiguity in how Domain Architecture (DA) runtime identity, session continuity, and Solution Architecture (SA) to DA handoff should work.

The immediate trigger was a disagreement in the Worker Container implementation about whether a DA container/session should be keyed by `workstream_id` or `domain_id`.

## Problem Statement

The convention text and templates correctly preserved `workstream_id` as the canonical SA to DA selector, but earlier draft field naming created a strong implication that each workstream was a standalone DA runtime target.

That implication conflicted with the intended operating model used by domain owners:

- A DA owns a domain, not a single workstream.
- A domain can receive multiple workstreams from different initiatives.
- A DA session should accumulate domain context over time.
- Workstreams are inbound demand items that the DA evaluates, sequences, and reconciles into a domain roadmap.

Example:

- Initiative A sends work to domain `order`.
- Initiative B sends work to domain `order`.
- Both workstreams should land in the same DA ownership boundary for `order`.
- The `order` DA should evaluate both, then produce a coherent roadmap and implementation plan for that domain.

Under that model, `workstream_id` is handoff context, not the primary DA container identity.

## Accepted Clarification

The convention now explicitly distinguishes three separate concepts.

### 1. Handoff identity

`workstream_id` remains the canonical SA to DA handoff selector.

Use it to identify:

- the inbound change demand
- the originating initiative context
- the workstream-specific handoff artifact set
- the workstream-specific git reference or path when needed

Normative reference: `enterprise_repo_convention.md` Section 5.3 item 3, Section 5.7.1.

### 2. Ownership identity

`domain_id` is the canonical DA ownership and session identity.

Use it to identify:

- the DA container or runtime endpoint
- the long-lived DA session
- the domain roadmap and planning context
- the stable owning repository for the domain

Normative reference: `enterprise_repo_convention.md` Section 5.3 item 3, Section 5.7.3.

### 3. Repository resolution

The convention defines repository resolution in two layers:

1. Resolve the inbound handoff by `workstream_id`.
2. Resolve the owning DA runtime by `domain_id`.

That means the runtime may accept a workstream-shaped handoff, but it must map that handoff into a domain-owned execution boundary.

Normative reference: `enterprise_repo_convention.md` Section 5.7.2, Section 13.

## Catalog Shape

The accepted change preserves the overall `domain-workstreams.yml` shape while making the owning domain repository target explicit:

```yaml
version: "1.0"
workstreams:
  - workstream_id: ws-init-a-order
    initiative_id: init-a
    domain_id: order
    status: active
    domain_repo_url: https://github.com/example/order-domain
    workstream_entrypoint: inputs/workstreams/ws-init-a-order/WORKSTREAM.md
    workstream_git_ref: main
```

The semantics are now explicit:

- `workstream_id` remains the canonical SA to DA handoff selector.
- `domain_id` is the DA ownership and session identity.
- `domain_repo_url` identifies the owning domain repository target for the workstream, not a separate DA runtime identity.

Illustrative example with two initiatives converging on one domain:

```yaml
version: "1.0"
workstreams:
  - workstream_id: ws-init-a-order
    initiative_id: init-a
    domain_id: order
    status: active
    domain_repo_url: https://github.com/example/order-domain
    workstream_entrypoint: inputs/workstreams/ws-init-a-order/WORKSTREAM.md
    workstream_git_ref: main

  - workstream_id: ws-init-b-order
    initiative_id: init-b
    domain_id: order
    status: active
    domain_repo_url: https://github.com/example/order-domain
    workstream_entrypoint: inputs/workstreams/ws-init-b-order/WORKSTREAM.md
    workstream_git_ref: main
```

In that example, both workstreams hand off to the same domain-owned DA runtime for `order`.

## Metadata Semantics

The convention now makes the following distinction explicit (Section 5.7.5):

- `domain_repo_url` is the authoritative domain-owned DA target repository when DA runtime identity is domain-scoped.
- Any runtime metadata field derived from `domain-workstreams.yml[].domain_repo_url` for a domain-scoped DA row must not be treated as a workstream-scoped runtime identity.

If a runtime or dashboard wants to expose workstream-derived repository context for a domain-owned DA view, it should prefer a more explicit name such as:

- `workstream_context_repo_url`

If a generic `repo_url` field is retained for compatibility, the implementation should document clearly whether it is:

1. authoritative DA target routing metadata, or
2. informational handoff-context metadata only.

## Accepted Normative Changes

The following points are now normative in `enterprise_repo_convention.md`:

1. `workstream_id` remains the canonical selector in `domain-workstreams.yml`. (Section 5.3 item 3)
2. `domain_id` is the canonical DA runtime identity. (Section 5.7.3)
3. DA runtime/session continuity must be domain-scoped, not workstream-scoped. (Section 5.7.3)
4. A workstream handoff must be attachable to an existing domain-scoped DA session. (Section 5.7.3)
5. `domain_repo_url` in `domain-workstreams.yml` is not the identity of a separate DA container. It identifies the owning domain repository target for self-sufficient routing. (Section 5.3 item 4, Section 5.7.2)
6. When both `domain-workstreams.yml[].domain_repo_url` and authoritative `domain-registry.yml[].domain_repo_url` exist, the registry remains authoritative and the values must match. (Section 5.7.2)
7. Many workstreams from different initiatives may converge on one domain-owned DA runtime. (Section 5.7.1)
8. Overloaded generic runtime fields such as `repo_url` for domain-scoped DA rows are discouraged unless semantics are explicitly documented. (Section 5.7.5)

## Option Evaluation (Historical)

Three options were evaluated. Option A was initially adopted; the upstream convention subsequently moved to domain-scoped repository targeting aligned with Option B's direction.

### Option A: Keep the earlier field naming, clarify semantics (Historical)

Keep the earlier workstream-scoped repository naming and clarify that it does not imply a unique DA runtime per workstream.

Pros: backward compatible, minimal schema disruption.
Cons: name remains potentially misleading.

### Option B: Rename the field to domain-owned targeting (Superseded by upstream changes)

Rename the field to a domain-owned repository target. This is the direction now reflected in the upstream convention.

### Option C: Split handoff and ownership explicitly (Not adopted)

Use `workstream_context_repo_url` and `domain_owner_repo_url`. Most explicit but largest convention change. Not required given Option A clarification.

## Runtime Guidance For Worker Container

Worker Container and similar runtimes should adopt these semantics, which are now consistent with the upstream convention:

1. DA session identity is `domain_id`.
2. A workstream may be used to discover the target domain, but it does not imply a separate long-lived DA container per workstream.
3. Explicit DA domain mode is valid and should remain supported.
4. If a workstream-based startup path exists, it should resolve:
   - `workstream_id` -> `domain_id`
   - then attach or route to the DA runtime for that domain
5. In DA domain mode, `OPENARCHITECT_GIT_REPO_URL` must resolve from authoritative `domain_repo_url`.
6. Discovery and workload automation should avoid conflating:
   - workstream as inbound handoff
   - domain as DA ownership/runtime identity

Worker Container and similar runtimes should also make two-stage validation explicit:

1. Discovery or planning validation:
   - confirms that the handoff can be associated with a valid domain identity
   - confirms required selector context is present for later runtime resolution
2. Startup resolution validation:
   - resolves the authoritative domain target from `domain-registry.yml`
   - enforces active-only domain status and authoritative repo resolution

Passing planning validation should not be interpreted as proof that startup
resolution will succeed. The convention allows these two stages (Section 5.7.4), but the
runtime should document them clearly.

This runtime shift is potentially backward-incompatible for local state and automation if any existing session or queue records are keyed by `workstream_id` rather than `domain_id`.

Affected runtime migration concerns include:

- persisted DA session ledgers keyed by `role + selector_id`
- queued or historical workload entries keyed by `workstream:<id>`
- dashboard/session views that assume one DA runtime per workstream
- operator habits and scripts that start DA containers with `ws-...` selectors

Recommended runtime migration behavior:

1. Treat existing workstream-keyed DA sessions as legacy records.
2. Do not silently overwrite them with domain-keyed sessions.
3. Start writing new DA session continuity records under `domain_id`.
4. Where possible, preserve the original `workstream_id` as attached inbound context on the domain-scoped session.
5. Update workload and dashboard code to render domain ownership and workstream context separately during the transition.

Heuristic guards are acceptable as runtime ergonomics, but they should not be
treated as part of the convention unless formally specified. For example,
prefix-based checks such as `ws-...` may help catch obvious operator mistakes,
but they are implementation conveniences rather than normative selector rules.

## Applied Upstream Artifacts

The following upstream convention artifacts have been updated:

- [enterprise_repo_convention.md](enterprise_repo_convention.md) — Section 5.3 field rules and Section 5.7 (DA Runtime Identity and Workstream Semantics)
- [skills/ea-convention/SKILL.md](skills/ea-convention/SKILL.md) — Workstream Semantics section
- [skills/ea-convention/templates/SOLUTION.md.template](skills/ea-convention/templates/SOLUTION.md.template) — Routing section
- [skills/ea-convention/templates/DOMAIN.md.template](skills/ea-convention/templates/DOMAIN.md.template) — DA Identity section

## Remaining Downstream Alignment (Worker Container)

The following Worker Container artifacts should align with the ratified convention. This is downstream implementation work, not a convention change. Paths are shown as sibling-repo relative references, not links in this repository:

- `../worker_container/DOMAIN.md`
- `../worker_container/README.md`
- `../worker_container/docs/startup_contract.md`
- `../worker_container/scripts/launch_container.py`
- `../worker_container/scripts/discover_enterprise_repo_graph.py`
- `../worker_container/scripts/workload_manager.py`
- `../worker_container/scripts/role_dispatcher.py`

## Migration Guidance

Migration should preserve compatibility:

1. Continue accepting `workstream_id` as the canonical inbound selector.
2. Normalize runtime/session identity to `domain_id`.
3. Preserve `workstream_id` in session metadata as inbound context.
4. Avoid breaking existing catalogs unless a field rename is formally adopted.
5. If a field rename is adopted in future, support old and new names during a transition window.
6. Migrate DA runtime/session continuity from `workstream_id` keys to `domain_id` keys with legacy read support during the transition period.
