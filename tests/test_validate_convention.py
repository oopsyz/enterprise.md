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
