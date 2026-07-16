from __future__ import annotations

import json

from jsonschema import Draft202012Validator, FormatChecker


def validate(schema_dir, name, value):
    schema = json.loads((schema_dir / name).read_text(encoding="utf-8-sig"))
    return list(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(value)
    )


def domain_row(**overrides):
    row = {
        "domain_id": "order",
        "name": "Order",
        "owner": "da",
        "status": "active",
    }
    row.update(overrides)
    return row


def test_registry_1_x_rejects_v2_subtype_fields(schema_dir):
    value = {
        "spec_name": "domain-registry",
        "spec_version": "1.0.0",
        "domains": [domain_row(entry_type="domain")],
    }
    assert validate(schema_dir, "domain-registry.schema.json", value)


def test_registry_2_x_requires_entry_type(schema_dir):
    value = {
        "spec_name": "domain-registry",
        "spec_version": "2.0.0",
        "domains": [domain_row()],
    }
    assert validate(schema_dir, "domain-registry.schema.json", value)


def test_registry_2_x_accepts_both_provider(schema_dir):
    value = {
        "spec_name": "domain-registry",
        "spec_version": "2.0.0",
        "domains": [domain_row(
            entry_type="both",
            domain_repo_url="https://github.com/acme/order",
            domain_entrypoint="DOMAIN.md",
            domain_git_ref="main",
            standards_provider={
                "entrypoint": "STANDARDS.md",
                "pattern_index_ref": "patterns/index.yml",
            },
        )],
    }
    assert validate(schema_dir, "domain-registry.schema.json", value) == []


def test_pattern_index_rejects_unsafe_path(schema_dir):
    value = {
        "spec_name": "pattern-index",
        "spec_version": "1.0.0",
        "patterns": [{
            "pattern_id": "p1",
            "path": "../outside.md",
            "title": "P1",
        }],
    }
    assert validate(schema_dir, "pattern-index.schema.json", value)


def test_initiatives_1_0_schema_rejects_standards_fields(schema_dir):
    value = {
        "spec_name": "initiatives",
        "spec_version": "1.0.0",
        "initiatives": [{
            "initiative_id": "init-a",
            "solution_repo_url": "https://github.com/acme/a",
            "solution_entrypoint": "SOLUTION.md",
            "solution_git_ref": "main",
            "status": "active",
            "standards_domain_id": "standards",
        }],
    }
    assert validate(schema_dir, "initiatives.schema.json", value)


def test_receipt_requires_initiative_id_for_initiative_selection(schema_dir):
    value = {
        "spec_name": "standards-resolution-receipt",
        "spec_version": "1.0.0",
        "initiative_context": True,
        "selection_source": "initiative",
        "index_selection_source": "provider_default",
        "standards_domain_id": "standards",
        "domain_repo_url": "https://github.com/acme/standards",
        "standards_entrypoint": "STANDARDS.md",
        "pattern_index_ref": "patterns.yml",
        "resolved_commit_sha": "a" * 40,
        "resolved_at": "2026-07-16T12:00:00Z",
    }
    assert validate(schema_dir, "standards-resolution-receipt.schema.json", value)


def test_receipt_requires_initiative_id_for_default_fallback(schema_dir):
    value = {
        "spec_name": "standards-resolution-receipt",
        "spec_version": "1.0.0",
        "initiative_context": True,
        "selection_source": "default",
        "index_selection_source": "provider_default",
        "standards_domain_id": "standards",
        "domain_repo_url": "https://github.com/acme/standards",
        "standards_entrypoint": "STANDARDS.md",
        "pattern_index_ref": "patterns.yml",
        "resolved_commit_sha": "a" * 40,
        "resolved_at": "2026-07-16T12:00:00Z",
    }
    assert validate(schema_dir, "standards-resolution-receipt.schema.json", value)


def test_standalone_default_receipt_omits_initiative_id(schema_dir):
    value = {
        "spec_name": "standards-resolution-receipt",
        "spec_version": "1.0.0",
        "initiative_context": False,
        "selection_source": "default",
        "index_selection_source": "provider_default",
        "standards_domain_id": "standards",
        "domain_repo_url": "https://github.com/acme/standards",
        "standards_entrypoint": "STANDARDS.md",
        "pattern_index_ref": "patterns.yml",
        "resolved_commit_sha": "a" * 40,
        "resolved_at": "2026-07-16T12:00:00Z",
    }
    assert validate(schema_dir, "standards-resolution-receipt.schema.json", value) == []


def test_initiative_pipeline_schema_carries_standards_fields(schema_dir):
    value = {
        "spec_name": "initiative-pipeline",
        "spec_version": "1.0.0",
        "initiatives": [{
            "initiative_id": "init-a",
            "standards_domain_id": "standards",
            "pattern_index_ref": "portfolios/a/index.yml",
            "routing": {
                "publish_to_selector": True,
                "selector_status": "active",
            },
        }],
    }
    assert validate(schema_dir, "initiative-pipeline.schema.json", value) == []
