#!/usr/bin/env python3
"""
Thin validator/linter for the enterprise.md routing convention.

Pass one or more catalog files. The script validates each file against the
authoritative schema in ../schemas/ and then applies cross-file and topology-
aware lint checks derived from the spec.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_BY_BASENAME = {
    "initiatives.yml": "initiatives.schema.json",
    "domain-workstreams.yml": "domain-workstreams.schema.json",
    "domain-implementations.yml": "domain-implementations.schema.json",
    "domain-registry.yml": "domain-registry.schema.json",
}

ROUTABLE_STATUSES = {"active", "in_progress"}


@dataclass
class LintError:
    code: str
    path: Path
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate convention catalogs against JSON Schema and lint checks."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Catalog files to validate (e.g. initiatives.yml domain-workstreams.yml).",
    )
    parser.add_argument(
        "--check-entrypoints",
        action="store_true",
        help="Validate repo-relative entrypoint paths when they are expected to exist in the current checkout.",
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="Treat only status=active as routable for lint checks that depend on routability.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as fh:
        return yaml.safe_load(fh)


def load_schema(schema_path: Path) -> dict[str, Any]:
    with schema_path.open("r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def schema_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "schemas"


def format_schema_error_path(error_path: Any) -> str:
    parts = [str(part) for part in error_path]
    return ".".join(parts) if parts else "<root>"


def add_error(errors: list[LintError], code: str, path: Path, message: str) -> None:
    errors.append(LintError(code=code, path=path, message=message))


def validate_schema(path: Path, doc: Any, errors: list[LintError]) -> None:
    schema_name = SCHEMA_BY_BASENAME.get(path.name)
    if not schema_name:
        add_error(errors, "ERR_UNSUPPORTED_CATALOG", path, f"unsupported catalog type: {path.name}")
        return
    schema = load_schema(schema_dir() / schema_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(doc), key=str):
        add_error(
            errors,
            "ERR_INVALID_SCHEMA",
            path,
            f"schema violation at {format_schema_error_path(error.path)}: {error.message}",
        )


def canonical_repo_id(path: Path, repo_url: str | None) -> str:
    if repo_url:
        return repo_url.rstrip("/").lower()
    return f"self:{path.resolve().parent.as_posix().lower()}"


def ensure_unique_ids(
    path: Path, entries: list[dict[str, Any]], key: str, errors: list[LintError]
) -> None:
    seen: dict[str, int] = {}
    for index, entry in enumerate(entries):
        value = entry.get(key)
        if not isinstance(value, str) or not value:
            continue
        if value in seen:
            add_error(
                errors,
                "ERR_SELECTOR_DUPLICATE",
                path,
                f"duplicate {key} '{value}' at entries {seen[value]} and {index}",
            )
        else:
            seen[value] = index


def check_local_entrypoint(
    errors: list[LintError],
    code: str,
    path: Path,
    label: str,
    entrypoint: Any,
    base_dir: Path,
) -> None:
    if not isinstance(entrypoint, str) or not entrypoint:
        add_error(errors, code, path, f"{label} is missing or empty")
        return
    if not (base_dir / entrypoint).exists():
        add_error(
            errors,
            code,
            path,
            f"{label} '{entrypoint}' does not exist relative to {base_dir}",
        )


def is_self_repo_reference(repo_url: Any) -> bool:
    return repo_url is None or not isinstance(repo_url, str) or repo_url.startswith(".") or "://" not in repo_url


def lint_initiatives(
    path: Path, doc: dict[str, Any], errors: list[LintError], check_entrypoints: bool
) -> None:
    ensure_unique_ids(path, doc.get("initiatives", []), "initiative_id", errors)
    if not check_entrypoints:
        return
    for index, initiative in enumerate(doc.get("initiatives", [])):
        if is_self_repo_reference(initiative.get("solution_repo_url")):
            check_local_entrypoint(
                errors,
                "ERR_ENTRYPOINT_MISSING",
                path,
                f"initiatives[{index}].solution_entrypoint",
                initiative.get("solution_entrypoint"),
                path.parent,
            )


def lint_domain_registry(
    path: Path, doc: dict[str, Any], errors: list[LintError], check_entrypoints: bool
) -> None:
    ensure_unique_ids(path, doc.get("domains", []), "domain_id", errors)
    if not check_entrypoints:
        return
    for index, domain in enumerate(doc.get("domains", [])):
        if is_self_repo_reference(domain.get("domain_repo_url")):
            check_local_entrypoint(
                errors,
                "ERR_ENTRYPOINT_MISSING",
                path,
                f"domains[{index}].domain_entrypoint",
                domain.get("domain_entrypoint"),
                path.parent,
            )


def lint_domain_workstreams(
    path: Path,
    doc: dict[str, Any],
    provided_catalogs: dict[str, tuple[Path, dict[str, Any]]],
    errors: list[LintError],
    check_entrypoints: bool,
    active_only: bool,
) -> None:
    workstreams = doc.get("workstreams", [])
    ensure_unique_ids(path, workstreams, "workstream_id", errors)
    routable_statuses = {"active"} if active_only else ROUTABLE_STATUSES

    registry_doc = provided_catalogs.get("domain-registry.yml")
    initiatives_doc = provided_catalogs.get("initiatives.yml")
    domain_ids = set()
    initiative_ids = set()
    if registry_doc:
        domain_ids = {
            entry.get("domain_id")
            for entry in registry_doc[1].get("domains", [])
            if isinstance(entry.get("domain_id"), str)
        }
    if initiatives_doc:
        initiative_ids = {
            entry.get("initiative_id")
            for entry in initiatives_doc[1].get("initiatives", [])
            if isinstance(entry.get("initiative_id"), str)
        }

    for index, workstream in enumerate(workstreams):
        status = workstream.get("status")
        entrypoint = workstream.get("workstream_entrypoint")
        repo_url = workstream.get("workstream_repo_url")
        if status in routable_statuses and not isinstance(entrypoint, str):
            add_error(
                errors,
                "ERR_ENTRYPOINT_MISSING",
                path,
                f"workstreams[{index}] routable status '{status}' requires a non-null workstream_entrypoint",
            )
        if not registry_doc and not isinstance(repo_url, str):
            add_error(
                errors,
                "ERR_TARGET_UNREACHABLE",
                path,
                f"workstreams[{index}] requires workstream_repo_url when no domain-registry.yml is provided",
            )
        if check_entrypoints and status in routable_statuses and is_self_repo_reference(repo_url):
            check_local_entrypoint(
                errors,
                "ERR_ENTRYPOINT_MISSING",
                path,
                f"workstreams[{index}].workstream_entrypoint",
                entrypoint,
                path.parent,
            )
        initiative_id = workstream.get("initiative_id")
        if initiatives_doc and isinstance(initiative_id, str) and initiative_id not in initiative_ids:
            add_error(
                errors,
                "ERR_INITIATIVE_NOT_FOUND",
                path,
                f"workstreams[{index}].initiative_id '{initiative_id}' does not resolve in initiatives.yml",
            )
        domain_id = workstream.get("domain_id")
        if registry_doc and isinstance(domain_id, str) and domain_id not in domain_ids:
            add_error(
                errors,
                "ERR_DOMAIN_NOT_FOUND",
                path,
                f"workstreams[{index}].domain_id '{domain_id}' does not resolve in domain-registry.yml",
            )


def lint_domain_implementations(
    path: Path,
    doc: dict[str, Any],
    errors: list[LintError],
    check_entrypoints: bool,
    active_only: bool,
) -> None:
    implementations = doc.get("implementations", [])
    ensure_unique_ids(path, implementations, "implementation_id", errors)
    routable_statuses = {"active"} if active_only else ROUTABLE_STATUSES

    implementation_ids = {
        entry.get("implementation_id")
        for entry in implementations
        if isinstance(entry.get("implementation_id"), str)
    }

    bindings: dict[str, dict[str, int]] = defaultdict(dict)
    for index, implementation in enumerate(implementations):
        replaced_by = implementation.get("replaced_by", [])
        if isinstance(replaced_by, list):
            for target in replaced_by:
                if isinstance(target, str) and target not in implementation_ids:
                    add_error(
                        errors,
                        "ERR_SELECTOR_MISSING",
                        path,
                        f"implementations[{index}].replaced_by references missing implementation_id '{target}'",
                    )

        repo = implementation.get("repo") or {}
        if not isinstance(repo, dict):
            continue
        repo_paths = repo.get("paths") or ["*"]
        if not isinstance(repo_paths, list):
            continue
        repo_ids = [canonical_repo_id(path, repo.get("url"))]
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
                    add_error(
                        errors,
                        "ERR_OVERLAPPING_PATHS",
                        path,
                        f"implementations[{index}] duplicates repo binding ({repo_id}, {repo_path}) already used by implementations[{prior}]",
                    )
                bindings[repo_id][repo_path] = index

            if "*" in bindings[repo_id] and len(bindings[repo_id]) > 1:
                add_error(
                    errors,
                    "ERR_OVERLAPPING_PATHS",
                    path,
                    f"repo binding set for {repo_id} mixes '*' with scoped paths, violating the uniqueness invariant",
                )

        if check_entrypoints and implementation.get("status") in routable_statuses and is_self_repo_reference(repo.get("url")):
            check_local_entrypoint(
                errors,
                "ERR_ENTRYPOINT_MISSING",
                path,
                f"implementations[{index}].repo.entrypoint",
                repo.get("entrypoint"),
                path.parent,
            )


def main() -> int:
    args = parse_args()
    files = [Path(name).resolve() for name in args.files]
    errors: list[LintError] = []
    loaded: dict[str, tuple[Path, dict[str, Any]]] = {}

    for path in files:
        if not path.exists():
            add_error(errors, "ERR_FILE_NOT_FOUND", path, "file does not exist")
            continue
        if path.name in loaded:
            add_error(errors, "ERR_SELECTOR_DUPLICATE", path, f"duplicate catalog basename in invocation: {path.name}")
            continue
        try:
            data = load_yaml(path)
        except Exception as exc:  # noqa: BLE001
            add_error(errors, "ERR_INVALID_SCHEMA", path, f"failed to parse YAML: {exc}")
            continue
        if not isinstance(data, dict):
            add_error(errors, "ERR_INVALID_SCHEMA", path, "top-level YAML document must be a mapping/object")
            continue
        loaded[path.name] = (path, data)
        validate_schema(path, data, errors)

    for name, (path, data) in loaded.items():
        if name == "initiatives.yml":
            lint_initiatives(path, data, errors, args.check_entrypoints)
        elif name == "domain-registry.yml":
            lint_domain_registry(path, data, errors, args.check_entrypoints)
        elif name == "domain-workstreams.yml":
            lint_domain_workstreams(path, data, loaded, errors, args.check_entrypoints, args.active_only)
        elif name == "domain-implementations.yml":
            lint_domain_implementations(path, data, errors, args.check_entrypoints, args.active_only)

    if errors:
        for error in errors:
            print(f"ERROR [{error.code}] {error.path}: {error.message}")
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
