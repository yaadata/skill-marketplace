---
name: grill
description: Quiz engineer on PR intent, changed behavior, validations, risks, reviewer questions, diff details. Use when user invokes $pr:grill or asks Codex to grill them on pull request understanding.
---

# PR Grill

## Purpose

Grill user on PR until they understand ins, outs, reviewer risk, diff details.

This skill may be wrong if evidence weak. So every assistant answer, correction, eval must cite evidence. No evidence, no confident claim.

## Inputs

Accept:

- GitHub or Codeberg PR URL
- PR number if current checkout makes repo/provider unambiguous
- existing `BODY.md`
- existing `NOTES.md`
- current checked-out PR ctx

## Source Of Truth

Prefer existing `pr:describe` materials first.

If user gives `BODY.md` or `NOTES.md`, load them plus live diff/local code as needed.

If no `pr:describe` artifact exists:

1. gather PR ctx using `pr:describe` flow
2. write or refresh local `pr:describe` materials first
3. then grill on artifact + diff + surrounding code

Do not treat PR body alone as truth if diff disagrees. Resolve against diff + local code.

## Evidence Rules

Every assistant-side answer/correction/eval must cite evidence from one or more:

- PR metadata
- `BODY.md`
- `NOTES.md`
- diff hunk refs
- local code refs

Allowed citation style:

- `plugins/foo/bar.go:L12-L44`
- `path/to/file @@ -10,7 +10,12 @@`
- `BODY.md` section name
- `gh pr view` / `fj ... view` fact summary

If evidence missing or conflicting:

- say uncertain
- inspect more
- do not guess

## Coverage Map

Cover all relevant buckets:

1. why PR exists
2. reviewer ctx / problem statement
3. changed behavior
4. key files / hunks
5. validations done
6. missing tests / checks
7. tradeoffs / alternatives
8. rollout risk / regression risk
9. likely reviewer objections or follow-up q

Exhaustive, not repetitive. If user proved bucket already, compress next q for that bucket.

## Interaction Rules

- Every question must use interactive select when Codex has interactive select available.
- Ask exactly 1 question at time.
- Put recommended option first. Label recommended option recommended.
- Do not ask plain free-form q if same decision can fit in 2-4 meaningful choices.
- Use free-form only when user must explain reasoning, teach back understanding, or provide evidence/detail that cannot fit small meaningful choice set.
- If native multi-select not available, emulate multi-select with repeated 1-question interactive select steps.
- If question starts as free-form, first decide whether it can be rewritten as interactive select. If yes, rewrite it.

## Quiz Flow

1. Load PR ctx.
2. Load or create `pr:describe` materials.
3. Inspect diff + surrounding code.
4. Build bucket checklist.
5. Ask 1 q at time.
6. Use interactive select for every question when available, including scope checks, hunk selection, validation checks, risk checks, reviewer-objection checks, and follow-up drill choices.
7. Use free-form only for teach-back, explanation, or evidence the user must supply in their own words and cannot express as small choice set.
8. Start high-level, then drill hunks/files/validations/risk.
9. After each answer, score bucket: covered, partial, wrong, deeper drill needed.
10. Continue until all relevant buckets covered or user exits.

For hunk-level drill:

- cite file + diff ref first
- summarize changed block
- ask intent/risk/test/tradeoff q
- use interactive select whenever hunk question can fit meaningful choices

## Answer Handling

If answer correct:

- ack brief
- cite evidence
- move on

If answer partial or wrong:

- cite evidence
- name exact gap
- explain expected answer
- ask 1 teach-back follow-up before moving on
- if follow-up can be meaningfully expressed as choices, use interactive select, not free-form

If repo or PR materials do not settle answer:

- say uncertain
- inspect more ctx
- ask narrower q if needed

## Teach-Back Loop

After correction:

1. cite evidence
2. restate expected answer
3. ask follow-up q on same concept
4. use interactive select for follow-up unless user must explain concept in their own words
5. mark bucket covered only after user shows understanding

## Output

Default: interactive chat quiz only.

Optional: if user explicitly wants recap, write:

`.local/docs/pr-grill/{provider}_{pr-number}_{branch-name-dashes-as-underscores}/GRILL.md`

If target dir exists, append short numeric suffix like nearby PR skills.

Recap shape:

- PR ctx
- buckets covered
- misses corrected
- evidence used
- reviewer-risk themes
- remaining weak spots / open q

Do not write artifact unless user says yes.
