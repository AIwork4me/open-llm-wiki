#!/usr/bin/env python3
"""Repository quality checks for open-llm-wiki."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SKILL_FIELDS = {
    "allowed-tools",
    "compatibility",
    "description",
    "license",
    "metadata",
    "name",
}
BANNED_TOKENS = [
    chr(0xFFFD),
    chr(0x922B),
    chr(0x9225),
    chr(0x922E),
    chr(0x9241),
    chr(0x9242),
    chr(0x9983),
    chr(0x628E),
    chr(0x6522),
    chr(0x64B1),
    chr(0x9428),
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = read(path)
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} missing YAML frontmatter")
    try:
        _, block, _ = text.split("---\n", 2)
    except ValueError:
        fail(f"{path.relative_to(ROOT)} has malformed YAML frontmatter")

    fields: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.startswith(" ") or line.startswith("-"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def check_skills() -> None:
    skills_dir = ROOT / "skills"
    expected = {"wiki-ingest", "query-writeback", "wiki-lint"}
    actual = {p.name for p in skills_dir.iterdir() if p.is_dir()}
    if actual != expected:
        fail(f"unexpected skill folders: {sorted(actual)}")

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            fail(f"{skill_dir.name} missing SKILL.md")
        fields = parse_frontmatter(skill_file)
        missing = {"name", "description"} - set(fields)
        if missing:
            fail(f"{skill_file.relative_to(ROOT)} missing fields: {sorted(missing)}")
        unexpected = set(fields) - ALLOWED_SKILL_FIELDS
        if unexpected:
            fail(f"{skill_file.relative_to(ROOT)} has unsupported fields: {sorted(unexpected)}")
        name = fields["name"].strip('"')
        if name != skill_dir.name:
            fail(f"{skill_file.relative_to(ROOT)} name {name!r} does not match folder")
        if len(fields["description"]) < 80:
            fail(f"{skill_file.relative_to(ROOT)} description is too short to trigger safely")


def check_docs() -> None:
    required = [
        "README.md",
        "README.zh.md",
        "QUICKSTART.md",
        "SCHEMA.md",
        "AGENTS.md",
        "AGENTS_SNIPPET.md",
        "EXAMPLES.md",
        "SHOWCASE.md",
        "PHILOSOPHY.md",
        "setup.sh",
    ]
    for item in required:
        if not (ROOT / item).exists():
            fail(f"missing required file: {item}")

    if (ROOT / "todo.md").exists():
        fail("todo.md should not be published as stale project guidance")

    for path in ROOT.rglob("*"):
        if path.is_dir() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".py", ".sh", ".yml", ".yaml", ".svg"}:
            continue
        text = read(path)
        for token in BANNED_TOKENS:
            if token in text:
                fail(f"{path.relative_to(ROOT)} contains mojibake token {token!r}")


def check_minimal_vault() -> None:
    vault = ROOT / "examples" / "minimal-vault"
    required = [
        "SCHEMA.md",
        "index.md",
        "log.md",
        "_state/id-counter.md",
        "sources/LLM-0001.md",
        "concepts/attention-mechanisms.md",
        "qa-reports/LLM-0001.md",
        "qa-reports/LLM-0001-contradiction.md",
    ]
    # SCHEMA.md is copied by setup, not stored inside the example vault.
    for item in required[1:]:
        if not (vault / item).exists():
            fail(f"minimal vault missing {item}")

    source_fields = parse_frontmatter(vault / "sources" / "LLM-0001.md")
    if source_fields.get("status") != "stable":
        fail("minimal vault source must be stable")

    qa = read(vault / "qa-reports" / "LLM-0001.md")
    if "verdict: PASS" not in qa:
        fail("minimal vault QA report must pass")

    index = read(vault / "index.md")
    for link in ("[[LLM-0001]]", "[[attention-mechanisms]]"):
        if link not in index:
            fail(f"minimal vault index missing {link}")


def check_setup_script() -> None:
    text = read(ROOT / "setup.sh")
    if ".claude/skills" not in text:
        fail("setup.sh must default to Claude Code skill directory")
    if "OPEN_LLM_WIKI_SKILL_DIR" not in text:
        fail("setup.sh must allow overriding skill directory")
    if not re.search(r"trap\s+cleanup\s+EXIT", text):
        fail("setup.sh must clean temp directory with trap")


def main() -> None:
    check_skills()
    check_docs()
    check_minimal_vault()
    check_setup_script()
    print("quality checks passed")


if __name__ == "__main__":
    main()
