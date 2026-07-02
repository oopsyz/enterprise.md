"""Shared fixtures for validator and header-checker tests.

The scripts under test are standalone files (not packages), so they are loaded
via importlib from their repo paths. The validator keeps module-level mutable
state (errors/warnings lists, a warn-once flag); the `validator` fixture resets
that state before each test so cases stay independent.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_validator = _load_module(
    "validate_convention",
    REPO_ROOT / "skills" / "ea-convention" / "scripts" / "validate_convention.py",
)
_header_checker = _load_module(
    "check_catalog_headers",
    REPO_ROOT / "scripts" / "check_catalog_headers.py",
)


@pytest.fixture
def validator():
    """The validator module with its collector state reset."""
    _validator.errors.clear()
    _validator.warnings.clear()
    _validator._schema_skipped_warned = False
    yield _validator
    _validator.errors.clear()
    _validator.warnings.clear()
    _validator._schema_skipped_warned = False


@pytest.fixture
def header_checker():
    return _header_checker


@pytest.fixture
def schema_dir() -> Path:
    return SCHEMA_DIR


DEFAULT_PATHS = {
    "initiatives": "ea/architecture/portfolio/initiatives.yml",
    "domain_registry": "ea/architecture/enterprise/domain-registry.yml",
    "solution_index": "sa/solution-index.yml",
    "workstreams": "sa/architecture/solution/domain-workstreams.yml",
    "da_root": "da",
}


@pytest.fixture
def repo(tmp_path: Path):
    """A builder for throwaway convention repos under tmp_path."""

    class Repo:
        root = tmp_path
        paths = dict(DEFAULT_PATHS)

        def write(self, rel_path: str, content: str) -> Path:
            target = tmp_path / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return target

        def run(self, *, explicit=(), repo_url=None, active_only=False,
                allow_empty=True, schema_dir=SCHEMA_DIR):
            return _validator.run(
                tmp_path, schema_dir, dict(self.paths), set(explicit),
                repo_url, active_only, allow_empty,
            )

    return Repo()


VALID_INITIATIVES = """\
spec_name: initiatives
spec_version: "1.0.0"
initiatives:
  - initiative_id: init-a
    solution_repo_url: https://github.com/acme/solution-a
    solution_entrypoint: SOLUTION.md
    solution_git_ref: main
    status: active
"""

VALID_WORKSTREAMS = """\
spec_name: domain-workstreams
spec_version: "1.0.0"
workstreams:
  - workstream_id: ws-init-a-order
    initiative_id: init-a
    domain_id: order
    workstream_entrypoint: inputs/workstreams/ws-init-a-order/WORKSTREAM.md
    workstream_git_ref: feature/ws-init-a-order
    domain_repo_url: https://github.com/acme/domain-order
    status: active
"""

VALID_IMPLEMENTATIONS = """\
spec_name: domain-implementations
spec_version: "1.0.0"
implementations:
  - implementation_id: order-api
    status: active
    repo:
      url: https://github.com/acme/order-api
      paths: ["src/order-api/*"]
"""


@pytest.fixture
def valid_initiatives() -> str:
    return VALID_INITIATIVES


@pytest.fixture
def valid_workstreams() -> str:
    return VALID_WORKSTREAMS


@pytest.fixture
def valid_implementations() -> str:
    return VALID_IMPLEMENTATIONS
