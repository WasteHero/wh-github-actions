# ValKey Service Workflow Reference

**Reference:** CT-1167
**Status:** Production
**Last Updated:** December 7, 2025

## Overview

The ValKey Service workflow validates the readiness and connectivity of a ValKey (Redis fork) service within your CI/CD pipeline.

| Property | Value |
|----------|-------|
| Purpose | ValKey service readiness validation |
| Trigger | workflow_call |
| Service Version | ValKey 8.0-Alpine |
| Default Port | 6379 |
| Outputs | valkey-ready (boolean) |
| Secrets Required | None |
| Permissions Required | contents: read |
| Runner | self-hosted, linux, X64, kubernetes |
| Typical Duration | ~60 seconds (30 retries × 2 seconds) |
| File Location | `.github/workflows/services/valkey-service.yml` |

## Purpose

Ensure ValKey cache service is fully operational before running dependent tasks:
- **Connection Validation**: Confirms the service accepts connections on the expected port
- **Health Status**: Verifies the service is responding to network requests
- **Network Connectivity**: Tests TCP availability for cache operations
- **Self-Hosted Runner Support**: Designed for Kubernetes-based self-hosted runners
- **Service Composition**: Part of multi-service orchestration pattern
- **Redis Compatibility**: Full compatibility with Redis clients and protocols

## Trigger

`workflow_call` - Called as a reusable workflow from consuming repositories.

## Basic Usage

### Minimal Configuration

```yaml
jobs:
  valkey-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main
```

### With Service Container

```yaml
services:
  valkey:
    image: valkey:8.0-alpine
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 2s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 6379:6379

jobs:
  valkey-service:
    services:
      valkey: ${{ env.services.valkey }}
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main
```

### In Test Pipeline

```yaml
jobs:
  valkey-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main

  integration-tests:
    needs: valkey-service
    runs-on: [self-hosted, linux, X64, kubernetes]
    if: ${{ needs.valkey-service.outputs.valkey-ready == 'true' }}
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --reporter=json
        env:
          REDIS_URL: redis://localhost:6379/0
```

## Outputs

The workflow exposes one output:

| Output | Type | Description |
|--------|------|-------------|
| valkey-ready | string ('true' or 'false') | Whether ValKey service is ready and accepting connections |

### Using Outputs

```yaml
jobs:
  valkey-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main

  tests:
    needs: valkey-service
    runs-on: ubuntu-latest
    if: ${{ needs.valkey-service.outputs.valkey-ready == 'true' }}
    steps:
      - run: echo "ValKey is ready, running tests"
```

## Secrets

**No secrets required.** The workflow uses default ValKey connection parameters.

## Configuration

### Runtime

- **Runs on:** `[self-hosted, linux, X64, kubernetes]`
- **Timeout:** 5 minutes (standard GitHub Actions limit)
- **Service Port:** 6379 (default ValKey/Redis port)
- **Retry Strategy:** 30 retries with 2-second intervals
- **Total Wait Time:** Up to 60 seconds

### Permissions

```yaml
permissions:
  contents: read
```

## What It Does

### Step 1: Wait for ValKey Service

```bash
uses: ./.github/actions/wait-for-service
with:
  service-type: valkey
  host: localhost
  port: '6379'
  max-retries: '30'
```

This step uses the `wait-for-service` composite action to poll the ValKey port:
- Tests TCP connection to `localhost:6379`
- Retries up to 30 times with 2-second intervals between attempts
- Succeeds when port becomes available
- Fails if port never becomes available within 60 seconds
- Sets output `ready: 'true'` on success, `'false'` on failure

**Expected behavior:**
- Service starting: "Waiting for service to be ready"
- Service ready: "Service is ready"
- Service failed: "Service failed to start within timeout"

### Step 2: Verify ValKey Connection

```bash
nc -zv localhost 6379
```

This step confirms the service is accepting network connections:
- Uses `nc` (netcat) to test TCP connectivity
- Verifies port is listening and responding
- Validates network accessibility (not just socket binding)
- Fails if network connectivity fails

**Expected behavior:**
- Success: "Connection to localhost 6379 port [tcp/*] succeeded!"
- Failure: "nc: connect to localhost port 6379 (tcp) failed"

## Environment Setup

### ValKey Container Configuration

For the service to be available, you need to configure the ValKey container in your workflow:

```yaml
services:
  valkey:
    image: valkey:8.0-alpine
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 2s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 6379:6379
```

### Connection Parameters

Default test configuration uses:
- **Host:** localhost
- **Port:** 6379
- **Database:** 0 (default)
- **Authentication:** None (default open access)

Customize these values by modifying your service container environment variables.

## Common Issues and Fixes

### Issue: "Connection refused" error

**Cause:** ValKey service container is not running or port is not exposed.

**Fix:**
1. Verify service container is defined in your workflow
2. Ensure port mapping is correct: `6379:6379`
3. Check that image is `valkey:8.0-alpine` or compatible version
4. Add health check configuration to services

```yaml
services:
  valkey:
    image: valkey:8.0-alpine
    ports:
      - 6379:6379  # Required
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 2s
```

### Issue: "nc: command not found"

**Cause:** Netcat tool is not installed in the runner environment.

**Fix:** The wait-for-service action only tests TCP connectivity. The nc verification step requires netcat to be installed:

```bash
# If using Ubuntu runner, install netcat
- name: Install netcat
  run: sudo apt-get install -y netcat-openbsd

# Then run the service workflow
- uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main
```

Or use Docker image with netcat pre-installed:

```bash
docker run -it valkey:8.0-alpine sh -c "nc -zv localhost 6379"
```

### Issue: "redis-cli: command not found"

**Cause:** Redis client tools are not installed for health checks.

**Fix:** The health check command requires redis-cli. Ensure your container has it:

```yaml
services:
  valkey:
    image: valkey:8.0-alpine
    options: >-
      --health-cmd "redis-cli ping"  # redis-cli is included in valkey image
      --health-interval 2s
```

For custom health checks, install redis-tools if needed:

```bash
# Within ValKey container
apk add redis-tools
```

### Issue: Timeout waiting for ValKey (fails after 60 seconds)

**Cause:** Service taking longer than expected to start, or health checks are failing.

**Fix:**
1. Check runner resource availability - ValKey needs memory to start
2. Verify health check interval is reasonable:

```yaml
services:
  valkey:
    image: valkey:8.0-alpine
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 2s        # Check every 2 seconds
      --health-timeout 5s         # Allow 5s per check
      --health-retries 30         # Try 30 times max
```

3. Increase runner capacity if available
4. Check Docker image is not corrupted: `docker pull valkey:8.0-alpine`

### Issue: Port 6379 already in use

**Cause:** Another service is already running on port 6379.

**Fix:**
1. Stop any local ValKey/Redis instances
2. Use different port in workflow:

```yaml
services:
  valkey:
    ports:
      - 6380:6379  # Map to different external port

# Then update connection string
- run: redis-cli -p 6380 ping
```

### Issue: Authentication or ACL failures

**Cause:** Attempting to use authentication with default configuration.

**Fix:** Default ValKey configuration has no authentication. For authentication:

```yaml
services:
  valkey:
    image: valkey:8.0-alpine
    command: ["valkey-server", "--requirepass", "mypassword"]
    ports:
      - 6379:6379

# Use authenticated connection
- run: redis-cli -h localhost -p 6379 -a mypassword ping
```

### Issue: Memory or persistence issues

**Cause:** ValKey consuming excessive memory or persisting unexpectedly.

**Fix:** Control memory and persistence:

```yaml
services:
  valkey:
    image: valkey:8.0-alpine
    command: ["valkey-server", "--maxmemory", "256mb", "--save", ""]
    ports:
      - 6379:6379
```

## Output Example

### Successful Execution

```
Wait for ValKey service
Attempting to connect to localhost:6379
Service is ready (Connected on attempt 3)
valkey-ready=true

Verify ValKey connection
Connection to localhost 6379 port [tcp/*] succeeded!
```

### Failed Execution

```
Wait for ValKey service
Attempting to connect to localhost:6379
Service failed to start within timeout (30 attempts, 60 seconds)
valkey-ready=false

Error: Service is not ready
```

## Integration with Other Workflows

### Multi-Service Setup

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  valkey-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main

  integration-tests:
    needs: [postgres-service, valkey-service]
    if: |
      ${{ needs.postgres-service.outputs.postgres-ready == 'true' &&
          needs.valkey-service.outputs.valkey-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --integration
```

### Sequential Service Startup

```yaml
jobs:
  valkey-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main

  cache-warmup:
    needs: valkey-service
    if: ${{ needs.valkey-service.outputs.valkey-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm run warmup:cache

  tests:
    needs: [valkey-service, cache-warmup]
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm test
```

### With Cache-Intensive Testing

```yaml
jobs:
  valkey-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main

  cache-tests:
    needs: valkey-service
    if: ${{ needs.valkey-service.outputs.valkey-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --grep "cache"
        env:
          REDIS_URL: redis://localhost:6379/0
          REDIS_TEST_DB: 1
```

## Performance

- **Service Startup:** ~2-5 seconds (typical)
- **First Health Check:** Immediate on service availability
- **Total Wait Time:** 2-15 seconds (depends on host load)
- **Timeout Threshold:** 60 seconds (30 retries × 2 seconds)
- **Network Overhead:** Minimal (local TCP checks)

### Performance Tips

1. **Use default retry count** - 30 retries is optimal for most cases
2. **Enable health checks** - Docker health checks improve reliability
3. **Use Alpine image** - `valkey:8.0-alpine` is lightweight and fast
4. **Check runner resources** - Ensure adequate CPU and memory
5. **Pre-warm cache** - Use initialization scripts if needed for tests

## Redis Compatibility

ValKey is fully compatible with Redis clients and protocols:

```yaml
# Any Redis client works with ValKey
- run: |
    npm install redis
    node -e "const redis = require('redis'); const client = redis.createClient({url: 'redis://localhost:6379'}); client.ping().then(console.log);"
```

### Supported Client Libraries

- **Node.js:** `redis`, `ioredis`, `node-redis`
- **Python:** `redis`, `aioredis`
- **Go:** `go-redis`, `redigo`
- **Java:** `jedis`, `lettuce`
- **.NET:** `StackExchange.Redis`

## Customization

### Changing Connection Parameters

Override the connection string in your verification step:

```yaml
jobs:
  valkey-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main

  custom-test:
    needs: valkey-service
    if: ${{ needs.valkey-service.outputs.valkey-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - run: redis-cli -h localhost -p 6379 -n 0 ping
```

### Using Different ValKey Versions

Modify the service container image:

```yaml
services:
  valkey:
    image: valkey:7.2-alpine  # Use ValKey 7.2 instead
    # ... rest of configuration
```

Then consume the service in your workflow.

### Custom Health Checks

Extend the verification with application-specific checks:

```yaml
jobs:
  valkey-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main

  advanced-verification:
    needs: valkey-service
    if: ${{ needs.valkey-service.outputs.valkey-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - name: Check ValKey version
        run: redis-cli --version

      - name: Verify server info
        run: redis-cli INFO server

      - name: Test set/get operations
        run: |
          redis-cli SET test_key test_value
          redis-cli GET test_key
          redis-cli DEL test_key

      - name: Check memory usage
        run: redis-cli INFO memory
```

## Troubleshooting

### Debug Mode

Add debug output to understand what's happening:

```yaml
jobs:
  valkey-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/valkey-service.yml@main

  debug:
    needs: valkey-service
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - name: Show service status
        run: docker ps -a

      - name: Check network connectivity
        run: netstat -tlnp | grep 6379

      - name: Test redis-cli directly
        run: redis-cli -h localhost -p 6379 ping

      - name: Check container logs
        run: docker logs $(docker ps -q --filter="ancestor=valkey:8.0-alpine")
```

### Manual Service Startup

For testing locally:

```bash
# Start ValKey in Docker
docker run --rm -d \
  --name valkey \
  -p 6379:6379 \
  valkey:8.0-alpine

# Wait a few seconds, then verify
sleep 2
redis-cli ping

# Clean up
docker stop valkey
```

## Best Practices

1. **Always use the output** - Check `valkey-ready` before running dependent jobs
2. **Health checks in services** - Configure Docker health checks for faster detection
3. **Reasonable retry count** - 30 retries (60 seconds) works for most scenarios
4. **Isolate cache database** - Use separate database numbers in CI (e.g., DB 1 for tests)
5. **Document dependencies** - Clearly show which jobs need ValKey
6. **Version specification** - Explicitly specify ValKey version: `valkey:8.0-alpine`
7. **Resource limits** - Set memory limits if needed: `--maxmemory 256mb`
8. **Clean test data** - Flush cache between test runs if needed: `FLUSHDB`

## Related Documentation

- [PostgreSQL Service Workflow](./postgresql-service-workflow.md) - Sibling service workflow for PostgreSQL
- [MongoDB Service Workflow](./mongodb-service-workflow.md) - Sibling service workflow for MongoDB
- [NATS Service Workflow](./nats-service-workflow.md) - Message broker service workflow
- [Service Composition Workflows](./README.md#service-composition-workflows-phase-2) - Overview of all service workflows
- [How to Debug Workflow Failures](../how-to-guides/debugging-workflow-failures.md) - Troubleshooting guide
- [ValKey Documentation](https://valkey.io/docs/) - Official ValKey documentation
- [Redis Documentation](https://redis.io/documentation) - Redis documentation (ValKey compatible)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 7, 2025 | Initial release, ValKey 8.0-Alpine support |

---

**Questions?** See [How-To Guides](../how-to-guides/README.md) for common problems or [Explanation](../explanation/README.md) for conceptual understanding.
