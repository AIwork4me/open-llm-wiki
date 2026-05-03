#!/usr/bin/env python3
"""Smoke evaluation for the open-llm-wiki runtime."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path = ROOT) -> str:
    result = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(result.returncode)
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Run runtime smoke evaluations.")
    parser.add_argument("--vault", type=Path, default=ROOT / "examples" / "minimal-vault")
    args = parser.parse_args()

    vault = args.vault.resolve()
    run([sys.executable, "scripts/wiki_lint.py", str(vault), "--fail-on", "p1"])
    search_output = run([sys.executable, "scripts/wiki_search.py", str(vault), "attention transformer", "--limit", "2"])
    if "Attention Is All You Need" not in search_output:
        raise SystemExit("search eval did not find expected source page")
    proposal = run(
        [
            sys.executable,
            "scripts/wiki_writeback.py",
            str(vault),
            "--target",
            "concepts/attention-mechanisms.md",
            "--query",
            "Why did attention become central?",
            "--body",
            "Attention became central because it created direct token-to-token interaction paths. [[LLM-0001]]",
        ]
    )
    if "Query-Derived Note" not in proposal or "Proposed log entry" not in proposal:
        raise SystemExit("writeback eval did not produce a reviewable proposal")

    with tempfile.TemporaryDirectory() as tmp:
        growth_vault = Path(tmp) / "growth-vault"
        shutil.copytree(vault, growth_vault)
        run(
            [
                sys.executable,
                "scripts/wiki_grow.py",
                str(growth_vault),
                "--discover-sources",
                "--plan-queue",
                "--queue-cadence",
                "weekly",
                "--science-review",
                "--apply-concept-revision",
            ]
        )
        run([sys.executable, "scripts/wiki_queue.py", str(growth_vault), "list"])
        run([sys.executable, "scripts/wiki_lint.py", str(growth_vault), "--fail-on", "p1"])

        test_vault = Path(tmp) / "vault"
        run([sys.executable, "scripts/wiki_init.py", str(test_vault), "--repo-root", str(ROOT)])
        run([sys.executable, "scripts/wiki_lint.py", str(test_vault), "--fail-on", "p1"])

        qa_vault = Path(tmp) / "qa-vault"
        shutil.copytree(vault, qa_vault)
        claim = {
            "claim_id": "claim-missing-anchor",
            "source_id": "LLM-0001",
            "claim_type": "metric",
            "predicate": "WMT 2014 EN-DE BLEU, base",
            "object": "27.3",
            "value": 27.3,
            "unit": "",
            "baseline": "prior systems",
            "normalized_value": 27.3,
            "evidence": "sources/LLM-0001.md#Missing Anchor",
            "concepts": ["attention-mechanisms"],
        }
        (qa_vault / "claims" / "claims.jsonl").write_text(
            json.dumps(claim, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        qa_output = run(
            [
                sys.executable,
                "scripts/wiki_semantic_qa.py",
                str(qa_vault),
                "--format",
                "json",
                "--fail-on",
                "none",
            ]
        )
        issues = json.loads(qa_output)["issues"]
        if not any("heading anchor does not exist" in item["message"] for item in issues):
            raise SystemExit("semantic QA eval did not flag a missing heading anchor")

    print("runtime eval passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
