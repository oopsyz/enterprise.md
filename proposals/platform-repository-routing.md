# Proposal: Platform Repository Navigation and Routing

**Proposal version:** 1.0.0
**Status:** Accepted for incorporation into the draft convention
**Extends:** Multi-Level Repository Navigation and Routing Convention

## Decision

Platform is a durable architecture ownership and repository boundary parallel
to Domain downstream of Solution Architecture. Integration is not a separate
architecture level: Platform owns the operational integration view, while the
providing Domain or component continues to own interface semantics.

The convention adds:

1. `PLATFORM.md` as the Platform repository entrypoint;
2. `platform-registry.yml` as the Enterprise-owned `platform_id` registry;
3. `platform-workstreams.yml` as the Solution-owned route from an Initiative
   to one Platform authority;
4. `platform-change-handoff.yml` as the optional immutable SA-to-Platform
   requested-change contract; and
5. `platform-implementations.yml` as the Platform-owned implementation route.

These artifacts form a parallel route, not an extension of Domain identity:

```text
initiative_id
  -> solution repository
     -> domain-workstreams.yml   -> domain_id   -> DOMAIN.md
     -> platform-workstreams.yml -> platform_id -> PLATFORM.md
```

## Ownership

| Concern | Durable authority |
| --- | --- |
| End-to-end change design, including integration | Solution Architecture |
| Business meaning and API/event/schema promise (`interface_id`) | Providing Domain or component authority |
| Broker, gateway, endpoint, queue/topic, network path, security, capacity, resilience, observability, and operating model (`connection_id`) | Platform Architecture / Platform Engineering / SRE |
| Accepted current/as-built topology | Enterprise State Graph |
| Coordination and lifecycle facts | OA Engine |

A repository operated by Integration Platform Engineering is a Platform
repository under this model. The convention does not introduce
`INTEGRATION.md`, `integration-registry.yml`, or a separate Integration role.

## Identity and cardinality

- `platform_id` is the stable Platform authority identity.
- One Platform receives zero or more Initiative-scoped workstreams over time.
- One Initiative may target zero or more Platforms.
- One Platform has one authoritative governance home, but multiple
  `platform_id` values may share a repository when entrypoints are
  unambiguous.
- One Platform may route to many implementation targets.
- Repository URL, branch, path, team name, and runtime-session identity never
  substitute for `platform_id`.

## Repository contract

`PLATFORM.md` owns concise navigation to the durable platform baseline,
operational integration topology, accepted connection definitions, platform
implementation catalog, and incoming workstream material. It does not become
a mutable deployment database or duplicate runtime telemetry.

The canonical Platform-owned content may include:

- platform capabilities and service boundaries;
- `connection_id` definitions linked to their `interface_id` contracts;
- brokers, gateways, service meshes, messaging services, queues, topics, and
  endpoint topology;
- security, capacity, resilience, observability, recovery, and operational
  guardrails;
- production-support and SRE-facing runbooks; and
- implementation routing through `platform-implementations.yml`.

## Workstream and handoff semantics

A Platform workstream is one Initiative's demand against exactly one durable
Platform authority. It does not create a Platform runtime or ownership boundary.

`platform-workstreams.yml` intentionally mirrors the deterministic behavior of
`domain-workstreams.yml` while using Platform-specific identifiers and
repository fields. A routable entry resolves its Workstream-specific
`WORKSTREAM.md` at `workstream_git_ref`; that file remains independent of the
Platform-level `PLATFORM.md` at `platform_git_ref`.

Optional `change_handoff_ref` binds exact Git bytes of a
`platform-change-handoff` using repository-relative path, full commit, and
SHA-256 digest. The handoff carries requested design change only. Runtime
progress, gates, decisions, deployment status, incidents, and evidence remain
outside the portable convention artifact.

The Platform handoff may identify stable `interface_id` and `connection_id`
values in its architecture-element delta. It never transfers semantic ownership
of an interface contract to Platform.

## Compatibility

This is additive. Existing EA-SA-DA adopters remain conformant without Platform
artifacts when their operating model has no routed Platform boundary. Once a
Platform boundary is declared:

- Core routed adoption requires `PLATFORM.md`, `platform-workstreams.yml`, and
  `platform-implementations.yml` at the boundaries that exist.
- Governed adoption additionally requires `platform-registry.yml`.
- Domain catalogs MUST NOT be used to disguise Platform targets.
- A Platform repository MAY also contain implementation code or multiple
  Platform contexts, provided selector and path bindings remain unambiguous.

## Acceptance criteria

1. Platform is defined as a durable peer of Domain downstream of Solution.
2. Integration remains a first-class relationship covered operationally by
   Platform, not another architecture level.
3. `platform_id` is the stable target identity.
4. Platform routing never reinterprets `domain_id` or Domain catalogs.
5. Platform and Workstream entrypoints remain independent.
6. Platform change handoffs use exact Git artifact identity and exclude runtime
   execution state.
7. Partial adopters are not required to create empty Platform artifacts.
8. Validators enforce Platform selector uniqueness, registry agreement,
   entrypoint resolution, repository-binding uniqueness, and accessible
   handoff integrity.
