# Contributing to Maintainer Metrics

Thank you for your interest in contributing to Maintainer Metrics! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the [issue tracker](https://github.com/lv188669/maintainer-metrics/issues) to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- A detailed description of the proposed feature
- Examples of how the feature would be used
- Why this enhancement would be useful

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install development dependencies**: `pip install -e ".[dev]"`
3. **Make your changes** following our coding standards
4. **Run the test suite**: `pytest`
5. **Check code quality**: `black src tests && ruff check src tests`
6. **Commit your changes** with a clear commit message
7. **Push to your fork** and submit a pull request

## Development Setup

```bash
git clone https://github.com/YOUR-USERNAME/maintainer-metrics.git
cd maintainer-metrics
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
pytest -v
```

## Coding Standards

- Follow PEP 8
- Use Black for code formatting (line length: 100)
- Use Ruff for linting
- Write tests for all new functionality
- Maintain or improve code coverage
- Use type hints and run mypy

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
