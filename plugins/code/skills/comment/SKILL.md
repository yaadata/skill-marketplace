---
name: comment
description: Draft and optionally insert a useful comment for a selected, pasted, or referenced code block. Use when the user invokes $code:comment or asks Codex to comment a specific block of code.
---

# Code Comment

Draft a comment for a particular code block. The comment should explain non-obvious intent, invariants, tradeoffs, domain context, or caveats. Do not restate obvious control flow.

## Inputs

The target may be:

- selected or pasted code
- a local file path
- a local `path:line` or `path:start-end` reference
- a named block, function, method, component, module, or symbol

If the target is local, inspect the surrounding code and nearby style before drafting. Match the language, comment syntax, and existing comment style.

## Required Questions

Ask questions one at a time. Use `request_user_input` when available. If unavailable, ask concise plain-text questions.

1. Ask the desired comment detail level:
   - Short
   - Balanced
   - Detailed
2. Ask whether the user has additional context that should shape the comment. This may be free-form input.

## Draft Workflow

1. Identify the exact block being commented.
2. Inspect local context when available: enclosing symbol, adjacent comments, tests, callers, and domain names.
3. Draft the comment only after the required questions are answered.
4. Show the proposed comment and where it would go.
5. Ask interactively whether to insert it.
6. If approved, edit the file with the smallest possible change.

## Comment Quality

- Explain why the code exists, not merely what each line does.
- Preserve useful domain language from the codebase.
- Keep comments close to the relevant block.
- Avoid stale predictions, TODOs, or claims that are not supported by local context or user-provided context.
- If the system behavior is uncertain, ask for more context instead of encoding a guess in the comment.
