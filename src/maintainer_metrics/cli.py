"""Command-line interface for maintainer-metrics."""

import json
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from maintainer_metrics import __version__
from maintainer_metrics.client import GitHubClient
from maintainer_metrics.metrics import RepositoryMetrics

console = Console()


def parse_repo(repo_arg: str) -> tuple[str, str]:
    """Parse owner/repo from argument.

    Args:
        repo_arg: Repository in format 'owner/repo'

    Returns:
        Tuple of (owner, repo)

    Raises:
        click.BadParameter: If format is invalid
    """
    parts = repo_arg.split("/")
    if len(parts) != 2:
        raise click.BadParameter(
            f"Repository must be in format 'owner/repo', got: {repo_arg}"
        )
    return parts[0], parts[1]


@click.group()
@click.version_option(version=__version__, prog_name="maintainer-metrics")
def main() -> None:
    """Maintainer Metrics - Health metrics for open-source maintainers.

    Report repository health metrics useful for grant applications,
    triage, and maintainer insights.
    """
    pass


@main.command()
@click.argument("repository")
@click.option(
    "--token",
    envvar="GITHUB_TOKEN",
    help="GitHub personal access token (or set GITHUB_TOKEN env var)",
)
@click.option(
    "--json-output",
    is_flag=True,
    help="Output metrics as JSON",
)
def check(repository: str, token: Optional[str], json_output: bool) -> None:
    """Check repository metrics and display detailed statistics.

    REPOSITORY should be in the format 'owner/repo', e.g., 'python/cpython'
    """
    try:
        owner, repo = parse_repo(repository)
        client = GitHubClient(token=token)
        metrics_calc = RepositoryMetrics(client, owner, repo)

        if not json_output:
            with console.status(f"[bold green]Fetching metrics for {owner}/{repo}..."):
                metrics = metrics_calc.get_all_metrics()
        else:
            metrics = metrics_calc.get_all_metrics()

        if json_output:
            click.echo(json.dumps(metrics, indent=2))
            return

        # Display rich formatted output
        console.print(
            Panel(
                f"[bold cyan]{owner}/{repo}[/bold cyan]",
                title="Repository Metrics",
                border_style="cyan",
            )
        )

        # Basic stats table
        basic_table = Table(title="Basic Statistics", show_header=False)
        basic_table.add_column("Metric", style="cyan")
        basic_table.add_column("Value", style="green")

        basic = metrics["basic"]
        basic_table.add_row("⭐ Stars", str(basic["stars"]))
        basic_table.add_row("🍴 Forks", str(basic["forks"]))
        basic_table.add_row("👀 Watchers", str(basic["watchers"]))
        basic_table.add_row("📂 Size", f"{basic['size_kb']} KB")
        basic_table.add_row(
            "📜 License", basic["license"] if basic["license"] else "None"
        )
        basic_table.add_row("🌿 Default Branch", basic["default_branch"])

        console.print(basic_table)
        console.print()

        # Issues table
        issues_table = Table(title="Issues", show_header=False)
        issues_table.add_column("Metric", style="cyan")
        issues_table.add_column("Value", style="yellow")

        issues = metrics["issues"]
        issues_table.add_row("Total Issues", str(issues["total"]))
        issues_table.add_row("Open Issues", str(issues["open"]))
        issues_table.add_row("Closed Issues", str(issues["closed"]))

        console.print(issues_table)
        console.print()

        # Pull Requests table
        pr_table = Table(title="Pull Requests", show_header=False)
        pr_table.add_column("Metric", style="cyan")
        pr_table.add_column("Value", style="magenta")

        prs = metrics["pull_requests"]
        pr_table.add_row("Total PRs", str(prs["total"]))
        pr_table.add_row("Open PRs", str(prs["open"]))
        pr_table.add_row("Closed PRs", str(prs["closed"]))
        pr_table.add_row("Merged PRs", str(prs["merged"]))
        pr_table.add_row("Merge Rate", f"{prs['merge_rate_percent']}%")

        console.print(pr_table)
        console.print()

        # Commit Activity table
        commit_table = Table(title="Recent Commit Activity", show_header=False)
        commit_table.add_column("Metric", style="cyan")
        commit_table.add_column("Value", style="blue")

        commits = metrics["commits"]
        commit_table.add_row(
            f"Commits (last {commits['days_analyzed']} days)",
            str(commits["total_commits"]),
        )
        commit_table.add_row("Unique Authors", str(commits["unique_authors"]))
        commit_table.add_row("Commits/Day", str(commits["commits_per_day"]))

        console.print(commit_table)
        console.print()

        # Releases table
        release_table = Table(title="Releases", show_header=False)
        release_table.add_column("Metric", style="cyan")
        release_table.add_column("Value", style="green")

        releases = metrics["releases"]
        release_table.add_row("Total Releases", str(releases["total_releases"]))

        latest = releases["latest_release"]
        if latest:
            release_table.add_row("Latest Release", latest["tag"] or "N/A")
            release_table.add_row("Release Name", latest["name"] or "N/A")
            release_table.add_row("Published At", latest["published_at"] or "N/A")

        if releases["avg_days_between_releases"]:
            release_table.add_row(
                "Avg Days Between Releases",
                str(releases["avg_days_between_releases"]),
            )

        console.print(release_table)
        console.print()

        # Branch Protection
        protection = metrics["branch_protection"]
        protection_text = Text()
        protection_text.append("🛡️  Branch Protection: ", style="cyan")
        if protection["is_protected"] is True:
            protection_text.append("Enabled", style="green bold")
        elif protection["is_protected"] is False:
            protection_text.append("Not Enabled", style="yellow")
        else:
            protection_text.append("Unknown (requires authentication)", style="dim")
        protection_text.append(f" (branch: {protection['default_branch']})", style="dim")

        console.print(protection_text)

    except click.BadParameter as e:
        console.print(f"[bold red]Error:[/bold red] {e.message}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.argument("repository")
@click.option(
    "--token",
    envvar="GITHUB_TOKEN",
    help="GitHub personal access token (or set GITHUB_TOKEN env var)",
)
@click.option(
    "--max-chars",
    default=500,
    type=int,
    help="Maximum characters for summary (default: 500)",
)
def summary(repository: str, token: Optional[str], max_chars: int) -> None:
    """Generate a plain-text summary suitable for grant applications.

    REPOSITORY should be in the format 'owner/repo', e.g., 'python/cpython'

    The summary is concise and suitable for pasting into grant forms
    or applications with character limits.
    """
    try:
        owner, repo = parse_repo(repository)
        client = GitHubClient(token=token)
        metrics_calc = RepositoryMetrics(client, owner, repo)

        with console.status(f"[bold green]Generating summary for {owner}/{repo}..."):
            summary_text = metrics_calc.generate_summary(max_chars=max_chars)

        console.print(Panel(summary_text, title="Repository Summary", border_style="green"))
        console.print(f"\n[dim]Character count: {len(summary_text)}/{max_chars}[/dim]")

    except click.BadParameter as e:
        console.print(f"[bold red]Error:[/bold red] {e.message}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--token",
    envvar="GITHUB_TOKEN",
    help="GitHub personal access token",
)
def rate_limit(token: Optional[str]) -> None:
    """Check GitHub API rate limit status."""
    try:
        client = GitHubClient(token=token)
        limits = client.get_rate_limit()

        core = limits.get("resources", {}).get("core", {})

        table = Table(title="GitHub API Rate Limits")
        table.add_column("Resource", style="cyan")
        table.add_column("Limit", style="green")
        table.add_column("Remaining", style="yellow")
        table.add_column("Reset", style="blue")

        from datetime import datetime

        reset_time = datetime.fromtimestamp(core.get("reset", 0))

        table.add_row(
            "Core API",
            str(core.get("limit", 0)),
            str(core.get("remaining", 0)),
            reset_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        console.print(table)

        if core.get("remaining", 0) < 100:
            console.print(
                "\n[yellow]⚠️  Warning: Low rate limit remaining. "
                "Consider using a GitHub token.[/yellow]"
            )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
