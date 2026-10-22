"""Repository metrics calculation and analysis."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from maintainer_metrics.client import GitHubClient


class RepositoryMetrics:
    """Calculate and analyze repository health metrics."""

    def __init__(self, client: GitHubClient, owner: str, repo: str) -> None:
        """Initialize metrics calculator.

        Args:
            client: GitHubClient instance
            owner: Repository owner
            repo: Repository name
        """
        self.client = client
        self.owner = owner
        self.repo = repo
        self._repo_data: Optional[Dict[str, Any]] = None
        self._issues: Optional[List[Dict[str, Any]]] = None
        self._pulls: Optional[List[Dict[str, Any]]] = None
        self._commits: Optional[List[Dict[str, Any]]] = None
        self._releases: Optional[List[Dict[str, Any]]] = None

    def _fetch_repo_data(self) -> Dict[str, Any]:
        """Fetch repository data (cached)."""
        if self._repo_data is None:
            self._repo_data = self.client.get_repository(self.owner, self.repo)
        return self._repo_data

    def _fetch_issues(self) -> List[Dict[str, Any]]:
        """Fetch all issues (cached)."""
        if self._issues is None:
            self._issues = self.client.get_issues(self.owner, self.repo)
        return self._issues

    def _fetch_pulls(self) -> List[Dict[str, Any]]:
        """Fetch all pull requests (cached)."""
        if self._pulls is None:
            self._pulls = self.client.get_pulls(self.owner, self.repo)
        return self._pulls

    def _fetch_commits(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch commits (cached for same parameters)."""
        if self._commits is None or since:
            self._commits = self.client.get_commits(self.owner, self.repo, since=since)
        return self._commits

    def _fetch_releases(self) -> List[Dict[str, Any]]:
        """Fetch releases (cached)."""
        if self._releases is None:
            self._releases = self.client.get_releases(self.owner, self.repo)
        return self._releases

    def get_basic_stats(self) -> Dict[str, Any]:
        """Get basic repository statistics.

        Returns:
            Dictionary with stars, forks, watchers, open issues count
        """
        repo = self._fetch_repo_data()
        return {
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "watchers": repo.get("subscribers_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "size_kb": repo.get("size", 0),
            "default_branch": repo.get("default_branch", "main"),
            "license": repo.get("license", {}).get("spdx_id") if repo.get("license") else None,
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
            "pushed_at": repo.get("pushed_at"),
        }

    def get_issue_metrics(self) -> Dict[str, Any]:
        """Get issue metrics (excluding PRs).

        Returns:
            Dictionary with open/closed issues, total count
        """
        issues = self._fetch_issues()
        # Filter out pull requests (they have a 'pull_request' key)
        real_issues = [issue for issue in issues if "pull_request" not in issue]

        open_issues = [issue for issue in real_issues if issue.get("state") == "open"]
        closed_issues = [issue for issue in real_issues if issue.get("state") == "closed"]

        return {
            "total": len(real_issues),
            "open": len(open_issues),
            "closed": len(closed_issues),
        }

    def get_pr_metrics(self) -> Dict[str, Any]:
        """Get pull request metrics.

        Returns:
            Dictionary with open/closed/merged PR counts and merge rate
        """
        pulls = self._fetch_pulls()

        open_prs = [pr for pr in pulls if pr.get("state") == "open"]
        closed_prs = [pr for pr in pulls if pr.get("state") == "closed"]
        merged_prs = [pr for pr in closed_prs if pr.get("merged_at") is not None]

        total_closed = len(closed_prs)
        merge_rate = (len(merged_prs) / total_closed * 100) if total_closed > 0 else 0

        return {
            "total": len(pulls),
            "open": len(open_prs),
            "closed": len(closed_prs),
            "merged": len(merged_prs),
            "merge_rate_percent": round(merge_rate, 1),
        }

    def get_commit_activity(self, days: int = 90) -> Dict[str, Any]:
        """Get recent commit activity.

        Args:
            days: Number of days to look back (default: 90)

        Returns:
            Dictionary with commit counts and activity info
        """
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        since_iso = since_date.isoformat()

        commits = self._fetch_commits(since=since_iso)

        # Get unique authors
        authors = set()
        for commit in commits:
            author = commit.get("author")
            if author and author.get("login"):
                authors.add(author["login"])

        return {
            "total_commits": len(commits),
            "days_analyzed": days,
            "unique_authors": len(authors),
            "commits_per_day": round(len(commits) / days, 2) if days > 0 else 0,
        }

    def get_release_info(self) -> Dict[str, Any]:
        """Get release information.

        Returns:
            Dictionary with release count, latest release, and cadence
        """
        releases = self._fetch_releases()

        latest_release = None
        if releases:
            latest = releases[0]
            latest_release = {
                "tag": latest.get("tag_name"),
                "name": latest.get("name"),
                "published_at": latest.get("published_at"),
                "prerelease": latest.get("prerelease", False),
            }

        # Calculate average release cadence (for repos with 2+ releases)
        avg_days_between_releases = None
        if len(releases) >= 2:
            first_date = datetime.fromisoformat(
                releases[-1].get("published_at", "").replace("Z", "+00:00")
            )
            last_date = datetime.fromisoformat(
                releases[0].get("published_at", "").replace("Z", "+00:00")
            )
            days_span = (last_date - first_date).days
            avg_days_between_releases = round(days_span / (len(releases) - 1), 1)

        return {
            "total_releases": len(releases),
            "latest_release": latest_release,
            "avg_days_between_releases": avg_days_between_releases,
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all repository metrics.

        Returns:
            Dictionary containing all metrics
        """
        basic = self.get_basic_stats()
        issues = self.get_issue_metrics()
        prs = self.get_pr_metrics()
        commits = self.get_commit_activity()
        releases = self.get_release_info()

        # Check branch protection if possible
        branch_protected = None
        default_branch = basic.get("default_branch", "main")
        try:
            protection = self.client.get_branch_protection(self.owner, self.repo, default_branch)
            branch_protected = protection is not None
        except Exception:
            branch_protected = None

        return {
            "repository": f"{self.owner}/{self.repo}",
            "basic": basic,
            "issues": issues,
            "pull_requests": prs,
            "commits": commits,
            "releases": releases,
            "branch_protection": {
                "default_branch": default_branch,
                "is_protected": branch_protected,
            },
        }

    def generate_summary(self, max_chars: int = 500) -> str:
        """Generate a plain-text summary suitable for grant applications.

        Args:
            max_chars: Maximum character limit for summary

        Returns:
            Plain text summary string
        """
        metrics = self.get_all_metrics()
        basic = metrics["basic"]
        issues = metrics["issues"]
        prs = metrics["pull_requests"]
        commits = metrics["commits"]
        releases = metrics["releases"]

        parts = [
            f"{self.owner}/{self.repo}:",
            f"{basic['stars']} stars, {basic['forks']} forks.",
        ]

        if issues["total"] > 0:
            parts.append(
                f"{issues['total']} issues ({issues['open']} open, {issues['closed']} closed)."
            )

        if prs["total"] > 0:
            parts.append(
                f"{prs['total']} PRs ({prs['merged']} merged, "
                f"{prs['merge_rate_percent']}% merge rate)."
            )

        if commits["total_commits"] > 0:
            parts.append(
                f"{commits['total_commits']} commits in last {commits['days_analyzed']} days "
                f"by {commits['unique_authors']} authors."
            )

        if releases["total_releases"] > 0:
            parts.append(f"{releases['total_releases']} releases.")
            latest = releases["latest_release"]
            if latest:
                parts.append(f"Latest: {latest['tag']}.")

        if basic["license"]:
            parts.append(f"License: {basic['license']}.")

        summary = " ".join(parts)

        # Truncate if needed
        if len(summary) > max_chars:
            summary = summary[: max_chars - 3] + "..."

        return summary
