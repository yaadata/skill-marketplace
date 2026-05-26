---
name: memorize
description: Extract durable learnings from chat context into a reviewable artifact and optional Codex memory update note. Use when the user invokes $chat:memorize or asks Codex to remember, memorize, store, or preserve learnings from the current chat.
---

# Chat Memorize

## Purpose

Extract future-useful learnings from the current conversation, review them with the user, write a local artifact first, then store approved learnings to Codex memory only after explicit approval.

This skill is memory-first, not transcript-first. Use `$chat:archive` when the user wants to preserve conversation context. Use `$chat:memorize` when the user wants durable guidance for future sessions.

## Output

Always write a reviewable artifact before writing memory:

```text
./.local/docs/chat-memorize/{NNNNN}_{short-description}.md
```

Memory storage, when approved, writes one batch note under:

```text
/Users/yaadata/.codex/memories/extensions/ad_hoc/notes/
```

Do not directly edit memory registry files.

## Workflow

1. Gather the visible chat or available session context.
2. If the source range is ambiguous, ask interactively whether to consider the full chat or a specific range.
3. Synthesize candidate learnings that may be useful in future Codex sessions.
4. For each candidate learning, challenge it with the user:
   - Is it accurate?
   - Is it durable beyond this moment?
   - Is the scope clear?
   - Is it worth future context?
5. Ask about candidates one at a time.
6. If a candidate is useful but too broad, propose a narrower revision and ask again.
7. Drop candidates the user rejects.
8. Ask whether the approved batch is global, project-specific, or mixed.
9. Write the reviewed artifact using `scripts/create_chat_memorize.py`.
10. Ask whether to store the approved learnings to permanent Codex memory.
11. If approved, write one batch memory update note under the ad-hoc memory notes directory.

## Interaction Rules

- Ask questions one at a time.
- Prefer interactive select for every user decision when available.
- If interactive select is unavailable, ask concise free-form questions.
- Do not write the local artifact until candidate review is complete.
- Do not write any memory update note unless the user explicitly approves memory storage.
- Never store a raw transcript as memory.

## Candidate Quality Bar

Prefer learnings that are:

- durable user preferences
- recurring repo or workflow requirements
- project-specific conventions
- command choices the user repeatedly wants preserved
- constraints that prevent future wrong turns
- stable explanations of how the user wants Codex to behave

Reject or revise learnings that are:

- one-off facts with no future value
- broad preferences without scope
- stale or time-sensitive facts without dates
- guesses not grounded in the chat
- implementation details that belong only in an archive

## Artifact Content

Use this structure:

```md
# {Title}

## Summary

What this memorize session extracted and why.

## Reviewed Learnings

- Learning: concise durable guidance.
  Scope: global, project-specific, or mixed.
  Rationale: why this should affect future sessions.

## Rejected Or Deferred

Candidates that were dropped or need more evidence.

## Memory Update

The exact approved memory-update content, or `Not approved`.
```

Omit empty sections. Keep wording precise and scoped.

## Memory Note Content

When memory storage is approved, write one batch note with:

- project or global scope
- path to the local memorize artifact
- approved durable learnings
- future-session guidance

Name the file:

```text
{timestamp}-chat-memorize-{slug}.md
```

Use a timestamp such as `YYYYMMDD-HHMMSS`.

## Script

Use the bundled script to create the review artifact:

```bash
python3 /path/to/memorize/scripts/create_chat_memorize.py \
  --base-dir "$PWD" \
  --title "Memorize title" \
  --description "short description" \
  --scope "project-specific" \
  --source-range "full chat" \
  --tags "tag-one,tag-two" \
  --body-file /tmp/body.md
```

Pass `--base-dir "$PWD"` so the artifact is written under the current workspace.

