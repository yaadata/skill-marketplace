#!/usr/bin/env python3
"""Recover a compact Codex handoff from Beads memory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


MAX_CONTEXT_CHARS = 2_000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-compact", action="store_true", help="Do not inject context; acknowledge only")
    parser.add_argument("--dry-run", action="store_true", help="Print recovered context as plain text")
    args = parser.parse_args()

    payload = read_stdin_json()
    cwd = str(payload.get("cwd") or os.getcwd())
    session_id = str(payload.get("session_id") or payload.get("sessionId") or "")
    event = str(payload.get("hook_event_name") or payload.get("hookEventName") or "SessionStart")

    if not bd_available():
        return emit_warning("bd not found; no compact handoff recovered")

    handoff = recall_first(memory_keys(session_id, cwd), cwd)
    if not handoff:
        return emit_noop()

    context = build_context(handoff)
    if args.dry_run:
        print(context)
        return 0

    if args.post_compact:
        return emit_success("✓ compact handoff available")

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


def read_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def memory_keys(session_id: str, cwd: str) -> list[str]:
    keys: list[str] = []
    if session_id:
        keys.append(f"codex-compact-{safe_key(session_id)}")
    keys.append(f"codex-compact-latest-{hash_cwd(cwd)}")
    return keys


def safe_key(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]+", "-", value).strip("-")[:160]


def hash_cwd(cwd: str) -> str:
    return hashlib.sha256(cwd.encode("utf-8")).hexdigest()[:16]


def bd_available() -> bool:
    return shutil.which("bd") is not None


def recall_first(keys: list[str], cwd: str) -> str:
    for key in keys:
        try:
            result = subprocess.run(
                ["bd", "recall", key],
                cwd=cwd if Path(cwd).exists() else None,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=8,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        text = result.stdout.strip()
        if result.returncode == 0 and text:
            return text
    return ""


def build_context(handoff: str) -> str:
    handoff = handoff.strip()
    if len(handoff) > MAX_CONTEXT_CHARS:
        handoff = handoff[: MAX_CONTEXT_CHARS - 40].rstrip() + "\n... [handoff truncated]"
    return f"""Recovered compact handoff from Beads.

Use this as concise resume context, not as a full transcript. Ask the user one at a time before reapplying any recovered active skills. Do not offer to reapply chat:before_compact or chat:after_compact.

{handoff}
"""


def emit_success(message: str) -> int:
    print(message)
    return 0


def emit_noop() -> int:
    print(json.dumps({"continue": True}))
    return 0


def emit_warning(message: str) -> int:
    print(json.dumps({"continue": True, "suppressOutput": True, "systemMessage": message}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
