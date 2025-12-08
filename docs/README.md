# WasteHero GitHub Actions Documentation

Welcome to the comprehensive documentation for WasteHero's shared GitHub Actions workflows and reusable composite actions. This repository provides centralized CI/CD building blocks used across all WasteHero projects.

## Documentation Structure

This documentation follows the **Diataxis framework**, which organizes content into four distinct quadrants based on user intent:

### 1. Tutorials - Learning-Oriented
**For users getting started:** Step-by-step guides that teach foundational concepts through hands-on practice.

- [Getting Started with Shared Workflows](tutorials/README.md) - Start here if you're new
- [Setting Up Your First CI Pipeline](tutorials/getting-started-first-pipeline.md) - Get a working pipeline in minutes
- [Configuring Secrets for Workflows](tutorials/configuring-repository-secrets.md) - Set up required authentication

### 2. How-To Guides - Problem-Oriented
**For users solving specific problems:** Task-focused instructions for accomplishing common goals.

- [How-To Guides Index](how-to-guides/README.md) - All problem-solving guides
- [Setting Up AI Quality Gates](how-to-guides/setting-up-ai-quality-gates.md) - Enable Claude-powered reviews
- [Using Standard Check Workflows](how-to-guides/using-standard-check-workflows.md) - Lint, type check, and security audit
- [Using Individual Workflow Components](how-to-guides/using-individual-workflows.md) - Pick and choose what you need
- [Configuring Type Checking](how-to-guides/configuring-type-checking.md) - Customize type checker settings
- [Debugging Workflow Failures](how-to-guides/debugging-workflow-failures.md) - Troubleshoot common issues

### 3. Reference - Information-Oriented
**For users looking up facts:** Complete technical specifications and API documentation.

- [Reference Guide Index](reference/README.md) - Complete reference
- [Python Lint Workflow Reference](reference/python-lint-workflow.md) - Lint workflow specification
- [Python Type Check Workflow Reference](reference/python-type-check-workflow.md) - Type check specification
- [Python Security Audit Workflow Reference](reference/python-security-audit-workflow.md) - Security audit specification
- [Python Quality Gate Workflow Reference](reference/python-quality-gate-workflow.md) - Quality gate specification
- [Python Review Gate Workflow Reference](reference/python-review-gate-workflow.md) - Review gate specification
- [Setup Python Environment Action Reference](reference/setup-python-env-action.md) - Action documentation
- [Wait for Service Action Reference](reference/wait-for-service-action.md) - Service health check documentation
- [Required Secrets Reference](reference/required-secrets.md) - All secrets and their purposes

### 4. Explanation - Understanding-Oriented
**For users understanding concepts:** Conceptual discussions, rationale, and architecture decisions.

- [Explanation Index](explanation/README.md) - All conceptual content
- [Why AI Quality Gates First?](explanation/why-ai-quality-gates-first.md) - Understanding the gate strategy
- [Architecture and Design](explanation/architecture-and-design.md) - How workflows are organized
- [The Three-Phase Pipeline Model](explanation/three-phase-pipeline-model.md) - Understanding phase execution
- [Security Considerations](explanation/security-considerations.md) - Security strategy and practices
- [CI/CD Best Practices](explanation/cicd-best-practices.md) - General CI/CD principles

## Quick Navigation

### I'm new to this repository
Start here: [Getting Started Tutorial](tutorials/README.md)

### I need to set up a workflow for my project
Go here: [Setting Up Your First CI Pipeline](tutorials/getting-started-first-pipeline.md)

### I have a specific problem to solve
Check: [How-To Guides](how-to-guides/README.md)

### I need to know exactly how something works
Visit: [Reference Documentation](reference/README.md)

### I want to understand the philosophy behind these workflows
Read: [Explanation Documentation](explanation/README.md)

## Content Overview

### Workflows Documented

**AI Quality Gate Workflows:**
- Python Quality Gate (CT-1179) - AI-powered quality analysis
- Python Review Gate (CT-1183) - Comprehensive code review

**Standard Check Workflows (CT-1166 Phase 3):**
- Python Lint (CT-1180) - Static analysis and formatting
- Python Type Check (CT-1181) - Type validation
- Python Security Audit (CT-1182) - Security vulnerability scanning

**Composite Actions:**
- Setup Python Environment - Python + UV setup with caching
- Wait for Service - Health checks for PostgreSQL, MongoDB, NATS, Vault, Valkey

### Secrets Explained

- `ANTHROPIC_API_KEY` - For AI quality gates and review workflows
- `UV_INDEX_WASTEHERO_USERNAME` - WasteHero private PyPI username
- `UV_INDEX_WASTEHERO_PASSWORD` - WasteHero private PyPI password

## Key Features

- **Reusable workflows** - Use across all WasteHero projects
- **Composable design** - Combine workflows as needed
- **AI-powered gates** - Claude-based quality and review
- **Security focused** - Built-in vulnerability scanning
- **Self-hosted ready** - Optimized for Kubernetes runners
- **Cached dependencies** - Fast, efficient execution

## Repository Structure

```
.github/
├── actions/              # Composite actions
│   ├── setup-python-env/
│   └── wait-for-service/
└── workflows/
    └── core/            # Reusable workflows
        ├── python-lint.yml
        ├── python-type-check.yml
        ├── python-security-audit.yml
        ├── python-quality-gate.yml
        └── python-review-gate.yml

docs/                     # This documentation
├── tutorials/           # Learning-oriented guides
├── how-to-guides/       # Problem-solving guides
├── reference/           # Technical specifications
└── explanation/         # Conceptual discussions
```

## Common Tasks

### Add workflow to your project
1. Create `.github/workflows/main.yml` in your project
2. Follow [Setting Up Your First CI Pipeline](tutorials/getting-started-first-pipeline.md)
3. Reference the workflows using `@main` or specific version tag

### Configure secrets
1. Go to repository Settings → Secrets and variables → Actions
2. Add required secrets based on [Required Secrets Reference](reference/required-secrets.md)
3. Use `secrets: inherit` or pass explicitly in workflows

### Troubleshoot a failing workflow
1. Check [Debugging Workflow Failures](how-to-guides/debugging-workflow-failures.md)
2. Review workflow output in GitHub Actions
3. Test locally with `act` before pushing

### Understand pipeline execution order
Read: [The Three-Phase Pipeline Model](explanation/three-phase-pipeline-model.md)

## Getting Help

1. **Check the documentation** - Use search to find relevant content
2. **Review troubleshooting guides** - Most issues are documented
3. **Check GitHub Actions logs** - Detailed error messages are usually there
4. **Contact DevOps team** - For issues beyond documentation

## Document Status

- Created: December 7, 2025
- Framework: Diataxis (4-quadrant documentation)
- Last Updated: December 7, 2025
- Version: 1.0.0

## Contributing to Documentation

When adding new workflows or features:
1. Create corresponding tutorial (learning path)
2. Add how-to guide (problem-solving)
3. Document in reference (technical specs)
4. Explain rationale in explanation (understanding)

This ensures comprehensive, accessible documentation that serves all user types.
