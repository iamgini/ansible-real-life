---
name: get-pr-number
description: >
  Determines the pull request number, status, and URL for a branch using the gh
  CLI. Use this skill when you need PR context for CI checks, SonarCloud
  analysis, or other workflows tied to an open pull request.
user-invocable: false
---

# Get PR Number Skill

A helper skill that determines the pull request number for a Git branch using the GitHub CLI.

## Purpose

Find pull request information for a branch:

- PR number
- PR status (open, closed, merged)
- PR URL
- PR title

This skill is designed to be invoked by other skills that need PR context.

## When to Invoke

TRIGGER when:

- Another skill needs to find the PR for the current branch
- You need to check if a branch has an associated PR
- You need PR metadata (number, URL, status)

DO NOT TRIGGER when:

- The user explicitly provides a PR number
- Working with branches that shouldn't have PRs (main, master, devel, stable branches)

## Dependencies

This skill uses the `get-upstream-info` skill to determine the upstream repository for PR lookups.

**Note on caching:** See the caching guidance in `get-upstream-info` skill documentation. If your skill invokes both `get-upstream-info` and `get-pr-number`, cache the upstream info and reuse it.

## Workflow

### 1. Get Upstream Repository Information

Use the `get-upstream-info` skill to determine the upstream repository:

```
Invoke get-upstream-info skill to get:
- UPSTREAM_PATH (e.g., ansible-collections/amazon.aws)
- CURRENT_PATH (e.g., octocat/amazon.aws)
- IS_FORK (whether the current repo is a fork)
```

This ensures that when working in a fork, PRs are looked up in the upstream repository where they actually exist.

### 2. Determine the Branch

**If user provides a branch name:**

Use the provided branch name.

**If no branch specified:**

Get the current branch:

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
```

**Handle special cases:**

- If branch is `HEAD` (detached HEAD state): Report error
- If branch is `main`, `master`, `devel`, or matches `stable-*`: Warn that these typically don't have PRs

### 3. Query Pull Requests for the Branch

Use `gh` to find PRs for the branch in the upstream repository:

**When working in a fork:**

```bash
# Extract fork owner from CURRENT_PATH
FORK_OWNER=$(echo "$CURRENT_PATH" | cut -d/ -f1)

# Query with fork-qualified branch name
gh pr list --repo "$UPSTREAM_PATH" --head "$FORK_OWNER:$BRANCH" --json number,state,title,url
```

**When not a fork:**

```bash
gh pr list --repo "$UPSTREAM_PATH" --head "$BRANCH" --json number,state,title,url
```

**Output example (PR exists):**

```json
[
  {
    "number": 1234,
    "state": "OPEN",
    "title": "Add support for new parameter",
    "url": "https://github.com/ansible-collections/amazon.aws/pull/1234"
  }
]
```

**Output example (no PR):**

```json
[]
```

### 4. Process Results

**No PR found:**

```
No pull request found for branch: feature/add-caching

Suggestions:
- Create a PR: gh pr create --repo <UPSTREAM_PATH>
- Check if branch name is correct
- Verify branch is pushed to remote
```

**Single PR found (most common):**

Extract and return PR information:

```bash
PR_NUMBER=$(echo "$RESULT" | jq -r '.[0].number')
PR_STATE=$(echo "$RESULT" | jq -r '.[0].state')
PR_TITLE=$(echo "$RESULT" | jq -r '.[0].title')
PR_URL=$(echo "$RESULT" | jq -r '.[0].url')
```

**Multiple PRs found:**

Prefer OPEN PR if available, otherwise use the most recent:

```bash
# Try to find an OPEN PR first
PR_NUMBER=$(echo "$RESULT" | jq -r '.[] | select(.state == "OPEN") | .number' | head -1)

# If no OPEN PR, use the first (most recent) PR
if [ -z "$PR_NUMBER" ]; then
    PR_NUMBER=$(echo "$RESULT" | jq -r '.[0].number')
fi
```

Warn the user:

```
Warning: Multiple PRs found for branch feature/add-caching
Using PR #1234 (OPEN)
Other PRs: #999 (CLOSED)
```

### 5. Return Information

Present the PR information in a clear format:

```
Pull Request Information
========================
Branch: feature/add-caching
Upstream: ansible-collections/amazon.aws
PR Number: 1234
State: OPEN
Title: Add support for new parameter
URL: https://github.com/ansible-collections/amazon.aws/pull/1234
```

## Output Format

When invoked by other skills, provide the information in a structured format:

```
BRANCH=feature/add-caching
UPSTREAM_PATH=ansible-collections/amazon.aws
PR_NUMBER=1234
PR_STATE=OPEN
PR_TITLE=Add support for new parameter
PR_URL=https://github.com/ansible-collections/amazon.aws/pull/1234
PR_FOUND=true
```

When no PR is found:

```
BRANCH=feature/add-caching
UPSTREAM_PATH=ansible-collections/amazon.aws
PR_FOUND=false
```

## Error Handling

### gh CLI Not Available

```bash
if ! command -v gh &> /dev/null; then
    echo "Error: gh CLI is not installed or not in PATH"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi
```

### Not a Git Repository

```bash
if ! git rev-parse --git-dir &> /dev/null; then
    echo "Error: Current directory is not a Git repository"
    exit 1
fi
```

### Branch Not Pushed to Remote

```bash
if ! git rev-parse --verify "origin/$BRANCH" &> /dev/null 2>&1; then
    echo "Warning: Branch '$BRANCH' does not exist on remote 'origin'"
    echo "Push the branch first: git push -u origin $BRANCH"
fi
```

### Detached HEAD State

```bash
if [ "$BRANCH" = "HEAD" ]; then
    echo "Error: Currently in detached HEAD state"
    echo "Checkout a branch first: git checkout <branch-name>"
    exit 1
fi
```

### Protected/Main Branches

```bash
if [[ "$BRANCH" =~ ^(main|master|devel)$ ]] || [[ "$BRANCH" =~ ^stable- ]]; then
    echo "Warning: Branch '$BRANCH' is a protected branch that typically doesn't have PRs"
    echo "Did you mean to check a feature branch instead?"
fi
```

### Authentication Issues

```bash
if gh pr list 2>&1 | grep -q "authentication"; then
    echo "Error: gh CLI is not authenticated"
    echo "Run 'gh auth login' to authenticate with GitHub"
    exit 1
fi
```

### get-upstream-info Failure

```bash
if ! upstream_info=$(invoke get-upstream-info); then
    echo "Error: Failed to determine upstream repository"
    echo "Ensure you're in a GitHub repository"
    exit 1
fi
```

## Example Usage

### Example 1: Fork Workflow with Open PR

```
Current repo: octocat/amazon.aws (fork)
Upstream: ansible-collections/amazon.aws
Current branch: feature/add-caching

Steps:
1. get-upstream-info returns:
   UPSTREAM_PATH=ansible-collections/amazon.aws
   CURRENT_PATH=octocat/amazon.aws
   IS_FORK=true
2. gh pr list --repo ansible-collections/amazon.aws --head octocat:feature/add-caching

Result:
PR_NUMBER=1234
PR_STATE=OPEN
UPSTREAM_PATH=ansible-collections/amazon.aws
PR_FOUND=true
```

### Example 2: Direct Clone (Not a Fork)

```
Current repo: ansible-collections/amazon.aws (not a fork)
Current branch: feature/add-caching

Steps:
1. get-upstream-info returns:
   UPSTREAM_PATH=ansible-collections/amazon.aws
   IS_FORK=false
2. gh pr list --repo ansible-collections/amazon.aws --head feature/add-caching

Result:
PR_NUMBER=1234
PR_STATE=OPEN
UPSTREAM_PATH=ansible-collections/amazon.aws
PR_FOUND=true
```

### Example 3: Branch Without PR

```
Current branch: local-experiment

Result:
PR_FOUND=false
Suggestion: Create a PR with 'gh pr create --repo ansible-collections/amazon.aws'
```

### Example 4: Protected Branch (Warning)

```
Current branch: main
Warning: Branch 'main' is a protected branch that typically doesn't have PRs

Result:
PR_FOUND=false
```

## Integration with Other Skills

This skill is designed to be referenced by other skills:

**In sonarcloud-remediation skill:**

```
Use the `get-pr-number` skill to determine if the current work has an associated PR.
If PR_FOUND is true, use PR_NUMBER to fetch PR-specific SonarCloud issues.
```

**In pr-review skill:**

```
Use the `get-pr-number` skill to find the PR to review.
Use PR_NUMBER to fetch PR metadata, files changed, and comments.
```

**In changelog skill (update mode):**

```
Use the `get-pr-number` skill to determine which PR number to add to changelog fragments.
```

**In create-pr skill:**

```
Use the `get-pr-number` skill to check if a PR already exists for the current branch.
If PR_FOUND is true, warn the user before creating a duplicate.
```

## Important Notes

### Fork-Qualified Branch Names

When working in a fork, PRs in the upstream repository are identified by `owner:branch` format:

- Your fork: `octocat/amazon.aws` on branch `feature/add-caching`
- Upstream PR: `ansible-collections/amazon.aws` PR with head `octocat:feature/add-caching`

The skill handles this automatically by using `get-upstream-info` to detect fork status.

### Protected Branch Names

The following branches are considered protected and typically don't have PRs:

- `main` - Primary development branch (GitHub default)
- `master` - Primary development branch (Git default)
- `devel` - Development branch (common in Ansible projects)
- `stable-*` - Stable release branches (e.g., `stable-2`, `stable-3.1`)

### PR State Meanings

- **OPEN**: PR is active and can be reviewed/merged
- **CLOSED**: PR was closed without merging
- **MERGED**: PR was successfully merged (state becomes MERGED)

### Multiple PRs per Branch

Whilst rare, it's possible to have multiple PRs for the same branch:

- An old closed PR
- A new open PR after reopening work

The skill handles this by preferring OPEN PRs.

### Why Use --repo Parameter

Without `--repo`, `gh pr list` looks for PRs in the current repository:

- In a fork: Would find PRs targeting the fork (rarely what you want)
- In upstream: Would work, but inconsistent behaviour

Using `--repo` with upstream path ensures consistent PR lookups regardless of fork status.

### Performance

- Invokes `get-upstream-info`: 1 gh API call
- Runs `gh pr list`: 1 gh API call
- Total: 2 API calls per invocation

See caching guidance in `get-upstream-info` to optimize workflows that need both values.
