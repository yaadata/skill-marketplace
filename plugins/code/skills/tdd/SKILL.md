---
name: tdd
description: Implement code changes with test-driven development. Use when the user invokes $code:tdd or asks Codex to implement through red-green TDD loops, choose test entry points, verify failing tests, then implement behavior until tests pass.
---

# Code TDD

## Purpose

Implement changes through test-driven development. Work one behavior at a time: choose the test entry point, create a failing test, inspect that it fails for the expected reason, implement only enough code to pass, inspect that it is green, then ask before staging.

This skill can be used with `$code:pair`. When both are active, `$code:pair` controls the human-guided chunk interaction and `$code:tdd` controls the implementation discipline for each chunk.

## Inputs

The user may provide:

- an implementation prompt
- an accepted `$code:plan`
- a Beads task
- a Jira, Linear, GitHub, or Codeberg issue
- a focused code change request

If the input is broad, decompose it into behavior slices before editing.

## Core Rules

- Use grill-me style questions before choosing test strategy.
- Explore the repo before asking questions that code can answer.
- Ask one decision at a time.
- Use interactive selection for every user decision when available.
- Tests are not all-or-nothing. Ask whether a test is needed per behavior slice.
- If a behavior does not warrant a test, record the explicit no-test decision and substitute validation before implementing that slice.
- Prefer focused tests and focused validation over broad test suites.
- Do not continue past dirty worktree, ambiguous test entry point, or unexpected test failure without an interactive decision.
- User controls commits. Ask before staging each completed green loop.

## Workflow

1. Load the request context and inspect relevant code, tests, docs, and current git state.
2. Break the change into behavior slices.
3. For each behavior slice:
   - describe the behavior and likely files involved
   - ask whether that specific behavior needs a test
   - recommend the best test entry point based on local patterns
   - ask the user to confirm the test entry point
4. If the behavior needs a test:
   - for new functions or public entry points, create a minimal empty stub first so the test can compile when possible
   - add one focused failing test for one behavior
   - run the focused test
   - inspect and summarize the red result
   - require the failure to match the expected behavior assertion
   - if the red result fails for the wrong reason, fix the test or stub before implementing behavior
   - implement only enough code to make the focused test pass
   - rerun focused validation until green
   - inspect and summarize the green result
5. If the behavior does not need a test:
   - record why the test is cumbersome or not useful
   - choose substitute validation interactively
   - implement the slice
   - run the substitute validation when applicable
6. After each slice, summarize the diff and ask before staging.
7. Move to the next behavior only after the user approves continuing.

## Red Phase Requirements

- A red test must be run before implementation for every tested behavior.
- Red because a symbol is missing is allowed only when a compile-capable stub is impractical.
- Stub-first is preferred for new functions and public entry points.
- A red run that fails for unrelated setup, syntax, fixture, or environment reasons is not a valid red phase.
- Fix invalid red phases before implementing production behavior.

## Green Phase Requirements

- Green must be observed with the focused command that failed red.
- If implementation changes shared behavior, run the smallest relevant broader validation after the focused green test.
- Do not claim green unless the command output was inspected.

## Pairing With `$code:pair`

When invoked with `$code:pair`:

- Keep `$code:pair` no-edit behavior unless the user chooses to bail for the current chunk.
- Use `$code:tdd` to define the red-green sequence for the paired chunk.
- If the user writes the code, inspect their test and implementation before deciding whether the TDD loop is complete.
- If Codex implements a bailed chunk, follow the normal `$code:tdd` red-green workflow for that chunk.
- Return to the pairing checklist after the TDD chunk is green or explicitly marked no-test with substitute validation.

## Staging

After each completed behavior slice:

1. Summarize the changed files and validation.
2. Show whether the slice was tested or explicitly marked no-test.
3. Ask interactively before staging.
4. Stage only the completed slice if the user approves.

Do not commit unless the user explicitly asks.
