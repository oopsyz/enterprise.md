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
                                  [--active-only]

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

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# --- YAML loading ---

try:
    import yaml
    def load_yaml(path: Path) -> Any:
        with open(path, encoding="utf-8-sig") as f:
            return yaml.safe_load(f)
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# --- Schema validation (optional, requires jsonschema) ---

try:
    from jsonschema import Draft202012Validator, FormatChecker
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

SCHEMA_BY_BASENAME = {
    "initiatives.yml":             "initiatives.schema.json",
    "domain-workstreams.yml":      "domain-workstreams.schema.json",
    "domain-implementations.yml":  "domain-implementations.schema.json",
    "domain-registry.yml":         "domain-registry.schema.json",
    "solution-index.yml":          "solution-index.schema.json",
    "domain-roadmap.yml":          "domain-roadmap.schema.json",
}

ROUTABLE_STATUSES = {"active", "in_progress"}

# --- Error collection ---

errors: list[str] = []
warnings: list[str] = []


def err(code: str, message: str, path: Any = None) -> None:
    location = f" [{path}]" if path else ""
    errors.append(f"  {code}{location}: {message}")


def warn(message: str, path: Any = None) -> None:
    location = f" [{path}]" if path else ""
    warnings.append(f"  WARN{location}: {message}")


def note(message: str) -> None:
    print(f"  (skipped: {message})")


# --- Schema validation ---

def validate_schema(data: Any, schema_path: Path, artifact_path: Path) -> None:
    if not HAS_JSONSCHEMA:
        return
    if not schema_path.exists():
        warn(f"Schema file not found, skipping schema check", path=artifact_path)
        return
    with open(schema_path, encoding="utf-8-sig") as f:
        schema = json.load(f)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(data), key=str):
        err("ERR_INVALID_SCHEMA", f"schema violation: {error.message}", path=artifact_path)


# --- Helpers ---

def file_exists_local(root: Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def is_local_path(repo_url: Any, this_repo_url: str | None) -> bool:
    """
    True if repo_url refers to this repo.
    - No url AND this_repo_url is provided means monorepo (local by definition).
    - No url AND no this_repo_url means we cannot confirm locality — skip check.
    - If this_repo_url is not provided, remote entrypoint checks are skipped.
    """
    if not repo_url:
        return bool(this_repo_url)
    if not this_repo_url:
        return False
    return repo_url.rstrip("/") == this_repo_url.rstrip("/")


def canonical_repo_id(artifact_path: Path, repo_url: str | None) -> str:
    if repo_url:
        return repo_url.rstrip("/").lower()
    return f"self:{artifact_path.resolve().parent.as_posix().lower()}"


def normalize_repo_url(repo_url: Any) -> str | None:
    if isinstance(repo_url, str) and repo_url:
        return repo_url.rstrip("/")
    return None


def ensure_unique_ids(
    entries: list[dict[str, Any]], key: str, path: Any
) -> set[str]:
    seen: dict[str, int] = {}
    ids: set[str] = set()
    for index, entry in enumerate(entries):
        value = entry.get(key)
        if not isinstance(value, str) or not value:
            continue
        if value in seen:
            err("ERR_SELECTOR_DUPLICATE",
                f"duplicate {key} '{value}' at entries {seen[value]} and {index}",
                path=path)
        else:
            seen[value] = index
        ids.add(value)
    return ids


# --- Main validation ---

def run(root: Path, schema_dir: Path, paths: dict, explicit_paths: set,
        this_repo_url: str | None, active_only: bool) -> int:
    """
    explicit_paths: set of path keys the user passed explicitly on the CLI.
    If a catalog is absent AND its key is not in explicit_paths, it is treated
    as 'layer not present here' (skipped). If its key IS in explicit_paths,
    the file is expected to exist and its absence is an error.
    """
    routable_statuses = {"active"} if active_only else ROUTABLE_STATUSES

    print(f"Validating convention at: {root}")
    print(f"Repo URL: {this_repo_url or '(not provided — remote entrypoint checks skipped)'}")
    print()

    # -------------------------
    # 1. ENTERPRISE LAYER
    # -------------------------
    print("[ EA Layer ]")

    initiatives_path = root / paths["initiatives"]
    domain_registry_path = root / paths["domain_registry"]

    initiative_ids: set[str] = set()
    if not initiatives_path.exists():
        if "initiatives" in explicit_paths:
            err("ERR_ENTRYPOINT_MISSING", f"{paths['initiatives']} not found")
        else:
            note("initiatives.yml absent — EA layer not present in this repo")
    else:
        initiatives_data = load_yaml(initiatives_path)
        validate_schema(initiatives_data, schema_dir / "initiatives.schema.json", initiatives_path)
        initiatives_list = (initiatives_data or {}).get("initiatives", [])
        initiative_ids = ensure_unique_ids(initiatives_list, "initiative_id", initiatives_path)
        for index, init in enumerate(initiatives_list):
            sol_url = init.get("solution_repo_url", "")
            sol_ep = init.get("solution_entrypoint", "")
            if sol_ep and is_local_path(sol_url, this_repo_url):
                if not file_exists_local(root, sol_ep):
                    err("ERR_ENTRYPOINT_MISSING",
                        f"initiatives[{index}] solution_entrypoint '{sol_ep}' not found",
                        path=initiatives_path)
        print(f"  initiatives: {len(initiative_ids)} ({', '.join(sorted(initiative_ids)) or 'none'})")

    domain_ids: set[str] = set()
    domain_repo_urls_by_id: dict[str, str] = {}
    has_domain_registry = False
    if not domain_registry_path.exists():
        if "domain_registry" in explicit_paths:
            err("ERR_ENTRYPOINT_MISSING", f"{paths['domain_registry']} not found")
        else:
            note("domain-registry.yml absent — EA domain registry not present in this repo")
    else:
        has_domain_registry = True
        registry_data = load_yaml(domain_registry_path)
        validate_schema(registry_data, schema_dir / "domain-registry.schema.json", domain_registry_path)
        domains_list = (registry_data or {}).get("domains", [])
        domain_ids = ensure_unique_ids(domains_list, "domain_id", domain_registry_path)
        for index, domain in enumerate(domains_list):
            domain_id = domain.get("domain_id", "")
            d_url = domain.get("domain_repo_url", "")
            d_ep = domain.get("domain_entrypoint", "")
            normalized_d_url = normalize_repo_url(d_url)
            if isinstance(domain_id, str) and domain_id and normalized_d_url:
                domain_repo_urls_by_id[domain_id] = normalized_d_url
            if d_ep and is_local_path(d_url, this_repo_url):
                if not file_exists_local(root, d_ep):
                    err("ERR_ENTRYPOINT_MISSING",
                        f"domains[{index}] domain_entrypoint '{d_ep}' not found",
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
        for di, domain in enumerate((si_data or {}).get("domains", [])):
            for vfield in ("oda_component", "tmf_apis"):
                if vfield in domain:
                    warn(f"domains[{di}] contains vertical-specific field '{vfield}' — move to metadata: for industry annotations",
                         path=solution_index_path)
        print(f"  solution-index: ok")

    workstream_ids: set[str] = set()
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

        workstreams_list = (ws_data or {}).get("workstreams", [])
        workstream_ids = ensure_unique_ids(workstreams_list, "workstream_id", workstreams_path)
        active_ws = 0
        for index, ws in enumerate(workstreams_list):
            ws_init_id = ws.get("initiative_id", "")
            if initiative_ids and not ws_init_id:
                err("ERR_SELECTOR_MISSING",
                    f"workstreams[{index}] requires initiative_id when initiatives.yml is present",
                    path=workstreams_path)
            if ws_init_id and initiative_ids and ws_init_id not in initiative_ids:
                err("ERR_INITIATIVE_NOT_FOUND",
                    f"workstreams[{index}] initiative_id '{ws_init_id}' not in initiatives",
                    path=workstreams_path)

            ws_dom_id = ws.get("domain_id", "")
            if ws_dom_id and domain_ids and ws_dom_id not in domain_ids:
                err("ERR_DOMAIN_NOT_FOUND",
                    f"workstreams[{index}] domain_id '{ws_dom_id}' not in domain-registry",
                    path=workstreams_path)

            status = ws.get("status")
            entrypoint = ws.get("workstream_entrypoint")
            domain_repo_url = ws.get("domain_repo_url")
            ws_url = domain_repo_url if isinstance(domain_repo_url, str) else ""
            normalized_ws_url = normalize_repo_url(domain_repo_url)
            registry_ws_url = domain_repo_urls_by_id.get(ws_dom_id)

            if "workstream_repo_url" in ws:
                warn(f"workstreams[{index}] uses legacy field 'workstream_repo_url' - rename to 'domain_repo_url'",
                     path=workstreams_path)

            if normalized_ws_url and registry_ws_url and normalized_ws_url != registry_ws_url:
                err("ERR_CONFLICT",
                    f"workstreams[{index}] domain_repo_url '{domain_repo_url}' does not match authoritative domain-registry.yml value '{registry_ws_url}' for domain_id '{ws_dom_id}'",
                    path=workstreams_path)

            # Routable workstreams must have an entrypoint
            if status in routable_statuses and not isinstance(entrypoint, str):
                err("ERR_ENTRYPOINT_MISSING",
                    f"workstreams[{index}] routable status '{status}' requires a non-null workstream_entrypoint",
                    path=workstreams_path)

            # Without a domain registry, workstreams need their own repo URL
            if not has_domain_registry and not normalized_ws_url:
                err("ERR_TARGET_UNREACHABLE",
                    f"workstreams[{index}] requires domain_repo_url when no domain-registry.yml is provided",
                    path=workstreams_path)

            if entrypoint and is_local_path(ws_url, this_repo_url):
                if not file_exists_local(root, entrypoint):
                    err("ERR_ENTRYPOINT_MISSING",
                        f"workstreams[{index}] workstream_entrypoint '{entrypoint}' not found",
                        path=workstreams_path)

            for vfield in ("oda_component_name", "tmfc_component_id"):
                if vfield in ws:
                    warn(f"workstreams[{index}] contains vertical-specific field '{vfield}' — move to metadata: for industry annotations",
                         path=workstreams_path)

            if status == "inactive":
                warn(f"workstream '{ws.get('workstream_id', '')}' is inactive — not routable",
                     path=workstreams_path)
            elif status in routable_statuses:
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

            impl_ids: set[str] = set()
            if not impl_path.exists():
                warn(f"domain '{domain_id}' has no domain-implementations.yml")
            else:
                impl_data = load_yaml(impl_path)
                validate_schema(impl_data, schema_dir / "domain-implementations.schema.json", impl_path)
                implementations = (impl_data or {}).get("implementations", [])
                impl_ids = ensure_unique_ids(implementations, "implementation_id", impl_path)

                # --- replaced_by validation ---
                for index, impl in enumerate(implementations):
                    replaced_by = impl.get("replaced_by", [])
                    if isinstance(replaced_by, list):
                        for target in replaced_by:
                            if isinstance(target, str) and target not in impl_ids:
                                err("ERR_SELECTOR_MISSING",
                                    f"implementations[{index}].replaced_by references missing implementation_id '{target}'",
                                    path=impl_path)

                # --- path binding uniqueness (ERR_OVERLAPPING_PATHS) ---
                bindings: dict[str, dict[str, int]] = defaultdict(dict)
                active_impl = 0
                for index, impl in enumerate(implementations):
                    if impl.get("status") in routable_statuses:
                        active_impl += 1

                    repo = impl.get("repo") or {}
                    if not isinstance(repo, dict):
                        continue
                    repo_paths = repo.get("paths") or ["*"]
                    if not isinstance(repo_paths, list):
                        continue
                    repo_ids = [canonical_repo_id(impl_path, repo.get("url"))]
                    aliases = repo.get("aliases") or []
                    if isinstance(aliases, list):
                        repo_ids.extend(
                            alias.rstrip("/").lower()
                            for alias in aliases
                            if isinstance(alias, str) and alias
                        )

                    for repo_id in repo_ids:
                        for repo_path in repo_paths:
                            if not isinstance(repo_path, str):
                                continue
                            prior = bindings[repo_id].get(repo_path)
                            if prior is not None:
                                err("ERR_OVERLAPPING_PATHS",
                                    f"implementations[{index}] duplicates repo binding ({repo_id}, {repo_path}) already used by implementations[{prior}]",
                                    path=impl_path)
                            bindings[repo_id][repo_path] = index

                        if "*" in bindings[repo_id] and len(bindings[repo_id]) > 1:
                            err("ERR_OVERLAPPING_PATHS",
                                f"repo binding set for {repo_id} mixes '*' with scoped paths, violating the uniqueness invariant",
                                path=impl_path)

                    for vfield in ("oda_component_name", "tmfc_component_id"):
                        if vfield in impl:
                            warn(f"implementations[{index}] contains vertical-specific field '{vfield}' — move to metadata: for industry annotations",
                                 path=impl_path)

                    # Entrypoint check for routable implementations
                    if impl.get("status") in routable_statuses:
                        repo_url = repo.get("url", "")
                        repo_ep = repo.get("entrypoint", "")
                        if not repo_url:
                            warn(f"domain '{domain_id}' implementation '{impl.get('implementation_id', '')}' has no repo.url (local path only)",
                                 path=impl_path)
                        if repo_ep and is_local_path(repo_url, this_repo_url):
                            if not file_exists_local(root, repo_ep):
                                err("ERR_ENTRYPOINT_MISSING",
                                    f"implementations[{index}] repo.entrypoint '{repo_ep}' not found",
                                    path=impl_path)

                # --- domain-roadmap.yml (proposed extension) ---
                roadmap_count = 0
                if roadmap_path.exists():
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


def main() -> None:
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
    parser.add_argument("--active-only", action="store_true",
                        help="Treat only status=active as routable (default: active + in_progress)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else Path(__file__).parent.parent / "references"

    if not root.exists():
        print(f"ERROR: root directory '{root}' does not exist", file=sys.stderr)
        sys.exit(2)

    # Track which paths were explicitly provided vs defaulted.
    # Only explicitly-provided paths trigger errors on absence.
    explicit_paths: set[str] = set()
    paths: dict[str, str] = {}
    for key, default in DEFAULTS.items():
        cli_val = getattr(args, key, None)
        if cli_val is not None:
            paths[key] = cli_val
            explicit_paths.add(key)
        else:
            paths[key] = default

    sys.exit(run(root, schema_dir, paths, explicit_paths, args.repo_url, args.active_only))


if __name__ == "__main__":
    main()
