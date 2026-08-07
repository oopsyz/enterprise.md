# PLATFORM

Platform architecture repository entrypoint for `<platform-id>`.

## Read First

1. This file

## Parent

- [ENTERPRISE](<enterprise-repo-url>/blob/main/ENTERPRISE.md)

## Canonical Artifacts

- `platform-implementations.yml`
- `architecture/platforms/<platform-id>/platform-design.yml`
- `architecture/platforms/<platform-id>/connection-catalog.yml`

## Integration Ownership

Platform owns operated `connection_id` realizations. The providing Domain or
component retains ownership of semantic contracts identified by `interface_id`.

## Policy

Fail closed on missing, ambiguous, inactive, or unverified selectors and
artifact references.
