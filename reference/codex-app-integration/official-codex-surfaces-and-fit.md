# Official Codex Surfaces And Fit

## Question

Does the `enterprise.md` convention fit the official Codex product model?

## Short Answer

Yes, but as an adapter layer over Codex rather than as a direct modification of the stock Codex App client.

## Closest Official Surfaces

1. `AGENTS.md`
   - repo-local behavior contract
   - natural fit for Layer A entry guidance
2. Skills
   - best fit for deterministic routing helpers and reusable workflow logic
3. Config and managed configuration
   - best fit for policy knobs, default bootstrap sources, and fail-closed settings
4. Codex App Server
   - best fit for a rich client or enterprise wrapper experience
5. Codex SDK
   - best fit for service-side integration and backend orchestration

## What Fits Cleanly

1. Layer A entrypoint-aware navigation
2. Layer B deterministic selector-based routing
3. fail-closed routing behavior
4. profile-based adoption
5. Git artifacts as the shared context surface

## What Does Not Need To Change In Codex

1. the reasoning model
2. the core thread concept
3. the local repo-attached workflow model

## Main Implementation Idea

Implement the convention as:

1. a routing skill or router service
2. a thread-launch or thread-switch helper
3. a thin UI layer that shows routed context

Not as:

1. a heuristic repo crawler
2. a hidden cross-thread memory mechanism
3. a replacement for canonical Git artifacts
