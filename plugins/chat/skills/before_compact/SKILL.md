---
name: before_compact
description: Capture a concise Beads handoff before Codex compaction or shutdown. Use when the user invokes $chat:before_compact, asks to preserve active skills before compacting, or wants the current chat/task state stored for resume.
---

# Chat Before Compact

## Purpose

Create a compact, durable handoff in Beads before compaction.

Use this skill to preserve:

- active skills currently guiding the session, excluding `chat:before_compact` and `chat:after_compact`
- concise chat context
- current task state and discussion position
- the next deliverable or decision needed after resume

## Workflow

1. Identify active skills from the visible chat and session context.
2. Exclude compact-management skills: `chat:before_compact` and `chat:after_compact`.
3. Summarize the current state in no more than a few short bullets.
4. Record what should happen next in deliverable terms.
5. Store the handoff with Beads:

```bash
bd remember "<compact handoff>" --key "codex-compact-{session_id}"
bd remember "<compact handoff>" --key "codex-compact-latest-{cwd_hash}"
```

If the session id is unknown, use only the cwd-latest key.

## Handoff Shape

Keep the handoff concise:

```md
Codex compact handoff
timestamp: ...
event: manual
cwd: ...
session: ...

Active skills:
- $plugin:skill

Current state:
- ...

Next deliverable:
- ...

Risks or assumptions:
- ...
```

Do not store a raw transcript. Prefer a short, human-readable summary that can be safely injected after compaction without bloating context.

## Automatic Hook

The Chat plugin also provides a lifecycle hook that captures a deterministic fallback handoff on `PreCompact`. Manual `$chat:before_compact` should produce a richer handoff when the visible context is important enough to summarize semantically.

Normal session end uses a separate skills-only restore hook, not this compact-summary handoff.
