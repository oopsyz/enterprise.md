# Templates

Starter templates for adopting the Multi-Level Repository Navigation and Routing Convention. Copy and customize for your organization.

## Entrypoint Templates

| Template | Level | Description |
|---|---|---|
| [ENTERPRISE.md.template](ENTERPRISE.md.template) | Enterprise | EA portfolio repo entrypoint |
| [SOLUTION.md.template](SOLUTION.md.template) | Solution | SA baseline repo entrypoint |
| [DOMAIN.md.template](DOMAIN.md.template) | Domain | DA design repo entrypoint |

## AGENTS.md Role Templates

| Template | Role | Description |
|---|---|---|
| [AGENTS.ea.md.template](AGENTS.ea.md.template) | EA | Enterprise architect agent instructions |
| [AGENTS.sa.md.template](AGENTS.sa.md.template) | SA | Solution architect agent instructions |
| [AGENTS.da.md.template](AGENTS.da.md.template) | DA | Domain architect agent instructions |
| [AGENTS.dev.md.template](AGENTS.dev.md.template) | Dev | Developer agent instructions |

## Routing Catalog Templates

| Template | Level | Selector | Profile |
|---|---|---|---|
| [initiatives.yml.template](initiatives.yml.template) | Enterprise | `initiative_id` | B+ |
| [domain-workstreams.yml.template](domain-workstreams.yml.template) | Solution | `workstream_id` | B+ |
| [implementation-catalog.yml.template](implementation-catalog.yml.template) | Domain | `work_item_id` or `api_id` | B+ (when selector-driven domain->implementation boundary exists) |

Format note: YAML is canonical for routing catalogs. JSON is an optional schema-equivalent compatibility projection.

## Governance Templates

| Template | Level | Profile |
|---|---|---|
| [domain-registry.yml.template](domain-registry.yml.template) | Enterprise | C |
| [solution-index.yml.template](solution-index.yml.template) | Solution | C |
| [initiative-pipeline.yml.template](initiative-pipeline.yml.template) | Enterprise | C |

Note: `governance-state.yml` (required for the Governed profile) does not have a starter template. See [examples/governed/domain-repo/governance-state.yml](../examples/governed/domain-repo/governance-state.yml) for a working sample.

## Industry-Specific Templates

| Template | Industry | Description |
|---|---|---|
| [industry/domain-registry.telco.yml.template](industry/domain-registry.telco.yml.template) | Telco | 35 TMF ODA components mapped 1:1 to domains |

## Usage

1. Decide whether you need Layer A only or a conformance profile (`Core` or `Governed`) from the [proposal](../enterprise_repo_convention.md).
2. Copy the relevant templates into your repository.
3. Remove the `.template` extension.
4. Ensure your repository has an `AGENTS.md` that directs agents to read the level entrypoint (see Key Rule 2 in the proposal).
5. Replace placeholder values (`<...>`) with your organization's data.
6. See [examples/](../examples/) for complete working samples at each profile level.
