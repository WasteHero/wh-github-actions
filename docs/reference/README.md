# Reference Documentation

Complete technical specifications for all workflows, actions, and configurations.

## Workflows

### AI-Powered Workflows

These workflows use Claude AI for intelligent code analysis:

| Workflow | Reference | Purpose |
|----------|-----------|---------|
| Python Quality Gate | [python-quality-gate-workflow.md](python-quality-gate-workflow.md) | AI code quality analysis |
| Python Review Gate | [python-review-gate-workflow.md](python-review-gate-workflow.md) | Comprehensive code review |

### Standard Check Workflows

Traditional automated code quality checks:

| Workflow | Reference | Purpose |
|----------|-----------|---------|
| Python Lint | [python-lint-workflow.md](python-lint-workflow.md) | Linting and formatting |
| Python Type Check | [python-type-check-workflow.md](python-type-check-workflow.md) | Type validation |
| Python Security Audit | [python-security-audit-workflow.md](python-security-audit-workflow.md) | Security scanning |

## Composite Actions

Reusable action building blocks:

| Action | Reference | Purpose |
|--------|-----------|---------|
| Setup Python Environment | [setup-python-env-action.md](setup-python-env-action.md) | Python + UV setup |
| Wait for Service | [wait-for-service-action.md](wait-for-service-action.md) | Service health checks |

## Configuration

### Secrets

| Secret | Reference | Purpose |
|--------|-----------|---------|
| All Required Secrets | [required-secrets.md](required-secrets.md) | Secret configuration |

## Quick Navigation

### Looking for...

**How to use a specific workflow?**
→ Find it in the Workflows table above and click the reference link

**Parameters and options for a workflow?**
→ Open the workflow reference page (linked above)

**Environment variables?**
→ See the specific workflow reference page

**Inputs and outputs?**
→ See the specific action reference page

**Security configuration?**
→ See [required-secrets.md](required-secrets.md)

## Workflow Specifications

Each workflow reference includes:

- **Purpose** - What the workflow does
- **Trigger** - How it gets invoked
- **Configuration** - Runtime settings
- **Inputs** - Parameters you provide
- **Outputs** - Results it produces
- **Secrets** - Required credentials
- **Permissions** - GitHub permissions needed
- **Usage** - How to call it
- **Behavior** - What happens when it runs
- **Performance** - Typical execution time
- **Troubleshooting** - Common issues

## Action Specifications

Each action reference includes:

- **Description** - What the action does
- **Usage** - How to use it
- **Inputs** - Input parameters
- **Outputs** - Output values
- **Exit Codes** - Success/failure indicators
- **Examples** - Real-world usage

## Secrets Reference

The [required-secrets.md](required-secrets.md) guide includes:

- **Secret name** - Exact name to use
- **Purpose** - What it's used for
- **Used by** - Which workflows need it
- **How to obtain** - Instructions to get it
- **Security notes** - Best practices
- **Troubleshooting** - Common issues

## Common Usage Patterns

### Minimal Pipeline (Lint Only)

```yaml
jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

See: [python-lint-workflow.md](python-lint-workflow.md)

### Complete Quality Pipeline

```yaml
jobs:
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

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

  review:
    needs: [lint, type-check, security-audit]
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-review-gate.yml@main
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### With Service Dependencies

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432

jobs:
  wait-for-db:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: WasteHero/wastehero-github-actions/.github/actions/wait-for-service@main
        with:
          service-type: postgres
          host: localhost
          port: 5432
      - run: echo "PostgreSQL is ready"
```

See: [wait-for-service-action.md](wait-for-service-action.md)

## Version References

### Workflow Versions

Use one of:
- `@main` - Latest version (recommended for active development)
- `@v1.0` - Specific release tag (recommended for stability)
- `@abc123` - Specific commit hash (maximum control)

### Finding Available Versions

Check the [WasteHero GitHub Actions releases](https://github.com/WasteHero/wastehero-github-actions/releases)

## Environment Variables

### Standard Workflow Environment

All workflows have access to standard GitHub variables:
- `${{ github.repository }}` - Owner/repo
- `${{ github.event.pull_request.number }}` - PR number
- `${{ secrets.GITHUB_TOKEN }}` - GitHub token

See specific workflow reference for additional env vars.

## Permissions Reference

### Default Permissions

Most workflows use:
```yaml
permissions:
  contents: read
```

### Workflows with Additional Permissions

| Workflow | Additional | Reason |
|----------|-----------|--------|
| Python Lint | `pull-requests: write` | Posts comments to PR |
| Python Quality Gate | `pull-requests: write` | Posts findings to PR |
| Python Review Gate | `pull-requests: write` | Posts review to PR |
| Python Security Audit | `security-events: write` | Creates security alerts |

## Performance Characteristics

Approximate execution times (on self-hosted K8s runners):

| Workflow | Time | Notes |
|----------|------|-------|
| Python Lint | 30s | No dependencies needed |
| Python Type Check | 60-120s | Includes dependency install |
| Python Security Audit | 60-120s | Includes dependency install |
| Python Quality Gate | 30-60s | Depends on code size |
| Python Review Gate | 60-120s | Depends on code size |

### Cache Performance

With cache hits:
- Type Check: ~45s (down from 120s)
- Security Audit: ~45s (down from 120s)
- Lint: ~20s (already fast)

## File Organization

```
.github/
├── actions/
│   ├── setup-python-env/
│   │   └── action.yml
│   └── wait-for-service/
│       └── action.yml
└── workflows/
    └── core/
        ├── python-lint.yml
        ├── python-type-check.yml
        ├── python-security-audit.yml
        ├── python-quality-gate.yml
        └── python-review-gate.yml
```

## Troubleshooting Quick Reference

| Issue | Reference |
|-------|-----------|
| Workflow not triggering | [Debugging Workflow Failures](../how-to-guides/debugging-workflow-failures.md) |
| Secret not found | [required-secrets.md](required-secrets.md) |
| Authentication failed | [required-secrets.md](required-secrets.md) |
| Slow execution | [python-type-check-workflow.md](python-type-check-workflow.md#performance) |
| False positive findings | [python-security-audit-workflow.md](python-security-audit-workflow.md#suppressing-findings) |

## Links to Detailed References

Ready to dive into the details? Choose your workflow:

1. **[Python Lint Workflow](python-lint-workflow.md)** - Linting and formatting specs
2. **[Python Type Check Workflow](python-type-check-workflow.md)** - Type checking specs
3. **[Python Security Audit Workflow](python-security-audit-workflow.md)** - Security specs
4. **[Python Quality Gate Workflow](python-quality-gate-workflow.md)** - AI quality specs
5. **[Python Review Gate Workflow](python-review-gate-workflow.md)** - AI review specs
6. **[Setup Python Environment Action](setup-python-env-action.md)** - Action specs
7. **[Wait for Service Action](wait-for-service-action.md)** - Service check specs
8. **[Required Secrets](required-secrets.md)** - Secret configuration specs

---

**Looking for how to do something?** Check the [How-To Guides](../how-to-guides/README.md)

**Want to understand the concepts?** Check the [Explanation](../explanation/README.md)

**Getting started?** Check the [Tutorials](../tutorials/README.md)
