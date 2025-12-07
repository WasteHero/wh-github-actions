# Python Lint Workflow Reference

**Reference:** CT-1180
**Status:** Production
**Last Updated:** December 7, 2025

## Overview

The Python Lint workflow performs static code analysis and formatting validation using Ruff.

| Property | Value |
|----------|-------|
| Purpose | Code style and quality |
| Speed | Very Fast (~30s) |
| Dependencies | None |
| Secrets Required | None |
| Permissions Required | contents: read, pull-requests: write |
| File Location | `.github/workflows/core/python-lint.yml` |

## Purpose

Enforce code style consistency and identify common code quality issues:
- **Style**: Detects PEP 8 violations
- **Unused code**: Identifies unused imports and variables
- **Structure**: Finds circular imports and other issues
- **Formatting**: Validates code matches Ruff standards

## Trigger

`workflow_call` - Called as a reusable workflow from other repositories.

## Basic Usage

```yaml
jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

## Inputs

No inputs - uses defaults.

## Secrets

**No secrets required.**

## Configuration

### Runtime

- **Runs on:** `[self-hosted, linux, X64, kubernetes]`
- **Python version:** 3.13 (from system)
- **Timeout:** 5 minutes

### Permissions

```yaml
permissions:
  contents: read
  pull-requests: write
```

## What It Does

### Step 1: Check Out Code
```bash
actions/checkout@v4
```
Clones repository with full history.

### Step 2: Run Ruff Linting
```bash
ruff check --output-format=github
```

Detects code issues and formats output for GitHub annotations.

**Output:** Appears as inline comments on pull requests.

### Step 3: Run Ruff Formatting Check
```bash
ruff format --check
```

Validates code matches Ruff's formatting standards.

Does not modify files (--check flag).

## Ruff Rules

### Linting Rules

The workflow uses Ruff's default rule set, which includes:

| Code | Category | Examples |
|------|----------|----------|
| E | pycodestyle errors | Line too long, indentation |
| W | pycodestyle warnings | Blank lines, whitespace |
| F | Pyflakes | Undefined names, unused imports |
| I | isort | Import sorting |
| N | pep8-naming | Variable naming conventions |
| UP | pyupgrade | Deprecated syntax |
| S | Security | Hardcoded secrets, SQL injection |

Full list: https://docs.astral.sh/ruff/rules/

### Formatting Standards

Ruff format uses:
- **Line length:** 88 characters (Black standard)
- **Indentation:** 4 spaces (PEP 8)
- **Quote style:** Double quotes (configurable)
- **Import order:** isort compatible

## Common Issues and Fixes

### E501: Line Too Long

**Error:**
```
E501 Line too long (100 > 88 characters)
```

**Cause:** Line exceeds 88 character limit

**Fix:**
```python
# Before:
result = my_function(arg1, arg2, arg3, arg4, arg5, arg6)

# After:
result = my_function(
    arg1, arg2, arg3, arg4, arg5, arg6
)
```

### F401: Unused Import

**Error:**
```
F401 'os' imported but unused
```

**Cause:** Import that's never used

**Fix:** Remove the import line

### I001: Import Sorting

**Error:**
```
I001 Import 'sys' not sorted correctly
```

**Cause:** Imports not in proper order (stdlib, third-party, local)

**Fix:**
```python
# Before:
import os
from my_module import something
import sys

# After:
import os
import sys
from my_module import something
```

## Output

### If Successful
Workflow shows green checkmark, no issues found.

### If Failed
Workflow shows red X with details:
- Error messages appear in logs
- Inline comments on PR for each issue
- Summary of total issues

### PR Comments

Example output:
```
python-lint

Files with lint errors:
- myfile.py:5:1 - E501 Line too long
- myfile.py:3:1 - F401 'os' imported but unused

Fix with:
ruff format
ruff check --fix
```

## Fixing Issues Locally

### Automatic Fix

Ruff can fix many issues automatically:

```bash
# Format code
ruff format

# Fix fixable lint issues
ruff check --fix
```

### Manual Review

For issues Ruff can't fix:
```bash
# See all issues
ruff check

# See issues for specific file
ruff check myfile.py
```

Then manually fix based on error messages.

## Performance

- **Typical run:** 25-35 seconds
- **No cache:** 25-35 seconds (consistent, no deps)
- **Variation:** Depends on code size

Large codebases (~10k files) may take up to 1 minute.

## Integration with Other Workflows

### Run First
Place lint first in your pipeline since it's fastest:

```yaml
jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main

  type-check:
    needs: lint
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main

  tests:
    needs: [lint, type-check]
    runs-on: ubuntu-latest
    steps:
      - run: pytest
```

### Blocking Status

Lint failures block PR merge when set as required check in branch protection rules.

## Customization

### Ruff Configuration

Configure Ruff in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100  # Override default 88
target-version = "py313"

[tool.ruff.lint]
select = ["E", "W", "F", "I"]
ignore = ["E501"]  # Ignore line too long

[tool.ruff.format]
quote-style = "single"  # Use single quotes
```

### Suppressing Issues

Suppress specific issues inline:

```python
# Ignore one issue on a line
x = os.system("echo hi")  # noqa: S605

# Ignore all issues on a line
result = some_code()  # noqa

# Ignore in entire file
# ruff: noqa
```

## Troubleshooting

### Workflow Doesn't Run

**Problem:** Workflow created but doesn't appear in Actions tab

**Solution:**
- File must be at `.github/workflows/filename.yml`
- File must be committed to GitHub
- GitHub Actions must be enabled in repository settings

### Unexpected Lint Errors

**Problem:** Code that looks fine fails lint

**Solution:**
- Ruff might have stricter rules than expected
- Review the error message carefully
- Check Ruff rule documentation
- Try `ruff format` to auto-fix many issues

### All Imports Are Flagged

**Problem:** Many I001 (import sorting) errors

**Solution:**
- Run `ruff check --fix` to auto-sort imports
- Or organize manually: stdlib → third-party → local
- Ruff follows isort conventions

## Best Practices

1. **Run locally before pushing** - Catch issues early
2. **Fix automatically when possible** - `ruff format` and `ruff check --fix`
3. **Review manual fixes** - For issues Ruff can't fix automatically
4. **Configure project standards** - Set Ruff config in `pyproject.toml`
5. **Don't suppress without reason** - Only use `# noqa` when justified

## Related Documentation

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [How to Debug Workflow Failures](../how-to-guides/debugging-workflow-failures.md)
- [Configuring Linting Rules](../how-to-guides/configuring-linting-rules.md)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 7, 2025 | Initial release |

---

**Questions?** See [How-To Guides](../how-to-guides/README.md) for common problems.
