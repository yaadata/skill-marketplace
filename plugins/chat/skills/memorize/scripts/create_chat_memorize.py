#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a numbered chat memorize artifact under ./.local/docs/chat-memorize."
    )
    parser.add_argument("--base-dir", required=True, help="Workspace root for the artifact")
    parser.add_argument("--title", required=True, help="Frontmatter title")
    parser.add_argument(
        "--description", required=True, help="Short description for frontmatter and slug"
    )
    parser.add_argument(
        "--scope",
        required=True,
        choices=("global", "project-specific", "mixed"),
        help="Scope of the approved learning batch",
    )
    parser.add_argument(
        "--source-range", required=True, help="Conversation range considered for memorization"
    )
    parser.add_argument(
        "--tags",
        required=True,
        help="Comma-separated single-word tags for frontmatter",
    )
    parser.add_argument(
        "--body-file", required=True, help="Path to a Markdown file containing the artifact body"
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("description must contain at least one alphanumeric character")
    return slug


def parse_tags(value: str) -> list[str]:
    tags = [tag.strip().lower() for tag in value.split(",") if tag.strip()]
    if not tags:
        raise ValueError("at least one tag is required")
    invalid = [tag for tag in tags if not re.fullmatch(r"[a-z0-9-]+", tag)]
    if invalid:
        raise ValueError(
            f"tags must be single words using letters, digits, or hyphens: {', '.join(invalid)}"
        )
    return tags


def next_number(memorize_dir: Path) -> int:
    highest = 0
    for path in memorize_dir.glob("*.md"):
        match = re.match(r"(\d{5})_", path.name)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def build_frontmatter(
    number: str,
    title: str,
    scope: str,
    source_range: str,
    tags: list[str],
    description: str,
) -> str:
    tag_lines = "\n".join(f"  - {tag}" for tag in tags)
    return (
        "---\n"
        f"number: {number}\n"
        f"title: {title}\n"
        f"date: {date.today().isoformat()}\n"
        f"scope: {scope}\n"
        f"source_range: {source_range}\n"
        "tags:\n"
        f"{tag_lines}\n"
        f"description: {description}\n"
        "---\n"
    )


def main() -> int:
    args = parse_args()

    base_dir = Path(args.base_dir).expanduser().resolve()
    memorize_dir = base_dir / ".local" / "docs" / "chat-memorize"
    memorize_dir.mkdir(parents=True, exist_ok=True)

    body_path = Path(args.body_file).expanduser().resolve()
    body = body_path.read_text(encoding="utf-8").strip()
    if not body:
        raise ValueError("body file must contain Markdown content")

    title = args.title.strip()
    description = args.description.strip()
    source_range = args.source_range.strip()
    if not title:
        raise ValueError("title is required")
    if not description:
        raise ValueError("description is required")
    if not source_range:
        raise ValueError("source-range is required")

    tags = parse_tags(args.tags)
    number = f"{next_number(memorize_dir):05d}"
    artifact_path = memorize_dir / f"{number}_{slugify(description)}.md"

    frontmatter = build_frontmatter(
        number,
        title,
        args.scope,
        source_range,
        tags,
        description,
    )
    artifact_path.write_text(f"{frontmatter}\n{body}\n", encoding="utf-8")
    print(artifact_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
