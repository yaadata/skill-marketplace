---
name: create
description: Create concise, problem-focused tickets in Jira, Linear, GitHub, Codeberg or Forgejo, GitLab, and Gitea through an available MCP connector or provider CLI. Use when the user invokes $ticket:create or asks Codex to interactively create an issue or ticket with project, template, assignment, and sprint or iteration choices.
---

# Create Ticket

Create one external ticket through a user-controlled, select-only interview. Describe the problem and desired outcomes. Never prescribe a solution.

## Hard Requirements

- Require a working Beads database discoverable from the launch directory. If `bd memories ticket-create-routing --json` cannot run, stop. Do not initialize Beads implicitly.
- Require the installed Caveman skill. Invoke it before drafting. If unavailable, stop; never substitute ordinary drafting.
- Ask exactly one question at a time through the interactive select action.
- Give every question 2–3 meaningful options. Put the recommended option first and label it recommended.
- Never ask a plain-text or direct free-form question. Rely on the select action's tab/free-form path for custom values or more information; do not add an `Other` option yourself.
- Never create, update, or publish externally before the final preview and explicit `Create ticket` selection.

If interactive select is unavailable, stop and explain that this workflow requires selectable questions with the tab/free-form path.

## Workflow

### 1. Load Saved Routing

Read the project-scoped memory:

```bash
bd memories ticket-create-routing --json
```

Accept only a memory shaped like:

```json
{"version":1,"provider":"jira|linear|git-host","host":"github|codeberg|forgejo|gitlab|gitea|null","interface":"mcp|cli","tool":"tool-identifier"}
```

Ignore malformed or unsupported values. Do not remember projects, repositories, assignees, iterations, templates, or ticket content.

### 2. Select Provider and Tool

Ask which provider to use: Jira, Linear, or Git Host. If saved routing exists, put its provider and tool first, for example `Linear via saved MCP (Recommended)`.

For Git Host, ask for GitHub, Codeberg/Forgejo, GitLab, or Gitea. Then ask for the repository. Use current remotes and accessible repositories to propose up to three concrete `owner/repository` choices.

Read [providers.md](references/providers.md) after the provider is selected. Discover usable MCP connectors and installed CLIs before offering tool choices. Never offer an unavailable tool.

- If the selected provider and host match saved routing and its tool is usable, use it.
- Otherwise, ask the user to choose among the available MCP or CLI interfaces.
- If no supported interface is available, stop and report the missing provider capability.
- If the chosen interface later lacks a required capability, ask: `Switch once`, `Switch and remember`, or `Cancel`. Never mix interfaces silently.

After the user confirms a new remembered route, update it:

```bash
bd remember '{"version":1,"provider":"...","host":"...","interface":"...","tool":"..."}' --key ticket-create-routing
```

A one-time switch must not update memory.

### 3. Discover Provider Metadata

Use the chosen tool read-only before asking ticket questions.

- Jira and Linear: discover accessible projects and ask the user to select one. Include `No project` only when the provider permits it.
- Git Host: use the selected repository as the project boundary.
- Discover only fields required to create a ticket in the selected project, such as a Jira issue type. Ask for each required value with discovered choices.
- Resolve the authenticated user's identity for the later assignment choice.
- Discover accessible ticket templates.
- Discover active provider-native sprints, cycles, or iterations. Do not reinterpret milestones, due dates, or arbitrary scheduling fields as sprints.

When more than three choices exist, rank by current repository, current or active state, and recent relevance. Offer the top choices; the user can use the tab/free-form path for an exact identifier or more information.

### 4. Select Template and Placement

Ask whether to use an accessible existing template or the default structure. If multiple templates exist, offer the most relevant concrete templates.

If an existing template requests a solution, approach, implementation, technical design, or prescribed changes, ask exactly:

- `Sanitize existing template (Recommended)`
- `Use default template`

Never offer a path that retains solution-oriented content.

Ask whether to assign the ticket to the authenticated user. Recommend based on context; do not assume assignment.

If a native sprint, cycle, or iteration exists, ask which one to use and include an unplanned or no-iteration choice. Skip this question when no native iteration is accessible.

### 5. Gather Problem Content

Gather a title, Context, Scope, and Definition of Done. Derive 2–3 concise candidate answers from the user's request, conversation, repository evidence, and provider metadata. Each question remains a select; the tab/free-form path accepts custom wording or missing facts.

If evidence is insufficient, offer evidence-gathering choices such as inspecting the current repository or using the supplied conversation. Do not invent facts.

Use the default body when no existing template is selected:

```markdown
## Context

{Problem, impact, and relevant evidence.}

## Scope

{Affected behavior and boundaries. No implementation tasks.}

## Definition of Done

- [ ] {Observable outcome.}
```

For an existing template, preserve useful problem-oriented sections and required provider fields. Keep Context, Scope, and Definition of Done unless the selected template expresses the same information under equivalent headings.

### 6. Draft with Caveman

Ask for drafting intensity:

- `Caveman Lite (Recommended)` — concise professional sentences.
- `Caveman Full` — terse fragments where meaning stays clear.

Invoke the installed Caveman skill at the selected intensity before writing the title or body. Keep provider identifiers, error text, and technical symbols exact.

The title and body must describe the problem, impact, boundaries, evidence, and observable outcomes. They must not contain:

- proposed solutions or recommendations
- implementation steps or task breakdowns
- technical designs or architecture choices
- prescribed tools, APIs, data models, or code changes

Scan the draft for headings or language such as `Solution`, `Approach`, `Implementation`, `Technical Design`, `we should`, or `change X to Y`. Rewrite violations before previewing. Definition of Done states externally observable results, never the means used to reach them.

### 7. Preview and Create

Show one complete preview containing:

- provider, host, and selected tool
- project or repository
- required provider fields
- assignee
- sprint, cycle, or iteration
- selected template and any sanitization
- title and complete body

Then ask:

- `Create ticket (Recommended)` only when the preview is complete and accurate
- `Revise`
- `Cancel`

`Revise` starts select-based field revision and returns to the full preview. `Cancel` performs no external write.

On `Create ticket`, use only the confirmed values and chosen interface. If creation fails, show the exact error and ask `Retry`, `Switch tool`, or `Cancel`; a switch still requires a new preview and confirmation.

Return the created ticket key or number, URL, provider, and project or repository. Do not perform follow-up edits.
