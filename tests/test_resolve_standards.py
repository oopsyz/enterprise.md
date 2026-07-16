from __future__ import annotations


def registry():
    return {
        "spec_name": "domain-registry",
        "spec_version": "2.0.0",
        "domains": [{
            "domain_id": "standards",
            "name": "Standards",
            "owner": "ea",
            "entry_type": "standards_provider",
            "domain_repo_url": "https://github.com/acme/standards",
            "domain_git_ref": "main",
            "status": "active",
            "standards_provider": {
                "enterprise_default": True,
                "entrypoint": "STANDARDS.md",
                "pattern_index_ref": "patterns.yml",
            },
        }],
    }


def prepare_provider(repo):
    repo.write("AGENTS.md", "# AGENTS\n")
    repo.write("STANDARDS.md", (
        "# STANDARDS\n\n"
        "## Purpose\nGoverned standards.\n\n"
        "## Ownership\nOwned by EA.\n\n"
        "## Pattern Index\nDefault: [patterns.yml](patterns.yml).\n"
        "Approved alternate indexes may be selected; the resolution receipt records the result.\n\n"
        "## Publication Policy\nOnly approved content is published.\n\n"
        "## Escalation\nContact EA.\n"
    ))
    repo.write("patterns.yml", (
        'spec_name: pattern-index\nspec_version: "1.0.0"\n'
        "patterns:\n"
        "  - pattern_id: p1\n"
        "    path: patterns/p1.md\n"
        "    title: Pattern One\n"
    ))
    repo.write("patterns/p1.md", "# Pattern One\n")


def test_default_resolution_emits_receipt(repo, standards_resolver, schema_dir):
    prepare_provider(repo)
    receipt = standards_resolver.resolve(
        registry(), repo.root, schema_dir,
        resolved_commit_sha="a" * 40,
        resolved_at="2026-07-16T12:00:00Z",
    )
    assert receipt["selection_source"] == "default"
    assert receipt["index_selection_source"] == "provider_default"
    assert receipt["initiative_context"] is False
    assert receipt["resolved_commit_sha"] == "a" * 40


def test_initiative_selection_rejects_explicit_override(standards_resolver):
    initiatives = {
        "spec_name": "initiatives",
        "spec_version": "1.1.0",
        "initiatives": [{
            "initiative_id": "init-a",
            "standards_domain_id": "standards",
        }]
    }
    try:
        standards_resolver.choose_provider(
            registry(), initiatives, "init-a", "standards", None
        )
    except standards_resolver.ResolutionError as exc:
        assert exc.code == "ERR_STANDARDS_OVERRIDE_NOT_AUTHORIZED"
    else:
        raise AssertionError("override should fail")


def test_initiative_receipt_records_provenance(repo, standards_resolver, schema_dir):
    prepare_provider(repo)
    initiatives = {
        "spec_name": "initiatives",
        "spec_version": "1.1.0",
        "initiatives": [{
            "initiative_id": "init-a",
            "standards_domain_id": "standards",
        }]
    }
    receipt = standards_resolver.resolve(
        registry(), repo.root, schema_dir, initiatives, "init-a",
        resolved_commit_sha="b" * 40,
        resolved_at="2026-07-16T12:00:00Z",
    )
    assert receipt["selection_source"] == "initiative"
    assert receipt["initiative_context"] is True
    assert receipt["initiative_id"] == "init-a"


def test_initiative_index_override_precedes_provider_default(
    repo, standards_resolver, schema_dir
):
    prepare_provider(repo)
    repo.write("initiative-index.yml", (
        'spec_name: pattern-index\nspec_version: "1.0.0"\n'
        "patterns:\n"
        "  - pattern_id: p1\n"
        "    path: patterns/p1.md\n"
        "    title: Pattern One\n"
    ))
    initiatives = {
        "spec_name": "initiatives",
        "spec_version": "1.1.0",
        "initiatives": [{
            "initiative_id": "init-a",
            "standards_domain_id": "standards",
            "pattern_index_ref": "initiative-index.yml",
        }],
    }
    receipt = standards_resolver.resolve(
        registry(), repo.root, schema_dir, initiatives, "init-a",
        resolved_commit_sha="b" * 40,
        resolved_at="2026-07-16T12:00:00Z",
    )
    assert receipt["index_selection_source"] == "initiative"
    assert receipt["pattern_index_ref"] == "initiative-index.yml"


def test_initiative_default_fallback_still_records_context(
    repo, standards_resolver, schema_dir
):
    prepare_provider(repo)
    initiatives = {
        "spec_name": "initiatives",
        "spec_version": "1.0.0",
        "initiatives": [{"initiative_id": "init-a"}],
    }
    receipt = standards_resolver.resolve(
        registry(), repo.root, schema_dir, initiatives, "init-a",
        resolved_commit_sha="c" * 40,
        resolved_at="2026-07-16T12:00:00Z",
    )
    assert receipt["selection_source"] == "default"
    assert receipt["initiative_context"] is True
    assert receipt["initiative_id"] == "init-a"


def test_explicit_provider_and_index_without_initiative(
    repo, standards_resolver, schema_dir
):
    prepare_provider(repo)
    repo.write("alternate.yml", (
        'spec_name: pattern-index\nspec_version: "1.0.0"\n'
        "patterns:\n"
        "  - pattern_id: p1\n"
        "    path: patterns/p1.md\n"
        "    title: Pattern One\n"
    ))
    receipt = standards_resolver.resolve(
        registry(), repo.root, schema_dir,
        explicit_provider="standards", explicit_index="alternate.yml",
        resolved_commit_sha="d" * 40,
        resolved_at="2026-07-16T12:00:00Z",
    )
    assert receipt["selection_source"] == "explicit"
    assert receipt["initiative_context"] is False
    assert receipt["index_selection_source"] == "explicit"
    assert receipt["pattern_index_ref"] == "alternate.yml"


def test_bound_initiative_cannot_be_suppressed(standards_resolver):
    try:
        standards_resolver.choose_provider(
            registry(), bound_initiative_id="init-a"
        )
    except standards_resolver.ResolutionError as exc:
        assert exc.code == "ERR_STANDARDS_INITIATIVE_CONTEXT_REQUIRED"
    else:
        raise AssertionError("suppressed initiative context should fail")


def test_in_progress_provider_is_ineligible(standards_resolver):
    data = registry()
    data["domains"][0]["status"] = "in_progress"
    try:
        standards_resolver.choose_provider(data, explicit_provider="standards")
    except standards_resolver.ResolutionError as exc:
        assert exc.code == "ERR_STANDARDS_DOMAIN_NOT_ELIGIBLE"
    else:
        raise AssertionError("in-progress provider should fail")


def test_unknown_registry_major_fails_closed(standards_resolver):
    data = registry()
    data["spec_version"] = "3.0.0"
    try:
        standards_resolver.choose_provider(data)
    except standards_resolver.ResolutionError as exc:
        assert exc.code == "ERR_VERSION_UNSUPPORTED"
    else:
        raise AssertionError("unknown major should fail")


def test_registry_1_x_cannot_resolve_standards(standards_resolver):
    data = registry()
    data["spec_version"] = "1.0.0"
    for row in data["domains"]:
        row.pop("entry_type", None)
        row.pop("standards_provider", None)
    try:
        standards_resolver.choose_provider(data)
    except standards_resolver.ResolutionError as exc:
        assert exc.code == "ERR_VERSION_UNSUPPORTED"
    else:
        raise AssertionError("domain-registry 1.x cannot resolve standards")


def test_duplicate_provider_id_is_ambiguous(standards_resolver):
    data = registry()
    data["domains"].append(dict(data["domains"][0]))
    try:
        standards_resolver.choose_provider(data)
    except standards_resolver.ResolutionError as exc:
        assert exc.code == "ERR_SELECTOR_AMBIGUOUS"
    else:
        raise AssertionError("duplicate provider ID should fail")


def test_missing_root_agents_fails(repo, standards_resolver, schema_dir):
    prepare_provider(repo)
    (repo.root / "AGENTS.md").unlink()
    try:
        standards_resolver.resolve(
            registry(), repo.root, schema_dir, resolved_commit_sha="e" * 40
        )
    except standards_resolver.ResolutionError as exc:
        assert exc.code == "ERR_STANDARDS_INSTRUCTIONS_MISSING"
    else:
        raise AssertionError("missing AGENTS.md should fail")


def test_invalid_entrypoint_contract_fails(repo, standards_resolver, schema_dir):
    prepare_provider(repo)
    repo.write("STANDARDS.md", "# STANDARDS\n")
    try:
        standards_resolver.resolve(
            registry(), repo.root, schema_dir, resolved_commit_sha="f" * 40
        )
    except standards_resolver.ResolutionError as exc:
        assert exc.code == "ERR_STANDARDS_ENTRYPOINT_INVALID"
    else:
        raise AssertionError("invalid entrypoint should fail")


def test_missing_pattern_document_fails(repo, standards_resolver, schema_dir):
    prepare_provider(repo)
    (repo.root / "patterns" / "p1.md").unlink()
    try:
        standards_resolver.resolve(
            registry(), repo.root, schema_dir, resolved_commit_sha="a" * 40
        )
    except standards_resolver.ResolutionError as exc:
        assert exc.code == "ERR_PATTERN_INDEX_INVALID"
    else:
        raise AssertionError("missing pattern document should fail")


def test_unsafe_explicit_index_fails(repo, standards_resolver, schema_dir):
    prepare_provider(repo)
    try:
        standards_resolver.resolve(
            registry(), repo.root, schema_dir,
            explicit_provider="standards", explicit_index="../patterns.yml",
            resolved_commit_sha="a" * 40,
        )
    except standards_resolver.ResolutionError as exc:
        assert exc.code == "ERR_PATTERN_INDEX_INVALID"
    else:
        raise AssertionError("unsafe index path should fail")


def test_generator_preserves_standards_selection(initiatives_generator):
    selector = initiatives_generator.generate_selector({
        "spec_name": "initiative-pipeline",
        "spec_version": "1.0.0",
        "initiatives": [{
            "initiative_id": "init-a",
            "name": "A",
            "solution_repo_url": "https://github.com/acme/a",
            "solution_git_ref": "main",
            "standards_domain_id": "standards",
            "pattern_index_ref": "portfolios/a/index.yml",
            "routing": {
                "publish_to_selector": True,
                "selector_status": "active",
            },
        }],
    })
    row = selector["initiatives"][0]
    assert selector["spec_version"] == "1.1.0"
    assert row["standards_domain_id"] == "standards"
    assert row["pattern_index_ref"] == "portfolios/a/index.yml"
