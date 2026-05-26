---
name: archive
description: Synthesize chat context into a project-local archive note. Use when the user invokes $chat:archive or asks Codex to archive, save, summarize, or preserve the current chat or the chat since a prior archive point.
---

# Chat Archive

## Purpose

Create a reusable Markdown archive of important chat context at:

```text
./.local/docs/chat-archive/{NNNNN}_{short-description}.md
```

Use this skill to preserve decisions, rationale, implementation details, and follow-ups from the current conversation. The archive is project-local by default. Store anything into Codex memory only after an explicit user decision.

## Workflow

1. Gather the major themes of the visible chat or available session context.
2. Ask interactively whether the archive should cover the full chat or a specific point/range, unless the user already gave a precise range.
3. If the user wants "since the last archive point", inspect existing `.local/docs/chat-archive/*.md` when available, then ask the user to confirm the boundary before writing.
4. Present discovered themes one at a time and ask interactively whether to include each theme.
5. Synthesize only the selected themes. Do not invent details.
6. Ask whether the archive is attached to a project.
7. Write the project-local archive using `scripts/create_chat_archive.py`.
8. If project-attached, ask whether to store the discussion to Codex memory.
9. If the user approves memory storage, create one ad-hoc memory update note under `/Users/yaadata/.codex/memories/extensions/ad_hoc/notes/`.

## Interaction Rules

- Ask questions one at a time.
- Prefer interactive select for every user decision when the tool is available.
- If interactive select is not available, ask concise free-form questions.
- Do not write the archive until the user has chosen the source range and selected the themes to preserve.
- Do not write a memory update note unless the user explicitly approves it.
- If there are too many themes, group related themes before asking.

## Archive Content

Use theme sections by default:

```md
# {Title}

## Summary

Brief synthesis of the selected chat range.

## {Theme}

### Decisions

Durable choices the user and Codex made.

### Details

Important context, commands, paths, constraints, and rationale.

### Follow-ups

Open questions, future edits, or checks that remain useful later.
```

Omit empty subsections. Keep the archive concise, but preserve enough detail for a future Codex session to recover the important context.

## Frontmatter

The helper script writes required frontmatter:

- `number`: five-digit archive number, for example `00001`
- `title`: human-readable title
- `date`: current date in `YYYY-MM-DD`
- `project`: project name or `none`
- `source_range`: full chat, confirmed range, or last archive boundary
- `tags`: single-word tags
- `description`: short description used in the filename slug

Normalize the filename description to lowercase hyphenated text.

## Memory Handoff

When the user approves Codex memory storage:

1. Write a small Markdown note in `/Users/yaadata/.codex/memories/extensions/ad_hoc/notes/`.
2. Name it `{timestamp}-chat-archive-{slug}.md`.
3. Include the project, archive path, durable decisions, and future-session guidance.
4. Keep it focused on reusable facts, not a transcript.

Memory updates require explicit approval every time.

## Script

Use the bundled script to create the archive file:

```bash
python3 /path/to/archive/scripts/create_chat_archive.py \
  --base-dir "$PWD" \
  --title "Archive title" \
  --description "short description" \
  --project "project name or none" \
  --source-range "full chat" \
  --tags "tag-one,tag-two" \
  --body-file /tmp/body.md
```

Pass `--base-dir "$PWD"` so the note is written under the current workspace.

