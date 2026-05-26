---
name: task
description: Continue or start a Beads task from a clean branch. Use when the user invokes $code:task or asks Codex to work on, resume, continue, claim, plan, or implement a bd/Beads task.
---

# Code Task

Work from a Beads task handoff. Load the task, verify branch/worktree context, ensure an accepted `$code:plan` exists, then implement from that plan with atomic approval gates.

## Inputs

The user may provide:

- a Beads ID such as `bd-123`
- the current checked-out branch and no ID
- a request to continue the current Beads task

If an explicit ID is provided, load it with `bd show {id} --long`. Otherwise use `bd show --current --long`. If the current task is missing or ambiguous, ask interactively for the task ID.

## Core Workflow

1. Load task context:
   - Beads task details
   - parent epic and dependencies when relevant
   - design, notes, metadata, acceptance criteria, and comments
2. Show the task summary and ask interactively before claiming with `bd update {id} --claim`.
3. Inspect git context:
   - current branch
   - worktree status
   - expected branch and base from the task handoff, when present
4. Stop and ask interactively before continuing if:
   - the current branch does not match the task handoff
   - the expected base is unclear or mismatched
   - the worktree has staged or unstaged changes
   - multiple plausible tasks or plans are found
5. Find an accepted phase plan.
6. If no accepted plan exists, run `$code:plan` for this Beads task.
7. Implement from the accepted plan.
8. After validation passes, summarize work and ask interactively before closing the Beads task.

## Plan Lookup

Look for an accepted plan in this order:

1. Beads task design, notes, metadata, spec ID, or external references containing a plan path.
2. `.local/docs/code-plan/**/{NNNN}_PLAN.md` files that mention the Beads ID.
3. `.local/docs/code-plan/**/{NNNN}_PLAN.md` files that match the task title or branch name.

Do not silently choose between multiple plausible plans. Show the candidates and ask interactively.

If `$code:plan` creates a new accepted plan artifact, ask interactively before recording the plan path back to Beads as a note or metadata.

## Implementation

Follow the accepted plan. If the plan includes atomic commits:

- implement one commit-sized change at a time
- stage only that change
- summarize the staged diff
- ask interactively before committing or moving to the next atomic change

If the plan does not include atomic commits but the change is large, ask whether to split the work into atomic commits before editing.

## Beads Updates

All Beads mutations require an interactive decision:

- claiming the task with `bd update {id} --claim`
- recording the accepted plan path
- adding notes about progress or validation
- closing the task with `bd close {id}`

Prefer concise Beads notes that include paths, commits, validation commands, and remaining risks.

## Safety Rules

- Do not infer a task silently if multiple candidates are plausible.
- Do not continue on branch mismatch, unexpected base, or dirty worktree without an interactive decision.
- Do not skip `$code:plan` unless an accepted plan is found.
- Do not close Beads tasks automatically.
- Do not create or switch git branches unless the user explicitly asks.
