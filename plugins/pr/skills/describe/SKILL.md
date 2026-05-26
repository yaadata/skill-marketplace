---
name: describe
description: Draft and optionally publish GitHub or Codeberg pull request bodies. Use when the user invokes $pr:describe or asks Codex to describe PR changes, write a PR body, update a PR description, or publish a PR body using gh or fj.
---

# PR Describe

Use this skill to describe pull request changes and optionally update the live PR
body. The workflow gathers PR context, asks the user what to include, writes a
durable local body artifact, and only publishes after explicit confirmation.

## Inputs

Accept a GitHub or Codeberg PR URL. If the user provides only a PR number,
resolve it only when the current checkout unambiguously matches the provider and
repository.

Do not update the PR title. Do not publish until the generated body artifact has
been written and the user confirms publishing.

## Gather Context

Before gathering PR data:

1. Inspect the current worktree.
2. If checkout would disturb local changes, stop and ask how to proceed.
3. Gather the current remote URL and verify it matches the PR repository when a
   checkout or provider command depends on the local repository.
4. Gather PR metadata, current body, base/head, changed files, diff stats, the
   full diff, relevant surrounding code, and any repository PR template.

Provider rules:

- GitHub:
  - Use `gh pr view` for PR metadata and current body.
  - Use `gh pr diff` for the diff.
  - Publish only after confirmation with
    `gh pr edit <pr> --body-file {artifact_body_path}`.
- Codeberg:
  - Use `fj` from forgejo-cli to view PR details.
  - Parse `owner/repo` and PR number from the URL.
  - Verify `origin` points to the same Codeberg repository.
  - Check out the PR locally with `fj --host codeberg.org pr checkout {PR_NUMBER}`
    before analyzing local code context. If a deterministic local branch name is
    needed, use
    `fj --host codeberg.org pr checkout --branch-name pr/{PR_NUMBER} {PR_NUMBER}`.
  - Gather details with:
    - `fj --host codeberg.org pr -R origin view {PR_NUMBER}`
    - `fj --host codeberg.org pr -R origin view {PR_NUMBER} body`
    - `fj --host codeberg.org pr -R origin view {PR_NUMBER} files`
    - `fj --host codeberg.org pr -R origin view {PR_NUMBER} diff`
    - `fj --host codeberg.org pr -R origin view {PR_NUMBER} commits`
  - Publish only after confirmation with `fj pr edit {PR_NUMBER} body {NEW_BODY}`.
  - If `fj` is missing, stop and say forgejo-cli is required for Codeberg PR
    body updates.

For Codeberg publishing, pass the complete generated body as the `NEW_BODY`
argument. If the body is too large or quoting would be unsafe, stop and report
that `fj pr edit body` only exposes a direct body argument or editor flow.

## PR Template Handling

Look for repository PR templates before drafting. Check common locations such as
`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`,
`.github/PULL_REQUEST_TEMPLATE/*.md`, `docs/pull_request_template.md`, and
`PULL_REQUEST_TEMPLATE.md`.

If a template exists and suggests a body structure, ask the user what to do
before drafting. Ask exactly one interactive select question when available:

- Use PR template structure (recommended when the template is specific).
- Use default `$pr:describe` structure.
- Blend template with `$pr:describe` sections.

If the selected structure conflicts with the default `Context`, `Details`, and
optional `Validations` sections, follow the user's selected structure and keep
the generated content faithful to the intent of the selected verbosity,
diagram, and validation choices.

## Interactive Choices

Ask exactly one question at a time. If Codex has an interactive select action
available, use it. Put the recommended choice first and label it recommended.

Ask these questions before drafting:

1. Include a diagram?
2. Include a `### Validations` section?
3. If validations are included, what validation categories should be mentioned?
4. What exact validations were done?
5. What verbosity should the PR body use?

Recommendations:

- Diagram: recommend yes for non-trivial control flow, architecture, state,
  data-flow, lifecycle, permission, or integration changes; otherwise recommend
  no.
- Validations section: recommend include.
- Validation categories: ask with one select at a time because native
  checkbox-style multi-select may not be available. Useful categories are tests,
  lint/static checks, manual checks, build/package checks, docs-only review, or
  not run.
- Exact validations: ask for free-form details after categories are selected,
  such as exact commands, manual scenarios, or `not run`.
- Verbosity:
  - `Rounded` (recommended): detailed but high level enough for an engineer to
    understand and navigate the change.
  - `Extreme Details`: explains the code nuances and any new topics or
    technologies introduced by the change.
  - `Lazy`: high-level description only because the code is self-explanatory.

Record the user's choices in the artifact notes before publishing.

## Diagram

If the user includes a diagram, spawn a focused low-effort diagram subagent.
Give it the PR URL, base/head, changed-file list, diff summary, and relevant
code context. Tell it not to edit files.

The diagram subagent should return concise Mermaid. Choose diagram type by
change shape: sequence for runtime flow, flowchart for control/data paths, or
class/module diagram for structural changes. If a diagram is not useful after
inspection, say so and ask the user whether to omit it.

Embed included diagrams in a toggleable block:

````markdown
<details>
<summary>Diagram</summary>

```mermaid
{diagram}
```

</details>
````

## Artifact

Write the generated body to:

`.local/docs/pr-describe/{provider}_{pr-number}_{branch-name-dashes-as-underscores}/BODY.md`

Never overwrite an existing describe directory. If the target exists, append a
short numeric suffix.

Normalize the artifact directory name as:

- Provider is exactly `github` or `codeberg`.
- PR number is decimal digits.
- Branch name replaces `/` with `_`.
- Branch name replaces `-` with `_`.
- Any other path-unsafe branch-name characters are replaced with `_`.

Also write a short notes file beside the body:

`.local/docs/pr-describe/{provider}_{pr-number}_{branch-name-dashes-as-underscores}/NOTES.md`

The notes file records the PR URL, provider, base/head, selected body structure,
selected verbosity, diagram choice, validation choice, publish confirmation, and
publish command.

## Body Format

Use this default PR body structure unless the user selected a PR-template-based
structure:

```markdown
## Context

{summary of why this change exists and what reviewer context matters}

### Details

{description of what changed, shaped by the selected verbosity}

{optional toggleable diagram}

### Validations

{selected validation details}
```

If the user chooses not to include validations, omit `### Validations` entirely.

Replace the entire live PR body when publishing. Do not attempt to preserve
custom sections from the existing body unless the user explicitly asks for that
in the current run.

## Publishing

After writing `BODY.md`, ask the user whether to publish it. Use interactive
select when available. Recommend publishing only when the artifact accurately
reflects the PR and validations.

If the user declines, leave the artifact in place and do not call `gh pr edit`
or `fj pr edit`.

If publishing succeeds, update `NOTES.md` with the publish status. Return only
the artifact path and a one-line status summary.
