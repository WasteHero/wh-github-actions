# NATS Service Workflow Reference

**Reference:** CT-1167
**Status:** Production
**Last Updated:** December 7, 2025

## Overview

The NATS Service workflow validates the readiness and connectivity of a NATS messaging system with JetStream support within your CI/CD pipeline.

| Property | Value |
|----------|-------|
| Purpose | NATS service readiness validation |
| Trigger | workflow_call |
| Service Version | NATS with JetStream |
| Default Port | 4222 |
| Outputs | nats-ready (boolean) |
| Secrets Required | None |
| Permissions Required | contents: read |
| Runner | self-hosted, linux, X64, kubernetes |
| Typical Duration | ~60 seconds (30 retries × 2 seconds) |
| File Location | `.github/workflows/services/nats-service.yml` |

## Purpose

Ensure NATS messaging service is fully operational before running dependent tasks:
- **Connection Validation**: Confirms the broker accepts connections on the expected port
- **Health Status**: Verifies the service is responding to network requests
- **Message Broker Readiness**: Tests TCP availability for publish/subscribe operations
- **Self-Hosted Runner Support**: Designed for Kubernetes-based self-hosted runners
- **Service Composition**: Part of multi-service orchestration pattern
- **JetStream Availability**: NATS JetStream enabled for event streaming
- **Stream Initialization**: Application-driven, idempotent stream creation

## Trigger

`workflow_call` - Called as a reusable workflow from consuming repositories.

## Basic Usage

### Minimal Configuration

```yaml
jobs:
  nats-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main
```

### With Service Container

```yaml
services:
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
  nats-service:
    services:
      nats: ${{ env.services.nats }}
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main
```

### In Test Pipeline

```yaml
jobs:
  nats-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main

  integration-tests:
    needs: nats-service
    runs-on: [self-hosted, linux, X64, kubernetes]
    if: ${{ needs.nats-service.outputs.nats-ready == 'true' }}
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --reporter=json
        env:
          NATS_URL: nats://localhost:4222
```

## Outputs

The workflow exposes one output:

| Output | Type | Description |
|--------|------|-------------|
| nats-ready | string ('true' or 'false') | Whether NATS service is ready and accepting connections |

### Using Outputs

```yaml
jobs:
  nats-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main

  tests:
    needs: nats-service
    runs-on: ubuntu-latest
    if: ${{ needs.nats-service.outputs.nats-ready == 'true' }}
    steps:
      - run: echo "NATS is ready, running tests"
```

## Secrets

**No secrets required.** The workflow uses default NATS connection parameters.

## Configuration

### Runtime

- **Runs on:** `[self-hosted, linux, X64, kubernetes]`
- **Timeout:** 5 minutes (standard GitHub Actions limit)
- **Service Port:** 4222 (default NATS protocol port)
- **Monitoring Port:** 8222 (optional HTTP monitoring)
- **Retry Strategy:** 30 retries with 2-second intervals
- **Total Wait Time:** Up to 60 seconds

### Permissions

```yaml
permissions:
  contents: read
```

## What It Does

### Step 1: Wait for NATS Service

```bash
uses: ./.github/actions/wait-for-service
with:
  service-type: nats
  host: localhost
  port: '4222'
  max-retries: '30'
```

This step uses the `wait-for-service` composite action to poll the NATS port:
- Tests TCP connection to `localhost:4222`
- Retries up to 30 times with 2-second intervals between attempts
- Succeeds when port becomes available
- Fails if port never becomes available within 60 seconds
- Sets output `ready: 'true'` on success, `'false'` on failure

**Expected behavior:**
- Service starting: "Waiting for service to be ready"
- Service ready: "Service is ready"
- Service failed: "Service failed to start within timeout"

### Step 2: Verify NATS Connection

```bash
nc -zv localhost 4222
```

This step confirms the service is accepting network connections:
- Uses `nc` (netcat) to test TCP connectivity
- Verifies port is listening and responding
- Validates network accessibility for messaging
- Fails if network connectivity fails

**Expected behavior:**
- Success: "Connection to localhost 4222 port [tcp/*] succeeded!"
- Failure: "nc: connect to localhost port 4222 (tcp) failed"

## Environment Setup

### NATS Container Configuration

For the service to be available, you need to configure the NATS container in your workflow:

```yaml
services:
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
```

**Important:** The `-js` flag enables JetStream, which is required for event streaming capabilities.

### Connection Parameters

Default test configuration uses:
- **Host:** localhost
- **Port:** 4222 (NATS protocol)
- **Monitoring Port:** 8222 (HTTP metrics - optional)
- **Authentication:** None (default open access)

### Stream Initialization

**Important Note:** Stream creation is **NOT** handled by this workflow. Streams must be created idempotently by your application code:

```javascript
// Example: Node.js stream initialization (idempotent)
import { connect } from "nats";

const nc = await connect({ servers: "nats://localhost:4222" });
const js = nc.jetstream();

// Create stream if it doesn't exist (idempotent)
const streamConfig = {
  name: "EVENTS",
  subjects: ["events.>"],
  retention: "interest",
};

try {
  await js.getStreamInfo("EVENTS");
  console.log("Stream already exists");
} catch (e) {
  // Stream doesn't exist, create it
  await js.addStream(streamConfig);
  console.log("Stream created");
}
```

This approach ensures streams are created exactly once, regardless of how many times the service starts.

## Common Issues and Fixes

### Issue: "Connection refused" error

**Cause:** NATS service container is not running or port is not exposed.

**Fix:**
1. Verify service container is defined in your workflow
2. Ensure port mapping is correct: `4222:4222`
3. Check that image is `nats:latest` or compatible version
4. Add health check configuration to services

```yaml
services:
  nats:
    image: nats:latest
    command: "nats-server -js"
    ports:
      - 4222:4222  # Required
    options: >-
      --health-cmd "nats-cli server check"
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
- uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main
```

Or use Docker image with netcat pre-installed:

```bash
docker run -it nats:latest sh -c "nc -zv localhost 4222"
```

### Issue: JetStream not enabled

**Cause:** NATS server running without JetStream support.

**Fix:** Ensure the NATS server is started with `-js` flag:

```yaml
services:
  nats:
    image: nats:latest
    command: "nats-server -js"  # Must include -js for JetStream
    ports:
      - 4222:4222
```

### Issue: Stream creation fails with "stream not found"

**Cause:** Attempting to publish to a stream that doesn't exist without creating it first.

**Fix:** Create streams idempotently in your application code before publishing:

```javascript
const js = nc.jetstream();

// Create or get existing stream
const stream = await js.addStream({
  name: "EVENTS",
  subjects: ["events.>"],
}).catch(e => {
  if (e.code === "JSSTREAM_GENERAL_API_ERR" && e.description?.includes("stream already exists")) {
    return js.getStreamInfo("EVENTS");
  }
  throw e;
});
```

### Issue: Timeout waiting for NATS (fails after 60 seconds)

**Cause:** Service taking longer than expected to start, or health checks are failing.

**Fix:**
1. Check runner resource availability - NATS needs memory to start
2. Verify health check interval is reasonable:

```yaml
services:
  nats:
    image: nats:latest
    command: "nats-server -js"
    options: >-
      --health-cmd "nats-cli server check"
      --health-interval 2s        # Check every 2 seconds
      --health-timeout 5s         # Allow 5s per check
      --health-retries 30         # Try 30 times max
```

3. Increase runner capacity if available
4. Check Docker image is not corrupted: `docker pull nats:latest`

### Issue: Port 4222 already in use

**Cause:** Another service is already running on port 4222.

**Fix:**
1. Stop any local NATS instances
2. Use different port in workflow:

```yaml
services:
  nats:
    ports:
      - 4223:4222  # Map to different external port

# Then update connection string
- run: nats-cli server -s nats://localhost:4223 info
```

### Issue: Message loss or subscription issues

**Cause:** Subscribers not connected before publishers send messages.

**Fix:** Ensure subscribers are active before publishing. Use JetStream push consumers:

```javascript
const js = nc.jetstream();

// Create durable consumer (survives subscriber disconnect)
const consumer = await js.subscribe("EVENTS.>", {
  durable: "test_consumer",
  config: {
    deliver_policy: DeliverPolicy.All,
  },
});
```

### Issue: Memory or CPU constraints

**Cause:** NATS service consuming unexpected resources.

**Fix:** Monitor and limit NATS resource usage:

```yaml
services:
  nats:
    image: nats:latest
    command: "nats-server -js"
    options: >-
      --memory=512m
      --cpus=0.5
    ports:
      - 4222:4222
```

## Output Example

### Successful Execution

```
Wait for NATS service
Attempting to connect to localhost:4222
Service is ready (Connected on attempt 2)
nats-ready=true

Verify NATS connection
Connection to localhost 4222 port [tcp/*] succeeded!
```

### Failed Execution

```
Wait for NATS service
Attempting to connect to localhost:4222
Service failed to start within timeout (30 attempts, 60 seconds)
nats-ready=false

Error: Service is not ready
```

## Integration with Other Workflows

### Multi-Service Setup

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  nats-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main

  integration-tests:
    needs: [postgres-service, nats-service]
    if: |
      ${{ needs.postgres-service.outputs.postgres-ready == 'true' &&
          needs.nats-service.outputs.nats-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --integration
```

### Event Streaming Workflow

```yaml
jobs:
  nats-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main

  stream-setup:
    needs: nats-service
    if: ${{ needs.nats-service.outputs.nats-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm run setup:streams

  tests:
    needs: [nats-service, stream-setup]
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --event-streaming
```

### Request-Reply Pattern Testing

```yaml
jobs:
  nats-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main

  request-reply-tests:
    needs: nats-service
    if: ${{ needs.nats-service.outputs.nats-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --grep "request-reply"
        env:
          NATS_URL: nats://localhost:4222
```

## Performance

- **Service Startup:** ~1-3 seconds (typical)
- **First Health Check:** Immediate on service availability
- **Total Wait Time:** 1-10 seconds (depends on host load)
- **Timeout Threshold:** 60 seconds (30 retries × 2 seconds)
- **Network Overhead:** Minimal (local TCP checks)
- **JetStream Overhead:** ~100ms for stream creation (idempotent)

### Performance Tips

1. **Use default retry count** - 30 retries is optimal for most cases
2. **Enable JetStream** - Use `-js` flag for event streaming support
3. **Use latest image** - `nats:latest` is well-optimized for containers
4. **Check runner resources** - Ensure adequate CPU and memory
5. **Create streams once** - Use idempotent stream creation in app code
6. **Monitor JetStream** - Use HTTP monitoring port (8222) if needed

## JetStream Features

NATS JetStream provides reliable message delivery:

```javascript
const js = nc.jetstream();

// Publish with confirmation
const ack = await js.publish("EVENTS.user.created", {
  userId: "123",
  email: "user@example.com",
});
console.log(`Message published with sequence ${ack.metadata.sequence.stream}`);

// Consume with durability
const consumer = await js.subscribe("EVENTS.user.>", {
  durable: "user_processor",
});
```

## Customization

### Changing Connection Parameters

Override the connection string in your verification step:

```yaml
jobs:
  nats-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main

  custom-test:
    needs: nats-service
    if: ${{ needs.nats-service.outputs.nats-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - run: nats-cli server -s nats://localhost:4222 info
```

### Using Different NATS Versions

Modify the service container image:

```yaml
services:
  nats:
    image: nats:2.9-alpine  # Use specific NATS version
    command: "nats-server -js"
    # ... rest of configuration
```

Then consume the service in your workflow.

### Custom Health Checks

Extend the verification with application-specific checks:

```yaml
jobs:
  nats-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main

  advanced-verification:
    needs: nats-service
    if: ${{ needs.nats-service.outputs.nats-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - name: Check NATS server info
        run: nats-cli server -s nats://localhost:4222 info

      - name: Test publish-subscribe
        run: |
          nats-cli pub TEST.subject "test message"
          timeout 2 nats-cli sub TEST.subject || true

      - name: Check JetStream status
        run: nats-cli server -s nats://localhost:4222 report jetstream
```

## Troubleshooting

### Debug Mode

Add debug output to understand what's happening:

```yaml
jobs:
  nats-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/nats-service.yml@main

  debug:
    needs: nats-service
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - name: Show service status
        run: docker ps -a

      - name: Check network connectivity
        run: netstat -tlnp | grep 4222

      - name: Test nats-cli directly
        run: nats-cli server -s nats://localhost:4222 info

      - name: Check container logs
        run: docker logs $(docker ps -q --filter="ancestor=nats:latest")
```

### Manual Service Startup

For testing locally:

```bash
# Start NATS in Docker with JetStream
docker run --rm -d \
  --name nats \
  -p 4222:4222 \
  -p 8222:8222 \
  nats:latest \
  nats-server -js

# Wait a few seconds, then verify
sleep 2
nats-cli server -s nats://localhost:4222 info

# Clean up
docker stop nats
```

## Best Practices

1. **Always use the output** - Check `nats-ready` before running dependent jobs
2. **Health checks in services** - Configure Docker health checks for faster detection
3. **Reasonable retry count** - 30 retries (60 seconds) works for most scenarios
4. **Create streams idempotently** - Handle stream already exists errors gracefully
5. **Document dependencies** - Clearly show which jobs need NATS
6. **Enable JetStream** - Always use `-js` flag for reliable message delivery
7. **Use durable consumers** - Subscribe with durable names for persistence
8. **Monitor performance** - Use HTTP monitoring port (8222) if needed

## Related Documentation

- [PostgreSQL Service Workflow](./postgresql-service-workflow.md) - Sibling service workflow for PostgreSQL
- [ValKey Service Workflow](./valkey-service-workflow.md) - Cache service workflow
- [Vault Service Workflow](./vault-service-workflow.md) - Secrets management service workflow
- [Service Composition Workflows](./README.md#service-composition-workflows-phase-2) - Overview of all service workflows
- [How to Debug Workflow Failures](../how-to-guides/debugging-workflow-failures.md) - Troubleshooting guide
- [NATS Documentation](https://docs.nats.io/) - Official NATS documentation
- [JetStream Documentation](https://docs.nats.io/nats-concepts/jetstream) - JetStream feature guide

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 7, 2025 | Initial release, NATS with JetStream support |

---

**Questions?** See [How-To Guides](../how-to-guides/README.md) for common problems or [Explanation](../explanation/README.md) for conceptual understanding.
