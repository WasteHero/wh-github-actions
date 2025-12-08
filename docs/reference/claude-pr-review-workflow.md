# Claude PR Review Workflow Reference

**Reference:** CT-1187
**Status:** Production
**Last Updated:** December 8, 2025

## Overview

The Claude PR Review workflow provides intelligent, non-blocking code feedback on pull requests using Claude Haiku 4.5. Unlike blocking quality gates, this informational workflow always posts constructive code review comments without preventing PR merges, making it ideal for continuous learning and code improvement guidance.

| Property | Value |
|----------|-------|
| Purpose | Informational code review with AI feedback |
| Type | Informational (non-blocking) |
| Trigger | Pull requests (opened, synchronize, ready_for_review) |
| Speed | 30-90 seconds per PR |
| Dependencies | None |
| Secrets Required | ANTHROPIC_API_KEY |
| Permissions Required | contents: read, pull-requests: write |
| Model | Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) |
| Runner | [self-hosted, linux, X64, kubernetes] |
| File Location | `.github/workflows/ai/claude-pr-review.yml` |
| Draft PRs | Skipped (feature, not a limitation) |

## Purpose

Provide constructive code feedback on pull requests to help developers improve code quality using the @agent-py-reviewer pattern:

- **Agent-Powered**: Uses @agent-py-reviewer from WasteHero/claude-development-environment
- **Structured Output**: Generates JSON schema-formatted analysis for reliable parsing
- **Informational Only**: Never blocks PR merges or subsequent jobs
- **Always Posts Feedback**: Comments even when code is excellent quality
- **Learning-Oriented**: Suggests improvements and best practices
- **Complementary**: Works alongside blocking quality gates (CT-1179, CT-1183)
- **Cost-Efficient**: Uses Claude Haiku 4.5 for optimal performance and pricing
- **Real-Time**: Provides feedback as PRs are opened or updated

## Trigger

The workflow triggers on pull request events:

```yaml
on:
  pull_request:
    types:
      - opened
      - synchronize
      - ready_for_review
```

### What Each Event Does

- **`opened`**: Triggers when a PR is first created
- **`synchronize`**: Triggers when new commits are pushed to the PR
- **`ready_for_review`**: Triggers when a draft PR is marked as ready

### Important Note: Draft PRs

The workflow automatically skips draft pull requests. This is intentional because:
- Draft PRs are typically work-in-progress
- Feedback on incomplete code may be premature
- Developers can still request reviews manually if needed

When a draft PR is marked as ready for review, the workflow will then run.

## Basic Usage

### Using in Your Repository

Add to your workflow file (e.g., `.github/workflows/ci.yml`):

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  claude-review:
    uses: WasteHero/wastehero-github-actions/.github/workflows/ai/claude-pr-review.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Complete Pipeline with Quality Gates

Combine with blocking gates for comprehensive analysis:

```yaml
name: Python CI with AI Review

on:
  pull_request:
    branches: [main]

jobs:
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  review-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-review-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  claude-review:
    uses: WasteHero/wastehero-github-actions/.github/workflows/ai/claude-pr-review.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  lint:
    needs: quality-gate
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main

  tests:
    needs: [quality-gate, review-gate]
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pytest
```

### With Only Informational Review (No Blocking Gates)

For teams that prefer optional quality checks:

```yaml
name: CI with Feedback

on:
  pull_request:
    branches: [main]

jobs:
  claude-review:
    uses: WasteHero/wastehero-github-actions/.github/workflows/ai/claude-pr-review.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  lint:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-lint.yml@main

  tests:
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: pytest
```

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `project` | string | Yes | Repository name (e.g., `owner/repo`) - typically `${{ github.repository }}` |
| `pr-number` | number | Yes | Pull request number - typically `${{ github.event.pull_request.number }}` |

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
- **Timeout:** 5 minutes
- **Model:** Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- **Max turns:** 2 (conversation depth)

### Permissions

```yaml
permissions:
  contents: read
  pull-requests: write
```

**Explanation:**
- `contents: read` - Allows reading repository code and PR changes
- `pull-requests: write` - Allows posting comments to pull requests

### Environment

The workflow runs in a container with:
- Full GitHub context (repo, PR, branch info)
- Access to PR code via checkout
- Git history for context

## What It Does

### Step 1: Check Out Code
```bash
actions/checkout@v4
  with:
    fetch-depth: 0
```
- Clones the repository
- Includes full git history (depth: 0)
- Necessary for Claude to understand code changes

### Step 2: Checkout Claude Agents
```bash
actions/checkout@v4
  with:
    repository: WasteHero/claude-development-environment
    path: .claude/agents
    token: ${{ secrets.GITHUB_TOKEN }}
```
- Fetches the @agent-py-reviewer agent definition from WasteHero/claude-development-environment
- Copies agent configuration to `.claude/agents/` for Claude Code to discover
- Uses GITHUB_TOKEN (automatically provided) for repository access

### Step 3: Setup Agents
- Ensures `.claude/agents/py-reviewer.md` is accessible to Claude Code
- Registers @agent-py-reviewer pattern for use in prompts
- Validates agent configuration is correct

### Step 4: Prepare Review Context and Run Agent
```bash
anthropics/claude-code-action@v1
  --model claude-haiku-4-5-20251001
  --max-turns 2
```

Sends PR context to Claude with @agent-py-reviewer pattern to:
- Invoke the structured review agent
- Analyze code quality and style with JSON schema output
- Identify potential bugs or issues
- Suggest improvements
- Check for security concerns
- Review test coverage
- Comment on performance considerations
- Return structured JSON response for reliable parsing

**Agent Output Format (JSON Schema):**
```json
{
  "summary": "Overall assessment",
  "categories": {
    "quality": ["finding 1", "finding 2"],
    "performance": ["finding 1"],
    "security": ["finding 1"],
    "testing": ["finding 1"]
  },
  "recommendations": ["action 1", "action 2"],
  "praise": ["positive observation"]
}
```

### Step 5: Parse and Post Review Comment

Claude's JSON-structured feedback is parsed and posted as a PR comment with:
- Summary of findings
- Organized by issue category
- Line-number references
- Actionable suggestions
- Praise for good patterns

Posted using `github-script` action to ensure reliable formatting and parsing.

### Step 6: Workflow Completion

The workflow **always succeeds** (exit 0):
- No code changes cause failure
- Comment is posted regardless of feedback
- Never blocks subsequent jobs or PR merge
- JSON parsing errors are handled gracefully

## PR Comments

### Comment Format

Example PR comment from Claude:

```
## Claude PR Review

Great work on this PR! Here are some observations:

### Code Quality
- The error handling in `handle_payment.py:45-52` could be more specific
  - Consider catching individual exception types instead of bare except
  - Suggestion: Add logging before re-raising

### Potential Improvements
- The `fetch_user_data()` function could benefit from caching
  - This function is called 3 times in the test suite
  - Suggestion: Use @lru_cache or implement memoization

### Well Done
- Excellent test coverage in `tests/payment/test_gateway.py`
- Clear variable naming throughout
- Good use of type hints

### Questions
- Is the database connection pooling configured? (Found in `db_init.py:22`)
  - Could affect performance under load
  - Suggest reviewing connection pool size settings
```

### What You'll Always See

- Comments are always posted (even for excellent code)
- Feedback is constructive and learning-focused
- Issues are categorized (Quality, Performance, Security, Testing, etc.)
- Actionable suggestions are provided
- File paths and line numbers are referenced

### No Code Changes

The workflow:
- Never commits changes
- Never approves or requests changes
- Never affects the PR's merge status
- Purely advisory

## Configuration and Requirements

### Agent Repository Checkout

The workflow requires access to WasteHero/claude-development-environment:

- **Uses:** `GITHUB_TOKEN` (automatically provided by GitHub Actions)
- **Permissions:** Requires `contents: read` on the external repository
- **Repository:** WasteHero/claude-development-environment (public)
- **Path:** Agents checked out to `.claude/agents/` directory

If checkout fails, verify:
- Repository access is not restricted
- Branch/ref exists in claude-development-environment
- GITHUB_TOKEN has appropriate permissions

## Common Issues and Fixes

### 1. API Key Not Configured

**Problem:**
```
Error: ANTHROPIC_API_KEY secret not found
```

**Cause:** The secret hasn't been added to the repository

**Fix:**
1. Go to Repository Settings
2. Click Secrets and variables > Actions
3. Create a new secret named `ANTHROPIC_API_KEY`
4. Paste your API key from https://console.anthropic.com/account/keys
5. The workflow will automatically use it on the next PR

### 2. Workflow Doesn't Run on Draft PRs

**Problem:**
```
Workflow doesn't start when I create a draft PR
```

**Cause:** By design, the workflow skips draft pull requests

**Fix:**
- Mark the draft PR as "Ready for review"
- This triggers the workflow to run
- This is intentional to avoid feedback on work-in-progress code

**Workaround:** If you want feedback on draft PRs:
- Create a comment on the PR with `@claude-review` (if enabled)
- Or mark as ready for review temporarily

### 2a. Agent Checkout Fails

**Problem:**
```
Error: Could not checkout WasteHero/claude-development-environment
Failed to clone repository
```

**Cause:** Repository access issue or agent path problem

**Fix:**
1. Verify repository exists: https://github.com/WasteHero/claude-development-environment
2. Check GITHUB_TOKEN permissions in workflow
3. Verify branch/ref exists in the agent repository
4. Check `.claude/agents/` path is writable
5. Review agent file structure (should contain py-reviewer.md)

**Debug:**
```yaml
- name: Debug Agent Checkout
  run: |
    ls -la .claude/agents/ || echo "Directory not created"
    ls -la .claude/agents/py-reviewer.md || echo "py-reviewer.md not found"
```

### 2b. No Structured Output (JSON Parsing)

**Problem:**
```
Error: Failed to parse JSON response from Claude
Agent output format is invalid
```

**Cause:** @agent-py-reviewer did not return valid JSON schema

**Fix:**
1. Verify agent file (py-reviewer.md) is properly formatted
2. Check Claude's response includes valid JSON
3. Review github-script parser for correct JSON path
4. Ensure JSON schema matches expected structure

**Expected JSON Structure:**
```json
{
  "summary": "string",
  "categories": {
    "quality": ["string"],
    "performance": ["string"],
    "security": ["string"],
    "testing": ["string"]
  },
  "recommendations": ["string"],
  "praise": ["string"]
}
```

### 3. No Comments Posted

**Problem:**
```
PR shows no review comment from Claude
```

**Cause:** Several possibilities

**Debugging:**
1. Check workflow logs for errors:
   - Go to Actions tab on the PR
   - Look for the claude-pr-review workflow
   - Expand steps to see error messages
   - Check for JSON parsing errors in logs

2. Verify PR permissions:
   - Repository Settings > Actions > Permissions
   - Ensure "Read and write permissions" is enabled

3. Check if PR is a draft:
   - Mark as ready for review if it's a draft

4. Verify API key:
   - Go to Secrets and variables > Actions
   - Confirm `ANTHROPIC_API_KEY` exists and is not empty

5. Check Agent Checkout:
   - Verify Step 2 (Checkout Claude Agents) succeeded
   - Ensure `.claude/agents/py-reviewer.md` exists

6. Check JSON output:
   - Review logs for agent output format
   - Verify github-script can parse the response

7. Check PR size:
   - Extremely large PRs might timeout
   - Break into smaller PRs if possible

**Fix:**
- Add debugging log: Check Actions tab for detailed error messages
- Verify all configuration is correct
- Test with a smaller PR to isolate issues
- Check agent output in workflow logs
- Contact DevOps team if persistent

### 4. Review Quality Issues

**Problem:**
```
Claude's feedback seems generic or not relevant
Agent output doesn't match expectations
```

**Cause:** The agent may need refinement, or code context is unclear

**Fix:**
- Ensure PR description is clear and contextual
- Remember Claude Haiku is a smaller model, optimized for speed
- For more detailed reviews, use the blocking gates (CT-1179, CT-1183)
- The review is designed to be complementary, not exhaustive
- Feedback improves over time as patterns are learned

**Customization:** If you need custom review behavior:
- Fork the py-reviewer.md agent from WasteHero/claude-development-environment
- Modify the agent prompt to specialize for your codebase
- Update workflow to use your fork: `repository: YOUR_ORG/claude-development-environment`
- Test locally with Claude Code before using

**Agent Tuning:**
- Review py-reviewer.md structure and prompting
- Adjust JSON schema output if needed
- Test with sample PRs to validate improvements

### 5. Slow Review Comments

**Problem:**
```
Claude takes 2-3 minutes to post a comment
Agent processing is slow
```

**Cause:** Network latency, API rate limiting, large code changes, or agent processing

**Fix:**
- Normal time is 30-90 seconds (Step 2 checkout + Step 4 agent run)
- If consistently slow:
  - Check if you're hitting API rate limits
  - Verify agent checkout (Step 2) completes quickly
  - Split large PRs into smaller ones
  - Check network connectivity from runner

- If single PR is slow:
  - One-time latency or API load
  - Subsequent reviews should be faster

**Optimization:**
- Ensure `.claude/agents/` checkout is cached between runs
- Consider PR size reduction to speed agent analysis
- Monitor Step 2 checkout time vs Step 4 agent execution time

### 6. API Rate Limiting

**Problem:**
```
429 Too Many Requests error
```

**Cause:** Anthropic API rate limit exceeded

**Fix:**
1. Wait before rerunning the workflow
2. Check your API usage at https://console.anthropic.com
3. Consider upgrading your API plan
4. Reduce concurrent PRs being reviewed

**Prevention:**
- Space out PR reviews if possible
- Use smaller PRs to reduce processing time
- Monitor API usage regularly

### 7. Workflow Appears But Doesn't Complete

**Problem:**
```
Workflow shows as "running" but never finishes
```

**Cause:** Timeout, API hang, or runner issue

**Fix:**
1. Wait up to 5 minutes (the timeout)
2. If still running after 5 minutes, GitHub will kill it
3. The PR is NOT blocked by workflow failure
4. Push a new commit to trigger another review attempt

### 8. Cost Considerations

**Problem:**
```
Worried about API costs from running reviews on every PR
```

**Solution:**
- Claude Haiku 4.5 is extremely cost-efficient
- Typical PR review: ~$0.01-0.05
- Costs less than blocking gates (which are longer)
- Runs only on actual code changes (filtered by PR event)

**Estimate:** For 20 PRs/day:
- ~20 reviews × $0.03 average = ~$0.60/day
- ~$18/month
- Less than blocking gates due to shorter context

### 9. Review Not Appearing on Specific Files

**Problem:**
```
Claude comments on some files but not all changed files
```

**Cause:** File size or number limits, PR scope

**Fix:**
- Review comment summarizes key findings
- Not every file is individually commented on (GitHub limit)
- File-specific comments appear in the main review comment
- If you need line-by-line feedback, use blocking gates

### 10. Comment Formatting Issues

**Problem:**
```
PR comment formatting is broken or incomplete
Agent JSON output visible in comment
```

**Cause:** github-script JSON parsing or formatting issue

**Fix:**
1. Verify github-script step processes JSON correctly
2. Check github-script body template for formatting errors
3. Ensure JSON parsing filters properly
4. Review logs for JSON structure issues

**Debug:**
```javascript
// Verify JSON is valid before posting
const result = JSON.parse(agentOutput);
console.log("Parsed categories:", result.categories);
console.log("Parsed recommendations:", result.recommendations);
```

### 11. Comparing to Blocking Quality Gates

**Problem:**
```
Unclear if I should use this workflow or the blocking gates
Confused about agent-based vs blocking implementations
```

**Key Differences:**

| Aspect | Claude Review (Agent) | Quality Gate | Review Gate |
|--------|----------------------|--------------|-------------|
| Implementation | @agent-py-reviewer | Direct prompt | Direct prompt |
| Output | JSON schema (parsed) | Direct feedback | Direct feedback |
| Blocking | No (informational) | Yes (blocks merge) | Yes (blocks merge) |
| Always Runs | Yes | Only on failure | Only on failure |
| Comments Always | Yes | Only if errors | Only if errors |
| Cost | Lowest (~$0.03) | Higher | Higher |
| Focus | Learning, improvement | Bug detection | Comprehensive review |
| Use Case | Feedback for all PRs | Enforce standards | Catch complex issues |
| Agent Loading | From WasteHero/claude-dev-env | None (direct) | None (direct) |

**Agent-Based Advantages:**
- Structured output ensures reliable parsing
- Reusable agent across multiple workflows
- Consistent prompt behavior
- Easier to maintain and test

**Recommendation:**
- Use Claude Review (agent-based) for continuous feedback
- Use Blocking Gates for mandatory quality standards
- Both now support agent patterns in respective workflows
- Combine all three for comprehensive coverage

### 12. Disabling the Workflow

**Problem:**
```
I want to turn off Claude reviews for now
```

**Fix: Temporarily Disable**
1. Go to Actions tab
2. Find "Claude PR Review" workflow
3. Click the three dots menu
4. Select "Disable workflow"

**Fix: Permanently Remove**
1. Delete the workflow reference from your `.github/workflows/` file
2. Or comment out the job:
   ```yaml
   # claude-review:
   #   uses: WasteHero/wastehero-github-actions/.github/workflows/ai/claude-pr-review.yml@main
   ```

### 13. Draft PR Behavior Clarification

**Problem:**
```
I marked PR as draft but it still got reviewed
```

**Explanation:**
- When you push to a draft PR, it stays draft
- When you mark as "Ready for review", the next event triggers
- The workflow only runs on new events (opened, synchronized, ready_for_review)
- Existing draft PR reviews are NOT deleted

**Fix:**
- If you don't want the review, you can:
  - Edit the PR comment and explain it was draft
  - Delete the comment if it's not helpful
  - Or just ignore it until the PR is actually ready

## How It Compares to Blocking Gates

### Key Architectural Difference

Claude PR Review uses the **@agent-py-reviewer pattern** from WasteHero/claude-development-environment, while blocking gates use direct prompts. This agent-based approach provides:

- Consistent, structured output (JSON schema)
- Reliable parsing and validation
- Reusable agent definition
- Easier maintenance and testing
- Informational-only execution (never blocks)

### Comparison Table

| Feature | Claude PR Review (This Workflow) | Python Quality Gate (CT-1179) | Python Review Gate (CT-1183) |
|---------|----------------------------------|-------------------------------|------------------------------|
| **Architecture** | @agent-py-reviewer pattern | Direct prompt | Direct prompt |
| **Agent Loading** | From WasteHero/claude-dev-env | Not used | Not used |
| **Output Format** | JSON schema (structured) | Free-form text | Free-form text |
| **Parsing** | github-script (reliable) | Comment parsing | Comment parsing |
| **Blocking** | No (informational) | Yes (blocks merge) | Yes (blocks merge) |
| **Always Runs** | Yes | Only on failure | Only on failure |
| **Always Comments** | Yes (feedback always posted) | Only if errors | Only if errors |
| **Cost per Review** | ~$0.01-0.05 | ~$0.05-0.10 | ~$0.10-0.20 |
| **Speed** | 30-90 seconds | 60-120 seconds | 90-180 seconds |
| **Focus** | Learning & improvement | Bug detection | Comprehensive analysis |
| **Review Type** | Continuous feedback | Mandatory quality | Deep analysis |
| **Use Case** | All PRs (advisory) | Enforce standards | Catch complex issues |

### When to Use Each

**Claude PR Review (This Workflow)**
- Want continuous learning and improvement
- Prefer non-blocking suggestions
- Have junior developers who benefit from guidance
- Want feedback on every PR (not just failures)
- Cost is important
- Want structured, parseable output

**Python Quality Gate (CT-1179)**
- Need to enforce code standards
- Want to block specific types of bugs
- Have strict quality requirements
- Need specific error detection
- Can tolerate higher cost
- Want blocking enforcement

**Python Review Gate (CT-1183)**
- Need comprehensive code analysis
- Want to catch complex issues
- Have senior engineers reviewing
- Need detailed performance/security analysis
- Can tolerate highest cost
- Want blocking enforcement

### Pipeline Example with Both

```yaml
name: Comprehensive PR Analysis

on:
  pull_request:
    branches: [main]

jobs:
  # Informational feedback (agent-based, never blocks)
  claude-review:
    uses: WasteHero/wastehero-github-actions/.github/workflows/ai/claude-pr-review.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  # Blocking quality enforcement
  quality-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-quality-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  # Blocking comprehensive review
  review-gate:
    uses: WasteHero/wastehero-github-actions/.github/workflows/core/python-review-gate.yml@main
    with:
      project: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  # These run after gates pass
  tests:
    needs: [quality-gate, review-gate]
    runs-on: [self-hosted, linux, X64, kubernetes]
    steps:
      - uses: actions/checkout@v4
      - run: pytest
```

**Workflow Sequence:**
1. Claude Review runs (agent-based, always posts feedback)
2. Developer sees suggestions (non-blocking)
3. Quality Gate runs (blocking, standard enforcement)
4. If Quality Gate passes, Review Gate runs (blocking, deep analysis)
5. If both gates pass, Tests run
6. Ready to merge

## Integration with Quality Gates

### The Three-Layer Approach

WasteHero recommends a three-layer AI review system:

1. **Claude PR Review (CT-1187)** - This workflow (agent-based)
   - Always runs, never blocks
   - Provides learning-focused feedback
   - Uses @agent-py-reviewer from external repository
   - Structured JSON output
   - Lowest cost

2. **Python Quality Gate (CT-1179)** - Blocking gate (direct prompt)
   - Runs on every PR
   - Blocks merge if issues found
   - Catches specific bugs and anti-patterns
   - Medium cost

3. **Python Review Gate (CT-1183)** - Comprehensive review (direct prompt)
   - Runs on every PR
   - Blocks merge if issues found
   - Deep code analysis (performance, security, testing)
   - Highest cost

### How They Work Together

```
PR Created
    |
    v
Claude Review (agent-based, informational, always posts)
    |
    +-- If issues: Developer sees feedback comment (JSON-parsed)
    +-- If excellent: Developer sees praise
    |
    v (can merge or push changes)
Quality Gate (direct prompt, blocking, checks specific issues)
    |
    +-- If fails: Cannot merge, see what to fix
    |
    v (if passed or auto-fixed)
Review Gate (direct prompt, blocking, comprehensive analysis)
    |
    +-- If fails: Cannot merge, deep analysis provided
    |
    v (if passed)
Tests (can run in parallel)
    |
    v (if all pass)
Ready to Merge
```

### Choosing Your Configuration

**For Learning-Focused Teams:**
```yaml
# Just Claude Review (agent-based) - feedback without blocking
claude-review:
  uses: ...claude-pr-review.yml@main
```

**For Traditional Quality Control:**
```yaml
# Blocking gates only (direct prompts) - strict enforcement
quality-gate:
  uses: ...python-quality-gate.yml@main
review-gate:
  uses: ...python-review-gate.yml@main
```

**For Comprehensive Coverage (Recommended):**
```yaml
# All three - agent-based feedback + direct-prompt blocking gates
claude-review:
  uses: ...claude-pr-review.yml@main

quality-gate:
  uses: ...python-quality-gate.yml@main

review-gate:
  uses: ...python-review-gate.yml@main
```

### Reference Links

- **Python Quality Gate**: See [python-quality-gate-workflow.md](./reference/python-quality-gate-workflow.md) (CT-1179)
- **Python Review Gate**: See [python-review-gate-workflow.md](./reference/python-review-gate-workflow.md) (CT-1183)
- **AI Workflows Overview**: See [ai-quality-gates.md](./ai-quality-gates.md)
- **Claude Development Environment**: https://github.com/WasteHero/claude-development-environment
- **Parent Task**: CT-1168 (Foundation Workflows)

## Performance

### Typical Execution Times

Based on self-hosted Kubernetes runners:

| PR Size | Time | Notes |
|---------|------|-------|
| Small (1-5 files) | 30-45s | Quick analysis |
| Medium (5-20 files) | 45-90s | Standard analysis |
| Large (20+ files) | 60-120s | More context to analyze |
| Very Large (100+ files) | 90-180s | May hit timeout at 300s |

### What Affects Speed

**Faster:**
- Smaller code changes
- Cached API responses
- Off-peak hours
- Smaller files

**Slower:**
- Large files
- Many files changed
- Complex code patterns
- Peak API usage times

### Timeout Configuration

- **Maximum:** 5 minutes (300 seconds)
- **Typical:** 30-90 seconds
- **Very large PRs:** May approach 5-minute limit

If your PR consistently hits the timeout:
- Break it into smaller PRs
- Simplify code structure
- Consider splitting functionality

### Cost Per Review

Using Claude Haiku 4.5:
- **Input tokens:** ~1000-3000 (code context)
- **Output tokens:** ~500-1000 (feedback)
- **Cost per review:** ~$0.01-0.05 USD

This is significantly cheaper than blocking gates due to:
- Shorter model conversations
- Optimized prompting
- Smaller output format

## Best Practices

### Agent Usage

1. **Agents are loaded from external repository**
   - py-reviewer.md comes from WasteHero/claude-development-environment
   - Checkout happens automatically in Step 2
   - Ensure external repository is accessible
   - Cache the agent directory between runs for efficiency

2. **Structured output ensures reliable parsing**
   - Agent returns JSON schema format
   - github-script parses structured output
   - Validates JSON structure before posting
   - Handles parsing errors gracefully

3. **Compare to blocking gates (CT-1179, CT-1183)**
   - This workflow is informational (never blocks)
   - Blocking gates use direct prompts (not agents)
   - Informational feedback is learning-focused
   - Blocking gates enforce standards
   - Use both for comprehensive coverage

### When to Use This Workflow

Use Claude PR Review when:
- You want continuous learning and improvement
- You have junior developers who benefit from guidance
- You want feedback on all PRs (not just failures)
- You prefer non-blocking suggestions over strict enforcement
- Cost is a consideration
- You want AI to complement human reviews
- You prefer structured, parseable output (JSON schema)

### When NOT to Use This Workflow

Skip this workflow when:
- You only want blocking quality gates
- You have strict enforcement needs
- Cost must be minimized to absolute zero
- You need very detailed, complex analysis
- Informational feedback will be ignored

### Combining with Human Reviews

Best practice: Use Claude + human code review

```yaml
# PR comes in
# Claude provides automated feedback immediately (agent-based)
# Humans add specialized feedback
# Discussion happens in PR comments
# All feedback informs final decision
```

### Optimizing Review Quality

1. **Review the feedback** - Don't ignore Claude's comments
2. **Iterate** - Use suggestions to improve code
3. **Learn patterns** - Understand recurring feedback topics
4. **Customize if needed** - Fork agent and update workflow reference
5. **Provide context** - Clear PR descriptions help Claude understand intent
6. **Monitor agent performance** - Track output structure and quality over time

### Configuration Best Practices

1. **Always set project and pr-number inputs**
   ```yaml
   with:
     project: ${{ github.repository }}
     pr-number: ${{ github.event.pull_request.number }}
   ```

2. **Protect your API key**
   - Use repository secrets, never hardcode
   - Use organization secrets for sharing
   - Rotate keys periodically

3. **Test workflow locally**
   ```bash
   act -j claude-review -s ANTHROPIC_API_KEY=sk-ant-...
   ```

4. **Monitor workflow runs**
   - Check Actions tab regularly
   - Review error logs if comments don't appear
   - Track API usage at console.anthropic.com
   - Monitor agent checkout and JSON parsing steps

5. **Verify agent accessibility**
   - Ensure WasteHero/claude-development-environment is accessible
   - Test agent checkout in workflow logs
   - Validate .claude/agents/py-reviewer.md exists

6. **Documentation**
   - Document in your CONTRIBUTING.md
   - Explain to new developers how to use feedback
   - Link to this reference documentation
   - Mention agent-based architecture

## Related Documentation

- **[AI-Powered Quality Gates Overview](../ai-quality-gates.md)** - Complete AI workflows guide
- **[Python Quality Gate Reference](python-quality-gate-workflow.md)** - CT-1179 (blocking quality analysis)
- **[Python Review Gate Reference](python-review-gate-workflow.md)** - CT-1183 (blocking comprehensive review)
- **[Python Lint Workflow](python-lint-workflow.md)** - CT-1180 (traditional linting)
- **[Debugging Workflow Failures](../how-to-guides/debugging-workflow-failures.md)** - How to debug issues
- **[How to Configure Secrets](../tutorials/configuring-repository-secrets.md)** - Secret setup guide
- **[Anthropic API Documentation](https://docs.anthropic.com)** - Claude API reference
- **[Claude Code Action](https://github.com/anthropics/claude-code-action)** - Action documentation
- **[GitHub Actions Documentation](https://docs.github.com/en/actions)** - GitHub Actions reference

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 8, 2025 | Initial release - Informational PR review workflow |

## Changelog

### v1.0 (December 8, 2025)

**Initial Release**
- Implemented Claude Haiku 4.5-based PR review workflow
- Informational (non-blocking) feedback on code changes
- Always posts PR comments with constructive suggestions
- Skips draft PRs automatically
- Integrates with blocking quality gates
- Comprehensive documentation with 12+ troubleshooting scenarios
- Cost-optimized using Claude Haiku model

---

**Questions?** See [How-To Guides](../how-to-guides/README.md) for common problems or review [AI-Powered Quality Gates](../ai-quality-gates.md) for workflow comparison.

**Want to understand AI workflows?** Check [Explanation](../explanation/README.md) for conceptual background.

**Getting started?** Check [Tutorials](../tutorials/README.md) for step-by-step guides.
