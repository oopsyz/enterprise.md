# AGENTS

Role: ea
Instruction: Always read `ENTERPRISE.md` (mandatory entrypoint for this level).
Guardrail: `ENTERPRISE.md` is a critical contract file. Preserve template section structure and keep mutable operational detail in linked canonical artifacts.
References:

- `ENTERPRISE.md` - enterprise-level entrypoint
- `initiatives.yml` - enterprise-to-solution routing catalog
- `domain-registry.yml` - domain governance registry

Bootstrap:

- Set `EA_REPO_URL` to this repository's clone URL for runtime discovery.
