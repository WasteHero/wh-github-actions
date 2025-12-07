# Reference Documentation

Complete technical specifications for all workflows, actions, and configurations.

## Workflows

### AI-Powered Workflows

These workflows use Claude AI for intelligent code analysis:

| Workflow | Reference | Purpose |
|----------|-----------|---------|
| Python Quality Gate | [python-quality-gate-workflow.md](python-quality-gate-workflow.md) | AI code quality analysis |
| Python Review Gate | [python-review-gate-workflow.md](python-review-gate-workflow.md) | Comprehensive code review |

### Standard Check Workflows

Traditional automated code quality checks:

| Workflow | Reference | Purpose |
|----------|-----------|---------|
| Python Lint | [python-lint-workflow.md](python-lint-workflow.md) | Linting and formatting |
| Python Type Check | [python-type-check-workflow.md](python-type-check-workflow.md) | Type validation |
| Python Security Audit | [python-security-audit-workflow.md](python-security-audit-workflow.md) | Security scanning |

### Service Composition Workflows (Phase 2)

Service composition workflows validate the availability of external services (databases, caches, message brokers) in your CI/CD pipeline. These reusable workflows ensure services are fully operational before dependent tasks execute.

| Workflow | Reference | Service | Port |
|----------|-----------|---------|------|
| PostgreSQL Service | [postgresql-service-workflow.md](postgresql-service-workflow.md) | PostgreSQL 17-Alpine | 5432 |
| MongoDB Service | [mongodb-service-workflow.md](mongodb-service-workflow.md) | MongoDB 8.0 | 27017 |
| ValKey Service | [valkey-service-workflow.md](valkey-service-workflow.md) | ValKey 8.0-Alpine (Redis fork) | 6379 |
| NATS Service | [nats-service-workflow.md](nats-service-workflow.md) | NATS with JetStream | 4222 |
| Vault Service | [vault-service-workflow.md](vault-service-workflow.md) | HashiCorp Vault 1.18 | 8200 |

## Composite Actions

Reusable action building blocks:

| Action | Reference | Purpose |
|--------|-----------|---------|
| Setup Python Environment | [setup-python-env-action.md](setup-python-env-action.md) | Python + UV setup |
| Wait for Service | [wait-for-service-action.md](wait-for-service-action.md) | Service health checks |

## Configuration

### Secrets

| Secret | Reference | Purpose |
|--------|-----------|---------|
| All Required Secrets | [required-secrets.md](required-secrets.md) | Secret configuration |

## Quick Navigation

### Looking for...

**How to use a specific workflow?**
→ Find it in the Workflows table above and click the reference link

**Parameters and options for a workflow?**
→ Open the workflow reference page (linked above)

**Environment variables?**
→ See the specific workflow reference page

**Inputs and outputs?**
→ See the specific action reference page

**Security configuration?**
→ See [required-secrets.md](required-secrets.md)

## Workflow Specifications

Each workflow reference includes:

- **Purpose** - What the workflow does
- **Trigger** - How it gets invoked
- **Configuration** - Runtime settings
- **Inputs** - Parameters you provide
- **Outputs** - Results it produces
- **Secrets** - Required credentials
- **Permissions** - GitHub permissions needed
- **Usage** - How to call it
- **Behavior** - What happens when it runs
- **Performance** - Typical execution time
- **Troubleshooting** - Common issues

## Action Specifications

Each action reference includes:

- **Description** - What the action does
- **Usage** - How to use it
- **Inputs** - Input parameters
- **Outputs** - Output values
- **Exit Codes** - Success/failure indicators
- **Examples** - Real-world usage

## Secrets Reference

The [required-secrets.md](required-secrets.md) guide includes:

- **Secret name** - Exact name to use
- **Purpose** - What it's used for
- **Used by** - Which workflows need it
- **How to obtain** - Instructions to get it
- **Security notes** - Best practices
- **Troubleshooting** - Common issues

## Common Usage Patterns

### Minimal Pipeline (Lint Only)

```yaml
jobs:
  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main
```

See: [python-lint-workflow.md](python-lint-workflow.md)

### Complete Quality Pipeline

```yaml
jobs:
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

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

  review:
    needs: [lint, type-check, security-audit]
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-review-gate.yml@main
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### With PostgreSQL Service

Using the new service composition workflows:

```yaml
services:
  postgres:
    image: postgres:17-alpine
    env:
      POSTGRES_DB: testdb
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready
      --health-interval 2s
      --health-timeout 5s
      --health-retries 30
    ports:
      - 5432:5432

jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  tests:
    needs: postgres-service
    if: ${{ needs.postgres-service.outputs.postgres-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
```

See: [postgresql-service-workflow.md](postgresql-service-workflow.md)

### With Multiple Service Dependencies

```yaml
services:
  postgres:
    image: postgres:17-alpine
    env:
      POSTGRES_DB: testdb
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready
      --health-interval 2s
      --health-timeout 5s
      --health-retries 30
    ports:
      - 5432:5432

  mongodb:
    image: mongo:8.0
    options: >-
      --health-cmd mongosh
      --health-interval 2s
      --health-timeout 5s
      --health-retries 30
    ports:
      - 27017:27017

jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  mongodb-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main

  integration-tests:
    needs: [postgres-service, mongodb-service]
    if: |
      ${{ needs.postgres-service.outputs.postgres-ready == 'true' &&
          needs.mongodb-service.outputs.mongodb-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --integration
```

See: [postgresql-service-workflow.md](postgresql-service-workflow.md) and [mongodb-service-workflow.md](mongodb-service-workflow.md)

### Complete Multi-Service Stack (Phase 2)

Example with all Phase 2 services: PostgreSQL, MongoDB, ValKey cache, NATS messaging, and Vault secrets:

```yaml
services:
  postgres:
    image: postgres:17-alpine
    env:
      POSTGRES_DB: testdb
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready
      --health-interval 2s
      --health-timeout 5s
      --health-retries 30
    ports:
      - 5432:5432

  mongodb:
    image: mongo:8.0
    options: >-
      --health-cmd mongosh
      --health-interval 2s
      --health-timeout 5s
      --health-retries 30
    ports:
      - 27017:27017

  valkey:
    image: valkey:8.0-alpine
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 2s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 6379:6379

  nats:
    image: nats:latest
    command: "nats-server -js"
    options: >-
      --health-cmd "nats-cli server check"
      --health-interval 2s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 4222:4222
      - 8222:8222

  vault:
    image: hashicorp/vault:1.18
    env:
      VAULT_DEV_ROOT_TOKEN_ID: dev-token
      VAULT_DEV_LISTEN_ADDRESS: "0.0.0.0:8200"
    options: >-
      --health-cmd "vault status"
      --health-interval 2s
      --health-timeout 5s
      --health-retries 5
      --cap-add IPC_LOCK
    ports:
      - 8200:8200

jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  mongodb-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main

  valkey-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main

  nats-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main

  vault-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main

  integration-tests:
    needs: [postgres-service, mongodb-service, valkey-service, nats-service, vault-service]
    if: |
      ${{ needs.postgres-service.outputs.postgres-ready == 'true' &&
          needs.mongodb-service.outputs.mongodb-ready == 'true' &&
          needs.valkey-service.outputs.valkey-ready == 'true' &&
          needs.nats-service.outputs.nats-ready == 'true' &&
          needs.vault-service.outputs.vault-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
      MONGODB_URI: mongodb://localhost:27017/testdb
      REDIS_URL: redis://localhost:6379/0
      NATS_URL: nats://localhost:4222
      VAULT_ADDR: http://localhost:8200
      VAULT_TOKEN: dev-token
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --integration --all-services
```

See: [postgresql-service-workflow.md](postgresql-service-workflow.md), [mongodb-service-workflow.md](mongodb-service-workflow.md), [valkey-service-workflow.md](valkey-service-workflow.md), [nats-service-workflow.md](nats-service-workflow.md), and [vault-service-workflow.md](vault-service-workflow.md)

## Version References

### Workflow Versions

Use one of:
- `@main` - Latest version (recommended for active development)
- `@v1.0` - Specific release tag (recommended for stability)
- `@abc123` - Specific commit hash (maximum control)

### Finding Available Versions

Check the [WasteHero GitHub Actions releases](https://github.com/WasteHero/wastehero-github-actions/releases)

## Environment Variables

### Standard Workflow Environment

All workflows have access to standard GitHub variables:
- `${{ github.repository }}` - Owner/repo
- `${{ github.event.pull_request.number }}` - PR number
- `${{ secrets.GITHUB_TOKEN }}` - GitHub token

See specific workflow reference for additional env vars.

## Permissions Reference

### Default Permissions

Most workflows use:
```yaml
permissions:
  contents: read
```

### Workflows with Additional Permissions

| Workflow | Additional | Reason |
|----------|-----------|--------|
| Python Lint | `pull-requests: write` | Posts comments to PR |
| Python Quality Gate | `pull-requests: write` | Posts findings to PR |
| Python Review Gate | `pull-requests: write` | Posts review to PR |
| Python Security Audit | `security-events: write` | Creates security alerts |

## Performance Characteristics

Approximate execution times (on self-hosted K8s runners):

| Workflow | Time | Notes |
|----------|------|-------|
| Python Lint | 30s | No dependencies needed |
| Python Type Check | 60-120s | Includes dependency install |
| Python Security Audit | 60-120s | Includes dependency install |
| Python Quality Gate | 30-60s | Depends on code size |
| Python Review Gate | 60-120s | Depends on code size |

### Cache Performance

With cache hits:
- Type Check: ~45s (down from 120s)
- Security Audit: ~45s (down from 120s)
- Lint: ~20s (already fast)

## File Organization

```
.github/
├── actions/
│   ├── setup-python-env/
│   │   └── action.yml
│   └── wait-for-service/
│       └── action.yml
└── workflows/
    └── core/
        ├── python-lint.yml
        ├── python-type-check.yml
        ├── python-security-audit.yml
        ├── python-quality-gate.yml
        └── python-review-gate.yml
```

## Troubleshooting Quick Reference

| Issue | Reference |
|-------|-----------|
| Workflow not triggering | [Debugging Workflow Failures](../how-to-guides/debugging-workflow-failures.md) |
| Secret not found | [required-secrets.md](required-secrets.md) |
| Authentication failed | [required-secrets.md](required-secrets.md) |
| Slow execution | [python-type-check-workflow.md](python-type-check-workflow.md#performance) |
| False positive findings | [python-security-audit-workflow.md](python-security-audit-workflow.md#suppressing-findings) |

## Links to Detailed References

Ready to dive into the details? Choose your workflow:

### Code Quality & Analysis Workflows

1. **[Python Lint Workflow](python-lint-workflow.md)** - Linting and formatting specs
2. **[Python Type Check Workflow](python-type-check-workflow.md)** - Type checking specs
3. **[Python Security Audit Workflow](python-security-audit-workflow.md)** - Security specs
4. **[Python Quality Gate Workflow](python-quality-gate-workflow.md)** - AI quality specs
5. **[Python Review Gate Workflow](python-review-gate-workflow.md)** - AI review specs

### Service Composition Workflows

6. **[PostgreSQL Service Workflow](postgresql-service-workflow.md)** - PostgreSQL readiness specs
7. **[MongoDB Service Workflow](mongodb-service-workflow.md)** - MongoDB readiness specs
8. **[ValKey Service Workflow](valkey-service-workflow.md)** - ValKey (Redis fork) readiness specs
9. **[NATS Service Workflow](nats-service-workflow.md)** - NATS message broker with JetStream specs
10. **[Vault Service Workflow](vault-service-workflow.md)** - HashiCorp Vault secrets management specs

### Configuration

11. **[Required Secrets](required-secrets.md)** - Secret configuration specs

---

**Looking for how to do something?** Check the [How-To Guides](../how-to-guides/README.md)

**Want to understand the concepts?** Check the [Explanation](../explanation/README.md)

**Getting started?** Check the [Tutorials](../tutorials/README.md)
