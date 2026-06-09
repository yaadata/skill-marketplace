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
13. After the accepted artifact is written, create the Beads task handoff.
14. After the Beads task handoff is created, perform the recorded implementation handoff.
15. Every final proposed plan must include an `Implementation Handoff` section so a clear-context `SessionStart` hook can recover selected implementation skills.

## Artifact Timing

Do not write a plan artifact while the plan is still being developed.

Artifact generation happens only after:

1. the final plan has been presented to the user, and
2. the user explicitly accepts it.

If the active collaboration mode prevents file writes, present the final plan and defer artifact creation until the user exits that mode or asks to implement the accepted plan. After leaving that mode and writing the deferred artifact, perform the recorded implementation handoff.

## Implementation Handoff

Hard sequence after acceptance:

`write artifact -> update accepted path -> create Beads tasks -> invoke selected skills`

Do not ask another implementation handoff question after the artifact is accepted. Do not invoke an implementation skill that was not selected in the accepted plan.

Invocation map:

- `$code:tdd` + `$code:pair` selected: invoke both with accepted plan path and recorded decisions.
- only `$code:tdd` selected: invoke `$code:tdd` with accepted plan path and recorded TDD decisions.
- only `$code:pair` selected: invoke `$code:pair` with accepted plan path and recorded pairing decision.
- none selected: stop after artifact + Beads tasks.

Every final proposed plan must contain this exact hook-readable block:

```markdown
## Implementation Handoff
- Selected skills: $code:tdd, $code:pair
- TDD: all slices | selected slices | not selected
- TDD slices: concise list, or none
- Pairing: selected | not selected
- Accepted plan path: deferred until acceptance
```

- List only selected implementation skills in `Selected skills`; use `none` when no implementation skill was selected.
- Keep every value concise and single-line.
- Use `Accepted plan path: deferred until acceptance` before artifact write; replace it with the actual artifact path after write.
- Clear-context recovery may use this block to reapply selected skills.

## Beads Task Handoff

Create Beads tasks only after accepted artifact exists and its handoff block has actual path.

Preflight:

- Verify `bd` exists and repo has initialized Beads DB.
- If unavailable, stop before implementation handoff. Report accepted plan path, selected skills, and exact Beads failure.
- Never create tasks for draft plans.

Task graph:

- Create skill gate first, always, even when selected skills = `none`.
- Gate labels: `code-plan,implementation-handoff,skill-gate`.
- Gate metadata: `accepted_plan_path`, `selected_skills`, `tdd_mode`, `tdd_slices`, `pairing`, `task_order:0`.
- Create one implementation task per plan slice.
- Slice labels: `code-plan,implementation-handoff,implementation-slice`.
- Slice metadata: `accepted_plan_path`, `selected_skills`, `task_order` using 1-based slice order.
- Slice description: goal, files/symbols/subsystems, notes, validation, skill mode, report-back instructions.
- Add `--skills` only when selected skills is not `none`.
- Every slice task depends on gate: `bd dep add <slice-task-id> <skill-gate-task-id>`.

Command shapes:

```bash
bd create "Set implementation skills for <accepted plan filename>" \
  --type task \
  --labels code-plan,implementation-handoff,skill-gate \
  --due +2w \
  --skills '$code:tdd,$code:pair' \
  --metadata '{"accepted_plan_path":"...","selected_skills":"$code:tdd, $code:pair","tdd_mode":"all slices","tdd_slices":"...","pairing":"selected","task_order":0}' \
  --description "Records the implementation skills for the accepted plan before any implementation task starts." \
  --silent

bd create "<slice title>" \
  --type task \
  --labels code-plan,implementation-handoff,implementation-slice \
  --due +2w \
  --skills '$code:tdd,$code:pair' \
  --metadata '{"accepted_plan_path":"...","selected_skills":"$code:tdd, $code:pair","task_order":1}' \
  --description "<slice description>" \
  --silent

bd dep add <slice-task-id> <skill-gate-task-id>
```

After tasks exist, summarize only accepted plan path, skill gate task ID, slice task IDs in order, and selected skills.

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
