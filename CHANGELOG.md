# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-22

### Added
- Initial release of maintainer-metrics
- `check` command for detailed repository metrics
- `summary` command for grant application summaries
- `rate-limit` command to check GitHub API limits
- Support for GitHub REST API with optional authentication
- Rich terminal output with color formatting
- JSON output option for integration
- Metrics tracked:
  - Repository stars, forks, watchers
  - Issue counts (open/closed)
  - Pull request metrics with merge rates
  - Commit activity (last 90 days)
  - Release information and cadence
  - Branch protection status
  - License detection
- Comprehensive test suite with pytest
- GitHub Actions CI workflow
- MIT License
- Documentation (README, basic setup)

[0.1.0]: https://github.com/lv188669/maintainer-metrics/releases/tag/v0.1.0
