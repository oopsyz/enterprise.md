# AGENTS

Role: ea
Instruction: After reading this file, read `ENTERPRISE.md` (mandatory entrypoint).
Guardrail: `ENTERPRISE.md` is a critical contract file. Preserve template section structure and keep mutable operational detail in linked canonical artifacts.
References:
- `ENTERPRISE.md` - enterprise-level entrypoint
- `initiatives.yml` - enterprise-to-solution routing catalog
Bootstrap:
- Set `EA_REPO_URL` to this repository's clone URL for runtime discovery.

