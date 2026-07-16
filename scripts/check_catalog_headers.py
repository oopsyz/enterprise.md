#!/usr/bin/env python3
"""Check the header contract (Section 5.2) for canonical catalog files.

Starter packs and templates carry intentional placeholder values (for example
`<solution-key>`) that deliberately violate schema `pattern` constraints, so full
schema validation is not meaningful for them. This lightweight check verifies only
the header discipline every canonical catalog MUST satisfy:

  * `spec_name` is present and equals the canonical value for that catalog type
    (this is a writer-side gate, so deprecated read aliases such as
    `multi-scale-routing` are NOT accepted), and
  * `spec_version` is present and is a full MAJOR.MINOR.PATCH version.

A bare `version` header no longer satisfies the contract.

Usage:
    python check_catalog_headers.py FILE [FILE ...]

Exit codes:
    0  all files satisfy the header contract
    1  one or more files failed
    2  usage / load error
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

# basename -> canonical spec_name that writers MUST emit.
# This is a writer-side gate: deprecated read aliases (e.g. multi-scale-routing)
# are intentionally NOT accepted here, because starter packs and templates must
# emit only the canonical value.
EXPECTED = {
    "initiatives.yml":            "initiatives",
    "domain-workstreams.yml":     "domain-workstreams",
    "domain-implementations.yml": "domain-implementations",
    "domain-registry.yml":        "domain-registry",
    "solution-index.yml":         "solution-index",
    "domain-roadmap.yml":         "domain-roadmap",
    "initiative-pipeline.yml":    "initiative-pipeline",
    "pattern-index.yml":          "pattern-index",
    "standards-resolution-receipt.yml": "standards-resolution-receipt",
}


def check(path: Path) -> list[str]:
    problems: list[str] = []
    canonical = EXPECTED.get(path.name)
    if canonical is None:
        return [f"{path}: unknown catalog type '{path.name}' (no header contract defined)"]

    with open(path, encoding="utf-8-sig") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return [f"{path}: expected a YAML mapping at the top level"]

    spec_name = data.get("spec_name")
    if spec_name != canonical:
        problems.append(f"{path}: spec_name is {spec_name!r}, expected {canonical!r}")

    spec_version = data.get("spec_version")
    if not isinstance(spec_version, str) or not SEMVER.match(spec_version):
        problems.append(f"{path}: spec_version is {spec_version!r}, expected MAJOR.MINOR.PATCH")
        if "version" in data and "spec_version" not in data:
            problems.append(f"{path}: bare 'version' no longer satisfies the header contract")

    return problems


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: check_catalog_headers.py FILE [FILE ...]", file=sys.stderr)
        return 2

    all_problems: list[str] = []
    for arg in argv:
        path = Path(arg)
        if not path.exists():
            all_problems.append(f"{path}: file not found")
            continue
        all_problems.extend(check(path))

    if all_problems:
        print(f"Header contract FAILED ({len(all_problems)} problem(s)):")
        for p in all_problems:
            print(f"  {p}")
        return 1

    print(f"Header contract OK — {len(argv)} file(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
