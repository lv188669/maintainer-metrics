# maintainer-metrics

[![CI](https://github.com/lv188669/maintainer-metrics/actions/workflows/ci.yml/badge.svg)](https://github.com/lv188669/maintainer-metrics/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python CLI tool that reports open-source maintainer health metrics useful for grant applications and repository triage.

## Features

- ⭐ Repository statistics (stars, forks, watchers)
- 📊 Issue and PR metrics with merge rates
- 🔄 Recent commit activity and contributor counts
- 📦 Release cadence and version tracking
- 🛡️ Branch protection status (when available)
- 📝 Plain-text summaries for grant applications (character-limited)
- 🎨 Rich terminal output with color formatting
- 🔌 Works with or without GitHub authentication

## Installation

```bash
pip install git+https://github.com/lv188669/maintainer-metrics.git
```

Or clone and install locally:

```bash
git clone https://github.com/lv188669/maintainer-metrics.git
cd maintainer-metrics
pip install -e .
```

## Usage

### Check Repository Metrics

Get detailed metrics for any public repository:

```bash
maintainer-metrics check python/cpython
```

Output includes:
- Basic statistics (stars, forks, watchers, size, license)
- Issue counts (total, open, closed)
- Pull request metrics (total, open, closed, merged, merge rate)
- Recent commit activity (last 90 days)
- Release information
- Branch protection status

### Generate Summary for Grants

Generate a concise plain-text summary suitable for grant applications:

```bash
maintainer-metrics summary python/cpython
```

Customize character limit:

```bash
maintainer-metrics summary python/cpython --max-chars 300
```

### JSON Output

Get metrics as JSON for integration with other tools:

```bash
maintainer-metrics check python/cpython --json-output
```

### Check Rate Limits

Monitor your GitHub API rate limit:

```bash
maintainer-metrics rate-limit
```

## Authentication

For higher API rate limits, provide a GitHub personal access token:

```bash
export GITHUB_TOKEN="your_token_here"
maintainer-metrics check owner/repo
```

Or pass it directly:

```bash
maintainer-metrics check owner/repo --token YOUR_TOKEN
```

## Example Output

```bash
$ maintainer-metrics check django/django
```

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                 Repository Metrics                   ┃
┃                    django/django                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

               Basic Statistics                
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ⭐ Stars        │ 75,234                  ┃
┃ 🍴 Forks        │ 30,456                  ┃
┃ 👀 Watchers     │ 3,210                   ┃
┃ 📜 License      │ BSD-3-Clause            ┃
┗━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Development

### Setup

```bash
git clone https://github.com/lv188669/maintainer-metrics.git
cd maintainer-metrics
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest -v
```

### Code Quality

```bash
black src tests
ruff check src tests
mypy src
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Royce Generoso ([@lv188669](https://github.com/lv188669))

## Acknowledgments

Built with:
- [requests](https://requests.readthedocs.io/) - HTTP library
- [click](https://click.palletsprojects.com/) - CLI framework
- [rich](https://rich.readthedocs.io/) - Terminal formatting
