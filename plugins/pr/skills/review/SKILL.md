---
name: review
description: Review GitHub or Codeberg pull requests with optional diagram, security, nitpicky, and interactive hunk-discussion modules. Use when the user invokes $pr:review or asks for a modular PR review, PR security review, PR diagram, nitpicky PR review, or PR line-by-line discussion.
---

# PR Review

Use this skill for checkout-based pull request review. The workflow gathers PR
context, asks which review modules to run, writes a durable local artifact, and
optionally walks the diff interactively with the user.

## Inputs

Accept a GitHub or Codeberg PR URL. If the user provides only a PR number,
resolve it only when the current checkout unambiguously matches the provider and
repository.

Do not publish PR comments or push code. Prepare comment-ready snippets in the
artifact instead.

## Checkout

Before checkout:

1. Inspect the current worktree.
2. If checkout would disturb local changes, stop and ask how to
   proceed.
3. Gather the current remote URL and verify it matches the PR repository.

Provider rules:

- GitHub: use `gh pr checkout <url>`.
- Codeberg: use `fj` from forgejo-cli to view PR details and check out the PR:
  1. Parse `owner/repo` and PR number from the URL.
  2. Verify `origin` points to the same Codeberg repository.
  3. View the PR with `fj --host codeberg.org pr -R origin view {PR_NUMBER}`.
  4. Check out the PR with `fj --host codeberg.org pr checkout {PR_NUMBER}`.
     If a deterministic local branch name is needed, use
     `fj --host codeberg.org pr checkout --branch-name pr/{PR_NUMBER} {PR_NUMBER}`.
  5. Gather details with:
     - `fj --host codeberg.org pr -R origin view {PR_NUMBER} body`
     - `fj --host codeberg.org pr -R origin view {PR_NUMBER} files`
     - `fj --host codeberg.org pr -R origin view {PR_NUMBER} diff`
     - `fj --host codeberg.org pr -R origin view {PR_NUMBER} comments`
     - `fj --host codeberg.org pr -R origin view {PR_NUMBER} commits`
  6. If `fj` is missing, stop and say forgejo-cli is required for Codeberg PR
     checkout and viewing. If checkout fails, report the failed command and
     remote URL.

After checkout, gather PR metadata, base/head, changed files, diff stats, the
full diff, and relevant surrounding code.

## Artifact

Write the review to:

`.local/docs/pr-review/{provider}_{pr-number}_{branch-name-dashes-as-underscores}/REVIEW.md`

Never overwrite an existing review directory. If the target exists, append a
short numeric suffix.

Normalize the artifact directory name as:

- Provider is exactly `github` or `codeberg`.
- PR number is decimal digits.
- Branch name replaces `/` with `_`.
- Branch name replaces `-` with `_`.
- Any other path-unsafe branch-name characters are replaced with `_`.

Use this structure:

```markdown
## Context

Pull-Request: {url}
Provider: {github|codeberg}
Title: {title if available}
Author: {author if available}
Base: {base}
Head: {head}

## Module Selection

## Change Diagram

## Subagent Summaries

### Diagram

### Security

### Nits

## Interactive Review Notes

## Findings

## Test Coverage

## Comment Snippets

## Verdict
```

For skipped modules, keep the heading and write `Skipped: {reason}`.

## Module Selection

Not every PR needs every review module. Ask which modules to run after checkout
and initial context gathering. Native checkbox-style multi-select may not be
available, so emulate multi-select with one interactive select question at a
time.

Ask exactly one question at a time. If Codex has an interactive select action
available, use it. Put the recommended choice first and label it recommended.

Ask these module questions:

1. Run diagram/change-map pass?
2. Run security audit pass?
3. Run nitpicky review pass?
4. Run interactive hunk discussion?

Recommend `yes` for:

- Diagram: non-trivial control flow, architecture, state, or data-flow changes.
- Security: auth, permissions, parsing, command execution, secrets, PII,
  dependency, network, sandbox, filesystem, or user-data changes.
- Nits: most hand-written code changes, unless generated, vendored, or purely
  mechanical.
- Hunk discussion: risky, broad, unfamiliar, security-sensitive, or
  behavior-changing PRs.

Record each selected or skipped module in `## Module Selection` before spawning
any subagents.

## Optional Subagents

Spawn only the selected subagents. Give each selected subagent the PR URL,
base/head, changed-file list, diff summary, and enough focused code context to
answer its prompt. Tell subagents to avoid edits.

Available roles:

1. Diagram agent
   - Reasoning effort: low.
   - Output: concise change map and Mermaid diagrams.
   - Choose diagram type by change shape: sequence for runtime flow, flowchart
     for control/data paths, class/module diagram for structural changes.
   - If a diagram is not useful, say so and provide a compact change map.

2. Security agent
   - Reasoning effort: medium.
   - Output: security risks, missing safeguards, and security-positive notes.
   - Check authn/authz, injection, command execution, secrets, PII/data exposure,
     unsafe file/network IO, dependency and supply-chain changes, sandbox or
     permission changes, privilege boundaries, logging, and error disclosure.
   - Mark each concern as blocking, non-blocking, or informational.

3. Nitpicky agent
   - Reasoning effort: low.
   - Output: small correctness, readability, naming, test, docs, maintainability,
     style, and edge-case comments.
   - Prefer actionable nits. Do not inflate nits into blockers unless they hide a
     real bug or review risk.

Consolidate selected subagent outputs into the artifact before any interactive
hunk discussion.

## Interactive Hunk Discussion

Run this only when selected in module selection.

After selected subagent summaries are written, ask which hunk discussion mode to
use. Ask this as a single interactive select question when available:

- Hunk-by-hunk: best for risky, unfamiliar, security-sensitive, broad, or
  behavior-changing PRs.
- Findings-only: best when subagents found concrete risks but most hunks are
  straightforward.
- Summary-only: skips hunk questioning and moves to the final verdict.

Questioning rules:

- Ask exactly one question at a time.
- Use interactive select for discrete choices when available.
- Put the recommended choice first and label it recommended.
- Use free-form questions only when the answer cannot be expressed as a small
  set of meaningful choices.
- After each answer, record the answer in the artifact before asking the next
  question.

Treat "chunk" and "hunk" as equivalent for this workflow.

For each reviewed hunk or chunk:

1. Present the git diff reference range under review, using the diff hunk
   metadata such as `path/to/file.go @@ -12,7 +12,9 @@`.
2. Include a human-readable location like `path/to/file.go:L12-L20` when it can
   be derived from the diff range.
3. Include the hunk header or nearest symbol/context marker when available.
4. Describe the surrounding code context to the best of Codex's knowledge before
   asking the user a question.
5. Provide a concise summary of the changed block.
6. Ask the user interactively whether they have any questions about this hunk or
   chunk before moving on.
7. Ask one targeted question about intent, risk, tests, or alternatives.
8. Incorporate relevant subagent findings for that hunk.
9. Record the user's answers, unresolved questions, and any new findings in the
   artifact.

In hunk-by-hunk mode, do not skip a changed hunk unless it is generated,
vendored, lockfile-only, or the user explicitly asks to skip it. For huge PRs,
batch adjacent trivial hunks in the same file, but preserve line references in
the notes.

## Final Verdict

After the selected modules complete, update the artifact with:

- Blocking findings first, with file/line references.
- Non-blocking findings and nits separately.
- Test coverage summary, including missing tests.
- Comment-ready snippets for the PR.
- A verdict: approve, approve with nits, request changes, or needs follow-up.

Return only the artifact path and a one-line status summary.
