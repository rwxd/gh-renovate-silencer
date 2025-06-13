"""GitHub client for interacting with notifications."""

from typing import List, Tuple

import github
import requests
from github import Github
from github.Notification import Notification
from rich.console import Console

from gh_renovate_silencer.models import Config

console = Console()


class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self, config: Config):
        """Initialize the GitHub client.

        Args:
            config: Configuration for the client
        """
        self.config = config
        self.client = Github(config.github_token)
        self.user = self.client.get_user()

        if self.config.verbose:
            console.print(f"Authenticated as: [bold]{self.user.login}[/]")

    def get_renovate_notifications(self) -> Tuple[List[Notification], List[Notification]]:
        """Get all unread notifications and incomplete notifications from Renovate bot.

        Returns:
            Tuple of (unread notifications, incomplete notifications) from Renovate bot
        """
        # Get unread notifications
        unread_notifications = self.client.get_user().get_notifications(all=False)
        # Get all notifications (including read but not completed)
        all_notifications = self.client.get_user().get_notifications(all=True)

        renovate_unread = []
        renovate_incomplete = []

        if self.config.verbose:
            console.print(
                f"[bold]Total unread notifications found:[/] {unread_notifications.totalCount}"
            )
            console.print(f"[bold]Total notifications found:[/] {all_notifications.totalCount}")

        # Process unread notifications
        if unread_notifications.totalCount > 0:
            if self.config.verbose:
                console.print("\n[bold]Processing unread notifications:[/]")

            renovate_unread = self._process_notifications(unread_notifications, "unread")

        # Process all notifications to find incomplete ones
        if all_notifications.totalCount > 0:
            if self.config.verbose:
                console.print("\n[bold]Processing all notifications to find incomplete ones:[/]")

            # Get all notifications that are from Renovate but not in the unread list
            all_renovate = self._process_notifications(all_notifications, "incomplete")
            renovate_incomplete = [n for n in all_renovate if n not in renovate_unread]

        if self.config.verbose:
            console.print(f"\n[bold]Renovate unread notifications found:[/] {len(renovate_unread)}")
            console.print(
                f"[bold]Renovate incomplete notifications found:[/] {len(renovate_incomplete)}"
            )

        return renovate_unread, renovate_incomplete

    def _process_notifications(self, notifications, notification_type: str) -> List[Notification]:
        """Process notifications to find ones from Renovate.

        Args:
            notifications: List of notifications to process
            notification_type: Type of notifications being processed ("unread" or "incomplete")

        Returns:
            List of Renovate notifications
        """
        renovate_notifications = []

        for notification in notifications:
            # Print notification details in verbose mode
            if self.config.verbose:
                console.print(
                    f"- [bold]{notification.repository.full_name}[/]: {notification.subject.title}"
                )
                console.print(f"  Type: {notification.subject.type}")

            # Only check if it's a PR notification
            if notification.subject.type != "PullRequest":
                if self.config.verbose:
                    console.print("  [yellow]✗[/] Not a PullRequest notification, skipping")
                continue

            # For PRs, check if it was created by Renovate
            try:
                pr = notification.get_pull_request()
                creator = pr.user.login.lower()

                if self.config.verbose:
                    console.print(f"  PR created by: {pr.user.login}")

                # Check if the PR creator is Renovate
                if "renovate" in creator or creator.endswith("[bot]"):
                    if self.config.verbose:
                        console.print("  [green]✓[/] PR created by Renovate bot")

                    # Skip excluded repositories
                    if notification.repository.full_name in self.config.exclude_repos:
                        if self.config.verbose:
                            console.print(
                                f"  [red]✗[/] Skipping notification from excluded repository: [bold]{notification.repository.full_name}[/]"
                            )
                        continue

                    # Add to renovate notifications
                    renovate_notifications.append(notification)
                    if self.config.verbose:
                        console.print(
                            f"  [green]✓[/] Added to Renovate {notification_type} notifications list"
                        )
                elif self.config.verbose:
                    console.print("  [yellow]✗[/] PR not created by Renovate bot")

            except Exception as e:
                if self.config.verbose:
                    console.print(f"  [red]![/] Error checking PR creator: {e!s}")

        return renovate_notifications

    def process_notifications(
        self,
        unread_notifications: List[Notification],
        incomplete_notifications: List[Notification],
        dry_run: bool = False,
    ) -> Tuple[int, int]:
        """Process both unread and incomplete notifications.

        Args:
            unread_notifications: List of unread notifications to mark as read
            incomplete_notifications: List of incomplete notifications to mark as complete
            dry_run: If True, only show what would be done without making changes

        Returns:
            Tuple of (count of notifications marked as read, count of notifications marked as complete)
        """
        read_count = 0
        complete_count = 0

        if dry_run:
            if unread_notifications:
                console.print(
                    "[yellow]Dry run mode - showing unread notifications that would be marked as read:[/]"
                )
                for notification in unread_notifications:
                    console.print(
                        f"Would mark as read: {notification.repository.full_name} - {notification.subject.title}"
                    )

            if incomplete_notifications:
                console.print(
                    "[yellow]Dry run mode - showing incomplete notifications that would be marked as complete:[/]"
                )
                for notification in incomplete_notifications:
                    console.print(
                        f"Would mark as complete: {notification.repository.full_name} - {notification.subject.title}"
                    )

            return 0, 0

        # Mark unread notifications as read
        if unread_notifications:
            if self.config.verbose:
                console.print("\n[bold]Marking unread notifications as read:[/]")
            read_count = self._mark_notifications_as_read(unread_notifications)

        # Mark incomplete notifications as complete
        if incomplete_notifications:
            if self.config.verbose:
                console.print("\n[bold]Marking incomplete notifications as complete:[/]")
            complete_count = self._mark_notifications_as_complete(incomplete_notifications)

        return read_count, complete_count

    def _mark_notifications_as_read(self, notifications: List[Notification]) -> int:
        """Mark notifications as read.

        Args:
            notifications: List of notifications to mark as read

        Returns:
            Number of notifications marked as read
        """
        count = 0
        for notification in notifications:
            try:
                notification.mark_as_read()
                count += 1
                if self.config.verbose:
                    console.print(
                        f"Marked as read: [bold]{notification.repository.full_name}[/] - {notification.subject.title}"
                    )
            except github.GithubException as e:
                console.print(f"[bold red]Error:[/] Failed to mark notification as read: {e}")

        return count

    def _mark_notifications_as_complete(self, notifications: List[Notification]) -> int:
        """Mark notifications as complete (done).

        Args:
            notifications: List of notifications to mark as complete

        Returns:
            Number of notifications marked as complete
        """
        count = 0
        for notification in notifications:
            try:
                # Get the thread ID from the notification
                thread_id = notification.id

                # Create the URL for the DELETE request
                url = f"https://api.github.com/notifications/threads/{thread_id}"

                # Make the request using requests library
                response = requests.delete(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.config.github_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                )

                # Check if the request was successful
                if response.status_code != 204:
                    raise github.GithubException(
                        response.status_code, f"Failed to mark thread as done: {response.text}"
                    )

                count += 1
                if self.config.verbose:
                    console.print(
                        f"Marked thread {thread_id} as done: [bold]{notification.repository.full_name}[/] - {notification.subject.title}"
                    )
            except Exception as e:
                console.print(f"[bold red]Error:[/] Failed to mark thread as done: {e}")

        return count
