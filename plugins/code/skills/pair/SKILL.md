---
name: pair
description: Pair-program interactively without editing files. Use when the user invokes $code:pair or asks Codex to pair on a plan, prompt, ticket, issue, pull request, Jira, Linear, GitHub, Codeberg, or implementation task while the human writes the code.
---

# Code Pair

Guide a human through implementation without editing files. Pairing is advisory, interactive, and bidirectional. Track remaining pairing chunks in Beads when available.

## Inputs

The user may provide:

- a plan path or pasted plan
- a general implementation description
- a Beads task
- a Jira or Linear ticket
- a GitHub or Codeberg issue or pull request

If no input is provided, ask interactively for a plan, prompt, or ticket to pair on.

For external tickets, use available provider CLIs or tools when available. If context cannot be fetched or is ambiguous, ask the user to paste details.

## No-Edit Mode

While pairing:

- Do not edit files.
- Do not apply patches.
- Do not run mutating repo commands.
- Do not run tests by default.
- Do not claim to have changed code.
- Read, search, inspect git state, and inspect local code as needed.
- Beads task tracking is the only allowed mutation, and only after user confirmation.

If the user chooses to bail for a chunk, no-edit mode is suspended for that chunk only. After that chunk is implemented, resume pairing on the next chunk unless the user explicitly exits pairing.

## Beads Tracking

At the start of `$code:pair`:

1. Check whether Beads is available. If no database is initialized, tell the user to run `bd init --stealth --non-interactive` or set `BEADS_DIR`, then ask whether to continue untracked.
2. Search for open or in-progress tasks labeled `code-pair` that match the current repo/session/input metadata when available.
3. If matching tasks exist, use them as the remaining pairing checklist instead of creating duplicates.
4. If no matching tasks exist, build the ordered pairing checklist in-chat first, then ask once before creating all chunk tasks.

For each created chunk task:

- Use `bd create`.
- Set `--type task`, `--label code-pair`, and `--due +2w`.
- Set metadata for `code_pair=true`, current repo/cwd, session when known, input reference when known, and chunk order.
- Put goal, files or symbols, implementation notes, validation, and report-back instructions in the description.
- Do not use `--ephemeral`; pairing chunks must remain durable and exported.

During pairing:

- Ask before `bd update <id> --claim` when starting a chunk.
- Ask before `bd close <id> --reason "Pairing chunk completed"` when the user reports a chunk complete.
- Keep the in-chat checklist aligned with confirmed Beads status.

## Workflow

1. Load the input context.
2. Inspect relevant local code when needed to avoid guessing.
3. Confirm the request is specific enough to pair on. If it is vague, ask one interactive question at a time until the implementation path is clear.
4. Recover or create the Beads-tracked pairing checklist.
5. For each remaining chunk, ask interactively whether the user wants to:
   - show the task or instructions
   - show code
   - bail and let Codex implement this chunk only
6. If the user asks to show code, ask interactively whether they want:
   - minimal pasteable snippets
   - a unified diff sketch
7. Pause after each chunk so the user can implement and report back.
8. When the user reports back, inspect the code or diff they actually wrote when available.
9. If the user implemented a different approach, verify whether it satisfies the chunk goal and preserves the broader plan.
10. If the approach is valid, treat the user's implementation as the new source of truth, update the remaining checklist, and continue from that path.
11. If the approach is risky or incomplete, explain the concrete issue and ask one interactive decision about whether to adjust, revert, or continue with a modified plan.
12. Adapt the next chunk based on feedback, errors, test failures, changed constraints, or better implementation ideas.
13. When the checklist is complete, provide final validation guidance and explicitly exit pairing mode.

## Chunk Guidance

For task or instruction view, include:

- goal
- files or symbols to inspect/change
- implementation notes
- validation for the chunk
- what the user should report back

For code view:

- keep snippets small and pasteable unless the user chose a diff sketch
- name the file, function, class, test, or command involved
- match local conventions
- state assumptions when exact code depends on unseen context
- include test or validation snippets when they reduce risk

## Human Redirection

Pairing is not a one-way script.

If the user disagrees with the suggested path or has a better implementation approach:

1. Restate the user's approach to confirm understanding.
2. Compare it briefly against the current checklist.
3. Revise the remaining chunks to follow the user's approach when it is coherent and safe.
4. Ask one focused question only if the new path changes scope, risk, API shape, or validation.

Do not keep pushing the original checklist after the user has redirected the implementation.

## Bail Behavior

Bailing applies only to the current chunk or diff being paired on.

When the user bails:

1. Exit advisory mode for the current chunk.
2. Implement that chunk using normal Codex behavior.
3. Validate as appropriate for that chunk.
4. Return to the pairing checklist for the next chunk.

Do not treat a chunk-level bail as an exit from the whole pairing session.

## Boundaries

- Stay in pairing mode until the checklist is complete or the user explicitly exits.
- Avoid broad rewrites when the request calls for incremental work.
- Surface missing context early.
- If the user gets stuck, narrow the chunk or propose a debugging step before moving on.
