# WasteHero GitHub Actions

Shared and reusable GitHub Actions workflows for all WasteHero projects.

## Overview

This repository contains centralized GitHub Actions workflows that can be reused across all WasteHero organization repositories. This approach ensures consistency, reduces duplication, and simplifies maintenance of CI/CD pipelines.

## Workflows

### Core Standard Check Workflows (CT-1166 Phase 3)

Located in `.github/workflows/core/`:

#### Python Lint (`python-lint.yml`) - CT-1180
Static code analysis and formatting validation using Ruff.

**Purpose**: Enforce code style consistency and identify common code quality issues.

**Trigger**: `workflow_call` (reusable workflow)

**Checks:**
- Linting: `ruff check --output-format=github`
- Formatting: `ruff format --check`

**Permissions**: `contents: read`, `pull-requests: write`

**Secrets Required**: None

**Usage:**
```yaml
jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

#### Python Type Check (`python-type-check.yml`) - CT-1181
Static type validation with pyright/mypy.

**Purpose**: Validate Python type hints and catch type-related errors.

**Trigger**: `workflow_call` (reusable workflow)

**Features**: Uses UV for efficient dependency management and caching

**Secrets Required**:
- `UV_INDEX_WASTEHERO_USERNAME`: Username for WasteHero private PyPI
- `UV_INDEX_WASTEHERO_PASSWORD`: Password for WasteHero private PyPI

**Usage:**
```yaml
jobs:
  type-check:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

#### Python Security Audit (`python-security-audit.yml`) - CT-1182
Security vulnerability scanning using Ruff security rules.

**Purpose**: Scan Python code for security vulnerabilities and unsafe patterns.

**Trigger**: `workflow_call` (reusable workflow)

**Checks**: Ruff security rules (S001-S699) including:
- Hardcoded secrets detection
- SQL injection vulnerabilities
- Insecure deserialization
- Unsafe cryptographic functions
- And more OWASP Top 10 related issues

**Permissions**: `contents: read`, `security-events: write`

**Secrets Required**:
- `UV_INDEX_WASTEHERO_USERNAME`: Username for WasteHero private PyPI
- `UV_INDEX_WASTEHERO_PASSWORD`: Password for WasteHero private PyPI

**Usage:**
```yaml
jobs:
  security-audit:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-security-audit.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

For detailed documentation, see [STANDARD_CHECK_WORKFLOWS.md](docs/STANDARD_CHECK_WORKFLOWS.md)

### Core AI Quality Gate Workflows

Located in `.github/workflows/core/`:

#### Python Quality Gate (`python-quality-gate.yml`)
Automated Python code quality analysis using Claude AI.

**Inputs:**
- `project` (string, required): GitHub repository in format "owner/repo"
- `pr-number` (number, required): Pull request number

**Secrets Required:**
- `ANTHROPIC_API_KEY`: API key from console.anthropic.com

**Output:** Posts quality analysis results to PR with issue count and summary

#### Python Review Gate (`python-review-gate.yml`)
Comprehensive Python code review using Claude AI.

**Inputs:**
- `project` (string, required): GitHub repository in format "owner/repo"
- `pr-number` (number, required): Pull request number

**Secrets Required:**
- `ANTHROPIC_API_KEY`: API key from console.anthropic.com

**Output:** Posts code review findings to PR with categorized issues and count

For detailed documentation, see [AI_QUALITY_GATES.md](docs/AI_QUALITY_GATES.md)

## Required Secrets

Configure these secrets in your repository or organization settings (**Settings → Secrets and variables → Actions**):

### 1. ANTHROPIC_API_KEY
**Used by**: AI Quality Gate workflows (`python-quality-gate.yml`, `python-review-gate.yml`)

**Purpose**: Authenticates with Claude AI for automated code quality analysis and review

**How to obtain**:
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Copy the key value

**Scope**: Repository or Organization level

**Required for**:
- `python-quality-gate.yml` - AI-powered quality analysis
- `python-review-gate.yml` - AI-powered code review

---

### 2. UV_INDEX_WASTEHERO_USERNAME
**Used by**: Standard check workflows (`python-type-check.yml`, `python-security-audit.yml`)

**Purpose**: Username for authenticating with WasteHero's private PyPI repository at `pypi.wastehero.io`

**Scope**: Repository or Organization level

**Required for**:
- `python-type-check.yml` - Type checking with dependencies
- `python-security-audit.yml` - Security scanning with dependencies

---

### 3. UV_INDEX_WASTEHERO_PASSWORD
**Used by**: Standard check workflows (`python-type-check.yml`, `python-security-audit.yml`)

**Purpose**: Password/token for authenticating with WasteHero's private PyPI repository

**Scope**: Repository or Organization level

**Required for**:
- `python-type-check.yml` - Type checking with dependencies
- `python-security-audit.yml` - Security scanning with dependencies

---

**Note**: Secrets are automatically inherited by reusable workflows when called with `secrets: inherit` or passed explicitly

## Usage

### Basic Usage

To use these shared workflows in your WasteHero project, reference them in your repository's workflow file:

```yaml
name: My Workflow
on: [pull_request]

jobs:
  call-shared-workflow:
    uses: WasteHero/wastehero-github-actions/.github/workflows/workflow-name.yml@main
    secrets: inherit
```

### Complete CI Pipeline Example

Here's a complete example using all workflows in the correct order:

```yaml
name: Python CI Pipeline

on:
  pull_request:
    branches: [main, develop]

jobs:
  # Phase 1: AI Quality Gate (runs first, blocks everything if issues found)
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  # Phase 2: Standard Checks (run in parallel after quality gate passes)
  lint:
    needs: quality-gate
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main

  type-check:
    needs: quality-gate
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}

  security-audit:
    needs: quality-gate
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-security-audit.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}

  # Phase 3: AI Code Review (runs after standard checks pass)
  code-review:
    needs: [lint, type-check, security-audit]
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-review-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  # Phase 4: Your tests (run after all gates pass)
  tests:
    needs: [code-review]
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - uses: WasteHero/wastehero-github-actions/.github/actions/setup-python-env@main
      - run: uv run pytest
```

## Contributing

When adding or modifying workflows:
1. Ensure workflows are generalized for use across multiple projects
2. Document any required secrets or inputs
3. Test changes thoroughly before merging to main
4. Update this README with new workflow documentation

## Support

For questions or issues with these workflows, please contact the DevOps team or open an issue in this repository.
