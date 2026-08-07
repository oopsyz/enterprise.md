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


def test_workstreams_schema_rejects_embedded_execution_state(schema_dir):
    value = {
        "spec_name": "domain-workstreams",
        "spec_version": "1.0.0",
        "workstreams": [],
        "execution": {
            "state": "not_started",
            "processed_workstreams": [],
            "skipped_workstreams": [],
        },
    }
    assert validate(schema_dir, "domain-workstreams.schema.json", value)


def valid_artifact_ref():
    return {
        "ref_version": "v2",
        "artifact_id": "art-solution-design",
        "version": "1.0.0",
        "repository_url": "https://github.com/acme/solution",
        "repository_entrypoint": "SOLUTION.md",
        "artifact_path": "architecture/solution/design.yml",
        "commit_sha": "a" * 40,
        "digest": "sha256:" + "b" * 64,
    }


def valid_domain_change_handoff():
    return {
        "spec_name": "domain-change-handoff",
        "spec_version": "1.0.0",
        "workstream_id": "ws-init-a-order",
        "initiative_id": "init-a",
        "solution_design_ref": valid_artifact_ref(),
        "target": {
            "kind": "domain",
            "domain_id": "order",
            "baseline_state": "not_materialized",
            "baseline_absence_reason": "No accepted domain baseline exists yet.",
        },
        "requested_delta": {
            "requirements": {"add": ["req-family-plan-eligibility"]},
        },
        "acceptance_criteria": [{
            "criterion_id": "ac-family-plan-order-001",
            "statement": "The Order domain represents family-plan eligibility.",
        }],
    }


def test_domain_change_handoff_accepts_both_baseline_states(schema_dir):
    without_baseline = valid_domain_change_handoff()
    assert validate(schema_dir, "domain-change-handoff.schema.json", without_baseline) == []

    with_baseline = valid_domain_change_handoff()
    with_baseline["target"] = {
        "kind": "domain",
        "domain_id": "order",
        "baseline_state": "existing",
        "baseline_ref": {
            "baseline_id": "order-P14",
            "artifact_ref": valid_artifact_ref(),
        },
    }
    assert validate(schema_dir, "domain-change-handoff.schema.json", with_baseline) == []


def test_domain_change_handoff_rejects_lifecycle_and_ambiguous_baseline(schema_dir):
    value = valid_domain_change_handoff()
    value["work_item_id"] = "wi-runtime-state-does-not-belong-here"
    value["target"]["baseline_ref"] = {
        "baseline_id": "order-P14",
        "artifact_ref": valid_artifact_ref(),
    }
    assert validate(schema_dir, "domain-change-handoff.schema.json", value)


def test_domain_change_handoff_rejects_an_empty_delta(schema_dir):
    value = valid_domain_change_handoff()
    value["requested_delta"] = {
        "requirements": {"add": []},
        "architecture_elements": {"change": []},
    }
    assert validate(schema_dir, "domain-change-handoff.schema.json", value)


def test_workstreams_schema_preserves_legacy_handoff_and_types_change_handoff(schema_dir):
    value = {
        "spec_name": "domain-workstreams",
        "spec_version": "1.0.0",
        "workstreams": [{
            "workstream_id": "ws-init-a-order",
            "initiative_id": "init-a",
            "domain_id": "order",
            "workstream_entrypoint": "inputs/workstreams/ws-init-a-order/WORKSTREAM.md",
            "workstream_git_ref": "feature/ws-init-a-order",
            "handoff_ref": "opaque-legacy-key",
            "change_handoff_ref": {
                "ref_version": "v1",
                "artifact_path": "inputs/workstreams/ws-init-a-order/domain-change-handoff.yml",
                "commit_sha": "a" * 40,
                "digest": "sha256:" + "b" * 64,
            },
            "status": "active",
        }],
    }
    assert validate(schema_dir, "domain-workstreams.schema.json", value) == []


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
