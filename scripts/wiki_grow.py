#!/usr/bin/env python3
"""Run the semantic self-growth loop for an open-llm-wiki vault."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    print("$ " + " ".join(command))
    result = subprocess.run(command, cwd=ROOT, text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract claims, QA them, scan contradictions, revise concepts, and lint.")
    parser.add_argument("vault", type=Path)
    parser.add_argument("--ingest-corpus", action="store_true", help="First ingest raw/*_markdown/combined.md files.")
    parser.add_argument("--apply-concept-revision", action="store_true")
    parser.add_argument("--semantic-fail-on", choices=["none", "p0", "p1", "p2"], default="p1")
    parser.add_argument("--skip-lint", action="store_true")
    args = parser.parse_args()

    vault = str(args.vault.resolve())
    if args.ingest_corpus:
        run([sys.executable, str(SCRIPTS / "wiki_ingest_corpus.py"), vault, "--resume"])
    run([sys.executable, str(SCRIPTS / "wiki_claims.py"), vault])
    run(
        [
            sys.executable,
            str(SCRIPTS / "wiki_semantic_qa.py"),
            vault,
            "--write-report",
            "--fail-on",
            args.semantic_fail_on,
        ]
    )
    run([sys.executable, str(SCRIPTS / "wiki_contradictions.py"), vault, "--write-report"])
    revision = [sys.executable, str(SCRIPTS / "wiki_concept_revision.py"), vault]
    if args.apply_concept_revision:
        revision.append("--apply")
    run(revision)
    if not args.skip_lint:
        run([sys.executable, str(SCRIPTS / "wiki_lint.py"), vault, "--fail-on", "p1"])
    print("semantic growth loop completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
