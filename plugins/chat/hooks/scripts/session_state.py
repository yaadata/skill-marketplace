"""Shared helpers for Chat plugin compact and session hooks."""

from __future__ import annotations

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


def read_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def read_transcript(path_value: Any, max_bytes: int = MAX_TRANSCRIPT_BYTES) -> str:
    if not path_value:
        return ""
    path = Path(str(path_value)).expanduser()
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - max_bytes))
            data = handle.read()
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace")


def extract_text_entries(transcript: str, *, max_lines: int = 400) -> list[str]:
    entries: list[str] = []
    for line in transcript.splitlines()[-max_lines:]:
        text = extract_text_from_line(line)
        if text:
            entries.append(text)
    return entries


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


def detect_task_state(transcript: str) -> list[str]:
    if not transcript:
        return []

    task_patterns = (
        r"\bcurrent task\b",
        r"\btasks? left\b",
        r"\bremaining tasks?\b",
        r"\bcurrent goals?\b",
        r"\bactive goals?\b",
        r"\bnext deliverable\b",
        r"\bin_progress\b",
        r"\bTODO\b",
        r"\bbd[- ][A-Za-z0-9_.:-]+\b",
    )
    combined = re.compile("|".join(task_patterns), re.IGNORECASE)
    entries = [scrub_compact_skills(entry) for entry in extract_text_entries(transcript)]
    candidates = [entry for entry in entries if combined.search(entry)]
    return candidates[-4:]


def safe_key(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]+", "-", value).strip("-")[:160]


def hash_cwd(cwd: str) -> str:
    return hashlib.sha256(cwd.encode("utf-8")).hexdigest()[:16]


def bd_available() -> bool:
    return shutil.which("bd") is not None


def remember(key: str, value: str, cwd: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["bd", "remember", value, "--key", key],
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


def emit_noop() -> int:
    print(json.dumps({"continue": True}))
    return 0


def emit_warning(message: str) -> int:
    print(json.dumps({"continue": True, "suppressOutput": True, "systemMessage": message}))
    return 0


def first_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""
