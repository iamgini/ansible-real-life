---
name: get-pr-zuul-results
description: >
  Fetches Zuul CI build status and log URLs for ansible-collections pull
  requests. Use this skill when you need to check Zuul results, summarize
  failing builds, or retrieve log links for a PR.
user-invocable: false
---

# Skill: get-pr-zuul-results

## Purpose

Get the results of Zuul CI builds for a pull request in ansible-collections repositories.
Provides build status, log URLs, and actionable insights for failed jobs.

This is typically a helper skill invoked by workflows that need to check Zuul CI status.

## When to Invoke

TRIGGER when:

- Need to check Zuul CI status for ansible-collections PRs
- Another skill needs Zuul build results within a workflow
- Programmatically checking CI status for ansible-collections repositories

DO NOT TRIGGER when:

- Checking GitHub Actions/GitLab CI (use `get-pr-action-results` instead)
- User wants to run tests locally (use `run-tests` skill)
- Repository doesn't use Zuul CI

## Inputs

- `pr_number` (optional): PR number to check. If not provided, will detect from current branch.
- `project` (optional): Project name. Default: `ansible-collections/amazon.aws`

## Prerequisites

- `curl` for API requests
- `get-pr-number` skill available for finding PR from branch
- `get-upstream-info` skill available for detecting project name

## Workflow

### Step 1 — Determine what to check

If `pr_number` is provided, use it directly.

Otherwise, use the `get-pr-number` skill to find the PR for the current branch.

If no PR exists yet, report error.

### Step 2 — Determine project name

If `project` is provided, use it directly.

Otherwise, use the `get-upstream-info` skill to determine the upstream repository.

Default to `ansible-collections/amazon.aws` if not detected.

### Step 3 — Query Zuul API for buildsets

Fetch recent buildsets for the PR:

```bash
curl -s "https://gateway-cloud-softwarefactory.apps.ocp.cloud.ci.centos.org/zuul/api/tenant/ansible/buildsets?project=<project>&change=<pr_number>&limit=5"
```

This returns up to 5 recent buildsets for the PR.

### Step 4 — Display buildset summary

For each buildset (most recent first), show:

- UUID
- Result (SUCCESS/FAILURE/DEQUEUED/RETRY)
- Patchset (commit hash)
- First build start time
- Last build end time

Example:

```
Recent buildsets for PR #2974:
1. abc123... - SUCCESS - Commit: def456 - Ended: 2026-05-18 10:30:00
2. ghi789... - FAILURE - Commit: jkl012 - Ended: 2026-05-18 09:15:00
3. mno345... - DEQUEUED - Commit: pqr678 - Ended: 2026-05-18 08:45:00
```

### Step 5 — Get detailed build information

For the most recent buildset, fetch detailed build results:

```bash
curl -s "https://gateway-cloud-softwarefactory.apps.ocp.cloud.ci.centos.org/zuul/api/tenant/ansible/buildset/<uuid>"
```

This returns all builds (jobs) within the buildset.

### Step 6 — Analyze build results

For each build in the buildset, extract:

- Job name
- Result (SUCCESS/FAILURE/SKIPPED/RETRY)
- Duration (seconds)
- Log URL (if available)
- job-output.txt URL (construct as: `<log_url>/job-output.txt`)

Categorize builds:

- **Failed builds**: result = FAILURE
- **Successful builds**: result = SUCCESS
- **Skipped builds**: result = SKIPPED
- **Retrying builds**: result = RETRY

### Step 7 — Summarize results

Present a clear summary:

```
Zuul CI Status for PR #<number> (<project>)
────────────────────────────────────────────

Latest Buildset: <uuid>
Result: <result>
Commit: <patchset>
Started: <start_time>
Ended: <end_time>

Builds:
✓ ansible-test-sanity-2.14 - SUCCESS (245s)
✓ ansible-test-units-2.15 - SUCCESS (180s)
✗ ansible-test-integration-2.16 - FAILURE (420s)
  Log: https://logs.example.com/abc123/ansible-test-integration-2.16/
  Output: https://logs.example.com/abc123/ansible-test-integration-2.16/job-output.txt
⊘ ansible-test-sanity-devel - SKIPPED

Summary:
- Failed: 1
- Successful: 2
- Skipped: 1
```

### Step 8 — Provide structured output

Return data that can be used by calling workflows:

```
Failed Jobs:
- ansible-test-integration-2.16

Failed Job Logs:
- https://logs.example.com/abc123/ansible-test-integration-2.16/job-output.txt

Overall Result: FAILURE
```

## Important Notes

### Zuul API Specifics

- **Tenant**: The Zuul tenant for Ansible collections is `ansible` (not `local`)
- **Base URL**: `https://gateway-cloud-softwarefactory.apps.ocp.cloud.ci.centos.org/zuul/api/tenant/ansible/`
- **Buildsets**: A buildset contains multiple builds (job executions) for a single commit
- **Log URLs**: Job output is always at `<log_url>/job-output.txt` when log_url is present

### Build Results

- **SUCCESS**: Build passed all tests
- **FAILURE**: Build failed (examine logs)
- **SKIPPED**: Build was skipped (dependencies failed or job not applicable)
- **RETRY**: Job will be retried automatically
- **DEQUEUED**: Build was superseded by a newer commit (ignore this buildset)

### Log Availability

- Log URLs may be null for SKIPPED, RETRY, or DEQUEUED builds
- Focus on FAILURE builds for troubleshooting
- job-output.txt contains the full console output

## Integration with Other Skills

- **get-pr-number**: Used to find PR number from current branch
- **get-upstream-info**: Used to determine project name
- **check-pr-actions**: May invoke this skill for Zuul-based repositories

## Example Output

### Example 1: All builds passing

```
User: "Check Zuul status for PR #2974"

Step 1: Use provided PR number - 2974
Step 2: Detect project - ansible-collections/amazon.aws
Step 3: Query buildsets - Found 3 buildsets
Step 4: Display summary - Latest is SUCCESS
Step 5: Get detailed results

Zuul CI Status for PR #2974 (ansible-collections/amazon.aws)
──────────────────────────────────────────────────────────────

Latest Buildset: abc123def456
Result: SUCCESS
Commit: 7cc81ba
Started: 2026-05-18 09:00:00 UTC
Ended: 2026-05-18 09:25:00 UTC

Builds:
✓ ansible-test-sanity-2.14 - SUCCESS (245s)
✓ ansible-test-sanity-2.15 - SUCCESS (238s)
✓ ansible-test-units-2.14 - SUCCESS (180s)
✓ ansible-test-units-2.15 - SUCCESS (175s)

Summary:
- Failed: 0
- Successful: 4
- Skipped: 0

All Zuul builds passed! ✓
```

### Example 2: Build failures

```
User: "Check Zuul CI for current branch"

Step 1: Detect PR from branch - Found PR #2975
Step 2: Detect project - ansible-collections/community.aws
Step 3: Query buildsets
Step 4: Latest buildset is FAILURE

Zuul CI Status for PR #2975 (ansible-collections/community.aws)
──────────────────────────────────────────────────────────────

Latest Buildset: ghi789jkl012
Result: FAILURE
Commit: mno3456
Started: 2026-05-18 10:00:00 UTC
Ended: 2026-05-18 10:30:00 UTC

Builds:
✓ ansible-test-sanity-2.14 - SUCCESS (240s)
✗ ansible-test-sanity-2.15 - FAILURE (125s)
  Log: https://logs.opendev.org/12/34567/8/check/ansible-test-sanity-2.15/abc123/
  Output: https://logs.opendev.org/12/34567/8/check/ansible-test-sanity-2.15/abc123/job-output.txt
✗ ansible-test-units-2.15 - FAILURE (95s)
  Log: https://logs.opendev.org/12/34567/8/check/ansible-test-units-2.15/def456/
  Output: https://logs.opendev.org/12/34567/8/check/ansible-test-units-2.15/def456/job-output.txt
⊘ ansible-test-integration-2.15 - SKIPPED

Summary:
- Failed: 2
- Successful: 1
- Skipped: 1

Failed Jobs:
- ansible-test-sanity-2.15
- ansible-test-units-2.15

Failed Job Logs:
- https://logs.opendev.org/12/34567/8/check/ansible-test-sanity-2.15/abc123/job-output.txt
- https://logs.opendev.org/12/34567/8/check/ansible-test-units-2.15/def456/job-output.txt

Overall Result: FAILURE
```

### Example 3: Dequeued buildsets

```
User: "Check Zuul for PR #2976"

Step 1: Use PR number - 2976
Step 2: Detect project
Step 3: Query buildsets - Found 5

Recent buildsets for PR #2976:
1. pqr789stu012 - SUCCESS - Commit: vwx3456 - Ended: 2026-05-18 11:00:00
2. yza123bcd456 - DEQUEUED - Commit: efg7890 - Ended: 2026-05-18 10:50:00
3. hij234klm567 - DEQUEUED - Commit: nop8901 - Ended: 2026-05-18 10:45:00

Latest non-dequeued buildset: pqr789stu012

Zuul CI Status for PR #2976 (ansible-collections/amazon.aws)
──────────────────────────────────────────────────────────────

Latest Buildset: pqr789stu012
Result: SUCCESS
Commit: vwx3456
Started: 2026-05-18 10:45:00 UTC
Ended: 2026-05-18 11:00:00 UTC

Builds:
✓ ansible-test-sanity-2.14 - SUCCESS (250s)
✓ ansible-test-units-2.14 - SUCCESS (185s)

Summary:
- Failed: 0
- Successful: 2
- Skipped: 0

Note: 2 buildsets were dequeued (superseded by newer commits)
All Zuul builds passed! ✓
```
