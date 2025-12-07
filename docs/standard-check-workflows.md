# Standard Python Check Workflows

This document describes the standard Python check workflows (CT-1166 Phase 3) that provide foundational code quality, type safety, and security checks for WasteHero Python projects.

## Overview

The standard check workflows are designed to be reusable, composable building blocks that can be called individually or combined to create comprehensive CI/CD pipelines. They follow GitHub Actions best practices and are optimized for execution on self-hosted Kubernetes runners.

## Workflows

### 1. Python Lint (`python-lint.yml`)

**CT-1180 Subtask**: Static code analysis and formatting validation

**Purpose**: Enforce code style consistency and identify common code quality issues using Ruff.

**Trigger**: `workflow_call` (reusable workflow)

**Runs On**: `[self-hosted, linux, X64, kubernetes]`

**Permissions**:
- `contents: read` - Read repository code
- `pull-requests: write` - Write comments to pull requests

**Actions Used**:
- `actions/checkout@v4` - Clone repository
- `astral-sh/ruff-action@v3` - Official Ruff linting and formatting action

**Checks Performed**:
1. **Linting**: `ruff check --output-format=github`
   - Detects PEP 8 violations
   - Identifies unused imports and variables
   - Reports circular imports and other structural issues
   - Output formatted as GitHub annotations for inline PR comments

2. **Formatting**: `ruff format --check`
   - Validates code matches Ruff's formatting standards
   - No changes made, only validation (--check flag)
   - Helps ensure consistency across the codebase

**Usage Example**:
```yaml
name: My Python Lint Check
on: [pull_request]

jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

**Secrets Required**: None

**Notes**:
- Uses official Ruff GitHub Action (not a custom action)
- Does not modify files, only validates
- Reports issues as GitHub annotations for inline PR feedback
- Fast execution, no dependency installation required

---

### 2. Python Type Check (`python-type-check.yml`)

**CT-1181 Subtask**: Static type validation with pyright/mypy

**Purpose**: Validate Python type hints and catch type-related errors using configured type checker (pyright or mypy).

**Trigger**: `workflow_call` (reusable workflow)

**Runs On**: `[self-hosted, linux, X64, kubernetes]`

**Permissions**:
- `contents: read` - Read repository code

**Composite Actions Used**:
- `./.github/actions/setup-python-env` - Setup Python 3.13 with UV package manager and caching

**Secrets Required**:
- `UV_INDEX_WASTEHERO_USERNAME` - Username for WasteHero private PyPI index
- `UV_INDEX_WASTEHERO_PASSWORD` - Password for WasteHero private PyPI index

**Steps**:
1. Checkout code
2. Setup Python environment using composite action
3. Install project dependencies with UV:
   ```bash
   uv sync --extra-index-url https://$USERNAME:$PASSWORD@pypi.wastehero.io/team/wastehero_libraries/+simple/
   ```
4. Run type checker:
   ```bash
   uv run ty
   ```

**Type Checker Configuration**:
- The `uv run ty` command executes the type checker defined in `pyproject.toml`
- Typically uses either Pyright or Mypy (configured in project)
- Validates type annotations against actual code usage
- Reports type mismatches and incomplete annotations

**Usage Example**:
```yaml
name: My Python Type Check
on: [pull_request]

jobs:
  type-check:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

**Requirements**:
- Project must have UV configured with type checker dependency
- `uv run ty` command must be defined in `pyproject.toml`
- WasteHero PyPI credentials must be available as repository secrets

**Notes**:
- Leverages UV's efficient dependency management
- Caches Python and UV dependencies for faster subsequent runs
- Supports both public and private WasteHero package dependencies
- Type checking failure prevents merge (when used in required checks)

---

### 3. Python Security Audit (`python-security-audit.yml`)

**CT-1182 Subtask**: Security vulnerability scanning and code security analysis

**Purpose**: Scan Python code for security vulnerabilities and unsafe patterns using Ruff's security rules.

**Trigger**: `workflow_call` (reusable workflow)

**Runs On**: `[self-hosted, linux, X64, kubernetes]`

**Permissions**:
- `contents: read` - Read repository code
- `security-events: write` - Create security alerts and events

**Composite Actions Used**:
- `./.github/actions/setup-python-env` - Setup Python 3.13 with UV package manager and caching

**Secrets Required**:
- `UV_INDEX_WASTEHERO_USERNAME` - Username for WasteHero private PyPI index
- `UV_INDEX_WASTEHERO_PASSWORD` - Password for WasteHero private PyPI index

**Steps**:
1. Checkout code
2. Setup Python environment using composite action
3. Install project dependencies with UV:
   ```bash
   uv sync --extra-index-url https://$USERNAME:$PASSWORD@pypi.wastehero.io/team/wastehero_libraries/+simple/
   ```
4. Run security audit:
   ```bash
   uv run ruff check --select=S
   ```

**Security Checks Performed**:
- Hardcoded passwords and secrets detection
- SQL injection vulnerabilities
- Insecure deserialization (pickle)
- Use of insecure cryptographic functions
- Insecure temporary file creation
- Unsafe YAML loading
- Dangerous system calls
- Other OWASP Top 10 related issues

The `--select=S` flag selects only Ruff's security rules (S001-S699).

**Usage Example**:
```yaml
name: My Python Security Audit
on: [pull_request]

jobs:
  security-audit:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-security-audit.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

**Requirements**:
- Project must have UV configured with dependencies
- WasteHero PyPI credentials must be available as repository secrets
- Dependencies must be installed to analyze security issues accurately

**Notes**:
- Can create GitHub security alerts (with `security-events: write` permission)
- Security audit failure blocks merge (when used in required checks)
- Complements static analysis with security-specific scanning
- Helps maintain compliance with security best practices

---

## Combining Workflows

These standard check workflows can be combined to create comprehensive CI pipelines. Example:

```yaml
name: Python Quality Checks
on: [pull_request]

jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main

  type-check:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}

  security-audit:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-security-audit.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

## Repository Secrets Required

To use the type check and security audit workflows, configure the following secrets in your repository:

**Settings > Secrets and variables > Actions**

| Secret | Description | Example |
|--------|-------------|---------|
| `UV_INDEX_WASTEHERO_USERNAME` | Username for WasteHero private PyPI index | `your-username` |
| `UV_INDEX_WASTEHERO_PASSWORD` | Password/token for WasteHero private PyPI index | `ghp_xxxxxxxxxxxx` |

## Best Practices

1. **Execution Order**: Run lint checks first (fast, no dependencies), then type checks and security audits (slower, require dependencies)

2. **Required Checks**: Mark workflows as required checks in branch protection rules to enforce code quality standards

3. **Concurrency**: Use concurrency groups to cancel superseded runs:
   ```yaml
   concurrency:
     group: checks-${{ github.ref }}-${{ github.event_name }}
     cancel-in-progress: true
   ```

4. **Failure Handling**:
   - Lint failures should block merges
   - Type check failures should block merges
   - Security audit findings should be reviewed and resolved before merge

5. **Local Testing**: Test workflows locally with `act` before pushing:
   ```bash
   # Test lint workflow
   act -W .github/workflows/core/python-lint.yml

   # Test type check (requires secrets)
   act -W .github/workflows/core/python-type-check.yml \
     --secret UV_INDEX_WASTEHERO_USERNAME=user \
     --secret UV_INDEX_WASTEHERO_PASSWORD=pass
   ```

## Related Workflows

- **Python Quality Gate** (`python-quality-gate.yml`): AI-powered code quality analysis using Claude
- **Python Review Gate** (`python-review-gate.yml`): Comprehensive code review using Claude AI

## Troubleshooting

### Type Check Fails with "Module not found"
- Verify WasteHero PyPI credentials are configured
- Check that `pyproject.toml` includes all required dependencies
- Ensure UV index URL is correct in the workflow

### Security Audit Reports False Positives
- Review Ruff security rule documentation: https://docs.astral.sh/ruff/rules/#security-s
- Suppress specific issues with `# noqa: S602` (for security rule S602)
- Update security rules configuration in `pyproject.toml`

### Workflows Not Triggering
- Verify the calling workflow uses `workflow_call` event
- Check workflow file is on the correct branch
- Ensure file paths use `.github/workflows/core/` prefix

## Version Management

- `@main` - Uses latest version from main branch (recommended for flexibility)
- `@v1.0` - Uses specific release tag (recommended for stability)
- `@commit-sha` - Uses specific commit (maximum control)

## See Also

- [GitHub Actions Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [UV Package Manager](https://astral.sh/blog/uv-python-packaging-revolution)
- [AI Quality Gates Documentation](./AI_QUALITY_GATES.md)
