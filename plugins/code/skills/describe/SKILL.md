---
name: describe
description: Teach an engineer how selected, pasted, or referenced code works. Use when the user invokes $code:describe or asks Codex to explain a code block, file range, or how code connects to the rest of the system.
---

# Code Describe

Teach the user about the target code. Assume the engineer may be unfamiliar with this domain or this part of the codebase.

## Inputs

The target may be:

- selected or pasted code
- a local file path
- a local `path:line` or `path:start-end` reference
- a named block, function, method, component, module, or symbol

If a file reference or symbol is available, inspect the surrounding code before explaining. Prefer local source, tests, callers, docs, and configuration over inference.

## Interactive Scope

Before explaining, ask one interactive decision:

- Learn this block
- Learn connections
- Learn both

Use `request_user_input` when available. If unavailable, ask a concise plain-text question. Do not ask more than one question at a time.

## Teaching Workflow

1. Identify the exact code under discussion.
2. If the target is local, gather nearby context: enclosing symbol, imports, callers, tests, and related configuration when useful.
3. Explain at the selected scope:
   - **Block**: what the code does, key branches, data shape, side effects, assumptions, and why it may be written this way.
   - **Connections**: how it is called, what calls it, what it depends on, what state or data flows through it, and what breaks if it changes.
   - **Both**: start with the local block, then connect it outward.
4. Use a teacher tone: define domain terms, name invariants, and make implicit assumptions explicit.
5. Prefer concrete references like `path/to/file.ext:L12-L24` when discussing local code.

## Deep Or Uncertain Domains

For deep topics such as networking, infra, auth, storage, concurrency, build systems, deployment, distributed systems, or generated code:

- Do not guess how the broader system works.
- Separate confirmed facts from inferences.
- If more context is needed, tell the user what is missing and offer to inspect specific sources next.
- Pair with the user to find relevant information when it is not discoverable locally.

## Output

Default to an interactive chat explanation. Only write a Markdown artifact if the user explicitly asks for one.
