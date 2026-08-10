---
name: get-pr-action-results
description: >
  Fetches GitHub Actions or GitLab CI results for a pull request or branch and
  analyzes failures. Use this skill when you need to diagnose CI failures,
  examine logs, and get suggested fixes.
user-invocable: false
---

# Skill: get-pr-action-results

## Purpose

Get the results of GitHub Actions/GitLab CI for a pull request or branch and analyze any failures.
Provides actionable insights by examining logs, identifying patterns across matrix tests, and suggesting specific fixes.

This is typically a helper skill invoked by the `check-pr-actions` command or other workflows.

## When to Invoke

TRIGGER when:

- Invoked by check-pr-actions command
- Need to programmatically check CI status within a workflow
- Another skill needs to verify CI results before proceeding

DO NOT TRIGGER when:

- User wants to run tests locally (use `run-tests` skill)
- User wants to create a PR (use `create-pr` skill)
- Just asking about CI configuration (not checking status)
- User directly asks to check PR (use check-pr-actions command instead)

## Inputs

- `pr_number` (optional): PR number to check. If not provided, will detect from current branch.
- `branch` (optional): Branch name to check if no PR exists yet.

## Prerequisites

- `gh` CLI installed and authenticated
- `get-upstream-info` skill available for detecting upstream repository
- `get-pr-number` skill available for finding PR from branch

## Workflow

### Step 1 — Determine what to check

If `pr_number` is provided, use it directly.

Otherwise, use the `get-pr-number` skill to find the PR for the current branch.

If no PR exists yet, check for workflow runs on the current branch directly.

### Step 2 — Get upstream repository info

Use the `get-upstream-info` skill to determine:

- Upstream repository (owner/repo)
- Service type (GitHub or GitLab)

This ensures we check the right repository (not the fork).

### Step 3 — List recent workflow runs

**For GitHub:**

```bash
gh run list --repo <upstream-repo> --branch <branch-name> --limit 10
```

Or if checking a specific PR:

```bash
gh run list --repo <upstream-repo> --json conclusion,status,workflowName,createdAt,databaseId --jq '.[] | select(.conclusion != "success")'
```

**For GitLab:**

```bash
gh api /projects/<project-id>/pipelines --method GET
```

(GitLab support via gh extension or API calls)

### Step 4 — Identify failures

Filter the runs to find:

- Failed runs (conclusion: failure)
- In-progress runs (status: in_progress)
- Cancelled runs (conclusion: cancelled)

Display a summary:

```
Recent workflow runs for <branch>:
✗ Build and test - Failed (2 hours ago)
✗ Integration tests - Failed (2 hours ago)
⊙ Lint - In progress (30 minutes ago)
✓ Documentation - Passed (3 hours ago)
```

### Step 5 — Analyze failures (matrix tests)

For failed workflow runs, focus on matrix test jobs:

**Strategy for matrix tests:**

When tests fail across multiple Python/Ansible combinations:

1. Identify the **oldest** combination that failed (e.g., Python 3.9, Ansible 2.14)
2. Identify the **newest** combination that failed (e.g., Python 3.12, Ansible 2.17)
3. Fetch and analyze logs from both to understand if it's:
   - Version-specific issue (only old or only new combinations fail)
   - Universal issue (all combinations fail with same error)
   - Different issues (different errors in different combinations)

**Get job logs:**

```bash
gh run view <run-id> --repo <upstream-repo> --log-failed
```

Or for specific jobs:

```bash
gh run view <run-id> --repo <upstream-repo> --job <job-id> --log
```

### Step 6 — Summarize failures

Present a clear summary:

```
Failure Analysis for PR #123
────────────────────────────────

Workflow: Build and test
Status: Failed

Failed Jobs (Matrix):
- sanity-3.9-2.14: FAILED
- sanity-3.12-2.17: FAILED
- unit-3.10-2.15: PASSED
- unit-3.11-2.16: PASSED

Error Pattern:
Both oldest (3.9/2.14) and newest (3.12/2.17) sanity tests fail with:

  ERROR: plugins/modules/ec2_instance.py:123:5: yamllint: line too long (85 > 80 characters)
  ERROR: plugins/modules/ec2_instance.py:456:1: ansible-test-pep8: E501 line too long

Affected Files:
- plugins/modules/ec2_instance.py:123
- plugins/modules/ec2_instance.py:456
```

### Step 7 — Suggest fixes

Based on error patterns, suggest specific fixes:

**For linting/formatting errors:**

```
Suggested Fix:

This is a straightforward formatting issue. The lines exceed the maximum length.

Fix:
1. Shorten line 123 in ec2_instance.py (currently 85 chars, limit 80)
2. Shorten line 456 in ec2_instance.py

Would you like me to fix these formatting issues?
```

**For test failures:**

```
Suggested Fix:

The test is failing because the mock expects 'instance_id' but receives 'InstanceId'.

Fix:
1. Update tests/unit/plugins/modules/test_ec2_instance.py:234
2. Change mock expectation from 'instance_id' to 'InstanceId'

This appears to be a test-only change, not a code change.
```

**For version-specific issues:**

```
Suggested Fix:

This failure only occurs on Python 3.12 + Ansible 2.17, suggesting a compatibility issue.

Investigation needed:
1. Check if using deprecated syntax removed in Ansible 2.17
2. Verify Python 3.12 compatibility for any syntax changes
3. Review recent Ansible 2.17 porting guide

The error suggests the issue is in plugins/module_utils/ec2.py:89
```

### Step 8 — Offer to apply fixes (optional)

If the fix is straightforward:

- Formatting/linting issues
- Simple syntax fixes
- Clear test updates

Use `AskUserQuestion` to ask:

```
Would you like me to apply this fix?
```

If yes, apply the fix using Edit tool, then suggest re-running prepush checks.

## Important Notes

### Matrix Test Strategy

When analyzing matrix tests:

- **Don't check every combination** - only oldest and newest failures
- Skip passed tests entirely
- Focus on actionable errors, not warnings
- Look for patterns: do all fail the same way, or different ways?

### Upstream vs Fork

- Always check the **upstream repository** (where PR is opened), not the fork
- PRs are on the upstream (e.g., ansible-collections/amazon.aws)
- Use `get-upstream-info` skill to determine the correct repository

### Log Analysis

- Focus on the **last 50 lines** of failed job logs (where errors appear)
- Extract file paths and line numbers when available
- Identify error codes (E501, yamllint, ansible-test codes)
- Look for stack traces in test failures

### Service-Specific Commands

**GitHub:**

- `gh run list` - List workflow runs
- `gh run view <id>` - View run details
- `gh run view <id> --log-failed` - Get logs for failed jobs

**GitLab:**

- Use `gh api` with GitLab API endpoints
- Or use `glab` CLI if available

## Integration with Other Skills

- **get-pr-number**: Used to find PR number from current branch
- **get-upstream-info**: Used to determine upstream repository
- **run-tests**: Used if suggesting to run tests locally before pushing
- **create-pr**: User may run this skill after creating a PR

## Example Output

### Example 1: Successful status check

```
User: "Check the PR status"

Step 1: Detect PR number - Found PR #456
Step 2: Get upstream - ansible-collections/amazon.aws
Step 3: List runs - 4 recent runs found
Step 4: Identify failures - All passed

PR #456 Status: ✓ All checks passing

Recent runs:
✓ Build and test - Passed (1 hour ago)
✓ Integration tests - Passed (1 hour ago)
✓ Lint - Passed (1 hour ago)

Your PR is ready for review.
```

### Example 2: Formatting failures

```
User: "Why is my PR failing?"

Step 1: Detect PR number - Found PR #457
Step 2: Get upstream - ansible-collections/amazon.aws
Step 3: List runs - Found failed run
Step 4: Identify failures - Sanity tests failing
Step 5: Analyze logs - Checked Python 3.9 and 3.12 runs

Failure Analysis for PR #457
────────────────────────────────

Workflow: Build and test
Status: Failed (all Python versions)

Failed Jobs:
- sanity-3.9-2.14: FAILED (formatting)
- sanity-3.12-2.17: FAILED (formatting)

Error Pattern:
All sanity tests fail with the same formatting errors:

  plugins/modules/s3_bucket.py:234:1: E501 line too long (96 > 80)
  plugins/modules/s3_bucket.py:456:5: E128 continuation line under-indented

Suggested Fix:
These are straightforward formatting issues.

Would you like me to fix these formatting errors?
> Yes

Applying fixes...
- Fixed line 234: Split long line
- Fixed line 456: Corrected indentation

Changes applied. Run the `run-tests` skill to verify locally,
then push to update the PR.
```

### Example 3: Version-specific failure

```
User: "Check actions"

Step 1: No PR yet, check branch
Step 2: Get upstream - ansible-collections/community.general
Step 3: List runs for branch
Step 4: Found failures
Step 5: Analyze - Python 3.12 only

Failure Analysis for branch feature/new-module
───────────────────────────────────────────────

Workflow: Tests
Status: Failed (Python 3.12 only)

Failed Jobs:
- unit-3.12-2.17: FAILED
- unit-3.9-2.14: PASSED
- unit-3.10-2.15: PASSED
- unit-3.11-2.16: PASSED

Error (Python 3.12 only):
  tests/unit/plugins/modules/test_new_module.py:45
  AttributeError: 'dict' object has no attribute 'has_key'

Root Cause:
The code uses dict.has_key() which was removed in Python 3.9+.
This should have failed on all versions, but only fails on 3.12
due to test environment differences.

Suggested Fix:
Replace dict.has_key(key) with key in dict

File: tests/unit/plugins/modules/test_new_module.py:45
Change: if params.has_key('name'):
To:     if 'name' in params:

Would you like me to apply this fix?
```
