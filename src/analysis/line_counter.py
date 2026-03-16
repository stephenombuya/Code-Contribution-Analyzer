"""
Line-of-code counter with blank/comment filtering options.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.analysis.language_detector import detect_language, is_generated, IGNORED_LANGUAGES

logger = logging.getLogger(__name__)


@dataclass
class FileCount:
    path: str
    language: str
    total_lines: int
    code_lines: int
    blank_lines: int
    comment_lines: int


@dataclass
class RepoLineCount:
    total_lines: int = 0
    code_lines: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    by_language: dict[str, dict[str, int]] = field(default_factory=dict)
    files_counted: int = 0
    files_skipped: int = 0

    def add(self, fc: FileCount) -> None:
        self.total_lines += fc.total_lines
        self.code_lines += fc.code_lines
        self.blank_lines += fc.blank_lines
        self.comment_lines += fc.comment_lines
        self.files_counted += 1
        lang = fc.language
        if lang not in self.by_language:
            self.by_language[lang] = {
                "total": 0, "code": 0, "blank": 0, "comment": 0, "files": 0,
            }
        self.by_language[lang]["total"] += fc.total_lines
        self.by_language[lang]["code"] += fc.code_lines
        self.by_language[lang]["blank"] += fc.blank_lines
        self.by_language[lang]["comment"] += fc.comment_lines
        self.by_language[lang]["files"] += 1

    def to_dict(self) -> dict:
        return {
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "blank_lines": self.blank_lines,
            "comment_lines": self.comment_lines,
            "files_counted": self.files_counted,
            "files_skipped": self.files_skipped,
            "by_language": self.by_language,
        }


# ── Single-line comment prefixes per language ──────────────────────────────────
COMMENT_PREFIXES: dict[str, list[str]] = {
    "Python": ["#"],
    "Ruby": ["#"],
    "Shell": ["#"],
    "PowerShell": ["#"],
    "JavaScript": ["//", "/*"],
    "TypeScript": ["//", "/*"],
    "Java": ["//", "/*"],
    "C": ["//", "/*"],
    "C++": ["//", "/*"],
    "C#": ["//", "/*"],
    "Go": ["//", "/*"],
    "Rust": ["//", "/*"],
    "Kotlin": ["//", "/*"],
    "Swift": ["//", "/*"],
    "Scala": ["//", "/*"],
    "PHP": ["//", "#", "/*"],
    "Dart": ["//", "/*"],
    "SQL": ["--", "/*"],
    "SCSS": ["//", "/*"],
    "CSS": ["/*"],
    "R": ["#"],
    "Julia": ["#"],
    "Perl": ["#"],
    "Lua": ["--"],
    "Haskell": ["--", "{-"],
    "Elixir": ["#"],
    "Erlang": ["%"],
    "Groovy": ["//", "/*"],
}


def _is_comment(line: str, lang: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    prefixes = COMMENT_PREFIXES.get(lang, [])
    return any(stripped.startswith(p) for p in prefixes)


def count_file(filepath: str | Path) -> Optional[FileCount]:
    """
    Count lines in a single file.  Returns None for skipped files.
    """
    p = Path(filepath)
    if is_generated(p):
        return None

    lang = detect_language(p)
    if lang is None or lang in IGNORED_LANGUAGES:
        return None

    total = blank = comment = 0
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as fh:
            for raw_line in fh:
                total += 1
                stripped = raw_line.strip()
                if not stripped:
                    blank += 1
                elif _is_comment(raw_line, lang):
                    comment += 1
    except (OSError, PermissionError) as exc:
        logger.debug("Skipping %s: %s", filepath, exc)
        return None

    return FileCount(
        path=str(filepath),
        language=lang,
        total_lines=total,
        code_lines=total - blank - comment,
        blank_lines=blank,
        comment_lines=comment,
    )


def count_directory(directory: str | Path) -> RepoLineCount:
    """
    Recursively count lines in all source files under a directory.
    """
    root = Path(directory)
    result = RepoLineCount()

    for filepath in root.rglob("*"):
        if not filepath.is_file():
            continue
        fc = count_file(filepath)
        if fc is None:
            result.files_skipped += 1
        else:
            result.add(fc)

    logger.debug(
        "Counted %d files (%d skipped) in %s.",
        result.files_counted, result.files_skipped, directory,
    )
    return result
