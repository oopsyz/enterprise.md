# Changelog

All notable changes to this project should be documented in this file.

The format is loosely based on Keep a Changelog, with project-level draft/spec releases recorded here.

## [Unreleased]

### Added

- Platform as a durable repository and architecture ownership boundary parallel
  to Domain downstream of Solution, covering operational integration through
  `PLATFORM.md`, stable `platform_id`, `interface_id` references, and operated
  `connection_id` realizations
- canonical `platform-registry`, `platform-workstreams`,
  `platform-change-handoff`, and `platform-implementations` 1.0 schemas,
  templates, examples, role pack, and validator support
- optional canonical `domain-change-handoff` 1.0 artifact and typed
  `change_handoff_ref` for immutable SA-to-Domain Workstream change content;
  legacy `handoff_ref` remains opaque and unchanged
- governed standards-provider routing, versioned pattern indexes, resolution
  receipts, a runtime resolver, and a standards-field-preserving initiative
  selector generator
- optional `repo.entrypoint` and `repo.git_ref` fields for `domain-implementations.yml`
- reserved interoperable bootstrap defaults: `ENTERPRISE_MD_BOOTSTRAP_URL` environment variable and `/.well-known/enterprise-md.json` discovery endpoint (Section 4)
- `domain-registry.yml` promoted to the canonical catalog set with `domain_id` selector semantics (Sections 5.1, 9); `solution-index.yml` and `governance-state.yml` named normatively with minimum fields (Section 9)
- documented optional provenance, correlation, and handoff fields (`generated_at_utc`, `generated_by`, `workspace_id`, `workstream_uuid`, `handoff_ref`, display names) (Section 5.3)
- workstream semantics: demand-unit model, domain-scoped DA identity, registry-authoritative repo resolution (Section 5.7) with a matching `ERR_CONFLICT` precedence rule (Section 10)
- read/write routing operation classes; `deprecated` is resolvable for read only, with a mandatory `deprecated_target` warning (Sections 5.4, 5.5)
- registration of `domain-roadmap.yml` as a proposed non-normative extension, excluded from the canonical catalog set (Appendix A)

### Changed

- `solution-index` advances to 1.1.0 with optional Platform scope references;
  existing Domain-only topologies remain conformant and need no placeholder
  Platform artifacts
- routing and conformance rules now branch from Solution to Domain and/or
  Platform; Platform targets must not be represented through Domain catalogs
- unified catalog header contract: all canonical catalogs MUST use `spec_name` + `spec_version` (full MAJOR.MINOR.PATCH). `spec_name: multi-scale-routing` is still accepted on read as a deprecated alias for `domain-implementations`; a bare `version` header is deprecated and no longer satisfies the contract — such files MUST be migrated to `spec_name`/`spec_version` (Section 5.2). Migration note: `spec_version: "1.0.0"` is the first published header contract; bare-`version` files are pre-contract draft artifacts, so this migration is not a `MAJOR` increment (Section 6, header contract lineage)
- `repo.paths` scoping is glob-based with a whole-repository default of `["*"]`, and the uniqueness invariant is stated in terms of pattern overlap (Sections 5.3, 11)
- authoritative JSON schemas moved from `skills/ea-convention/references/` to top-level `schemas/`; the validator auto-detects an adopter repo's vendored `schemas/`, the tool's own top-level `schemas/`, and the legacy `references/` layout
- validator and skill error vocabulary aligned with spec Section 11 (`ERR_SELECTOR_AMBIGUOUS`, `ERR_REFERENCE_UNRESOLVED`, `ERR_CONFLICT`, ...); removed the warning on omitted `repo.url`, which is a legal monorepo default
- examples, templates, and packs updated: `solution-index.yml` uses `domain_id` (was `domain_key`), tool-specific `.openarchitect/` paths replaced with convention-neutral artifacts, embedded `execution:` state removed from workstream catalogs (now prohibited by Section 5.1)

### Notes

- purpose: let a first-party Domain repo route deterministically into adopted external or open-source implementation repositories without requiring those upstream repos to add `DOMAIN.md`, `AGENTS.md`, or other convention files
- `repo.entrypoint` identifies the file agents should open in the target repo
- `repo.git_ref` lets the Domain repo pin the revision that the architecture was validated against
- this is a backward-compatible additive change to the domain->implementation routing contract

## [0.1.0] - 2026-03-10

Initial public draft release.

### Added

- initial specification for the Multi-Level Repository Navigation and Routing Convention
- Layer A entrypoint convention covering `ENTERPRISE.md`, `SOLUTION.md`, and `DOMAIN.md`
- Layer B routing catalog specification for `initiatives.yml`, `domain-workstreams.yml`, and `domain-implementations.yml`
- conformance profile definitions for `Core` and `Governed`
- starter templates for entrypoints, role-specific `AGENTS.md`, Claude Code bridge `CLAUDE.md`, and routing/governance catalogs
- working examples for `Core` and `Governed` profiles
- open-source project metadata including contribution, governance, code of conduct, security, issue templates, PR template, and docs CI

### Notes

- This is a draft proposed standard and may still change in backward-incompatible ways before a stable `1.0.0` release.
