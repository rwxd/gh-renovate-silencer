"""Tests for the CLI module."""

from typer.testing import CliRunner

from gh_renovate_silencer.cli import app

runner = CliRunner()


def test_cli_help():
    """Test the CLI help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Silence GitHub notifications from Renovate bot" in result.stdout


def test_silence_command_help():
    """Test the silence command help output."""
    result = runner.invoke(app, ["silence", "--help"])
    assert result.exit_code == 0
    assert "Silence GitHub notifications from Renovate bot" in result.stdout
