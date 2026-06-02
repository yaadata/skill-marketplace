#!/usr/bin/env python3
"""Recover active skills for normal Codex startup or resume."""

from __future__ import annotations

import argparse
import json
import os
import re

from session_state import bd_available, emit_noop, emit_warning, flatten_content, hash_cwd, read_stdin_json, read_transcript, recall_first, safe_key


MAX_CONTEXT_CHARS = 1_200
MAX_CLEAR_CONTEXT_CHARS = 1_400


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print recovered context as plain text")
    args = parser.parse_args()

    payload = read_stdin_json()
    cwd = str(payload.get("cwd") or os.getcwd())
    session_id = str(payload.get("session_id") or payload.get("sessionId") or "")
    event = str(payload.get("hook_event_name") or payload.get("hookEventName") or "SessionStart")
    source = str(payload.get("source") or "")

    if source == "clear":
        transcript = read_transcript(payload.get("transcript_path") or payload.get("transcriptPath"))
        clear_context = build_clear_plan_context(transcript)
        if clear_context:
            if args.dry_run:
                print(clear_context)
                return 0
            return emit_context(event, clear_context)

    if not bd_available():
        return emit_warning("bd not found; no session skills recovered")

    record = recall_first(memory_keys(session_id, cwd), cwd)
    if not record:
        return emit_noop()

    context = build_context(record)
    if args.dry_run:
        print(context)
        return 0

    return emit_context(event, context)


def emit_context(event: str, context: str) -> int:
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


def build_clear_plan_context(transcript: str) -> str:
    plan = latest_plan_text(transcript)
    if not plan:
        return ""

    skills = selected_implementation_skills(plan)
    if not skills:
        return ""

    plan_path = accepted_plan_path(plan)
    tdd = handoff_value(plan, "TDD")
    pairing = handoff_value(plan, "Pairing")
    slices = handoff_value(plan, "TDD slices")

    lines = [
        "Recovered accepted code plan implementation handoff from clear-context SessionStart.",
        "",
        "The user cleared context and requested implementation. Reapply the selected implementation skills directly; do not ask again because the plan already recorded the handoff decision.",
        "",
        "Selected implementation skills:",
    ]
    lines.extend(f"- ${skill}" for skill in skills)

    if plan_path:
        lines.extend(["", f"Accepted plan path: {plan_path}"])
    if tdd:
        lines.append(f"TDD: {tdd}")
    if pairing:
        lines.append(f"Pairing: {pairing}")
    if slices:
        lines.append(f"TDD slices: {slices}")

    lines.extend(
        [
            "",
            "Implement from the accepted plan and preserve the plan's recorded skill choices.",
        ]
    )
    context = "\n".join(lines)
    if len(context) > MAX_CLEAR_CONTEXT_CHARS:
        context = context[: MAX_CLEAR_CONTEXT_CHARS - 40].rstrip() + "\n... [plan handoff truncated]"
    return context


def latest_plan_text(transcript: str) -> str:
    if not transcript:
        return ""

    text = "\n".join(extract_message_text(transcript)[-80:])
    blocks = re.findall(r"<proposed_plan>\s*(.*?)\s*</proposed_plan>", text, flags=re.IGNORECASE | re.DOTALL)
    if blocks:
        return blocks[-1]
    if "Implementation Handoff" in text:
        return text
    return ""


def extract_message_text(transcript: str) -> list[str]:
    entries: list[str] = []
    for line in transcript.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            item = json.loads(stripped)
        except json.JSONDecodeError:
            entries.append(stripped)
            continue
        if not isinstance(item, dict):
            continue
        text = flatten_content(item.get("content") or item.get("text") or item.get("message"))
        if text:
            entries.append(text)
    return entries


def selected_implementation_skills(plan: str) -> list[str]:
    section = implementation_handoff_section(plan)
    if not section:
        return []

    skills: list[str] = []
    lowered = section.lower()
    if "all slices | selected slices | not selected" in lowered or "selected | not selected" in lowered:
        return []
    if re.search(r"\$?code:tdd\b", section) and not re.search(r"code:tdd\s*[:=-]\s*(no|none|false|not selected)", lowered):
        skills.append("code:tdd")
    if re.search(r"\$?code:pair\b", section) and not re.search(r"code:pair\s*[:=-]\s*(no|none|false|not selected)", lowered):
        skills.append("code:pair")
    return skills


def implementation_handoff_section(plan: str) -> str:
    match = re.search(
        r"(?im)^#{1,4}\s*Implementation Handoff\s*$([\s\S]*?)(?=^#{1,4}\s+\S|\Z)",
        plan,
    )
    return match.group(1).strip() if match else ""


def handoff_value(plan: str, label: str) -> str:
    section = implementation_handoff_section(plan)
    if not section:
        return ""
    match = re.search(rf"(?im)^\s*[-*]?\s*{re.escape(label)}\s*:\s*(.+?)\s*$", section)
    return match.group(1).strip()[:240] if match else ""


def accepted_plan_path(plan: str) -> str:
    section = implementation_handoff_section(plan)
    if not section:
        return ""
    match = re.search(r"(?im)^\s*[-*]?\s*Accepted plan path\s*:\s*(`?)(.+?)\1\s*$", section)
    return match.group(2).strip()[:240] if match else ""


if __name__ == "__main__":
    raise SystemExit(main())
