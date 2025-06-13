# GitHub Renovate Silencer

A simple CLI tool to silence GitHub notifications from Renovate bot.

## Features

- Automatically mark all Renovate bot notifications as read
- Exclude specific repositories from silencing
- Dry run mode to preview actions without making changes
- Containerized for easy deployment

## Installation

### Using pip with uv

```bash
uv pip install git+https://github.com/rwxd/gh-renovate-silencer.git
```

### Using Docker

```bash
docker pull ghcr.io/rwxd/gh-renovate-silencer:latest
```

## Usage

### CLI

```bash
# Basic usage
gh-renovate-silencer silence --token YOUR_GITHUB_TOKEN

# Exclude specific repositories
gh-renovate-silencer silence --token YOUR_GITHUB_TOKEN --exclude owner/repo1 --exclude owner/repo2

# Dry run mode
gh-renovate-silencer silence --token YOUR_GITHUB_TOKEN --dry-run

# Using environment variable for token
export GITHUB_TOKEN=YOUR_GITHUB_TOKEN
gh-renovate-silencer silence
```

### Docker

```bash
docker run -e GITHUB_TOKEN=YOUR_GITHUB_TOKEN ghcr.io/rwxd/gh-renovate-silencer:latest

# With excluded repositories
docker run -e GITHUB_TOKEN=YOUR_GITHUB_TOKEN ghcr.io/rwxd/gh-renovate-silencer:latest --exclude owner/repo1 --exclude owner/repo2
```

## Getting a GitHub Token

To use this tool, you'll need a GitHub Personal Access Token (PAT) with the appropriate permissions:

1. Go to your GitHub account settings: https://github.com/settings/tokens
2. Click "Generate new token" (classic)
3. Give your token a descriptive name (e.g., "Renovate Notification Silencer")
4. Select the **notifications** scope
5. Click "Generate token"
6. Copy the token immediately (you won't be able to see it again)

You can use this token with the `--token` flag or set it as the `GITHUB_TOKEN` environment variable.

## Required Permissions

The GitHub token needs the following permissions:
- `notifications` - To read and mark notifications as read

## License

MIT
