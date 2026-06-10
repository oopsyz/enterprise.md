# Changelog

All notable changes to this project should be documented in this file.

The format is loosely based on Keep a Changelog, with project-level draft/spec releases recorded here.

## [Unreleased]

### Added

- optional `repo.entrypoint` and `repo.git_ref` fields for `domain-implementations.yml`
- reserved interoperable bootstrap defaults: `ENTERPRISE_MD_BOOTSTRAP_URL` environment variable and `/.well-known/enterprise-md.json` discovery endpoint (Section 4)
- `domain-registry.yml` promoted to the canonical catalog set with `domain_id` selector semantics (Sections 5.1, 9); `solution-index.yml` and `governance-state.yml` named normatively with minimum fields (Section 9)
- documented optional provenance, correlation, and handoff fields (`generated_at_utc`, `generated_by`, `workspace_id`, `workstream_uuid`, `handoff_ref`, display names) (Section 5.3)
- workstream semantics: demand-unit model, domain-scoped DA identity, registry-authoritative repo resolution (Section 5.8) with a matching `ERR_CONFLICT` precedence rule (Section 10)
- read/write routing operation classes; `deprecated` is resolvable for read only, with a mandatory `deprecated_target` warning (Sections 5.4, 5.5)
- extension mechanism and registration of `domain-roadmap.yml` as a non-normative extension (Section 15)

### Changed

- unified catalog header contract: all canonical catalogs use `spec_name` + `spec_version` (full MAJOR.MINOR.PATCH); bare `version` and `spec_name: multi-scale-routing` are deprecated read-side aliases for the 1.x line (Section 5.2)
- `workstream_git_ref` is now optional/nullable pre-materialization; resolvers fall back to the target repository's default branch (Section 5.3)
- glob semantics defined as gitignore-style; whole-repository default changed from `["*"]` to `["**"]`, and the uniqueness invariant is stated in terms of pattern overlap (Sections 5.3, 11)
- authoritative JSON schemas moved from `skills/ea-convention/references/` to top-level `schemas/`; the validator auto-detects both locations
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
