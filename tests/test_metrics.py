"""Tests for metrics calculation."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from maintainer_metrics.client import GitHubClient
from maintainer_metrics.metrics import RepositoryMetrics


@pytest.fixture
def mock_client():
    """Create a mock GitHub client."""
    return MagicMock(spec=GitHubClient)


@pytest.fixture
def sample_repo_data():
    """Sample repository data."""
    return {
        "stargazers_count": 1234,
        "forks_count": 567,
        "subscribers_count": 89,
        "open_issues_count": 42,
        "size": 5000,
        "default_branch": "main",
        "license": {"spdx_id": "MIT"},
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2023-06-15T12:00:00Z",
        "pushed_at": "2023-06-15T12:00:00Z",
    }


@pytest.fixture
def sample_issues():
    """Sample issues data."""
    return [
        {"id": 1, "state": "open"},
        {"id": 2, "state": "closed"},
        {"id": 3, "state": "open", "pull_request": {}},  # This is a PR
    ]


@pytest.fixture
def sample_pulls():
    """Sample pull requests data."""
    return [
        {"id": 1, "state": "open"},
        {"id": 2, "state": "closed", "merged_at": "2023-06-01T00:00:00Z"},
        {"id": 3, "state": "closed", "merged_at": None},
    ]


@pytest.fixture
def sample_commits():
    """Sample commits data."""
    return [
        {
            "sha": "abc123",
            "author": {"login": "user1"},
            "commit": {"author": {"date": "2023-06-01T00:00:00Z"}},
        },
        {
            "sha": "def456",
            "author": {"login": "user2"},
            "commit": {"author": {"date": "2023-06-02T00:00:00Z"}},
        },
        {
            "sha": "ghi789",
            "author": {"login": "user1"},
            "commit": {"author": {"date": "2023-06-03T00:00:00Z"}},
        },
    ]


@pytest.fixture
def sample_releases():
    """Sample releases data."""
    return [
        {
            "tag_name": "v2.0.0",
            "name": "Version 2.0.0",
            "published_at": "2023-06-01T00:00:00Z",
            "prerelease": False,
        },
        {
            "tag_name": "v1.0.0",
            "name": "Version 1.0.0",
            "published_at": "2023-01-01T00:00:00Z",
            "prerelease": False,
        },
    ]


def test_basic_stats(mock_client, sample_repo_data):
    """Test basic statistics calculation."""
    mock_client.get_repository.return_value = sample_repo_data
    metrics = RepositoryMetrics(mock_client, "owner", "repo")

    stats = metrics.get_basic_stats()

    assert stats["stars"] == 1234
    assert stats["forks"] == 567
    assert stats["watchers"] == 89
    assert stats["open_issues"] == 42
    assert stats["size_kb"] == 5000
    assert stats["default_branch"] == "main"
    assert stats["license"] == "MIT"


def test_basic_stats_no_license(mock_client, sample_repo_data):
    """Test basic stats when there's no license."""
    sample_repo_data["license"] = None
    mock_client.get_repository.return_value = sample_repo_data
    metrics = RepositoryMetrics(mock_client, "owner", "repo")

    stats = metrics.get_basic_stats()
    assert stats["license"] is None


def test_issue_metrics(mock_client, sample_repo_data, sample_issues):
    """Test issue metrics calculation."""
    mock_client.get_repository.return_value = sample_repo_data
    mock_client.get_issues.return_value = sample_issues
    metrics = RepositoryMetrics(mock_client, "owner", "repo")

    issue_stats = metrics.get_issue_metrics()

    # Should exclude the PR (id: 3)
    assert issue_stats["total"] == 2
    assert issue_stats["open"] == 1
    assert issue_stats["closed"] == 1


def test_pr_metrics(mock_client, sample_repo_data, sample_pulls):
    """Test pull request metrics calculation."""
    mock_client.get_repository.return_value = sample_repo_data
    mock_client.get_pulls.return_value = sample_pulls
    metrics = RepositoryMetrics(mock_client, "owner", "repo")

    pr_stats = metrics.get_pr_metrics()

    assert pr_stats["total"] == 3
    assert pr_stats["open"] == 1
    assert pr_stats["closed"] == 2
    assert pr_stats["merged"] == 1
    assert pr_stats["merge_rate_percent"] == 50.0


def test_pr_metrics_no_closed(mock_client, sample_repo_data):
    """Test PR metrics when there are no closed PRs."""
    mock_client.get_repository.return_value = sample_repo_data
    mock_client.get_pulls.return_value = [{"id": 1, "state": "open"}]
    metrics = RepositoryMetrics(mock_client, "owner", "repo")

    pr_stats = metrics.get_pr_metrics()
    assert pr_stats["merge_rate_percent"] == 0


def test_commit_activity(mock_client, sample_repo_data, sample_commits):
    """Test commit activity calculation."""
    mock_client.get_repository.return_value = sample_repo_data
    mock_client.get_commits.return_value = sample_commits
    metrics = RepositoryMetrics(mock_client, "owner", "repo")

    commit_stats = metrics.get_commit_activity(days=90)

    assert commit_stats["total_commits"] == 3
    assert commit_stats["days_analyzed"] == 90
    assert commit_stats["unique_authors"] == 2
    assert commit_stats["commits_per_day"] == pytest.approx(0.03, rel=0.01)


def test_release_info(mock_client, sample_repo_data, sample_releases):
    """Test release information calculation."""
    mock_client.get_repository.return_value = sample_repo_data
    mock_client.get_releases.return_value = sample_releases
    metrics = RepositoryMetrics(mock_client, "owner", "repo")

    release_stats = metrics.get_release_info()

    assert release_stats["total_releases"] == 2
    assert release_stats["latest_release"]["tag"] == "v2.0.0"
    assert release_stats["latest_release"]["name"] == "Version 2.0.0"
    assert release_stats["avg_days_between_releases"] is not None


def test_release_info_no_releases(mock_client, sample_repo_data):
    """Test release info when there are no releases."""
    mock_client.get_repository.return_value = sample_repo_data
    mock_client.get_releases.return_value = []
    metrics = RepositoryMetrics(mock_client, "owner", "repo")

    release_stats = metrics.get_release_info()

    assert release_stats["total_releases"] == 0
    assert release_stats["latest_release"] is None
    assert release_stats["avg_days_between_releases"] is None


def test_release_info_single_release(mock_client, sample_repo_data, sample_releases):
    """Test release info with only one release."""
    mock_client.get_repository.return_value = sample_repo_data
    mock_client.get_releases.return_value = [sample_releases[0]]
    metrics = RepositoryMetrics(mock_client, "owner", "repo")

    release_stats = metrics.get_release_info()

    assert release_stats["total_releases"] == 1
    assert release_stats["avg_days_between_releases"] is None


def test_get_all_metrics(
    mock_client,
    sample_repo_data,
    sample_issues,
    sample_pulls,
    sample_commits,
    sample_releases,
):
    """Test getting all metrics together."""
    mock_client.get_repository.return_value = sample_repo_data
    mock_client.get_issues.return_value = sample_issues
    mock_client.get_pulls.return_value = sample_pulls
    mock_client.get_commits.return_value = sample_commits
    mock_client.get_releases.return_value = sample_releases
    mock_client.get_branch_protection.return_value = {"enabled": True}

    metrics = RepositoryMetrics(mock_client, "owner", "repo")
    all_metrics = metrics.get_all_metrics()

    assert all_metrics["repository"] == "owner/repo"
    assert "basic" in all_metrics
    assert "issues" in all_metrics
    assert "pull_requests" in all_metrics
    assert "commits" in all_metrics
    assert "releases" in all_metrics
    assert "branch_protection" in all_metrics
    assert all_metrics["branch_protection"]["is_protected"] is True


def test_generate_summary(
    mock_client,
    sample_repo_data,
    sample_issues,
    sample_pulls,
    sample_commits,
    sample_releases,
):
    """Test summary generation."""
    mock_client.get_repository.return_value = sample_repo_data
    mock_client.get_issues.return_value = sample_issues
    mock_client.get_pulls.return_value = sample_pulls
    mock_client.get_commits.return_value = sample_commits
    mock_client.get_releases.return_value = sample_releases
    mock_client.get_branch_protection.return_value = None

    metrics = RepositoryMetrics(mock_client, "owner", "repo")
    summary = metrics.generate_summary(max_chars=500)

    assert len(summary) <= 500
    assert "owner/repo" in summary
    assert "1234 stars" in summary
    assert "567 forks" in summary
    assert "MIT" in summary


def test_generate_summary_truncation(
    mock_client,
    sample_repo_data,
    sample_issues,
    sample_pulls,
    sample_commits,
    sample_releases,
):
    """Test summary truncation when it exceeds max_chars."""
    mock_client.get_repository.return_value = sample_repo_data
    mock_client.get_issues.return_value = sample_issues
    mock_client.get_pulls.return_value = sample_pulls
    mock_client.get_commits.return_value = sample_commits
    mock_client.get_releases.return_value = sample_releases
    mock_client.get_branch_protection.return_value = None

    metrics = RepositoryMetrics(mock_client, "owner", "repo")
    summary = metrics.generate_summary(max_chars=50)

    assert len(summary) <= 50
    assert summary.endswith("...")


def test_caching(mock_client, sample_repo_data):
    """Test that data is cached and API calls aren't repeated."""
    mock_client.get_repository.return_value = sample_repo_data
    metrics = RepositoryMetrics(mock_client, "owner", "repo")

    # Call twice
    metrics.get_basic_stats()
    metrics.get_basic_stats()

    # Should only call the API once
    assert mock_client.get_repository.call_count == 1
