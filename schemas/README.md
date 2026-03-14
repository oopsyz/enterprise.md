# Schemas

Authoritative machine-readable schemas for canonical catalog validation.

Current schemas:

1. `initiatives.schema.json`
2. `domain-workstreams.schema.json`
3. `domain-implementations.schema.json`
4. `domain-registry.schema.json`

These schemas cover structural validation and required-field conformance. Cross-file reference integrity, selector uniqueness, and topology-aware checks still require a validator/linter layer.

See [../enterprise_repo_convention.md](../enterprise_repo_convention.md) Section 7 and [../reference/operational-guidance.md](../reference/operational-guidance.md) for how schemas and lint checks fit together.
