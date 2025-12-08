# Python Tests Workflow Reference

**Reference:** CT-1186
**Status:** Production
**Last Updated:** December 7, 2025

## Overview

The Python Tests workflow orchestrates dynamic service composition for Python test execution with optional database, cache, and message broker dependencies. It supports multiple Python versions via matrix testing and flexible service configuration.

| Property | Value |
|----------|-------|
| Purpose | Python test execution with optional service dependencies |
| Trigger | workflow_call |
| Inputs | 8 (service toggles + configuration) |
| Secrets | 2 (UV_INDEX credentials) |
| Outputs | test-result (if implemented) |
| Runner | [self-hosted, linux, X64, kubernetes] |
| Python Versions | 3.11, 3.12, 3.13 (via matrix) |
| Services Supported | PostgreSQL, MongoDB, ValKey, NATS, Vault |
| Default Timeout | 30 minutes |
| File Location | `.github/workflows/services/python-tests.yml` |

## Purpose

Execute Python tests with optional dynamic service composition:
- **Flexible Service Configuration**: Enable/disable PostgreSQL, MongoDB, ValKey, NATS, Vault independently
- **Matrix Testing**: Test against multiple Python versions (3.11, 3.12, 3.13) simultaneously
- **Dependency Management**: Automatically wait for service readiness before tests
- **Custom Test Arguments**: Pass pytest arguments and configure timeout per run
- **Private PyPI**: Access WasteHero private Python package index via UV
- **Self-Hosted Runners**: Designed for Kubernetes-based self-hosted runner infrastructure

## Trigger

`workflow_call` - Called as a reusable workflow from consuming repositories.

## Basic Usage

### Minimal Configuration (Default Python 3.13, No Services)

```yaml
jobs:
  tests:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Multi-Version Testing (Python 3.11, 3.12, 3.13)

```yaml
jobs:
  tests:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    with:
      python-versions: '["3.11", "3.12", "3.13"]'
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### With PostgreSQL Service

```yaml
services:
  postgres:
    image: postgres:17-alpine
    env:
      POSTGRES_DB: testdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready
      --health-interval 2s
      --health-timeout 5s
      --health-retries 30
    ports:
      - 5432:5432

jobs:
  tests:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    with:
      enable-postgresql: true
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Full Stack (All Services: PostgreSQL, MongoDB, ValKey, NATS, Vault)

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
  tests:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    with:
      enable-postgresql: true
      enable-mongodb: true
      enable-valkey: true
      enable-nats: true
      enable-vault: true
      python-versions: '["3.11", "3.12", "3.13"]'
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

## Inputs Documentation

All inputs are optional and have sensible defaults.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| enable-postgresql | boolean | false | Enable PostgreSQL 17-Alpine service dependency and wait for readiness |
| enable-mongodb | boolean | false | Enable MongoDB 8.0 service dependency and wait for readiness |
| enable-valkey | boolean | false | Enable ValKey 8.0-Alpine (Redis fork) service dependency and wait for readiness |
| enable-nats | boolean | false | Enable NATS with JetStream service dependency and wait for readiness |
| enable-vault | boolean | false | Enable HashiCorp Vault 1.18 service dependency and wait for readiness |
| python-versions | string | ["3.13"] | JSON array of Python versions to test. Supports "3.11", "3.12", "3.13" |
| pytest-args | string | tests/ -v | Arguments passed to pytest command (e.g., "tests/ -v --tb=short") |
| test-timeout | number | 30 | Test job timeout in minutes (max 360) |

### Input Details

#### enable-postgresql

Enable PostgreSQL 17-Alpine database service. When true:
- Workflow waits for PostgreSQL port 5432 to be ready
- Sets `POSTGRES_URL` environment variable: `postgresql://localhost:5432`
- Requires service container defined in consuming workflow

#### enable-mongodb

Enable MongoDB 8.0 document database service. When true:
- Workflow waits for MongoDB port 27017 to be ready
- Sets `MONGODB_URL` environment variable: `mongodb://localhost:27017`
- Requires service container defined in consuming workflow

#### enable-valkey

Enable ValKey 8.0-Alpine (Redis-compatible) cache service. When true:
- Workflow waits for ValKey port 6379 to be ready
- Sets `VALKEY_URL` environment variable: `valkey://localhost:6379/0`
- Requires service container defined in consuming workflow

#### enable-nats

Enable NATS with JetStream message broker service. When true:
- Workflow waits for NATS port 4222 to be ready
- Sets `NATS_URL` environment variable: `nats://localhost:4222`
- Requires service container defined in consuming workflow

#### enable-vault

Enable HashiCorp Vault secrets management service. When true:
- Workflow waits for Vault port 8200 to be ready
- Sets `VAULT_ADDR` environment variable: `http://localhost:8200`
- Sets `VAULT_TOKEN` environment variable: `dev-token` (for dev mode)
- Requires service container defined in consuming workflow

#### python-versions

JSON array string of Python versions to test in matrix. Examples:
- `'["3.13"]'` - Single version (default)
- `'["3.12", "3.13"]'` - Two versions
- `'["3.11", "3.12", "3.13"]'` - All supported versions

The matrix expands to run tests for each version independently. Results show pass/fail per version.

#### pytest-args

Arguments passed directly to pytest command. Examples:
- `tests/ -v` - Verbose test discovery from tests/ directory (default)
- `tests/ -v --tb=short` - Shorter traceback format
- `tests/unit -v` - Only unit tests
- `tests/ -v -k 'not integration'` - Skip integration tests
- `tests/ -v --cov=myapp` - With coverage reporting

#### test-timeout

Maximum time in minutes to allow test job to run. If exceeded, job fails immediately.

Recommendations:
- Unit tests only: 10-15 minutes
- Unit + integration: 20-30 minutes (default)
- With all services: 30-45 minutes
- Performance/load tests: 45-60 minutes

## Secrets

Two secrets are **required** for this workflow to function.

| Secret | Type | Required | Description |
|--------|------|----------|-------------|
| UV_INDEX_WASTEHERO_USERNAME | string | true | Username for WasteHero private PyPI index |
| UV_INDEX_WASTEHERO_PASSWORD | string | true | Password/token for WasteHero private PyPI index |

### Secret Setup

Store these secrets in your GitHub repository settings:

1. Go to repository Settings → Secrets and variables → Actions
2. Create `UV_INDEX_WASTEHERO_USERNAME` with your username
3. Create `UV_INDEX_WASTEHERO_PASSWORD` with your access token
4. Reference in workflow: `secrets: { UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}, ... }`

See [Required Secrets](./required-secrets.md) for detailed setup instructions.

## Configuration

### Runtime

- **Runs on:** `[self-hosted, linux, X64, kubernetes]`
- **Python Versions:** 3.11, 3.12, 3.13 (configurable via matrix)
- **Timeout:** Per-job timeout via `test-timeout` input (default 30 minutes)
- **Overall Timeout:** 5 minutes (standard GitHub Actions limit per job)
- **Matrix Strategy:** fail-fast: false (all versions test even if one fails)

### Permissions

```yaml
permissions:
  contents: read
```

## What It Does

### Step 1: Checkout Code

```bash
uses: actions/checkout@v4
```

Clones repository with full history to access source code and tests.

### Step 2: Setup Python Environment

```bash
uses: ./.github/actions/setup-python-env
with:
  python-version: ${{ matrix.python-version }}
```

Uses the `setup-python-env` composite action to:
- Install specified Python version (3.11, 3.12, or 3.13)
- Install UV package manager
- Set up development environment
- Configure Python for test execution

See [Setup Python Environment Action](./setup-python-env-action.md) for details.

### Step 3-7: Wait for Services (Conditional)

```bash
uses: ./.github/actions/wait-for-service
with:
  service-type: 'postgres'
  host: 'localhost'
  port: '5432'
  max-retries: 30
```

Executed only if corresponding service is enabled via input. Each service wait step:
- Tests TCP connectivity on specified port
- Retries up to 30 times with 2-second intervals
- Succeeds when port becomes available (60 seconds max)
- Fails and stops test job if service unavailable

Services waited for (in order):
1. PostgreSQL (5432) - if `enable-postgresql: true`
2. MongoDB (27017) - if `enable-mongodb: true`
3. ValKey (6379) - if `enable-valkey: true`
4. NATS (4222) - if `enable-nats: true`
5. Vault (8200) - if `enable-vault: true`

See [Wait for Service Action](./wait-for-service-action.md) for details.

### Step 8: Install Dependencies

```bash
uv sync --extra-index-url https://${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}:${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}@pypi.wastehero.io/team/wastehero_libraries/+simple/
```

Installs Python dependencies using UV with:
- PyPI standard index (public packages)
- WasteHero private PyPI index (private packages)
- Credentials from secrets (injected at runtime)
- Dependency locking via uv.lock file

This step:
- Reads pyproject.toml and/or requirements files
- Resolves all transitive dependencies
- Downloads from both public and private indexes
- Caches dependencies when possible
- Fails if any dependency cannot be found or installed

### Step 9: Run Tests

```bash
uv run pytest ${{ inputs.pytest-args }}
timeout-minutes: ${{ inputs.test-timeout }}
```

Executes pytest with:
- Arguments provided via `pytest-args` input
- Virtual environment from UV
- Timeout configured via `test-timeout` input
- Environment variables for all enabled services

## Service Orchestration

### How Services Are Managed

The python-tests workflow implements **decoupled service orchestration**:

1. **Service Definition** - You define service containers in your consuming workflow with proper Docker health checks
2. **Runner Infrastructure** - Self-hosted Kubernetes runner automatically starts service containers on the same network
3. **Service Discovery** - Services accessible via `localhost` (K8s network linking)
4. **Readiness Validation** - Workflow uses wait-for-service action to verify each service
5. **Environment Setup** - Automatically sets service URLs as environment variables
6. **Conditional Execution** - Service waits only execute if corresponding input flag is true

### Service Container Setup

For each service you want to use, define it in your consuming workflow's `services` block:

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
```

Health checks are critical - they enable fast detection of service readiness.

### Environment Variables

The workflow automatically makes these environment variables available to pytest:

| Variable | Set When | Value | Usage |
|----------|----------|-------|-------|
| POSTGRES_URL | enable-postgresql | postgresql://localhost:5432 | Database connection |
| MONGODB_URL | enable-mongodb | mongodb://localhost:27017 | Document store connection |
| VALKEY_URL | enable-valkey | valkey://localhost:6379/0 | Cache connection |
| NATS_URL | enable-nats | nats://localhost:4222 | Message broker URL |
| VAULT_ADDR | enable-vault | http://localhost:8200 | Vault server address |
| VAULT_TOKEN | enable-vault | dev-token | Vault authentication token |

Use these variables in your test configuration:

```python
# tests/conftest.py
import os
import pytest

@pytest.fixture(scope="session")
def db_url():
    return os.environ.get("POSTGRES_URL", "postgresql://localhost:5432")

@pytest.fixture(scope="session")
def cache_url():
    return os.environ.get("VALKEY_URL", "valkey://localhost:6379/0")
```

## Matrix Testing

### Python Version Matrix

The workflow uses GitHub Actions matrix to test multiple Python versions in parallel:

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ${{ fromJson(inputs.python-versions) }}
```

### How Matrix Expansion Works

When you provide `python-versions: '["3.11", "3.12", "3.13"]'`:

1. The `fromJson()` function parses the JSON string to an array
2. GitHub Actions creates one job per Python version
3. Each job runs independently with its own Python version
4. Job name shows version: "Test with Python 3.11", "Test with Python 3.12", etc.
5. All jobs run in parallel (scheduler permitting)
6. Results show separately per version

**Example:** With 3 Python versions and 2 service combinations:
- 6 total test jobs created
- Each runs independently
- Can see exactly which versions pass/fail
- Total runtime ~same as 1 version (parallel execution)

### Matrix Best Practices

1. **Test realistic versions** - Include versions your users might use
2. **Start with latest** - Python 3.13 first, then 3.12, then 3.11
3. **Don't test too many** - 3 versions is typical, more slows CI
4. **Consider OS** - All use same Linux runner, so OS differences minimal
5. **Name jobs clearly** - Matrix shows version in job name automatically

## Common Issues and Fixes

### Issue: Service Not Starting

**Cause:** Service container failed to start or runner can't reach it.

**Fix:**
1. Verify service container definition has proper health check
2. Check Docker image is correct: `postgres:17-alpine`, `mongo:8.0`, etc.
3. Ensure port mappings are correct: `- 5432:5432`
4. Check runner has enough resources (K8s nodes available)
5. Enable runner debug output for more details

```yaml
services:
  postgres:
    image: postgres:17-alpine
    env:
      POSTGRES_DB: testdb
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready      # Health check CRITICAL
      --health-interval 2s
      --health-timeout 5s
      --health-retries 30
    ports:
      - 5432:5432                  # Port mapping CRITICAL
```

### Issue: Port Conflicts

**Cause:** Another job or process is using the same port.

**Fix:**
1. Use unique ports for parallel jobs if needed
2. Check runner isn't running other services
3. Wait for previous job to finish before starting new one

```yaml
jobs:
  tests:
    # ... prevents parallel execution on same runner
    runs-on: [self-hosted, linux, X64, kubernetes]
```

### Issue: Dependency Installation Errors

**Cause:** Missing private PyPI credentials or dependency not available.

**Error message:** `ERROR: Could not find a version...` or `401 Unauthorized`

**Fix:**
1. Verify UV_INDEX secrets are set in repository settings
2. Check secrets have correct username/password
3. Verify private package exists in WasteHero index
4. Check pyproject.toml dependencies are correct
5. Try installing manually locally with credentials

```bash
uv sync --extra-index-url https://username:password@pypi.wastehero.io/team/wastehero_libraries/+simple/
```

### Issue: Pytest Fails with ModuleNotFoundError

**Cause:** Dependencies not installed or Python path incorrect.

**Error:** `ModuleNotFoundError: No module named 'mypackage'`

**Fix:**
1. Verify pyproject.toml or requirements.txt lists the package
2. Check uv sync completed successfully
3. Verify package is in private PyPI if private package
4. Check pytest is discovering tests correctly

```bash
# Test locally
uv sync
uv run pytest tests/ -v
```

### Issue: Services Timeout (Fails After 60 Seconds)

**Cause:** Service taking longer than expected to start, or health checks failing.

**Fix:**
1. Check runner resource availability - services need CPU/memory
2. Verify health check configuration is reasonable
3. Consider using lightweight images: `postgres:17-alpine` not `postgres:17`
4. Increase `max-retries` if needed (30 is default for 60 seconds total)

```yaml
services:
  postgres:
    options: >-
      --health-cmd pg_isready
      --health-interval 2s        # Check every 2s
      --health-timeout 5s         # Allow 5s per check
      --health-retries 40         # 80s total wait instead of 60s
```

### Issue: Matrix Expands to Too Many Jobs

**Cause:** Providing too many Python versions creates job explosion.

**Fix:**
1. Reduce to 2-3 Python versions
2. Only test versions you actually support
3. Consider using only latest version for pre-commit checks

```yaml
# Good - 3 jobs
python-versions: '["3.11", "3.12", "3.13"]'

# Too many - 10 jobs!
python-versions: '["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]'
```

### Issue: Tests Pass Locally but Fail in Workflow

**Cause:** Environment differences or missing service setup.

**Fix:**
1. Run services locally (Docker) to match CI environment
2. Use same pytest arguments as workflow
3. Set environment variables locally: `export POSTGRES_URL=...`
4. Check Python versions match (3.11 vs 3.13 behavior differences)

```bash
# Replicate CI locally
docker run --rm -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:17-alpine
uv sync
POSTGRES_URL=postgresql://localhost:5432 uv run pytest tests/ -v
docker stop postgres
```

### Issue: Timeout During Test Execution

**Cause:** Tests take longer than `test-timeout` setting.

**Error:** `The operation timed out`

**Fix:**
1. Increase `test-timeout` input
2. Optimize slow tests
3. Split tests into smaller suites
4. Run slow tests separately with longer timeout

```yaml
jobs:
  tests:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    with:
      test-timeout: 45  # Increase from default 30
```

### Issue: Matrix Version Not Running

**Cause:** JSON parsing failed for python-versions input.

**Error:** `Invalid JSON` or only one version runs

**Fix:**
1. Use proper JSON array format: `'["3.11", "3.12", "3.13"]'`
2. Single quotes around entire string (not double quotes)
3. Test parsing locally with Python
4. Match exact version strings (no "3.11.0", just "3.11")

```python
import json
# Test your JSON string
versions = json.loads('["3.11", "3.12", "3.13"]')
print(versions)  # ['3.11', '3.12', '3.13']
```

## Integration Patterns

### Pattern 1: Microservice Testing

Test service components that depend on databases:

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  tests:
    needs: postgres-service
    if: ${{ needs.postgres-service.outputs.postgres-ready == 'true' }}
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    with:
      enable-postgresql: true
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Pattern 2: Database Migration Testing

Test database migrations against real PostgreSQL:

```yaml
services:
  postgres:
    image: postgres:17-alpine
    env:
      POSTGRES_DB: testdb
      POSTGRES_PASSWORD: postgres
    ports:
      - 5432:5432

jobs:
  migrations:
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: python -m alembic upgrade head
        env:
          POSTGRES_URL: postgresql://postgres:postgres@localhost:5432/testdb

  tests:
    needs: migrations
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    with:
      enable-postgresql: true
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Pattern 3: Multi-Database Compatibility

Test against multiple databases in parallel:

```yaml
jobs:
  tests-postgres:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    with:
      enable-postgresql: true
      python-versions: '["3.13"]'
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}

  tests-mongodb:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    with:
      enable-mongodb: true
      python-versions: '["3.13"]'
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Pattern 4: Performance Testing with Services

Run performance benchmarks with real services:

```yaml
jobs:
  performance-tests:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    with:
      enable-postgresql: true
      enable-valkey: true
      pytest-args: 'tests/performance -v --benchmark-only'
      test-timeout: 60
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

### Pattern 5: Integration Test Suite with Full Stack

Test entire application stack:

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

jobs:
  integration-tests:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/python-tests.yml@main
    with:
      enable-postgresql: true
      enable-mongodb: true
      enable-valkey: true
      enable-nats: true
      python-versions: '["3.11", "3.12", "3.13"]'
      pytest-args: 'tests/integration -v'
      test-timeout: 45
    secrets:
      UV_INDEX_WASTEHERO_USERNAME: ${{ secrets.UV_INDEX_WASTEHERO_USERNAME }}
      UV_INDEX_WASTEHERO_PASSWORD: ${{ secrets.UV_INDEX_WASTEHERO_PASSWORD }}
```

## Performance Characteristics

### Typical Execution Times

On self-hosted Kubernetes runners with cached dependencies:

| Scenario | Time | Notes |
|----------|------|-------|
| No services, single version | 2-3 min | Setup + test execution |
| With 1 service | 2.5-3.5 min | +30s service startup |
| With 2-3 services | 3-4 min | ~30s per service in parallel |
| With all 5 services | 4-5 min | All services start in parallel |
| 3 Python versions, no services | 6-9 min | 3 jobs × 2-3 min each |
| 3 versions + 3 services | 12-15 min | 3 jobs × (3-4 min + service wait) |

### Performance Optimization Tips

1. **Use dependency caching** - UV caches dependencies, reuse across runs
2. **Minimize services** - Only enable services actually needed
3. **Reduce Python versions** - Test fewer versions for faster feedback
4. **Optimize tests** - Use pytest markers to skip slow tests in quick runs
5. **Parallelize CI** - Run different test categories in parallel jobs
6. **Alpine images** - Lightweight service images start faster
7. **Health checks** - Proper Docker health checks enable faster readiness

### Scaling Considerations

With many Python versions and services:
- Each version runs independently (can fill runner queue)
- Services start in parallel when possible
- Monitor runner utilization in GitHub Actions
- Consider limiting matrix to 2-3 versions for pre-commit
- Use full matrix only for main branch/releases

## Best Practices

1. **Define all services in consuming workflow** - Not in python-tests workflow itself
2. **Use health checks** - Docker health checks critical for fast service readiness detection
3. **Only enable needed services** - Each service adds ~30s startup time
4. **Version-specific constraints** - Use `python-versions` for target versions only
5. **Configure pytest correctly** - Match local development setup in pytest-args
6. **Handle missing services gracefully** - Your code should work with/without services
7. **Test realistic scenarios** - Use same services in CI as in production
8. **Document service requirements** - README should list what services are needed
9. **Security**: Never hardcode credentials, use secrets exclusively
10. **Permissions minimal** - Workflow only reads repository contents

## Related Documentation

- [PostgreSQL Service Workflow](./postgresql-service-workflow.md) - PostgreSQL service validation
- [MongoDB Service Workflow](./mongodb-service-workflow.md) - MongoDB service validation
- [ValKey Service Workflow](./valkey-service-workflow.md) - ValKey cache service validation
- [NATS Service Workflow](./nats-service-workflow.md) - NATS message broker validation
- [Vault Service Workflow](./vault-service-workflow.md) - Vault secrets management validation
- [Setup Python Environment Action](./setup-python-env-action.md) - Python environment setup details
- [Wait for Service Action](./wait-for-service-action.md) - Service readiness validation details
- [Required Secrets](./required-secrets.md) - Secret configuration guide
- [How to Debug Workflow Failures](../how-to-guides/debugging-workflow-failures.md) - Troubleshooting guide

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 7, 2025 | Initial release, supports PostgreSQL, MongoDB, ValKey, NATS, Vault with Python matrix testing |

---

**Questions?** See [How-To Guides](../how-to-guides/README.md) for common problems or [Explanation](../explanation/README.md) for conceptual understanding.
