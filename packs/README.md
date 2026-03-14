# Packs

Ready-to-drop role packs for the enterprise.md convention. Each pack contains the files needed for a specific repo role, with placeholders for repo-specific values.

## Available Packs

| Pack | Role | Repo type | Key files |
| - | - | - | - |
| [`ea/`](ea/) | Enterprise Architect | Enterprise repo | `ENTERPRISE.md`, `initiatives.yml`, `domain-registry.yml` |
| [`sa/`](sa/) | Solution Architect | Solution repo | `SOLUTION.md`, `solution-index.yml`, `domain-workstreams.yml` |
| [`da/`](da/) | Domain Architect | Domain repo | `DOMAIN.md`, `domain-implementations.yml` |
| [`dev/`](dev/) | Developer | Implementation repo | `AGENTS.md`, `CLAUDE.md` (points agents to the Domain repo for context) |

## How to use

1. Copy the relevant pack folder contents into your repo root.
2. Replace all `<placeholder>` values with your repo-specific values.
3. Commit.

Placeholders follow the pattern `<kebab-case-description>`. Common ones:

| Placeholder | Description |
| - | - |
| `<org>` | GitHub organisation name |
| `<enterprise-id>` | Stable enterprise identifier |
| `<solution-key>` | Stable kebab-case solution key |
| `<domain-id>` | Stable kebab-case domain identifier |
| `<initiative-id>` | Stable kebab-case initiative identifier |
| `<enterprise-repo-url>` | Full URL to the enterprise repo |

## Pack layout

```text
packs/
|-- ea/                              <- Enterprise repo
|   |-- AGENTS.md
|   |-- CLAUDE.md
|   |-- ENTERPRISE.md
|   `-- architecture/
|       |-- portfolio/
|       |   `-- initiatives.yml
|       `-- enterprise/
|           `-- domain-registry.yml
|
|-- sa/                              <- Solution repo
|   |-- AGENTS.md
|   |-- CLAUDE.md
|   |-- SOLUTION.md
|   |-- solution-index.yml
|   `-- architecture/
|       `-- solution/
|           `-- domain-workstreams.yml
|
|-- da/                              <- Domain repo
|   |-- AGENTS.md
|   |-- CLAUDE.md
|   |-- DOMAIN.md
|   `-- domain-implementations.yml
|
`-- dev/                             <- Implementation repo
    |-- AGENTS.md
    `-- CLAUDE.md
```
