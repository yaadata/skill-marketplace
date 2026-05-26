---
name: todo
description: Generate issue-tracker-ready Markdown todo artifacts from a topic, code area, file, plan, ticket, issue, Slack discussion, or external reference. Use when the user invokes $code:todo or asks Codex to draft a todo, task, issue body, implementation checklist, or tracker-ready Markdown.
---

# Code Todo

Create a Markdown todo artifact that can be pasted into an issue tracker. This skill writes an artifact only; it does not create or update tracker issues.

## Inputs

The user may provide:

- topic or feature area
- code area, symbol, file, or file range
- plan path or pasted plan
- Jira or Linear ticket
- Slack thread or message context
- GitHub issue or pull request
- Codeberg issue or pull request
- pasted notes or discussion

If the input is incomplete, ask one interactive question at a time until the todo is decision-complete.

## Context Gathering

Explore before asking:

- Read local files, plans, tests, docs, and code areas when provided.
- Use available Jira, Linear, Slack, GitHub, or Codeberg tools/connectors when available.
- For Codeberg issue context, use either a URL or `fj issue view <id>` and `fj issue view <id> comments` when the local repo/remote makes that possible.
- If external context cannot be fetched or is ambiguous, ask the user to paste the missing details.

Do not publish to external trackers. Do not create, update, close, or comment on issues.

## Interactive Interview

Act like `grill-me`:

- Ask one decision at a time.
- Use interactive selection for decisions when available.
- Provide a recommended answer with each decision.
- If a question can be answered from local or fetched context, inspect that context instead of asking.
- Continue until the todo is decision-complete.

Clarify:

- target tracker, optional: Jira, Linear, GitHub, Codeberg, Slack-derived, or tracker-neutral
- title/topic
- background and context
- goal
- scope and non-scope
- target code areas
- dependencies and blockers
- implementation notes
- acceptance criteria
- validation expectations
- risks and open questions

## Artifact Path

Write artifacts to:

`./.local/docs/code-todo/{NNNNN}_topic_summary.md`

Determine `NNNNN` by scanning `.local/docs/code-todo/` for files matching five-digit prefixes and incrementing the highest number. Start at `00001`.

Create `topic_summary` as a lowercase slug from the todo topic:

- replace spaces and punctuation with underscores
- collapse repeated underscores
- trim leading and trailing underscores
- keep it concise

Artifacts are not branch-scoped.

## Markdown Format

Use tracker-neutral Markdown by default. Tailor small details to the optional target tracker, but keep the document paste-ready for any tracker.

Include:

- Title
- Context
- Goal
- Scope
- Tasks
- Acceptance Criteria
- Validation
- References
- Risks / Open Questions

Prefer checklists for concrete work items. Keep references specific: file paths, issue URLs, Slack links, plan paths, or command names when known.

## Completion

After writing the artifact, report only the file path and a one-line description. Do not ask to publish the issue unless the user explicitly asks.
