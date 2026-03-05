# DOMAIN

Domain entrypoint for the `enterprise.md` standard repository. This repo defines and maintains the multi-level repository navigation and routing convention.

## Read First

1. This file - domain context and navigation
2. `README.md` - proposal overview, profile model, and adoption flow
3. `multi_level_repository_navigation_and_routing_convention.md` - normative specification

## Parent

- [ENTERPRISE](https://github.com/oopsyz/tincan-ea/blob/main/ENTERPRISE.md)

## Critical File Contract

- Keep required section headings from this template.
- Do not rename or delete required sections.
- Keep this file concise: identity, routing semantics, and links.
- Put detailed or mutable operational values in canonical artifacts and link them here.
- If a required section has no content, keep it and write `Not applicable`.

## Knowledge Store Layout

```text
DOMAIN.md
AGENTS.md
README.md
multi_level_repository_navigation_and_routing_convention.md
templates/
examples/
```

## Canonical Artifacts

- `multi_level_repository_navigation_and_routing_convention.md` (normative convention specification)
- `templates/ENTERPRISE.md.template` (enterprise entrypoint template)
- `templates/SOLUTION.md.template` (solution entrypoint template)
- `templates/DOMAIN.md.template` (domain entrypoint template)
- `templates/initiatives.yml.template` (enterprise routing catalog template)
- `templates/domain-workstreams.yml.template` (solution routing catalog template)
- `templates/implementation-catalog.yml.template` (domain routing catalog template)
- `examples/profile-a/`, `examples/profile-b/`, `examples/profile-c/` (reference implementations by conformance level)

## Routing

Not applicable. This standards repository defines routing conventions but does not execute runtime selector routing.

## Upstream Inputs

- Community and internal feedback on multi-repository navigation and governance patterns
- Implementation learnings from adopters using templates and profiles

## Policy

- Keep this repository specification-focused and implementation-agnostic.
- Keep templates and examples synchronized with the normative specification.
- Avoid embedding tool- or runtime-specific assumptions into the standard.
