# PostgreSQL Service Workflow Reference

**Reference:** CT-1184
**Status:** Production
**Last Updated:** December 7, 2025

## Overview

The PostgreSQL Service workflow validates the readiness and connectivity of a PostgreSQL 17-Alpine database service within your CI/CD pipeline.

| Property | Value |
|----------|-------|
| Purpose | PostgreSQL service readiness validation |
| Trigger | workflow_call |
| Service Version | PostgreSQL 17-Alpine |
| Default Port | 5432 |
| Outputs | postgres-ready (boolean) |
| Secrets Required | None |
| Permissions Required | contents: read |
| Runner | self-hosted, linux, X64, kubernetes |
| Typical Duration | ~60 seconds (30 retries × 2 seconds) |
| File Location | `.github/workflows/services/postgresql-service.yml` |

## Purpose

Ensure PostgreSQL database service is fully operational before running dependent tasks:
- **Connection Validation**: Confirms the database accepts connections on the expected port
- **Health Status**: Verifies the service is responding to health checks
- **Database Connectivity**: Tests actual SQL query execution
- **Self-Hosted Runner Support**: Designed for Kubernetes-based self-hosted runners
- **Service Composition**: First phase of multi-service orchestration pattern

## Trigger

`workflow_call` - Called as a reusable workflow from consuming repositories.

## Basic Usage

### Minimal Configuration

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main
```

### With Service Container

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
      --health-retries 5

jobs:
  postgres-service:
    services:
      postgres: ${{ env.services.postgres }}
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main
```

### In Test Pipeline

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  integration-tests:
    needs: postgres-service
    runs-on: [self-hosted, linux, X64, kubernetes]
    if: ${{ needs.postgres-service.outputs.postgres-ready == 'true' }}
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --reporter=json
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
```

## Outputs

The workflow exposes one output:

| Output | Type | Description |
|--------|------|-------------|
| postgres-ready | string ('true' or 'false') | Whether PostgreSQL service is ready and accepting connections |

### Using Outputs

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  tests:
    needs: postgres-service
    runs-on: ubuntu-latest
    if: ${{ needs.postgres-service.outputs.postgres-ready == 'true' }}
    steps:
      - run: echo "PostgreSQL is ready, running tests"
```

## Secrets

**No secrets required.** The workflow uses default PostgreSQL connection parameters.

## Configuration

### Runtime

- **Runs on:** `[self-hosted, linux, X64, kubernetes]`
- **Timeout:** 5 minutes (standard GitHub Actions limit)
- **Service Port:** 5432 (default PostgreSQL port)
- **Retry Strategy:** 30 retries with 2-second intervals
- **Total Wait Time:** Up to 60 seconds

### Permissions

```yaml
permissions:
  contents: read
```

## What It Does

### Step 1: Wait for PostgreSQL Service

```bash
uses: ./.github/actions/wait-for-service
with:
  service-type: postgres
  host: localhost
  port: '5432'
  max-retries: '30'
```

This step uses the `wait-for-service` composite action to poll the PostgreSQL port:
- Tests TCP connection to `localhost:5432`
- Retries up to 30 times with 2-second intervals between attempts
- Succeeds when port becomes available
- Fails if port never becomes available within 60 seconds
- Sets output `ready: 'true'` on success, `'false'` on failure

**Expected behavior:**
- Service starting: "Waiting for service to be ready"
- Service ready: "Service is ready"
- Service failed: "Service failed to start within timeout"

### Step 2: Verify PostgreSQL Connection

```bash
psql postgresql://localhost:5432/testdb -c 'SELECT 1'
```

This step confirms the database is not only accepting connections but can execute SQL:
- Connects using `psql` command-line client
- Executes a simple health-check query: `SELECT 1`
- Fails if database is not responding correctly
- Validates the service is fully operational (not just listening on the port)

**Expected behavior:**
- Success: Returns `1` (one row with value 1)
- Failure: Connection refused or query execution error

## Environment Setup

### PostgreSQL Container Configuration

For the service to be available, you need to configure the PostgreSQL container in your workflow:

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
      --health-retries 5
    ports:
      - 5432:5432
```

### Database Credentials

Default test configuration uses:
- **Host:** localhost
- **Port:** 5432
- **Database:** testdb
- **User:** postgres (default)
- **Password:** postgres (default)

Customize these values by modifying your service container environment variables.

## Common Issues and Fixes

### Issue: "Connection refused" error

**Cause:** PostgreSQL service container is not running or port is not exposed.

**Fix:**
1. Verify service container is defined in your workflow
2. Ensure port mapping is correct: `5432:5432`
3. Check that image is `postgres:17-alpine` or compatible version
4. Add health check configuration to services

```yaml
services:
  postgres:
    image: postgres:17-alpine
    ports:
      - 5432:5432  # Required
    options: >-
      --health-cmd pg_isready
      --health-interval 2s
```

### Issue: "psql: command not found"

**Cause:** PostgreSQL client tools are not installed in the runner environment.

**Fix:** The wait-for-service action only tests TCP connectivity. The psql verification step requires psql to be installed:

```bash
# If using Ubuntu runner, install postgresql-client
- name: Install PostgreSQL client
  run: sudo apt-get install -y postgresql-client

# Then run the service workflow
- uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main
```

Or use Docker image with PostgreSQL tools pre-installed:

```bash
docker run -it postgres:17-alpine psql postgresql://localhost:5432/testdb -c 'SELECT 1'
```

### Issue: "database 'testdb' does not exist"

**Cause:** PostgreSQL service not initialized with the expected database.

**Fix:** Ensure the POSTGRES_DB environment variable is set:

```yaml
services:
  postgres:
    image: postgres:17-alpine
    env:
      POSTGRES_DB: testdb  # Required
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
```

### Issue: Timeout waiting for PostgreSQL (fails after 60 seconds)

**Cause:** Service taking longer than expected to start, or health checks are failing.

**Fix:**
1. Check runner resource availability - PostgreSQL needs memory to start
2. Verify health check interval is reasonable:

```yaml
services:
  postgres:
    image: postgres:17-alpine
    options: >-
      --health-cmd pg_isready
      --health-interval 2s        # Check every 2 seconds
      --health-timeout 5s         # Allow 5s per check
      --health-retries 30         # Try 30 times max
```

3. Increase runner capacity if available
4. Check Docker image is not corrupted: `docker pull postgres:17-alpine`

### Issue: Port 5432 already in use

**Cause:** Another service is already running on port 5432.

**Fix:**
1. Stop any local PostgreSQL instances
2. Use different port in workflow:

```yaml
services:
  postgres:
    ports:
      - 5433:5432  # Map to different external port

# Then update connection string
- run: psql postgresql://localhost:5433/testdb -c 'SELECT 1'
```

### Issue: Password authentication failed

**Cause:** Incorrect credentials in psql connection string.

**Fix:** Verify environment variables match connection attempt:

```yaml
services:
  postgres:
    env:
      POSTGRES_PASSWORD: mypassword

# Use matching credentials
- run: psql postgresql://postgres:mypassword@localhost:5432/testdb -c 'SELECT 1'
```

## Output Example

### Successful Execution

```
Wait for PostgreSQL service
Attempting to connect to localhost:5432
Service is ready (Connected on attempt 3)
postgres-ready=true

Verify PostgreSQL connection
 ?column?
----------
        1
(1 row)
```

### Failed Execution

```
Wait for PostgreSQL service
Attempting to connect to localhost:5432
Service failed to start within timeout (30 attempts, 60 seconds)
postgres-ready=false

Error: Service is not ready
```

## Integration with Other Workflows

### Multi-Service Setup

```yaml
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

### Sequential Service Startup

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  migrations:
    needs: postgres-service
    if: ${{ needs.postgres-service.outputs.postgres-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm run migrate

  tests:
    needs: [postgres-service, migrations]
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm test
```

## Performance

- **Service Startup:** ~5-10 seconds (typical)
- **First Health Check:** Immediate on service availability
- **Total Wait Time:** 5-30 seconds (depends on host load)
- **Timeout Threshold:** 60 seconds (30 retries × 2 seconds)
- **Network Overhead:** Minimal (local TCP checks)

### Performance Tips

1. **Use default retry count** - 30 retries is optimal for most cases
2. **Enable health checks** - Docker health checks improve reliability
3. **Use Alpine image** - `postgres:17-alpine` is lighter than full PostgreSQL image
4. **Check runner resources** - Ensure adequate CPU and memory

## Customization

### Changing Connection Parameters

Override the connection string in your verification step:

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  custom-test:
    needs: postgres-service
    if: ${{ needs.postgres-service.outputs.postgres-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - run: psql postgresql://myuser:mypass@localhost:5432/mydb -c 'SELECT version()'
```

### Using Different PostgreSQL Versions

Modify the service container image:

```yaml
services:
  postgres:
    image: postgres:16-alpine  # Use PostgreSQL 16 instead
    # ... rest of configuration
```

Then consume the service in your workflow.

### Custom Health Checks

Extend the verification with application-specific checks:

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  advanced-verification:
    needs: postgres-service
    if: ${{ needs.postgres-service.outputs.postgres-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - name: Check PostgreSQL version
        run: psql postgresql://localhost:5432/testdb -c 'SHOW server_version'

      - name: List databases
        run: psql postgresql://localhost:5432/testdb -l

      - name: Check replication status
        run: psql postgresql://localhost:5432/testdb -c 'SELECT * FROM pg_stat_replication'
```

## Troubleshooting

### Debug Mode

Add debug output to understand what's happening:

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  debug:
    needs: postgres-service
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - name: Show service status
        run: docker ps -a

      - name: Check network connectivity
        run: netstat -tlnp | grep 5432

      - name: Test psql directly
        run: psql -h localhost -U postgres -d testdb -c 'SELECT 1'
```

### Manual Service Startup

For testing locally:

```bash
# Start PostgreSQL in Docker
docker run --rm -d \
  --name postgres \
  -e POSTGRES_DB=testdb \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:17-alpine

# Wait a few seconds, then verify
psql postgresql://localhost:5432/testdb -c 'SELECT 1'

# Clean up
docker stop postgres
```

## Best Practices

1. **Always use the output** - Check `postgres-ready` before running dependent jobs
2. **Health checks in services** - Configure Docker health checks for faster detection
3. **Reasonable retry count** - 30 retries (60 seconds) works for most scenarios
4. **Isolate database** - Use separate `testdb` for CI to avoid conflicts
5. **Document dependencies** - Clearly show which jobs need PostgreSQL
6. **Version specification** - Explicitly specify PostgreSQL version: `postgres:17-alpine`

## Related Documentation

- [MongoDB Service Workflow](./mongodb-service-workflow.md) - Sibling service workflow for MongoDB
- [Service Composition Workflows](./README.md#service-composition-workflows-phase-2) - Overview of all service workflows
- [How to Debug Workflow Failures](../how-to-guides/debugging-workflow-failures.md) - Troubleshooting guide
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) - Official PostgreSQL documentation

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 7, 2025 | Initial release, PostgreSQL 17-Alpine support |

---

**Questions?** See [How-To Guides](../how-to-guides/README.md) for common problems or [Explanation](../explanation/README.md) for conceptual understanding.
