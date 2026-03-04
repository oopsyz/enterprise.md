# Templates

Starter templates for adopting the Multi-Level Repository Entrypoint Convention. Copy and customize for your organization.

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

## Governance Templates

| Template | Level | Profile |
|---|---|---|
| [domain-registry.yml.template](domain-registry.yml.template) | Enterprise | C |
| [solution-index.yml.template](solution-index.yml.template) | Solution | C |
| [initiative-pipeline.yml.template](initiative-pipeline.yml.template) | Enterprise | C |

## Industry-Specific Templates

| Template | Industry | Description |
|---|---|---|
| [industry/domain-registry.telco.yml.template](industry/domain-registry.telco.yml.template) | Telco | 35 TMF ODA components mapped 1:1 to domains |

## Usage

1. Pick a conformance profile (A, B, or C) from the [proposal](../multi_level_repository_entrypoint_convention.md).
2. Copy the relevant templates into your repository.
3. Remove the `.template` extension.
4. Replace placeholder values (`<...>`) with your organization's data.
5. See [examples/](../examples/) for complete working samples at each profile level.
