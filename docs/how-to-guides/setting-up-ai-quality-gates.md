# Setting Up AI-Powered Quality Gates

## Overview

This guide walks you through enabling AI-powered quality gates (Python Quality Gate and Python Review Gate) in your project's CI/CD pipeline.

## Prerequisites

- Repository with Python code
- Admin access to repository settings
- GitHub Actions enabled
- WasteHero GitHub Actions shared workflows accessible

## Step 1: Set Up the ANTHROPIC_API_KEY Secret

AI quality gates require an Anthropic API key to run Claude models.

### Option A: Repository Secrets (Single Repository)

If you want this secret only for one repository:

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Select **Secrets and variables** > **Actions** (left sidebar)
4. Click **New repository secret**
5. Name: `ANTHROPIC_API_KEY`
6. Value: Paste your API key from [https://console.anthropic.com](https://console.anthropic.com)
7. Click **Add secret**

### Option B: Organization Secrets (All Repositories)

If you want all your repositories to have access:

1. Go to your GitHub organization
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New organization secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: Paste your API key
6. Under "Repository access": Select "All repositories" or specific ones
7. Click **Add secret**

### Getting Your API Key

If you don't have an API key yet:

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in or create an account
3. Navigate to API keys
4. Click "Create key"
5. Copy the key immediately (it won't be shown again)

## Step 2: Create or Update Your Workflow File

Add the AI quality gates to your project's workflow file.

### Option A: Add to Existing Workflow

If you already have a `.github/workflows/main.yml` file:

1. Open `.github/workflows/main.yml`
2. Add the jobs for quality gates (see examples below)
3. Add `needs:` dependencies if using other jobs
4. Commit and push

### Option B: Create New Workflow

Create a new file `.github/workflows/python-quality.yml`:

```yaml
name: Python Quality Checks

on:
  pull_request:
    branches: [main]

jobs:
  # INFORMATIONAL: Non-blocking feedback
  claude-review:
    uses: WasteHero/wastehero-github-actions/.github/workflows/ai/claude-pr-review.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  # BLOCKING: Quality enforcement
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  # BLOCKING: Comprehensive review
  review-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-review-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Step 3: Configure Gates

### Blocking Gates Only (Strict Quality)

If you only want to enforce quality standards without the learning-focused feedback:

```yaml
jobs:
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  review-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-review-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Informational Only (Learning-Focused)

If you only want feedback without blocking PRs:

```yaml
jobs:
  claude-review:
    uses: WasteHero/wastehero-github-actions/.github/workflows/ai/claude-pr-review.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Full Pipeline (All Gates + Standard Checks)

Complete example with AI gates, standard checks, and tests:

```yaml
name: Comprehensive Python CI

on:
  pull_request:
    branches: [main]

jobs:
  # INFORMATIONAL: Non-blocking feedback
  claude-review:
    uses: WasteHero/wastehero-github-actions/.github/workflows/ai/claude-pr-review.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  # BLOCKING: Quality enforcement (gates Phase 1)
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  review-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-review-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  # STANDARD CHECKS: Phase 2 (run after gates pass)
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

  # TESTS: Phase 3 (run after standard checks pass)
  tests:
    needs: [lint, type-check, security-audit]
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

## Step 4: Test Your Configuration

### Verify Secrets Are Set

1. Go to your repository Settings > Secrets and variables > Actions
2. Confirm `ANTHROPIC_API_KEY` is listed
3. Confirm it has a green checkmark

### Test Locally (Optional)

Use [act](https://github.com/nektos/act) to test workflows locally:

```bash
# List available workflows
act -l

# Run a specific workflow
act workflow_call -j python-quality-gate -s ANTHROPIC_API_KEY=sk-ant-...
```

### Test on a PR

The easiest way to test:

1. Push a branch with a simple change
2. Create a pull request
3. Watch GitHub Actions run
4. Check PR comments for feedback

## Step 5: Understanding Gate Results

### Quality Gate Passes

If the quality gate passes, you'll see:

```
## Python Quality Gate Analysis

✅ No quality issues found

The code meets quality standards and is ready for further checks.
```

### Quality Gate Fails

If the quality gate finds issues, you'll see:

```
## Python Quality Gate Analysis

Issues found in code quality analysis:

1. **Potential Logic Error** (my_module/handler.py:45-52)
   - The error handling catches all exceptions but only logs some
   - Risk: Unexpected exceptions could fail silently
   - Fix: Catch specific exception types or add more detailed logging

2. **Performance Issue** (my_module/data.py:120)
   - The `fetch_data()` function is called 3 times in `process()`
   - Risk: Wasted API calls and slower execution
   - Fix: Cache the result or restructure the code

PR will not merge until these issues are addressed.
```

When the gate fails:

1. Read the findings in the PR comment
2. Address each issue in your code
3. Push fixes to the same PR branch
4. Quality gate will automatically re-run
5. Once fixed, continue with other checks

### Review Gate Fails

The review gate provides more comprehensive feedback:

```
## Python Code Review

### Code Quality Issues
- [Issue 1 description]

### Performance Concerns
- [Issue 1 description]

### Security Considerations
- [Issue 1 description]

### Testing & Coverage
- [Issue 1 description]

PR will not merge until these items are reviewed and addressed.
```

### Claude PR Review (Informational)

Even if gates pass, Claude PR Review provides non-blocking suggestions:

```
## Claude PR Review

Great work on this PR! Here are some observations:

### Code Quality
- The function `validate_input()` could handle edge cases better
  - Suggestion: Add checks for None values

### Performance
- The list comprehension in line 45 could be optimized
  - Suggestion: Use built-in functions instead

### Well Done
- Excellent test coverage
- Clear variable naming throughout
- Good use of type hints
```

## Step 6: Make Quality Gates Required (Optional)

To prevent PRs from merging without passing quality gates:

1. Go to repository **Settings** > **Branches** > **Branch protection rules**
2. Edit your main branch rule
3. Under "Require status checks to pass before merging"
4. Search for and select:
   - `quality-gate` (if using)
   - `review-gate` (if using)
5. Save changes

Now PRs cannot merge without passing the gates.

## Troubleshooting

### Workflow Not Triggering

**Problem**: Quality gate workflow doesn't run on PR creation.

**Solutions**:
- Verify workflow file is in `.github/workflows/` directory
- Confirm GitHub Actions is enabled in Settings > Actions
- Check that the branch reference in `uses:` is correct
- Wait a few seconds - workflows sometimes have a slight delay

### API Key Error

**Problem**: Workflow fails with "API key not found" or authentication error.

**Solutions**:
- Verify secret name is exactly `ANTHROPIC_API_KEY` (case-sensitive)
- Confirm secret is set in repository (Settings > Secrets)
- Verify API key is valid and not expired
- Check quota on Anthropic console
- If using organization secrets, confirm repository has access

### Claude Code Action Not Found

**Problem**: Error about missing `claude-code-action`.

**Solutions**:
- Verify workflow uses official action: `anthropics/claude-code-action@v1`
- Check that action version is compatible with your GitHub Actions setup
- Review Claude Code action docs: https://github.com/anthropics/claude-code-action

### Workflow Runs But Always Fails

**Problem**: Quality gate runs but always fails, even on good code.

**Solutions**:
- Check PR comment for specific findings
- Review Claude's analysis - it explains what to fix
- Test with a simpler change (e.g., just docs)
- Check GitHub Actions logs for error details
- Ensure Python files follow reasonable standards

### Slow or Timeout

**Problem**: Quality gates take too long or timeout.

**Solutions**:
- This is normal - gates take 30-120 seconds
- GitHub has a 6-hour timeout, which is more than enough
- If consistently timing out, check GitHub status page
- Review Anthropic API status: https://status.anthropic.com

## Cost Monitoring

AI quality gates use Anthropic API, which has a cost:

- **Quality Gate**: ~$0.07 per PR
- **Review Gate**: ~$0.15 per PR
- **PR Review**: ~$0.03 per PR (if using informational)

### Monitor Your Usage

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Check "Usage" dashboard
3. Review API costs for your account

### Reduce Costs

If costs are higher than expected:

1. Use informational gates only (no blocking)
2. Disable Custom Agent (only use when needed)
3. Run gates only on main branch, not all PRs
4. Use `workflow_dispatch` for manual runs instead of automatic

## Next Steps

- **To understand gate strategy**: Read [AI Gates Strategy](/docs/explanation/ai-gates-strategy.md)
- **For detailed specifications**: See reference documentation
- **To understand the full pipeline**: Read [Three-Phase Pipeline Model](/docs/explanation/three-phase-pipeline-model.md)
- **For troubleshooting help**: Check [Debugging Workflow Failures](/docs/how-to-guides/debugging-workflow-failures.md)

## Related Documentation

- [Python Quality Gate Reference](/docs/reference/python-quality-gate-workflow.md)
- [Python Review Gate Reference](/docs/reference/python-review-gate-workflow.md)
- [Required Secrets Reference](/docs/reference/required-secrets.md)
