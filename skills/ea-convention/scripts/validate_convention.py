#!/usr/bin/env python3
"""
Enterprise Convention Validator
Validates referential integrity and schema conformance for ea/sa/da convention artifacts.

Usage:
    python validate_convention.py [--root REPO_ROOT] [--schema-dir SCHEMA_DIR]

Exit codes:
    0  clean
    1  validation errors found
    2  missing required files or import errors
"""

import argparse
import json
import os
import sys
from pathlib import Path

# --- YAML loading ---

try:
    import yaml
    def load_yaml(path):
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# --- Schema validation (optional, requires jsonschema) ---

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# --- Error collection ---

errors = []
warnings = []

def err(code, message, path=None):
    location = f" [{path}]" if path else ""
    errors.append(f"  {code}{location}: {message}")

def warn(message, path=None):
    location = f" [{path}]" if path else ""
    warnings.append(f"  WARN{location}: {message}")

# --- Schema validation ---

def validate_schema(data, schema_path, artifact_path):
    if not HAS_JSONSCHEMA:
        return
    if not schema_path.exists():
        warn(f"Schema file not found, skipping schema check", path=artifact_path)
        return
    with open(schema_path) as f:
        schema = json.load(f)
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        err("ERR_SCHEMA_INVALID", e.message, path=artifact_path)

# --- File helpers ---

def file_exists_local(root, rel_path):
    """Check if a path exists locally (same-repo references only)."""
    return (root / rel_path).exists()

def is_local_path(repo_url, current_repo_url):
    """True if the repo_url matches the current repo (same-repo reference)."""
    if not repo_url:
        return True  # no url = local
    if not current_repo_url:
        return False
    return repo_url.rstrip("/") == current_repo_url.rstrip("/")

# --- Main validation ---

def run(root: Path, schema_dir: Path):
    print(f"Validating convention at: {root}\n")

    # -------------------------
    # 1. ENTERPRISE LAYER (ea/)
    # -------------------------
    print("[ EA Layer ]")

    initiatives_path = root / "ea/architecture/portfolio/initiatives.yml"
    domain_registry_path = root / "ea/architecture/enterprise/domain-registry.yml"

    if not initiatives_path.exists():
        err("ERR_ENTRYPOINT_MISSING", "ea/architecture/portfolio/initiatives.yml not found")
        initiative_ids = set()
        repo_url = None
    else:
        initiatives_data = load_yaml(initiatives_path)
        validate_schema(initiatives_data, schema_dir / "initiatives.schema.json", initiatives_path)
        initiative_ids = set()
        repo_url = None
        seen_init_ids = set()
        for init in (initiatives_data or {}).get("initiatives", []):
            iid = init.get("initiative_id", "")
            if iid in seen_init_ids:
                err("ERR_SELECTOR_DUPLICATE", f"Duplicate initiative_id '{iid}'", path=initiatives_path)
            seen_init_ids.add(iid)
            initiative_ids.add(iid)
            # Check local solution_entrypoint
            sol_url = init.get("solution_repo_url", "")
            sol_ep = init.get("solution_entrypoint", "")
            if not repo_url:
                repo_url = sol_url
            if sol_ep and is_local_path(sol_url, repo_url):
                if not file_exists_local(root, sol_ep):
                    err("ERR_ENTRYPOINT_MISSING",
                        f"initiative '{iid}' solution_entrypoint '{sol_ep}' not found",
                        path=initiatives_path)
        print(f"  initiatives: {len(initiative_ids)} ({', '.join(sorted(initiative_ids)) or 'none'})")

    if not domain_registry_path.exists():
        err("ERR_ENTRYPOINT_MISSING", "ea/architecture/enterprise/domain-registry.yml not found")
        domain_ids = set()
    else:
        registry_data = load_yaml(domain_registry_path)
        validate_schema(registry_data, schema_dir / "domain-registry.schema.json", domain_registry_path)
        domain_ids = set()
        seen_domain_ids = set()
        for domain in (registry_data or {}).get("domains", []):
            did = domain.get("domain_id", "")
            if did in seen_domain_ids:
                err("ERR_SELECTOR_DUPLICATE", f"Duplicate domain_id '{did}'", path=domain_registry_path)
            seen_domain_ids.add(did)
            domain_ids.add(did)
            d_url = domain.get("domain_repo_url", "")
            d_ep = domain.get("domain_entrypoint", "")
            if d_ep and is_local_path(d_url, repo_url):
                if not file_exists_local(root, d_ep):
                    err("ERR_ENTRYPOINT_MISSING",
                        f"domain '{did}' domain_entrypoint '{d_ep}' not found",
                        path=domain_registry_path)
        print(f"  domains: {len(domain_ids)} ({', '.join(sorted(domain_ids)) or 'none'})")

    # -------------------------
    # 2. SOLUTION LAYER (sa/)
    # -------------------------
    print("\n[ SA Layer ]")

    solution_index_path = root / "sa/solution-index.yml"
    workstreams_path = root / "sa/architecture/solution/domain-workstreams.yml"

    if solution_index_path.exists():
        si_data = load_yaml(solution_index_path)
        validate_schema(si_data, schema_dir / "solution-index.schema.json", solution_index_path)
        print(f"  solution-index.yml: ok")
    else:
        warn("sa/solution-index.yml not found")

    workstream_ids = set()
    if not workstreams_path.exists():
        warn("sa/architecture/solution/domain-workstreams.yml not found")
    else:
        ws_data = load_yaml(workstreams_path)
        validate_schema(ws_data, schema_dir / "domain-workstreams.schema.json", workstreams_path)

        # Top-level initiative_id on workstreams file
        ws_file_init_id = (ws_data or {}).get("initiative_id", "")
        if ws_file_init_id and ws_file_init_id not in initiative_ids:
            err("ERR_INITIATIVE_NOT_FOUND",
                f"domain-workstreams.yml initiative_id '{ws_file_init_id}' not in initiatives.yml",
                path=workstreams_path)

        seen_ws_ids = set()
        active_ws = 0
        for ws in (ws_data or {}).get("workstreams", []):
            wsid = ws.get("workstream_id", "")
            if wsid in seen_ws_ids:
                err("ERR_SELECTOR_DUPLICATE", f"Duplicate workstream_id '{wsid}'", path=workstreams_path)
            seen_ws_ids.add(wsid)
            workstream_ids.add(wsid)

            # initiative_id referential integrity
            ws_init_id = ws.get("initiative_id", "")
            if ws_init_id and ws_init_id not in initiative_ids:
                err("ERR_INITIATIVE_NOT_FOUND",
                    f"workstream '{wsid}' initiative_id '{ws_init_id}' not in initiatives.yml",
                    path=workstreams_path)

            # domain_id referential integrity
            ws_dom_id = ws.get("domain_id", "")
            if ws_dom_id and ws_dom_id not in domain_ids:
                err("ERR_DOMAIN_NOT_FOUND",
                    f"workstream '{wsid}' domain_id '{ws_dom_id}' not in domain-registry.yml",
                    path=workstreams_path)

            # workstream_entrypoint existence (local only)
            ws_url = ws.get("workstream_repo_url", "")
            ws_ep = ws.get("workstream_entrypoint", "")
            if ws_ep and is_local_path(ws_url, repo_url):
                if not file_exists_local(root, ws_ep):
                    err("ERR_ENTRYPOINT_MISSING",
                        f"workstream '{wsid}' workstream_entrypoint '{ws_ep}' not found",
                        path=workstreams_path)

            # status policy
            if ws.get("status") == "inactive":
                warn(f"workstream '{wsid}' is inactive — not routable", path=workstreams_path)
            elif ws.get("status") == "active":
                active_ws += 1

        print(f"  workstreams: {len(workstream_ids)} total, {active_ws} active")

    # -------------------------
    # 3. DOMAIN LAYER (da/)
    # -------------------------
    print("\n[ DA Layer ]")

    da_root = root / "da"
    if not da_root.exists():
        warn("da/ directory not found")
    else:
        domain_dirs = [d for d in da_root.iterdir() if d.is_dir()]
        for domain_dir in sorted(domain_dirs):
            domain_id = domain_dir.name
            impl_path = domain_dir / "domain-implementations.yml"
            roadmap_path = domain_dir / "domain-roadmap.yml"

            impl_ids = set()
            if not impl_path.exists():
                warn(f"domain '{domain_id}' has no domain-implementations.yml")
            else:
                impl_data = load_yaml(impl_path)
                validate_schema(impl_data, schema_dir / "domain-implementations.schema.json", impl_path)
                seen_impl_ids = set()
                active_impl = 0
                for impl in (impl_data or {}).get("implementations", []):
                    iid = impl.get("implementation_id", "")
                    if iid in seen_impl_ids:
                        err("ERR_SELECTOR_DUPLICATE",
                            f"Duplicate implementation_id '{iid}' in domain '{domain_id}'",
                            path=impl_path)
                    seen_impl_ids.add(iid)
                    impl_ids.add(iid)
                    if impl.get("status") == "active":
                        active_impl += 1
                    # Warn on missing repo.url for active implementations
                    if impl.get("status") == "active":
                        repo = impl.get("repo", {})
                        if not repo.get("url"):
                            warn(f"domain '{domain_id}' implementation '{iid}' has no repo.url (local path only)",
                                 path=impl_path)

                roadmap_count = 0
                if roadmap_path.exists():
                    roadmap_data = load_yaml(roadmap_path)
                    validate_schema(roadmap_data, schema_dir / "domain-roadmap.schema.json", roadmap_path)
                    for item in (roadmap_data or {}).get("items", []):
                        roadmap_count += 1
                        riid = item.get("roadmap_item_id", "")
                        # workstream_ids referential integrity
                        for wsid in item.get("workstream_ids", []):
                            if wsid not in workstream_ids:
                                err("ERR_WORKSTREAM_NOT_FOUND",
                                    f"roadmap item '{riid}' references unknown workstream_id '{wsid}'",
                                    path=roadmap_path)
                        # implementation_ids referential integrity
                        for iid in item.get("implementation_ids", []):
                            if iid not in impl_ids:
                                err("ERR_IMPLEMENTATION_NOT_FOUND",
                                    f"roadmap item '{riid}' references unknown implementation_id '{iid}'",
                                    path=roadmap_path)

                print(f"  {domain_id}: {len(impl_ids)} impl(s), {active_impl} active"
                      + (f", {roadmap_count} roadmap item(s)" if roadmap_count else ", no roadmap"))

    # -------------------------
    # 4. RESULTS
    # -------------------------
    print()
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(w)
        print()

    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(e)
        print(f"\nResult: FAIL — {len(errors)} error(s)")
        return 1
    else:
        print("Result: CLEAN — no errors")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Enterprise Convention Validator")
    parser.add_argument("--root", default=".", help="Repo root directory (default: current directory)")
    parser.add_argument("--schema-dir", help="Directory containing schema files (default: auto-detect from script location)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.schema_dir:
        schema_dir = Path(args.schema_dir).resolve()
    else:
        schema_dir = Path(__file__).parent.parent / "references"

    if not root.exists():
        print(f"ERROR: root directory '{root}' does not exist", file=sys.stderr)
        sys.exit(2)

    sys.exit(run(root, schema_dir))


if __name__ == "__main__":
    main()
