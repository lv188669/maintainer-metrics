"""Tests for GitHub client."""

import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from maintainer_metrics.client import GitHubClient


@pytest.fixture
def mock_response():
    """Create a mock response."""
    response = MagicMock()
    response.json.return_value = {"test": "data"}
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def client():
    """Create a GitHubClient instance without token."""
    with patch.dict(os.environ, {}, clear=True):
        return GitHubClient()


def test_client_initialization_without_token():
    """Test client initialization without token."""
    with patch.dict(os.environ, {}, clear=True):
        client = GitHubClient()
        assert client.token is None
        assert "Authorization" not in client.session.headers


def test_client_initialization_with_token():
    """Test client initialization with explicit token."""
    client = GitHubClient(token="test_token")
    assert client.token == "test_token"
    assert client.session.headers["Authorization"] == "Bearer test_token"


def test_client_initialization_with_env_token():
    """Test client initialization with environment token."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
        client = GitHubClient()
        assert client.token == "env_token"
        assert client.session.headers["Authorization"] == "Bearer env_token"


def test_get_repository(client, mock_response):
    """Test getting repository information."""
    with patch.object(client.session, "get", return_value=mock_response):
        result = client.get_repository("owner", "repo")
        assert result == {"test": "data"}
        client.session.get.assert_called_once()


def test_get_issues(client, mock_response):
    """Test getting repository issues."""
    mock_response.json.return_value = [{"id": 1}, {"id": 2}]
    with patch.object(client.session, "get", return_value=mock_response):
        result = client.get_issues("owner", "repo")
        assert len(result) == 2
        assert result[0]["id"] == 1


def test_get_pulls(client, mock_response):
    """Test getting pull requests."""
    mock_response.json.return_value = [{"id": 1, "number": 1}]
    with patch.object(client.session, "get", return_value=mock_response):
        result = client.get_pulls("owner", "repo")
        assert len(result) == 1
        assert result[0]["number"] == 1


def test_get_commits(client, mock_response):
    """Test getting commits."""
    mock_response.json.return_value = [{"sha": "abc123"}]
    with patch.object(client.session, "get", return_value=mock_response):
        result = client.get_commits("owner", "repo")
        assert len(result) == 1
        assert result[0]["sha"] == "abc123"


def test_get_releases(client, mock_response):
    """Test getting releases."""
    mock_response.json.return_value = [{"tag_name": "v1.0.0"}]
    with patch.object(client.session, "get", return_value=mock_response):
        result = client.get_releases("owner", "repo")
        assert len(result) == 1
        assert result[0]["tag_name"] == "v1.0.0"


def test_get_branch_protection_success(client, mock_response):
    """Test getting branch protection when it exists."""
    mock_response.json.return_value = {"enabled": True}
    with patch.object(client.session, "get", return_value=mock_response):
        result = client.get_branch_protection("owner", "repo", "main")
        assert result == {"enabled": True}


def test_get_branch_protection_not_found(client):
    """Test getting branch protection when it doesn't exist."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    error = requests.HTTPError()
    error.response = mock_response
    mock_response.raise_for_status.side_effect = error

    with patch.object(client.session, "get", return_value=mock_response):
        result = client.get_branch_protection("owner", "repo", "main")
        assert result is None


def test_get_rate_limit(client, mock_response):
    """Test getting rate limit information."""
    mock_response.json.return_value = {"resources": {"core": {"limit": 5000}}}
    with patch.object(client.session, "get", return_value=mock_response):
        result = client.get_rate_limit()
        assert "resources" in result


def test_http_error_handling(client):
    """Test HTTP error handling."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError("Server error")

    with patch.object(client.session, "get", return_value=mock_response):
        with pytest.raises(requests.HTTPError):
            client.get_repository("owner", "repo")


def test_pagination_issues(client):
    """Test issue pagination."""
    # First page: 100 items, second page: 50 items
    response1 = MagicMock()
    response1.json.return_value = [{"id": i} for i in range(100)]
    response1.raise_for_status.return_value = None

    response2 = MagicMock()
    response2.json.return_value = [{"id": i} for i in range(100, 150)]
    response2.raise_for_status.return_value = None

    with patch.object(client.session, "get", side_effect=[response1, response2]):
        result = client.get_issues("owner", "repo")
        assert len(result) == 150
