#!/usr/bin/env python3
"""
Enterprise Convention Validator
Validates referential integrity and schema conformance for ea/sa/da convention artifacts.

Usage:
    python validate_convention.py [--root REPO_ROOT] [--schema-dir SCHEMA_DIR]
                                  [--repo-url REPO_URL]
                                  [--initiatives PATH] [--domain-registry PATH]
                                  [--solution-index PATH] [--workstreams PATH]
                                  [--da-root PATH]

Path arguments are relative to --root. They default to the reference layout
(ea/architecture/portfolio/initiatives.yml etc.). Repos using a different layout
must supply the correct paths explicitly.

Partial-adoption topology support:
  The spec allows EA-only, SA+DA, DA-only, and full EA+SA+DA topologies.
  Missing layer catalogs are treated as absent (skipped with a note) unless the
  user explicitly supplied that path — in which case the file is expected to exist.
  This means a DA-only repo will not fail on missing EA or SA catalogs.

DA layout assumption:
  The validator assumes one subdirectory per domain under --da-root, each
  containing domain-implementations.yml. This structure is implied by the spec
  examples. Flat or otherwise custom DA layouts are not supported by this
  validator and must be validated manually.

Exit codes:
    0  clean
    1  validation errors found
    2  missing required files or import errors
"""

import argparse
import json
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

# --- Default paths (reference implementation layout) ---

DEFAULTS = {
    "initiatives":     "ea/architecture/portfolio/initiatives.yml",
    "domain_registry": "ea/architecture/enterprise/domain-registry.yml",
    "solution_index":  "sa/solution-index.yml",
    "workstreams":     "sa/architecture/solution/domain-workstreams.yml",
    "da_root":         "da",
}

# --- Error collection ---

errors = []
warnings = []

def err(code, message, path=None):
    location = f" [{path}]" if path else ""
    errors.append(f"  {code}{location}: {message}")

def warn(message, path=None):
    location = f" [{path}]" if path else ""
    warnings.append(f"  WARN{location}: {message}")

def note(message):
    print(f"  (skipped: {message})")

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
    return (root / rel_path).exists()

def is_local_path(repo_url, this_repo_url):
    """
    True if repo_url refers to this repo.
    - No url means monorepo (local by definition).
    - If this_repo_url is not provided, we cannot confirm locality — skip check.
    """
    if not repo_url:
        return True
    if not this_repo_url:
        return False
    return repo_url.rstrip("/") == this_repo_url.rstrip("/")

# --- Main validation ---

def run(root: Path, schema_dir: Path, paths: dict, explicit_paths: set, this_repo_url: str):
    """
    explicit_paths: set of path keys the user passed explicitly on the CLI.
    If a catalog is absent AND its key is not in explicit_paths, it is treated
    as 'layer not present here' (skipped). If its key IS in explicit_paths,
    the file is expected to exist and its absence is an error.
    """
    print(f"Validating convention at: {root}")
    print(f"Repo URL: {this_repo_url or '(not provided — remote entrypoint checks skipped)'}")
    print()

    # -------------------------
    # 1. ENTERPRISE LAYER
    # -------------------------
    print("[ EA Layer ]")

    initiatives_path = root / paths["initiatives"]
    domain_registry_path = root / paths["domain_registry"]

    initiative_ids = set()
    if not initiatives_path.exists():
        if "initiatives" in explicit_paths:
            err("ERR_ENTRYPOINT_MISSING", f"{paths['initiatives']} not found")
        else:
            note("initiatives.yml absent — EA layer not present in this repo")
    else:
        initiatives_data = load_yaml(initiatives_path)
        validate_schema(initiatives_data, schema_dir / "initiatives.schema.json", initiatives_path)
        seen_init_ids = set()
        for init in (initiatives_data or {}).get("initiatives", []):
            iid = init.get("initiative_id", "")
            if iid in seen_init_ids:
                err("ERR_SELECTOR_DUPLICATE", f"Duplicate initiative_id '{iid}'", path=initiatives_path)
            seen_init_ids.add(iid)
            initiative_ids.add(iid)
            sol_url = init.get("solution_repo_url", "")
            sol_ep = init.get("solution_entrypoint", "")
            if sol_ep and is_local_path(sol_url, this_repo_url):
                if not file_exists_local(root, sol_ep):
                    err("ERR_ENTRYPOINT_MISSING",
                        f"initiative '{iid}' solution_entrypoint '{sol_ep}' not found",
                        path=initiatives_path)
        print(f"  initiatives: {len(initiative_ids)} ({', '.join(sorted(initiative_ids)) or 'none'})")

    domain_ids = set()
    if not domain_registry_path.exists():
        if "domain_registry" in explicit_paths:
            err("ERR_ENTRYPOINT_MISSING", f"{paths['domain_registry']} not found")
        else:
            note("domain-registry.yml absent — EA domain registry not present in this repo")
    else:
        registry_data = load_yaml(domain_registry_path)
        validate_schema(registry_data, schema_dir / "domain-registry.schema.json", domain_registry_path)
        seen_domain_ids = set()
        for domain in (registry_data or {}).get("domains", []):
            did = domain.get("domain_id", "")
            if did in seen_domain_ids:
                err("ERR_SELECTOR_DUPLICATE", f"Duplicate domain_id '{did}'", path=domain_registry_path)
            seen_domain_ids.add(did)
            domain_ids.add(did)
            d_url = domain.get("domain_repo_url", "")
            d_ep = domain.get("domain_entrypoint", "")
            if d_ep and is_local_path(d_url, this_repo_url):
                if not file_exists_local(root, d_ep):
                    err("ERR_ENTRYPOINT_MISSING",
                        f"domain '{did}' domain_entrypoint '{d_ep}' not found",
                        path=domain_registry_path)
        print(f"  domains: {len(domain_ids)} ({', '.join(sorted(domain_ids)) or 'none'})")

    # -------------------------
    # 2. SOLUTION LAYER
    # -------------------------
    print("\n[ SA Layer ]")

    solution_index_path = root / paths["solution_index"]
    workstreams_path = root / paths["workstreams"]

    if not solution_index_path.exists():
        if "solution_index" in explicit_paths:
            err("ERR_ENTRYPOINT_MISSING", f"{paths['solution_index']} not found")
        else:
            note("solution-index.yml absent — SA layer not present in this repo")
    else:
        si_data = load_yaml(solution_index_path)
        validate_schema(si_data, schema_dir / "solution-index.schema.json", solution_index_path)
        print(f"  solution-index: ok")

    workstream_ids = set()
    if not workstreams_path.exists():
        if "workstreams" in explicit_paths:
            err("ERR_ENTRYPOINT_MISSING", f"{paths['workstreams']} not found")
        else:
            note("domain-workstreams.yml absent — SA workstream catalog not present in this repo")
    else:
        ws_data = load_yaml(workstreams_path)
        validate_schema(ws_data, schema_dir / "domain-workstreams.schema.json", workstreams_path)

        ws_file_init_id = (ws_data or {}).get("initiative_id", "")
        if ws_file_init_id and initiative_ids and ws_file_init_id not in initiative_ids:
            err("ERR_INITIATIVE_NOT_FOUND",
                f"workstreams file initiative_id '{ws_file_init_id}' not in initiatives",
                path=workstreams_path)

        seen_ws_ids = set()
        active_ws = 0
        for ws in (ws_data or {}).get("workstreams", []):
            wsid = ws.get("workstream_id", "")
            if wsid in seen_ws_ids:
                err("ERR_SELECTOR_DUPLICATE", f"Duplicate workstream_id '{wsid}'", path=workstreams_path)
            seen_ws_ids.add(wsid)
            workstream_ids.add(wsid)

            ws_init_id = ws.get("initiative_id", "")
            if ws_init_id and initiative_ids and ws_init_id not in initiative_ids:
                err("ERR_INITIATIVE_NOT_FOUND",
                    f"workstream '{wsid}' initiative_id '{ws_init_id}' not in initiatives",
                    path=workstreams_path)

            ws_dom_id = ws.get("domain_id", "")
            if ws_dom_id and domain_ids and ws_dom_id not in domain_ids:
                err("ERR_DOMAIN_NOT_FOUND",
                    f"workstream '{wsid}' domain_id '{ws_dom_id}' not in domain-registry",
                    path=workstreams_path)

            ws_url = ws.get("workstream_repo_url", "")
            ws_ep = ws.get("workstream_entrypoint", "")
            if ws_ep and is_local_path(ws_url, this_repo_url):
                if not file_exists_local(root, ws_ep):
                    err("ERR_ENTRYPOINT_MISSING",
                        f"workstream '{wsid}' workstream_entrypoint '{ws_ep}' not found",
                        path=workstreams_path)

            if ws.get("status") == "inactive":
                warn(f"workstream '{wsid}' is inactive — not routable", path=workstreams_path)
            elif ws.get("status") == "active":
                active_ws += 1

        print(f"  workstreams: {len(workstream_ids)} total, {active_ws} active")

    # -------------------------
    # 3. DOMAIN LAYER
    # -------------------------
    print("\n[ DA Layer ]")

    da_root = root / paths["da_root"]
    if not da_root.exists():
        if "da_root" in explicit_paths:
            err("ERR_ENTRYPOINT_MISSING", f"{paths['da_root']}/ not found")
        else:
            note("da/ directory absent — DA layer not present in this repo")
    else:
        domain_dirs = [d for d in da_root.iterdir() if d.is_dir()]
        if not domain_dirs:
            if "da_root" in explicit_paths:
                warn(
                    f"'{paths['da_root']}' has no domain subdirectories — "
                    "DA validation was skipped. If this is a flat or custom layout, "
                    "the validator does not support it and results may be incomplete."
                )
            else:
                note("da/ exists but contains no domain subdirectories")
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
                        repo = impl.get("repo", {})
                        if not repo.get("url"):
                            warn(f"domain '{domain_id}' implementation '{iid}' has no repo.url (local path only)",
                                 path=impl_path)

                roadmap_count = 0
                if roadmap_path.exists():
                    # domain-roadmap.yml is a proposed convention extension — not in current spec.
                    # Validated if present, never required.
                    roadmap_data = load_yaml(roadmap_path)
                    validate_schema(roadmap_data, schema_dir / "domain-roadmap.schema.json", roadmap_path)
                    for item in (roadmap_data or {}).get("items", []):
                        roadmap_count += 1
                        riid = item.get("roadmap_item_id", "")
                        for wsid in item.get("workstream_ids", []):
                            if wsid not in workstream_ids:
                                err("ERR_WORKSTREAM_NOT_FOUND",
                                    f"roadmap item '{riid}' references unknown workstream_id '{wsid}'",
                                    path=roadmap_path)
                        for iid in item.get("implementation_ids", []):
                            if iid not in impl_ids:
                                err("ERR_IMPLEMENTATION_NOT_FOUND",
                                    f"roadmap item '{riid}' references unknown implementation_id '{iid}'",
                                    path=roadmap_path)

                print(f"  {domain_id}: {len(impl_ids)} impl(s), {active_impl} active"
                      + (f", {roadmap_count} roadmap item(s) [proposed ext]" if roadmap_count else ""))

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
    parser = argparse.ArgumentParser(
        description="Enterprise Convention Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Partial-adoption topology:
  Missing layer catalogs are treated as 'layer not present' (skipped) unless
  you pass the path explicitly on the CLI, in which case the file is expected.

DA layout:
  The validator assumes one subdirectory per domain under --da-root, each
  containing domain-implementations.yml. Custom DA layouts are not supported.

Default paths (reference layout):
  --initiatives     ea/architecture/portfolio/initiatives.yml
  --domain-registry ea/architecture/enterprise/domain-registry.yml
  --solution-index  sa/solution-index.yml
  --workstreams     sa/architecture/solution/domain-workstreams.yml
  --da-root         da
        """
    )
    parser.add_argument("--root", default=".",
                        help="Repo root directory (default: current directory)")
    parser.add_argument("--schema-dir",
                        help="Directory containing schema files (default: auto-detect)")
    parser.add_argument("--repo-url",
                        help="Canonical URL of this repo (used to distinguish local vs remote entrypoints). "
                             "If omitted, remote entrypoint checks are skipped.")
    parser.add_argument("--initiatives", default=None,
                        help=f"Path to initiatives.yml (default: {DEFAULTS['initiatives']})")
    parser.add_argument("--domain-registry", default=None, dest="domain_registry",
                        help=f"Path to domain-registry.yml (default: {DEFAULTS['domain_registry']})")
    parser.add_argument("--solution-index", default=None, dest="solution_index",
                        help=f"Path to solution-index.yml (default: {DEFAULTS['solution_index']})")
    parser.add_argument("--workstreams", default=None,
                        help=f"Path to domain-workstreams.yml (default: {DEFAULTS['workstreams']})")
    parser.add_argument("--da-root", default=None, dest="da_root",
                        help=f"Path to DA domain root directory (default: {DEFAULTS['da_root']})")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else Path(__file__).parent.parent / "references"

    if not root.exists():
        print(f"ERROR: root directory '{root}' does not exist", file=sys.stderr)
        sys.exit(2)

    # Track which paths were explicitly provided vs defaulted.
    # Only explicitly-provided paths trigger errors on absence.
    explicit_paths = set()
    paths = {}
    for key, default in DEFAULTS.items():
        cli_val = getattr(args, key, None)
        if cli_val is not None:
            paths[key] = cli_val
            explicit_paths.add(key)
        else:
            paths[key] = default

    sys.exit(run(root, schema_dir, paths, explicit_paths, args.repo_url))


if __name__ == "__main__":
    main()
