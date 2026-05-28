#!/usr/bin/env python3
"""Capture a compact Codex handoff into Beads memory."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


COMPACT_SKILLS = {"chat:before_compact", "chat:after_compact", "$chat:before_compact", "$chat:after_compact"}
MAX_TRANSCRIPT_BYTES = 180_000
MAX_RECENT_CHARS = 2_400
MAX_HANDOFF_CHARS = 4_000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print handoff instead of writing to Beads")
    args = parser.parse_args()

    payload = read_stdin_json()
    cwd = str(payload.get("cwd") or os.getcwd())
    session_id = str(payload.get("session_id") or payload.get("sessionId") or "")
    event = str(payload.get("hook_event_name") or payload.get("hookEventName") or payload.get("event") or "unknown")
    trigger = str(payload.get("trigger") or "")
    transcript_path = payload.get("transcript_path") or payload.get("transcriptPath")
    transcript = read_transcript(transcript_path)
    recent = recent_context(transcript)
    skills = extract_skills(transcript)
    handoff = build_handoff(
        cwd=cwd,
        session_id=session_id,
        event=event,
        trigger=trigger,
        skills=skills,
        recent=recent,
    )

    if args.dry_run:
        print(handoff)
        return 0

    if not bd_available():
        return emit_warning("bd not found; compact handoff not stored")

    keys = memory_keys(session_id, cwd)
    stored = False
    errors: list[str] = []
    for key in keys:
        ok_result, error = remember(key, handoff, cwd)
        stored = ok_result or stored
        if error:
            errors.append(f"{key}: {error}")

    if stored:
        return emit_success()
    return emit_warning(f"bd remember failed; compact handoff not stored: {errors[0] if errors else 'unknown error'}")


def read_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def read_transcript(path_value: Any) -> str:
    if not path_value:
        return ""
    path = Path(str(path_value)).expanduser()
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - MAX_TRANSCRIPT_BYTES))
            data = handle.read()
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace")


def recent_context(transcript: str) -> str:
    if not transcript:
        return "No transcript was available to the hook."

    entries: list[str] = []
    for line in transcript.splitlines()[-400:]:
        text = extract_text_from_line(line)
        if text:
            entries.append(text)

    if not entries:
        text = transcript[-MAX_RECENT_CHARS:]
    else:
        text = "\n".join(entries[-18:])

    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    text = scrub_compact_skills(text)
    if len(text) > MAX_RECENT_CHARS:
        text = text[-MAX_RECENT_CHARS:]
    return text or "No useful recent transcript text was available."


def extract_text_from_line(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return ""
    try:
        item = json.loads(stripped)
    except json.JSONDecodeError:
        return clean_text(stripped)

    if not isinstance(item, dict):
        return ""

    role = item.get("role") or item.get("type") or item.get("source")
    content = item.get("content") or item.get("text") or item.get("message")
    text = flatten_content(content)
    if not text:
        return ""
    prefix = f"{role}: " if role else ""
    return clean_text(prefix + text)


def flatten_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content") or item.get("input")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts)
    if isinstance(value, dict):
        text = value.get("text") or value.get("content") or value.get("input")
        return text if isinstance(text, str) else ""
    return ""


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:800]


def scrub_compact_skills(text: str) -> str:
    for name in ("$chat:before_compact", "$chat:after_compact", "chat:before_compact", "chat:after_compact"):
        text = text.replace(name, "[compact-management skill]")
    return text


def extract_skills(transcript: str) -> list[str]:
    found: set[str] = set()

    for plugin, skill in re.findall(r"\$([A-Za-z0-9_-]+):([A-Za-z0-9_-]+)", transcript):
        found.add(f"{plugin}:{skill}")

    for skill in re.findall(r"\$([A-Za-z][A-Za-z0-9_-]+)", transcript):
        if skill not in {"chat", "code", "pr"}:
            found.add(skill)

    for skill in re.findall(r"<name>\s*([^<\s]+)\s*</name>", transcript):
        found.add(skill.strip())

    filtered = []
    for skill in sorted(found):
        normalized = skill.strip()
        if normalized in COMPACT_SKILLS:
            continue
        if f"${normalized}" in COMPACT_SKILLS:
            continue
        filtered.append(normalized)
    return filtered[:12]


def build_handoff(
    *,
    cwd: str,
    session_id: str,
    event: str,
    trigger: str,
    skills: list[str],
    recent: str,
) -> str:
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    cwd_hash = hash_cwd(cwd)
    active = "\n".join(f"- ${skill}" for skill in skills) if skills else "- none detected"
    trigger_text = f" ({trigger})" if trigger else ""
    body = f"""Codex compact handoff
timestamp: {now}
event: {event}{trigger_text}
cwd: {cwd}
cwd_hash: {cwd_hash}
session: {session_id or "unknown"}

Active skills:
{active}

Current state:
- Automatic hook capture from recent transcript context.
- Treat this as a compact fallback, not a complete transcript.

Next deliverable:
- Continue from the latest user request and visible repo state.
- If recovered skills are relevant, ask the user one at a time before reapplying them.

Recent context:
{recent}
"""
    if len(body) > MAX_HANDOFF_CHARS:
        body = body[: MAX_HANDOFF_CHARS - 40].rstrip() + "\n... [handoff truncated]\n"
    return body


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


def remember(key: str, handoff: str, cwd: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["bd", "remember", handoff, "--key", key],
            cwd=cwd if Path(cwd).exists() else None,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            timeout=8,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    if result.returncode == 0:
        return True, ""
    return False, first_line(result.stderr) or f"bd remember exited {result.returncode}"


def first_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def emit_success() -> int:
    print(json.dumps({"continue": True}))
    return 0


def emit_warning(message: str) -> int:
    print(json.dumps({"continue": True, "suppressOutput": True, "systemMessage": message}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
