---
name: learn
description: Teach broad project topics with sourced code references, interactive understanding checks, optional diagrams, optional quizzes or tutorials, and optional persistent notes. Use when the user invokes $code:learn or asks Codex to learn, teach, explain, or explore a broad topic related to the current project.
---

# Code Learn

## Purpose

Teach a broad topic related to the current project. This is a bidirectional learning mode: Codex inspects the codebase, explains concepts with sources, checks the user's understanding, and adapts the explanation based on the user's answers.

Use `$code:describe` for a specific block, file range, or symbol. Use `$code:learn` for broad project topics that may span multiple files, modules, tests, docs, or external concepts.

## No-Edit Mode

While learning:

- Do not edit files.
- Do not apply patches.
- Do not run formatters.
- Do not run tests or builds.
- Do not run mutating commands.
- Do not claim to have changed code.
- Read files, search, inspect docs, and inspect git state as needed.

The only allowed file write is an optional persistent learning note after the user explicitly approves it.

## Source Requirements

- Every factual explanation must cite a concrete source.
- Prefer local code references for how the project works, using `path/to/file.ext:L12-L24`.
- If a concept is newly introduced to the user, or needs outside domain background, reference internet sources in addition to local code.
- For online references, use available approved browsing or documentation tools and cite the source.
- If a claim cannot be verified from code or cited sources, say that it is unverified and ask whether to inspect more context.
- Do not make probabilistic guesses.

## Workflow

1. Identify the broad topic from the user request.
2. If the topic is too broad or ambiguous, ask one interactive clarifying question at a time.
3. Inspect relevant project code, docs, tests, configuration, and callers using read/search/git inspection only.
4. Break the topic into major concepts.
5. For each concept:
   - show the relevant code snippets or references
   - explain what the code establishes
   - cite internet sources when the concept is newly introduced or needs domain background
   - ask interactively whether a diagram would help
   - ask interactively whether a quiz or tutorial would help
   - use teach-back to affirm the user's understanding
6. If the user misunderstands a concept, correct the specific gap with references and ask a follow-up teach-back.
7. Continue until the user confirms the topic is understood or exits learning mode.
8. Ask whether to store the session to a persistent Markdown note.
9. If approved, write the note using `scripts/create_code_learn_note.py`.

## Interaction Rules

- Ask questions one at a time.
- Prefer interactive select for every user decision when available.
- Use free-form input when the user needs to explain their understanding.
- Do not move to the next major concept until the user has had a chance to ask questions or teach it back.
- Keep explanations scoped to the current project topic unless the user asks to branch out.

## Diagrams, Quizzes, And Tutorials

- Ask per concept whether a diagram would help.
- If the user agrees, provide a concise Mermaid diagram or ASCII diagram in chat.
- Ask per concept whether a quiz or tutorial would help.
- If the user chooses a quiz, every question and answer key must cite local code or internet sources.
- If the user chooses a tutorial, make it stepwise and source-backed.

## Persistent Note

When the user approves storing the learning session, create:

```text
./.local/docs/code-learn/{NNNNN}_{short-description}.md
```

Use a concept-map style note:

```md
# {Title}

## Summary

What topic was learned and why it matters in this project.

## Concepts

Each major concept with code references and internet references when used.

## Diagrams

Diagrams the user requested.

## Quiz Or Tutorial

Material the user requested, with cited answers.

## Understanding Checkpoints

Teach-back answers, corrections, and remaining open questions.
```

Omit empty sections.

## Script

Use the bundled script to create the persistent note:

```bash
python3 /path/to/learn/scripts/create_code_learn_note.py \
  --base-dir "$PWD" \
  --title "Learning title" \
  --description "short description" \
  --topic "topic" \
  --tags "tag-one,tag-two" \
  --body-file /tmp/body.md
```

Pass `--base-dir "$PWD"` so the note is written under the current workspace.

