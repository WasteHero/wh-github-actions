# Using Standard Python Check Workflows

## Overview

This guide shows you how to add and configure standard Python check workflows (lint, type check, and security audit) in your project's CI/CD pipeline.

## Prerequisites

- Repository with Python code
- `.github/workflows/` directory created
- WasteHero GitHub Actions shared workflows accessible
- For type checking and security audit: WasteHero PyPI credentials (if using private packages)

## Workflows at a Glance

| Workflow | File | Purpose | Speed | Cost | Blocks PR |
|----------|------|---------|-------|------|-----------|
| Python Lint | python-lint.yml | Style and code quality | 10-30s | Free | Yes |
| Python Type Check | python-type-check.yml | Type safety | 20-60s | Free | Yes |
| Python Security Audit | python-security-audit.yml | Vulnerability scanning | 20-60s | Free | Yes |

## Step 1: Add Python Lint

### Minimal Configuration

Lint is the fastest check and requires no additional secrets:

```yaml
name: Python Lint

on: [pull_request]

jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

### Full Configuration with Details

```yaml
name: Python Lint

on:
  pull_request:
    branches: [main, develop]
    paths:
      - '**.py'
      - '.github/workflows/lint.yml'

jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

### What Lint Checks

Ruff linting detects:

- **Style violations** - Spacing, indentation, naming conventions
- **Unused imports** - Import statements that aren't used
- **Undefined variables** - Variables referenced but not defined
- **Circular imports** - Import loops
- **Dead code** - Code that can never execute
- **Common mistakes** - Many other quality issues

### Lint Output Example

Passing:
```
✅ Ruff lint check passed
✅ Ruff format check passed
```

Failing:
```
❌ Ruff found issues:

myapp/models.py:5:1: F401 [unused-import] `os` imported but unused
myapp/handlers.py:20:1: E302 [too-many-blank-lines] Expected 2 blank lines, found 3
myapp/utils.py:45:1: E501 [line-too-long] Line too long (101 > 88 characters)
```

## Step 2: Add Python Type Check

### Configure Repository Secrets First

Type checking requires access to private packages:

1. Go to repository **Settings** > **Secrets and variables** > **Actions**
2. Create two secrets:
   - `UV_INDEX_WASTEHERO_USERNAME` - Your WasteHero PyPI username
   - `UV_INDEX_WASTEHERO_PASSWORD` - Your WasteHero PyPI token

### Minimal Configuration

```yaml
name: Python Type Check

on: [pull_request]

jobs:
  type-check:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Depend on Lint (Optional but Recommended)

```yaml
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

### What Type Check Detects

Pyright/Mypy type checking detects:

- **Type mismatches** - Passing wrong types to functions
- **None references** - Accessing properties on None
- **Missing type hints** - Unmapped types
- **Type incompatibilities** - Incompatible operations
- **Unsafe operations** - Operations without type safety

### Type Check Output Example

Passing:
```
✅ Type checking passed (0 errors)
```

Failing:
```
❌ Type checking found issues:

myapp/models.py:15 - error: Argument of type "str" cannot be assigned to parameter "id" of type "int"
myapp/handlers.py:42 - error: "None" has no attribute "user"
myapp/utils.py:60 - error: Missing type annotation for variable "result"
```

### Configuring Type Checker

Type checker (Pyright or Mypy) is configured in your project's `pyproject.toml`:

```toml
[tool.pyright]
typeCheckingMode = "basic"  # or "standard" or "strict"

# Or for Mypy:
[tool.mypy]
python_version = "3.11"
strict = true
```

## Step 3: Add Python Security Audit

### Configure Repository Secrets First

Security audit requires the same secrets as type checking:

1. Go to repository **Settings** > **Secrets and variables** > **Actions**
2. Ensure you have:
   - `UV_INDEX_WASTEHERO_USERNAME`
   - `UV_INDEX_WASTEHERO_PASSWORD`

### Minimal Configuration

```yaml
name: Python Security Audit

on: [pull_request]

jobs:
  security-audit:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-security-audit.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Run in Parallel with Type Check

```yaml
jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main

  type-check:
    needs: lint
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}

  security-audit:
    needs: lint
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-security-audit.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### What Security Audit Detects

Ruff security rules (S001-S699) detect:

- **Hardcoded secrets** - Passwords or API keys in source code
- **SQL injection** - Unsafe SQL query construction
- **Insecure deserialization** - Use of pickle without validation
- **Insecure crypto** - Weak cryptographic functions
- **Unsafe temp files** - Temporary files with predictable names
- **Dangerous imports** - Unsafe modules like `pickle` or `yaml`
- **System calls** - Dangerous subprocess usage
- **Other OWASP issues** - Top 10 vulnerabilities

### Security Audit Output Example

Passing:
```
✅ Security audit passed (0 findings)
```

Failing:
```
❌ Security audit found issues:

myapp/auth.py:25:1: S101 [assert-used] Use of assert detected; use pytest.fail
myapp/database.py:40:1: S608 [sql-string-concatenation] Possible SQL injection
myapp/config.py:15:1: S105 [hardcoded-password] Possible hardcoded password
```

## Complete Workflow Examples

### Example 1: Lint Only

For simple projects or as a starting point:

```yaml
name: Python Lint

on:
  pull_request:
    branches: [main]

jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

### Example 2: All Standard Checks

For comprehensive Python validation:

```yaml
name: Python Standard Checks

on:
  pull_request:
    branches: [main]

jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main

  type-check:
    needs: lint
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}

  security-audit:
    needs: lint
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-security-audit.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Example 3: Standard Checks + Tests

For full CI pipeline with tests:

```yaml
name: Python CI

on:
  pull_request:
    branches: [main]

jobs:
  # Phase 1: Standard Checks (Parallel)
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main

  type-check:
    needs: lint
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-type-check.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}

  security-audit:
    needs: lint
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-security-audit.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}

  # Phase 2: Tests (after checks pass)
  tests:
    needs: [type-check, security-audit]
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

### Example 4: Standard Checks + AI Gates + Tests

For comprehensive quality assurance:

```yaml
name: Comprehensive Python CI

on:
  pull_request:
    branches: [main]

jobs:
  # Phase 1: AI Quality Gates (Informational + Blocking)
  claude-review:
    uses: WasteHero/wastehero-github-actions/.github/workflows/ai/claude-pr-review.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  # Phase 2: Standard Checks (Parallel)
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

  # Phase 3: Tests
  tests:
    needs: [lint, type-check, security-audit, claude-review]
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

## Configuration Files

### Ruff Configuration

Create `.ruff.toml` or add to `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

# Ignore specific rules
extend-ignore = ["E501"]

# Exclude files
exclude = ["migrations/", "build/"]
```

### Type Checker Configuration

In `pyproject.toml`:

```toml
[tool.pyright]
typeCheckingMode = "basic"  # or "standard" or "strict"
pythonVersion = "3.11"
exclude = ["**/migrations/"]

# Or for Mypy:
[tool.mypy]
python_version = "3.11"
strict = true
exclude = ["migrations/"]
```

## Handling Check Failures

### Lint Failures

When lint fails:

```bash
# See what needs fixing
ruff check myapp/

# Let Ruff fix what it can
ruff format myapp/

# Fix remaining issues manually
ruff check myapp/
```

### Type Check Failures

When type checking fails:

1. Read the error message carefully
2. Add type hints to fix the issue
3. Example: `def process(data: str) -> int:`
4. For complex types, use `# type: ignore` only as last resort

### Security Audit Failures

When security audit fails:

1. Review the finding - is it a real issue?
2. If real: Fix the security issue
3. If false positive: Add `# noqa: S602` comment with explanation
4. Document why you're suppressing

Example:
```python
# Intentionally using shell=True for legacy system command
subprocess.run(user_input, shell=True)  # noqa: S602
```

## Local Testing

Run checks locally before pushing:

### Check Everything Locally

```bash
# Lint
ruff check .
ruff format . --check

# Type check
pyright .

# Security audit
ruff check --select=S .

# Run tests
pytest
```

### Quick Check with Make

Add a Makefile:

```makefile
check:
	ruff check .
	ruff format . --check
	pyright .
	ruff check --select=S .
	pytest

fix:
	ruff format .
```

Then run:
```bash
make check
make fix
```

## Troubleshooting

### Type Check Fails with "Module not found"

**Problem**: Type checker can't find project modules.

**Solutions**:
- Verify all dependencies in `pyproject.toml`
- Ensure `uv sync` was run
- Check Python path configuration
- Verify import statements are correct

### Security Audit Reports False Positives

**Problem**: Security rule is too strict for your use case.

**Solutions**:
1. Review the finding carefully
2. Add suppression comment: `# noqa: S602`
3. Document why it's safe
4. Never suppress without understanding the risk

### Lint Always Fails on Same File

**Problem**: Same lint issues keep appearing.

**Solutions**:
- Run `ruff format` to auto-fix style issues
- Update `pyproject.toml` to suppress intentional issues
- Refactor code to pass linting
- Check for configuration conflicts

### Workflow Runs but Tests Fail

**Problem**: Checks pass but tests fail.

**Solutions**:
- Tests are different from checks
- Checks verify style and types, tests verify functionality
- Run `pytest` locally to debug
- Add more tests to catch issues earlier

## Performance Optimization

### Speed up Type Checking

```bash
# Use faster type checker if available
# In pyproject.toml, prefer pyright over mypy
[tool.pyright]
# ...
```

### Run in Parallel

```yaml
jobs:
  type-check:
    needs: lint
    # Runs while security-audit also runs
  security-audit:
    needs: lint
    # Runs in parallel with type-check
```

### Cache Dependencies

The workflows automatically cache dependencies for faster runs.

## Make Checks Required

To prevent PRs from merging without passing checks:

1. Go to repository **Settings** > **Branches**
2. Edit branch protection rule for `main`
3. Under "Require status checks to pass before merging"
4. Select:
   - `lint` workflow
   - `type-check` workflow (if using)
   - `security-audit` workflow (if using)
5. Save

Now all checks must pass before PR can merge.

## Next Steps

- **To understand the strategy**: Read [Standard Checks Strategy](/docs/explanation/standard-checks-strategy.md)
- **For detailed specifications**: See reference documentation
- **To set up AI gates**: See [Setting Up AI Quality Gates](/docs/how-to-guides/setting-up-ai-quality-gates.md)
- **To understand the full pipeline**: Read [Three-Phase Pipeline Model](/docs/explanation/three-phase-pipeline-model.md)

## Related Documentation

- [Python Lint Workflow Reference](/docs/reference/python-lint-workflow.md)
- [Python Type Check Workflow Reference](/docs/reference/python-type-check-workflow.md)
- [Python Security Audit Workflow Reference](/docs/reference/python-security-audit-workflow.md)
- [Required Secrets Reference](/docs/reference/required-secrets.md)
