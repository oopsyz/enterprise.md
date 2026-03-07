# Resolve Codex Git Target Contract

## Purpose

Define a Codex-facing deterministic resolver contract derived from the existing selector-routing model.

This contract is intended for a `resolve_codex_git_target.py` style tool or skill.

## Design Goal

The resolver should behave like a pure routing service:

1. read canonical artifacts
2. resolve one target or a bounded target set
3. fail closed on ambiguity or invalid state
4. return structured routing context for Codex

## Inputs

Core inputs:

1. `mode`: `bootstrap | route | inspect`
2. `role`: `ea | sa | da | dev`
3. `selector_id`
4. `bootstrap_repo`
5. `git_ref`
6. `selector_source_repo`
7. `selector_catalog`
8. `implementation_catalog`
9. `allow_override`
10. `strict_active_only`

Optional inputs:

1. `domain_registry_catalog`
2. `solution_index_catalog`
3. `governance_state_catalog`
4. `local_root`
5. `output=json`

## Recommended Request Shape

```json
{
  "mode": "route",
  "role": "da",
  "bootstrap": {
    "repo_url": "https://github.com/example-org/ea-repo",
    "git_ref": "main"
  },
  "selector": {
    "kind": "workstream_id",
    "value": "ws-init-bss-modernization-om"
  },
  "sources": {
    "selector_source_repo_url": "https://github.com/example-org/bss-solution-repo",
    "selector_catalog": "architecture/solution/domain-workstreams.yml",
    "domain_registry_catalog": "architecture/enterprise/domain-registry.yml",
    "solution_index_catalog": "solution-index.yml",
    "governance_state_catalog": "governance-state.yml"
  },
  "options": {
    "strict_active_only": true,
    "allow_override": false,
    "include_governance": true
  }
}
```

## Success Response

```json
{
  "status": "ok",
  "repo_level": "domain",
  "resolution_type": "selector",
  "target": {
    "repo_url": "https://github.com/example-org/order-domain-repo",
    "git_ref": "feature/ws-init-bss-modernization-om",
    "workdir": "inputs/workstreams/ws-init-bss-modernization-om",
    "entrypoint": "inputs/workstreams/ws-init-bss-modernization-om/WORKSTREAM.md"
  },
  "context": {
    "role": "da",
    "selector_kind": "workstream_id",
    "selector_id": "ws-init-bss-modernization-om",
    "selector_status": "active",
    "initiative_id": "init-bss-modernization",
    "domain_id": "om",
    "handoff_ref": "architecture/solution/domain-handoffs/om/component-specs.yml"
  },
  "upstream": [
    {
      "level": "enterprise",
      "repo_url": "https://github.com/example-org/ea-repo",
      "entrypoint": "ENTERPRISE.md"
    },
    {
      "level": "solution",
      "repo_url": "https://github.com/example-org/bss-solution-repo",
      "entrypoint": "SOLUTION.md"
    }
  ],
  "governance": {
    "available": true,
    "profile": "c",
    "domain_registry_status": "active",
    "workstream_status": "active"
  }
}
```

## Error Response

```json
{
  "status": "error",
  "error_code": "NON_ROUTABLE_STATUS",
  "message": "workstream_id ws-init-bss-modernization-newdomain is not routable because status is approved",
  "details": {
    "role": "da",
    "selector_kind": "workstream_id",
    "selector_id": "ws-init-bss-modernization-newdomain",
    "catalog": "architecture/solution/domain-workstreams.yml"
  }
}
```

## Recommended Error Codes

1. `BOOTSTRAP_NOT_FOUND`
2. `BOOTSTRAP_AMBIGUOUS`
3. `MISSING_ENTRYPOINT`
4. `MISSING_CATALOG`
5. `SCHEMA_INVALID`
6. `UNSUPPORTED_VERSION`
7. `SELECTOR_NOT_FOUND`
8. `SELECTOR_AMBIGUOUS`
9. `NON_ROUTABLE_STATUS`
10. `MISSING_TARGET_FIELD`
11. `REPO_UNRESOLVABLE`
12. `GIT_REF_UNRESOLVABLE`
13. `CATALOG_DRIFT`

## Field Rules

1. `repo_url` is required for routed targets unless a local-root mode explicitly replaces it
2. `entrypoint` is required for returned targets
3. `git_ref` is required when the catalog provides one, otherwise default from bootstrap or platform policy
4. `workdir` should be repo-relative and default to `.`
5. YAML is authoritative over JSON
6. if YAML and JSON disagree, fail closed with `CATALOG_DRIFT`

## Role Mapping

1. `ea`
   - bootstrap into the enterprise repo
   - open `ENTERPRISE.md`
2. `sa`
   - resolve `initiative_id`
   - open the solution repo and `SOLUTION.md`
3. `da`
   - resolve `workstream_id`
   - open the domain repo, `workstream_git_ref`, `workstream_path`, and `workstream_entrypoint`
4. `dev`
   - resolve `work_item_id` or `api_id`
   - open the implementation target path with the relevant domain context

## Codex Usage Model

The Codex-facing client should:

1. call the resolver first
2. open the resolved repo, ref, and workdir only when the resolver succeeds
3. inject the returned context into the new or existing thread
4. show routing errors directly instead of falling back to heuristic search
