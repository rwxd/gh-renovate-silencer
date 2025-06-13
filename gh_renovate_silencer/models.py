"""Data models for GitHub Renovate Bot notification silencer."""

from typing import List, Optional

from pydantic import BaseModel


class Config(BaseModel):
    """Configuration for the GitHub client."""

    github_token: str
    exclude_repos: List[str] = []
    dry_run: bool = False
    verbose: bool = False
