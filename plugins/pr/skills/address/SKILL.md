---
name: address
description: Address GitHub or Codeberg pull request review feedback from a review file or PR URL. Use when the user invokes $pr:address or asks Codex to ingest PR feedback, validate review comments, discuss feedback, and apply accepted fixes as atomic staged changes.
---

# PR Address

Use this skill to ingest pull request feedback, validate whether each point is
still valid, discuss each issue with the user, and apply accepted fixes as
separate atomic staged changes. The user creates commits between fixes.

## Inputs

Accept either:

- A file path. Treat it as the full review artifact or human-readable review
  notes.
- A GitHub or Codeberg PR URL. If the user provides only a PR number, resolve it
  only when the current checkout unambiguously matches the provider and
  repository.

## Checkout And Safety

Before applying fixes:

1. Inspect the current worktree.
2. If there are existing staged or unstaged changes, stop and ask how to proceed.
3. Prefer working on the actual PR head.

Provider checkout rules:

- GitHub: use `gh pr checkout <url>`.
- Codeberg: `fj pr checkout` exists and may be used when appropriate. If that
  is unavailable or unsuitable, use the existing Codeberg fetch fallback pattern:
  `git fetch origin refs/pull/{PR_NUMBER}/head:pr/{PR_NUMBER}` then
  `git checkout pr/{PR_NUMBER}`.

Do not create commits. The user will commit each staged fix and then give the
go-ahead to continue.

## Feedback Ingestion

For a file input:

- Read the whole file as the source review.
- Extract findings, nits, questions, requested changes, and unresolved concerns.
- Preserve file paths, line references, reviewer names, and quoted rationale when
  available.

For a PR URL:

1. Ask exactly one interactive select question when available:
   - Scan all non-author comments.
   - Use a specific review.
2. For all-comments mode, identify the PR author from provider metadata and
   exclude comments authored by that user.
3. For specific-review mode, fetch provider metadata first and build reviewer
   choices from non-author users with reviews, latest reviews, comments, or
   line-level review comments.
4. Ask for the reviewer with interactive select choices when available. Each
   choice should show the reviewer username plus useful context such as review
   state, review count, comment count, or latest review time when available.
5. If the reviewer list is too large, ask one interactive narrowing or paging
   question at a time instead of asking the user to type a username. Examples:
   show the first page of reviewers, show the next page, filter to reviewers
   with unresolved or requested-change feedback, or filter by review state.
6. Use free-form reviewer username input only when no reviewer choices can be
   discovered from provider metadata or comments.

Provider comment rules:

- GitHub:
  - Use `gh pr view --json author,comments,reviews,latestReviews,files,headRefName,baseRefName,url,title`.
  - Use `gh pr view --comments` for human-readable context when useful.
  - Use `gh api` when needed to retrieve review comments, threads, or line-level
    comments not exposed by `gh pr view`.
- Codeberg:
  - Use `fj --host codeberg.org pr -R origin view {PR_NUMBER}` for metadata.
  - Use `fj --host codeberg.org pr -R origin view {PR_NUMBER} comments`.
  - Use `fj --host codeberg.org pr -R origin view {PR_NUMBER} comment {IDX}`
    when a specific comment needs expansion.

## Artifact

Write the addressing record to:

`.local/docs/pr-address/{provider}_{pr-number}_{branch-name-dashes-as-underscores}/ADDRESS.md`

For file inputs where provider, PR number, or branch cannot be determined, use:

`.local/docs/pr-address/file_unknown_{branch-name-dashes-as-underscores}/ADDRESS.md`

Never overwrite an existing address directory. If the target exists, append a
short numeric suffix.

Normalize the artifact directory name as:

- Provider is exactly `github`, `codeberg`, or `file`.
- PR number is decimal digits, or `unknown` for file inputs without PR metadata.
- Branch name replaces `/` with `_`.
- Branch name replaces `-` with `_`.
- Any other path-unsafe branch-name characters are replaced with `_`.

Use this structure:

```markdown
## Context

## Feedback Source

## Normalized Feedback

## Validity Checks

## Discussion Log

## Applied Fixes

## Staged Changes

## Validation Results

## Remaining Work
```

## Normalize And Validate Feedback

Normalize raw comments into feedback issues. Group multiple comments that point
to the same underlying issue.

For each issue, validate before asking the user to act on it:

- Check whether the referenced code still exists.
- Check whether the concern is technically accurate.
- Check whether existing code or tests already address it.
- Check whether the feedback is stale because the PR has changed.
- Mark the issue as `valid`, `invalid/stale`, `partially valid`, or `uncertain`.

Codex must not blindly accept review feedback. Discuss invalid, stale, partially
valid, and uncertain feedback too, with evidence, unless the user chooses to skip
it.

## Discussion Workflow

Discuss one normalized feedback issue at a time. For each issue:

1. Show the relevant code and line references.
2. Summarize the reviewer point.
3. Show Codex's validity assessment and evidence.
4. Recommend one action.
5. Ask the user whether to accept, reject, defer, or revise the handling.

Every user decision must be an interactive decision when Codex has an
interactive select action available. Ask exactly one question at a time. Put the
recommended option first and label it recommended. Use free-form input only when
the user must provide information that cannot be expressed as a small set of
meaningful choices. Reviewer username selection must use provider-derived
interactive choices when available; free-form reviewer input is only a fallback
when no choices can be discovered.

Record each decision in `ADDRESS.md` before moving to implementation.

## Applying Fixes

For each accepted issue requiring a code change:

1. Ask interactively whether to implement that issue's fix directly or invoke
   `$code:pair` for guided no-edit implementation.
2. If `$code:pair` is selected, invoke it only for the accepted code fix and
   validation guidance. Do not include `ADDRESS.md` updates in the pairing
   task.
3. Apply only that issue's fix.
4. Run the narrowest relevant validation for that fix, plus static checks when
   clearly applicable.
5. Stage only the files or hunks for that atomic fix.
6. Update `ADDRESS.md` with the changed files, validation result, and staged
   summary.
7. Stop and wait for the user to create the commit and explicitly give the
   go-ahead before moving to the next feedback item.

Do not combine unrelated accepted feedback into one staged change. If two
comments describe the same underlying issue, handle them as one issue and one
atomic staged change.

Do not create commits in Codex. The user commits between fixes.

## Final Output

When the workflow is complete or paused, return:

- The `ADDRESS.md` path.
- A concise git status summary.
- Validation results for the latest staged fix or completed run.
