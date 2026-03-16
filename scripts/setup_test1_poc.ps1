[CmdletBinding()]
param(
    [string]$RemoteRepoUrl,
    [string]$TargetPath
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($RemoteRepoUrl)) {
    $RemoteRepoUrl = Read-Host "Enter the canonical GitHub repository URL to embed in generated files"
}

if ([string]::IsNullOrWhiteSpace($RemoteRepoUrl)) {
    throw "RemoteRepoUrl is required."
}

if ([string]::IsNullOrWhiteSpace($TargetPath)) {
    $defaultTarget = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "..\test1"))
    $TargetPath = Read-Host "Enter the target directory to create the PoC in [$defaultTarget]"
    if ([string]::IsNullOrWhiteSpace($TargetPath)) {
        $TargetPath = $defaultTarget
    }
}

$target = [System.IO.Path]::GetFullPath($TargetPath)

if (!(Test-Path $target)) {
    New-Item -ItemType Directory -Path $target | Out-Null
}

$packMap = @{
    "packs/ea" = (Join-Path $target "ea")
    "packs/sa" = (Join-Path $target "sa")
    "packs/da" = (Join-Path $target "da")
}

foreach ($srcRel in $packMap.Keys) {
    $src = Join-Path $repoRoot $srcRel
    $dst = $packMap[$srcRel]
    if (!(Test-Path $dst)) {
        New-Item -ItemType Directory -Path $dst -Force | Out-Null
    }
    Copy-Item -Path (Join-Path $src "*") -Destination $dst -Recurse -Force
}

$implDirs = @(
    (Join-Path $target "implementations/order-api"),
    (Join-Path $target "implementations/order-events")
)

foreach ($dir in $implDirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Set-Content -Path (Join-Path $target "implementations/order-api/README.md") -Encoding UTF8 -Value @"
# order-api

PoC implementation directory for the order API.
"@

Set-Content -Path (Join-Path $target "implementations/order-events/README.md") -Encoding UTF8 -Value @"
# order-events

PoC implementation directory for order event processing.
"@

$eaEnterprise = Join-Path $target "ea/ENTERPRISE.md"
$eaAgents = Join-Path $target "ea/AGENTS.md"
$eaClaude = Join-Path $target "ea/CLAUDE.md"
$eaInitiatives = Join-Path $target "ea/architecture/portfolio/initiatives.yml"
$eaRegistry = Join-Path $target "ea/architecture/enterprise/domain-registry.yml"

Set-Content -Path $eaEnterprise -Encoding UTF8 -Value @"
# ENTERPRISE

Monorepo PoC enterprise entrypoint. Routes initiatives to solution directories inside this repository.

## Read First

1. This file - enterprise context and navigation

## Parent

Not applicable

## Critical File Contract

- Keep required section headings from this template.
- Do not rename or delete required sections.
- Keep this file concise: identity, routing semantics, and links.
- Put detailed/mutable operational values in canonical artifacts and link them here.
- If a required section has no content, keep it and write `Not applicable`.

## Knowledge Store Layout

```text
ea/
|-- ENTERPRISE.md
|-- AGENTS.md
|-- CLAUDE.md
`-- architecture/
    |-- portfolio/
    |   `-- initiatives.yml
    `-- enterprise/
        `-- domain-registry.yml
sa/
|-- SOLUTION.md
|-- solution-index.yml
`-- architecture/solution/domain-workstreams.yml
da/
|-- DOMAIN.md
`-- domain-implementations.yml
implementations/
|-- order-api/
`-- order-events/
```

## Canonical Artifacts

- `ea/architecture/portfolio/initiatives.yml` (runtime routing selector)
- `ea/architecture/enterprise/domain-registry.yml` (enterprise domain governance)

## Routing

`INITIATIVE_ID` -> `ea/architecture/portfolio/initiatives.yml` -> `solution_repo_url` + `solution_entrypoint`

## Policy

- Active-only routing; fail-closed on non-active status.
- Resolve solution targets from `ea/architecture/portfolio/initiatives.yml`.
"@

Set-Content -Path $eaAgents -Encoding UTF8 -Value @"
# AGENTS

Role: ea
Instruction: Always read `ENTERPRISE.md` (mandatory entrypoint for this level).
"@

Set-Content -Path $eaClaude -Encoding UTF8 -Value @"
# CLAUDE

Role: ea
Bootstrap: Read `AGENTS.md` first.
Instruction: Then read `ENTERPRISE.md` (mandatory entrypoint for this level).
Guardrail: `AGENTS.md` and `ENTERPRISE.md` remain the canonical contract files. Keep mutable operational detail in linked canonical artifacts, not in `CLAUDE.md`.
"@

Set-Content -Path $eaInitiatives -Encoding UTF8 -Value @"
version: "1.0"
initiatives:
  - initiative_id: init-order-modernization
    name: Order Modernization PoC
    status: active
    owner: solution-architecture
    solution_repo_url: $RemoteRepoUrl
    solution_entrypoint: sa/SOLUTION.md
"@

Set-Content -Path $eaRegistry -Encoding UTF8 -Value @"
version: "1.0"
domains:
  - domain_id: order-management
    domain_name: Order Management
    status: active
    owner: domain-architecture
    domain_repo_url: $RemoteRepoUrl
    domain_entrypoint: da/DOMAIN.md
"@

$saSolution = Join-Path $target "sa/SOLUTION.md"
$saAgents = Join-Path $target "sa/AGENTS.md"
$saClaude = Join-Path $target "sa/CLAUDE.md"
$saIndex = Join-Path $target "sa/solution-index.yml"
$saWorkstreams = Join-Path $target "sa/architecture/solution/domain-workstreams.yml"

Set-Content -Path $saSolution -Encoding UTF8 -Value @"
# SOLUTION

Monorepo PoC solution entrypoint. Owns the SA baseline and routes domain workstreams to domain directories in this repository.

## Read First

1. This file - solution context and navigation

## Parent

- [ENTERPRISE](../ea/ENTERPRISE.md)

## Critical File Contract

- Keep required section headings from this template.
- Do not rename or delete required sections.
- Keep this file concise: identity, routing semantics, and links.
- Put detailed/mutable operational values in canonical artifacts and link them here.
- If a required section has no content, keep it and write `Not applicable`.

## Knowledge Store Layout

```text
SOLUTION.md
AGENTS.md
solution-index.yml
architecture/
`-- solution/
    `-- domain-workstreams.yml
```

## Canonical Artifacts

- `solution-index.yml`
- `architecture/solution/domain-workstreams.yml`

## Routing

`WORKSTREAM_ID` -> `architecture/solution/domain-workstreams.yml` -> `workstream_repo_url` + `workstream_entrypoint`

## Scope

- Solution key: order-poc
- Owners: SA: solution-architecture, Domains: order-management
"@

Set-Content -Path $saAgents -Encoding UTF8 -Value @"
# AGENTS

Role: sa
Instruction: Always read `SOLUTION.md` (mandatory entrypoint for this level).
"@

Set-Content -Path $saClaude -Encoding UTF8 -Value @"
# CLAUDE

Role: sa
Bootstrap: Read `AGENTS.md` first.
Instruction: Then read `SOLUTION.md` (mandatory entrypoint for this level).
Guardrail: `AGENTS.md` and `SOLUTION.md` remain the canonical contract files. Keep mutable operational detail in linked canonical artifacts, not in `CLAUDE.md`.
"@

Set-Content -Path $saIndex -Encoding UTF8 -Value @"
version: "0.2"
solution_key: order-poc
display_name: Order Modernization PoC
description: Monorepo proof of concept for EA to SA to DA routing.
owners:
  solution_architect: solution-architecture
  enterprise_id: test1-monorepo
entrypoints:
  solution_md: SOLUTION.md
  agents_md: AGENTS.md
  cascade_state: .openarchitect/cascade-state.yml
domains:
  - domain_key: order-management
    oda_component: Order Management
    domain_repo:
      repo_url: $RemoteRepoUrl
      entrypoints:
        domain_md: da/DOMAIN.md
        agents_md: da/AGENTS.md
        cascade_state: .openarchitect/cascade-state.yml
    tmf_apis: []
repos:
  - repo_key: monorepo
    repo_url: $RemoteRepoUrl
    purpose: design-and-poc
    description: Single repository PoC containing EA, SA, DA, and implementation directories.
    entrypoints:
      solution_md: sa/SOLUTION.md
      agents_md: sa/AGENTS.md
      cascade_state: .openarchitect/cascade-state.yml
"@

Set-Content -Path $saWorkstreams -Encoding UTF8 -Value @"
version: "1.0"
workspace_id: test1-monorepo
initiative_id: init-order-modernization
generated_at_utc: 2026-03-14T00:00:00Z
generated_by: codex
workstreams:
  - workstream_id: ws-init-order-modernization-order-management
    workstream_uuid: 11111111-1111-4111-8111-111111111111
    initiative_id: init-order-modernization
    domain_id: order-management
    domain_name: Order Management
    oda_component_name: Order Management
    name: Order Modernization x Order Management
    workstream_entrypoint: da/DOMAIN.md
    workstream_git_ref: main
    workstream_repo_url: $RemoteRepoUrl
    workstream_path: da/
    tmfc_component_id: TMFC005
    handoff_ref: poc-order-management
    status: active
    owner: domain-architecture
    metadata:
      priority: high
      milestone: 2026-q1
execution:
  state: not_started
  processed_workstreams: []
  skipped_workstreams: []
notes: Monorepo proof of concept.
"@

$daDomain = Join-Path $target "da/DOMAIN.md"
$daAgents = Join-Path $target "da/AGENTS.md"
$daClaude = Join-Path $target "da/CLAUDE.md"
$daImpl = Join-Path $target "da/domain-implementations.yml"

Set-Content -Path $daDomain -Encoding UTF8 -Value @"
# DOMAIN

Monorepo PoC domain entrypoint. Owns domain design baselines and routes to implementation directories in this repository.

## Read First

1. This file - domain context and navigation

## Parent

- [ENTERPRISE](../ea/ENTERPRISE.md)

## Critical File Contract

- Keep required section headings from this template.
- Do not rename or delete required sections.
- Keep this file concise: identity, routing semantics, and links.
- Put detailed/mutable operational values in canonical artifacts and link them here.
- If a required section has no content, keep it and write `Not applicable`.

## Knowledge Store Layout

```text
DOMAIN.md
AGENTS.md
domain-implementations.yml
../implementations/
|-- order-api/
`-- order-events/
```

## Canonical Artifacts

- `domain-implementations.yml`

## Routing

`implementation_id` -> `domain-implementations.yml` -> `repo.url` + `repo.paths` + optional `repo.entrypoint` + optional `repo.git_ref`

## Policy

- Treat selector inputs as authoritative (`implementation_id`).
- Fail-closed on inactive status by default.
"@

Set-Content -Path $daAgents -Encoding UTF8 -Value @"
# AGENTS

Role: da
Instruction: Always read `DOMAIN.md` (mandatory entrypoint for this level).
"@

Set-Content -Path $daClaude -Encoding UTF8 -Value @"
# CLAUDE

Role: da
Bootstrap: Read `AGENTS.md` first.
Instruction: Then read `DOMAIN.md` (mandatory entrypoint for this level).
Guardrail: `AGENTS.md` and `DOMAIN.md` remain the canonical contract files. Keep mutable operational detail in linked canonical artifacts, not in `CLAUDE.md`.
"@

Set-Content -Path $daImpl -Encoding UTF8 -Value @"
spec_name: multi-scale-routing
spec_version: "1.0.0"
implementations:
  - implementation_id: order-api
    status: active
    repo:
      paths: ["implementations/order-api/*"]
      entrypoint: implementations/order-api/README.md
      git_ref: main
    owners: [domain-architecture]

  - implementation_id: order-events
    status: active
    repo:
      paths: ["implementations/order-events/*"]
      entrypoint: implementations/order-events/README.md
      git_ref: main
    owners: [domain-architecture]
"@

Set-Content -Path (Join-Path $target "README.md") -Encoding UTF8 -Value @"
# test1

Monorepo proof of concept for the enterprise.md routing convention.

Layout:
- `ea/` enterprise context
- `sa/` solution context
- `da/` domain context
- `implementations/` implementation directories resolved by the domain catalog

Recommended reading order:
1. `ea/AGENTS.md`
2. `ea/ENTERPRISE.md`
3. `sa/SOLUTION.md`
4. `da/DOMAIN.md`
"@

Write-Output "Created monorepo PoC at: $target"
Get-ChildItem -Recurse -File $target | ForEach-Object { $_.FullName.Substring($target.Length + 1) }
