---
name: get-upstream-info
description: >
  Determines upstream repository information and service identifiers using the
  gh CLI. Use this skill when you need the canonical GitHub org, repo path, or
  derived keys such as SonarCloud project identifiers.
user-invocable: false
---

# Get Upstream Info Skill

A helper skill that determines upstream repository information using the GitHub CLI.

## Purpose

Extract and parse repository metadata to provide:

- GitHub organisation name
- Repository name
- Fully qualified repository path (e.g., `ansible-collections/amazon.aws`)
- Derived identifiers (e.g., SonarCloud project key)

This skill is designed to be invoked by other skills that need repository context.

## When to Invoke

TRIGGER when:

- Another skill needs to determine the upstream repository
- You need to derive service-specific identifiers (SonarCloud, etc.)
- You need to work with the canonical upstream (not fork)

DO NOT TRIGGER when:

- The user explicitly provides repository information
- Working with local-only repositories

## Workflow

### 1. Query Repository Information via gh CLI

Use `gh` to determine the current repository and its parent (if it's a fork):

```bash
gh repo view --json parent,nameWithOwner,name,owner
```

**Output example (fork):**

```json
{
  "name": "amazon.aws",
  "nameWithOwner": "octocat/amazon.aws",
  "owner": {
    "login": "octocat"
  },
  "parent": {
    "name": "amazon.aws",
    "owner": {
      "login": "ansible-collections"
    }
  }
}
```

**Output example (not a fork):**

```json
{
  "name": "ai-forge",
  "nameWithOwner": "ansible-community/ai-forge",
  "owner": {
    "login": "ansible-community"
  },
  "parent": null
}
```

### 2. Determine Upstream

**If `parent` exists (repository is a fork):**

- Upstream organisation: `parent.owner.login`
- Upstream repository: `parent.name`
- Upstream full path: `parent.owner.login/parent.name`

**If `parent` is null (not a fork):**

- Upstream organisation: `owner.login`
- Upstream repository: `name`
- Upstream full path: `nameWithOwner`

**Implementation:**

```bash
REPO_INFO=$(gh repo view --json parent,nameWithOwner,name,owner)

# Check if parent exists
if echo "$REPO_INFO" | jq -e '.parent != null' > /dev/null; then
    # Repository is a fork, use parent
    UPSTREAM_ORG=$(echo "$REPO_INFO" | jq -r '.parent.owner.login')
    UPSTREAM_REPO=$(echo "$REPO_INFO" | jq -r '.parent.name')
else
    # Not a fork, use current repository
    UPSTREAM_ORG=$(echo "$REPO_INFO" | jq -r '.owner.login')
    UPSTREAM_REPO=$(echo "$REPO_INFO" | jq -r '.name')
fi

UPSTREAM_PATH="${UPSTREAM_ORG}/${UPSTREAM_REPO}"
```

### 3. Derive Additional Identifiers

**SonarCloud project key:**

Replace `/` with `_` in the upstream path:

```bash
SONARCLOUD_KEY="${UPSTREAM_PATH//\//_}"
```

Example: `ansible-collections/amazon.aws` → `ansible-collections_amazon.aws`

**GitHub API path:**

```bash
GITHUB_API_PATH="repos/${UPSTREAM_PATH}"
```

Example: `repos/ansible-collections/amazon.aws`

**GitHub repository URL:**

```bash
GITHUB_URL="https://github.com/${UPSTREAM_PATH}"
```

Example: `https://github.com/ansible-collections/amazon.aws`

### 4. Return Information

Present the extracted information in a clear format:

```
Upstream Repository Information
================================
Organisation: ansible-collections
Repository: amazon.aws
Full path: ansible-collections/amazon.aws
Fork: Yes (current: octocat/amazon.aws)

Derived Identifiers:
- SonarCloud project key: ansible-collections_amazon.aws
- GitHub API path: repos/ansible-collections/amazon.aws
- GitHub URL: https://github.com/ansible-collections/amazon.aws
```

## Output Format

When invoked by other skills, provide the information in a structured format:

```
UPSTREAM_ORG=ansible-collections
UPSTREAM_REPO=amazon.aws
UPSTREAM_PATH=ansible-collections/amazon.aws
SONARCLOUD_KEY=ansible-collections_amazon.aws
GITHUB_API_PATH=repos/ansible-collections/amazon.aws
GITHUB_URL=https://github.com/ansible-collections/amazon.aws
IS_FORK=true
CURRENT_PATH=octocat/amazon.aws
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

### Not a GitHub Repository

```bash
if ! gh repo view &> /dev/null; then
    echo "Error: Current directory is not a GitHub repository or gh is not authenticated"
    echo "Run 'gh auth login' to authenticate"
    exit 1
fi
```

### Authentication Issues

```bash
if gh repo view --json parent 2>&1 | grep -q "authentication"; then
    echo "Error: gh CLI is not authenticated"
    echo "Run 'gh auth login' to authenticate with GitHub"
    exit 1
fi
```

## Example Usage

### Example 1: Fork Workflow

```
Repository: octocat/amazon.aws (fork of ansible-collections/amazon.aws)

Result:
UPSTREAM_PATH=ansible-collections/amazon.aws
IS_FORK=true
CURRENT_PATH=octocat/amazon.aws
```

### Example 2: Direct Clone (Not a Fork)

```
Repository: ansible-community/ai-forge (not a fork)

Result:
UPSTREAM_PATH=ansible-community/ai-forge
IS_FORK=false
CURRENT_PATH=ansible-community/ai-forge
```

## Caching Upstream Information

The upstream repository for a project **does not change during a session**. Skills and workflows should cache the result of `get-upstream-info` to avoid redundant API calls.

**Single skill needing upstream info multiple times:**

```
# At start of skill execution
upstream_info = invoke get-upstream-info
UPSTREAM_PATH = extract from upstream_info
SONARCLOUD_KEY = extract from upstream_info

# Reuse throughout skill
- Use SONARCLOUD_KEY for API calls
- Use UPSTREAM_PATH for gh commands
- Use GITHUB_URL for links
```

**Multiple skills in a workflow:**

```
# At start of workflow
upstream_info = invoke get-upstream-info once
Store values in session context

# Pass to skills as they're invoked
- sonarcloud-remediation: use cached SONARCLOUD_KEY
- get-pr-number: use cached UPSTREAM_PATH
- create-pr: use cached UPSTREAM_PATH
```

**Benefits:**

- Reduces `gh repo view` API calls (respects rate limiting)
- Improves performance (fewer subprocess executions)
- Ensures consistency across workflow

**When to re-invoke:**

- Never within the same session/workflow
- Only if user explicitly changes to a different repository directory

## Integration with Other Skills

This skill is designed to be referenced by other skills:

**In sonarcloud-remediation skill:**

```
Use the `get-upstream-info` skill to determine the SonarCloud project key.
Cache the result at the start of the skill if used multiple times.
```

**In get-pr-number skill:**

```
Use the `get-upstream-info` skill to determine the upstream repository for PR lookups.
Result should be cached if calling skill invokes both get-upstream-info and get-pr-number.
```

**In create-pr skill:**

```
Use the `get-upstream-info` skill to determine the target repository for the pull request.
Cache the result for use in PR creation and changelog updates.
```

**In release skill:**

```
Use the `get-upstream-info` skill to determine the repository for creating GitHub releases.
```

## Advantages Over Git Remote Parsing

1. **Accurate fork detection**: `gh` knows the GitHub parent relationship
2. **No URL parsing**: No need to handle different URL formats (HTTPS, SSH)
3. **Authoritative source**: Uses GitHub's API data directly
4. **Simpler logic**: One command instead of multiple git remote checks
5. **Error handling**: Clear error messages for auth and availability issues

## Important Notes

### Dependency

This skill requires:

- `gh` CLI installed and available in PATH
- GitHub authentication configured (`gh auth login`)
- Current directory must be a GitHub repository

### Fork vs Upstream

The skill always returns the **upstream** (canonical) repository:

- For forks: Returns the parent repository
- For non-forks: Returns the current repository

This matches the common development workflow where:

- Contributors fork repositories
- PRs target the upstream repository
- CI/CD runs against the upstream

### Service-Specific Derivations

Currently supports:

- **SonarCloud**: `org_repo` format
- **GitHub API**: `repos/org/repo` format
- **GitHub URLs**: `https://github.com/org/repo`

Future extensions could add:

- CircleCI project identifiers
- Travis CI repository slugs
- Other CI/CD service identifiers
