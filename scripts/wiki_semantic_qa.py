#!/usr/bin/env python3
"""Run semantic-quality checks over extracted wiki claims."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from wiki_common import SOURCE_ID_RE, ensure_within, json_dump, read_text, write_text


@dataclass
class Issue:
    priority: str
    subject: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"priority": self.priority, "subject": self.subject, "message": self.message}


def load_claims(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise SystemExit(f"claims file not found: {path}")
    claims = []
    for number, line in enumerate(read_text(path).splitlines(), 1):
        if not line.strip():
            continue
        try:
            claims.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL at {path}:{number}: {exc}") from exc
    return claims


def evidence_target(vault: Path, evidence: str) -> tuple[Path | None, int | None]:
    target = evidence.split("#", 1)[0].strip()
    if not target or target.startswith("http"):
        return None, None
    if "/" not in target and "\\" not in target and not target.endswith((".md", ".txt", ".pdf", ".jsonl")):
        return None, None
    path = (vault / target).resolve()
    try:
        path.relative_to(vault.resolve())
    except ValueError:
        return None, None
    line_match = re.search(r"#L(\d+)", evidence)
    line_number = int(line_match.group(1)) if line_match else None
    return path, line_number


def check_claims(vault: Path, claims: list[dict[str, object]]) -> list[Issue]:
    issues: list[Issue] = []
    source_ids = {path.stem for path in (vault / "sources").glob("LLM-*.md")}
    claims_by_source: dict[str, int] = {}
    for claim in claims:
        source_id = str(claim.get("source_id", ""))
        subject = str(claim.get("claim_id") or source_id or "claim")
        if not SOURCE_ID_RE.fullmatch(source_id):
            issues.append(Issue("P1", subject, "claim has invalid or missing source_id"))
            continue
        claims_by_source[source_id] = claims_by_source.get(source_id, 0) + 1
        if source_id not in source_ids:
            issues.append(Issue("P1", subject, f"claim points to missing source {source_id}"))
        evidence = str(claim.get("evidence", ""))
        if not evidence:
            issues.append(Issue("P1", subject, "claim has no evidence anchor"))
            continue
        if claim.get("claim_type") == "metric" and "normalized_value" not in claim:
            issues.append(Issue("P2", subject, "metric claim has not been normalized"))
        path, line_number = evidence_target(vault, evidence)
        if path is None:
            issues.append(Issue("P2", subject, f"evidence is human-readable but not machine-resolvable: {evidence}"))
            continue
        if not path.exists():
            issues.append(Issue("P1", subject, f"evidence path does not exist: {evidence}"))
            continue
        if line_number is not None:
            lines = read_text(path).splitlines()
            if line_number < 1 or line_number > len(lines):
                issues.append(Issue("P1", subject, f"evidence line is out of range: {evidence}"))
                continue
            value = claim.get("object")
            if value and str(value) not in lines[line_number - 1] and claim.get("claim_type") == "metric":
                issues.append(Issue("P2", subject, f"metric value is not visible on anchored line: {evidence}"))
    for source_id in sorted(source_ids):
        if claims_by_source.get(source_id, 0) == 0:
            issues.append(Issue("P1", source_id, "stable source has no extracted claims"))
    return issues


def markdown_report(vault: Path, claims_path: Path, claims: list[dict[str, object]], issues: list[Issue]) -> str:
    p0 = sum(1 for issue in issues if issue.priority == "P0")
    p1 = sum(1 for issue in issues if issue.priority == "P1")
    p2 = sum(1 for issue in issues if issue.priority == "P2")
    verdict = "PASS" if p0 == 0 and p1 == 0 else "FAIL"
    lines = [
        "# Semantic QA Report",
        f"- date: {datetime.now().strftime('%Y-%m-%d')}",
        f"- vault: {vault}",
        f"- claims: {len(claims)}",
        f"- p0: {p0}",
        f"- p1: {p1}",
        f"- p2: {p2}",
        f"- verdict: {verdict}",
        "",
        "## Findings",
    ]
    if not issues:
        lines.append("- none")
    else:
        for issue in issues:
            lines.append(f"- [{issue.priority}] {issue.subject}: {issue.message}")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            f"- claims file: `{claims_path.as_posix()}`",
            "- P1 means the claim graph is not safe enough for autonomous writeback.",
            "- P2 means the claim is usable but should be improved by a future reviewer.",
        ]
    )
    return "\n".join(lines) + "\n"


def should_fail(issues: list[Issue], fail_on: str) -> bool:
    priorities = {issue.priority for issue in issues}
    if fail_on == "none":
        return False
    if fail_on == "p0":
        return "P0" in priorities
    if fail_on == "p1":
        return bool(priorities.intersection({"P0", "P1"}))
    if fail_on == "p2":
        return bool(priorities.intersection({"P0", "P1", "P2"}))
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Check extracted claims against source evidence.")
    parser.add_argument("vault", type=Path)
    parser.add_argument("--claims", type=Path, help="Defaults to <vault>/claims/claims.jsonl.")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report", type=Path, help="Defaults to <vault>/qa-reports/semantic-qa-YYYY-MM-DD.md.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--fail-on", choices=["none", "p0", "p1", "p2"], default="p1")
    args = parser.parse_args()

    vault = args.vault.resolve()
    claims_path = (args.claims or vault / "claims" / "claims.jsonl").resolve()
    claims = load_claims(claims_path)
    issues = check_claims(vault, claims)
    if args.format == "json":
        print(json_dump({"claims": len(claims), "issues": [issue.as_dict() for issue in issues]}))
    else:
        print(markdown_report(vault, claims_path, claims, issues))
    if args.write_report:
        report = ensure_within(
            args.report or vault / "qa-reports" / f"semantic-qa-{datetime.now().strftime('%Y-%m-%d')}.md",
            vault,
            "semantic QA report must stay inside the vault",
        )
        write_text(report, markdown_report(vault, claims_path, claims, issues))
        print(f"report: {report}")
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
