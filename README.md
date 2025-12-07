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

### AI PR Workflows

Automated workflows that leverage AI to enhance pull request processes, including:
- Automated code reviews
- PR description generation
- Code quality analysis
- Automated testing and validation

## Testing

The repository includes comprehensive test workflows for validating the quality gates:

- **`test-quality-gate-mock.yml`**: Tests the Python Quality Gate workflow
- **`test-review-gate-mock.yml`**: Tests the Python Review Gate workflow

**Running Tests Locally:**

```bash
# Install act (GitHub Actions runtime simulator)
brew install act  # macOS
# or
pacman -S act     # Linux (Arch)

# Run quality gate tests
act -W .github/workflows/test-quality-gate-mock.yml workflow_dispatch \
  --secret ANTHROPIC_API_KEY=mock-key

# Run review gate tests
act -W .github/workflows/test-review-gate-mock.yml workflow_dispatch \
  --secret ANTHROPIC_API_KEY=mock-key
```

For detailed testing instructions, see [TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md)

For test results and validation details, see [TEST_REPORT.md](TEST_REPORT.md)

## Usage

To use these shared workflows in your WasteHero project, reference them in your repository's workflow file:

```yaml
name: My Workflow
on: [pull_request]

jobs:
  call-shared-workflow:
    uses: WasteHero/wh-github-actions/.github/workflows/workflow-name.yml@main
    secrets: inherit
```

## Contributing

When adding or modifying workflows:
1. Ensure workflows are generalized for use across multiple projects
2. Document any required secrets or inputs
3. Test changes thoroughly before merging to main
4. Update this README with new workflow documentation

## Support

For questions or issues with these workflows, please contact the DevOps team or open an issue in this repository.
