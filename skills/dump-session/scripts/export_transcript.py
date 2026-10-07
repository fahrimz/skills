#!/usr/bin/env python3
"""Export user/assistant turns from a local Codex or Claude JSONL session."""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from typing import Any, Iterable

def text_content(value: Any) -> str:
    if isinstance(value, str): return value
    if isinstance(value, list):
        return "".join(part if isinstance(part, str) else str(part.get("text", part.get("output_text", ""))) for part in value if isinstance(part, str) or (isinstance(part, dict) and part.get("type") in ("text", "output_text")))
    return ""

def detect_provider(path: Path) -> str:
    """Detect a copied transcript from its records, then fall back to its path."""
    if "/.codex/" in str(path):
        return "codex"
    if "/.claude/" in str(path):
        return "claude"
    try:
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                item = json.loads(line)
                if "payload" in item and item.get("payload", {}).get("type"):
                    return "codex"
                if item.get("type") in ("user", "assistant", "attachment"):
                    return "claude"
    except (OSError, json.JSONDecodeError):
        pass
    raise SystemExit("Cannot detect transcript provider; pass a Codex or Claude JSONL file.")

def record_cwd(path: Path, provider: str) -> str | None:
    try:
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                item = json.loads(line)
                value = item.get("payload", {}).get("cwd") if provider == "codex" else item.get("cwd")
                if value: return value
    except (OSError, json.JSONDecodeError): return None
    return None

def choose_session(provider: str, session: str, cwd: str | None) -> tuple[str, Path]:
    home, roots, candidates = Path.home(), [], []
    if provider in ("auto", "codex"): roots.append(("codex", home / ".codex" / "sessions"))
    if provider in ("auto", "claude"): roots.append(("claude", home / ".claude" / "projects"))
    for detected, root in roots:
        for path in root.glob("**/*.jsonl"):
            if cwd and record_cwd(path, detected) != os.path.abspath(cwd): continue
            if session != "latest" and path.stem != session: continue
            candidates.append((path.stat().st_mtime, detected, path))
    if not candidates: raise SystemExit("No matching session found. Pass --input PATH.")
    _, detected, path = max(candidates)
    return detected, path

def turns(path: Path, provider: str) -> Iterable[tuple[str, str]]:
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            try: item = json.loads(line)
            except json.JSONDecodeError: continue
            if provider == "codex":
                payload = item.get("payload", {})
                if payload.get("type") != "message": continue
                role, content = payload.get("role"), text_content(payload.get("content"))
            else:
                role = item.get("type")
                if role not in ("user", "assistant"): continue
                content = text_content(item.get("message", {}).get("content"))
            if role in ("user", "assistant") and content.strip(): yield role, content.strip()

def markdown(items: Iterable[tuple[str, str]]) -> str:
    labels, output, previous = {"user": "User", "assistant": "Assistant"}, [], None
    for role, content in items:
        if (role, content) == previous: continue
        output.append(f"> **{labels[role]}:** {content.replace(chr(10), chr(10) + '> ')}")
        previous = (role, content)
    return "\n\n".join(output) + ("\n" if output else "")

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("auto", "codex", "claude"), default="auto")
    parser.add_argument("--session", default="latest")
    parser.add_argument("--cwd")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    provider, path = (detect_provider(args.input), args.input) if args.input else choose_session(args.provider, args.session, args.cwd)
    data = list(turns(path, provider))
    rendered = markdown(data) if args.format == "markdown" else json.dumps([dict(role=r, content=c) for r, c in data], indent=2) + "\n"
    if args.output: args.output.write_text(rendered, encoding="utf-8")
    else: print(rendered, end="")

if __name__ == "__main__": main()
