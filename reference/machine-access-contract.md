# Machine Access Contract

This companion document explains the optional machine access contract defined in Section 5.7 of the Multi-Level Repository Navigation and Routing Convention.

Purpose:

- provide a common query contract over canonical routing catalogs
- enable interoperable resolver behavior across CLI, API, MCP, or other access surfaces
- keep transport and runtime choices outside the core convention

This document is companion guidance. The normative contract lives in Section 5.7 of the main specification.

## Scope

The contract standardizes:

- required operations
- inputs and outputs
- error behavior
- authority and freshness rules

The contract does not standardize:

- CLI syntax
- HTTP endpoints
- authentication
- programming language
- deployment model

## Required Operations

### `resolve`

Resolves a single catalog entry by canonical selector type and selector value.

Examples of canonical resolution:

- `initiative_id=init-example`
- `workstream_id=ws-init-example-order`
- `implementation_id=order-api`

### `list`

Returns entries for a catalog, optionally filtered by exact-match status.

Examples:

- list all `initiatives.yml` entries
- list `domain-workstreams.yml` entries with `status=active`
- list `domain-implementations.yml` entries with `status=active`

### `validate`

Reports catalog integrity against the minimum checks expected by the convention.

The expected checks are:

- schema and required fields
- selector uniqueness
- cross-file referential integrity
- status-policy compliance
- version compatibility
- entrypoint/path existence checks when target artifacts are available to the validator

## Input Contract

Required input expectations:

- `resolve` uses a canonical selector type and canonical selector value
- `list` may include an exact-match status filter
- callers should not rely on fuzzy search or implementation-specific aliases for deterministic resolution

The goal is deterministic access, not search convenience.

## Output Contract

Outputs must preserve canonical semantics.

Minimum expectations:

- `resolve` returns the canonical fields required for the relevant catalog type
- `list` returns canonical entries without changing their meaning
- extension fields are allowed, but canonical fields must remain present and unmodified

Recommended metadata fields:

- `artifact_path`
- `artifact_revision`
- `catalog_type`
- `generated_at`
- `staleness_boundary`

## Error Contract

Machine access surfaces should align with the convention's structured error model.

Minimum required codes:

- `ERR_SELECTOR_MISSING`
- `ERR_SELECTOR_AMBIGUOUS`
- `ERR_SELECTOR_NOT_ROUTABLE`

Other applicable codes may also be used, such as:

- `ERR_CONFLICT`
- `ERR_TARGET_UNREACHABLE`
- `ERR_ACCESS_DENIED`
- `ERR_SELECTOR_DUPLICATE`
- `ERR_INITIATIVE_NOT_FOUND`
- `ERR_DOMAIN_NOT_FOUND`
- `ERR_ENTRYPOINT_MISSING`

## Authority Rule

Canonical YAML is authoritative.

Any machine access surface is a projection over the canonical artifacts, not an independent source of truth.

If a query surface disagrees with the canonical YAML, the YAML wins.

## Freshness Rule

Implementations should make freshness visible rather than implicit.

Acceptable patterns include:

- returning results that are consistent with the current authoritative YAML revision
- returning a response revision identifier that can be compared to the source artifact
- declaring a bounded staleness model

The main requirement is that a consumer can determine whether a response reflects the authoritative catalog state.

## Realization Patterns

The same contract can be implemented through different surfaces:

- CLI
- HTTP API
- MCP tool
- library call
- generated local cache

These surfaces can vary, as long as the contract semantics stay stable.

## Design Guidance

Use the contract when you want:

- targeted selector lookup without reading full catalogs every time
- machine-readable validation results
- consistent behavior across tools and runtimes

Prefer direct YAML reads when you want:

- full raw source inspection
- auditing of the canonical artifact
- troubleshooting projection or freshness problems

## Bottom Line

Section 5.7 standardizes what a machine access surface must mean.

This companion document explains how different implementations can realize that contract without turning the convention into a CLI or API specification.
