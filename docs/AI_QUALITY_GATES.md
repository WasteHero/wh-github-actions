# AI-Powered Quality Gate Workflows

## Overview

This document describes the AI-powered quality gate workflows for WasteHero's CI/CD pipeline. These workflows use Claude Code to perform automated code quality analysis and comprehensive code reviews on Python projects.

## Workflows

### 1. Python Quality Gate (`python-quality-gate.yml`)

**Reference**: CT-1179

Performs automated code quality analysis using Claude's `@agent-py-quality` tool.

#### Trigger
- `workflow_call`: Reusable workflow for use in other repositories

#### Configuration
- **Runs on**: `[self-hosted, linux, X64, kubernetes]`
- **Model**: Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- **Max turns**: 3
- **Required Secret**: `ANTHROPIC_API_KEY`

#### Permissions
```yaml
contents: read
pull-requests: write
```

#### Behavior
1. Checks out code with full history (`fetch-depth: 0`)
2. Runs Claude Code action with `@agent-py-quality` prompt
3. Posts quality analysis findings as PR comment
4. **Fails workflow if issues are found** (blocking gate)
5. Passes only if output contains "No quality issues found"

#### Usage in Consumer Repositories

Add to your workflow file:

```yaml
jobs:
  quality-gate:
    uses: WasteHero/wh-github-actions/.github/workflows/core/python-quality-gate.yml@feature/CT-1166-foundation-workflows
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### 2. Python Review Gate (`python-review-gate.yml`)

**Reference**: CT-1183

Performs comprehensive code review using Claude's `@agent-py-reviewer` tool.

#### Trigger
- `workflow_call`: Reusable workflow for use in other repositories

#### Configuration
- **Runs on**: `[self-hosted, linux, X64, kubernetes]`
- **Model**: Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- **Max turns**: 5
- **Required Secret**: `ANTHROPIC_API_KEY`

#### Permissions
```yaml
contents: read
pull-requests: write
```

#### Review Focus Areas
- Code quality and best practices
- Performance issues
- Security vulnerabilities
- Test coverage

#### Behavior
1. Checks out code with full git history (`fetch-depth: 0`)
2. Runs Claude Code action with `@agent-py-reviewer` prompt
3. Posts review findings as PR comment organized by category
4. **Fails workflow if issues are found** (blocking gate)
5. Passes only if output contains "No significant issues found in code review"

#### Usage in Consumer Repositories

Add to your workflow file:

```yaml
jobs:
  review-gate:
    uses: WasteHero/wh-github-actions/.github/workflows/core/python-review-gate.yml@feature/CT-1166-foundation-workflows
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Integration Example

Complete workflow example using both gates:

```yaml
name: Python CI with AI Gates

on:
  pull_request:
    branches: [main]

jobs:
  quality-gate:
    uses: WasteHero/wh-github-actions/.github/workflows/core/python-quality-gate.yml@feature/CT-1166-foundation-workflows
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  review-gate:
    uses: WasteHero/wh-github-actions/.github/workflows/core/python-review-gate.yml@feature/CT-1166-foundation-workflows
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  tests:
    needs: [quality-gate, review-gate]
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: pytest
```

## Required Secrets

Both workflows require the `ANTHROPIC_API_KEY` secret to be configured in the consuming repository.

### Setup Instructions

1. Go to your repository's Settings
2. Navigate to Secrets and variables > Actions
3. Create a new repository secret named `ANTHROPIC_API_KEY`
4. Paste your Anthropic API key from https://console.anthropic.com
5. Click "Add secret"

Alternatively, use organization secrets to share across all WasteHero repositories.

## PR Comments

Both workflows post their findings as comments on pull requests:

### Quality Gate Comment Format
```
## Python Quality Gate Analysis

- Issue description
- File and line number
- How to fix

OR

✅ No quality issues found
```

### Review Gate Comment Format
```
## Python Code Review

- Issue category (Quality/Performance/Security/Testing)
- Issue description
- File and line number
- Recommended fix

OR

✅ No significant issues found in code review
```

## Workflow Exit Behavior

Both workflows use the following logic:

| Condition | Result |
|-----------|--------|
| No issues found | Workflow passes (exit 0) |
| Issues found | Workflow fails (exit 1), blocks subsequent jobs |

This ensures that:
- PR cannot merge until quality gates pass
- Tests and other jobs don't run if quality gates fail
- Issues are clearly documented in PR comments

## Testing Workflows Locally

To test these workflows locally before pushing to the main branch, use [nektos/act](https://github.com/nektos/act):

```bash
# List available workflows
act -l

# Run the quality gate workflow
act workflow_call -j python-quality-gate -s ANTHROPIC_API_KEY=sk-ant-...

# Run the review gate workflow
act workflow_call -j python-review-gate -s ANTHROPIC_API_KEY=sk-ant-...
```

## Troubleshooting

### Workflow Not Triggering
- Ensure the branch reference is correct in the `uses:` statement
- Verify the workflow file exists in the specified path
- Check GitHub Actions is enabled in your repository

### API Key Error
- Verify `ANTHROPIC_API_KEY` secret is configured in the repository
- Ensure the secret name matches exactly (case-sensitive)
- Check that the API key is valid and not expired

### Claude Code Action Not Found
- Verify `anthropics/claude-code-action@v1` is the correct action reference
- Check that the action version is compatible with your GitHub Actions setup

### Gate Always Fails
- Check PR comment for detailed findings
- Review Claude's analysis in the GitHub Actions logs
- Ensure Python files follow project code standards

## Model Version

Both workflows use **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) for optimal performance and cost efficiency in CI/CD environments.

To update the model version:
1. Check https://docs.anthropic.com/en/docs/about-claude/models/all-models for the latest version
2. Update the `--model` parameter in the `claude_args` field
3. Test locally with act before merging
4. Document the change in commit message

## Security Considerations

- API keys are handled securely via GitHub Secrets
- Workflows have minimal required permissions (`contents: read`, `pull-requests: write`)
- No sensitive data is exposed in logs or PR comments
- Claude Code action is pinned to specific version (`@v1`)

## Support

For questions or issues with these workflows:
1. Check the troubleshooting section above
2. Review Claude Code action documentation: https://github.com/anthropics/claude-code-action
3. Contact the DevOps team
4. Open an issue in the wastehero-github-actions repository
