# Setting Up Your First CI Pipeline

**Time to complete: 20 minutes**

## Goal

Create a working CI pipeline in your project that uses the shared workflows.

## Prerequisites

- A GitHub repository with Python code
- Write access to the repository
- Basic understanding of YAML syntax
- Completed [Getting Started with Shared Workflows](getting-started-shared-workflows.md) tutorial

## Step 1: Create the Workflow Directory Structure

First, create the necessary directory structure in your project:

```bash
mkdir -p .github/workflows
```

This is where GitHub Actions looks for workflow files.

## Step 2: Create Your First Workflow File

Create a file `.github/workflows/python-checks.yml` in your repository:

```yaml
name: Python Code Checks

on:
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

Let me break down what this does:

- **`name:`** - Display name for your workflow
- **`on: pull_request:`** - Trigger when a pull request is created or updated
- **`branches:`** - Only trigger for PRs to main or develop
- **`jobs:`** - Define what should run
- **`lint:`** - Name of this job
- **`uses:`** - Call the shared python-lint workflow from wastehero-github-actions
- **`@main`** - Use the main branch version

## Step 3: Push to GitHub

Commit and push this file to a branch:

```bash
git add .github/workflows/python-checks.yml
git commit -m "Add Python linting workflow"
git push origin feature/add-workflows
```

## Step 4: Create a Pull Request

Create a PR to trigger the workflow:

```bash
# On GitHub, create a PR from your feature branch to main
```

## Step 5: Monitor the Workflow

1. Go to your repository on GitHub
2. Click the "Actions" tab
3. Find your workflow in the list
4. Click on it to see detailed output

You should see:
- Green checkmark if lint passes
- Red X if lint fails
- Details about any issues found

## Verification

Your workflow ran successfully when you see:
- Workflow name appears in Actions tab
- Status shows as "completed" (with green checkmark or red X)
- Job "lint" shows as passed or failed with specific reason

## Understanding the Results

### If it passes:
Your code style is good! The linting workflow didn't find any issues.

### If it fails:
You'll see error messages like:
- `E501 line too long` - Lines exceed 88 characters
- `F841 local variable assigned but never used` - Unused variable
- `Import not sorted correctly` - Import ordering issue

These can usually be fixed by running `ruff format` locally or following the specific guidance.

## Step 6: Add Type Checking (Optional)

Once lint passes, add type checking. Update your workflow:

```yaml
name: Python Code Checks

on:
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main

  type-check:
    needs: lint
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

The `needs: lint` means type-check only runs after lint completes successfully.

But wait! You'll need to set up secrets first. See [Configuring Repository Secrets](configuring-repository-secrets.md) for that step.

## Step 7: Test Locally (Optional)

You can test your workflow locally using `act`:

```bash
# Install act: https://github.com/nektos/act

# List available workflows
act -l

# Run the lint workflow
act pull_request
```

Local testing helps catch issues before pushing to GitHub.

## Common Issues and Solutions

### Workflow doesn't appear in Actions tab

**Problem:** You created the file but it's not showing up.

**Solution:**
- Verify file path is exactly `.github/workflows/filename.yml`
- Check branch is pushed to GitHub
- Refresh the page
- File must have valid YAML syntax

### Workflow runs but shows errors immediately

**Problem:** Workflow starts but fails immediately.

**Likely cause:** YAML syntax error

**Solution:**
- Copy the exact examples from this guide
- Check indentation (YAML is whitespace-sensitive)
- Validate YAML syntax at https://yamllint.com

### "Could not find workflow"

**Problem:** Workflow references invalid path.

**Solution:**
- Verify the `uses:` path is correct
- Check workflow exists in wastehero-github-actions repo
- Use `@main` or specific tag, not branch names
- Path is case-sensitive

## What Happens Next

Your workflow will:
1. Trigger on every pull request to main or develop
2. Check out your code
3. Run Ruff linting and formatting checks
4. Report results to the PR
5. Pass or fail based on findings

When you add more jobs, they run according to `needs:` dependencies.

## Expanding Your Pipeline

You can add more workflows:

```yaml
jobs:
  lint:
    # ... lint config

  type-check:
    needs: lint
    # ... type-check config

  security-audit:
    needs: lint
    # ... security config
```

Each job runs independently (in parallel), but you can control execution order with `needs:`.

## Next Steps

1. **Configure Secrets** - If adding workflows that need authentication
   → Go to [Configuring Repository Secrets](configuring-repository-secrets.md)

2. **Add More Checks** - If you want a complete pipeline
   → Go to [Running the Complete CI Pipeline](running-complete-ci-pipeline.md)

3. **Fix Your Code** - If checks are failing
   → Go to [Debugging Workflow Failures](../how-to-guides/debugging-workflow-failures.md)

## Success Checklist

You've successfully completed this tutorial when:
- ✓ Workflow file created at `.github/workflows/python-checks.yml`
- ✓ File committed and pushed to GitHub
- ✓ PR created to trigger the workflow
- ✓ Workflow appears in Actions tab
- ✓ Workflow completes (pass or fail)
- ✓ You understand what each line does

## Troubleshooting

### The workflow runs but I don't see comments on my PR

The lint workflow doesn't post comments by default. It only shows results in the Actions tab and as a check status.

### How do I fix lint errors?

Run this locally:
```bash
ruff check --fix
ruff format
```

Then commit the fixes.

### My workflow ran too fast, did it actually run?

Yes! Lint is fast because it doesn't need to install dependencies. Type checking takes longer.

## Learn More

- [Python Lint Workflow Reference](../reference/python-lint-workflow.md)
- [How-To Guides](../how-to-guides/README.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Ready for more?** Go to [Configuring Repository Secrets](configuring-repository-secrets.md) to set up secrets for workflows that need them.
