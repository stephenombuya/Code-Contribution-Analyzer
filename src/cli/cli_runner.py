"""
CLI entry point — run analyses directly from the command line.

Usage:
  python -m src.cli.cli_runner analyze --platform github --token ghp_xxx --username octocat
  python -m src.cli.cli_runner analyze --platform github --token ghp_xxx --output report.pdf
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import box

console = Console()


@click.group()
@click.version_option("1.0.0")
def cli():
    """Code Contribution Analyzer — gain insights into your coding journey."""
    pass


@cli.command()
@click.option("--platform", "-p", required=True,
              type=click.Choice(["github", "gitlab", "bitbucket"]),
              help="Code hosting platform.")
@click.option("--token", "-t", envvar="API_TOKEN",
              help="Personal access token (or set API_TOKEN env var).")
@click.option("--username", "-u", default=None,
              help="Username to analyze (defaults to token owner).")
@click.option("--since", default=None, help="Start date YYYY-MM-DD.")
@click.option("--until", default=None, help="End date YYYY-MM-DD.")
@click.option("--max-repos", default=50, show_default=True,
              help="Maximum number of repos to analyze.")
@click.option("--output", "-o", default=None,
              help="Save report to file (.json, .csv, or .pdf).")
@click.option("--no-private", is_flag=True, default=False,
              help="Exclude private repositories.")
def analyze(platform, token, username, since, until, max_repos, output, no_private):
    """Analyze contribution data for a platform account."""

    if not token:
        console.print("[red]Error:[/] No token provided. Use --token or set API_TOKEN env var.")
        sys.exit(1)

    # Import here to keep CLI startup fast
    from src.api_clients.github_client import GitHubClient
    from src.api_clients.gitlab_client import GitLabClient
    from src.api_clients.bitbucket_client import BitbucketClient
    from src.analysis.contribution_analyzer import ContributionAnalyzer
    from src.visualization.report_generator import ReportGenerator

    clients = {
        "github": GitHubClient,
        "gitlab": GitLabClient,
        "bitbucket": BitbucketClient,
    }

    client_cls = clients[platform]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Connecting to {platform}…", total=None)

        try:
            client = client_cls(token)
            user_info = client.get_authenticated_user()
            effective_user = username or user_info.get("login") or user_info.get("username") or ""
            progress.update(task, description=f"Analyzing @{effective_user} on {platform}…")

            analyzer = ContributionAnalyzer(client, effective_user)
            summary = analyzer.analyze(
                since=since,
                until=until,
                max_repos=max_repos,
                include_private=not no_private,
            )
            progress.update(task, description="Done!", completed=1, total=1)

        except Exception as exc:
            progress.stop()
            console.print(f"[red]Analysis failed:[/] {exc}")
            sys.exit(1)

    # ── Print results ─────────────────────────────────────────────────────────
    data = summary.to_dict()

    console.print()
    console.print(Panel.fit(
        f"[bold white]@{summary.username}[/] on [bold cyan]{summary.platform}[/]",
        title="Analysis Complete",
        border_style="bright_blue",
    ))

    # Summary table
    t = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    t.add_column("Metric", style="dim")
    t.add_column("Value", style="bold white")
    t.add_row("Repositories", f"{data['total_repos']:,}")
    t.add_row("Commits", f"{data['total_commits']:,}")
    t.add_row("Lines Added", f"[green]+{data['total_additions']:,}[/]")
    t.add_row("Lines Removed", f"[red]-{data['total_deletions']:,}[/]")
    t.add_row("Net Lines", f"[cyan]{data['net_lines']:,}[/]")
    console.print(t)
    console.print()

    # Top languages
    if data.get("languages"):
        lang_table = Table(title="Top Languages", box=box.SIMPLE, padding=(0, 1))
        lang_table.add_column("Language", style="cyan")
        lang_table.add_column("Net LOC", style="white", justify="right")
        lang_table.add_column("Share", style="dim", justify="right")
        total_loc = sum(data["languages"].values()) or 1
        for lang, loc in sorted(data["languages"].items(), key=lambda x: x[1], reverse=True)[:10]:
            pct = loc / total_loc * 100
            lang_table.add_row(lang, f"{loc:,}", f"{pct:.1f}%")
        console.print(lang_table)
        console.print()

    # Top repos
    if data.get("top_repos"):
        repo_table = Table(title="Top Repositories", box=box.SIMPLE, padding=(0, 1))
        repo_table.add_column("Repository", style="white")
        repo_table.add_column("Language", style="cyan")
        repo_table.add_column("Commits", justify="right")
        repo_table.add_column("+Lines", justify="right", style="green")
        for repo in data["top_repos"][:10]:
            repo_table.add_row(
                repo.get("full_name", ""),
                repo.get("language", ""),
                str(repo.get("user_commits", 0)),
                f"+{repo.get('user_additions', 0):,}",
            )
        console.print(repo_table)
        console.print()

    # ── Save report ───────────────────────────────────────────────────────────
    if output:
        out_path = Path(output)
        gen = ReportGenerator(data, summary.username, summary.platform)

        if out_path.suffix == ".json":
            out_path.write_bytes(gen.to_json())
        elif out_path.suffix == ".csv":
            out_path.write_bytes(gen.to_csv())
        elif out_path.suffix == ".pdf":
            out_path.write_bytes(gen.to_pdf())
        else:
            console.print(f"[yellow]Unknown extension '{out_path.suffix}'. Saving as JSON.[/]")
            out_path = out_path.with_suffix(".json")
            out_path.write_bytes(gen.to_json())

        console.print(f"[green]Report saved:[/] {out_path.resolve()}")


@cli.command()
@click.option("--platform", "-p", required=True,
              type=click.Choice(["github", "gitlab", "bitbucket"]))
@click.option("--token", "-t", envvar="API_TOKEN")
def whoami(platform, token):
    """Show the authenticated user for a given token."""
    if not token:
        console.print("[red]Error:[/] No token provided.")
        sys.exit(1)
    from src.api_clients.github_client import GitHubClient
    from src.api_clients.gitlab_client import GitLabClient
    from src.api_clients.bitbucket_client import BitbucketClient
    clients = {"github": GitHubClient, "gitlab": GitLabClient, "bitbucket": BitbucketClient}
    try:
        client = clients[platform](token)
        info = client.get_authenticated_user()
        name = info.get("name") or info.get("login") or info.get("username") or "Unknown"
        login = info.get("login") or info.get("username") or ""
        console.print(f"[green]Authenticated as:[/] {name} (@{login}) on {platform}")
    except Exception as exc:
        console.print(f"[red]Authentication failed:[/] {exc}")


if __name__ == "__main__":
    cli()
