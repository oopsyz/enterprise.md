---
name: ea-convention
version: "1.0.0"
description: >
  Use this skill when the user wants to manage, validate, or navigate the
  ea/sa/da/dev enterprise convention artifacts. Triggers include: adding an
  initiative, domain, workstream, implementation, or roadmap item; validating
  referential integrity; tracing a routing chain; or reviewing the status of
  any layer. Keywords: initiative, domain, workstream, implementation, roadmap,
  ea, sa, da, domain-registry, domain-workstreams, domain-implementations,
  domain-roadmap, convention, routing, referential integrity.
---

# Enterprise Convention Skill

Manages the three-layer enterprise convention: **EA** (Enterprise Architecture) →
**SA** (Solution Architecture) → **DA** (Domain Architecture), with **dev** as
an execution role under DA where coding agents operate.

## Template Files

All file templates are in `{skill_base_dir}/templates/`. Always read from these
files when creating convention artifacts — never use ad-hoc content.

| Template file | Used for |
| --- | --- |
| `ENTERPRISE.md.template` | EA entrypoint |
| `SOLUTION.md.template` | SA entrypoint |
| `DOMAIN.md.template` | DA domain entrypoint |
| `AGENTS.ea.md.template` | EA AGENTS.md |
| `AGENTS.sa.md.template` | SA AGENTS.md |
| `AGENTS.da.md.template` | DA AGENTS.md |
| `AGENTS.dev.md.template` | DEV AGENTS.md |
| `CLAUDE.ea.md.template` | EA CLAUDE.md |
| `CLAUDE.sa.md.template` | SA CLAUDE.md |
| `CLAUDE.da.md.template` | DA CLAUDE.md |
| `CLAUDE.dev.md.template` | DEV CLAUDE.md |
| `initiatives.yml.template` | EA initiatives selector |
| `domain-registry.yml.template` | EA domain registry |
| `solution-index.yml.template` | SA solution index |
| `domain-workstreams.yml.template` | SA workstream selector |
| `domain-implementations.yml.template` | DA implementation selector |

When using a template, read the file and substitute placeholder values (e.g.
`<enterprise-repo-url>`, `<solution-key>`, `<workspace-id-or-null>`) with real
values provided by the user. Strip comment lines (starting with `#`) from YAML
templates before writing.

## Layout Assumption

> **Important:** The spec defines canonical artifact *types* but not their file
> paths — path placement is implementation-defined
> (`enterprise_repo_convention.md` Section 5). This skill assumes the reference
> layout below. Repos using a different layout must supply explicit paths to the
> VALIDATE operation and adjust ADD/INIT scaffolding accordingly.

| Artifact | Reference path (this skill's default) |
| --- | --- |
| Initiatives selector | `ea/architecture/portfolio/initiatives.yml` |
| Domain registry | `ea/architecture/enterprise/domain-registry.yml` |
| Solution index | `sa/solution-index.yml` |
| Workstream selector | `sa/architecture/solution/domain-workstreams.yml` |
| DA domain root | `da/{domain}/` |

## Convention Overview

| Layer | Entrypoint | Canonical Artifacts |
| ------- | ------------ | --------------------- |
| EA | `ENTERPRISE.md` | `initiatives.yml`, `domain-registry.yml` |
| SA | `SOLUTION.md` | `solution-index.yml`, `domain-workstreams.yml` |
| DA | `DOMAIN.md` | `domain-implementations.yml` |

### Routing Chain

```text
INITIATIVE_ID
  → initiatives.yml → solution_entrypoint
    → domain-workstreams.yml → workstream_entrypoint
      → domain-implementations.yml → repo.url + repo.paths + repo.entrypoint
```

**Policy:** fail-closed on `status: inactive`. Only `status: active` entries are routable.

### Workstream Semantics

- A domain may have **multiple workstreams** from different initiatives.
- A workstream is a **demand unit** against a domain, not a unique implementation unit.
- `domain-workstreams.yml` is dual-purpose: deterministic routing metadata + inbound demand signals.
- The **domain architect** reconciles competing workstreams into a coherent domain change plan.
- DA runtime identity is **domain-scoped**: `domain_id` is the canonical DA session and ownership identity, not `workstream_id`.
- `domain_repo_url` identifies the **owning domain repository target** for the workstream, not a separate DA container or runtime identity. When `domain-registry.yml` is present, its `domain_repo_url` is authoritative and any copy in `domain-workstreams.yml` must match it.
- A workstream handoff is attachable to an existing domain-scoped DA session; it does not create a new ownership boundary.

### Three-Artifact Domain Chain (proposed)

> `domain-roadmap.yml` is a **proposed convention extension** not yet ratified
> in the main spec. It is supported by this skill but should not be treated as
> normative until added to `enterprise_repo_convention.md`.

1. `domain-workstreams.yml` — inbound demand + routing (owned by `sa`, in spec)
2. `domain-roadmap.yml` — planning and sequencing (owned by `da`, **proposed**)
3. `domain-implementations.yml` — implementation target mapping (owned by `da`, in spec)

### Referential Integrity Rules

- `domain-workstreams.yml[].initiative_id` → must exist in `initiatives.yml[].initiative_id`
- `domain-workstreams.yml[].domain_id` → must exist in `domain-registry.yml[].domain_id`
- `domain-workstreams.yml[].workstream_entrypoint` → must be a real file path
- `domain-roadmap.yml[].workstream_ids[]` → each must exist in `domain-workstreams.yml[].workstream_id`
- `domain-roadmap.yml[].implementation_ids[]` → each must exist in `domain-implementations.yml[].implementation_id`
- `domain-registry.yml[].domain_entrypoint` → must be a real file path
- `initiatives.yml[].solution_entrypoint` → must be a real file path

---

## Operations

> **Layout note:** All operations below are implemented for the reference layout
> paths listed in the Layout Assumption table above. This skill does not
> auto-detect alternate layouts. If the user's repo uses different paths, they
> must state the actual path for each artifact when invoking the operation, and
> the agent should substitute that path wherever a reference path appears in
> the steps below.
>
> **Getting started — monorepo first:** If you are new to the convention, we
> recommend starting with a **single-repo (monorepo) setup** where EA, SA, DA,
> and dev artifacts all live in one repository. This lets you explore the full
> routing chain — from initiative to implementation — without managing multiple
> repos, cloning, or bootstrap packages. Use INIT to create the EA layer, then
> ADD INITIATIVE and ADD DOMAIN with the "same repo" option to scaffold SA and
> DA alongside it. Once you are comfortable with how the layers connect, you can
> split domains or solutions into their own repos using ONBOARD. The convention
> works identically in both layouts; the only difference is where the files live.

### ONBOARD

Set up an existing external repo to participate in the convention. Use this when
a user provides a repo URL that already has code — the convention artifacts need
to be added to it so AI agents and the routing chain can navigate it.

First ask: which layer does this repo serve?

- `sa` — solution repo (orchestrates a business scenario across domains)
- `da` — domain implementation repo (realizes a specific domain capability)
- `dev` — coding-level repo where agents implement changes (execution role under `da`)

The primary output is a **bootstrap package** — a local folder containing the
convention artifacts for the target repo. The user can copy this into the
external repo manually, or the Post-Scaffold Git Workflow can push it there
directly if git/network access to the target repo is available (see below).

---

#### ONBOARD: SA

Generates bootstrap package at `.convention-bootstrap/sa/` in the current repo.

Required inputs:

- `repo_url`: URL of the existing SA repo
- `initiative_id`: must exist in `initiatives.yml`
- `solution_key`: slug for this solution

Package contents — read each from `templates/`:

- `SOLUTION.md` ← `SOLUTION.md.template` (substitute `<enterprise-repo-url>`, `<solution-key>`)
- `AGENTS.md` ← `AGENTS.sa.md.template`
- `CLAUDE.md` ← `CLAUDE.sa.md.template`
- `solution-index.yml` ← `solution-index.yml.template` (substitute `solution_key`, owners)
- `architecture/solution/domain-workstreams.yml` ← `domain-workstreams.yml.template` (substitute `initiative_id`, set `workstreams: []`)

After generating:

1. Update `initiatives.yml` — set `solution_repo_url` to `repo_url` and `solution_entrypoint` to `SOLUTION.md`.
2. Run the **Post-Scaffold Git Workflow** (handles both pushing to the target repo and the manual-copy fallback).

---

#### ONBOARD: DA

Generates bootstrap package at `.convention-bootstrap/da/{domain_id}/` in the current repo.

Required inputs:

- `repo_url`: URL of the existing DA repo
- `domain_id`: must exist in `domain-registry.yml`

Package contents — read each from `templates/`:

- `DOMAIN.md` ← `DOMAIN.md.template` (substitute `<enterprise-repo-url>`)
- `AGENTS.md` ← `AGENTS.da.md.template`
- `CLAUDE.md` ← `CLAUDE.da.md.template`
- `domain-implementations.yml` ← `domain-implementations.yml.template` (set `implementations: []`, strip examples)

After generating:

1. Update `domain-registry.yml` — set `domain_repo_url` to `repo_url` and `domain_entrypoint` to `DOMAIN.md`.
2. Run the **Post-Scaffold Git Workflow** (handles both pushing to the target repo and the manual-copy fallback).

> `domain-roadmap.yml` is **not** included by default — it is a proposed extension. Use ADD ROADMAP ITEM (under Proposed Extensions) if the domain architect wants to adopt it.

---

#### ONBOARD: DEV

Generates bootstrap package at `.convention-bootstrap/dev/{domain_id}/` in the current repo.

DEV is an execution role under `da`, not a full architecture layer. Package is minimal.

Required inputs:

- `repo_url`: URL of the existing dev repo
- `domain_id`: the domain this repo implements
- `implementation_id`: must exist in `da/{domain_id}/domain-implementations.yml`

Package contents:

- `AGENTS.md` ← `AGENTS.dev.md.template` (substitute `domain_id`, `domain_entrypoint`)
- `CLAUDE.md` ← `CLAUDE.dev.md.template` (substitute `domain_id`, `domain_entrypoint`)
- `README.md` — only if one does not already exist: name, purpose, owning domain, link to `da/{domain_id}/DOMAIN.md`

After generating:

1. Update `da/{domain_id}/domain-implementations.yml` — set `repo.url` to `repo_url`, set `status: active`.
2. Run the **Post-Scaffold Git Workflow** (handles both pushing to the target repo and the manual-copy fallback). Note: if the target repo already has a `README.md`, the Push 2 commit should not overwrite it — warn the user to merge manually.

---

### INIT

Bootstrap a brand new enterprise repo with the full EA layer structure. Use this
when starting from scratch — no existing `ea/` directory.

Required inputs:

- `repo_url`: URL of this repo
- `owner`: team or role name for enterprise architecture

Steps:

1. Confirm `ea/ENTERPRISE.md` does not already exist. If it does, abort and suggest VALIDATE or STATUS instead.
2. Create the following files from `templates/`:
   - `ea/ENTERPRISE.md` ← `ENTERPRISE.md.template`
   - `ea/AGENTS.md` ← `AGENTS.ea.md.template`
   - `ea/CLAUDE.md` ← `CLAUDE.ea.md.template`
   - `ea/architecture/portfolio/initiatives.yml` ← `initiatives.yml.template` (set `initiatives: []`, strip examples)
   - `ea/architecture/enterprise/domain-registry.yml` ← `domain-registry.yml.template` (set `domains: []`, strip examples)
3. Confirm completion and tell the user their next steps: ADD DOMAIN, then ADD INITIATIVE.
4. Run the **Post-Scaffold Git Workflow**.

---

### VALIDATE

Run the bundled validation script against the current repo:

```bash
python "{skill_base_dir}/scripts/validate_convention.py" --root . --repo-url <this-repo-url>
```

The script auto-detects its schema directory from `{skill_base_dir}/references/`.

**If the repo uses a non-default layout**, supply explicit paths:

```bash
python "{skill_base_dir}/scripts/validate_convention.py" \
  --root . \
  --repo-url <this-repo-url> \
  --initiatives <path/to/initiatives.yml> \
  --domain-registry <path/to/domain-registry.yml> \
  --solution-index <path/to/solution-index.yml> \
  --workstreams <path/to/domain-workstreams.yml> \
  --da-root <path/to/da-root>
```

All paths are relative to `--root`. Defaults match the reference layout (see Layout Assumption above).

`--repo-url` should be the canonical URL of the repo being validated (e.g. `https://github.com/org/repo`). It is used to distinguish local entrypoints from remote ones. If omitted, remote entrypoint existence checks are skipped rather than producing false positives.

**Schema validation** (requires `jsonschema` — skipped gracefully if not installed):

- Each canonical YAML conforms to its JSON Schema in `references/`

**Lint validation** (always runs):

- `initiative_id`, `domain_id`, `workstream_id`, `implementation_id` uniqueness
- `domain-workstreams.yml[].initiative_id` → exists in `initiatives.yml`
- `domain-workstreams.yml[].domain_id` → exists in `domain-registry.yml`
- All local entrypoint paths exist on disk
- `domain-roadmap.yml` referential integrity if present (proposed extension — validated but not required)
- Warns on inactive workstreams and implementations missing `repo.url`

Exit code 0 = clean. Exit code 1 = errors. Exit code 2 = missing dependencies.

---

### ROUTE

Trace the full routing chain for a given `initiative_id`.

Steps:

1. Read `ea/architecture/portfolio/initiatives.yml` — find matching `initiative_id`, check `status: active`, output `solution_entrypoint`.
2. Read `sa/architecture/solution/domain-workstreams.yml` — list all workstreams where `initiative_id` matches, show `domain_id`, `status`, `workstream_entrypoint`.
3. For each active workstream, read `da/{domain_id}/domain-implementations.yml` — list active implementations with `repo.url` and `repo.entrypoint`.
4. Display the full chain as a readable trace.

---

### STATUS

Show a summary of all layers.

Steps:

1. Read `ea/architecture/portfolio/initiatives.yml` — list initiatives with `status`.
2. Read `ea/architecture/enterprise/domain-registry.yml` — list domains with `status`.
3. Read `sa/architecture/solution/domain-workstreams.yml` — list workstreams grouped by `domain_id` with `status`.
4. For each domain, read `da/{domain}/domain-implementations.yml` — count active implementations.
5. If `da/{domain}/domain-roadmap.yml` exists — count roadmap items.
6. Display as a layered summary table.

---

### ADD INITIATIVE

Add a new initiative to `ea/architecture/portfolio/initiatives.yml`.

Required fields:

- `initiative_id`: unique, convention: `init-{slug}`
- `name`: human-readable name
- `status`: `active` or `inactive`
- `owner`: team or role name
- `solution_repo_url`: URL of the solution repo
- `solution_entrypoint`: path to `SOLUTION.md`

Steps:

1. Read `ea/architecture/portfolio/initiatives.yml`.
2. Confirm `initiative_id` is not already present.
3. Ask whether the solution lives in the **same repo** or a **separate repo**.
4. Append the new entry (modelled on `initiatives.yml.template` entry shape, values substituted).
5. Write the file.
6. If **same repo**: scaffold SA structure — read templates from `templates/` and create:
   - `sa/SOLUTION.md` ← `SOLUTION.md.template`
   - `sa/AGENTS.md` ← `AGENTS.sa.md.template`
   - `sa/CLAUDE.md` ← `CLAUDE.sa.md.template`
   - `sa/solution-index.yml` ← `solution-index.yml.template` (substitute `solution_key`, `initiative_id`)
   - `sa/architecture/solution/domain-workstreams.yml` ← `domain-workstreams.yml.template` (substitute `initiative_id`, set `workstreams: []`)
7. If **separate repo**: skip scaffolding. Warn that `solution_entrypoint` must exist in the target repo before VALIDATE will pass.
8. Run the **Post-Scaffold Git Workflow** (applies in both same-repo and separate-repo cases, since `initiatives.yml` was modified).

---

### ADD DOMAIN

Add a new domain to the enterprise registry and scaffold its DA structure.

Required fields:

- `domain_id`: unique, convention: `{slug}` e.g. `payments-provider-integration`
- `domain_name`: human-readable name
- `status`: `active` or `inactive`
- `owner`: team or role name
- `domain_repo_url`: URL of the domain repo
- `domain_entrypoint`: path to `DOMAIN.md`

Steps:

1. Read `ea/architecture/enterprise/domain-registry.yml`.
2. Confirm `domain_id` is not already present.
3. Ask whether the domain lives in the **same repo** or a **separate repo**.
4. Append the new entry (modelled on `domain-registry.yml.template` entry shape, values substituted).
5. Write the file.
6. If **same repo**: scaffold DA structure — read templates from `templates/` and create:
   - `da/{domain_id}/DOMAIN.md` ← `DOMAIN.md.template`
   - `da/{domain_id}/AGENTS.md` ← `AGENTS.da.md.template`
   - `da/{domain_id}/CLAUDE.md` ← `CLAUDE.da.md.template`
   - `da/{domain_id}/domain-implementations.yml` ← `domain-implementations.yml.template` (set `implementations: []`, strip examples)
7. If **separate repo**: skip scaffolding. Warn that `domain_entrypoint` must exist in the target repo before VALIDATE will pass.
8. Run the **Post-Scaffold Git Workflow** (applies in both cases, since `domain-registry.yml` was modified).

---

### ADD WORKSTREAM

Add a new workstream to `sa/architecture/solution/domain-workstreams.yml`.

Required fields:

- `workstream_id`: unique, convention: `ws-{initiative_id}-{domain_id}`
- `workstream_uuid`: UUID v4
- `initiative_id`: must exist in `initiatives.yml`
- `domain_id`: must exist in `domain-registry.yml`
- `domain_name`: human-readable domain name
- `name`: workstream display name
- `workstream_entrypoint`: path to domain DOMAIN.md
- `domain_repo_url`: URL of the owning domain repo for self-sufficient routing
- `workstream_path`: path to domain directory
- `status`: `active` or `inactive`

Optional fields:

- `metadata.priority`, `metadata.milestone`

Steps:

1. Read `sa/architecture/solution/domain-workstreams.yml`.
2. Confirm `workstream_id` is not already present.
3. Confirm `initiative_id` exists in `initiatives.yml`.
4. Confirm `domain_id` exists in `domain-registry.yml`.
5. Append the new entry (modelled on `domain-workstreams.yml.template` workstream entry shape).
6. Write the file.
7. Run the **Post-Scaffold Git Workflow**.

---

### ADD IMPLEMENTATION

Add a new implementation target to `da/{domain_id}/domain-implementations.yml`.

First ask: is this an **existing project** (open-source or third-party) or a **custom implementation** (new code)?

#### Case 1: Existing project

Register the pointer only. Repo already exists; the convention does not own it.

Steps:

1. Read `da/{domain_id}/domain-implementations.yml`.
2. Confirm `implementation_id` is not already present.
3. Append the new entry (modelled on the upstream example in `domain-implementations.yml.template`).
4. Write the file.
5. Run the **Post-Scaffold Git Workflow**.

#### Case 2: Custom implementation — same repo (monorepo)

Scaffold a subdirectory for the custom implementation inside the monorepo.

Additional required input:

- `dev_path`: convention: `dev/{domain_id}/{implementation_id}/`

Steps:

1. Read `da/{domain_id}/domain-implementations.yml`.
2. Confirm `implementation_id` is not already present.
3. Scaffold `{dev_path}/`:
   - `README.md` — name, purpose, owning domain
   - `AGENTS.md` ← `AGENTS.dev.md.template` (substitute `domain_id`, `domain_entrypoint`)
   - `CLAUDE.md` ← `CLAUDE.dev.md.template` (substitute `domain_id`, `domain_entrypoint`)
4. Append the new entry with `repo.paths: ["{dev_path}/**"]`, `repo.entrypoint: {dev_path}/README.md`.
5. Write the file.
6. Run the **Post-Scaffold Git Workflow**.

#### Case 3: Custom implementation — separate repo

Generate a bootstrap package the user applies to the new repo.

Steps:

1. Read `da/{domain_id}/domain-implementations.yml`.
2. Confirm `implementation_id` is not already present.
3. Create bootstrap folder at `da/{domain_id}/bootstrap/{implementation_id}/`:
   - `README.md` — name, purpose, owning domain, link to `da/{domain_id}/DOMAIN.md`
   - `AGENTS.md` ← `AGENTS.dev.md.template` (substitute `domain_id`, `domain_entrypoint`)
   - `CLAUDE.md` ← `CLAUDE.dev.md.template`
4. Append entry with `repo.url: "TODO: set repo url"` and `status: inactive`.
5. Write the file.
6. Remind user: set `repo.url` and flip `status: active` once the repo exists.
7. Run the **Post-Scaffold Git Workflow**.

---

## Post-Scaffold Git Workflow

After any operation that creates or modifies convention artifacts, **offer to
push the changes into a branch of the remote repo**.

This workflow applies to two categories of operation:

- **Scaffolding operations** (create new files): INIT, ONBOARD, ADD INITIATIVE
  with same-repo SA scaffolding, ADD DOMAIN with same-repo DA scaffolding,
  ADD IMPLEMENTATION with monorepo scaffolding or bootstrap package.
- **YAML-only operations** (modify existing files): ADD INITIATIVE
  (separate-repo), ADD DOMAIN (separate-repo), ADD WORKSTREAM,
  ADD IMPLEMENTATION case 1 (existing project), ADD ROADMAP ITEM.

Present this as an opt-in prompt, matching the operation type:

> *Scaffolding operations:*
> The convention files have been created locally. Would you like me to commit
> and push them to a new branch so you can open a pull request?
>
> *YAML-only operations:*
> The registry has been updated. Would you like me to commit and push the
> change to a new branch so you can open a pull request?

If the user accepts:

1. **Create a feature branch** from the current branch:
   - Branch naming convention by operation:
     - INIT: `convention/init`
     - ONBOARD SA: `convention/onboard-sa-{solution_key}`
     - ONBOARD DA: `convention/onboard-da-{domain_id}`
     - ONBOARD DEV: `convention/onboard-dev-{domain_id}-{implementation_id}`
     - ADD INITIATIVE: `convention/add-initiative-{initiative_id}`
     - ADD DOMAIN: `convention/add-domain-{domain_id}`
     - ADD WORKSTREAM: `convention/add-workstream-{workstream_id}`
     - ADD IMPLEMENTATION: `convention/add-impl-{domain_id}-{implementation_id}`
     - ADD ROADMAP ITEM: `convention/add-roadmap-{domain_id}-{roadmap_item_id}`
2. **Stage only the files created or modified** by the operation — do not use
   `git add -A` or `git add .`. Use explicit file paths.
3. **Commit** with a descriptive message, e.g.:
   - Scaffolding: `convention: bootstrap EA layer structure`
   - Scaffolding: `convention: onboard SA for solution {solution_key}`
   - Scaffolding: `convention: add domain {domain_id}`
   - YAML-only: `convention: add initiative {initiative_id} (separate repo)`
   - YAML-only: `convention: add domain {domain_id} (separate repo)`
   - YAML-only: `convention: add workstream {workstream_id}`
   - YAML-only: `convention: register implementation {implementation_id} in {domain_id}`
   - YAML-only: `convention: add roadmap item {roadmap_item_id} to {domain_id}`
4. **Push** the branch with `-u` to set tracking:

   ```bash
   git push -u origin <branch-name>
   ```

5. **Offer to open a pull request** using `gh pr create`. If the user accepts,
   create the PR targeting the repo's default branch. Detect it with one of
   these methods (try in order, use the first that succeeds):
   1. `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`
   2. `git rev-parse --abbrev-ref origin/HEAD` (returns e.g. `origin/main` — strip the `origin/` prefix)
   3. Ask the user.

   Create the PR with:
   - Title: short description matching the commit message
   - Body: list of files added/modified and the operation that produced them

If the user declines, skip silently — do not re-prompt.

> **Scope of the push — what goes where:**
>
> - **Same-repo scaffolding** (INIT, ADD INITIATIVE/DOMAIN with same-repo
>   scaffolding, ADD IMPLEMENTATION monorepo): all generated files live
>   permanently in this repo. Push them directly.
>
> - **YAML-only operations** (ADD INITIATIVE separate-repo, ADD DOMAIN
>   separate-repo, ADD WORKSTREAM, ADD IMPLEMENTATION case 1, ADD ROADMAP
>   ITEM): only existing YAML files are modified — no new directories or
>   bootstrap packages. Push the modified file(s) directly. Push 2 does not
>   apply.
>
> - **ONBOARD operations** (SA, DA, DEV) and **ADD IMPLEMENTATION separate-repo**:
>   two pushes are involved — one to the enterprise repo and one to the target repo:
>
>   **Push 1 — Enterprise repo** (registry updates):
>   - Registry files modified by the operation (`initiatives.yml`,
>     `domain-registry.yml`, or `domain-implementations.yml`) belong in the
>     enterprise repo permanently. Push them via the standard workflow above.
>   - Do **not** push the bootstrap package to the enterprise repo — it is a
>     temporary staging area and should be deleted locally after Push 2.
>
>   **Push 2 — Target repo** (bootstrap package → SA, DA, or DEV repo):
>   After Push 1, check whether the agent has git and network access to the
>   target repo (e.g. can it run `git ls-remote <repo_url>`?).
>
>   - **If access is available**, offer to push the bootstrap package directly:
>
>     > Would you like me to clone the target repo, apply the bootstrap package,
>     > and push a branch there?
>
>     If the user accepts:
>     1. Clone the target repo to a temporary directory (e.g.
>        `../tmp/{repo-name}` or a system temp path).
>     2. Copy the bootstrap package contents into the repo root.
>     3. Create a feature branch:
>        - ONBOARD SA: `convention/bootstrap-sa-{solution_key}`
>        - ONBOARD DA: `convention/bootstrap-da-{domain_id}`
>        - ONBOARD DEV: `convention/bootstrap-dev-{implementation_id}`
>        - ADD IMPLEMENTATION separate-repo: `convention/bootstrap-impl-{implementation_id}`
>     4. Stage only the bootstrap files (explicit paths, no `git add -A`).
>     5. Commit with a descriptive message, e.g.
>        `convention: bootstrap SA convention artifacts for {solution_key}`.
>     6. Push the branch with `-u`.
>     7. Offer to open a PR on the target repo via `gh pr create`.
>     8. Clean up: delete the bootstrap package from the enterprise repo
>        (`.convention-bootstrap/` or `da/{domain_id}/bootstrap/`).
>
>   - **If access is not available** (sandboxed environment, no network, auth
>     failure), or the user declines, fall back to the manual path:
>     1. Tell the user: copy the contents of the bootstrap package into the root
>        of the target repo.
>     2. Remind them to clean up the local staging folder
>        (`.convention-bootstrap/` or `da/{domain_id}/bootstrap/`) afterward.
>     3. Suggest running VALIDATE once the target repo has the files.

---

## Error Codes

| Code | Meaning |
| ------ | --------- |
| `ERR_INITIATIVE_NOT_FOUND` | `initiative_id` does not exist in `initiatives.yml` |
| `ERR_DOMAIN_NOT_FOUND` | `domain_id` does not exist in `domain-registry.yml` |
| `ERR_WORKSTREAM_NOT_FOUND` | `workstream_id` does not exist in `domain-workstreams.yml` |
| `ERR_IMPLEMENTATION_NOT_FOUND` | `implementation_id` does not exist in `domain-implementations.yml` |
| `ERR_SELECTOR_DUPLICATE` | ID already exists in the target artifact |
| `ERR_ENTRYPOINT_MISSING` | Referenced file path does not exist |
| `ERR_STATUS_INACTIVE` | Entry exists but `status` is not `active` — fail-closed |

## Decision Rule

- If it defines what must be true in the convention → **Spec Rule**
- If it checks or enforces those rules automatically → **Conformance And Tooling**
- If it is a reusable best practice → **Guidance And Patterns**
- If it only affects the current business scenario → **Solution-Specific Action**

---

## Proposed Extensions

> **These operations produce artifacts that are not yet ratified in
> `enterprise_repo_convention.md`.** Adopting them is optional. The validator
> will check them if they are present but will never require them. Do not
> present these as normative convention requirements.

### ADD ROADMAP ITEM (proposed)

Adds or creates a domain roadmap artifact `da/{domain_id}/domain-roadmap.yml`.
This artifact is useful for domain architects who want to explicitly sequence
inbound workstream demand against implementation targets — but it is not required
by the current spec.

Required fields:

- `roadmap_item_id`: unique within domain, convention: `ri-{domain_id}-{slug}`
- `workstream_ids`: one or more `workstream_id` values (must exist in `domain-workstreams.yml`)
- `implementation_ids`: one or more `implementation_id` values (must exist in `domain-implementations.yml`)
- `status`: `planned`, `in-progress`, or `done`

Optional fields: `name`, `priority`, `milestone`, `notes`

Steps:

1. If `da/{domain_id}/domain-roadmap.yml` does not exist, create it:

   `spec_name: domain-roadmap`, `spec_version: "1.0.0"`, `domain_id: {domain_id}`, `items: []`

2. Read the file.
3. Confirm `roadmap_item_id` is not already present.
4. Validate each `workstream_id` exists in `domain-workstreams.yml`.
5. Validate each `implementation_id` exists in `da/{domain_id}/domain-implementations.yml`.
6. Append the new entry under `items:`.
7. Write the file.
8. Run the **Post-Scaffold Git Workflow**.
