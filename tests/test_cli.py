"""Tests for CLI commands."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from maintainer_metrics.cli import main, parse_repo


def test_parse_repo_valid():
    """Test parsing valid repository format."""
    owner, repo = parse_repo("python/cpython")
    assert owner == "python"
    assert repo == "cpython"


def test_parse_repo_invalid():
    """Test parsing invalid repository format."""
    from click import BadParameter

    with pytest.raises(BadParameter):
        parse_repo("invalid")

    with pytest.raises(BadParameter):
        parse_repo("too/many/slashes")


def test_cli_version():
    """Test --version flag."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.1" in result.output


def test_cli_help():
    """Test --help flag."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Maintainer Metrics" in result.output


@patch("maintainer_metrics.cli.GitHubClient")
@patch("maintainer_metrics.cli.RepositoryMetrics")
def test_check_command_json_output(mock_metrics_class, mock_client_class):
    """Test check command with JSON output."""
    mock_metrics = MagicMock()
    mock_metrics_class.return_value = mock_metrics
    mock_metrics.get_all_metrics.return_value = {
        "repository": "owner/repo",
        "basic": {"stars": 100, "forks": 50},
    }

    runner = CliRunner()
    result = runner.invoke(main, ["check", "owner/repo", "--json-output"])

    assert result.exit_code == 0
    assert '"repository": "owner/repo"' in result.output
    assert '"stars": 100' in result.output


@patch("maintainer_metrics.cli.GitHubClient")
@patch("maintainer_metrics.cli.RepositoryMetrics")
def test_check_command_rich_output(mock_metrics_class, mock_client_class):
    """Test check command with rich formatted output."""
    mock_metrics = MagicMock()
    mock_metrics_class.return_value = mock_metrics
    mock_metrics.get_all_metrics.return_value = {
        "repository": "owner/repo",
        "basic": {
            "stars": 100,
            "forks": 50,
            "watchers": 25,
            "size_kb": 1000,
            "license": "MIT",
            "default_branch": "main",
        },
        "issues": {"total": 10, "open": 5, "closed": 5},
        "pull_requests": {
            "total": 20,
            "open": 3,
            "closed": 17,
            "merged": 15,
            "merge_rate_percent": 88.2,
        },
        "commits": {
            "total_commits": 100,
            "days_analyzed": 90,
            "unique_authors": 10,
            "commits_per_day": 1.11,
        },
        "releases": {
            "total_releases": 5,
            "latest_release": {
                "tag": "v1.0.0",
                "name": "Release 1.0.0",
                "published_at": "2023-06-01T00:00:00Z",
                "prerelease": False,
            },
            "avg_days_between_releases": 30.0,
        },
        "branch_protection": {"default_branch": "main", "is_protected": True},
    }

    runner = CliRunner()
    result = runner.invoke(main, ["check", "owner/repo"])

    assert result.exit_code == 0
    assert "owner/repo" in result.output
    # Check for some key metrics in output
    assert "100" in result.output  # stars
    assert "50" in result.output  # forks


@patch("maintainer_metrics.cli.GitHubClient")
@patch("maintainer_metrics.cli.RepositoryMetrics")
def test_summary_command(mock_metrics_class, mock_client_class):
    """Test summary command."""
    mock_metrics = MagicMock()
    mock_metrics_class.return_value = mock_metrics
    mock_metrics.generate_summary.return_value = "Test summary with metrics"

    runner = CliRunner()
    result = runner.invoke(main, ["summary", "owner/repo"])

    assert result.exit_code == 0
    assert "Test summary with metrics" in result.output
    assert "Character count:" in result.output


@patch("maintainer_metrics.cli.GitHubClient")
@patch("maintainer_metrics.cli.RepositoryMetrics")
def test_summary_command_with_max_chars(mock_metrics_class, mock_client_class):
    """Test summary command with custom max_chars."""
    mock_metrics = MagicMock()
    mock_metrics_class.return_value = mock_metrics
    mock_metrics.generate_summary.return_value = "Short summary"

    runner = CliRunner()
    result = runner.invoke(main, ["summary", "owner/repo", "--max-chars", "100"])

    assert result.exit_code == 0
    mock_metrics.generate_summary.assert_called_once_with(max_chars=100)


def test_check_invalid_repo_format():
    """Test check command with invalid repository format."""
    runner = CliRunner()
    result = runner.invoke(main, ["check", "invalid-format"])

    assert result.exit_code == 1
    assert "Error:" in result.output


@patch("maintainer_metrics.cli.GitHubClient")
@patch("maintainer_metrics.cli.RepositoryMetrics")
def test_check_with_token(mock_metrics_class, mock_client_class):
    """Test check command with explicit token."""
    mock_metrics = MagicMock()
    mock_metrics_class.return_value = mock_metrics
    mock_metrics.get_all_metrics.return_value = {
        "repository": "owner/repo",
        "basic": {
            "stars": 100,
            "forks": 50,
            "watchers": 25,
            "size_kb": 1000,
            "license": "MIT",
            "default_branch": "main",
        },
        "issues": {"total": 10, "open": 5, "closed": 5},
        "pull_requests": {
            "total": 20,
            "open": 3,
            "closed": 17,
            "merged": 15,
            "merge_rate_percent": 88.2,
        },
        "commits": {
            "total_commits": 100,
            "days_analyzed": 90,
            "unique_authors": 10,
            "commits_per_day": 1.11,
        },
        "releases": {
            "total_releases": 5,
            "latest_release": {
                "tag": "v1.0.0",
                "name": "Release 1.0.0",
                "published_at": "2023-06-01T00:00:00Z",
                "prerelease": False,
            },
            "avg_days_between_releases": 30.0,
        },
        "branch_protection": {"default_branch": "main", "is_protected": True},
    }

    runner = CliRunner()
    result = runner.invoke(main, ["check", "owner/repo", "--token", "test_token"])

    assert result.exit_code == 0
    mock_client_class.assert_called_with(token="test_token")


@patch("maintainer_metrics.cli.GitHubClient")
def test_rate_limit_command(mock_client_class):
    """Test rate-limit command."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.get_rate_limit.return_value = {
        "resources": {
            "core": {
                "limit": 5000,
                "remaining": 4999,
                "reset": 1609459200,
            }
        }
    }

    runner = CliRunner()
    result = runner.invoke(main, ["rate-limit"])

    assert result.exit_code == 0
    assert "5000" in result.output
    assert "4999" in result.output
