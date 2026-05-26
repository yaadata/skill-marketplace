---
name: architect
description: Architect large code changes into phased implementation work. Use when the user invokes $code:architect or asks Codex to design a multi-phase architecture, generate architecture diagrams, create Beads tasks, or decompose broad work into branch-based implementation phases.
---

# Code Architect

Architect broad implementation work into reviewed phases, diagrams, and Beads tasks. This is an architecture and decomposition skill, not an implementation skill.

## Core Behavior

Act like `grill-me`:

- Explore the repo before asking questions.
- If a question can be answered from code, configs, docs, tests, current git state, or Beads state, inspect those sources instead of asking.
- Ask one decision at a time.
- Use interactive selection for every decision when available.
- Provide a recommended answer with each decision.
- Continue until goals, constraints, architecture options, phase boundaries, dependencies, validation, rollout, and task handoff are resolved.
- Do not create artifacts or Beads tasks until the architecture package is accepted.

## Workflow

1. Confirm the request is architecture-level work. If it is a single implementation task, use `$code:plan`.
2. Gather local context:
   - current branch and git status
   - relevant source, tests, docs, config, and existing patterns
   - current Beads context when useful
3. Interview the user interactively:
   - goal and non-goals
   - constraints and compatibility requirements
   - target maintainers and review expectations
   - architecture alternatives and tradeoffs
   - selected architecture
   - phase boundaries and dependency order
   - validation and rollout risks
   - Beads task shape and acceptance criteria
4. Always present multiple architecture options with tradeoffs before selecting the final phased architecture.
5. Generate a Mermaid diagram in Markdown for the selected architecture.
6. Present the completed architecture package in chat and ask the user to accept it.
7. Only after acceptance:
   - write the architecture artifact
   - dry-run Beads creation
   - create Beads tasks if the dry-run matches the accepted architecture

## Architecture Artifact

Write accepted artifacts to:

`./.local/docs/code-architect/{branch-with-slashes-replaced}/{NNNN}_ARCHITECTURE.md`

Determine `NNNN` by scanning that branch directory for existing files matching `*_ARCHITECTURE.md` and incrementing the highest 4-digit prefix. Start at `0001`.

Include:

- Summary
- Goals and non-goals
- Constraints
- Architecture options considered
- Selected architecture
- Mermaid diagram
- Phase breakdown
- Dependency order
- Branch plan
- Beads task plan
- Validation and rollout plan
- Assumptions and accepted defaults

## Branch Plan

Do not create git branches during architecture.

Each phase must specify:

- intended clean branch name
- base branch
- dependency on earlier phases, when applicable

Default base branch is the current branch at architecture time.

Default branch names use:

`architect/{short-topic}/phase-{n}-{slug}`

Allow the user to revise branch names during architecture review before acceptance.

## Beads Integration

After architecture acceptance, use `bd create --dry-run` before mutating Beads.

If the dry-run matches the accepted architecture, create:

- one parent epic
- one child task per phase
- dependencies between phase tasks where needed

Each phase task must include:

- phase goal
- intended clean branch name and base branch
- dependencies
- acceptance criteria
- validation expectations
- instruction to run `$code:plan` when the task is picked up

Prefer `bd create` fields such as `--type epic`, `--type task`, `--parent`, `--description`, `--design`, `--acceptance`, `--labels`, and `--deps` when they fit. Keep task content readable for humans.

## Handoff To Code Plan

Do not create detailed phase implementation plans during architecture unless the user explicitly asks.

The default handoff is:

1. A user or agent takes a phase task from Beads.
2. They start from the specified clean branch base.
3. They run `$code:plan` for that phase.
4. `$code:plan` creates the accepted phase implementation plan and atomic commit sequence.
