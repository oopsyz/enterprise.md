# Changelog

All notable changes to this project should be documented in this file.

The format is loosely based on Keep a Changelog, with project-level draft/spec releases recorded here.

## [Unreleased]

### Added

- optional `repo.entrypoint` and `repo.git_ref` fields for `domain-implementations.yml`

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
