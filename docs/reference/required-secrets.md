# Required Secrets Reference

Complete reference for all secrets used by WasteHero shared workflows.

## Overview

Three secrets are used across different workflows. Most workflows require no secrets, but the most powerful ones (AI gates and dependency-based checks) require authentication.

| Secret | Used By | Required | Priority |
|--------|---------|----------|----------|
| ANTHROPIC_API_KEY | Quality Gate, Review Gate | If using AI workflows | High |
| UV_INDEX_WASTEHERO_USERNAME | Type Check, Security Audit | If using these checks | Medium |
| UV_INDEX_WASTEHERO_PASSWORD | Type Check, Security Audit | If using these checks | Medium |

## ANTHROPIC_API_KEY

### Basic Information

- **Name:** `ANTHROPIC_API_KEY`
- **Type:** API Key
- **Scope:** Repository or Organization level
- **Required by:** [python-quality-gate.yml](python-quality-gate-workflow.md), [python-review-gate.yml](python-review-gate-workflow.md)

### Purpose

Authenticates with Anthropic's Claude API for:
- Python Quality Gate workflow - Automated code quality analysis
- Python Review Gate workflow - Comprehensive code review

### How to Obtain

1. Visit [Anthropic Console](https://console.anthropic.com)
2. Sign in with your account
3. Navigate to "API Keys" or "Account" section
4. Create a new API key
5. Copy the full key value (format: `sk-ant-...`)
6. Store safely

### Security Notes

- This is a secret credential - treat as password
- Don't commit to version control
- Don't share in chat or email
- Rotate periodically (recommended: every 6 months)
- Monitor usage in Anthropic console
- Use organization secrets if shared across projects

### Configuration Steps

#### In GitHub Settings

1. Go to repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `ANTHROPIC_API_KEY` (exact spelling)
5. Value: Paste your API key
6. Click "Add secret"

#### In Workflow

Reference the secret:

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

Or use `secrets: inherit` if organization secret:

```yaml
jobs:
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    secrets: inherit
```

### Troubleshooting

**Error: "Secret 'ANTHROPIC_API_KEY' not found"**
- Verify secret is added in Settings
- Check exact spelling (case-sensitive)
- Refresh GitHub page and try again

**Error: "Invalid API key"**
- Verify you copied the full key from console
- Check key hasn't been revoked
- Try generating a new key

**Error: "Quota exceeded"**
- Check API usage in Anthropic console
- May have exceeded free tier limits
- Contact Anthropic about upgrading

**Workflow fails without error**
- Check GitHub Actions logs
- Look for authentication failures
- Verify secret is being passed correctly

## UV_INDEX_WASTEHERO_USERNAME

### Basic Information

- **Name:** `UV_INDEX_WASTEHERO_USERNAME`
- **Type:** Username
- **Scope:** Repository or Organization level
- **Required by:** [python-type-check.yml](python-type-check-workflow.md), [python-security-audit.yml](python-security-audit-workflow.md)

### Purpose

Username for authenticating with WasteHero's private PyPI repository at `pypi.wastehero.io`.

Used when:
- Installing dependencies from WasteHero's private packages
- Type checking needs to analyze private package types
- Security audit needs to check private packages

### How to Obtain

1. Contact your DevOps team
2. Request PyPI repository credentials
3. You'll receive username and password/token
4. Store securely

### Security Notes

- This is less sensitive than password but still private
- Don't commit to version control
- Consider rotating annually
- Use organization secrets if shared across projects

### Configuration Steps

#### In GitHub Settings

1. Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `UV_INDEX_WASTEHERO_USERNAME` (exact spelling)
4. Value: Your PyPI username
5. Click "Add secret"

#### In Workflow

Reference the secret:

```yaml
jobs:
  type-check:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Troubleshooting

**Error: "Invalid username"**
- Verify username is correct
- Check no spaces before/after
- Confirm with DevOps team

**Error: "Authentication failed"**
- Username/password pair might be mismatched
- Credentials might be expired
- Contact DevOps team

## UV_INDEX_WASTEHERO_PASSWORD

### Basic Information

- **Name:** `UV_INDEX_WASTEHERO_PASSWORD`
- **Type:** Password/Token
- **Scope:** Repository or Organization level
- **Required by:** [python-type-check.yml](python-type-check-workflow.md), [python-security-audit.yml](python-security-audit-workflow.md)

### Purpose

Password or authentication token for WasteHero's private PyPI repository.

Used together with `UV_INDEX_WASTEHERO_USERNAME` for authentication.

### How to Obtain

1. Contact your DevOps team
2. Request PyPI repository credentials
3. You'll receive a password or token
4. Store securely (treat as password)

### Security Notes

- This is a secret credential - treat as password
- Critical security asset - rotate regularly (every 3 months)
- Never commit to version control
- Don't share in any channel
- Use strong, unique credentials
- Use organization secrets if shared

### Configuration Steps

#### In GitHub Settings

1. Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `UV_INDEX_WASTEHERO_PASSWORD` (exact spelling)
4. Value: Your PyPI password/token
5. Click "Add secret"

#### In Workflow

Reference the secret:

```yaml
jobs:
  security-audit:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-security-audit.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Troubleshooting

**Error: "Invalid password"**
- Verify password is exact copy from DevOps
- Check no spaces before/after
- Credentials might be expired
- Contact DevOps to regenerate

**Error: "Authentication failed"**
- Username might be wrong
- Password might be wrong
- Credentials might be revoked
- Verify both username and password are correct

## Common Patterns

### Minimal Setup (No Secrets)

If you only use Python Lint:

```yaml
jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

No secrets needed!

### With AI Quality Gates

Add ANTHROPIC_API_KEY:

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

### With Private Dependencies

Add both UV credentials:

```yaml
jobs:
  type-check:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Complete Setup

All workflows with all secrets:

```yaml
jobs:
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
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

## Best Practices

### For Security

1. **Rotate regularly** - Every 3-6 months
2. **Use organization secrets** - For credentials shared across projects
3. **Audit access** - Check who has access in Settings
4. **Monitor usage** - Watch for unusual activity
5. **Use service accounts** - Never personal credentials

### For Maintenance

1. **Document needs** - List which secrets each project needs
2. **Test secrets** - Verify they work after adding
3. **Plan rotation** - Set calendar reminders for rotation
4. **Keep backups** - Store credentials safely for rotation scenarios

### For Developers

1. **Don't hardcode** - Always use secrets, never hardcode
2. **Test locally** - Verify locally with credentials before pushing
3. **Request access** - Ask DevOps if you need credentials
4. **Report issues** - Tell team if credentials seem compromised

## Verification

Secrets are configured correctly when:
- ✓ Listed in Settings → Secrets and variables → Actions
- ✓ No "secret not found" errors in workflows
- ✓ Workflows complete without authentication failures
- ✓ No secrets appear in logs or PR comments

## Related Documentation

- [Configuring Repository Secrets Tutorial](../tutorials/configuring-repository-secrets.md)
- [Debugging Workflow Failures](../how-to-guides/debugging-workflow-failures.md)
- [Security Considerations](../explanation/security-considerations.md)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)

---

**Question about secrets?** Check [Debugging Workflow Failures](../how-to-guides/debugging-workflow-failures.md) for troubleshooting.
