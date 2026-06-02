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
5. Independently ask whether implementation handoff should include `$code:pair`:
   - include `$code:pair`
   - do not include `$code:pair`
6. When TDD is selected for all or part of the implementation, include:
   - behavior slices that should use red-green loops
   - likely test entry points when discoverable from local code
   - behavior slices explicitly marked no-test with substitute validation
7. Record the independent `$code:pair` decision in the final plan.
8. For large, risky, cross-cutting, or multi-subsystem changes, ask whether to include atomic commits.
9. When atomic commits are included, describe each commit with:
   - single purpose
   - expected files or areas
   - validation for that commit
   - review boundary
10. Present the completed plan in chat.
11. Ask the user to accept the plan.
12. Only after acceptance, write the artifact.
13. After the accepted artifact is written, perform the recorded implementation handoff.
14. Every final proposed plan must include an `Implementation Handoff` section so a clear-context `SessionStart` hook can recover selected implementation skills.

## Artifact Timing

Do not write a plan artifact while the plan is still being developed.

Artifact generation happens only after:

1. the final plan has been presented to the user, and
2. the user explicitly accepts it.

If the active collaboration mode prevents file writes, present the final plan and defer artifact creation until the user exits that mode or asks to implement the accepted plan. After leaving that mode and writing the deferred artifact, perform the recorded implementation handoff.

## Implementation Handoff

After writing an accepted plan artifact, do not ask another implementation handoff question. Use the recorded independent `$code:tdd` and `$code:pair` decisions from the accepted plan:

- When both were selected, invoke `$code:pair + $code:tdd` with the accepted plan path and recorded decisions.
- When only TDD was selected, invoke `$code:tdd` with the accepted plan path and recorded TDD decisions.
- When only pairing was selected, invoke `$code:pair` with the accepted plan path and recorded pairing decision.
- When neither was selected, stop after writing the plan artifact.

Do not invoke an implementation skill that was not selected in the accepted plan.

The final proposed plan must contain this exact heading and fields:

```markdown
## Implementation Handoff
- Selected skills: $code:tdd, $code:pair
- TDD: all slices | selected slices | not selected
- TDD slices: concise list, or none
- Pairing: selected | not selected
- Accepted plan path: deferred until acceptance
```

Rules:

- List only selected implementation skills in `Selected skills`; use `none` when no implementation skill was selected.
- Keep values concise and single-line so hook recovery can inject them without expanding context.
- Before the artifact is accepted and written, set `Accepted plan path` to `deferred until acceptance`.
- After writing the artifact, use the actual artifact path in the handoff.
- If the user clears context and asks to implement, the clear-context recovery hook may use this section to reapply selected implementation skills without asking again.

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
- Implementation handoff
- TDD decision and behavior slices, when applicable
- Atomic commits, when applicable
- Test and validation plan
- Assumptions and defaults chosen

Prefer concrete decisions over open-ended brainstorming. Record unresolved questions only if they intentionally remain out of scope.
