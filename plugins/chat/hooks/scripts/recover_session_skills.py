#!/usr/bin/env python3
"""Recover active skills for normal Codex startup or resume."""

from __future__ import annotations

import argparse
import json
import os

from session_state import bd_available, emit_common, hash_cwd, read_stdin_json, recall_first, safe_key


MAX_CONTEXT_CHARS = 1_200


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print recovered context as plain text")
    args = parser.parse_args()

    payload = read_stdin_json()
    cwd = str(payload.get("cwd") or os.getcwd())
    session_id = str(payload.get("session_id") or payload.get("sessionId") or "")
    event = str(payload.get("hook_event_name") or payload.get("hookEventName") or "SessionStart")

    if not bd_available():
        return emit_common("bd not found; no session skills recovered")

    record = recall_first(memory_keys(session_id, cwd), cwd)
    if not record:
        return emit_common("No session skill restore record found in Beads")

    context = build_context(record)
    if args.dry_run:
        print(context)
        return 0

    print(
        json.dumps(
            {
                "continue": True,
                "suppressOutput": True,
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "additionalContext": context,
                },
            }
        )
    )
    return 0


def memory_keys(session_id: str, cwd: str) -> list[str]:
    keys: list[str] = []
    if session_id:
        keys.append(f"codex-session-skills-{safe_key(session_id)}")
    keys.append(f"codex-session-skills-latest-{hash_cwd(cwd)}")
    return keys


def build_context(record: str) -> str:
    record = record.strip()
    if len(record) > MAX_CONTEXT_CHARS:
        record = record[: MAX_CONTEXT_CHARS - 40].rstrip() + "\n... [session skill record truncated]"
    return f"""Recovered session skill restore record from Beads.

This is not a chat summary. Use it only to ask the user one at a time before reapplying recovered active skills. If a Task state section exists, use it only as minimal orientation for current or remaining tasks.

{record}
"""


if __name__ == "__main__":
    raise SystemExit(main())
