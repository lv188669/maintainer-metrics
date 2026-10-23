# Security Policy

## Supported Versions

We actively support the latest released version of `maintainer-metrics`.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in `maintainer-metrics`, please report it responsibly:

### Private Disclosure

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Report via GitHub Security Advisories: [Report a vulnerability](https://github.com/lv188669/maintainer-metrics/security/advisories/new)
3. Or email: lv188669@users.noreply.github.com with subject line `[SECURITY] maintainer-metrics`

### What to Include

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if you have one)

### Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Fix timeline**: Depends on severity
  - Critical: Immediate (hours to days)
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: Next release cycle

### Disclosure Policy

- We will acknowledge your report within 48 hours
- We will coordinate the fix and release with you
- We will credit you in the release notes (unless you prefer to remain anonymous)
- We follow coordinated disclosure: we will not disclose the vulnerability publicly until a fix is released

## Security Best Practices

When using `maintainer-metrics`:

- **Protect your GitHub token**: Never commit tokens to version control
- **Use environment variables**: Store `GITHUB_TOKEN` in environment variables
- **Limit token scope**: Use tokens with minimal required permissions (public_repo read access is sufficient)
- **Rotate tokens regularly**: Generate new tokens periodically
- **Use fine-grained tokens**: GitHub fine-grained personal access tokens are preferred over classic tokens

## Known Security Considerations

- This tool makes authenticated requests to the GitHub API using the provided token
- The tool does not store or transmit tokens anywhere except to GitHub's official API
- All API requests use HTTPS
- No user data is collected or transmitted to third parties

## Dependencies

We use Dependabot to monitor and update dependencies for known vulnerabilities. See `.github/dependabot.yml` for configuration.
