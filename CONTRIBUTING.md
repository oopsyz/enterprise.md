# Contributing

## Scope

This repository is a draft specification and template set, not a runtime system.

Contributions are welcome for:

- specification clarity and correctness
- template consistency
- example quality
- cross-linking and navigation
- governance and adoption guidance

Do not treat files under `examples/` as live production configuration.

## Before You Open A Pull Request

1. Check whether the change belongs in the canonical specification file: [enterprise_repo_convention.md](enterprise_repo_convention.md).
2. Keep the change focused on one topic, section, or artifact family.
3. Update linked documentation when a change affects navigation, terminology, or conformance behavior.
4. Preserve stable section numbering intent within the current spec version.

## Issues

When opening an issue, include:

- whether the feedback applies to Layer A or Layer B
- whether it affects `Core`, `Governed`, or both profiles
- whether the issue is editorial, normative, or implementation guidance

Use feature requests for new proposal ideas and bug reports for broken links, template drift, or inconsistencies.

## Pull Request Expectations

Pull requests should:

- explain the problem being solved
- identify the affected spec sections or templates
- note any normative behavior changes
- avoid unrelated cleanup

If you change a template, update the relevant examples only when the example is meant to reflect the new normative guidance. Keep examples illustrative.

## Writing Guidance

- Link to canonical files instead of copying long excerpts.
- Prefer concise, normative language for requirements.
- Use `MUST`, `SHOULD`, and `MAY` consistently when changing normative text.
- Keep routing behavior deterministic and fail-closed unless the proposal explicitly states otherwise.

## Review And Merge

Maintainers review for specification coherence, backward impact on adopters, and clarity for both humans and tools. Large or normative changes may be discussed in issues before merge.

## Licensing

By submitting a contribution, you represent that you have the right to contribute it under the repository license in [LICENSE](LICENSE).
