# Debugging Workflow Failures

## Problem

Your workflow is failing and you need to understand why and how to fix it.

## Prerequisites

- A GitHub repository with a failing workflow
- Access to GitHub Actions logs
- Basic understanding of what each check does

## Systematic Approach

Follow these steps in order to debug workflow failures:

### Step 1: Check the GitHub Actions Tab

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Find your workflow run in the list
4. Click on it to see details

### Step 2: Identify Which Job Failed

Look at the job list on the left side:
- Green checkmark = passed
- Red X = failed
- Yellow circle = running or waiting

Click the failed job to see details.

### Step 3: Read the Error Message

Scroll through the job output to find the error. Look for:
- `ERROR:` or `error:` messages
- Red text highlighting
- Step that failed (marked with red X)

Common patterns:
```
Error: Secret 'ANTHROPIC_API_KEY' not found
Error: Command failed: ruff check
Error: Module not found: fastapi
```

### Step 4: Determine the Problem Category

Use the error message to find the category:

**Category A: Configuration Issues**
- Secrets not found
- Workflow syntax errors
- Missing inputs or parameters
- Workflow not triggered correctly

**Category B: Code Quality Issues**
- Lint errors
- Type errors
- Security findings
- Test failures

**Category C: Environment Issues**
- Dependency installation failed
- Service not ready
- Python version mismatch
- Cache issues

**Category D: Permission Issues**
- Access denied
- Write permissions missing
- Authentication failed

### Step 5: Find Your Specific Problem Below

## Configuration Issues

### Error: "Secret not found"

**Message:** `Error: Secret 'ANTHROPIC_API_KEY' not found`

**Cause:** Secret is not configured in the repository

**Fix:**
1. Go to Settings → Secrets and variables → Actions
2. Check the secret is listed
3. If missing, add it (see [Configuring Repository Secrets](../tutorials/configuring-repository-secrets.md))
4. If present, check name spelling (case-sensitive)
5. Re-run the workflow

**Verification:** Workflow completes without secret error

### Error: YAML syntax error

**Message:** `Error parsing workflow file`

**Cause:** Invalid YAML in your workflow file

**Fix:**
1. Check file indentation (YAML is whitespace-sensitive)
2. Use 2-space indentation (not tabs)
3. Validate YAML at https://yamllint.com
4. Common mistakes:
   - Missing colons after keys
   - Incorrect indentation
   - Unclosed strings

**Example of wrong indentation:**
```yaml
jobs:
  lint:
    uses: ...
  type-check:  # Wrong! Should be at same level as lint
     uses: ...
```

### Error: "Workflow not found"

**Message:** `Error: Could not find workflow file`

**Cause:** Workflow file is not in the right location

**Fix:**
- File must be at: `.github/workflows/filename.yml`
- Check path is exact match
- Verify file is committed to GitHub (not just local)
- Try full path: `.github/workflows/python-checks.yml`

## Code Quality Issues

### Lint Failures

**Message:** Multiple `ERROR` lines about code style

**Cause:** Code doesn't follow formatting standards

**Fix:**
1. Read the error (usually tells you what's wrong)
2. Fix locally:
   ```bash
   ruff check --fix
   ruff format
   ```
3. Commit and push
4. Re-run workflow

**Common lint errors:**
- `E501` - Line too long (max 88 chars)
- `F841` - Unused variable
- `F401` - Unused import
- `I001` - Import sorting

### Type Checking Failures

**Message:** `error: ... is not assignable to ...`

**Cause:** Type mismatch in code

**Fix:**
1. Read the error message - it shows the type mismatch
2. Look at the file and line number
3. Either:
   - Fix the code to match the type
   - Add correct type hints
   - Suppress with `# type: ignore` (if you understand why)
4. Test locally: `uv run mypy` or equivalent
5. Commit and push

**Example:**
```python
# Wrong:
x: int = "hello"  # Type error: str not assignable to int

# Right:
x: str = "hello"  # Type matches
```

### Security Audit Findings

**Message:** `Security issue: S602 ... (subprocess without shell=False)`

**Cause:** Code uses potentially unsafe patterns

**Fix:**
1. Review the security finding - is it real?
2. If real, fix the code to use safer patterns
3. If false positive, suppress:
   ```python
   subprocess.run(cmd, shell=True)  # noqa: S602
   ```
4. Test locally: `uv run ruff check --select=S`
5. Commit and push

See [Suppressing Security Audit Findings](suppressing-security-audit-findings.md) for more details.

## Environment Issues

### Error: "Module not found"

**Message:** `ModuleNotFoundError: No module named 'fastapi'`

**Cause:** Dependency is not installed

**Fix:**
1. Check `pyproject.toml` includes the dependency
2. Make sure WasteHero PyPI credentials are configured
3. Test locally:
   ```bash
   uv sync
   uv run mypy
   ```
4. If still fails, commit and try again

### Error: "Service not ready"

**Message:** `ERROR: postgres not ready after 30 attempts`

**Cause:** Service initialization failed

**Fix:**
1. Check service is specified correctly
2. Verify port number
3. Check service logs in GitHub Actions output
4. Increase timeout if needed:
   ```yaml
   - uses: WasteHero/wastehero-github-actions/.github/actions/wait-for-service@main
     with:
       service-type: postgres
       port: 5432
       max-retries: 60  # Increased from default 30
   ```

## Permission Issues

### Error: "Permission denied"

**Message:** `error: Permission denied when writing to: /path/to/file`

**Cause:** Workflow doesn't have write permissions

**Fix:**
1. Check workflow has correct permissions
2. Add this to your workflow:
   ```yaml
   permissions:
     contents: write
     pull-requests: write
   ```
3. Or verify the job has needed permissions

### Error: "Authentication failed"

**Message:** `fatal: could not read Username for 'https://github.com': No such file or directory`

**Cause:** GitHub token is missing or invalid

**Fix:**
1. Most workflows need `actions/checkout@v4` which handles auth
2. If custom git commands, ensure:
   ```yaml
   - uses: actions/checkout@v4
   ```
3. Is before any git commands

## AI Workflow Issues

### Quality Gate Always Fails

**Message:** Workflow runs but always reports issues

**Cause:** Code genuinely has quality issues, OR Claude is being strict

**Fix:**
1. Review the PR comment with specific findings
2. Fix the issues Claude identified
3. Push a new commit
4. Workflow will re-run automatically

### Review Gate Fails Immediately

**Message:** Workflow starts but fails before completing review

**Cause:** Claude API error or timeout

**Fix:**
1. Check ANTHROPIC_API_KEY is valid
2. Check API quota hasn't been exceeded
3. Try again in a few minutes
4. Contact DevOps if persists

## Performance Issues

### Workflow Takes Too Long

**Problem:** Workflow completes but takes much longer than expected

**Fix:**
1. Check if caching is working (should see "cache hit")
2. Dependencies are being reinstalled unnecessarily
3. Look for slow steps in output
4. See [Optimizing Workflow Performance](optimizing-workflow-performance.md)

## Verification

Your debugging was successful when:
- ✓ You identified the specific error
- ✓ You understand what caused it
- ✓ You can fix it (either code or configuration)
- ✓ You tested the fix
- ✓ Workflow passes on next run

## If You're Still Stuck

### Gather Information
1. Full workflow output (screenshot if needed)
2. The exact error message
3. What changed since it last worked
4. Steps you've already tried

### Get Help
1. Check [Reference Documentation](../reference/README.md) for specific workflow details
2. Review [Explanation](../explanation/README.md) for conceptual understanding
3. Ask the DevOps team with the information you gathered

## Quick Reference

| Error | Likely Cause | Quick Fix |
|-------|-------------|----------|
| Secret not found | Not configured | Add in Settings |
| YAML syntax error | Invalid YAML | Validate at yamllint.com |
| Lint failure | Code style | Run `ruff format` locally |
| Type error | Type mismatch | Fix types or add hints |
| Security issue | Unsafe pattern | Fix code or suppress |
| Module not found | Dependency missing | Check pyproject.toml |

---

**Can't find your issue?** Go back to [How-To Guides](README.md) and find another guide that matches your problem.
