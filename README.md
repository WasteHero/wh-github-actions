# WasteHero GitHub Actions

Shared and reusable GitHub Actions workflows for all WasteHero projects.

## Overview

This repository contains centralized GitHub Actions workflows that can be reused across all WasteHero organization repositories. This approach ensures consistency, reduces duplication, and simplifies maintenance of CI/CD pipelines.

## Workflows

### AI PR Workflows

Automated workflows that leverage AI to enhance pull request processes, including:
- Automated code reviews
- PR description generation
- Code quality analysis
- Automated testing and validation

## Usage

To use these shared workflows in your WasteHero project, reference them in your repository's workflow file:

```yaml
name: My Workflow
on: [pull_request]

jobs:
  call-shared-workflow:
    uses: WasteHero/wh-github-actions/.github/workflows/workflow-name.yml@main
    secrets: inherit
```

## Contributing

When adding or modifying workflows:
1. Ensure workflows are generalized for use across multiple projects
2. Document any required secrets or inputs
3. Test changes thoroughly before merging to main
4. Update this README with new workflow documentation

## Support

For questions or issues with these workflows, please contact the DevOps team or open an issue in this repository.
