#!/usr/bin/env python3
"""
generate_pack.py — Generate an enterprise.md role pack into a target directory.

Usage:
    python generate_pack.py <pack> <target-dir>

Pack types: ea, sa, da, dev

Examples:
    python generate_pack.py ea ~/repos/my-enterprise-repo
    python generate_pack.py da ~/repos/payments-domain-repo
"""

import sys
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PACKS = {
    "ea": {
        "label": "Enterprise Architect (EA)",
        "questions": [
            ("org",             "GitHub org name"),
            ("enterprise-id",   "Enterprise ID (stable, kebab-case)"),
            ("initiative-name", "Initiative display name"),
            ("initiative-id",   "Initiative ID (stable, kebab-case)"),
            ("sa-team",         "SA team/owner name"),
            ("solution-repo",   "Solution repo name"),
            ("domain-id",       "Initial domain ID (kebab-case)"),
            ("domain-name",     "Domain display name"),
            ("domain-repo",     "Domain repo name"),
            ("domain-owner",    "Domain architect/owner name"),
        ],
        "derived": lambda a: {},
    },
    "sa": {
        "label": "Solution Architect (SA)",
        "questions": [
            ("org",                   "GitHub org name"),
            ("solution-key",          "Solution key (stable, kebab-case)"),
            ("solution-display-name", "Solution display name"),
            ("solution-description",  "Solution short description"),
            ("sa-team",               "SA team/owner name"),
            ("enterprise-id",         "Enterprise ID"),
            ("enterprise-repo-url",   "Enterprise repo URL (full git URL)"),
            ("domain-id",             "Initial domain ID (kebab-case)"),
            ("domain-name",           "Domain display name"),
            ("domain-repo",           "Domain repo name"),
            ("domain-owner",          "Domain architect/owner name"),
            ("initiative-id",         "Initiative ID (kebab-case)"),
        ],
        "derived": lambda a: {
            "workstream-id":          f"ws-{a.get('initiative-id','init')}-{a.get('domain-id','domain')}",
            "ws-initiative-domain":   f"ws-{a.get('initiative-id','init')}-{a.get('domain-id','domain')}",
            "initiative-domain-name": f"{a.get('initiative-id','init')} x {a.get('domain-name', a.get('domain-id','domain'))}",
            "domain-list":            a.get("domain-id", "<domain-id>"),
        },
    },
    "da": {
        "label": "Domain Architect (DA)",
        "questions": [
            ("org",                 "GitHub org name"),
            ("domain-id",           "Domain ID (stable, kebab-case)"),
            ("enterprise-repo-url", "Enterprise repo URL (full git URL)"),
            ("implementation-id",   "Initial implementation ID (kebab-case)"),
            ("repo",                "Implementation repo name"),
            ("service-path",        "Service path within that repo (e.g. services/risk)"),
            ("team",                "Owning team name"),
        ],
        "derived": lambda a: {
            "workstream-id": "<workstream-id>",  # transient — user fills in per workstream
        },
    },
    "dev": {
        "label": "Developer (Dev)",
        "questions": [
            ("implementation-id", "Implementation ID for this repo (from domain-implementations.yml)"),
        ],
        "derived": lambda a: {},
    },
}

# Aliases: normalize legacy or variant placeholder names to a canonical key.
# Pack files should use kebab-case; this map handles any residual variants.
ALIASES = {
    "domain_id":                "domain-id",
    "domain":                   "domain-id",
    "WORKSTREAM_ID":            "workstream-id",
    "Human Readable Name":      "solution-display-name",
    "short description":        "solution-description",
    "name-or-team":             "sa-team",
    "kebab-case-stable-key":    "solution-key",
    "Domain Name":              "domain-name",
    "Initiative Name":          "initiative-name",
    "Initiative x Domain Name": "initiative-domain-name",
    "domain-arch-owner":        "domain-owner",
}

# Placeholders left intentionally as-is — optional/example values for the user to fill in manually.
LEAVE_AS_IS = {
    "branch-or-tag",
    "cap-id",
    "capability description",
    "TMF ODA component name",
    "TMFC###",
    "high|medium|low",
    "yyyy-Qn",
    "Domain x Domain Name",
    "kebab-case-description",
    "placeholder",
}


def ask(prompt):
    try:
        value = input(f"  {prompt}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)
    return value


def collect_answers(pack_key):
    config = PACKS[pack_key]
    print(f"\nGenerating {config['label']} pack\n")
    answers = {}
    for key, prompt in config["questions"]:
        if key not in answers:
            answers[key] = ask(prompt)
    answers.update(config["derived"](answers))
    return answers


def substitute(text, answers):
    def replacer(m):
        raw = m.group(1)
        if raw in LEAVE_AS_IS:
            return m.group(0)
        key = ALIASES.get(raw, raw)
        if key in answers:
            return answers[key]
        return m.group(0)  # unknown — leave for manual fill-in

    return re.sub(r"<([^>]+)>", replacer, text)


def copy_pack(pack_key, target_dir, answers):
    src = os.path.join(SCRIPT_DIR, pack_key)
    if not os.path.isdir(src):
        print(f"Error: pack directory not found: {src}")
        sys.exit(1)

    os.makedirs(target_dir, exist_ok=True)
    written = []
    remaining = set()

    for root, dirs, files in os.walk(src):
        rel_root = os.path.relpath(root, src)
        dest_root = os.path.join(target_dir, rel_root) if rel_root != "." else target_dir
        os.makedirs(dest_root, exist_ok=True)

        for fname in files:
            src_path = os.path.join(root, fname)
            dest_path = os.path.join(dest_root, fname)

            with open(src_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = substitute(content, answers)

            for m in re.finditer(r"<([^>]+)>", content):
                if m.group(1) not in LEAVE_AS_IS:
                    remaining.add(m.group(1))

            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)

            written.append(os.path.relpath(dest_path, target_dir))

    return written, remaining


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    pack_key = sys.argv[1].lower()
    target_dir = os.path.abspath(sys.argv[2])

    if pack_key not in PACKS:
        print(f"Error: unknown pack '{pack_key}'. Choose from: {', '.join(PACKS)}")
        sys.exit(1)

    answers = collect_answers(pack_key)
    written, remaining = copy_pack(pack_key, target_dir, answers)

    print(f"\nPack written to: {target_dir}")
    for f in written:
        print(f"  {f}")

    if remaining:
        print("\nPlaceholders still requiring manual fill-in:")
        for p in sorted(remaining):
            print(f"  <{p}>")
    else:
        print("\nAll placeholders substituted.")


if __name__ == "__main__":
    main()
