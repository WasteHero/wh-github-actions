# Claude Custom Agent Workflow Reference

**Reference:** CT-1188
**Status:** Production
**Last Updated:** December 8, 2025

## Overview

The Claude Custom Agent workflow provides on-demand, interactive AI assistance by responding to @claude mentions in pull request and issue comments. Unlike the automatic PR Review workflow (CT-1187), this workflow enables developers to trigger custom agents with specific directives, making it ideal for targeted analysis, debugging, and decision support when needed rather than on every code change.

| Property | Value |
|----------|-------|
| Purpose | On-demand AI assistance via @claude mentions |
| Type | Interactive (user-triggered, informational) |
| Trigger | Issue comments, PR review comments with @claude mention |
| Speed | 30-180 seconds depending on agent complexity |
| Dependencies | None |
| Secrets Required | ANTHROPIC_API_KEY |
| Permissions Required | contents: read, pull-requests: write, issues: write |
| Model | Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) |
| Runner | [self-hosted, linux, X64, kubernetes] |
| File Location | `.github/workflows/ai/claude-custom-agent.yml` |
| Max Turns | 10 (interactive conversation depth) |
| Supported Agents | @agent-py-reviewer, @agent-js-reviewer, @agent-devops-expert (and custom agents) |

## Purpose

Enable developers to request on-demand AI analysis using custom agents with specific directives:

- **User-Controlled**: Triggered only when developer adds @claude mention in comments
- **Agent-Powered**: Supports @agent-py-reviewer, @agent-js-reviewer, @agent-devops-expert
- **Flexible Focus**: Developers specify what they need analyzed (performance, security, architecture, etc.)
- **Informational Only**: Never blocks workflows or PR merges
- **Interactive**: Supports multi-turn conversations (up to 10 turns)
- **Dual-Source Loading**: Loads agents from both WasteHero/claude-development-environment and ~/.wastehero/agents/ on runner
- **Graceful Fallback**: Continues with available agents if custom agents not found
- **Non-Blocking**: Workflow always succeeds even if agent encounters errors
- **Cost-Efficient**: Uses Claude Haiku 4.5 for optimal performance and pricing

## How It Differs from PR Review Workflow

The Claude PR Review workflow (CT-1187) and Custom Agent workflow serve different purposes:

| Aspect | PR Review (CT-1187) | Custom Agent (CT-1188) |
|--------|-------------------|----------------------|
| **Triggering** | Automatic on PR open/update | Manual, via @claude mention |
| **Frequency** | Every PR change | Only when requested |
| **Agent** | Fixed (@agent-py-reviewer) | User-selectable (py-reviewer, js-reviewer, etc.) |
| **Directive** | Standard review focus | Custom ("check performance", "security analysis", etc.) |
| **Scope** | All code changes | Specific areas user mentions |
| **Conversations** | Single response (2 turns) | Multi-turn (up to 10 turns) |
| **Availability** | PRs only | Issues and PRs |
| **Comments** | Always posted | Posted per user request |
| **Use Case** | Continuous feedback | Targeted assistance on demand |

## Trigger

The workflow triggers on comment creation with @claude mention:

```yaml
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  custom-agent:
    if: contains(github.event.comment.body, '@claude')
```

### What Each Event Does

- **`issue_comment` / `created`**: Triggers when a comment is added to an issue, if it contains @claude
- **`pull_request_review_comment` / `created`**: Triggers when a review comment is added to a PR, if it contains @claude

### Important Notes

- **Exact Mention Required**: The comment must contain `@claude` (not `@Claude`, case-sensitive by default)
- **User-Initiated**: Only runs when someone intentionally adds the mention
- **Immediate Processing**: Starts workflow within seconds of comment being posted
- **Works in Both Contexts**: Functions equally in issues and PR review comments

## Basic Usage

### Simple Agent Request

To request custom agent analysis, add a comment with @claude mention:

```
@claude review this code for performance issues
```

The workflow will:
1. Detect the @claude mention
2. Load available agents
3. Invoke Claude with the comment text
4. Post a response (if multi-turn, you can reply for follow-up)

### Request with Specific Agent

Specify which agent to use:

```
@claude @agent-py-reviewer check this for security vulnerabilities
```

### Multi-Turn Conversation

Start with an initial request, then reply to Claude's response:

```
@claude @agent-devops-expert review this deployment configuration

(Claude responds...)

@claude can you specifically check the IAM policies?

(Claude responds to follow-up)
```

The conversation continues up to 10 turns (developer → Claude → developer → ... up to 10 total messages).

### Usage Examples

**Example 1: Performance Analysis**
```
@claude analyze this function for performance bottlenecks. It's called frequently
in the hot path. Should we optimize the database queries?
```

**Example 2: Architecture Review**
```
@claude @agent-devops-expert what's your assessment of this microservices
architecture? Any scalability concerns?
```

**Example 3: Security Audit**
```
@claude @agent-py-reviewer carefully review this authentication logic for
security vulnerabilities. Look especially at token handling.
```

**Example 4: Debug Assistance**
```
@claude help me understand why this test is flaking. It passes locally but
fails in CI sometimes. Any patterns you notice?
```

**Example 5: Code Review Follow-up**
```
@claude in your previous review, you mentioned the error handling could be
better. Can you suggest a specific refactoring approach?
```

## Inputs

The workflow uses GitHub context directly (no explicit inputs required):

| Context | Source | Purpose |
|---------|--------|---------|
| Comment Body | `github.event.comment.body` | Contains @claude mention and user's request |
| Repository | `github.event.repository` | Repository context for code access |
| Issue/PR Number | `github.event.issue` or `github.event.pull_request` | Identifies where to post response |
| Comment Author | `github.event.comment.user.login` | Identifies who requested assistance |

## Secrets

### ANTHROPIC_API_KEY

**Required:** Yes

Your Anthropic API key for Claude access.

**Where to get it:**
1. Visit https://console.anthropic.com/account/keys
2. Create or copy an existing API key
3. Do NOT share this key

**How to configure:**
1. Go to your repository Settings
2. Navigate to Secrets and variables > Actions
3. Click "New repository secret"
4. Name: `ANTHROPIC_API_KEY`
5. Value: Paste your API key
6. Click "Add secret"

**Security:**
- Store in repository secrets, not in code
- Use organization secrets for shared access
- Rotate keys periodically
- Never commit keys to version control

## Configuration

### Runtime

- **Runner:** `[self-hosted, linux, X64, kubernetes]`
- **Timeout:** 5 minutes per request
- **Model:** Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- **Max turns:** 10 (interactive conversation depth)
- **Agent model:** claude-haiku-4-5-20251001

### Permissions

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

**Explanation:**
- `contents: read` - Allows reading repository code and comments
- `pull-requests: write` - Allows posting responses to PR review comments
- `issues: write` - Allows posting responses to issue comments

### Environment

The workflow runs in a container with:
- Full GitHub context (repo, issue/PR, comment info)
- Access to repository code via checkout
- Git history for context
- Home directory mounting for agent cache (for ~/.wastehero/agents/)

## What It Does

### Step 1: Check Out Code

```bash
actions/checkout@v4
```

- Clones the repository
- Provides code context for Claude
- Necessary for agents to analyze repository structure

### Step 2: Checkout Claude Development Environment

```bash
actions/checkout@v4
  with:
    repository: WasteHero/claude-development-environment
    path: .claude-dev-env
    token: ${{ secrets.GITHUB_TOKEN }}
```

- Fetches the shared agent definitions from WasteHero/claude-development-environment
- Copies agents to `.claude-dev-env/agents/` directory
- Uses GITHUB_TOKEN (automatically provided) for repository access
- Graceful failure: If checkout fails, workflow continues with runner agents

### Step 3: Load Custom Agents

```bash
mkdir -p .claude/agents

# Load agents from development environment repository
if [ -d .claude-dev-env/agents ]; then
  cp -r .claude-dev-env/agents/* .claude/agents/ || true
else
  echo "No custom agents found in repository"
fi

# Also check for agents in runner's home directory (fallback)
if [ -d ~/.wastehero/agents ]; then
  cp -r ~/.wastehero/agents/* .claude/agents/ || true
fi
```

This step:
- Creates `.claude/agents/` directory for agent discovery
- Loads agents from WasteHero/claude-development-environment (primary source)
- Falls back to ~/.wastehero/agents/ on runner (secondary source)
- Continues even if neither source has agents
- Lists loaded agents for debugging

### Step 4: Run Claude with Custom Agents

```bash
anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
    claude_args: "--model claude-haiku-4-5-20251001 --max-turns 10"
```

This step:
- Invokes Claude Code with loaded agents
- Claude reads the @claude mention and comment text
- Passes the repository context and git history
- Supports agent invocation via @agent-name pattern
- Enables multi-turn conversations (up to 10 turns)
- Responds directly to the comment thread

**Supported Agent Invocations:**
- `@claude review this` - Uses default Claude behavior
- `@claude @agent-py-reviewer analyze this` - Invokes Python reviewer agent
- `@claude @agent-js-reviewer check this` - Invokes JavaScript reviewer agent
- `@claude @agent-devops-expert assess this` - Invokes DevOps expert agent
- `@claude @custom-agent-name do this` - Invokes custom agent if loaded

### Step 5: Handle Workflow Errors

```bash
if: failure()
uses: actions/github-script@v7
with:
  script: |
    github.rest.issues.createComment({
      issue_number: context.issue.number || context.payload.pull_request.number,
      owner: context.repo.owner,
      repo: context.repo.repo,
      body: '⚠️ Claude Custom Agent workflow encountered an error. Please check the workflow logs.'
    });
```

If any step fails:
- Posts a warning comment to the issue/PR
- Links to workflow logs for debugging
- Allows developer to see that something went wrong
- Workflow still exits with success (non-blocking)

### Step 6: Workflow Completion

The workflow **always succeeds** (exit 0):
- Errors are handled gracefully
- Responses are posted regardless of outcome
- Never blocks subsequent jobs or PR merge
- Agent errors are caught and reported

## Agent Loading

### Primary Source: WasteHero/claude-development-environment

The workflow first attempts to load agents from the shared repository:

```bash
actions/checkout@v4
  with:
    repository: WasteHero/claude-development-environment
    path: .claude-dev-env
```

**Expected Structure:**
```
WasteHero/claude-development-environment
  agents/
    py-reviewer.md
    js-reviewer.md
    devops-expert.md
```

**Benefits:**
- Centralized agent maintenance
- Consistent agent behavior across all repositories
- Easy updates (version through git refs)
- Shared patterns and prompts

### Secondary Source: Runner Home Directory

If development environment checkout fails, agents are loaded from runner:

```bash
if [ -d ~/.wastehero/agents ]; then
  cp -r ~/.wastehero/agents/* .claude/agents/ || true
fi
```

**Expected Structure:**
```
~/.wastehero/agents/
  py-reviewer.md
  js-reviewer.md
  devops-expert.md
  custom-agent-1.md
  custom-agent-2.md
```

**Benefits:**
- Fallback for CI/CD isolation
- Custom agents specific to this runner
- Quick iteration without repository commits
- Local development environment mirror

### How Agent Discovery Works

After loading, Claude Code discovers agents by:
1. Scanning `.claude/agents/` directory
2. Looking for markdown files (*.md)
3. Parsing agent definitions from frontmatter
4. Registering @agent-name patterns for invocation
5. Making agents available via @agent-py-reviewer, @agent-js-reviewer, etc.

### Custom Agent Creation

To create a custom agent, create a markdown file in either location:

**File: ~/.wastehero/agents/my-custom-agent.md**
```markdown
---
agent: my-custom-agent
description: "Analyzes feature flags and configuration management"
skills:
  - feature flag analysis
  - configuration validation
  - deployment readiness
---

# My Custom Agent

You are an expert in feature flag management and configuration systems.

## Your Role

- Analyze feature flag implementation for correctness
- Validate configuration schemas
- Ensure safe deployment procedures
- Review rollout strategies

## Analysis Format

Return analysis in structured JSON:
{
  "summary": "Overall assessment",
  "findings": ["finding 1", "finding 2"],
  "recommendations": ["recommendation 1"],
  "severity": "info|warning|critical"
}
```

Then invoke with:
```
@claude @my-custom-agent analyze this feature flag implementation
```

## Common Issues and Fixes

### 1. @claude Mention Not Detected

**Problem:**
```
Posted @claude comment but workflow didn't run
```

**Cause:** Mention wasn't recognized or exact syntax not matched

**Fix:**
- Ensure comment contains `@claude` (case-sensitive)
- Check it's not escaped or in code block
- Verify workflow is enabled in Actions tab
- Confirm comment was successfully posted before checking

**Example Correct:**
```
@claude review this function
```

**Example Incorrect:**
```
@Claude review this (wrong case)
`@claude` review this (in code block)
@ claude review this (space between @ and claude)
```

**Debug:**
1. Go to Actions tab
2. Look for "Claude Custom Agents" workflow
3. Check if recent runs appear
4. If not, enable the workflow

### 2. Agent Files Not Found

**Problem:**
```
Workflow runs but Claude can't find custom agents
```

**Cause:** Agent files not loaded from either source

**Fix:**
1. Check WasteHero/claude-development-environment is accessible:
   ```bash
   curl -I https://github.com/WasteHero/claude-development-environment
   ```

2. Verify runner has ~/.wastehero/agents/:
   ```bash
   ssh runner
   ls -la ~/.wastehero/agents/
   ```

3. Check workflow logs for agent loading step
4. Ensure agent filenames use kebab-case (py-reviewer.md, not py_reviewer.md)

**Graceful Behavior:**
- Workflow continues even if agents aren't found
- Claude responds without custom agent patterns
- Still provides useful analysis

### 3. Custom Agents Directory Not Present

**Problem:**
```
Runner is new/freshly provisioned, no custom agents available
```

**Cause:** ~/.wastehero/agents/ not yet created on runner

**Fix:**
1. On runner, create directory:
   ```bash
   mkdir -p ~/.wastehero/agents
   ```

2. Copy agent definitions:
   ```bash
   cp /path/to/agents/*.md ~/.wastehero/agents/
   ```

3. Or rely on WasteHero/claude-development-environment primary source

### 4. API Key Missing or Invalid

**Problem:**
```
Error: ANTHROPIC_API_KEY secret not found
or
Error: Invalid API key provided
```

**Cause:** Secret not configured or key is incorrect

**Fix:**
1. Go to Repository Settings
2. Click Secrets and variables > Actions
3. Verify `ANTHROPIC_API_KEY` exists
4. Test API key at https://console.anthropic.com/account/keys
5. If expired, generate new key and update secret
6. Workflow will use new key on next @claude mention

### 5. Slow Responses

**Problem:**
```
Claude takes 1-3 minutes to respond to comment
```

**Cause:** Queue delays, model throughput, or complex request

**Fix:**
- This is normal for cloud-based API under load
- Responses typically arrive within 30-180 seconds
- Complex analysis (10+ files) may take longer
- If > 5 minutes, check workflow logs for errors

**To Speed Up:**
- Make requests more specific (narrows analysis scope)
- Use shorter comments (less text = faster processing)
- Avoid requesting analysis of entire large codebases
- Use specific agent for better performance (e.g., @agent-py-reviewer not generic Claude)

### 6. Agent Crashes or Returns Errors

**Problem:**
```
Workflow completes but Claude response shows error
Agent fails with "I cannot analyze this code"
```

**Cause:** Agent definition has issues or request is outside agent scope

**Fix:**
1. Verify agent file is valid markdown with proper frontmatter
2. Check agent description and skills match your request
3. Try again with more context (reference specific lines)
4. Fall back to generic Claude if agent is specialized
5. Check agent file has proper formatting:

   ```markdown
   ---
   agent: agent-name
   description: "What this agent does"
   ---
   # Agent content below
   ```

### 7. Permissions Problem

**Problem:**
```
Workflow runs but cannot post comment
Error: Permission denied when posting response
```

**Cause:** Missing permissions in workflow

**Fix:**
1. Add permissions to workflow:
   ```yaml
   permissions:
     contents: read
     pull-requests: write
     issues: write
   ```

2. Or add to repository workflow defaults

3. Verify GitHub token has write access

4. Check repository settings allow workflow comments

### 8. Testing Workflow Locally

**Problem:**
```
Want to test Claude custom agents before using in production
```

**Solution:**
1. Create a test repository (private)
2. Copy the workflow file:
   ```bash
   cp .github/workflows/ai/claude-custom-agent.yml /path/to/test-repo/.github/workflows/
   ```

3. Configure ANTHROPIC_API_KEY secret in test repo
4. Create a test issue or PR
5. Add comment with @claude mention
6. Monitor workflow execution in Actions tab
7. Debug any issues before applying to main repository

### 9. Multiple Agent Mentions in One Comment

**Problem:**
```
@claude @agent-py-reviewer and @agent-js-reviewer check this code
```

**Cause:** Unclear which agent should be invoked

**Fix:**
- Only one primary agent is typically used
- Make separate comments for different agent perspectives:
  ```
  Comment 1: @claude @agent-py-reviewer check this Python code
  Comment 2: @claude @agent-js-reviewer check this JavaScript code
  ```

- Or request multi-perspective in single agent:
  ```
  @claude review this code from both Python and JavaScript perspectives
  ```

### 10. Comment Edited After Initial Trigger

**Problem:**
```
Posted @claude comment, then edited it, but workflow doesn't re-trigger
```

**Cause:** Workflow only triggers on comment creation, not edit

**Fix:**
- To get re-analysis with updated request:
  - Delete original comment
  - Post new comment with @claude mention
  - This creates new event that triggers workflow

- Alternatively:
  - Reply to Claude's response to continue conversation (works in multi-turn)
  - This doesn't require new @claude mention

### 11. Agent Not Invoked (Generic Claude Instead)

**Problem:**
```
Used @claude @agent-py-reviewer but Claude didn't use Python agent
```

**Cause:** Agent not found or not properly loaded

**Fix:**
1. Verify agent file exists in one of two locations:
   - WasteHero/claude-development-environment/agents/py-reviewer.md
   - ~/.wastehero/agents/py-reviewer.md

2. Check agent is registered (proper markdown with frontmatter)
3. Verify filename matches agent name (py-reviewer.md for @agent-py-reviewer)
4. Check workflow logs show "agents loaded" message
5. Try without agent mention (generic Claude) as fallback

### 12. Workflow Appears to Hang

**Problem:**
```
Workflow started but no response appears in comment
Waiting > 5 minutes
```

**Cause:** Long-running request, queue delay, or timeout

**Fix:**
1. Check workflow logs:
   - Go to Actions tab
   - Click "Claude Custom Agents" workflow
   - Look for running job
   - Check logs for errors or stuck steps

2. If still running after 5 minutes:
   - GitHub will timeout and kill job
   - Check logs for what failed
   - Try again with simpler request

3. If stuck:
   - Comment a follow-up @claude message (might unstick)
   - Or wait for timeout to complete

## Configuration and Requirements

### Agent Repository Access

The workflow requires read access to WasteHero/claude-development-environment:

- **Uses:** `GITHUB_TOKEN` (automatically provided by GitHub Actions)
- **Permissions:** Requires `contents: read` on external repository
- **Repository:** WasteHero/claude-development-environment (public)
- **Path:** Agents checked out to `.claude-dev-env/agents/` directory
- **Fallback:** If checkout fails, uses runner's ~/.wastehero/agents/

If checkout fails, verify:
- Repository is not restricted
- Branch/ref exists
- GITHUB_TOKEN has appropriate permissions
- Network connectivity to GitHub

### Runner Agents

Secondary agent source on runner:

- **Location:** ~/.wastehero/agents/
- **Permissions:** Must be readable by workflow user
- **Format:** Markdown files (*.md) with agent definitions
- **Scope:** Specific to this runner (not shared)
- **Management:** Updated manually or via deployment scripts

### Agent File Format

Agents should follow this markdown structure:

```markdown
---
agent: agent-name
description: "What this agent does"
skills:
  - skill 1
  - skill 2
aliases:
  - alternative-name
---

# Agent Name

Description of what this agent does and when to use it.

## Capabilities

- Capability 1
- Capability 2

## Usage

Instructions for using the agent.

## Response Format

JSON schema or format the agent uses for responses.
```

## Performance

### Typical Execution Times

- **Workflow startup:** 5-10 seconds
- **Agent loading:** 2-5 seconds
- **Claude analysis:** 15-60 seconds (depending on request complexity)
- **Response posting:** 2-3 seconds
- **Total typical:** 30-90 seconds from comment to response

### What Affects Speed

- **Request complexity** - "review this" is faster than "analyze entire architecture"
- **Code size** - Analyzing 100 LOC is faster than 10,000 LOC
- **API queue** - Peak times slower than off-peak
- **Agent sophistication** - Specialized agents may be slower than generic Claude
- **Number of turns** - Each reply adds 30-60 seconds

### Timeout Configuration

- **Default:** 5 minutes per workflow run
- **Per request:** If > 5 minutes, GitHub Actions will timeout
- **Handle failure:** Workflow has error handler to post notification

### Cost Per Request

- **Haiku 4.5 typical:** ~$0.001-0.01 per request
- **Average 1000-token request:** ~$0.005
- **With 10-turn conversation:** ~$0.05
- **Compare:** Much cheaper than PR Review workflow due to on-demand nature

**Estimate:** For 10 @claude requests per day:
- ~10 requests × $0.005 average = ~$0.05/day
- ~$1.50/month
- Very cost-efficient

## Best Practices

### Agent Usage

**Do:**
- Request specific analysis ("check this for SQL injection", not "review this")
- Mention file names and line numbers for context
- Use appropriate agent for domain (@agent-devops-expert for infrastructure)
- Break complex requests into multiple focused questions
- Use follow-up comments in multi-turn for clarification

**Don't:**
- Request vague analysis ("what do you think about this?")
- Paste entire files without specific question
- Use wrong agent for domain (Python review with @agent-js-reviewer)
- Ask for code generation (outside agent scope, use Claude Code directly)
- Overload with too much context at once

### When to Use Custom Agents

**Ideal Use Cases:**
- Quick feedback on specific code before committing
- Performance analysis of hot paths
- Security audit of authentication logic
- Architecture review of new components
- Debugging flaky tests
- DevOps/infrastructure assessment
- Multi-perspective analysis (Python + JavaScript in separate comments)

**Not Ideal:**
- Every code change (use PR Review workflow instead)
- Continuous feedback (use PR Review workflow)
- Code generation tasks (use Claude Code directly)
- Trivial questions (too much overhead)

### Comment Etiquette

**Good:**
```
@claude review line 45-60 for performance issues. This function
is in our hot path and handles 1000 requests/second. Any optimization
opportunities?
```

**Poor:**
```
@claude what do you think
```

**Good:**
```
@claude can you explain why this test flakes in CI but passes locally?
Test at tests/payment/test_processor.py:123
```

**Poor:**
```
@claude help
```

### Cost Optimization

- **Specific requests** are cheaper (less processing)
- **Fewer tokens** in request = lower cost
- **Single agent** invocations are more efficient than multiple agents
- **Focused questions** need less analysis

### Performance Tips

- Reference specific lines/functions (helps agent scope analysis)
- Include relevant configuration in comment if applicable
- Mention context (e.g., "this runs 1000s of times per minute")
- Keep requests to single concern (architecture, performance, security)

### Monitoring Usage

To track custom agent usage:

1. Review GitHub Actions workflow runs
2. Check `ANTHROPIC_API_KEY` usage in Anthropic console
3. Monitor comment frequency on issues/PRs
4. Estimate costs from typical request patterns

## Related Documentation

- **[Claude PR Review Workflow (CT-1187)](./claude-pr-review-workflow.md)** - Automatic feedback on every PR
- **[Python Quality Gate (CT-1179)](./python-quality-gate-workflow.md)** - Blocking quality checks
- **[Python Review Gate (CT-1183)](./python-review-gate-workflow.md)** - Comprehensive code analysis
- **[Python Lint Workflow (CT-1181)](./python-lint-workflow.md)** - Linting and style checks
- **[WasteHero Claude Development Environment](https://github.com/WasteHero/claude-development-environment)** - Shared agent repository

## Version History

### v1.0 (December 8, 2025)

**Initial Release**
- Comment-based triggering via @claude mention
- Support for custom agents from external repository
- Fallback to runner home directory (~/.wastehero/agents/)
- Multi-turn conversation support (up to 10 turns)
- Graceful error handling with error notification
- Support for issues and PR review comments
- Non-blocking workflow execution
- Interactive agent invocation patterns

## Changelog

### v1.0 Features
- Responds to @claude mentions in issue and PR review comments
- Loads custom agents from WasteHero/claude-development-environment repository
- Falls back to ~/.wastehero/agents/ on runner if primary source unavailable
- Supports @agent-py-reviewer, @agent-js-reviewer, @agent-devops-expert patterns
- Enables multi-turn conversations (up to 10 turns for interactive debugging)
- Always succeeds (never blocks workflow, graceful error handling)
- Posts error notification to issue/PR if workflow fails
- Uses Claude Haiku 4.5 for cost-efficient analysis
- Requires contents:read, pull-requests:write, issues:write permissions

**Key Differences from PR Review:**
- User-triggered (not automatic)
- Multi-agent support (not just @agent-py-reviewer)
- Works in issues and PR comments (not just PR review)
- Up to 10 turns (not 2 turns)
- Requires @claude mention (not automatic)

**Related Issues:**
- CT-1188: Claude Custom Agent Workflow
- CT-1187: Claude PR Review Workflow
- Integration with WasteHero/claude-development-environment
