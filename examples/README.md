# Grant Summary Examples

This directory contains example outputs from the `maintainer-metrics summary` command, which generates concise plain-text summaries suitable for grant applications with character limits.

## Example 1: Small Repository (lv188669/maintainer-metrics)

```bash
$ maintainer-metrics summary lv188669/maintainer-metrics --max-chars 500
```

**Output:**

```
lv188669/maintainer-metrics: 0 stars, 0 forks. 3 issues (3 open, 0 closed).
2 PRs (1 merged, 100.0% merge rate). 9 commits in last 90 days by 1 authors.
1 releases. Latest: v0.1.0. License: MIT.
```

**Character count:** 194/500

---

## Example 2: Large Repository (django/django)

```bash
$ maintainer-metrics summary django/django --max-chars 500
```

**Output:**

```
django/django: 91562 stars, 37211 forks. 1000 PRs (348 merged, 45.7% merge
rate). 233 commits in last 90 days by 63 authors. License: BSD-3-Clause.
```

**Character count:** 147/500

---

## Usage Tips

1. **Adjust character limits** based on your grant application requirements:
   ```bash
   maintainer-metrics summary owner/repo --max-chars 300
   ```

2. **Use authentication** for higher API rate limits:
   ```bash
   export GITHUB_TOKEN="your_token_here"
   maintainer-metrics summary owner/repo
   ```

3. **Copy plain text** directly into grant applications without the formatting box.

## What's Included

The summary automatically includes:
- Repository name and basic stats (stars, forks)
- Issue metrics (total, open, closed)
- Pull request metrics (total, merged, merge rate)
- Recent commit activity (last 90 days, unique authors)
- Release information (total releases, latest version)
- License type

All within your specified character limit for convenient copy-paste into grant forms.
