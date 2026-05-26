---
name: plan
description: Create an exhaustive implementation plan for code changes. Use when the user invokes $code:plan or asks Codex to plan an implementation, design a change, or produce a reusable implementation plan artifact.
---

# Code Plan

Create a decision-complete implementation plan. This is a planning skill, not an implementation skill.

## Core Behavior

Act like `grill-me`:

- Explore the repo before asking questions.
- If a question can be answered from code, configs, docs, tests, or current git state, inspect those sources instead of asking.
- Ask one decision at a time.
- Use interactive selection for every decision when available.
- Provide a recommended answer with each decision.
- Continue until goal, success criteria, audience, scope, constraints, approach, interfaces, edge cases, tests, rollout, and implementation sequencing are settled.
- Do not produce the final plan until the design tree is resolved.

## Workflow

1. Confirm the requested plan is for implementation work. If the user is only asking for explanation or comments, use `$code:describe` or `$code:comment` instead.
2. Gather local context:
   - current branch and git status
   - relevant files, symbols, tests, docs, configuration, and existing patterns
   - prior plans only when directly relevant
3. Interview the user interactively:
   - goal and non-goals
   - success criteria
   - target audience and maintainers
   - constraints and compatibility requirements
   - implementation approach
   - public interfaces, schemas, commands, configuration, or user-visible behavior
   - failure modes, edge cases, migration needs, and rollout concerns
   - test and validation strategy
4. During test and validation strategy, always ask whether implementation should use `$code:tdd`:
   - use `$code:tdd` for implementation
   - do not use TDD
   - use TDD only for selected behavior slices
5. When TDD is selected for all or part of the implementation, include:
   - behavior slices that should use red-green loops
   - likely test entry points when discoverable from local code
   - behavior slices explicitly marked no-test with substitute validation
6. For large, risky, cross-cutting, or multi-subsystem changes, ask whether to include atomic commits.
7. When atomic commits are included, describe each commit with:
   - single purpose
   - expected files or areas
   - validation for that commit
   - review boundary
8. Present the completed plan in chat.
9. Ask the user to accept the plan.
10. Only after acceptance, write the artifact.
11. After the accepted artifact is written, ask interactively which implementation handoff to use.

## Artifact Timing

Do not write a plan artifact while the plan is still being developed.

Artifact generation happens only after:

1. the final plan has been presented to the user, and
2. the user explicitly accepts it.

If the active collaboration mode prevents file writes, present the final plan and defer artifact creation until the user exits that mode or asks to implement the accepted plan. After leaving that mode and writing the deferred artifact, always ask which implementation handoff to use.

## Implementation Handoff

After writing an accepted plan artifact, ask one interactive decision:

- Invoke `$code:tdd` for direct red-green implementation
- Invoke `$code:pair` for guided no-edit implementation
- Invoke `$code:pair + $code:tdd` for guided pairing with TDD discipline
- Stop after writing the plan artifact

Use interactive selection when available.

When TDD was selected in the accepted plan and the user has not indicated they want Codex to implement directly, recommend `$code:pair + $code:tdd`. When TDD was selected and the user wants Codex to implement directly, recommend `$code:tdd`. When TDD was not selected, recommend `$code:pair`.

Do not invoke any implementation skill silently. The handoff is optional, but the question is required after artifact creation, including when artifact creation was deferred until after Plan Mode. If the user selects a TDD-aware handoff, invoke `$code:tdd` with the accepted plan path and the recorded TDD decisions.

## Artifact Path

Write accepted artifacts to:

`./.local/docs/code-plan/{branch-with-slashes-replaced}/{NNNN}_PLAN.md`

Determine `NNNN` by scanning that branch directory for existing files matching `*_PLAN.md` and incrementing the highest 4-digit prefix. Start at `0001`.

## Plan Format

The final plan should be concise but implementation-ready. Include:

- Summary
- Key changes
- Public interfaces or behavior changes
- Implementation sequence
- TDD decision and behavior slices, when applicable
- Atomic commits, when applicable
- Test and validation plan
- Assumptions and defaults chosen

Prefer concrete decisions over open-ended brainstorming. Record unresolved questions only if they intentionally remain out of scope.
