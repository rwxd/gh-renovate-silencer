"""Command line interface for GitHub Renovate Bot notification silencer."""

import sys
from typing import List, Optional

import typer
from rich.console import Console

from gh_renovate_silencer.github_client import GitHubClient
from gh_renovate_silencer.models import Config

app = typer.Typer(help="Silence GitHub notifications from Renovate bot")
console = Console()


@app.command()
def silence(
    token: str = typer.Option(
        None, "--token", "-t", help="GitHub personal access token", envvar="GITHUB_TOKEN"
    ),
    exclude_repos: Optional[List[str]] = typer.Option(
        None,
        "--exclude",
        "-e",
        help="Repositories to exclude from silencing (can be specified multiple times)",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without actually doing it"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """Silence GitHub notifications from Renovate bot."""
    if not token:
        console.print("[bold red]Error:[/] GitHub token is required")
        console.print("Set it via --token option or GITHUB_TOKEN environment variable")
        sys.exit(1)

    config = Config(
        github_token=token,
        exclude_repos=exclude_repos or [],
        dry_run=dry_run,
        verbose=verbose,
    )

    client = GitHubClient(config)

    # Show a simple message instead of using a spinner
    if verbose:
        console.print("Fetching notifications...")

    # Get both unread and incomplete notifications
    unread_notifications, incomplete_notifications = client.get_renovate_notifications()

    if not unread_notifications and not incomplete_notifications:
        console.print("[green]No Renovate notifications found to process.[/]")
        return

    # Process both types of notifications
    read_count, complete_count = client.process_notifications(
        unread_notifications, incomplete_notifications, dry_run
    )

    if not dry_run:
        if read_count > 0:
            console.print(f"[green]Successfully marked {read_count} notifications as read[/]")
        if complete_count > 0:
            console.print(
                f"[green]Successfully marked {complete_count} notifications as complete[/]"
            )
        if read_count == 0 and complete_count == 0:
            console.print("[yellow]No notifications were processed.[/]")


if __name__ == "__main__":
    app()
