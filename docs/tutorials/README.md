# Tutorials - Getting Started with Shared Workflows

Welcome to the tutorials section! These guides are designed to teach you how to use WasteHero's shared GitHub Actions workflows through hands-on, step-by-step instruction.

## Learning Path

Start with the basics and work your way up:

### 1. [Getting Started with Shared Workflows](getting-started-shared-workflows.md)
**Time: 10 minutes**

Learn the fundamental concepts:
- What are shared workflows?
- Why use WasteHero's shared workflows?
- High-level overview of available workflows
- How to reference them in your project

**What you'll learn:**
- The benefits of centralized workflow management
- The three types of workflows available
- Basic terminology

### 2. [Setting Up Your First CI Pipeline](getting-started-first-pipeline.md)
**Time: 20 minutes**

Build a working CI pipeline from scratch:
- Create a workflow file in your project
- Reference the shared workflows
- Run your first quality checks
- See the workflow execute

**What you'll learn:**
- How to create a workflow file
- How to structure a CI pipeline
- How to reference shared workflows correctly
- How to interpret GitHub Actions results

### 3. [Configuring Repository Secrets](configuring-repository-secrets.md)
**Time: 15 minutes**

Set up authentication and credentials:
- Understand what secrets are needed
- Configure ANTHROPIC_API_KEY
- Configure WasteHero PyPI credentials
- Verify secrets are working

**What you'll learn:**
- What each secret does
- How to add secrets to your repository
- Security best practices
- How to debug secret issues

### 4. [Running the Complete CI Pipeline](running-complete-ci-pipeline.md)
**Time: 25 minutes**

Build a production-ready pipeline with all components:
- Set up all required secrets
- Configure AI quality gates
- Add standard checks
- Set execution order
- Monitor and interpret results

**What you'll learn:**
- How to orchestrate multiple workflows
- Phase-based execution model
- How to use `needs:` to control flow
- How to interpret different check results

## Tutorials by Workflow Type

### For AI Quality Gates
- [Setting Up AI Quality Gates](setting-up-ai-quality-gates.md)
- [Understanding Quality Gate Results](understanding-quality-gate-results.md)

### For Standard Checks
- [Setting Up Standard Python Checks](setting-up-standard-checks.md)
- [Working with Type Hints for Type Checking](working-with-type-hints.md)

### For Composite Actions
- [Using the Setup Python Action](using-setup-python-action.md)
- [Using the Wait for Service Action](using-wait-for-service-action.md)

## Prerequisites

- A GitHub repository you own or have write access to
- Basic familiarity with GitHub Actions (or willingness to learn!)
- Knowledge of Python projects (for Python-specific workflows)
- A WasteHero PyPI account (for private dependency access)

## How to Use These Tutorials

Each tutorial follows this structure:
1. **Goal** - What you'll accomplish
2. **Prerequisites** - What you need before starting
3. **Steps** - Follow these in order
4. **Verification** - How to confirm it worked
5. **What's Next** - Where to go from here

## Tips for Learning

- **Follow in order** - Later tutorials build on earlier ones
- **Do it yourself** - Actually create the workflows and run them
- **Experiment** - Try different configurations and see what happens
- **Reference docs** - Use reference section to understand specific options
- **Check examples** - Look at real examples in reference documentation

## Troubleshooting

If you get stuck:
1. **Check the specific guide** - Most have troubleshooting sections
2. **Review the error message** - GitHub Actions usually tells you what's wrong
3. **Check the reference docs** - For detailed option documentation
4. **Review debugging guide** - See [How to Debug Workflow Failures](../how-to-guides/debugging-workflow-failures.md)

## Next Steps

After completing these tutorials, you'll be ready to:
- Use any workflow in isolation
- Combine workflows into pipelines
- Configure advanced options
- Troubleshoot issues yourself
- Contribute improvements

Check out the [How-To Guides](../how-to-guides/README.md) for solving specific problems beyond the basic tutorials.

## Time Commitment

- **Tutorials 1-2**: ~30 minutes to get first pipeline working
- **All tutorials**: ~2 hours for complete mastery
- **Reference lookups**: 5-10 minutes per topic as needed

Start with [Getting Started with Shared Workflows](getting-started-shared-workflows.md) and follow along!
