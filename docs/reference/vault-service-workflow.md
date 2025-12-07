# Vault Service Workflow Reference

**Reference:** CT-1167
**Status:** Production
**Last Updated:** December 7, 2025

## Overview

The Vault Service workflow validates the readiness and connectivity of a HashiCorp Vault secrets management service within your CI/CD pipeline.

| Property | Value |
|----------|-------|
| Purpose | Vault service readiness validation |
| Trigger | workflow_call |
| Service Version | HashiCorp Vault 1.18 |
| Default Port | 8200 |
| Outputs | vault-ready (boolean), vault-token-ttl (string: '15-20 minutes') |
| Secrets Required | None |
| Permissions Required | contents: read |
| Runner | self-hosted, linux, X64, kubernetes |
| Typical Duration | ~60 seconds (30 retries × 2 seconds) |
| File Location | `.github/workflows/services/vault-service.yml` |

## Purpose

Ensure HashiCorp Vault service is fully operational and authenticated before running dependent tasks:
- **Connection Validation**: Confirms the service accepts connections on the expected port
- **Health Status**: Verifies the service is responding and unsealed
- **Authentication Readiness**: Validates AppRole authentication is configured
- **Token Management**: Provides token TTL configuration for CI/CD workflows
- **Self-Hosted Runner Support**: Designed for Kubernetes-based self-hosted runners
- **Service Composition**: Part of multi-service orchestration pattern
- **Secrets Access**: Enables dependent jobs to retrieve secrets securely

## Trigger

`workflow_call` - Called as a reusable workflow from consuming repositories.

## Basic Usage

### Minimal Configuration

```yaml
jobs:
  vault-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main
```

### With Service Container

```yaml
services:
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
  vault-service:
    services:
      vault: ${{ env.services.vault }}
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main
```

### In Test Pipeline

```yaml
jobs:
  vault-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main

  integration-tests:
    needs: vault-service
    runs-on: [self-hosted, linux, X64, kubernetes]
    if: ${{ needs.vault-service.outputs.vault-ready == 'true' }}
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --reporter=json
        env:
          VAULT_ADDR: http://localhost:8200
          VAULT_TOKEN: dev-token
```

## Outputs

The workflow exposes two outputs:

| Output | Type | Description |
|--------|------|-------------|
| vault-ready | string ('true' or 'false') | Whether Vault service is ready and accepting connections |
| vault-token-ttl | string | Token TTL configuration for CI/CD usage ('15-20 minutes') |

### Using Outputs

```yaml
jobs:
  vault-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main

  tests:
    needs: vault-service
    runs-on: ubuntu-latest
    if: ${{ needs.vault-service.outputs.vault-ready == 'true' }}
    steps:
      - run: echo "Vault is ready with TTL: ${{ needs.vault-service.outputs.vault-token-ttl }}"
```

## Secrets

**No secrets required for the workflow itself.** However, dependent jobs may need:
- `VAULT_TOKEN` - Authentication token for secret access
- `VAULT_ADDR` - Vault server URL (typically `http://localhost:8200`)

## Configuration

### Runtime

- **Runs on:** `[self-hosted, linux, X64, kubernetes]`
- **Timeout:** 5 minutes (standard GitHub Actions limit)
- **Service Port:** 8200 (default Vault HTTP API port)
- **Retry Strategy:** 30 retries with 2-second intervals
- **Total Wait Time:** Up to 60 seconds
- **Token TTL:** 15-20 minutes (recommended for CI/CD)

### Permissions

```yaml
permissions:
  contents: read
```

## What It Does

### Step 1: Wait for Vault Service

```bash
uses: ./.github/actions/wait-for-service
with:
  service-type: vault
  host: localhost
  port: '8200'
  max-retries: '30'
```

This step uses the `wait-for-service` composite action to poll the Vault port:
- Tests TCP connection to `localhost:8200`
- Retries up to 30 times with 2-second intervals between attempts
- Succeeds when port becomes available
- Fails if port never becomes available within 60 seconds
- Sets output `ready: 'true'` on success, `'false'` on failure

**Expected behavior:**
- Service starting: "Waiting for service to be ready"
- Service ready: "Service is ready"
- Service failed: "Service failed to start within timeout"

### Step 2: Verify Vault Connection

```bash
nc -zv localhost 8200
```

This step confirms the service is accepting network connections:
- Uses `nc` (netcat) to test TCP connectivity
- Verifies port is listening and responding
- Validates network accessibility for API requests
- Fails if network connectivity fails

**Expected behavior:**
- Success: "Connection to localhost 8200 port [tcp/*] succeeded!"
- Failure: "nc: connect to localhost port 8200 (tcp) failed"

## Environment Setup

### Vault Container Configuration (Development Mode)

For testing in CI/CD, use Vault's development mode:

```yaml
services:
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
```

**Important:** Development mode is suitable for testing only. For production, use proper Vault configuration.

### AppRole Authentication (Recommended for CI/CD)

AppRole is the preferred authentication method for CI/CD pipelines:

```bash
# Enable AppRole auth method
vault auth enable approle

# Create AppRole
vault write auth/approle/role/ci-role \
  token_ttl=15m \
  token_max_ttl=20m

# Get role ID
vault read auth/approle/role/ci-role/role-id

# Generate secret ID
vault write -f auth/approle/role/ci-role/secret-id
```

Then authenticate in your workflow:

```bash
# Login with AppRole
vault write auth/approle/login \
  role_id="<role-id>" \
  secret_id="<secret-id>"
```

### Connection Parameters

Default test configuration uses:
- **Host:** localhost
- **Port:** 8200
- **Protocol:** HTTP (use HTTPS in production)
- **Dev Token:** dev-token (development mode only)
- **Auth Method:** AppRole (recommended) or Token auth

### Token TTL Configuration

For CI/CD workflows, configure tokens with appropriate TTL:
- **Recommended TTL:** 15-20 minutes (covers most CI/CD jobs)
- **Minimum TTL:** 5 minutes (for quick jobs)
- **Maximum TTL:** 1 hour (for complex multi-step jobs)

## Common Issues and Fixes

### Issue: "Connection refused" error

**Cause:** Vault service container is not running or port is not exposed.

**Fix:**
1. Verify service container is defined in your workflow
2. Ensure port mapping is correct: `8200:8200`
3. Check that image is `hashicorp/vault:1.18` or compatible version
4. Add health check configuration to services

```yaml
services:
  vault:
    image: hashicorp/vault:1.18
    env:
      VAULT_DEV_ROOT_TOKEN_ID: dev-token
      VAULT_DEV_LISTEN_ADDRESS: "0.0.0.0:8200"
    ports:
      - 8200:8200  # Required
    options: >-
      --health-cmd "vault status"
      --health-interval 2s
      --cap-add IPC_LOCK
```

### Issue: "nc: command not found"

**Cause:** Netcat tool is not installed in the runner environment.

**Fix:** The wait-for-service action only tests TCP connectivity. The nc verification step requires netcat to be installed:

```bash
# If using Ubuntu runner, install netcat
- name: Install netcat
  run: sudo apt-get install -y netcat-openbsd

# Then run the service workflow
- uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main
```

Or use Docker image with netcat pre-installed:

```bash
docker run -it hashicorp/vault:1.18 sh -c "nc -zv localhost 8200"
```

### Issue: "Vault is sealed" error

**Cause:** Vault service started but is in sealed state.

**Fix:** In development mode, Vault auto-unseals. Ensure dev flags are set:

```yaml
services:
  vault:
    image: hashicorp/vault:1.18
    env:
      VAULT_DEV_ROOT_TOKEN_ID: dev-token  # Required for auto-unseal
      VAULT_DEV_LISTEN_ADDRESS: "0.0.0.0:8200"  # Required
    options: >-
      --health-cmd "vault status"
      --cap-add IPC_LOCK  # Required for memory locking
```

For production Vault, unseal manually:

```bash
# Get unseal keys and root token from initialization
vault operator unseal <unseal-key-1>
vault operator unseal <unseal-key-2>
vault operator unseal <unseal-key-3>
```

### Issue: "Permission denied" with IPC_LOCK

**Cause:** Container doesn't have permission to lock memory.

**Fix:** Add the `IPC_LOCK` capability:

```yaml
services:
  vault:
    image: hashicorp/vault:1.18
    options: >-
      --cap-add IPC_LOCK  # Required for memory locking
      --health-cmd "vault status"
      --health-interval 2s
```

### Issue: Timeout waiting for Vault (fails after 60 seconds)

**Cause:** Service taking longer than expected to start, or health checks are failing.

**Fix:**
1. Check runner resource availability - Vault needs memory to start
2. Verify health check interval is reasonable:

```yaml
services:
  vault:
    image: hashicorp/vault:1.18
    env:
      VAULT_DEV_ROOT_TOKEN_ID: dev-token
      VAULT_DEV_LISTEN_ADDRESS: "0.0.0.0:8200"
    options: >-
      --health-cmd "vault status"
      --health-interval 2s        # Check every 2 seconds
      --health-timeout 5s         # Allow 5s per check
      --health-retries 30         # Try 30 times max
      --cap-add IPC_LOCK
```

3. Increase runner capacity if available
4. Check Docker image is not corrupted: `docker pull hashicorp/vault:1.18`

### Issue: Port 8200 already in use

**Cause:** Another service is already running on port 8200.

**Fix:**
1. Stop any local Vault instances
2. Use different port in workflow:

```yaml
services:
  vault:
    ports:
      - 8201:8200  # Map to different external port

# Then update connection string
env:
  VAULT_ADDR: http://localhost:8201
```

### Issue: "Invalid token" or authentication failures

**Cause:** Token is invalid, expired, or credentials don't match configuration.

**Fix:** Verify token is correct and matches authentication method:

```yaml
services:
  vault:
    image: hashicorp/vault:1.18
    env:
      VAULT_DEV_ROOT_TOKEN_ID: dev-token  # Match this token
    ports:
      - 8200:8200

jobs:
  tests:
    env:
      VAULT_ADDR: http://localhost:8200
      VAULT_TOKEN: dev-token  # Must match VAULT_DEV_ROOT_TOKEN_ID
    steps:
      - run: vault status
```

### Issue: AppRole secret ID expired

**Cause:** Secret ID has a TTL and expires after use or timeout.

**Fix:** Generate new secret IDs regularly or configure longer TTL:

```bash
# Generate new secret ID for each workflow run
vault write -f auth/approle/role/ci-role/secret-id

# Or configure longer TTL for secret ID
vault write auth/approle/role/ci-role \
  secret_id_ttl=1h
```

## Output Example

### Successful Execution

```
Wait for Vault service
Attempting to connect to localhost:8200
Service is ready (Connected on attempt 2)
vault-ready=true
vault-token-ttl=15-20 minutes

Verify Vault connection
Connection to localhost 8200 port [tcp/*] succeeded!
```

### Failed Execution

```
Wait for Vault service
Attempting to connect to localhost:8200
Service failed to start within timeout (30 attempts, 60 seconds)
vault-ready=false

Error: Service is not ready
```

## Integration with Other Workflows

### Multi-Service Setup

```yaml
jobs:
  postgres-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/postgresql-service.yml@main

  vault-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main

  integration-tests:
    needs: [postgres-service, vault-service]
    if: |
      ${{ needs.postgres-service.outputs.postgres-ready == 'true' &&
          needs.vault-service.outputs.vault-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    env:
      VAULT_ADDR: http://localhost:8200
      VAULT_TOKEN: dev-token
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --integration
```

### Secrets Management Workflow

```yaml
jobs:
  vault-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main

  setup-secrets:
    needs: vault-service
    if: ${{ needs.vault-service.outputs.vault-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    env:
      VAULT_ADDR: http://localhost:8200
      VAULT_TOKEN: dev-token
    steps:
      - uses: actions/checkout@v4
      - run: npm run setup:vault-secrets

  tests:
    needs: [vault-service, setup-secrets]
    runs-on: [self-hosted, linux, X64, kubernetes]
    env:
      VAULT_ADDR: http://localhost:8200
      VAULT_TOKEN: dev-token
    steps:
      - uses: actions/checkout@v4
      - run: npm test -- --secrets
```

### AppRole Authentication Flow

```yaml
jobs:
  vault-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main

  authenticate:
    needs: vault-service
    if: ${{ needs.vault-service.outputs.vault-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    env:
      VAULT_ADDR: http://localhost:8200
    steps:
      - name: Authenticate with AppRole
        id: auth
        run: |
          TOKEN=$(vault write -field=client_token auth/approle/login \
            role_id="${{ secrets.VAULT_ROLE_ID }}" \
            secret_id="${{ secrets.VAULT_SECRET_ID }}")
          echo "::add-mask::$TOKEN"
          echo "vault-token=$TOKEN" >> "$GITHUB_OUTPUT"

      - name: Retrieve secrets
        env:
          VAULT_TOKEN: ${{ steps.auth.outputs.vault-token }}
        run: vault kv get secret/app/config
```

## Performance

- **Service Startup:** ~1-2 seconds (typical)
- **First Health Check:** Immediate on service availability
- **Total Wait Time:** 1-8 seconds (depends on host load)
- **Timeout Threshold:** 60 seconds (30 retries × 2 seconds)
- **Network Overhead:** Minimal (local TCP checks)
- **Token Generation:** ~100ms (AppRole login)

### Performance Tips

1. **Use default retry count** - 30 retries is optimal for most cases
2. **Enable health checks** - Docker health checks improve reliability
3. **Use Alpine image** - `hashicorp/vault:1.18-alpine` is lighter if available
4. **Check runner resources** - Ensure adequate CPU and memory
5. **Cache authentication tokens** - Reuse tokens for multiple requests
6. **Use AppRole** - AppRole is faster than other auth methods for automation

## Token Management Best Practices

### Token Lifecycle

For CI/CD workflows:

```javascript
// Get TTL from workflow output
const ttl = process.env.VAULT_TOKEN_TTL; // "15-20 minutes"

// Tokens should be renewed if approaching expiration
// Set renewal threshold to ~70% of TTL (10-14 minutes)
if (timeElapsed > tokenTTL * 0.7) {
  renew_token();
}
```

### AppRole with Metadata

Add metadata to AppRole for better tracking:

```bash
vault write auth/approle/role/ci-role \
  token_ttl=15m \
  bind_secret_id=true \
  policies="ci-policy" \
  metadata="ci-workflow=true,environment=test"
```

## Customization

### Changing Connection Parameters

Override the connection URL in your verification step:

```yaml
jobs:
  vault-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main

  custom-test:
    needs: vault-service
    if: ${{ needs.vault-service.outputs.vault-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    env:
      VAULT_ADDR: http://localhost:8200
      VAULT_TOKEN: dev-token
    steps:
      - run: vault status
```

### Using Different Vault Versions

Modify the service container image:

```yaml
services:
  vault:
    image: hashicorp/vault:1.17  # Use Vault 1.17 instead
    env:
      VAULT_DEV_ROOT_TOKEN_ID: dev-token
      VAULT_DEV_LISTEN_ADDRESS: "0.0.0.0:8200"
    # ... rest of configuration
```

Then consume the service in your workflow.

### Custom Health Checks

Extend the verification with application-specific checks:

```yaml
jobs:
  vault-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main

  advanced-verification:
    needs: vault-service
    if: ${{ needs.vault-service.outputs.vault-ready == 'true' }}
    runs-on: [self-hosted, linux, X64, kubernetes]
    env:
      VAULT_ADDR: http://localhost:8200
      VAULT_TOKEN: dev-token
    steps:
      - name: Check Vault status
        run: vault status

      - name: List auth methods
        run: vault auth list

      - name: Test secret storage
        run: |
          vault kv put secret/test key=value
          vault kv get secret/test

      - name: Check token info
        run: vault token lookup
```

## Troubleshooting

### Debug Mode

Add debug output to understand what's happening:

```yaml
jobs:
  vault-service:
    uses: WasteHero/wastehero-github-actions/.github/workflows/services/vault-service.yml@main

  debug:
    needs: vault-service
    runs-on: [self-hosted, linux, X64, kubernetes]
    env:
      VAULT_ADDR: http://localhost:8200
      VAULT_TOKEN: dev-token
    steps:
      - name: Show service status
        run: docker ps -a

      - name: Check network connectivity
        run: netstat -tlnp | grep 8200

      - name: Test vault directly
        run: vault status

      - name: Check container logs
        run: docker logs $(docker ps -q --filter="ancestor=hashicorp/vault:1.18")
```

### Manual Service Startup

For testing locally:

```bash
# Start Vault in Docker (development mode)
docker run --rm -d \
  --name vault \
  -e VAULT_DEV_ROOT_TOKEN_ID=dev-token \
  -e VAULT_DEV_LISTEN_ADDRESS="0.0.0.0:8200" \
  -p 8200:8200 \
  --cap-add IPC_LOCK \
  hashicorp/vault:1.18

# Wait a few seconds, then verify
sleep 2
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=dev-token
vault status

# Clean up
docker stop vault
```

## Best Practices

1. **Always use the output** - Check `vault-ready` before running dependent jobs
2. **Health checks in services** - Configure Docker health checks for faster detection
3. **Reasonable retry count** - 30 retries (60 seconds) works for most scenarios
4. **Use AppRole for CI/CD** - AppRole is the recommended authentication method
5. **Rotate secret IDs** - Generate new secret IDs for security
6. **Configure appropriate TTL** - 15-20 minutes is typical for CI/CD tokens
7. **Enable IPC_LOCK** - Protect Vault memory from being swapped to disk
8. **Use HTTPS in production** - Development mode uses HTTP, production must use HTTPS
9. **Document secrets paths** - Make it clear which secrets jobs need
10. **Monitor token usage** - Track which jobs are authenticating

## Related Documentation

- [PostgreSQL Service Workflow](./postgresql-service-workflow.md) - Sibling service workflow for PostgreSQL
- [ValKey Service Workflow](./valkey-service-workflow.md) - Cache service workflow
- [NATS Service Workflow](./nats-service-workflow.md) - Message broker service workflow
- [Service Composition Workflows](./README.md#service-composition-workflows-phase-2) - Overview of all service workflows
- [How to Debug Workflow Failures](../how-to-guides/debugging-workflow-failures.md) - Troubleshooting guide
- [Vault Documentation](https://www.vaultproject.io/docs) - Official Vault documentation
- [AppRole Auth Method](https://www.vaultproject.io/docs/auth/approle) - AppRole authentication guide

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 7, 2025 | Initial release, Vault 1.18 with AppRole auth support |

---

**Questions?** See [How-To Guides](../how-to-guides/README.md) for common problems or [Explanation](../explanation/README.md) for conceptual understanding.
