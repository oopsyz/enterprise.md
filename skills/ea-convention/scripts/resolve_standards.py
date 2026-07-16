#!/usr/bin/env python3
"""Resolve governed standards-provider routing and emit a versioned receipt."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


class ResolutionError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


SUPPORTED_MAJORS = {
    "domain-registry": {2},
    "initiatives": {1},
    "pattern-index": {1},
    "standards-resolution-receipt": {1},
}


def require_supported_version(data: dict[str, Any], expected_name: str) -> tuple[int, int, int]:
    if data.get("spec_name") != expected_name:
        raise ResolutionError("ERR_VERSION_UNSUPPORTED", f"expected spec_name {expected_name}")
    value = data.get("spec_version")
    if not isinstance(value, str) or re.fullmatch(r"\d+\.\d+\.\d+", value) is None:
        raise ResolutionError("ERR_VERSION_UNSUPPORTED", f"invalid {expected_name} spec_version")
    version = tuple(int(part) for part in value.split("."))
    if version[0] not in SUPPORTED_MAJORS[expected_name]:
        raise ResolutionError(
            "ERR_VERSION_UNSUPPORTED",
            f"{expected_name} major version {version[0]} is not supported",
        )
    return version


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8-sig") as handle:
            value = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        raise ResolutionError("ERR_INVALID_YAML", f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ResolutionError("ERR_INVALID_YAML", f"{path} must contain a mapping")
    return value


def safe_join(root: Path, relative: str, code: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ResolutionError(code, "path must be a non-empty repository-relative string")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ResolutionError(code, f"path escapes provider root: {relative}") from exc
    return candidate


def choose_provider(
    registry: dict[str, Any],
    initiatives: dict[str, Any] | None = None,
    initiative_id: str | None = None,
    explicit_provider: str | None = None,
    explicit_index: str | None = None,
    bound_initiative_id: str | None = None,
) -> tuple[dict[str, Any], str, str, str | None, str]:
    require_supported_version(registry, "domain-registry")
    if bound_initiative_id and initiative_id != bound_initiative_id:
        raise ResolutionError(
            "ERR_STANDARDS_INITIATIVE_CONTEXT_REQUIRED",
            f"governed work is bound to initiative '{bound_initiative_id}'",
        )
    domains = registry.get("domains", [])
    by_id: dict[str, dict[str, Any]] = {}
    for row in domains:
        if not isinstance(row, dict) or not isinstance(row.get("domain_id"), str):
            continue
        domain_id = row["domain_id"]
        if domain_id in by_id:
            raise ResolutionError("ERR_SELECTOR_AMBIGUOUS", f"duplicate domain_id: {domain_id}")
        by_id[domain_id] = row

    initiative = None
    if initiative_id:
        if initiatives is None:
            raise ResolutionError("ERR_INITIATIVE_NOT_FOUND", initiative_id)
        initiatives_version = require_supported_version(initiatives, "initiatives")
        if explicit_provider or explicit_index:
            raise ResolutionError(
                "ERR_STANDARDS_OVERRIDE_NOT_AUTHORIZED",
                "explicit standards overrides are forbidden under initiative context",
            )
        for row in (initiatives or {}).get("initiatives", []):
            if isinstance(row, dict) and row.get("initiative_id") == initiative_id:
                initiative = row
                break
        if initiative is None:
            raise ResolutionError("ERR_INITIATIVE_NOT_FOUND", initiative_id)
        if initiatives_version < (1, 1, 0) and (
            "standards_domain_id" in initiative or "pattern_index_ref" in initiative
        ):
            raise ResolutionError(
                "ERR_VERSION_UNSUPPORTED",
                "initiative standards fields require initiatives 1.1.0 or later",
            )

    selection_source = "default"
    selected_id = None
    if initiative and initiative.get("standards_domain_id"):
        selected_id = initiative["standards_domain_id"]
        selection_source = "initiative"
    elif not initiative and explicit_provider:
        selected_id = explicit_provider
        selection_source = "explicit"
    else:
        defaults = [
            row for row in domains
            if isinstance(row, dict)
            and row.get("status") == "active"
            and isinstance(row.get("standards_provider"), dict)
            and row["standards_provider"].get("enterprise_default") is True
        ]
        if len(defaults) != 1:
            code = "ERR_STANDARDS_DEFAULT_AMBIGUOUS" if len(defaults) > 1 else "ERR_STANDARDS_DOMAIN_NOT_FOUND"
            raise ResolutionError(code, "exactly one active enterprise default is required")
        selected_id = defaults[0]["domain_id"]

    provider = by_id.get(selected_id)
    if provider is None:
        raise ResolutionError("ERR_STANDARDS_DOMAIN_NOT_FOUND", str(selected_id))
    if provider.get("entry_type") not in {"standards_provider", "both"} or provider.get("status") != "active":
        raise ResolutionError("ERR_STANDARDS_DOMAIN_NOT_ELIGIBLE", str(selected_id))
    contract = provider.get("standards_provider")
    if not isinstance(contract, dict):
        raise ResolutionError("ERR_STANDARDS_DOMAIN_NOT_ELIGIBLE", str(selected_id))
    for field in ("domain_repo_url", "domain_git_ref"):
        if not isinstance(provider.get(field), str) or not provider[field]:
            raise ResolutionError("ERR_STANDARDS_DOMAIN_NOT_ELIGIBLE", f"{selected_id}: missing {field}")
    for field in ("entrypoint", "pattern_index_ref"):
        if not isinstance(contract.get(field), str) or not contract[field]:
            raise ResolutionError("ERR_STANDARDS_DOMAIN_NOT_ELIGIBLE", f"{selected_id}: missing {field}")

    if initiative and initiative.get("pattern_index_ref"):
        index_ref = initiative["pattern_index_ref"]
        index_source = "initiative"
    elif not initiative and explicit_index:
        if not explicit_provider:
            raise ResolutionError(
                "ERR_PATTERN_INDEX_MISSING",
                "explicit pattern_index_ref requires explicit standards_domain_id",
            )
        index_ref = explicit_index
        index_source = "explicit"
    else:
        index_ref = contract.get("pattern_index_ref")
        index_source = "provider_default"

    if not isinstance(index_ref, str) or not index_ref:
        raise ResolutionError("ERR_PATTERN_INDEX_MISSING", str(selected_id))
    return provider, selection_source, index_source, initiative_id, index_ref


def validate_entrypoint(entrypoint: Path, pattern_index_ref: str) -> None:
    if not entrypoint.is_file():
        raise ResolutionError("ERR_STANDARDS_ENTRYPOINT_INVALID", str(entrypoint))
    try:
        content = entrypoint.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ResolutionError("ERR_STANDARDS_ENTRYPOINT_INVALID", str(exc)) from exc
    headings = {
        line.lstrip("#").strip().lower()
        for line in content.splitlines()
        if line.lstrip().startswith("#")
    }
    required = {"purpose", "ownership", "pattern index", "publication policy", "escalation"}
    if missing := sorted(required - headings):
        raise ResolutionError(
            "ERR_STANDARDS_ENTRYPOINT_INVALID",
            f"missing headings: {', '.join(missing)}",
        )
    lowered = content.lower()
    if pattern_index_ref not in content:
        raise ResolutionError(
            "ERR_STANDARDS_ENTRYPOINT_INVALID",
            f"default pattern index is not linked: {pattern_index_ref}",
        )
    if "receipt" not in lowered or not any(term in lowered for term in ("alternate", "override")):
        raise ResolutionError(
            "ERR_STANDARDS_ENTRYPOINT_INVALID",
            "approved alternate-index and resolution-receipt guidance is required",
        )


def validate_pattern_documents(provider_root: Path, index_data: dict[str, Any]) -> None:
    seen: set[str] = set()
    for index, pattern in enumerate(index_data.get("patterns", [])):
        if not isinstance(pattern, dict):
            continue
        pattern_id = pattern.get("pattern_id")
        if pattern_id in seen:
            raise ResolutionError("ERR_PATTERN_INDEX_INVALID", f"duplicate pattern_id: {pattern_id}")
        if isinstance(pattern_id, str):
            seen.add(pattern_id)
        document = safe_join(
            provider_root, pattern.get("path"), "ERR_PATTERN_INDEX_INVALID"
        )
        if not document.is_file():
            raise ResolutionError(
                "ERR_PATTERN_INDEX_INVALID",
                f"patterns[{index}] document not found: {pattern.get('path')}",
            )


def resolve_commit(provider_root: Path, git_ref: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"{git_ref}^{{commit}}"],
        cwd=provider_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ResolutionError("ERR_REFERENCE_UNRESOLVED", result.stderr.strip())
    return result.stdout.strip()


def resolve(
    registry: dict[str, Any],
    provider_root: Path,
    schema_dir: Path,
    initiatives: dict[str, Any] | None = None,
    initiative_id: str | None = None,
    explicit_provider: str | None = None,
    explicit_index: str | None = None,
    bound_initiative_id: str | None = None,
    resolved_commit_sha: str | None = None,
    resolved_at: str | None = None,
) -> dict[str, Any]:
    provider, selection_source, index_source, bound_initiative, index_ref = choose_provider(
        registry, initiatives, initiative_id, explicit_provider, explicit_index,
        bound_initiative_id,
    )
    contract = provider["standards_provider"]
    entrypoint = safe_join(
        provider_root, contract["entrypoint"], "ERR_STANDARDS_ENTRYPOINT_INVALID"
    )
    if not (provider_root / "AGENTS.md").is_file():
        raise ResolutionError("ERR_STANDARDS_INSTRUCTIONS_MISSING", "root AGENTS.md is required")
    validate_entrypoint(entrypoint, contract["pattern_index_ref"])
    index_path = safe_join(provider_root, index_ref, "ERR_PATTERN_INDEX_INVALID")
    if not index_path.is_file():
        raise ResolutionError("ERR_PATTERN_INDEX_MISSING", str(index_path))
    index_data = load_yaml(index_path)
    try:
        schema = json.loads(
            (schema_dir / "pattern-index.schema.json").read_text(encoding="utf-8-sig")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ResolutionError("ERR_PATTERN_INDEX_INVALID", f"pattern-index schema: {exc}") from exc
    problems = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(index_data),
        key=str,
    )
    if problems:
        raise ResolutionError("ERR_PATTERN_INDEX_INVALID", problems[0].message)
    require_supported_version(index_data, "pattern-index")
    validate_pattern_documents(provider_root, index_data)

    commit_sha = resolved_commit_sha or resolve_commit(provider_root, provider["domain_git_ref"])
    receipt = {
        "spec_name": "standards-resolution-receipt",
        "spec_version": "1.0.0",
        "initiative_context": bound_initiative is not None,
        "selection_source": selection_source,
        "index_selection_source": index_source,
        "standards_domain_id": provider["domain_id"],
        "domain_repo_url": provider["domain_repo_url"],
        "standards_entrypoint": contract["entrypoint"],
        "pattern_index_ref": index_ref,
        "resolved_commit_sha": commit_sha,
        "resolved_at": resolved_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if bound_initiative:
        receipt["initiative_id"] = bound_initiative
    try:
        receipt_schema = json.loads(
            (schema_dir / "standards-resolution-receipt.schema.json").read_text(
                encoding="utf-8-sig"
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ResolutionError("ERR_INVALID_SCHEMA", f"receipt schema: {exc}") from exc
    receipt_problems = list(
        Draft202012Validator(receipt_schema, format_checker=FormatChecker()).iter_errors(receipt)
    )
    if receipt_problems:
        raise ResolutionError("ERR_INVALID_SCHEMA", receipt_problems[0].message)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain-registry", required=True)
    parser.add_argument("--provider-root", required=True)
    parser.add_argument("--initiatives")
    parser.add_argument("--initiative-id")
    parser.add_argument("--standards-domain-id")
    parser.add_argument("--pattern-index-ref")
    parser.add_argument(
        "--bound-initiative-id",
        help="Governed initiative binding; resolution fails if --initiative-id omits or differs from it.",
    )
    parser.add_argument("--schema-dir", default="schemas")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        receipt = resolve(
            load_yaml(Path(args.domain_registry)),
            Path(args.provider_root).resolve(),
            Path(args.schema_dir).resolve(),
            load_yaml(Path(args.initiatives)) if args.initiatives else None,
            args.initiative_id,
            args.standards_domain_id,
            args.pattern_index_ref,
            args.bound_initiative_id,
        )
    except ResolutionError as exc:
        print(json.dumps({"error": exc.code, "message": str(exc)}), file=sys.stderr)
        return 1
    rendered = yaml.safe_dump(receipt, sort_keys=False)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
