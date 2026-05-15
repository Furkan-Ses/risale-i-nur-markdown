#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_FILE_NAMES = {"Makefile"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".jsonl", ".txt", ".yml", ".yaml", ".toml"}
EXCLUDED_DIRS = {".git", ".obsidian", "graphify-out", "__pycache__"}

LOCAL_PATH_PATTERNS = (
    re.compile(r"/Users/"),
    re.compile(r"/home/"),
    re.compile(r"[A-Za-z]:\\\\Users\\\\"),
)
ATTRIBUTION_PATTERN = re.compile(r"Ali Tekdemir")


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.name in TEXT_FILE_NAMES or path.suffix in TEXT_SUFFIXES:
            files.append(path)
    return sorted(files)


def record_match(findings: list[str], path: Path, line_no: int, label: str, line: str) -> None:
    relative = path.relative_to(ROOT).as_posix()
    findings.append(f"{relative}:{line_no}: {label}: {line.strip()}")


def main() -> int:
    findings: list[str] = []

    for path in iter_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if path.suffix == ".py" and "re.compile(" in line:
                continue
            if any(pattern.search(line) for pattern in LOCAL_PATH_PATTERNS):
                record_match(findings, path, line_no, "local-path", line)
            if ATTRIBUTION_PATTERN.search(line) and path.relative_to(ROOT).as_posix() != "README.md":
                record_match(findings, path, line_no, "attribution-outside-readme", line)

    duplicate_dirs = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "ai" / "books").glob("* 2"))
    for duplicate_dir in duplicate_dirs:
        findings.append(f"{duplicate_dir}: duplicate-ai-directory")

    duplicate_artifacts = [
        ROOT / "ai 2",
        ROOT / "ai" / "books 2",
        ROOT / "ai" / "manifests 2",
        ROOT / "ai" / "passages 2",
        ROOT / "ai" / "README 2.md",
        ROOT / "ai" / "ANSWERING_POLICY 2.md",
    ]
    for artifact in duplicate_artifacts:
        if artifact.exists():
            findings.append(f"{artifact.relative_to(ROOT).as_posix()}: duplicate-ai-artifact")

    if findings:
        print("Public repo audit failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("Public repo audit passed: no local paths, no stray AI duplicate directories, and no attribution outside README.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
