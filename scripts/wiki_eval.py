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

        queue_vault = Path(tmp) / "queue-vault"
        shutil.copytree(vault, queue_vault)
        run([sys.executable, "scripts/wiki_queue.py", str(queue_vault), "plan", "--cadence", "now"])
        queue_path = queue_vault / "_state" / "growth-queue.jsonl"
        rows = [json.loads(line) for line in queue_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        due_at = {
            "discover": "2000-01-01T00:00:00",
            "grow": "2000-01-01T00:05:00",
            "science-review": "2000-01-01T00:10:00",
            "concept-revision": "2000-01-01T00:15:00",
            "lint": "2000-01-01T00:20:00",
        }
        for row in rows:
            row["due_at"] = due_at[str(row["action"])]
        queue_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )
        dry_run = run([sys.executable, "scripts/wiki_queue.py", str(queue_vault), "run-due", "--dry-run"])
        actions = [line.split(": ", 1)[1] for line in dry_run.splitlines() if line.startswith("run ")]
        if actions != ["discover", "grow", "science-review", "lint"]:
            raise SystemExit(f"queue dry-run order is not due-time order: {actions}")

        test_vault = Path(tmp) / "vault"
        run([sys.executable, "scripts/wiki_init.py", str(test_vault), "--repo-root", str(ROOT)])
        run([sys.executable, "scripts/wiki_lint.py", str(test_vault), "--fail-on", "p1"])

    print("runtime eval passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
