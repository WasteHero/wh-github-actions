# Standard Python Check Workflows Strategy

## Overview

This document explains the strategic role of standard Python check workflows in the WasteHero CI/CD pipeline, and how they complement AI-powered quality gates.

## What Are Standard Check Workflows?

Standard check workflows are traditional code quality, type safety, and security checks that form the foundation of Python CI/CD pipelines. They are the industry-standard checks that every Python project should run.

Three standard checks exist:

1. **Python Lint** (CT-1180) - Style and code quality via Ruff
2. **Python Type Check** (CT-1181) - Type safety via Pyright or Mypy
3. **Python Security Audit** (CT-1182) - Vulnerability scanning via Ruff security rules

## The Four Pillars of Code Quality

The WasteHero pipeline uses four complementary types of checks:

### 1. AI Quality Gates (Phase 1)
- What: Intelligent code analysis using Claude AI
- Finds: Logic errors, design issues, performance problems
- Speed: 30-60 seconds
- Cost: ~$0.05-0.20 per PR

### 2. Standard Checks (Phase 2)
- What: Traditional code quality tools
- Finds: Style issues, type errors, security vulnerabilities
- Speed: 30-120 seconds
- Cost: Free (no API calls)

### 3. AI Code Review (Phase 3)
- What: Comprehensive Claude AI review
- Finds: Everything AI gates miss, plus detailed feedback
- Speed: 60-120 seconds
- Cost: ~$0.10-0.20 per PR

### 4. Project Tests (Phase 3)
- What: Unit and integration tests
- Finds: Runtime errors, broken functionality
- Speed: Varies (30 seconds to minutes)
- Cost: Free (internal)

## Why Standard Checks Matter

While AI quality gates provide intelligent analysis, standard checks are essential because:

### 1. **Fast Feedback**
- No API calls needed (completely local)
- Results in seconds to minutes
- Can run offline during development

### 2. **Consistent Rules**
- Linting: Same style rules for all projects
- Type checking: Strict type validation
- Security: OWASP Top 10 scanning

### 3. **Developer Workflow**
- Developers can run checks locally (`ruff check`, `pyright`)
- Consistent with IDE integration
- Familiar tools across the industry

### 4. **Cost-Free**
- No API charges
- Scales infinitely without cost
- Can run on every commit

### 5. **Deterministic**
- Same input always produces same output
- No randomness or variance
- Reliable for CI/CD

### 6. **Non-ML Accuracy**
- Linter rules are precise and explicit
- Type checker rules are deterministic
- Security rules are based on known patterns

## The Three Workflows

### 1. Python Lint (CT-1180)

**Purpose**: Enforce code style consistency and identify common mistakes.

**Uses**: Ruff linter and formatter

**Detects**:
- PEP 8 violations (spacing, naming, structure)
- Unused imports and variables
- Circular imports
- Undefined names
- Many other style and quality issues

**Why**:
- Style consistency improves readability
- Catches obvious mistakes early
- Forces good habits
- Fast (no dependencies needed)

**Best Practice**: Run this first - it's the fastest and catches obvious issues.

### 2. Python Type Check (CT-1181)

**Purpose**: Validate Python type hints and catch type-related errors.

**Uses**: Pyright or Mypy (project-configured)

**Detects**:
- Type mismatches (wrong types passed to functions)
- Missing type hints
- Incomplete annotations
- Type incompatibilities
- Unsafe operations

**Why**:
- Type safety prevents entire classes of bugs
- Catches errors at edit-time, not runtime
- Improves code clarity
- Industry standard in modern Python

**Best Practice**: Run after lint since it requires dependencies.

### 3. Python Security Audit (CT-1182)

**Purpose**: Scan for security vulnerabilities and unsafe patterns.

**Uses**: Ruff security rules (S001-S699)

**Detects**:
- Hardcoded passwords and secrets
- SQL injection vulnerabilities
- Insecure deserialization (pickle)
- Unsafe cryptographic functions
- Insecure temporary file creation
- Unsafe YAML loading
- Dangerous system calls
- OWASP Top 10 issues

**Why**:
- Security is non-negotiable
- Catches vulnerable patterns automatically
- Prevents common exploits
- Required for production code

**Best Practice**: Run alongside type checking as it requires dependencies.

## The Three-Phase Pipeline

These standard checks are Phase 2 of the WasteHero three-phase pipeline:

```
Phase 1: AI Quality Gates (Fail-Fast)
├─ Quality Gate (CT-1179)
└─ PR Review (CT-1183)
         ↓
Phase 2: Standard Checks (Parallel)
├─ Lint (CT-1180) [Fast - no deps]
├─ Type Check (CT-1181) [Medium - needs deps]
└─ Security Audit (CT-1182) [Medium - needs deps]
         ↓
Phase 3: AI Review + Tests
├─ Python Review Gate (CT-1183)
└─ Project Tests (pytest, etc.)
```

**Why This Order?**

1. **Lint First** - Fastest, catches obvious issues, no dependencies needed
2. **Type/Security Parallel** - Both need dependencies, can run together
3. **AI Review/Tests Last** - More expensive, should only run on quality code

This ordering minimizes feedback latency while ensuring comprehensive checks.

## Workflows Comparison

| Check | Lint | Type Check | Security |
|-------|------|-----------|----------|
| **Tool** | Ruff | Pyright/Mypy | Ruff security rules |
| **Speed** | 10-30 seconds | 20-60 seconds | 20-60 seconds |
| **Dependencies** | No | Yes | Yes |
| **Cost** | Free | Free | Free |
| **Critical** | Yes | Yes | Yes |
| **Best For** | Style/quality | Type safety | Security |
| **Fail PR** | Yes | Yes | Yes |
| **Autofix** | Can (ruff format) | No | Manual fixes |

## Design Decisions

### Why Ruff for Linting?

- **Fast** - Rust implementation, extremely quick
- **Batteries-included** - Includes hundreds of checks
- **Modern** - Designed for modern Python
- **Growing** - Actively developed and improved

### Why Pyright/Mypy for Type Checking?

- **Industry Standard** - Used everywhere
- **Strict** - Can enforce strict typing
- **Configurable** - Adjust strictness as needed
- **Mature** - Battle-tested in production

### Why Separate Security Audit?

- **Specialized** - Focused on security issues
- **OWASP** - Covers Top 10 vulnerabilities
- **Explicit** - Can suppress specific findings
- **Auditable** - Can track security debt

## Integration with Other Checks

Standard checks work together with other pipeline components:

```
AI Gates (Intelligent)
         +
Standard Checks (Deterministic)
         +
Project Tests (Functional)
         +
Human Review (Contextual)
    =
    Comprehensive Quality Assurance
```

None should be removed:
- Remove AI gates? You lose intelligent analysis
- Remove standard checks? You lose consistent rules
- Remove tests? You lose functional verification
- Remove human review? You lose context

## Execution Order Guidelines

For optimal feedback and performance:

### Optimal Order
1. **Lint first** (fastest, no deps)
2. **Type check + Security audit parallel** (both need deps)
3. **AI review** (medium speed, more thorough)
4. **Tests** (slowest, most thorough)

### Example Dependency Chain
```yaml
lint:
  # No dependencies - runs first

type-check:
  needs: lint  # Optional, but good for sequencing

security-audit:
  needs: lint

ai-review:
  needs: [type-check, security-audit]

tests:
  needs: ai-review
```

## When to Customize Standard Checks

### Lint Rules
- Adjust rule strictness in `pyproject.toml` or `.ruff.toml`
- Suppress specific rules with `# noqa: E501`
- Ignore files/paths
- Example: Relax naming rules for legacy code

### Type Checking
- Adjust type checker (Pyright vs Mypy)
- Change strictness level
- Add type ignore comments: `# type: ignore`
- Configure in `pyproject.toml`

### Security Rules
- Suppress specific security rules: `# noqa: S602`
- Document why you're suppressing
- Suppress entire files or functions
- Review suppressed rules regularly

## Common Customizations

### Relax Lint Rules
```toml
[tool.ruff]
extend-ignore = ["E501"]  # Ignore long lines
```

### Make Type Checking Stricter
```toml
[tool.pyright]
typeCheckingMode = "strict"
```

### Suppress Security Finding
```python
# Needed for testing emergency recovery
subprocess.run(user_input, shell=True)  # noqa: S602
```

## Cost Analysis

Standard checks are free:

- **Lint**: No cost (local analysis)
- **Type Check**: No cost (local analysis)
- **Security Audit**: No cost (local analysis)

They can run unlimited times without additional cost, making them ideal for:
- Running locally before pushing
- Running on every commit
- Running on every branch
- Continuous validation

## Development Workflow

Most developers should run these checks locally before pushing:

### Pre-Push Workflow
```bash
# Check linting locally
ruff check .
ruff format . --check

# Check types locally
pyright .

# Check security locally
ruff check --select=S .

# Run tests locally
pytest

# Push only if all pass
git push
```

This prevents unnecessary CI runs and saves time.

## Key Principles

1. **Consistency** - Same rules across all projects
2. **Speed** - Local tools, immediate feedback
3. **Cost-Free** - No API charges
4. **Deterministic** - Reliable, reproducible results
5. **Foundation** - Baseline for code quality

## Integration Points

Standard checks integrate with:

- **IDEs** - Ruff, Pyright have IDE plugins
- **Pre-commit hooks** - Run locally before commit
- **CI/CD pipelines** - Run on every PR
- **Local development** - Run during coding

## Troubleshooting

### Lint Fails Locally But Passes in CI?
- Check Python version differences
- Verify Ruff version matches
- Use `ruff --version` to check

### Type Errors In CI But Not Locally?
- Ensure dependencies are the same
- Check Python version
- Verify type checker configuration matches

### Security Audit Too Noisy?
- Review findings carefully first
- Suppress only after review
- Document suppressions with comments
- Address root cause, not just suppress

## Migration Path

If you don't have these checks yet:

1. **Start with Lint** - Easiest to adopt
2. **Add Type Checking** - Requires some refactoring
3. **Add Security Audit** - Usually no issues for new code
4. **Layer with AI Gates** - Once basic checks pass

Each layer adds value without requiring the others.

## Best Practices

1. **Run Locally** - Don't rely on CI to find issues
2. **Fast Feedback** - Lint < 30 seconds
3. **No Surprises** - Same rules everywhere
4. **Customization** - Adjust for project needs
5. **Suppress Intentionally** - Never blindly ignore

## Next Steps

- **To set up standard checks**: See [Using Standard Check Workflows](/docs/how-to-guides/using-standard-check-workflows.md)
- **For configuration details**: See reference documentation
- **To understand the full pipeline**: Read [Three-Phase Pipeline Model](/docs/explanation/three-phase-pipeline-model.md)

## Further Reading

- [CI/CD Best Practices](/docs/explanation/cicd-best-practices.md) - General principles
- [Design Decisions and Trade-offs](/docs/explanation/design-decisions-tradeoffs.md) - Why these tools
- [Understanding Ruff](/docs/explanation/understanding-ruff.md) - Deep dive into linting
