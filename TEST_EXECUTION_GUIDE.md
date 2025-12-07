# CT-1166 Final Testing Execution Guide

## Overview

This document guides the comprehensive final testing of all workflows and composite actions for CT-1166.

## Test Suites

### 1. Composite Actions Tests
**File**: `.github/workflows/tests/test-composite-actions.yml`

**Components Tested**:
- `setup-python-env` action (default and custom Python versions)
- `wait-for-service` action (error handling, timeout behavior)
- Output passing between workflow steps
- Composite action chaining

**Run with act**:
```bash
act workflow_dispatch -W .github/workflows/tests/test-composite-actions.yml -j test-setup-python-env
```

### 2. Standard Check Workflows Tests
**File**: `.github/workflows/tests/test-standard-checks.yml`

**Components Tested**:
- `python-lint.yml` workflow validation
- `python-type-check.yml` workflow validation
- `python-security-audit.yml` workflow validation
- Workflow structure and callability
- Permissions configuration

**Run with act**:
```bash
act workflow_dispatch -W .github/workflows/tests/test-standard-checks.yml
```

### 3. AI Quality Gate Workflows Tests
**File**: `.github/workflows/tests/test-ai-quality-gates.yml`

**Components Tested**:
- `python-quality-gate.yml` workflow validation
- `python-review-gate.yml` workflow validation
- Claude Code action configuration
- JSON schema validation setup
- Agent checkout mechanism
- PR integration

**Run with act**:
```bash
act workflow_dispatch -W .github/workflows/tests/test-ai-quality-gates.yml
```

### 4. Integration Tests
**File**: `.github/workflows/tests/test-integration.yml`

**Components Tested**:
- All YAML syntax validation
- Action references validation
- Composite action references
- Secret handling validation
- Permissions blocks validation
- Runner configuration
- File structure validation
- Documentation sync

**Run with act**:
```bash
act workflow_dispatch -W .github/workflows/tests/test-integration.yml
```

### 5. Master Test Orchestration
**File**: `.github/workflows/tests/run-all-tests.yml`

**Orchestrates**: All test suites with selective execution

**Run with act**:
```bash
act workflow_dispatch -W .github/workflows/tests/run-all-tests.yml
```

## Quick Start Testing

### Validate YAML Syntax Only
```bash
python3 << 'EOF'
import yaml
import os

yaml_files = [f for root, dirs, files in os.walk('.github')
              for f in [os.path.join(root, file) for file in files if file.endswith(('.yml', '.yaml'))]]

for filepath in sorted(yaml_files):
    try:
        with open(filepath) as f:
            yaml.safe_load(f)
        print(f"✓ {filepath}")
    except Exception as e:
        print(f"✗ {filepath}: {e}")
EOF
```

### Run Composite Action Tests with Act
```bash
cd /home/khalid/Projects/work/wastehero.io/devops/wastehero-github-actions

# Test setup-python-env action
act workflow_dispatch \
  -W .github/workflows/tests/test-composite-actions.yml \
  -j test-setup-python-env

# Test wait-for-service action
act workflow_dispatch \
  -W .github/workflows/tests/test-composite-actions.yml \
  -j test-wait-for-service
```

### Run Standard Checks Tests
```bash
act workflow_dispatch \
  -W .github/workflows/tests/test-standard-checks.yml \
  -j validate-lint-workflow
```

### Run Integration Tests
```bash
act workflow_dispatch \
  -W .github/workflows/tests/test-integration.yml \
  -j test-all-yaml-syntax
```

## Environment Setup for Full Testing

### Required Secrets (Local Testing)
Create a `.env` file for local testing with act:

```bash
# For AI quality gate testing
ANTHROPIC_API_KEY=sk-ant-<your-api-key>

# For type-check and security-audit
UV_INDEX_WASTEHERO_USERNAME=<username>
UV_INDEX_WASTEHERO_PASSWORD=<password>

# GitHub token (optional, auto-provided in GitHub Actions)
GITHUB_TOKEN=ghp_<your-token>
```

### Run with Secrets
```bash
act workflow_dispatch \
  -W .github/workflows/tests/test-composite-actions.yml \
  --secret-file .env
```

## Testing Checklist

### Phase 1: YAML Validation
- [x] All YAML files pass syntax validation
- [x] All workflow files are valid
- [x] All composite action files are valid

### Phase 2: Composite Actions
- [ ] `setup-python-env` action works with defaults
- [ ] `setup-python-env` action works with custom Python version
- [ ] `setup-python-env` outputs are captured correctly
- [ ] `setup-python-env` caching works
- [ ] `wait-for-service` action validates inputs
- [ ] `wait-for-service` action handles timeouts
- [ ] Composite action output passing works
- [ ] Composite action chaining works

### Phase 3: Standard Check Workflows
- [ ] `python-lint.yml` YAML is valid
- [ ] `python-lint.yml` is callable
- [ ] `python-lint.yml` has correct permissions
- [ ] `python-type-check.yml` YAML is valid
- [ ] `python-type-check.yml` uses setup-python-env
- [ ] `python-type-check.yml` references secrets
- [ ] `python-security-audit.yml` YAML is valid
- [ ] `python-security-audit.yml` uses setup-python-env
- [ ] All workflows have proper runner config

### Phase 4: AI Quality Gates
- [ ] `python-quality-gate.yml` YAML is valid
- [ ] `python-quality-gate.yml` is callable
- [ ] `python-quality-gate.yml` has required inputs
- [ ] `python-quality-gate.yml` has required secrets
- [ ] `python-quality-gate.yml` uses claude-code-action
- [ ] `python-quality-gate.yml` configures JSON schema
- [ ] `python-review-gate.yml` YAML is valid
- [ ] `python-review-gate.yml` is callable
- [ ] Quality gates checkout Claude agents
- [ ] Quality gates post to PR correctly

### Phase 5: Integration
- [ ] All workflows reference each other correctly
- [ ] No hardcoded credentials found
- [ ] All secrets properly referenced
- [ ] Permissions follow least-privilege
- [ ] Directory structure is complete
- [ ] Documentation is up-to-date
- [ ] No regressions from previous phases

## Expected Test Results

### YAML Validation
```
✓ PASS: .github/actions/setup-python-env/action.yml
✓ PASS: .github/actions/wait-for-service/action.yml
✓ PASS: .github/workflows/core/python-lint.yml
✓ PASS: .github/workflows/core/python-quality-gate.yml
✓ PASS: .github/workflows/core/python-review-gate.yml
✓ PASS: .github/workflows/core/python-security-audit.yml
✓ PASS: .github/workflows/core/python-type-check.yml
✓ PASS: All test workflows
```

### Component Status
- Composite Actions: ✓ FUNCTIONAL
- Standard Checks: ✓ VALIDATED
- AI Quality Gates: ✓ CONFIGURED
- Integration: ✓ COMPLETE

## Troubleshooting

### Act Warnings
If you see warnings about `act` runner images, use:
```bash
act -P ubuntu-latest=catthehacker/ubuntu:act-latest \
    -P self-hosted=catthehacker/ubuntu:act-latest
```

### Secret Issues in Local Testing
Ensure `.env` file is properly formatted:
```bash
# Correct format
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Incorrect format
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### Python Not Found
Install Python or ensure it's in PATH:
```bash
python3 --version
```

## Results Documentation

After testing, document findings in:
- **CT-1166 Testing Results** (Jira)
- **Test Execution Report** (GitHub Actions artifacts)
- **Repository** (this document)

## Next Steps After Testing

1. **Merge to main**: Once all tests pass, merge `feature/CT-1166-foundation-workflows`
2. **Deploy to production**: Enable workflows in target repositories
3. **Monitor execution**: Track workflow performance and costs
4. **Update documentation**: Keep reference docs current

## Support Resources

- GitHub Actions Docs: https://docs.anthropic.com/en/docs/about-claude/models/all-models
- Act Documentation: https://github.com/nektos/act
- Claude Code Action: https://github.com/anthropics/claude-code-action
- Workflow Syntax: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
