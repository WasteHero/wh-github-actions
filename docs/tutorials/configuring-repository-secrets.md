# Configuring Repository Secrets

**Time to complete: 15 minutes**

## Goal

Learn how to configure GitHub repository secrets required by the shared workflows.

## Why Secrets?

Some workflows need access to private credentials:
- API keys for Claude AI (ANTHROPIC_API_KEY)
- Credentials for WasteHero's private PyPI (UV_INDEX_WASTEHERO_USERNAME, UV_INDEX_WASTEHERO_PASSWORD)

Secrets let you store these securely without putting them in your code or logs.

## Prerequisites

- Write access to your repository's settings
- Required credentials:
  - For AI workflows: Anthropic API key
  - For type check/security audit: WasteHero PyPI credentials

## Secret Types

### 1. ANTHROPIC_API_KEY

**Used by:** Python Quality Gate, Python Review Gate

**What it is:** Your API key from Anthropic's service

**How to get it:**
1. Visit https://console.anthropic.com
2. Log in with your Anthropic account
3. Navigate to API keys section
4. Create a new key
5. Copy the value (starts with `sk-ant-`)

### 2. UV_INDEX_WASTEHERO_USERNAME

**Used by:** Python Type Check, Python Security Audit

**What it is:** Username for WasteHero's private PyPI repository

**How to get it:** Contact your DevOps team for credentials

### 3. UV_INDEX_WASTEHERO_PASSWORD

**Used by:** Python Type Check, Python Security Audit

**What it is:** Password or token for WasteHero's private PyPI

**How to get it:** Contact your DevOps team for credentials

## Step-by-Step: Adding Secrets

### Step 1: Navigate to Settings

1. Open your GitHub repository
2. Click "Settings" tab
3. In the left sidebar, click "Secrets and variables"
4. Click "Actions"

You should see a page to manage action secrets.

### Step 2: Add ANTHROPIC_API_KEY (If Using AI Workflows)

1. Click "New repository secret"
2. Name: `ANTHROPIC_API_KEY`
3. Value: Paste your API key from Anthropic Console
4. Click "Add secret"

You'll see it listed without the actual value shown.

### Step 3: Add WasteHero PyPI Credentials (If Using Type Check or Security Audit)

1. Click "New repository secret"
2. Name: `UV_INDEX_WASTEHERO_USERNAME`
3. Value: Your WasteHero PyPI username
4. Click "Add secret"

Then add the password:

1. Click "New repository secret"
2. Name: `UV_INDEX_WASTEHERO_PASSWORD`
3. Value: Your WasteHero PyPI password/token
4. Click "Add secret"

### Step 4: Verify Secrets Are Added

Back on the Secrets and variables page, you should see:
- ANTHROPIC_API_KEY (if added)
- UV_INDEX_WASTEHERO_USERNAME (if added)
- UV_INDEX_WASTEHERO_PASSWORD (if added)

You won't see the values, just the names. That's correct.

## Using Secrets in Workflows

Now that secrets are configured, reference them in your workflow:

```yaml
jobs:
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

The syntax `${{ secrets.ANTHROPIC_API_KEY }}` retrieves the secret value securely.

### Alternative: Using `secrets: inherit`

For organization-level secrets, use:

```yaml
jobs:
  type-check:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets: inherit
```

This passes all secrets to the workflow without naming each one.

## Security Best Practices

### DO's
- Use separate credentials for each service
- Rotate credentials regularly
- Use organization secrets for shared credentials
- Review secret access in audit logs
- Use specific secret names in workflows (not `secrets: inherit` if unnecessary)

### DON'Ts
- Don't commit secrets to version control
- Don't log secret values
- Don't share credentials via chat or email
- Don't use personal credentials; use service accounts
- Don't hardcode secrets in workflows

## Verification

Your secrets are working when:

1. Workflow completes without "secret not found" errors
2. No authentication failures in logs
3. Workflows that use the secret run successfully

## Troubleshooting

### Secret Not Found Error

**Error:** `Error: Secret 'ANTHROPIC_API_KEY' not found`

**Cause:** Secret name doesn't match in workflow

**Solution:**
- Check secret name spelling (case-sensitive)
- Verify secret exists in Secrets and variables page
- Ensure you're on the right repository

### Authentication Failed

**Error:** `Failed to authenticate with PyPI`

**Cause:** Credentials are invalid or expired

**Solution:**
- Verify credentials with DevOps team
- Check credentials haven't changed
- Test credentials locally with UV:
  ```bash
  uv pip install --index-url https://username:password@pypi.wastehero.io/...
  ```

### Secret Not Available to Workflow

**Error:** Workflow doesn't see the secret

**Cause:** Secret scope issue

**Solution:**
- Verify secret is at repository level (not organization if not inherited)
- Check workflow has permission to use secrets
- Ensure secret is explicitly passed or using `secrets: inherit`

## Organization vs Repository Secrets

### Repository Secrets
- Specific to one repository
- Only available to workflows in that repo
- Use when credentials are project-specific

### Organization Secrets
- Shared across all repositories
- Reduces duplication
- Use for shared credentials like ANTHROPIC_API_KEY

To use organization secrets:
```yaml
secrets:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

GitHub automatically inherits organization secrets.

## Common Configurations

### Minimal Setup (Lint Only)
No secrets needed!

```yaml
jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

### With Type Checking

Needs: `UV_INDEX_WASTEHERO_USERNAME`, `UV_INDEX_WASTEHERO_PASSWORD`

```yaml
jobs:
  type-check:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### With AI Quality Gates

Needs: `ANTHROPIC_API_KEY`

```yaml
jobs:
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Complete Pipeline

All secrets:

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
```

## Next Steps

Now that secrets are configured, you can:

1. **Set up a complete pipeline** → [Running the Complete CI Pipeline](running-complete-ci-pipeline.md)
2. **Set up AI workflows** → [Setting Up AI Quality Gates](setting-up-ai-quality-gates.md)
3. **Troubleshoot issues** → [Debugging Workflow Failures](../how-to-guides/debugging-workflow-failures.md)

## Reference

- [Required Secrets Reference](../reference/required-secrets.md) - Detailed secret info
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)

## Success Checklist

You've completed this tutorial when:
- ✓ All required secrets are added to your repository
- ✓ Secret names exactly match workflow requirements
- ✓ You can see secrets listed in Settings → Secrets and variables
- ✓ You understand which workflows need which secrets
- ✓ You understand security best practices

---

**Ready to build your complete pipeline?** Go to [Running the Complete CI Pipeline](running-complete-ci-pipeline.md).
