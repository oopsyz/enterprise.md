#!/usr/bin/env python3
"""Generate initiatives.yml from initiative-pipeline.yml without losing standards selections."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


class GenerationError(Exception):
    pass


SELECTOR_STATUSES = {
    "active", "approved", "ready", "in_progress", "paused", "completed",
    "archived", "deprecated", "inactive",
}


def load_pipeline(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8-sig") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise GenerationError("pipeline must contain a YAML mapping")
    if data.get("spec_name") != "initiative-pipeline":
        raise GenerationError("pipeline spec_name must be 'initiative-pipeline'")
    version = data.get("spec_version")
    if not isinstance(version, str) or re.fullmatch(r"1\.\d+\.\d+", version) is None:
        raise GenerationError("unsupported initiative-pipeline spec_version")
    return data


def generate_selector(pipeline: dict[str, Any]) -> dict[str, Any]:
    selector_rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, source in enumerate(pipeline.get("initiatives", [])):
        if not isinstance(source, dict):
            raise GenerationError(f"initiatives[{index}] must be a mapping")
        routing = source.get("routing")
        if not isinstance(routing, dict) or routing.get("publish_to_selector") is not True:
            continue

        initiative_id = source.get("initiative_id")
        if not isinstance(initiative_id, str) or not initiative_id:
            raise GenerationError(f"initiatives[{index}] requires initiative_id")
        if initiative_id in seen:
            raise GenerationError(f"duplicate published initiative_id: {initiative_id}")
        seen.add(initiative_id)

        required = ("solution_repo_url", "solution_git_ref")
        missing = [field for field in required if not source.get(field)]
        if missing:
            raise GenerationError(
                f"initiative '{initiative_id}' cannot publish without {', '.join(missing)}"
            )

        selector_status = routing.get("selector_status", "active")
        if selector_status not in SELECTOR_STATUSES:
            raise GenerationError(
                f"initiative '{initiative_id}' has invalid selector_status '{selector_status}'"
            )
        row = {
            "initiative_id": initiative_id,
            "name": source.get("name", initiative_id),
            "solution_repo_url": source["solution_repo_url"],
            "solution_entrypoint": source.get("solution_entrypoint", "SOLUTION.md"),
            "solution_git_ref": source["solution_git_ref"],
            "status": selector_status,
        }
        if source.get("it_owner"):
            row["owner"] = source["it_owner"]
        for field in ("standards_domain_id", "pattern_index_ref"):
            if field in source:
                row[field] = source[field]
        if isinstance(source.get("metadata"), dict) and source["metadata"]:
            row["metadata"] = source["metadata"]
        selector_rows.append(row)

    return {
        "spec_name": "initiatives",
        "spec_version": "1.1.0",
        "initiatives": selector_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        selector = generate_selector(load_pipeline(Path(args.pipeline)))
    except (OSError, yaml.YAMLError, GenerationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(selector, sort_keys=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
