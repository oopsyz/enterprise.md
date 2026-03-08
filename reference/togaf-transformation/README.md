# TOGAF Transformation Vision

This folder stores working material on how the Multi-Level Repository Navigation and Routing Convention, combined with LLMs, could transform how enterprises practice TOGAF.

## Position

The goal is not simply to apply the convention to TOGAF artifacts. The goal is to use the convention plus LLMs to shift TOGAF from a document-centric method into an executable architecture operating model.

TOGAF continues to provide:

- the architecture method
- the content concepts
- the governance intent
- the decision rights of enterprise architects

The convention plus LLMs add:

- deterministic navigation across enterprise, solution, and domain levels
- machine-readable routing between architecture contexts
- policy-constrained agent execution
- continuous validation and traceability across repositories

## Transformation Thesis

TOGAF becomes an architecture control plane for humans and agents.

The convention supplies deterministic structure. LLMs supply interpretation, synthesis, and execution within that structure.

In this model, EA shifts from an advisory function toward an operating system for enterprise change.

## Example Stack

The rest of this document uses one example realization to make the transformation concrete.

It is not part of the convention itself, and it is not required for adoption.

Five components make this concrete:

1. **Convention** (`enterprise.md`): navigation and routing rules - entrypoints, routing catalogs, fail-closed policy, status vocabulary, ownership model.
2. **Current-state graph** (`enterprise-state`): live enterprise topology in Postgres plus Apache AGE with append-only provenance, governance constraints, and release lifecycle management.
3. **Reference knowledge base** (`vector_service`): TM Forum ODA/eTOM/SID/API standards ingested into Postgres with pgvector embeddings and Apache AGE graph traversal - semantically searchable by agents.
4. **Worker container** (`worker_container`): role-based container runtime that resolves convention selectors (`initiative_id`, `workstream_id`, `work_item_id`) to target repositories and starts an LLM agent at the correct architecture level.
5. **LLM**: reasoning, synthesis, and gap analysis - the model queries both the reference knowledge base and the current-state graph, and the gap analysis is the reasoning itself.

These five components form a distributed, agent-native Architecture Repository connected by shared identifiers and fail-closed routing.

## How the Convention Enables This

The convention is the structural foundation. Without it, the other components are useful but disconnected. With it:

- **Deterministic navigation**: an agent reads `AGENTS.md` then the level entrypoint, knows where it is in the architecture hierarchy, and can reach any other level without guessing.
- **Progressive disclosure**: the agent loads only what it needs - entrypoint (map), linked artifacts (detail), routing catalogs (traversal). This is context engineering for architecture.
- **Shared identity**: `initiative_id`, `workstream_id`, `domain_id`, and other stable identifiers are the join keys across the stack. Without convention-enforced stable identifiers, every cross-repo query is a fuzzy match.
- **Fail-closed routing**: the agent either resolves the selector or stops. No hallucinated targets and no inferred context.
- **Status vocabulary**: routable vs non-routable statuses (`active`, `in_progress` vs `paused`, `deprecated`) give agents and governance the same shared language for what can flow and what is blocked.

## What Changes

### 1. ADM becomes computationally enacted

ADM outputs stop behaving like static deliverables and become live, routable context for downstream work.

### 2. The Architecture Repository becomes distributed and computational

The Architecture Repository can be decomposed into navigation, state, and knowledge concerns connected by shared identifiers. That makes it more accessible to automation while keeping artifacts governed.

### 3. Governance moves toward encoded policy

Review boards do not disappear, but their role shifts upward:

- less manual interpretation of disconnected documents
- more definition of approval states, routing policy, ownership, and control rules

### 4. Traceability becomes native and auditable

Lineage from enterprise intent to solution workstream to domain implementation can be reconstructed from selectors, entrypoints, and governed artifacts.

### 5. Architecture work becomes agent-executable

Agents can enter at the correct level, resolve the correct context, and operate within explicit governance constraints rather than relying on ad hoc human handoff.

### 6. Business motivation becomes structured context

Business motivation can be captured as human-authored markdown files in the enterprise repository - for example `VISION.md`, `DRIVERS.md`, and `GOALS.md` - linked from `ENTERPRISE.md`. The convention's progressive disclosure still applies: `ENTERPRISE.md` is the map, and motivation files are the detail.

## EA and Business Change

This model can make EA materially more valuable to the business because EA no longer stops at description and review.

EA can work with business stakeholders to operationalize business change:

- business intent is captured at the enterprise level
- agents resolve the affected solution and domain contexts deterministically
- downstream implementation targets are located through governed catalogs
- change can move from business decision to prepared implementation far faster than traditional handoffs

Under the right controls, a business-level change can propagate from intent to governed implementation quickly enough to approach near-real-time delivery. That outcome depends on automated testing, approval policy, deployment controls, and production safety mechanisms. The convention does not replace those controls; it gives agents a reliable path through them.

This makes EA tangible in operational terms. EA becomes the steward of the enterprise execution model rather than only the author of architecture documents.

## The Architect's Role

The architect's work shifts from producing architecture artifacts to curating the architecture system:

- from drawing target architecture diagrams to curating the structure, identifiers, and relationships that agents rely on
- from writing architecture decision records to encoding decisions as constraints and routing policies
- from conducting gap analysis workshops to reviewing agent-generated assessments and validating results
- from presenting every artifact for approval to defining governance controls that enforce policy continuously
- from handing off work packages manually to configuring routing catalogs so work flows deterministically

The architect becomes the person who teaches the system what good architecture looks like rather than the person who manually produces and polices every deliverable.

## Boundaries

This vision does not imply:

- replacing enterprise architects
- replacing architectural judgment
- replacing TOGAF content, principles, or viewpoints

It changes the operating model around TOGAF:

- from static repository to navigable architecture fabric
- from manual handoff to deterministic routing
- from periodic review to continuous policy enforcement
- from document-heavy coordination to agent-assisted execution
- from advisory architecture to operationalized business change

## Contents

- [TOGAF Mapping](togaf-mapping.md): detailed mapping of convention concepts to TOGAF concepts, ADM phases, and Architecture Repository concerns.

## Short Form

TOGAF gave enterprises a method.

LLMs need an execution substrate.

This convention can be that substrate.
