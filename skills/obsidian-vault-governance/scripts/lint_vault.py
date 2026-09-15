#!/usr/bin/env python3
"""Mechanical health checks for an Obsidian vault.

No third-party dependencies. Semantic checks (contradictions/staleness) remain human/agent review.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]+)?\]\]")
REQUIRED = ("type", "created", "updated", "status")


def markdown_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if ".git" not in p.parts)


def frontmatter(text: str) -> tuple[bool, set[str]]:
    if not text.startswith("---\n"):
        return False, set()
    end = text.find("\n---", 4)
    if end < 0:
        return False, set()
    keys = set()
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z_][\w-]*):", line)
        if match:
            keys.add(match.group(1))
    return True, keys


def target_key(raw: str) -> str:
    target = raw.strip().rstrip("\\")
    return Path(target).name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--strict", action="store_true", help="return nonzero when mechanical findings exist")
    args = parser.parse_args()
    root = args.root.resolve()
    files = markdown_files(root)
    all_files = sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)
    by_name: dict[str, list[Path]] = defaultdict(list)
    by_path: dict[str, Path] = {}
    for path in all_files:
        by_name[path.stem].append(path)
        rel = path.relative_to(root).as_posix()
        by_path[rel] = path
        if path.suffix:
            by_path[rel[: -len(path.suffix)]] = path

    inbound: dict[Path, set[Path]] = defaultdict(set)
    broken: list[tuple[Path, str]] = []
    for source in files:
        text = source.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            raw = match.group(1).strip()
            normalized = raw.strip().rstrip("\\").lstrip("/")
            candidates = []
            if "/" in normalized:
                exact = by_path.get(normalized) or by_path.get(normalized + ".md")
                if exact:
                    candidates = [exact]
            if not candidates:
                candidates = by_name.get(target_key(normalized), [])
            if not candidates:
                broken.append((source.relative_to(root), raw))
            else:
                for dest in candidates:
                    if dest != source:
                        inbound[dest].add(source)

    missing_fm: list[Path] = []
    for path in files:
        if path.relative_to(root).parts[0] in {"sources"} or path.name == "CLAUDE.md":
            continue
        valid, keys = frontmatter(path.read_text(encoding="utf-8"))
        if not valid or any(key not in keys for key in REQUIRED):
            missing_fm.append(path.relative_to(root))

    # Characters that corrupt a [[wikilink]] target when they appear in a filename:
    # '#' is parsed as the heading-anchor separator ([[Page#Heading]]), '|' as the alias
    # separator ([[Page|alias]]), and '[' / ']' terminate the link early. A page named with
    # any of these can never be linked to safely — the link silently resolves to the wrong
    # (usually nonexistent) target instead of erroring, e.g. `KYC Batch Resolver (#177)...`
    # broke both the hub and log.md links that pointed at it (2026-09-15).
    UNSAFE_NAME_CHARS = set("#|[]")
    unsafe_names = [
        p.relative_to(root)
        for p in files
        if UNSAFE_NAME_CHARS & set(p.stem)
    ]

    orphans = [p.relative_to(root) for p in files if not inbound[p] and p.name not in {"index.md", "log.md", "CLAUDE.md"}]
    project_hub_gaps: list[Path] = []
    for path in files:
        rel = path.relative_to(root)
        if len(rel.parts) != 2 or rel.parts[0] != "projects" or rel.name.startswith("00 - "):
            continue
        hub_candidates = list((root / rel.parent).glob("00 - *.md"))
        if hub_candidates and path.stem not in hub_candidates[0].read_text(encoding="utf-8"):
            project_hub_gaps.append(rel)

    print(f"Vault: {root}")
    print(f"Markdown files: {len(files)}")
    print(f"Broken links: {len(broken)}")
    for source, target in broken:
        print(f"  BROKEN {source}: [[{target}]]")
    print(f"Orphan pages: {len(orphans)}")
    for path in orphans:
        print(f"  ORPHAN {path}")
    print(f"Project hub gaps: {len(project_hub_gaps)}")
    for path in project_hub_gaps:
        print(f"  HUB-GAP {path}")
    print(f"Pages missing required frontmatter: {len(missing_fm)}")
    for path in missing_fm:
        print(f"  FRONTMATTER {path}")
    print(f"Unsafe filenames (contain {sorted(UNSAFE_NAME_CHARS)}): {len(unsafe_names)}")
    for path in unsafe_names:
        print(f"  UNSAFE-NAME {path}")
    return 1 if args.strict and (broken or missing_fm or unsafe_names) else 0


if __name__ == "__main__":
    raise SystemExit(main())
