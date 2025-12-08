# MongoDB Service Workflow Reference

**Reference:** CT-1185
**Status:** Production
**Last Updated:** December 7, 2025

## Overview

The MongoDB Service workflow validates the readiness and connectivity of a MongoDB 8.0 database service within your CI/CD pipeline.

| Property | Value |
|----------|-------|
| Purpose | MongoDB service readiness validation |
| Trigger | workflow_call |
| Service Version | MongoDB 8.0 |
| Default Port | 27017 |
| Outputs | mongodb-ready (boolean) |
| Secrets Required | None |
| Permissions Required | contents: read |
| Runner | self-hosted, linux, X64, kubernetes |
| Typical Duration | ~60 seconds (30 retries × 2 seconds) |
| File Location | `.github/workflows/services/mongodb-service.yml` |

## Purpose

Ensure MongoDB database service is fully operational before running dependent tasks:
- **Connection Validation**: Confirms the database accepts connections on the expected port
- **Health Status**: Verifies the service is responding to health checks
- **Database Connectivity**: Tests actual database operations (ping command)
- **Self-Hosted Runner Support**: Designed for Kubernetes-based self-hosted runners
- **Service Composition**: First phase of multi-service orchestration pattern

## Trigger

`workflow_call` - Called as a reusable workflow from consuming repositories.

## Basic Usage

### Minimal Configuration

```yaml
jobs:
  mongodb-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main
```

### With Service Container

```yaml
services:
  mongodb:
    image: mongo:8.0
    options: >-
      --health-cmd mongosh
      --health-interval 2s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 27017:27017

jobs:
  mongodb-service:
    services:
      mongodb: ${{ env.services.mongodb }}
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main
```

### In Test Pipeline

```yaml
jobs:
  mongodb-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main

  integration-tests:
    needs: mongodb-service
    runs-on: [self-hosted, linux, X64, kubernetes]
    if: ${{ needs.mongodb-service.outputs.mongodb-ready == 'true' }}
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --reporter=json
        env:
          MONGODB_URI: mongodb://localhost:27017/testdb
```

## Outputs

The workflow exposes one output:

| Output | Type | Description |
|--------|------|-------------|
| mongodb-ready | string ('true' or 'false') | Whether MongoDB service is ready and accepting connections |

### Using Outputs

```yaml
jobs:
  mongodb-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main

  tests:
    needs: mongodb-service
    runs-on: ubuntu-latest
    if: ${{ needs.mongodb-service.outputs.mongodb-ready == 'true' }}
    steps:
      - run: echo "MongoDB is ready, running tests"
```

## Secrets

**No secrets required.** The workflow uses default MongoDB connection parameters.

## Configuration

### Runtime

- **Runs on:** `[self-hosted, linux, X64, kubernetes]`
- **Timeout:** 5 minutes (standard GitHub Actions limit)
- **Service Port:** 27017 (default MongoDB port)
- **Retry Strategy:** 30 retries with 2-second intervals
- **Total Wait Time:** Up to 60 seconds

### Permissions

```yaml
permissions:
  contents: read
```

## What It Does

### Step 1: Wait for MongoDB Service

```bash
uses: ./.github/actions/wait-for-service
with:
  service-type: mongodb
  host: localhost
  port: '27017'
  max-retries: '30'
```

This step uses the `wait-for-service` composite action to poll the MongoDB port:
- Tests TCP connection to `localhost:27017`
- Retries up to 30 times with 2-second intervals between attempts
- Succeeds when port becomes available
- Fails if port never becomes available within 60 seconds
- Sets output `ready: 'true'` on success, `'false'` on failure

**Expected behavior:**
- Service starting: "Waiting for service to be ready"
- Service ready: "Service is ready"
- Service failed: "Service failed to start within timeout"

### Step 2: Verify MongoDB Connection

```bash
mongosh mongodb://localhost:27017/testdb --eval "db.adminCommand('ping')"
```

This step confirms the database is not only accepting connections but can execute operations:
- Connects using `mongosh` command-line client (MongoDB 6.0+ shell)
- Executes a health-check ping command
- Fails if database is not responding correctly
- Validates the service is fully operational (not just listening on the port)

**Expected behavior:**
- Success: `{ ok: 1 }` response
- Failure: Connection error or authentication error

## Environment Setup

### MongoDB Container Configuration

For the service to be available, you need to configure the MongoDB container in your workflow:

```yaml
services:
  mongodb:
    image: mongo:8.0
    options: >-
      --health-cmd mongosh
      --health-interval 2s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 27017:27017
```

### Connection Parameters

Default test configuration uses:
- **Host:** localhost
- **Port:** 27017
- **Database:** testdb
- **Authentication:** None (default open access)

For production with authentication:

```yaml
services:
  mongodb:
    image: mongo:8.0
    env:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    ports:
      - 27017:27017

jobs:
  mongodb-service:
    needs: mongodb-service
    steps:
      - run: mongosh mongodb://admin:password@localhost:27017/testdb --eval "db.adminCommand('ping')"
```

## Common Issues and Fixes

### Issue: "Connection refused" error

**Cause:** MongoDB service container is not running or port is not exposed.

**Fix:**
1. Verify service container is defined in your workflow
2. Ensure port mapping is correct: `27017:27017`
3. Check that image is `mongo:8.0` or compatible version
4. Add health check configuration to services

```yaml
services:
  mongodb:
    image: mongo:8.0
    ports:
      - 27017:27017  # Required
    options: >-
      --health-cmd mongosh
      --health-interval 2s
```

### Issue: "mongosh: command not found"

**Cause:** MongoDB shell (mongosh) is not installed in the runner environment.

**Fix:** The wait-for-service action only tests TCP connectivity. The mongosh verification step requires mongosh to be installed:

```bash
# If using Ubuntu runner, install MongoDB tools
- name: Install MongoDB tools
  run: |
    sudo apt-get update
    sudo apt-get install -y mongodb-mongosh

# Then run the service workflow
- uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main
```

Or use Docker image with MongoDB tools pre-installed:

```bash
docker run -it mongo:8.0 mongosh mongodb://localhost:27017/testdb --eval "db.adminCommand('ping')"
```

### Issue: "bad auth" or "authentication failed"

**Cause:** Connection string doesn't match MongoDB authentication configuration.

**Fix:** Ensure credentials match the service configuration:

```yaml
services:
  mongodb:
    image: mongo:8.0
    env:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: secret

# Update connection string with credentials
- run: mongosh mongodb://admin:secret@localhost:27017/testdb --eval "db.adminCommand('ping')"
```

For the default workflow (no auth):

```yaml
services:
  mongodb:
    image: mongo:8.0
    # No authentication configuration

- run: mongosh mongodb://localhost:27017/testdb --eval "db.adminCommand('ping')"
```

### Issue: Timeout waiting for MongoDB (fails after 60 seconds)

**Cause:** Service taking longer than expected to start, or health checks are failing.

**Fix:**
1. Check runner resource availability - MongoDB needs memory to start
2. Verify health check interval is reasonable:

```yaml
services:
  mongodb:
    image: mongo:8.0
    options: >-
      --health-cmd mongosh
      --health-interval 2s        # Check every 2 seconds
      --health-timeout 5s         # Allow 5s per check
      --health-retries 30         # Try 30 times max
```

3. Increase runner capacity if available
4. Check Docker image is not corrupted: `docker pull mongo:8.0`

### Issue: Port 27017 already in use

**Cause:** Another service is already running on port 27017.

**Fix:**
1. Stop any local MongoDB instances
2. Use different port in workflow:

```yaml
services:
  mongodb:
    ports:
      - 27018:27017  # Map to different external port

# Then update connection string
- run: mongosh mongodb://localhost:27018/testdb --eval "db.adminCommand('ping')"
```

### Issue: Database 'testdb' not accessible

**Cause:** MongoDB allows implicit database creation, but may not have testdb initialized.

**Fix:** MongoDB automatically creates databases on first use. If issues persist:

```yaml
# Initialize database explicitly in a previous step
- name: Initialize MongoDB database
  run: |
    mongosh mongodb://localhost:27017/testdb --eval "
      db.createCollection('test');
      db.test.insertOne({initialized: true});
    "
```

### Issue: Replica set connection string fails

**Cause:** Using replica set URI without proper configuration.

**Fix:** For simple single-instance setup, use standard URI:

```bash
# Use standard connection
mongosh mongodb://localhost:27017/testdb

# Not replica set connection
mongosh 'mongodb://localhost:27017/?replicaSet=rs0'
```

## Output Example

### Successful Execution

```
Wait for MongoDB service
Attempting to connect to localhost:27017
Service is ready (Connected on attempt 3)
mongodb-ready=true

Verify MongoDB connection
{
  ok: 1
}
```

### Failed Execution

```
Wait for MongoDB service
Attempting to connect to localhost:27017
Service failed to start within timeout (30 attempts, 60 seconds)
mongodb-ready=false

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
  mongodb-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main

  seed-data:
    needs: mongodb-service
    if: ${{ needs.mongodb-service.outputs.mongodb-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm run seed:db

  tests:
    needs: [mongodb-service, seed-data]
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
3. **Use standard image** - `mongo:8.0` is well-optimized for containers
4. **Check runner resources** - Ensure adequate CPU and memory
5. **Avoid replica sets in CI** - Single instance is faster for testing

## Customization

### Changing Connection Parameters

Override the connection string in your verification step:

```yaml
jobs:
  mongodb-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main

  custom-test:
    needs: mongodb-service
    if: ${{ needs.mongodb-service.outputs.mongodb-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - run: mongosh mongodb://admin:secret@localhost:27017/mydb --eval "db.stats()"
```

### Using Different MongoDB Versions

Modify the service container image:

```yaml
services:
  mongodb:
    image: mongo:7.0  # Use MongoDB 7.0 instead
    # ... rest of configuration
```

Then consume the service in your workflow.

### Custom Health Checks

Extend the verification with application-specific checks:

```yaml
jobs:
  mongodb-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main

  advanced-verification:
    needs: mongodb-service
    if: ${{ needs.mongodb-service.outputs.mongodb-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - name: Check MongoDB version
        run: mongosh mongodb://localhost:27017/testdb --eval "db.version()"

      - name: List databases
        run: mongosh mongodb://localhost:27017/testdb --eval "show databases"

      - name: Check server status
        run: mongosh mongodb://localhost:27017/testdb --eval "db.serverStatus().ok"

      - name: Test write operation
        run: mongosh mongodb://localhost:27017/testdb --eval "
          db.test_collection.insertOne({timestamp: new Date(), status: 'verified'});
          db.test_collection.findOne();
        "
```

## Troubleshooting

### Debug Mode

Add debug output to understand what's happening:

```yaml
jobs:
  mongodb-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/mongodb-service.yml@main

  debug:
    needs: mongodb-service
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - name: Show service status
        run: docker ps -a

      - name: Check network connectivity
        run: netstat -tlnp | grep 27017

      - name: Test mongosh directly
        run: mongosh mongodb://localhost:27017/testdb --eval "db.adminCommand('ping')"

      - name: Check MongoDB logs
        run: docker logs $(docker ps -q --filter="ancestor=mongo:8.0")
```

### Manual Service Startup

For testing locally:

```bash
# Start MongoDB in Docker
docker run --rm -d \
  --name mongodb \
  -p 27017:27017 \
  mongo:8.0

# Wait a few seconds, then verify
mongosh mongodb://localhost:27017/testdb --eval "db.adminCommand('ping')"

# Clean up
docker stop mongodb
```

## Best Practices

1. **Always use the output** - Check `mongodb-ready` before running dependent jobs
2. **Health checks in services** - Configure Docker health checks for faster detection
3. **Reasonable retry count** - 30 retries (60 seconds) works for most scenarios
4. **Isolate database** - Use separate `testdb` for CI to avoid conflicts
5. **Document dependencies** - Clearly show which jobs need MongoDB
6. **Version specification** - Explicitly specify MongoDB version: `mongo:8.0`
7. **No authentication in CI** - Keep CI setup simple without authentication unless required

## Related Documentation

- [PostgreSQL Service Workflow](./postgresql-service-workflow.md) - Sibling service workflow for PostgreSQL
- [Service Composition Workflows](./README.md#service-composition-workflows-phase-2) - Overview of all service workflows
- [How to Debug Workflow Failures](../how-to-guides/debugging-workflow-failures.md) - Troubleshooting guide
- [MongoDB Documentation](https://docs.mongodb.com/) - Official MongoDB documentation

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 7, 2025 | Initial release, MongoDB 8.0 support |

---

**Questions?** See [How-To Guides](../how-to-guides/README.md) for common problems or [Explanation](../explanation/README.md) for conceptual understanding.
