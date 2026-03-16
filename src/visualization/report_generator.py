"""
Report generation: CSV, JSON, and PDF outputs.
"""
from __future__ import annotations

import csv
import io
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates downloadable reports from analysis results."""

    def __init__(self, result: dict, username: str, platform: str) -> None:
        self.result = result
        self.username = username
        self.platform = platform
        self.generated_at = datetime.now(timezone.utc).isoformat()

    # ── JSON ──────────────────────────────────────────────────────────────────

    def to_json(self) -> bytes:
        payload = {
            "generated_at": self.generated_at,
            "username": self.username,
            "platform": self.platform,
            "summary": {
                "total_repos": self.result.get("total_repos"),
                "total_commits": self.result.get("total_commits"),
                "total_additions": self.result.get("total_additions"),
                "total_deletions": self.result.get("total_deletions"),
                "net_lines": self.result.get("net_lines"),
            },
            "languages": self.result.get("languages", {}),
            "monthly_activity": self.result.get("monthly_activity", []),
            "repositories": self.result.get("repos", []),
        }
        return json.dumps(payload, indent=2, default=str).encode("utf-8")

    # ── CSV ───────────────────────────────────────────────────────────────────

    def to_csv(self) -> bytes:
        output = io.StringIO()

        # Sheet 1: Summary
        writer = csv.writer(output)
        writer.writerow(["Code Contribution Report"])
        writer.writerow(["Generated At", self.generated_at])
        writer.writerow(["Username", self.username])
        writer.writerow(["Platform", self.platform])
        writer.writerow([])

        writer.writerow(["=== SUMMARY ==="])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Repositories", self.result.get("total_repos", 0)])
        writer.writerow(["Total Commits", self.result.get("total_commits", 0)])
        writer.writerow(["Total Additions", self.result.get("total_additions", 0)])
        writer.writerow(["Total Deletions", self.result.get("total_deletions", 0)])
        writer.writerow(["Net Lines", self.result.get("net_lines", 0)])
        writer.writerow([])

        writer.writerow(["=== LANGUAGE BREAKDOWN ==="])
        writer.writerow(["Language", "Net Lines"])
        for lang, lines in sorted(
            (self.result.get("languages") or {}).items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            writer.writerow([lang, lines])
        writer.writerow([])

        writer.writerow(["=== MONTHLY ACTIVITY ==="])
        writer.writerow(["Month", "Commits", "Additions", "Deletions"])
        for m in self.result.get("monthly_activity", []):
            writer.writerow([
                m.get("month"),
                m.get("commits", 0),
                m.get("additions", 0),
                m.get("deletions", 0),
            ])
        writer.writerow([])

        writer.writerow(["=== REPOSITORIES ==="])
        writer.writerow([
            "Repository", "Language", "Stars", "Forks",
            "User Commits", "Additions", "Deletions", "Private",
        ])
        for repo in self.result.get("repos", []):
            writer.writerow([
                repo.get("full_name", ""),
                repo.get("language", ""),
                repo.get("stars", 0),
                repo.get("forks", 0),
                repo.get("user_commits", 0),
                repo.get("user_additions", 0),
                repo.get("user_deletions", 0),
                "Yes" if repo.get("is_private") else "No",
            ])

        return output.getvalue().encode("utf-8")

    # ── PDF (fpdf2) ───────────────────────────────────────────────────────────

    def to_pdf(self) -> bytes:
        try:
            from fpdf import FPDF, XPos, YPos
        except ImportError:
            logger.warning("fpdf2 not installed; falling back to JSON.")
            return self.to_json()

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ── Cover ────────────────────────────────────────────────────────────
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_fill_color(30, 41, 59)  # slate-800
        pdf.set_text_color(255, 255, 255)
        pdf.rect(0, 0, 210, 45, "F")
        pdf.set_xy(15, 10)
        pdf.cell(0, 10, "Code Contribution Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 12)
        pdf.set_xy(15, 25)
        pdf.cell(0, 8, f"@{self.username}  |  {self.platform.title()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(15, 33)
        pdf.cell(0, 8, f"Generated: {self.generated_at[:10]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(55)

        def section(title: str) -> None:
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_fill_color(241, 245, 249)
            pdf.cell(0, 9, f"  {title}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(3)

        def kv(key: str, value: Any, indent: int = 0) -> None:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_x(15 + indent)
            pdf.cell(70, 7, key + ":")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, str(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # ── Summary ──────────────────────────────────────────────────────────
        section("Summary")
        kv("Total Repositories", f"{self.result.get('total_repos', 0):,}")
        kv("Total Commits", f"{self.result.get('total_commits', 0):,}")
        kv("Lines Added", f"{self.result.get('total_additions', 0):,}")
        kv("Lines Deleted", f"{self.result.get('total_deletions', 0):,}")
        kv("Net Lines Written", f"{self.result.get('net_lines', 0):,}")
        pdf.ln(5)

        # ── Language breakdown ────────────────────────────────────────────────
        section("Language Breakdown")
        langs = sorted(
            (self.result.get("languages") or {}).items(),
            key=lambda x: x[1],
            reverse=True,
        )[:20]
        total_loc = sum(v for _, v in langs) or 1
        for lang, lines in langs:
            pct = lines / total_loc * 100
            pdf.set_font("Helvetica", "", 10)
            pdf.set_x(15)
            pdf.cell(60, 6, lang)
            pdf.cell(30, 6, f"{lines:,} lines")
            # bar
            bar_w = max(1, int(pct * 0.8))
            pdf.set_fill_color(99, 102, 241)  # indigo-500
            pdf.rect(pdf.get_x(), pdf.get_y() + 1, bar_w, 4, "F")
            pdf.set_x(pdf.get_x() + 85)
            pdf.cell(20, 6, f"{pct:.1f}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

        # ── Top repositories ──────────────────────────────────────────────────
        section("Top Repositories by Commits")
        top_repos = sorted(
            self.result.get("repos", []),
            key=lambda r: r.get("user_commits", 0),
            reverse=True,
        )[:15]
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(226, 232, 240)
        pdf.set_x(15)
        for col, w in [("Repository", 75), ("Language", 30), ("Commits", 20), ("+Lines", 25), ("-Lines", 25)]:
            pdf.cell(w, 7, col, fill=True)
        pdf.ln()
        pdf.set_font("Helvetica", "", 9)
        for i, repo in enumerate(top_repos):
            fill = i % 2 == 0
            pdf.set_fill_color(248, 250, 252) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.set_x(15)
            pdf.cell(75, 6, str(repo.get("full_name", ""))[:38], fill=fill)
            pdf.cell(30, 6, str(repo.get("language", ""))[:15], fill=fill)
            pdf.cell(20, 6, str(repo.get("user_commits", 0)), fill=fill)
            pdf.cell(25, 6, f"+{repo.get('user_additions', 0):,}", fill=fill)
            pdf.cell(25, 6, f"-{repo.get('user_deletions', 0):,}", fill=fill, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

        # ── Monthly activity ──────────────────────────────────────────────────
        monthly = self.result.get("monthly_activity", [])
        if monthly:
            section("Monthly Activity")
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_fill_color(226, 232, 240)
            pdf.set_x(15)
            for col, w in [("Month", 35), ("Commits", 30), ("Additions", 35), ("Deletions", 35)]:
                pdf.cell(w, 7, col, fill=True)
            pdf.ln()
            pdf.set_font("Helvetica", "", 9)
            for i, m in enumerate(monthly[-24:]):  # last 2 years
                fill = i % 2 == 0
                pdf.set_fill_color(248, 250, 252) if fill else pdf.set_fill_color(255, 255, 255)
                pdf.set_x(15)
                pdf.cell(35, 6, str(m.get("month", "")), fill=fill)
                pdf.cell(30, 6, str(m.get("commits", 0)), fill=fill)
                pdf.cell(35, 6, f"+{m.get('additions', 0):,}", fill=fill)
                pdf.cell(35, 6, f"-{m.get('deletions', 0):,}", fill=fill, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        return bytes(pdf.output())
