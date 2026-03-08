# TOGAF Mapping

This document maps the Multi-Level Repository Navigation and Routing Convention to TOGAF concepts.

Scope:

- convention concepts only
- no implementation-specific repository names
- useful to adopters regardless of toolchain or runtime stack

It is a mapping document, not a claim that the convention replaces TOGAF.

## Core Mapping

| Convention concept | Closest TOGAF concept | Practical impact |
|---|---|---|
| `ENTERPRISE.md`, `SOLUTION.md`, `DOMAIN.md` entrypoints | Architecture Repository navigation, architecture partitioning, architecture context | Gives each architecture level a stable starting point for humans and agents. |
| `initiatives.yml`, `domain-workstreams.yml`, `implementation-catalog.yml` | Architecture Repository catalogs, work package decomposition, migration planning artifacts | Turns architecture handoffs into machine-readable routing artifacts. |
| Status vocabulary (`active`, `in_progress`, `paused`, etc.) | Governance state, implementation status, change lifecycle | Creates a shared operational language for what can progress and what must stop. |
| Fail-closed routing policy | Architecture Governance, compliance control, change control discipline | Prevents ambiguous or unauthorized routing decisions from being silently accepted. |
| Ownership model (EA, SA, DA, repository owners) | Architecture Capability, governance roles, accountability model | Makes stewardship of architecture artifacts explicit instead of implicit. |
| Conformance profiles (A, B, C) | Capability maturity and adoption patterns | Lets organizations adopt lightweight navigation first, then add routing and governance. |

## Architecture Repository

TOGAF defines an Architecture Repository as a logical store of architecture assets. The convention does not replace that repository. It adds structure around how repository artifacts are entered, connected, and governed.

The mapping is:

| TOGAF repository concern | Convention contribution |
|---|---|
| Repository navigation | Level entrypoints provide deterministic starting points by architecture level. |
| Catalog structure | YAML routing catalogs provide canonical, machine-readable selector manifests. |
| Governance traceability | Status vocabulary, ownership, and fail-closed rules make governance state operational. |
| Repository partitioning | Enterprise, solution, and domain entrypoints separate concerns while preserving lineage. |

The key shift is that the repository becomes easier for humans and agents to traverse consistently.

## ADM Mapping

The convention does not redefine the ADM. It changes how ADM outputs can be organized and handed off.

### Preliminary and Phase A

| TOGAF concern | Convention mapping |
|---|---|
| Enterprise context | `ENTERPRISE.md` as the enterprise navigation entrypoint |
| Initiative identification | `initiatives.yml` selectors and statuses |
| Initial governance framing | ownership model plus routable vs non-routable states |

### Phases B, C, and D

| TOGAF concern | Convention mapping |
|---|---|
| Architecture decomposition | `SOLUTION.md` and `DOMAIN.md` separate solution and domain concerns |
| Cross-domain handoff | `domain-workstreams.yml` routes solution intent to domain workstreams |
| Context discovery | progressive disclosure through entrypoints and linked artifacts |

### Phases E and F

| TOGAF concern | Convention mapping |
|---|---|
| Work package and transition planning | routing catalogs define the next stable target |
| Migration state | status vocabulary expresses whether work is routable, paused, or historical |
| Implementation targeting | `implementation-catalog.yml` resolves work items or APIs to implementation locations where that routing boundary is in scope |

### Phases G and H

| TOGAF concern | Convention mapping |
|---|---|
| Governance control | fail-closed routing and versioning discipline |
| Change control | selector uniqueness, non-routable states, and conflict precedence |
| Governed adoption | Profile C adds governance-oriented artifacts and tighter operational control |

The practical implication is that architecture handoffs become more deterministic and less dependent on manual interpretation.

## Architecture Governance

This is where the convention has the strongest TOGAF alignment.

| Convention mechanism | TOGAF governance effect |
|---|---|
| Fail-closed routing | ambiguous or invalid decisions are blocked instead of guessed |
| Selector uniqueness | routing integrity becomes verifiable |
| Status vocabulary | governance policy can distinguish what is writable, routable, or read-only |
| Ownership model | accountability for architecture artifacts is explicit |
| Conflict precedence | competing artifacts have defined resolution order |
| Recommended CI validation | governance checks can move closer to continuous enforcement |

This does not remove review boards or architects. It moves some governance from interpretation into policy.

## Architecture Content Framework

TOGAF includes catalogs, matrices, and diagrams as core content forms. The convention primarily strengthens the catalog side of that model.

| TOGAF content type | Convention effect |
|---|---|
| Catalogs | become machine-readable and selector-driven |
| Matrices | remain external, but can be derived more consistently from linked artifacts and catalog relationships |
| Diagrams | remain external, but entrypoints and catalogs make their context easier to locate and govern |

So the convention does not replace architecture content. It makes content easier to organize, route, and validate.

## Architecture Capability

The convention gives TOGAF's Architecture Capability concept more operational shape.

| TOGAF capability concern | Convention support |
|---|---|
| Role clarity | EA, SA, DA, and repository-owner responsibilities are explicit |
| Operating model | each architecture level has a defined entrypoint and artifact set |
| Adoption maturity | Profiles A, B, and C provide a staged path from lightweight to governed practice |
| Tool independence | the convention remains additive and does not require a specific EA suite |

## Enterprise Continuum

The convention is not a direct replacement for the Enterprise Continuum, but it aligns with the same need to move between broader and more specific architectural contexts.

The closest mapping is:

- enterprise level for broad portfolio and coordination context
- solution level for scoped architecture coordination
- domain level for implementation-adjacent architecture context

The important contribution is progressive disclosure: each level reveals only the next relevant context instead of forcing every consumer to load everything at once.

## Limits of the Mapping

This mapping should be read carefully.

The convention does not provide:

- TOGAF's full metamodel
- a complete set of TOGAF deliverables
- business, data, application, and technology viewpoints by itself
- a substitute for architecture judgment

What it does provide is a structured navigation and governance layer that can make TOGAF-style architecture work more operational, more traceable, and more usable by automation.

## Bottom Line

TOGAF defines the architecture method and governance intent.

The convention adds deterministic entrypoints, routing catalogs, status semantics, ownership, and fail-closed control.

That makes TOGAF artifacts easier to locate, connect, govern, and traverse in multi-repository environments.
