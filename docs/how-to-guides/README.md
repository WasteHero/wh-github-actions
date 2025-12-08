# How-To Guides - Solving Specific Problems

Welcome to the how-to guides section! These guides help you solve specific problems and accomplish particular tasks with the shared workflows.

Unlike tutorials (which teach step-by-step), how-to guides assume you have basic knowledge and focus on solving your specific problem.

## By Problem

### "I need AI-powered code reviews"
→ [Setting Up AI Quality Gates](setting-up-ai-quality-gates.md)

### "I need to set up lint, type check, and security audit"
→ [Using Standard Check Workflows](using-standard-check-workflows.md)

### "I need to use only specific checks"
→ [Using Individual Workflow Components](using-individual-workflows.md)

### "I want to customize my type checker"
→ [Configuring Type Checking](configuring-type-checking.md)

### "My workflows keep failing"
→ [Debugging Workflow Failures](debugging-workflow-failures.md)

### "My security audit is too noisy"
→ [Suppressing Security Audit Findings](suppressing-security-audit-findings.md)

### "I need to understand what each check does"
→ [Understanding Check Results](understanding-check-results.md)

### "I want faster workflow execution"
→ [Optimizing Workflow Performance](optimizing-workflow-performance.md)

### "I need to test workflows locally"
→ [Testing Workflows Locally with Act](testing-workflows-locally-with-act.md)

### "My repository has special requirements"
→ [Customizing Workflows for Your Project](customizing-workflows-for-your-project.md)

## By Workflow Type

### AI Quality Gates
- [Setting Up AI Quality Gates](setting-up-ai-quality-gates.md)
- [Understanding AI Gate Results](understanding-ai-gate-results.md)
- [Troubleshooting AI Gates](troubleshooting-ai-gates.md)

### Standard Python Checks
- [Using Standard Check Workflows](using-standard-check-workflows.md) - Complete guide to all standard checks
  - [Configuring Linting Rules](configuring-linting-rules.md)
  - [Understanding Lint Output](understanding-lint-output.md)
  - [Fixing Common Lint Errors](fixing-common-lint-errors.md)
  - [Configuring Type Checking](configuring-type-checking.md)
  - [Understanding Type Errors](understanding-type-errors.md)
  - [Understanding Security Findings](understanding-security-findings.md)
  - [Suppressing Security Audit Findings](suppressing-security-audit-findings.md)

### Linting (Deprecated - use Standard Check Workflows)
- [Configuring Linting Rules](configuring-linting-rules.md)
- [Understanding Lint Output](understanding-lint-output.md)
- [Fixing Common Lint Errors](fixing-common-lint-errors.md)

### Type Checking
- [Configuring Type Checking](configuring-type-checking.md)
- [Understanding Type Errors](understanding-type-errors.md)
- [Writing Type-Hints](writing-type-hints.md)

### Security Auditing
- [Understanding Security Findings](understanding-security-findings.md)
- [Suppressing Security Audit Findings](suppressing-security-audit-findings.md)
- [Fixing Security Issues](fixing-security-issues.md)

### Actions
- [Using Setup Python Environment Action](using-setup-python-action.md)
- [Using Wait for Service Action](using-wait-for-service-action.md)
- [Creating Custom Composite Actions](creating-custom-composite-actions.md)

## By Skill Level

### Beginner
- [Using Individual Workflow Components](using-individual-workflows.md)
- [Understanding Check Results](understanding-check-results.md)
- [Debugging Workflow Failures](debugging-workflow-failures.md)

### Intermediate
- [Configuring Type Checking](configuring-type-checking.md)
- [Setting Up AI Quality Gates](setting-up-ai-quality-gates.md)
- [Suppressing Security Audit Findings](suppressing-security-audit-findings.md)

### Advanced
- [Customizing Workflows for Your Project](customizing-workflows-for-your-project.md)
- [Testing Workflows Locally with Act](testing-workflows-locally-with-act.md)
- [Creating Custom Composite Actions](creating-custom-composite-actions.md)

## Common Tasks Quick Links

| Task | Guide |
|------|-------|
| Set up all standard checks (lint, type, security) | [Using Standard Check Workflows](using-standard-check-workflows.md) |
| Set up AI reviews | [Setting Up AI Quality Gates](setting-up-ai-quality-gates.md) |
| Add linting to my project | [Using Individual Workflow Components](using-individual-workflows.md) |
| Enable type checking | [Configuring Type Checking](configuring-type-checking.md) |
| Fix a failing workflow | [Debugging Workflow Failures](debugging-workflow-failures.md) |
| Ignore a security warning | [Suppressing Security Audit Findings](suppressing-security-audit-findings.md) |
| Understand a test failure | [Understanding Check Results](understanding-check-results.md) |
| Speed up my checks | [Optimizing Workflow Performance](optimizing-workflow-performance.md) |
| Test before pushing | [Testing Workflows Locally with Act](testing-workflows-locally-with-act.md) |

## How to Use These Guides

Each how-to guide has:
1. **Problem description** - What you're trying to solve
2. **Prerequisites** - What you need before starting
3. **Steps** - How to solve it
4. **Verification** - How to confirm it worked
5. **Troubleshooting** - Common issues and solutions

## Structure

Guides are organized by:
- **Problem category** - What type of problem you're solving
- **Workflow** - Which check/workflow you're working with
- **Complexity** - How advanced the solution is

## When to Use Each Section

### Reference Documentation
Use this when you need to know:
- Exact workflow parameters
- All available options
- Precise technical specifications
- API details

→ Go to [Reference](../reference/README.md)

### Tutorials
Use this when you're:
- New to the system
- Learning for the first time
- Building something from scratch
- Want a learning path

→ Go to [Tutorials](../tutorials/README.md)

### Explanation
Use this when you want to understand:
- Why things work this way
- Architecture decisions
- Conceptual understanding
- Best practices reasoning

→ Go to [Explanation](../explanation/README.md)

## Find Your Problem

### Workflow-Related Issues

**"My workflow won't run"**
→ Check [Debugging Workflow Failures](debugging-workflow-failures.md)

**"Workflow runs but fails on checks"**
→ Check [Understanding Check Results](understanding-check-results.md)

**"Workflow is too slow"**
→ Check [Optimizing Workflow Performance](optimizing-workflow-performance.md)

### Configuration Issues

**"I need to customize checks"**
→ Check [Customizing Workflows for Your Project](customizing-workflows-for-your-project.md)

**"I want different type checking"**
→ Check [Configuring Type Checking](configuring-type-checking.md)

**"I need to ignore some security warnings"**
→ Check [Suppressing Security Audit Findings](suppressing-security-audit-findings.md)

### Understanding Issues

**"I don't understand what failed"**
→ Check [Understanding Check Results](understanding-check-results.md)

**"What do these type errors mean?"**
→ Check [Understanding Type Errors](understanding-type-errors.md)

**"What are these security findings?"**
→ Check [Understanding Security Findings](understanding-security-findings.md)

## Before You Proceed

Make sure you have:
- Basic understanding of workflows (see Tutorials if not)
- A configured GitHub Actions environment
- Repository write access (for most tasks)
- Relevant secrets configured (for some tasks)

## Still Can't Find Your Problem?

1. **Search the documentation** - Use Ctrl+F to search all docs
2. **Check the Reference** - Detailed technical info
3. **Check Explanation** - Conceptual understanding
4. **Review Examples** - Look at reference examples
5. **Contact DevOps** - If documentation doesn't help

---

**Ready to solve a problem?** Pick a guide above and start with the problem that matches yours!
