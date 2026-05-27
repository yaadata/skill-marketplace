#!/usr/bin/env python3
"""Capture active skills for normal Codex session restart."""

from __future__ import annotations

import argparse
import datetime as dt
import os

from session_state import bd_available, detect_task_state, extract_skills, hash_cwd, read_stdin_json, read_transcript, remember, safe_key


MAX_RECORD_CHARS = 2_000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print record instead of writing to Beads")
    args = parser.parse_args()

    payload = read_stdin_json()
    cwd = str(payload.get("cwd") or os.getcwd())
    session_id = str(payload.get("session_id") or payload.get("sessionId") or "")
    transcript = read_transcript(payload.get("transcript_path") or payload.get("transcriptPath"))
    skills = extract_skills(transcript)
    task_state = detect_task_state(transcript)
    record = build_record(cwd=cwd, session_id=session_id, skills=skills, task_state=task_state)

    if args.dry_run:
        print(record)
        return 0

    if not bd_available():
        return ok("bd not found; session skills not stored")

    stored = False
    errors: list[str] = []
    for key in memory_keys(session_id, cwd):
        ok_result, error = remember(key, record, cwd)
        stored = ok_result or stored
        if error:
            errors.append(f"{key}: {error}")

    if stored:
        return ok("session skills captured")
    return ok(f"bd remember failed; session skills not stored: {errors[0] if errors else 'unknown error'}")


def build_record(*, cwd: str, session_id: str, skills: list[str], task_state: list[str]) -> str:
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    active = "\n".join(f"- ${skill}" for skill in skills) if skills else "- none detected"
    tasks = ""
    if task_state:
        task_lines = "\n".join(f"- {item}" for item in task_state)
        tasks = f"\nTask state:\n{task_lines}\n"

    record = f"""Codex session skill restore
timestamp: {now}
cwd: {cwd}
cwd_hash: {hash_cwd(cwd)}
session: {session_id or "unknown"}

Active skills:
{active}
{tasks}
Restore behavior:
- Ask the user one at a time before reapplying recovered skills.
- Do not reapply chat:before_compact or chat:after_compact.
"""
    if len(record) > MAX_RECORD_CHARS:
        record = record[: MAX_RECORD_CHARS - 40].rstrip() + "\n... [session skill record truncated]\n"
    return record


def memory_keys(session_id: str, cwd: str) -> list[str]:
    keys: list[str] = []
    if session_id:
        keys.append(f"codex-session-skills-{safe_key(session_id)}")
    keys.append(f"codex-session-skills-latest-{hash_cwd(cwd)}")
    return keys


def ok(message: str) -> int:
    import json

    print(json.dumps({"continue": True, "suppressOutput": True, "systemMessage": message}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
