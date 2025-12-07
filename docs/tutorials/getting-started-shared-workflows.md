# Getting Started with Shared Workflows

**Time to complete: 10 minutes**

## Goal

Understand what shared workflows are, why they exist, and get a high-level overview of what's available in the WasteHero GitHub Actions repository.

## What Are Shared Workflows?

Shared workflows are reusable GitHub Actions workflow files that you can reference from other repositories. Instead of duplicating CI/CD logic across multiple projects, we maintain a single source of truth in the `wastehero-github-actions` repository.

Think of it like a library for CI/CD - rather than copying and pasting code everywhere, you point to shared, maintained workflows.

## Why Use Shared Workflows?

### Consistency
All WasteHero projects use the same code quality standards, security checks, and testing approaches. No more "this project has different linting rules than that one."

### Maintenance
When we upgrade tools (like Ruff, Pyright, or Python versions), we update once in the shared repository, and all projects automatically benefit from the improvement.

### Reduced Duplication
We don't maintain dozens of nearly-identical workflow files across repositories. Changes are made in one place.

### Standardization
New projects can get up and running quickly by using proven, tested workflows instead of starting from scratch.

### Organization Learning
As the DevOps team makes discoveries about CI/CD best practices, those improvements flow to all projects automatically.

## How Shared Workflows Work

### The Repository
The `wastehero-github-actions` repository contains:
- **Workflow files** in `.github/workflows/core/` - These are the reusable workflows
- **Composite actions** in `.github/actions/` - Reusable action scripts
- **Documentation** in `docs/` - Complete guides (you're reading it!)

### Calling a Shared Workflow

In your project's workflow file, you reference a shared workflow like this:

```yaml
jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

This says: "Use the python-lint.yml workflow from the wastehero-github-actions repository, main branch."

### Version Control

You can reference workflows by:
- **`@main`** - Latest version (recommended for active development)
- **`@v1.0`** - Specific release tag (recommended for stability)
- **`@abc123`** - Specific commit (maximum control)

## Available Workflows

### AI Quality Gate Workflows

These use Claude AI to analyze code quality and provide intelligent reviews:

**Python Quality Gate**
- Performs automated code quality analysis
- Blocks merge if quality issues are found
- Posts detailed feedback as PR comments
- CT-1179

**Python Review Gate**
- Comprehensive code review using AI
- Checks code quality, performance, security, and testing
- Blocks merge if issues are found
- CT-1183

### Standard Check Workflows

Traditional code quality checks:

**Python Lint**
- Static code analysis with Ruff
- Enforces code formatting and style
- No dependencies needed, runs quickly
- CT-1180

**Python Type Check**
- Type validation with Pyright or Mypy
- Catches type errors before runtime
- Requires Python environment setup
- CT-1181

**Python Security Audit**
- Security vulnerability scanning
- Detects hardcoded secrets, insecure patterns
- Uses Ruff security rules
- CT-1182

## Available Actions

### Setup Python Environment

Installs and configures Python with UV package manager:
- Installs Python (default: 3.13)
- Sets up UV for dependency management
- Handles caching for speed

### Wait for Service

Waits for services to be ready:
- PostgreSQL
- MongoDB
- NATS
- Vault
- Valkey

Useful for integration tests that need external services.

## Quick Comparison

| Need | Tool | Type |
|------|------|------|
| Check code style | Python Lint | Quick, no setup |
| Validate types | Python Type Check | Requires setup |
| Find vulnerabilities | Python Security Audit | Requires setup |
| Get AI review | Python Review Gate | AI-powered |
| Check code quality | Python Quality Gate | AI-powered |
| Install Python | Setup Python Env | Action |
| Wait for DB | Wait for Service | Action |

## The Three-Phase Pipeline Model

Most WasteHero projects use a three-phase approach:

**Phase 1: AI Quality Gate**
- Runs first, blocks everything if it fails
- AI analyzes code for quality issues
- Fast feedback on fundamental issues

**Phase 2: Standard Checks**
- Runs after quality gate passes
- Lint, type checking, security
- Traditional automated checks

**Phase 3: Code Review & Tests**
- Runs after standard checks pass
- AI comprehensive review
- Your project's tests

This order ensures problems are caught quickly and progressively.

## Key Concepts to Remember

1. **Reusable Workflows** - Defined once, used everywhere
2. **Composite Actions** - Reusable tasks within workflows
3. **Secrets** - Credentials managed securely in GitHub
4. **Workflow Call** - The trigger type for reusable workflows
5. **Phase Execution** - Using `needs:` to control execution order

## What You'll Learn Next

The next tutorial, [Setting Up Your First CI Pipeline](getting-started-first-pipeline.md), will walk you through actually creating a workflow file and getting it working.

You'll:
1. Create a workflow file in your project
2. Reference a shared workflow
3. Watch it execute
4. See your code being checked

## Terminology

- **Workflow** - A GitHub Actions configuration file (YAML)
- **Job** - A unit of work in a workflow
- **Step** - An individual command or action within a job
- **Action** - A reusable piece of workflow code
- **Composite Action** - An action made of multiple steps
- **Reusable Workflow** - A workflow that can be called by other workflows
- **Trigger** - What causes a workflow to run (e.g., pull request)

## Common Questions

**Q: Can I modify the shared workflows for my project?**
A: No, they're read-only when you call them. If you need different behavior, contact the DevOps team about modifying the shared workflow.

**Q: What if I don't like some checks?**
A: Many checks can be configured. Review the reference documentation or discuss with your team about changes to shared standards.

**Q: Can I use these workflows for non-Python projects?**
A: Currently, these workflows are Python-focused. Reach out to DevOps if you need workflows for other languages.

**Q: Is there a performance impact?**
A: No, shared workflows execute just like local ones. We optimize for speed and cache dependencies.

## Next Step

Ready to build your first pipeline? Go to [Setting Up Your First CI Pipeline](getting-started-first-pipeline.md).

---

**Questions?** Check the [Reference Documentation](../reference/README.md) for detailed technical information.
