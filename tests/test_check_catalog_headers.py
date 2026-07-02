"""Tests for scripts/check_catalog_headers.py — the writer-side header gate."""

from __future__ import annotations

from pathlib import Path


def write(tmp_path: Path, name: str, content: str) -> Path:
    target = tmp_path / name
    target.write_text(content, encoding="utf-8")
    return target


class TestCanonicalHeaders:
    def test_canonical_header_passes(self, header_checker, tmp_path):
        path = write(tmp_path, "initiatives.yml",
                     'spec_name: initiatives\nspec_version: "1.0.0"\n')
        assert header_checker.check(path) == []

    def test_all_catalog_types_have_expectations(self, header_checker, tmp_path):
        for basename, canonical in header_checker.EXPECTED.items():
            path = write(tmp_path, basename,
                         f'spec_name: {canonical}\nspec_version: "1.0.0"\n')
            assert header_checker.check(path) == [], basename


class TestRejections:
    def test_deprecated_read_alias_is_rejected_for_writers(self, header_checker,
                                                           tmp_path):
        path = write(tmp_path, "domain-implementations.yml",
                     'spec_name: multi-scale-routing\nspec_version: "1.0.0"\n')
        problems = header_checker.check(path)
        assert problems and "multi-scale-routing" in problems[0]

    def test_bare_version_header_is_rejected(self, header_checker, tmp_path):
        path = write(tmp_path, "initiatives.yml", 'version: "1.0"\n')
        problems = "\n".join(header_checker.check(path))
        assert "spec_name" in problems
        assert "no longer satisfies" in problems

    def test_partial_semver_is_rejected(self, header_checker, tmp_path):
        path = write(tmp_path, "initiatives.yml",
                     'spec_name: initiatives\nspec_version: "1.0"\n')
        problems = "\n".join(header_checker.check(path))
        assert "MAJOR.MINOR.PATCH" in problems

    def test_wrong_spec_name_for_type_is_rejected(self, header_checker, tmp_path):
        path = write(tmp_path, "domain-registry.yml",
                     'spec_name: initiatives\nspec_version: "1.0.0"\n')
        assert header_checker.check(path)

    def test_non_mapping_document_is_rejected(self, header_checker, tmp_path):
        path = write(tmp_path, "initiatives.yml", "- a\n- b\n")
        problems = "\n".join(header_checker.check(path))
        assert "mapping" in problems

    def test_unknown_catalog_basename_is_rejected(self, header_checker, tmp_path):
        path = write(tmp_path, "mystery.yml",
                     'spec_name: mystery\nspec_version: "1.0.0"\n')
        problems = "\n".join(header_checker.check(path))
        assert "unknown catalog type" in problems


class TestCli:
    def test_main_exit_codes(self, header_checker, tmp_path, capsys):
        good = write(tmp_path, "initiatives.yml",
                     'spec_name: initiatives\nspec_version: "1.0.0"\n')
        bad = write(tmp_path, "domain-registry.yml", 'version: "1.0"\n')
        assert header_checker.main([str(good)]) == 0
        assert header_checker.main([str(good), str(bad)]) == 1
        assert header_checker.main([]) == 2
        assert header_checker.main([str(tmp_path / "missing.yml")]) == 1
        capsys.readouterr()
