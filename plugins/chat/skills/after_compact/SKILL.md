---
name: after_compact
description: Recover a Beads compact handoff after Codex compaction or session resume. Use when the user invokes $chat:after_compact, asks to restore pre-compact context, or wants active skills considered after resume.
---

# Chat After Compact

## Purpose

Recover the latest compact handoff from Beads after compaction, then re-establish only the context that is still useful.

This skill is intentionally interactive for skills: do not silently reapply recovered skills unless the user explicitly asked for automatic reactivation.

## Workflow

1. Retrieve the handoff by exact session key first:

```bash
bd recall "codex-compact-{session_id}"
```

2. If no exact session handoff exists, retrieve the repository fallback:

```bash
bd recall "codex-compact-latest-{cwd_hash}"
```

3. Bring the concise current-state summary into context.
4. For each recovered skill except `chat:before_compact` and `chat:after_compact`, ask whether to reapply it.
5. Continue from the handoff's `Next deliverable`.

## Recovery Rules

- Keep recovered context short; target 1-2 KB.
- Treat the handoff as stale if the cwd or session does not match.
- Ask one skill-reapply question at a time.
- If Beads is unavailable or no handoff exists, continue normally and say that no compact handoff was found.

## Automatic Hook

The Chat plugin also provides a lifecycle hook that recovers Beads handoff context on `SessionStart` after compact. The hook injects a concise reminder and instructs Codex to ask before reapplying recovered skills.

Normal startup and resume use a separate session-skill restore hook. That path should not summarize the previous chat; it only restores skills and minimal task state when tasks are detected.
