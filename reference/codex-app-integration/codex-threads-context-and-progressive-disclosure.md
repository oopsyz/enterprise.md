# Codex Threads, Shared Context, And Progressive Disclosure

## Thread Isolation

Codex App threads should be treated as isolated working contexts.

That is not a problem for this convention.

## Shared Context Through Artifacts

The standard gives isolated threads a way to coordinate through shared Git artifacts.

Layer A shares navigation context:

1. `AGENTS.md`
2. `ENTERPRISE.md`
3. `SOLUTION.md`
4. `DOMAIN.md`

Layer B shares machine-routable context:

1. `initiatives.yml`
2. `domain-workstreams.yml`
3. `implementation-catalog.yml`

Optional governance artifacts share state and lineage:

1. `domain-registry.yml`
2. `solution-index.yml`
3. `governance-state.yml`

This means one thread does not need live memory from another thread.

It can reconstruct the required context by reading the same canonical artifacts.

## Progressive Disclosure

The convention applies progressive disclosure in three ways.

### 1. Across Repositories

1. start at the highest available level
2. route to a lower-level repo only when needed
3. open a more detailed context only after deterministic resolution

### 2. Across Files

1. `AGENTS.md` tells the agent how to behave locally
2. level entrypoints explain how to navigate at that level
3. routing catalogs disclose the next stable target only when traversal is needed
4. detailed design or implementation files are opened only after landing in the correct target

### 3. Across Detail Levels

1. entrypoints provide orientation
2. selectors provide deterministic routing
3. deep artifacts provide the full design or implementation detail

## Practical Consequence For Codex

The convention turns isolated Codex threads into a coordinated multi-repo system through deterministic artifact-based context sharing.

That is stronger than hidden shared thread memory because it is:

1. explicit
2. auditable
3. deterministic
4. tool-independent
