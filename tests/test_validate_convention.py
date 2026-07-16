"""Regression tests for skills/ea-convention/scripts/validate_convention.py.

Each test class maps to a defect class found during review:
crashes on malformed YAML, empty-vs-absent catalog conflation, silent
degradation without jsonschema, schema-dir resolution, and header contract
enforcement.
"""

from __future__ import annotations

from pathlib import Path


def errs(validator) -> str:
    return "\n".join(validator.errors)


def warns(validator) -> str:
    return "\n".join(validator.warnings)


class TestHappyPath:
    def test_full_core_topology_is_clean(self, repo, validator,
                                         valid_initiatives, valid_workstreams,
                                         valid_implementations):
        repo.write(repo.paths["initiatives"], valid_initiatives)
        repo.write(repo.paths["workstreams"], valid_workstreams)
        repo.write("da/order/domain-implementations.yml", valid_implementations)
        assert repo.run() == 0, errs(validator)
        assert validator.errors == []

    def test_flat_da_layout_is_supported(self, repo, validator,
                                         valid_implementations):
        repo.write("da/domain-implementations.yml", valid_implementations)
        assert repo.run() == 0, errs(validator)

    def test_no_catalogs_without_allow_empty_fails(self, repo, validator):
        assert repo.run(allow_empty=False) == 1
        assert "ERR_NO_CONTEXT" in errs(validator)


class TestMalformedYaml:
    """A malformed artifact must produce a controlled error, never a traceback."""

    def test_top_level_list_reports_invalid_yaml(self, repo, validator):
        repo.write(repo.paths["initiatives"], "- just\n- a\n- list\n")
        assert repo.run() == 1
        assert "ERR_INVALID_YAML" in errs(validator)

    def test_top_level_scalar_reports_invalid_yaml(self, repo, validator):
        repo.write(repo.paths["workstreams"], "just a string\n")
        assert repo.run() == 1
        assert "ERR_INVALID_YAML" in errs(validator)

    def test_scalar_entry_in_initiatives_does_not_crash(self, repo, validator):
        repo.write(repo.paths["initiatives"], (
            'spec_name: initiatives\nspec_version: "1.0.0"\n'
            "initiatives:\n  - just-a-string\n"
        ))
        assert repo.run() == 1
        assert "is not a mapping" in errs(validator)

    def test_scalar_entry_in_implementations_does_not_crash(self, repo, validator):
        repo.write("da/domain-implementations.yml", (
            'spec_name: domain-implementations\nspec_version: "1.0.0"\n'
            "implementations:\n  - scalar-impl\n"
        ))
        assert repo.run() == 1
        assert "is not a mapping" in errs(validator)

    def test_mapping_where_list_expected_does_not_crash(self, repo, validator):
        repo.write(repo.paths["initiatives"], (
            'spec_name: initiatives\nspec_version: "1.0.0"\n'
            "initiatives:\n  foo: bar\n"
        ))
        assert repo.run() == 1
        assert "ERR_INVALID_YAML" in errs(validator)


class TestEmptyVersusAbsent:
    """An empty authoritative catalog must still fail dangling references;
    an absent one must not."""

    def test_empty_initiatives_catches_ghost_reference(self, repo, validator,
                                                       valid_workstreams):
        repo.write(repo.paths["initiatives"],
                   'spec_name: initiatives\nspec_version: "1.0.0"\ninitiatives: []\n')
        repo.write(repo.paths["workstreams"], valid_workstreams)
        assert repo.run() == 1
        assert "ERR_INITIATIVE_NOT_FOUND" in errs(validator)

    def test_absent_initiatives_tolerates_workstream_reference(self, repo, validator,
                                                               valid_workstreams):
        repo.write(repo.paths["workstreams"], valid_workstreams)
        assert repo.run() == 0, errs(validator)
        assert "ERR_INITIATIVE_NOT_FOUND" not in errs(validator)

    def test_empty_registry_catches_ghost_domain(self, repo, validator,
                                                 valid_workstreams):
        repo.write(repo.paths["domain_registry"], (
            'spec_name: domain-registry\nspec_version: "1.0.0"\ndomains: []\n'
        ))
        repo.write(repo.paths["workstreams"], valid_workstreams)
        assert repo.run() == 1
        assert "ERR_DOMAIN_NOT_FOUND" in errs(validator)


class TestReferentialIntegrity:
    def test_duplicate_initiative_id_is_ambiguous(self, repo, validator,
                                                  valid_initiatives):
        doubled = valid_initiatives + (
            "  - initiative_id: init-a\n"
            "    solution_repo_url: https://github.com/acme/other\n"
            "    solution_entrypoint: SOLUTION.md\n"
            "    solution_git_ref: main\n"
            "    status: active\n"
        )
        repo.write(repo.paths["initiatives"], doubled)
        assert repo.run() == 1
        assert "ERR_SELECTOR_AMBIGUOUS" in errs(validator)

    def test_routable_workstream_requires_entrypoint(self, repo, validator):
        repo.write(repo.paths["workstreams"], (
            'spec_name: domain-workstreams\nspec_version: "1.0.0"\n'
            "workstreams:\n"
            "  - workstream_id: ws-x\n"
            "    domain_id: order\n"
            "    workstream_entrypoint: null\n"
            "    workstream_git_ref: main\n"
            "    domain_repo_url: https://github.com/acme/domain-order\n"
            "    status: active\n"
        ))
        assert repo.run() == 1
        assert "ERR_ENTRYPOINT_MISSING" in errs(validator)

    def test_explicitly_passed_missing_file_is_an_error(self, repo, validator):
        assert repo.run(explicit=("initiatives",)) == 1
        assert "ERR_ENTRYPOINT_MISSING" in errs(validator)

    def test_workstream_rejects_standards_only_target(self, repo, validator,
                                                      valid_workstreams):
        repo.write(repo.paths["domain_registry"], (
            'spec_name: domain-registry\nspec_version: "2.0.0"\n'
            "domains:\n"
            "  - domain_id: order\n"
            "    name: Standards\n"
            "    owner: ea\n"
            "    entry_type: standards_provider\n"
            "    domain_repo_url: https://github.com/acme/standards\n"
            "    domain_git_ref: main\n"
            "    status: active\n"
            "    standards_provider:\n"
            "      entrypoint: STANDARDS.md\n"
            "      pattern_index_ref: patterns.yml\n"
        ))
        repo.write(repo.paths["workstreams"], valid_workstreams)
        assert repo.run() == 1
        assert "ERR_WORKSTREAM_TARGET_NOT_DOMAIN" in errs(validator)

    def test_multiple_active_standards_defaults_fail(self, repo, validator):
        rows = ""
        for domain_id in ("standards-a", "standards-b"):
            rows += (
                f"  - domain_id: {domain_id}\n"
                "    name: Standards\n"
                "    owner: ea\n"
                "    entry_type: standards_provider\n"
                "    domain_repo_url: https://github.com/acme/standards\n"
                "    domain_git_ref: main\n"
                "    status: active\n"
                "    standards_provider:\n"
                "      enterprise_default: true\n"
                "      entrypoint: STANDARDS.md\n"
                "      pattern_index_ref: patterns.yml\n"
            )
        repo.write(repo.paths["domain_registry"],
                   'spec_name: domain-registry\nspec_version: "2.0.0"\ndomains:\n' + rows)
        assert repo.run() == 1
        assert "ERR_STANDARDS_DEFAULT_AMBIGUOUS" in errs(validator)

    def test_initiative_rejects_in_progress_provider(self, repo, validator):
        repo.write(repo.paths["initiatives"], (
            'spec_name: initiatives\nspec_version: "1.1.0"\n'
            "initiatives:\n"
            "  - initiative_id: init-a\n"
            "    solution_repo_url: https://github.com/acme/solution-a\n"
            "    solution_entrypoint: SOLUTION.md\n"
            "    solution_git_ref: main\n"
            "    status: active\n"
            "    standards_domain_id: standards\n"
        ))
        repo.write(repo.paths["domain_registry"], (
            'spec_name: domain-registry\nspec_version: "2.0.0"\n'
            "domains:\n"
            "  - domain_id: standards\n"
            "    name: Standards\n"
            "    owner: ea\n"
            "    entry_type: standards_provider\n"
            "    domain_repo_url: https://github.com/acme/standards\n"
            "    domain_git_ref: main\n"
            "    status: in_progress\n"
            "    standards_provider:\n"
            "      entrypoint: STANDARDS.md\n"
            "      pattern_index_ref: patterns.yml\n"
        ))
        assert repo.run() == 1
        assert "ERR_STANDARDS_DOMAIN_NOT_ELIGIBLE" in errs(validator)

    def test_local_provider_contract_and_pattern_documents_are_checked(
        self, repo, validator
    ):
        repo.write("AGENTS.md", "# AGENTS\n")
        repo.write("STANDARDS.md", (
            "# STANDARDS\n\n"
            "## Purpose\nStandards.\n\n"
            "## Ownership\nEA.\n\n"
            "## Pattern Index\n[patterns.yml](patterns.yml)\n"
            "Approved alternate indexes are recorded in the resolution receipt.\n\n"
            "## Publication Policy\nApproved content only.\n\n"
            "## Escalation\nContact EA.\n"
        ))
        repo.write("patterns.yml", (
            'spec_name: pattern-index\nspec_version: "1.0.0"\n'
            "patterns:\n"
            "  - pattern_id: missing\n"
            "    path: patterns/missing.md\n"
            "    title: Missing\n"
        ))
        repo.write(repo.paths["domain_registry"], (
            'spec_name: domain-registry\nspec_version: "2.0.0"\n'
            "domains:\n"
            "  - domain_id: standards\n"
            "    name: Standards\n"
            "    owner: ea\n"
            "    entry_type: standards_provider\n"
            "    domain_repo_url: https://github.com/acme/enterprise\n"
            "    domain_git_ref: main\n"
            "    status: active\n"
            "    standards_provider:\n"
            "      enterprise_default: true\n"
            "      entrypoint: STANDARDS.md\n"
            "      pattern_index_ref: patterns.yml\n"
        ))
        assert repo.run(repo_url="https://github.com/acme/enterprise") == 1
        assert "ERR_PATTERN_INDEX_INVALID" in errs(validator)

    def test_initiatives_1_1_selection_rejects_registry_1_x(self, repo, validator):
        repo.write(repo.paths["initiatives"], (
            'spec_name: initiatives\nspec_version: "1.1.0"\n'
            "initiatives:\n"
            "  - initiative_id: init-a\n"
            "    solution_repo_url: https://github.com/acme/solution-a\n"
            "    solution_entrypoint: SOLUTION.md\n"
            "    solution_git_ref: main\n"
            "    status: active\n"
            "    standards_domain_id: order\n"
        ))
        repo.write(repo.paths["domain_registry"], (
            'spec_name: domain-registry\nspec_version: "1.0.0"\n'
            "domains:\n"
            "  - domain_id: order\n"
            "    name: Order\n"
            "    owner: da\n"
            "    status: active\n"
        ))
        assert repo.run() == 1
        assert "standards selection requires domain-registry 2.x" in errs(validator)


class TestHeaderContract:
    def test_bare_version_header_fails_schema(self, repo, validator):
        repo.write(repo.paths["initiatives"], (
            'version: "1.0"\n'
            "initiatives:\n"
            "  - initiative_id: init-a\n"
            "    solution_repo_url: https://github.com/acme/solution-a\n"
            "    solution_entrypoint: SOLUTION.md\n"
            "    solution_git_ref: main\n"
            "    status: active\n"
        ))
        assert repo.run() == 1
        assert "spec_name" in errs(validator)

    def test_standards_fields_require_initiatives_1_1(self, repo, validator):
        repo.write(repo.paths["initiatives"], (
            'spec_name: initiatives\nspec_version: "1.0.0"\n'
            "initiatives:\n"
            "  - initiative_id: init-a\n"
            "    solution_repo_url: https://github.com/acme/solution-a\n"
            "    solution_entrypoint: SOLUTION.md\n"
            "    solution_git_ref: main\n"
            "    status: active\n"
            "    standards_domain_id: standards\n"
        ))
        assert repo.run() == 1
        assert "ERR_VERSION_UNSUPPORTED" in errs(validator)


class TestDegradedValidation:
    def test_missing_jsonschema_warns_instead_of_silence(self, repo, validator,
                                                         monkeypatch,
                                                         valid_initiatives):
        monkeypatch.setattr(validator, "HAS_JSONSCHEMA", False)
        repo.write(repo.paths["initiatives"], valid_initiatives)
        assert repo.run() == 0
        assert "jsonschema is not installed" in warns(validator)

    def test_lint_errors_still_fire_without_jsonschema(self, repo, validator,
                                                       monkeypatch):
        monkeypatch.setattr(validator, "HAS_JSONSCHEMA", False)
        repo.write("da/domain-implementations.yml", (
            'spec_name: domain-implementations\nspec_version: "1.0.0"\n'
            "implementations:\n  foo: bar\n"
        ))
        assert repo.run() == 1
        assert "ERR_INVALID_YAML" in errs(validator)

    def test_missing_schema_file_is_an_error(self, repo, validator, tmp_path,
                                             valid_initiatives):
        empty_schema_dir = tmp_path / "no-schemas-here"
        empty_schema_dir.mkdir()
        repo.write(repo.paths["initiatives"], valid_initiatives)
        assert repo.run(schema_dir=empty_schema_dir) == 1
        assert "ERR_SCHEMA_MISSING" in errs(validator)


class TestSchemaDirResolution:
    def test_explicit_dir_wins(self, validator, tmp_path, schema_dir):
        resolved = validator.resolve_schema_dir(tmp_path, str(schema_dir))
        assert resolved == schema_dir.resolve()

    def test_root_schemas_dir_is_preferred(self, validator, tmp_path):
        vendored = tmp_path / "schemas"
        vendored.mkdir()
        assert validator.resolve_schema_dir(tmp_path, None) == vendored.resolve()

    def test_falls_back_to_tool_schemas_for_adopter_repos(self, validator,
                                                          tmp_path, schema_dir):
        # tmp_path has no schemas/ of its own -> the tool's bundled top-level
        # schemas/ must be found so the default command works everywhere.
        resolved = validator.resolve_schema_dir(tmp_path, None)
        assert resolved == schema_dir.resolve()
        assert (resolved / "initiatives.schema.json").exists()
