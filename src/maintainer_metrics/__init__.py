"""Maintainer Metrics - Health metrics for open-source maintainers."""

__version__ = "0.1.0"
__author__ = "Royce Generoso"
__email__ = "lv188669@users.noreply.github.com"

from maintainer_metrics.client import GitHubClient
from maintainer_metrics.metrics import RepositoryMetrics

__all__ = ["GitHubClient", "RepositoryMetrics", "__version__"]
