# Operational Guidance

This document collects non-normative implementation guidance that complements the Multi-Level Repository Navigation and Routing Convention. The specification remains authoritative for conformance requirements; this file is for operationalization patterns.

## Validation and CI

Typical CI or lint implementations check:

1. schema and required-field conformance
2. selector uniqueness
3. cross-file reference integrity
4. status-policy compliance
5. catalog version compatibility
6. referenced repository reachability when CI identity can access the target
7. referenced entrypoint path existence when the target repository/revision is available to CI
8. stale or inaccessible routing targets before runtime rollout

A thin validator/linter commonly layers these checks in two passes:

1. validate each catalog against the authoritative machine-readable schema under `skills/ea-convention/references/`
2. apply cross-file, selector-uniqueness, and topology-aware checks that cannot be fully expressed in schema alone

Reference implementation in this repository:

1. `skills/ea-convention/scripts/validate_convention.py` validates schema conformance and cross-file rules.
2. Use `--active-only` to restrict routable statuses to `active` only.
3. Use `--repo-url` to enable local entrypoint path existence checks for entries that reference this repo.
4. This validator does not check Markdown links or heading anchors in documentation; use a separate doc-link check for that.

How these checks are implemented is toolchain-specific. Some teams will use repository-native CI, others will validate through provider APIs or orchestration runtimes.

Minimal CI example:

```yaml
name: validate-convention

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install jsonschema pyyaml
      - run: python skills/ea-convention/scripts/validate_convention.py --root .
```

Minimal pre-commit example:

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-enterprise-convention
        name: validate-enterprise-convention
        entry: python skills/ea-convention/scripts/validate_convention.py --root .
        language: system
        pass_filenames: false
```

## Observability

Minimum structured failure record fields commonly include:

1. `timestamp`
2. `level` (`enterprise`, `solution`, `domain`)
3. `selector_type`
4. `selector_id`
5. `artifact_path`
6. `error_code`
7. `message`

Teams MAY extend these with provider metadata, repository revision identifiers, correlation IDs, or remediation hints.

## Agent Context Engineering

Recommended harness/context practices:

1. Treat entrypoint files as maps, not encyclopedias.
2. Keep detailed knowledge in linked artifacts and canonical documents.
3. Add mechanical doc freshness checks in CI.
4. Start traversal with `AGENTS.md`, then the applicable level entrypoint, then the canonical selector catalog for the next boundary.
5. Treat `DOMAIN.md` plus `domain-implementations.yml` as the bounded-context contract for domain-scoped execution.

For additional harness-oriented guidance, see [harness-engineering.md](harness-engineering.md).

Possible IDE and agent integrations:

1. A lightweight IDE extension can resolve selectors like `initiative_id` or `implementation_id` into repository targets without changing the canonical YAML source.
2. Agent plugins can prefetch only the resolved entrypoint and catalog row for the current task, which keeps context windows smaller than repo-wide search.
3. Provider catalogs such as Backstage, Nx graph metadata, or similar inventory tools can mirror or enrich these artifacts, but they should not replace the canonical routing semantics stored in YAML.

## Reference Layout

Illustrative repository layout:

```text
<enterprise-repo>/
  AGENTS.md
  ENTERPRISE.md
  initiatives.yml
  domain-registry.yml

<solution-repo>/
  AGENTS.md
  SOLUTION.md
  domain-workstreams.yml
  solution-index.yml

<domain-repo>/
  AGENTS.md
  DOMAIN.md
  domain-implementations.yml
  governance-state.yml
```

## Reference Implementation Mapping

An implementation MAY map catalogs into architecture folders, for example:

1. `architecture/portfolio/initiatives.yml`
2. `architecture/solution/domain-workstreams.yml`
3. `domain-implementations.yml`

An implementation MAY use environment bootstrap variables such as `OPENARCHITECT_ROOT_REPO_URL` as its concrete bootstrap mechanism for the topmost level present.

## Adoption Notes

For proposal process purposes, a common decomposition is:

1. core extension: multi-scale entrypoint convention
2. optional extension: routing catalog specification
3. companion extension: schema conformance profile and migration guidance
4. companion guidance: harness/context engineering and operational practices

For brownfield rollout patterns, see [brownfield-adoption.md](brownfield-adoption.md).
