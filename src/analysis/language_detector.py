"""
Programming language detection by file extension, shebang, or content heuristics.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

# ── Extension → Language map ──────────────────────────────────────────────────
# Covers the vast majority of real-world repos

EXTENSION_MAP: dict[str, str] = {
    # Python
    ".py": "Python", ".pyw": "Python", ".pyi": "Python",
    # JavaScript / TypeScript
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".mts": "TypeScript",
    # Web
    ".html": "HTML", ".htm": "HTML",
    ".css": "CSS", ".scss": "SCSS", ".sass": "Sass", ".less": "Less",
    # Java / JVM
    ".java": "Java",
    ".kt": "Kotlin", ".kts": "Kotlin",
    ".scala": "Scala",
    ".groovy": "Groovy",
    ".clj": "Clojure", ".cljs": "Clojure",
    # C-family
    ".c": "C", ".h": "C",
    ".cpp": "C++", ".cxx": "C++", ".cc": "C++", ".hxx": "C++", ".hpp": "C++",
    ".cs": "C#",
    # Systems / Low-level
    ".rs": "Rust",
    ".go": "Go",
    ".swift": "Swift",
    ".m": "Objective-C", ".mm": "Objective-C",
    ".zig": "Zig",
    # Ruby / Rails
    ".rb": "Ruby", ".rake": "Ruby", ".gemspec": "Ruby",
    ".erb": "Ruby",
    # PHP
    ".php": "PHP", ".phtml": "PHP",
    # Shell
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".fish": "Shell",
    ".ps1": "PowerShell", ".psm1": "PowerShell",
    ".bat": "Batch", ".cmd": "Batch",
    # Data / Config
    ".json": "JSON", ".jsonc": "JSON",
    ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML",
    ".xml": "XML", ".xsd": "XML", ".xslt": "XML",
    ".csv": "CSV", ".tsv": "CSV",
    ".sql": "SQL",
    ".graphql": "GraphQL", ".gql": "GraphQL",
    ".proto": "Protobuf",
    # Docs
    ".md": "Markdown", ".mdx": "Markdown",
    ".rst": "reStructuredText",
    ".tex": "LaTeX",
    ".txt": "Text",
    # Dart / Flutter
    ".dart": "Dart",
    # Elixir / Erlang
    ".ex": "Elixir", ".exs": "Elixir",
    ".erl": "Erlang", ".hrl": "Erlang",
    # Haskell / OCaml / F#
    ".hs": "Haskell", ".lhs": "Haskell",
    ".ml": "OCaml", ".mli": "OCaml",
    ".fs": "F#", ".fsx": "F#",
    # Lua
    ".lua": "Lua",
    # R
    ".r": "R", ".R": "R",
    # Julia
    ".jl": "Julia",
    # Perl
    ".pl": "Perl", ".pm": "Perl",
    # Dockerfile / IaC
    "Dockerfile": "Dockerfile",
    ".tf": "Terraform", ".tfvars": "Terraform",
    ".bicep": "Bicep",
    ".nix": "Nix",
    # Jupyter
    ".ipynb": "Jupyter Notebook",
    # Assembly
    ".asm": "Assembly", ".s": "Assembly",
    # VHDL / Verilog
    ".vhd": "VHDL", ".vhdl": "VHDL",
    ".v": "Verilog", ".sv": "SystemVerilog",
}

# Filenames with no extension
FILENAME_MAP: dict[str, str] = {
    "Dockerfile": "Dockerfile",
    "Makefile": "Makefile",
    "Rakefile": "Ruby",
    "Gemfile": "Ruby",
    "Podfile": "Ruby",
    ".bashrc": "Shell",
    ".zshrc": "Shell",
    ".profile": "Shell",
    "CMakeLists.txt": "CMake",
    "BUILD": "Bazel",
    "WORKSPACE": "Bazel",
    "Jenkinsfile": "Groovy",
    "Vagrantfile": "Ruby",
}

# Shebang → language
SHEBANG_MAP: dict[str, str] = {
    "python": "Python",
    "python3": "Python",
    "node": "JavaScript",
    "ruby": "Ruby",
    "perl": "Perl",
    "bash": "Shell",
    "sh": "Shell",
    "zsh": "Shell",
    "php": "PHP",
}

# Languages to exclude from LOC counts (docs, data, generated)
IGNORED_LANGUAGES = frozenset({
    "Markdown", "Text", "JSON", "YAML", "TOML", "CSV", "XML",
    "reStructuredText", "LaTeX",
})


def detect_language(filepath: str | Path) -> Optional[str]:
    """
    Detect programming language for a given file path.
    Returns None if unknown or intentionally ignored.
    """
    p = Path(filepath)
    name = p.name
    suffix = p.suffix.lower()

    # 1. Exact filename match
    if name in FILENAME_MAP:
        return FILENAME_MAP[name]

    # 2. Extension match
    if suffix in EXTENSION_MAP:
        return EXTENSION_MAP[suffix]

    # 3. Upper-case suffix (e.g. .R)
    if p.suffix in EXTENSION_MAP:
        return EXTENSION_MAP[p.suffix]

    # 4. Shebang (only for extensionless files)
    if not suffix:
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                first_line = fh.readline(128)
            if first_line.startswith("#!"):
                for interpreter, lang in SHEBANG_MAP.items():
                    if interpreter in first_line:
                        return lang
        except (OSError, PermissionError):
            pass

    return None


def is_generated(filepath: str | Path) -> bool:
    """Heuristic: skip auto-generated files (minified, vendor, lockfiles)."""
    p = Path(filepath)
    parts = set(p.parts)
    skip_dirs = {
        "node_modules", "vendor", ".git", "__pycache__", ".tox",
        "dist", "build", "target", ".next", ".nuxt", "venv", ".venv",
        "env", ".env", "coverage", ".coverage", "htmlcov", "site-packages",
        "eggs", ".eggs", "bower_components", "jspm_packages",
    }
    if parts & skip_dirs:
        return True
    skip_patterns = (
        ".min.js", ".min.css", ".bundle.js", ".chunk.js",
        ".map", ".lock", "-lock.json", ".sum",
    )
    name = p.name.lower()
    return any(name.endswith(pat) for pat in skip_patterns)


def language_stats_from_files(
    filepaths: list[str | Path],
) -> dict[str, dict[str, int]]:
    """
    Given a list of file paths return:
      { "Python": {"files": N, "lines": N}, ... }
    Only counts lines for source files (not generated, not ignored).
    """
    stats: dict[str, dict[str, int]] = {}

    for fp in filepaths:
        if is_generated(fp):
            continue
        lang = detect_language(fp)
        if lang is None or lang in IGNORED_LANGUAGES:
            continue
        lines = _count_lines(fp)
        if lang not in stats:
            stats[lang] = {"files": 0, "lines": 0}
        stats[lang]["files"] += 1
        stats[lang]["lines"] += lines

    return stats


def _count_lines(filepath: str | Path) -> int:
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
            return sum(1 for _ in fh)
    except (OSError, PermissionError):
        return 0
