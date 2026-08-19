---
name: create
description: Create concise, problem-focused tickets in Jira, Linear, GitHub, Codeberg or Forgejo, GitLab, and Gitea through an available MCP connector or provider CLI. Use when the user invokes $ticket:create or asks Codex to create an issue or ticket automatically or through a paired interview with project, template, assignment, and sprint or iteration choices.
---

# Create Ticket

Create one external ticket in auto or paired mode. Describe the problem and desired outcomes. Never prescribe a solution.

## Hard Requirements

- Require a working Beads database discoverable from the launch directory. If `bd memories ticket-create-routing --json` cannot run, stop. Do not initialize Beads implicitly.
- Require the installed Caveman skill. Invoke it before drafting. If unavailable, stop; never substitute ordinary drafting.
- After prerequisite checks, the first user-facing question on every invocation must be `Run in auto mode?`.
- Ask exactly one question at a time through the interactive select action.
- Give every question 2–3 meaningful options. Put the recommended option first and label it recommended.
- Never ask a plain-text or direct free-form question. Rely on the select action's tab/free-form path for custom values or more information; do not add an `Other` option yourself.
- Never create, update, or publish externally before the complete decision preview and explicit `Create ticket` selection.

If interactive select is unavailable, stop and explain that this workflow requires selectable questions with the tab/free-form path.

## Workflow

### 1. Choose Mode

Ask exactly:

> Run in auto mode?

Options:

- `Yes (Recommended)` — decide ticket parameters, explain them, and ask only about unresolved fields.
- `No` — pair on ticket creation one decision at a time.

Do not ask another question before this one.

### 2. Load Saved Routing

Read the project-scoped memory:

```bash
bd memories ticket-create-routing --json
```

Accept only a memory shaped like:

```json
{"version":1,"provider":"jira|linear|git-host","host":"github|codeberg|forgejo|gitlab|gitea|null","interface":"mcp|cli","tool":"tool-identifier"}
```

Ignore malformed or unsupported values. Do not remember projects, repositories, assignees, iterations, templates, mode, or ticket content.

### 3. Resolve Parameters

Read [providers.md](references/providers.md) for the selected or inferred provider. Discover usable MCP connectors and installed CLIs before choosing or offering tools. Never use an unavailable tool.

Resolve all of these parameters:

- provider and Git host when applicable
- MCP or CLI tool
- Jira or Linear project, or Git repository
- provider-required fields such as Jira issue type
- existing or default template and any sanitization
- assignment to the authenticated user or unassigned
- provider-native sprint, cycle, or iteration when available
- Caveman Lite or Full
- title, Context, Scope, and Definition of Done

#### Auto Mode

Gather conversation context, repository evidence, current remotes, saved routing, and provider metadata read-only. Decide every supported parameter without asking when evidence is sufficient.

- Prefer saved routing when it is available, capable, and consistent with the ticket context.
- Otherwise choose the most relevant capable provider and tool. Do not change memory yet.
- Choose a project or repository from the current work context and accessible provider data.
- Choose only fields required by the provider plus the explicitly required project, template, assignment, and native iteration decisions.
- Choose Caveman Lite by default. Use Full only when compression will not reduce clarity.
- Record each value with a concise evidence-based rationale. Mark genuine uncertainty; never invent facts.

If one or more parameters cannot be resolved credibly, pair only on the first unresolved parameter through one select question. After the user answers, resume automatic resolution for the remaining parameters. Repeat only for parameters still blocked; never restart the full interview or switch the entire run to paired mode.

If the ticket problem itself lacks credible context, pair only on the missing title, Context, Scope, or Definition of Done inputs, then resume auto mode.

If the automatically chosen interface lacks a required capability, choose another capable interface when evidence clearly supports it. Otherwise pair only on the tool choice with `Switch once`, `Switch and remember`, or `Cancel`. Never mix interfaces silently.

#### Paired Mode

Ask for each parameter one at a time with 2–3 concrete choices derived from current evidence.

- Ask Jira, Linear, or Git Host. Put saved routing first when available.
- For Git Host, ask GitHub, Codeberg/Forgejo, GitLab, or Gitea, then ask for `owner/repository`.
- Ask for an available MCP or CLI when saved routing cannot be reused.
- Ask Jira and Linear users to select a project. Include `No project` only when the provider permits it.
- Ask only provider-required create fields.
- Ask for template, assignment, native iteration when available, Caveman intensity, and ticket content.

After the user explicitly confirms a new paired-mode route, remember it immediately:

```bash
bd remember '{"version":1,"provider":"...","host":"...","interface":"...","tool":"..."}' --key ticket-create-routing
```

A paired-mode one-time switch must not update memory.

### 4. Discover Provider Metadata

Use the chosen tool read-only before drafting.

- Jira and Linear: discover accessible projects and required create metadata.
- Git Host: use the selected repository as the project boundary.
- Resolve the authenticated user's identity.
- Discover accessible ticket templates.
- Discover active provider-native sprints, cycles, or iterations. Do not reinterpret milestones, due dates, or arbitrary scheduling fields as sprints.

When more than three choices exist in paired mode, rank by current repository, active state, and recent relevance. Offer the top choices; the tab/free-form path accepts an exact identifier or more information.

### 5. Select or Decide Template and Placement

If an existing template requests a solution, approach, implementation, technical design, or prescribed changes:

- Auto mode decides between sanitizing it and using the default, then explains the decision.
- Paired mode asks `Sanitize existing template (Recommended)` or `Use default template`.

Never retain solution-oriented content.

Auto mode decides assignment and native iteration from ownership and scheduling evidence. Paired mode asks. If no native iteration is accessible, record no iteration and do not reinterpret another scheduling field.

### 6. Gather Problem Content

Create a title, Context, Scope, and Definition of Done from supplied context and verified evidence. In paired mode, offer 2–3 concise candidates for each missing value. In auto mode, ask only when a value cannot be inferred credibly.

Use the default body when no existing template is selected:

```markdown
## Context

{Problem, impact, and relevant evidence.}

## Scope

{Affected behavior and boundaries. No implementation tasks.}

## Definition of Done

- [ ] {Observable outcome.}
```

For an existing template, preserve useful problem-oriented sections and required provider fields. Keep Context, Scope, and Definition of Done unless equivalent headings capture the same information.

### 7. Draft with Caveman

Auto mode decides Lite or Full and records why. Paired mode asks:

- `Caveman Lite (Recommended)` — concise professional sentences.
- `Caveman Full` — terse fragments where meaning stays clear.

Invoke the installed Caveman skill at the selected intensity before writing the title or body. Keep provider identifiers, error text, and technical symbols exact.

The title and body must describe the problem, impact, boundaries, evidence, and observable outcomes. They must not contain:

- proposed solutions or recommendations
- implementation steps or task breakdowns
- technical designs or architecture choices
- prescribed tools, APIs, data models, or code changes

Scan for headings or language such as `Solution`, `Approach`, `Implementation`, `Technical Design`, `we should`, or `change X to Y`. Rewrite violations before previewing. Definition of Done states observable results, never the means used to reach them.

### 8. Share Decisions and Create

Show one complete preview containing:

- mode
- provider, host, and selected tool
- project or repository
- required provider fields
- assignee
- sprint, cycle, or iteration
- selected template and any sanitization
- Caveman intensity
- title and complete body

In auto mode, add a concise rationale beside every decided parameter and identify any parameter supplied through focused pairing.

Then ask:

- `Create ticket (Recommended)` only when the preview is complete and accurate
- `Pair on changes`
- `Cancel`

`Pair on changes` asks which decision to revise and pairs only on that decision. Auto mode recomputes dependent automatic decisions; paired mode revisits only dependent paired fields. Both return to the complete preview. `Cancel` performs no external write and does not change auto-mode routing memory.

On `Create ticket`, use only the confirmed values and chosen interface. If creation fails, do not update auto-mode routing memory. Show the exact error and ask `Retry`, `Switch tool`, or `Cancel`; a switch requires a new preview and confirmation.

After successful auto-mode creation, persist changed routing with `bd remember ... --key ticket-create-routing`. If memory persistence fails, report it without editing or recreating the ticket.

Return the created ticket key or number, URL, provider, and project or repository. Do not perform follow-up edits.
