---
name: document
description: Write documentation artifacts that describe selected, pasted, referenced, or repository code. Use when the user invokes $code:document or asks Codex to create a code document, technical note, code walkthrough, subsystem summary, or code-oriented documentation artifact.
---

# Code Document

Create a documentation artifact that describes code. This skill writes an artifact after an interactive interview; it does not assume a fixed document format.

## Inputs

The user may provide:

- selected or pasted code
- a file, file range, symbol, function, class, module, package, or subsystem
- a branch, pull request, issue, task, plan, or discussion that identifies code to document
- an existing documentation file to update
- a general code area or topic

If the input is incomplete, ask one interactive question at a time until the document target is clear.

## Context Gathering

Explore before asking:

- Inspect local files, symbols, tests, docs, configs, git state, and existing nearby documentation when relevant.
- Use available issue, pull request, task, chat, or document connectors when the user points at external context.
- If a question can be answered from discovered context, answer it from that context instead of asking.
- Show concise relevant source snippets only when they materially ground a question or proposed detail.

Do not run mutating commands until the artifact destination and create/update behavior are clear.

## Interactive Interview

Act like `grill-me`:

- Ask one decision at a time.
- Use interactive selection for decisions when available.
- Provide a recommended answer with each decision.
- Continue until the document is decision-complete.
- Do not write the artifact until audience, purpose, output type, format guidance, included details, exclusions, destination, and acceptance criteria are settled.

Always ask for:

- output type:
  - Markdown
  - plain text
  - Other, with details
- free-form format instructions
- audience and purpose
- whether source references should be included

After inspecting the target code and document purpose, generate a dynamic menu of document-specific details to include. Include a free-form option for additional details. Do not use a fixed global section list; the right details differ from document to document.

Clarify exclusions when they materially affect the document, such as:

- code areas to omit
- implementation details that are too low-level
- historical context that should not be included
- security, performance, or operational details that should be included only at a high level

## Create Or Update

Create a new artifact by default.

Update an existing documentation file only when the user explicitly provides a target file. Before updating, inspect the target file and preserve its style, structure, terminology, and level of detail unless the user asks for a rewrite.

## Artifact Path

Write new artifacts to:

`./.local/docs/code-document/{concise-topic-slug}.{ext}`

Choose `{ext}` from the accepted output type:

- Markdown: `md`
- plain text: `txt`
- Other: use the extension implied by the user's details, or ask if unclear

Create `{concise-topic-slug}` as a lowercase slug from the document topic:

- keep it concise
- replace spaces and punctuation with hyphens
- collapse repeated hyphens
- trim leading and trailing hyphens

Artifacts are not branch-scoped.

## Document Format

Follow the user's free-form format instructions. If the user does not provide enough format guidance, ask follow-up questions until the expected shape is clear enough to write.

Use the dynamically selected details to determine the document's sections, ordering, density, examples, and references. Prefer concrete code-grounded claims over generic explanation.

When source references are requested, keep them specific with file paths, symbols, line references, issue links, plan paths, or command names when known.

## Completion

After writing the artifact, report only the file path and a one-line description.
