---
name: create-pr
description: >
  Creates a draft pull request with pre-flight checks, changelog validation,
  and formatted PR details. Use this skill when you are ready to open a pull
  request for collection changes.
user-invocable: true
---

# Skill: create-pr

## Purpose

Create a draft pull request following Ansible collection standards with pre-flight checks, changelog validation, and automated PR template formatting.

## When to Invoke

TRIGGER when:

- User asks to "create a PR", "create a pull request", "make a PR"
- User asks to "open a PR" or "submit changes"
- After completing a feature and user wants to propose changes upstream

DO NOT TRIGGER when:

- Creating a release PR (use `release` skill instead)
- User just wants to push changes without creating a PR

## Workflow

### Step 1 — Pre-flight checks

**Verify branch**:

- Check current branch with `git branch --show-current`
- If on `main` or `master`, STOP and warn: "Cannot create PR from main branch. Create a feature branch first."
- Display current branch name

**Check git status**:

- Run `git status --porcelain` to check for uncommitted changes
- If uncommitted changes exist:
  - Use `AskUserQuestion`: "Uncommitted changes detected. Proceed anyway?"
  - If user declines, STOP

**Check for changelog fragments**:

- Use `get-branch-changes` helper skill to get changed files in this branch
- Check if changes are only in: `changelogs/fragments/`, `.github/`, `tests/`, `docs/`, `*.md` files
  - If yes, changelog fragment NOT required
- For other code changes:
  - Filter changed files for changelog fragments: `grep '^changelogs/fragments/.*\.ya\?ml$'`
  - If changelog fragment exists:
    - Read it with `Read` tool to verify it describes current changes
    - If seems outdated, ask user: "Changelog fragment may be outdated. Update it?"
  - If no changelog fragment exists:
    - Use `AskUserQuestion`: "No changelog fragment found. Create one?"
    - If yes: "Use the `changelog-fragment` skill to create a fragment, then re-run create-pr"
    - If no: Note to apply `skip-changelog` label in Step 5

### Step 2 — Run tests (optional)

**Test validation**:

- Check if `run-tests` skill was invoked recently in this session
- If not, use `AskUserQuestion`: "Run tests before creating PR?"
  - If yes: Invoke `run-tests` skill
  - If tests fail, STOP and report failures
  - If no: Proceed (user takes responsibility)

### Step 3 — Push to remote

**Detect upstream and push**:

- Use `get-upstream-info` helper skill to determine upstream repository
- Check if branch is already tracking a remote: `git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null`
- If already pushed and up to date (`git status` shows "up to date"), skip push
- If not pushed or local is ahead:
  - Check user's CLAUDE.md for remote preference
  - If no preference and multiple remotes exist, use `AskUserQuestion` to select remote
  - Push with: `git push -u <remote> <branch-name>`
- If push fails, report error and STOP

### Step 4 — Analyze changes and generate PR details

**Gather context**:

- Use `get-branch-changes` helper skill to get:
  - Merge-base and target branch
  - Changed files with categorization
  - Commits in branch
- Read changelog fragment(s) if any exist
- Review file types from categorization (code, tests, docs, etc.)

**Generate PR suggestions**:

Based on analysis, draft:

- **Title**: Concise description from commits/changelog (≤ 72 chars)
- **Summary**: What changed and why (synthesize from commits)
  - Include "Fixes #NNN" or "Closes #NNN" if applicable
- **Component name**: Module/plugin name from changed files
- **Issue type**: Infer from changes:
  - `Bugfix` - if fixing bugs
  - `Feature` - if adding new functionality
  - `New Module` - if adding new module
  - `Docs` - if only documentation changes
  - `Test` - if only test changes

**Confirm with user**:

Use `AskUserQuestion` to present suggestions and allow editing:

```
Title: <suggested-title>
Summary: <suggested-summary>
Issue Type: <Bugfix/Feature/New Module/Docs/Test>
Component: <component-name>
```

### Step 5 — Create pull request

**Detect PR template**:

- Check if `.github/PULL_REQUEST_TEMPLATE.md` exists
- If exists, read it to determine required sections
- If not exists, use Ansible collection standard template

**Standard Ansible collection template**:

```markdown
##### SUMMARY
<user-approved summary>

<"Fixes #NNN" or "Closes #NNN" if applicable>

##### ISSUE TYPE
<Bugfix/Feature/New Module/Docs/Test Pull Request>

##### COMPONENT NAME
<user-approved component name>

##### ADDITIONAL INFORMATION
<any additional context from user>

Assisted-by: <AI model and version>
```

**Create draft PR**:

- Use `get-upstream-info` to get upstream repository path
- Run: `gh pr create --draft --repo <upstream-repo> --title "<title>" --body "<formatted-body>"`
- Parse PR number from output
- **IMPORTANT**: Assisted-by line must NOT be commented out
- **IMPORTANT**: Do NOT add a "Generated with Claude Code" line

**Apply labels**:

- If skip-changelog was chosen in Step 1: `gh pr edit <pr-number> --add-label skip-changelog --repo <upstream-repo>`
- If changelog fragments contain `breaking_changes:` section: `gh pr edit <pr-number> --add-label do_not_backport --repo <upstream-repo>`
- Check for other label needs based on changes

### Step 6 — Update changelog with PR number

**Update fragments**:

- If changelog fragment(s) exist:
  - Use `changelog-fragment` skill to update fragments with PR number
  - This will commit and push the update

### Step 7 — Report success

Display to user:

```text
✓ Pull request created successfully

PR URL: <pr-url>
PR Number: #<pr-number>
Status: Draft
Labels: <labels-applied>
Changelog: <updated/not-applicable>

Next steps:
- Review the PR online and make any adjustments
- Mark as ready for review when complete
- Respond to any CI failures or review comments
```

## Configuration

**Required tools**:

- `gh` CLI - For creating pull requests
- `git` - For branch and commit operations

**Optional helper skills**:

- `get-upstream-info` - Detects upstream repository (recommended)
- `changelog-fragment` - Creates/updates changelog fragments
- `run-tests` - Runs test suite before PR creation

**User preferences** (from CLAUDE.md):

- Default remote for pushing (e.g., `origin`, `upstream`, custom fork)
- PR template customizations
- Auto-label rules

## Notes

- Always creates draft PRs (user marks ready when appropriate)
- Follows Ansible collection PR conventions
- Integrates with existing changelog-fragment workflow
- Respects skip-changelog for non-code changes
- Uses get-upstream-info for repository detection (no hardcoding)

## Integration with Other Skills

- **get-branch-changes**: Determines merge-base and changed files for PR analysis
- **get-upstream-info**: Determines upstream repository path
- **changelog-fragment**: Creates and updates changelog fragments with PR URLs
- **run-tests**: Optional pre-PR test validation
- **release**: Creates release PRs (different workflow)
