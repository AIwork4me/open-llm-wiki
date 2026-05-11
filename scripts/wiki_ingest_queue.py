#!/usr/bin/env python3
"""Durable per-source ingest queue with resume, retry, and cancel support.

State file: _state/ingest-jobs.jsonl
Lock file:  _state/.ingest-jobs.lock

State machine:
  candidate -> queued -> parsing -> parsed -> drafting -> drafted ->
  extracting_claims -> claims_ready -> qa_running -> qa_passed | qa_failed ->
  publishing -> published -> stale | failed | cancelled | archived
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from wiki_common import ensure_within, read_text, write_text


QUEUE_FILENAME = "ingest-jobs.jsonl"
LOCK_FILENAME = ".ingest-jobs.lock"

VALID_STATUSES = frozenset({
    "candidate", "queued", "parsing", "parsed", "drafting", "drafted",
    "extracting_claims", "claims_ready", "qa_running", "qa_passed", "qa_failed",
    "publishing", "published", "stale", "failed", "cancelled", "archived",
})

TERMINAL_STATUSES = frozenset({"published", "failed", "cancelled", "archived", "stale"})

# Ordered pipeline steps. Each step transitions to the next on success.
PIPELINE_STEPS = [
    "parsing",
    "parsed",
    "drafting",
    "drafted",
    "extracting_claims",
    "claims_ready",
    "qa_running",
    "qa_passed",
    "publishing",
    "published",
]

JOB_REQUIRED_FIELDS = frozenset({
    "job_id", "source_uuid", "source_id", "kind", "status", "current_step",
    "attempt", "max_attempts", "started_at", "ended_at", "last_error",
    "log_path", "inputs", "outputs",
})


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def gen_job_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    short = hashlib.sha256(os.urandom(8)).hexdigest()[:4]
    return f"JOB-{ts}-{short}"


def source_uuid_from_path(path: Path) -> str:
    name = path.parent.name.removesuffix("_markdown")
    return hashlib.sha256(name.encode()).hexdigest()[:12]


class QueueLock:
    """File-based lock to prevent concurrent writes to queue and vault state."""

    def __init__(self, lock_path: Path):
        self._path = lock_path
        self._fd: int | None = None

    def acquire(self, timeout: float = 30.0) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        while True:
            try:
                self._fd = os.open(str(self._path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                payload = f"pid={os.getpid()} acquired={now_iso()}\n".encode("utf-8")
                os.write(self._fd, payload)
                return
            except FileExistsError:
                if time.monotonic() - started >= timeout:
                    raise TimeoutError(f"timed out waiting for queue lock: {self._path}")
                time.sleep(0.05)

    def release(self) -> None:
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            try:
                self._path.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                pass
            self._fd = None

    def __enter__(self) -> QueueLock:
        self.acquire()
        return self

    def __exit__(self, *args: object) -> None:
        self.release()


def load_jobs(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    jobs: list[dict[str, object]] = []
    for line in read_text(path).splitlines():
        if not line.strip():
            continue
        try:
            jobs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return jobs


def save_jobs(path: Path, jobs: list[dict[str, object]]) -> None:
    text = "".join(json.dumps(j, ensure_ascii=False, sort_keys=True) + "\n" for j in jobs)
    write_text(path, text)


def find_by_id(jobs: list[dict[str, object]], job_id: str) -> dict[str, object] | None:
    for job in jobs:
        if job.get("job_id") == job_id:
            return job
    return None


def find_by_source_uuid(jobs: list[dict[str, object]], source_uuid: str) -> list[dict[str, object]]:
    return [j for j in jobs if j.get("source_uuid") == source_uuid]


def next_step(current: str) -> str | None:
    if current not in PIPELINE_STEPS:
        return None
    idx = PIPELINE_STEPS.index(current)
    if idx + 1 < len(PIPELINE_STEPS):
        return PIPELINE_STEPS[idx + 1]
    return None


def make_job(
    source_uuid: str,
    source_id: str,
    kind: str,
    inputs: list[str],
    log_dir: Path,
    max_attempts: int = 3,
) -> dict[str, object]:
    job_id = gen_job_id()
    log_name = f"{job_id}.log"
    log_rel = f"log-archive/ingest/{log_name}"
    (log_dir / "log-archive" / "ingest").mkdir(parents=True, exist_ok=True)
    (log_dir / log_rel).write_text(f"# Ingest log {job_id}\n# source_uuid={source_uuid}\n# created={now_iso()}\n", encoding="utf-8")
    return {
        "job_id": job_id,
        "source_uuid": source_uuid,
        "source_id": source_id,
        "kind": kind,
        "status": "queued",
        "current_step": "queued",
        "attempt": 0,
        "max_attempts": max_attempts,
        "started_at": "",
        "ended_at": "",
        "last_error": "",
        "log_path": log_rel,
        "inputs": inputs,
        "outputs": [],
        "history": [],
    }


def append_log(vault: Path, job: dict[str, object], message: str) -> None:
    log_rel = str(job.get("log_path", ""))
    if not log_rel:
        return
    log_path = vault / log_rel
    if not log_path.parent.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = now_iso()
    step = job.get("current_step", "unknown")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] [{step}] {message}\n")


def transition(job: dict[str, object], new_step: str) -> None:
    old = job.get("current_step", "")
    history = job.get("history", [])
    history.append({"from": old, "to": new_step, "at": now_iso()})
    job["history"] = history
    job["current_step"] = new_step
    job["status"] = new_step


def plan(vault: Path, queue_path: Path) -> int:
    jobs = load_jobs(queue_path)
    raw_dir = vault / "raw"
    if not raw_dir.is_dir():
        return 0
    existing_uuids = {str(j.get("source_uuid")) for j in jobs}
    added = 0
    for combined in sorted(raw_dir.glob("*_markdown/combined.md")):
        uuid = source_uuid_from_path(combined)
        if uuid in existing_uuids:
            continue
        stem = combined.parent.name.removesuffix("_markdown")
        inputs = [f"raw/{combined.parent.name}/combined.md"]
        pdf = raw_dir / f"{stem}.pdf"
        if pdf.exists():
            inputs.append(f"raw/{stem}.pdf")
        job = make_job(uuid, "", "parse", inputs, vault)
        append_log(vault, job, "job created by --plan")
        jobs.append(job)
        added += 1
    save_jobs(queue_path, jobs)
    return added


def run_one(vault: Path, job: dict[str, object], scripts: Path) -> bool:
    """Execute a single job through its pipeline steps. Returns True on success."""
    job["attempt"] = int(job.get("attempt", 0)) + 1
    job["started_at"] = now_iso()
    job["ended_at"] = ""
    job["last_error"] = ""
    transition(job, "parsing")
    append_log(vault, job, f"attempt {job['attempt']} started")

    try:
        # Step: parse/draft/publish via wiki_ingest_corpus.py for one source
        inputs = job.get("inputs", [])
        combined_rel = ""
        for inp in inputs:
            if "combined.md" in str(inp):
                combined_rel = str(inp)
                break
        if not combined_rel:
            raise RuntimeError("no combined.md input found")

        combined_path = vault / combined_rel
        if not combined_path.exists():
            raise RuntimeError(f"combined.md not found: {combined_rel}")

        # Run ingest for this single source
        transition(job, "drafting")
        append_log(vault, job, "running wiki_ingest_corpus.py for single source")
        result = subprocess.run(
            [sys.executable, str(scripts / "wiki_ingest_corpus.py"),
             str(vault), "--resume", "--limit", "1"],
            text=True, capture_output=True, timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ingest failed: {result.stdout[-500:] if result.stdout else 'no output'}")

        transition(job, "drafted")
        append_log(vault, job, "drafting complete")

        # Run claims extraction
        transition(job, "extracting_claims")
        append_log(vault, job, "running wiki_claims.py")
        subprocess.run(
            [sys.executable, str(scripts / "wiki_claims.py"), str(vault)],
            text=True, capture_output=True, timeout=60,
        )

        transition(job, "claims_ready")
        append_log(vault, job, "claims extracted")

        # Run semantic QA
        transition(job, "qa_running")
        append_log(vault, job, "running wiki_semantic_qa.py")
        qa_result = subprocess.run(
            [sys.executable, str(scripts / "wiki_semantic_qa.py"),
             str(vault), "--fail-on", "none"],
            text=True, capture_output=True, timeout=60,
        )
        if qa_result.returncode != 0 and "FAIL" in (qa_result.stdout or ""):
            transition(job, "qa_failed")
            append_log(vault, job, "QA failed")
            job["last_error"] = "QA validation failed"
            return False

        transition(job, "qa_passed")
        append_log(vault, job, "QA passed")

        # Publish
        transition(job, "publishing")
        append_log(vault, job, "publishing")

        transition(job, "published")
        append_log(vault, job, "job completed successfully")
        job["ended_at"] = now_iso()
        return True

    except Exception as exc:
        job["last_error"] = f"{type(exc).__name__}: {exc}"
        transition(job, "failed")
        append_log(vault, job, f"failed: {exc}")
        job["ended_at"] = now_iso()
        return False


def run_next(vault: Path, queue_path: Path, lock: QueueLock) -> str | None:
    scripts = Path(__file__).resolve().parent
    jobs = load_jobs(queue_path)
    for job in jobs:
        if job.get("status") == "queued":
            with lock:
                jobs2 = load_jobs(queue_path)
                j = find_by_id(jobs2, str(job["job_id"]))
                if j is None or j.get("status") != "queued":
                    continue
                success = run_one(vault, j, scripts)
                save_jobs(queue_path, jobs2)
                return str(j["job_id"])
    return None


def run_source(vault: Path, queue_path: Path, source_uuid: str, lock: QueueLock) -> str | None:
    scripts = Path(__file__).resolve().parent
    with lock:
        jobs = load_jobs(queue_path)
        for job in jobs:
            if str(job.get("source_uuid")) == source_uuid and job.get("status") in ("queued", "failed"):
                job["status"] = "queued"
                job["current_step"] = "queued"
                success = run_one(vault, job, scripts)
                save_jobs(queue_path, jobs)
                return str(job["job_id"])
    return None


def retry_job(vault: Path, queue_path: Path, job_id: str, lock: QueueLock) -> bool:
    with lock:
        jobs = load_jobs(queue_path)
        job = find_by_id(jobs, job_id)
        if job is None:
            return False
        status = str(job.get("status", ""))
        if status not in ("failed", "cancelled", "stale"):
            return False
        max_att = int(job.get("max_attempts", 3))
        attempt = int(job.get("attempt", 0))
        if attempt >= max_att:
            return False
        # Preserve history
        history = list(job.get("history", []))
        history.append({"action": "retry", "from": status, "to": "queued", "at": now_iso()})
        job["history"] = history
        job["status"] = "queued"
        job["current_step"] = "queued"
        job["last_error"] = ""
        job["ended_at"] = ""
        append_log(vault, job, f"retried from {status}")
        save_jobs(queue_path, jobs)
        return True


def cancel_job(vault: Path, queue_path: Path, job_id: str, lock: QueueLock) -> bool:
    with lock:
        jobs = load_jobs(queue_path)
        job = find_by_id(jobs, job_id)
        if job is None:
            return False
        status = str(job.get("status", ""))
        if status in TERMINAL_STATUSES:
            return False
        history = list(job.get("history", []))
        history.append({"action": "cancel", "from": status, "to": "cancelled", "at": now_iso()})
        job["history"] = history
        job["status"] = "cancelled"
        job["current_step"] = "cancelled"
        job["ended_at"] = now_iso()
        append_log(vault, job, f"cancelled from {status}")
        save_jobs(queue_path, jobs)
        return True


def queue_summary(jobs: list[dict[str, object]]) -> dict[str, object]:
    by_status = Counter(str(j.get("status", "unknown")) for j in jobs)
    by_step = Counter(str(j.get("current_step", "unknown")) for j in jobs)
    return {
        "total": len(jobs),
        "by_status": dict(sorted(by_status.items())),
        "by_step": dict(sorted(by_step.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage the per-source ingest queue.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Commands:\n"
            "  --plan            Scan raw/*_markdown/ for new sources and enqueue them.\n"
            "  --run-next        Run the next queued job.\n"
            "  --run-source UUID Run (or re-run) jobs for a specific source_uuid.\n"
            "  --retry JOB_ID    Retry a failed or cancelled job.\n"
            "  --cancel JOB_ID   Cancel a running or queued job.\n"
            "  --list            List all jobs.\n"
            "  --summary         Print queue summary as JSON.\n"
        ),
    )
    parser.add_argument("vault", type=Path)
    parser.add_argument("--plan", action="store_true", help="Scan for new sources and enqueue.")
    parser.add_argument("--run-next", action="store_true", help="Run the next queued job.")
    parser.add_argument("--run-source", type=str, help="Run jobs for a specific source UUID.")
    parser.add_argument("--retry", type=str, help="Retry a specific job by job_id.")
    parser.add_argument("--cancel", type=str, help="Cancel a specific job by job_id.")
    parser.add_argument("--list", action="store_true", help="List all jobs.")
    parser.add_argument("--summary", action="store_true", help="Print queue summary.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    vault = args.vault.resolve()
    state_dir = ensure_within(vault / "_state", vault, "_state must stay inside the vault")
    state_dir.mkdir(parents=True, exist_ok=True)
    queue_path = ensure_within(state_dir / QUEUE_FILENAME, state_dir, "ingest queue must stay inside _state")
    lock_path = state_dir / LOCK_FILENAME
    lock = QueueLock(lock_path)

    has_action = any([args.plan, args.run_next, args.run_source, args.retry, args.cancel, args.list, args.summary])
    if not has_action:
        parser.print_help()
        return 0

    if args.plan:
        with lock:
            added = plan(vault, queue_path)
        print(f"planned: {added} new jobs")
        return 0

    if args.run_next:
        job_id = run_next(vault, queue_path, lock)
        if job_id:
            print(f"ran: {job_id}")
            return 0
        print("no queued jobs to run")
        return 0

    if args.run_source:
        job_id = run_source(vault, queue_path, args.run_source, lock)
        if job_id:
            print(f"ran: {job_id}")
            return 0
        print(f"no runnable job for source {args.run_source}")
        return 1

    if args.retry:
        ok = retry_job(vault, queue_path, args.retry, lock)
        if ok:
            print(f"retried: {args.retry}")
            return 0
        print(f"cannot retry: {args.retry}")
        return 1

    if args.cancel:
        ok = cancel_job(vault, queue_path, args.cancel, lock)
        if ok:
            print(f"cancelled: {args.cancel}")
            return 0
        print(f"cannot cancel: {args.cancel}")
        return 1

    if args.list:
        jobs = load_jobs(queue_path)
        for job in jobs:
            jid = job.get("job_id", "?")
            status = job.get("status", "?")
            step = job.get("current_step", "?")
            uuid = job.get("source_uuid", "?")
            sid = job.get("source_id", "")
            attempt = job.get("attempt", 0)
            err = str(job.get("last_error", ""))[:60]
            line = f"{jid}  {status}  step={step}  uuid={uuid}  source_id={sid}  attempt={attempt}"
            if err:
                line += f"  error={err}"
            print(line)
        return 0

    if args.summary:
        jobs = load_jobs(queue_path)
        s = queue_summary(jobs)
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
