"""GitHub API client for fetching repository metrics."""

import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None) -> None:
        """Initialize the GitHub client.

        Args:
            token: Optional GitHub personal access token for higher rate limits.
                   If not provided, will check GITHUB_TOKEN environment variable.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the GitHub API.

        Args:
            endpoint: API endpoint path
            params: Optional query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.HTTPError: If the request fails
        """
        url = urljoin(self.BASE_URL, endpoint)
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information.

        Args:
            owner: Repository owner (user or organization)
            repo: Repository name

        Returns:
            Repository data dictionary
        """
        return self._get(f"/repos/{owner}/{repo}")

    def get_issues(
        self, owner: str, repo: str, state: str = "all", per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """Get repository issues (includes pull requests in GitHub API).

        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state filter (open, closed, all)
            per_page: Number of results per page (max 100)

        Returns:
            List of issue data dictionaries
        """
        issues: List[Dict[str, Any]] = []
        page = 1
        while True:
            batch = self._get(
                f"/repos/{owner}/{repo}/issues",
                params={"state": state, "per_page": per_page, "page": page},
            )
            if not batch:
                break
            issues.extend(batch)
            if len(batch) < per_page:
                break
            page += 1
            if page > 10:  # Limit to 1000 issues to avoid excessive API calls
                break
        return issues

    def get_pulls(
        self, owner: str, repo: str, state: str = "all", per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """Get repository pull requests.

        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state filter (open, closed, all)
            per_page: Number of results per page (max 100)

        Returns:
            List of pull request data dictionaries
        """
        pulls: List[Dict[str, Any]] = []
        page = 1
        while True:
            batch = self._get(
                f"/repos/{owner}/{repo}/pulls",
                params={"state": state, "per_page": per_page, "page": page},
            )
            if not batch:
                break
            pulls.extend(batch)
            if len(batch) < per_page:
                break
            page += 1
            if page > 10:  # Limit to 1000 PRs
                break
        return pulls

    def get_commits(
        self, owner: str, repo: str, since: Optional[str] = None, per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """Get repository commits.

        Args:
            owner: Repository owner
            repo: Repository name
            since: Only commits after this date (ISO 8601 format)
            per_page: Number of results per page (max 100)

        Returns:
            List of commit data dictionaries
        """
        commits: List[Dict[str, Any]] = []
        page = 1
        params: Dict[str, Any] = {"per_page": per_page, "page": page}
        if since:
            params["since"] = since

        while True:
            params["page"] = page
            batch = self._get(f"/repos/{owner}/{repo}/commits", params=params)
            if not batch:
                break
            commits.extend(batch)
            if len(batch) < per_page:
                break
            page += 1
            if page > 5:  # Limit to 500 commits
                break
        return commits

    def get_releases(self, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """Get repository releases.

        Args:
            owner: Repository owner
            repo: Repository name
            per_page: Number of results per page (max 100)

        Returns:
            List of release data dictionaries
        """
        return self._get(f"/repos/{owner}/{repo}/releases", params={"per_page": per_page})  # type: ignore[return-value]

    def get_branch_protection(self, owner: str, repo: str, branch: str) -> Optional[Dict[str, Any]]:
        """Get branch protection rules (may require authentication).

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            Branch protection data or None if not accessible/configured
        """
        try:
            return self._get(f"/repos/{owner}/{repo}/branches/{branch}/protection")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code in (403, 404):
                return None
            raise

    def get_rate_limit(self) -> Dict[str, Any]:
        """Get current API rate limit status.

        Returns:
            Rate limit information
        """
        return self._get("/rate_limit")
