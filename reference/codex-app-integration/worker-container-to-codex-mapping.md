# Worker Container To Codex Mapping

## Current Worker Container Model

The current `worker_container` setup already behaves like a routing adapter:

1. one runtime instance is associated with one repo context
2. startup resolves selector inputs such as `INITIATIVE_ID`, `WORKSTREAM_ID`, and `WORK_ITEM_ID`
3. canonical YAML catalogs determine the target repo
4. different humans can attach to different runtime instances independently

This is operationally clean because it provides hard context isolation.

## Codex Thread Equivalence

A repo-attached Codex App thread is close to the same conceptual unit:

1. one thread is attached to one repo
2. one thread carries one local conversation history
3. one thread can stay focused on one architecture level or workstream

This means the cleanest Codex integration model is not "one thread manages everything."

It is:

1. one repo-attached thread per routed context
2. deterministic routing from one thread to another
3. shared context through canonical Git artifacts

## Practical Mapping

`worker_container` concept -> Codex-oriented concept

1. container startup resolver -> thread target resolver
2. `opencode serve` instance -> repo-attached Codex thread
3. `opencode attach` -> open or switch to the routed Codex thread
4. env-based selector context -> structured thread context
5. compose/runtime isolation -> thread/repo isolation

## Why This Matters

This avoids forcing one developer or one Codex thread to keep a mental map of many simultaneous routed contexts.

Instead:

1. enterprise work can stay in an EA thread
2. solution work can stay in an SA thread
3. domain work can stay in a DA thread
4. coordination happens through the standard's files rather than hidden thread memory
