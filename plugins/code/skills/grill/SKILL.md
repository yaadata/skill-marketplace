---
name: grill
description: Quiz engineer on code impl details, behavior, tests, risks, tradeoffs. Use when user invokes $code:grill or asks Codex to grill them on recent code edits, current diff, file, symbol, or pasted code.
---

# Code Grill

## Purpose

Grill user on code. Goal: prove user understands impl, not hear nice summary.

Mix high-level + low-level q. Exhaustive, not repetitive. If user already proved concept, compress next q for same concept or skip.

## Inputs

Accept:

- current local diff
- pasted code
- local file path
- local `path:line` or `path:start-end`
- symbol, fn, method, component, module

Default src: current local diff.

If target broad, narrow by changed files, explicit refs, related callers/tests/config.

## No-Edit Mode

While grilling:

- no file edits
- no patches
- no formatters
- no mutating cmds
- no claim code changed

Read/search/inspect OK. Tests/builds OK only if needed to inspect truth, not to implement.

## Source Rules

- Inspect code before grilling. No guess.
- Prefer local truth: source, callers, tests, docs, config, git diff.
- If claim not proven by inspected repo ctx, say uncertain. Inspect more or ask user for narrower target.
- For behavior/tradeoff claims, cite concrete refs like `path/to/file.go:L10-L28` when possible.

## Coverage Map

Cover all buckets unless target truly lacks bucket:

1. why change exist
2. user-visible or caller-visible behavior
3. control flow
4. data flow / state shape
5. invariants / assumptions
6. edge cases / failure modes
7. tests / validation / missing coverage
8. tradeoffs / alternatives rejected
9. regression risk / follow-on impact

Do not ask same q twice with new wording. If user already showed bucket understanding, move on.

## Interaction Rules

- Every question must use interactive select when Codex has interactive select available.
- Ask exactly 1 question at time.
- Never recommend an answer choice.
- Never label any option recommended, preferred, best guess, likely, or similar answer-bias wording.
- Present choices neutrally. Goal is quiz user, not steer user to right answer.
- Do not ask plain free-form q if same decision can fit in 2-4 meaningful choices.
- Use free-form only when user must explain reasoning, teach back understanding, or give detail that cannot fit small meaningful choice set.
- If native multi-select not available, emulate multi-select with repeated 1-question interactive select steps.
- If question starts as free-form, first decide whether it can be rewritten as interactive select. If yes, rewrite it.

## Quiz Flow

1. Identify target.
2. Inspect surrounding code.
3. Build bucket checklist.
4. Start high-level. Then drill low-level.
5. Ask 1 q at time.
6. Use interactive select for every question when available, including scope checks, bucket checks, confidence checks, tradeoff checks, and follow-up drill choices.
7. Use free-form only for teach-back, explanation, or evidence the user must supply in their own words and cannot express as small choice set.
8. After each answer, decide:
   - bucket covered
   - bucket partial
   - bucket wrong
   - deeper drill needed
9. Continue until all relevant buckets covered or user exits.

Adaptive rule:

- start broad
- drill where user weak
- compress where user strong
- never skip low-level details if they matter to correctness

## Answer Handling

If answer correct:

- ack brief
- move on
- do not dump full answer key unless user asks

If answer partial or wrong:

- name exact gap
- cite local code refs
- explain expected answer + tradeoff/risk
- ask 1 teach-back follow-up before moving on
- if follow-up can be meaningfully expressed as choices, use interactive select, not free-form

If answer plausible but unverified:

- say what repo proves
- say what still inferred
- inspect more before scoring if needed

## Teach-Back Loop

Correction not enough. Make user say it back.

Flow:

1. correct gap
2. cite evidence
3. ask narrow follow-up q on same concept
4. use interactive select for follow-up unless user must explain concept in their own words
5. if user now gets it, mark bucket covered
6. if still weak, simplify once more or say more inspection needed

## Output

Default: interactive chat quiz only.

Optional: if user explicitly wants recap, write study note:

`./.local/docs/code-grill/{branch-with-slashes-replaced}/{NNNN}_GRILL.md`

Use concise recap:

- target grilled
- buckets covered
- misses corrected
- key tradeoffs
- cited evidence refs
- remaining weak spots / open q

Do not write artifact unless user says yes.
