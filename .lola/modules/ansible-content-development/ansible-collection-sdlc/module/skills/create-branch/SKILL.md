---
name: create-branch
description: >
  Creates a new feature branch following project conventions. Use this skill when
  you need to start new work by fetching latest from origin, basing off
  origin/main, and configuring fork-friendly upstream tracking.
user-invocable: true
---

# Skill: create-branch

## Purpose

Create a new feature branch based on origin/main following project conventions.
This skill handles checking current state, fetching latest changes, creating the branch,
and setting up proper tracking for fork-based workflows.

## When to Invoke

TRIGGER when:

- User asks to create a new branch
- Starting work on a new feature, fix, or task
- User asks "create a branch for..."
- Beginning work that should not be on main

DO NOT TRIGGER when:

- Already on a feature branch and ready to work
- User is just asking about branch naming conventions

## Inputs

- `branch_name` (optional): Suggested branch name. If not provided, will prompt user with naming patterns.

## Workflow

### Step 1 — Verify current state

Check if there are uncommitted changes:

```bash
git status
```

If there are uncommitted changes, use `AskUserQuestion` to ask the user what to do:

Options:

- "Commit them first" (use `commit` skill)
- "Stash them"
- "Discard them"
- "Continue anyway"

Handle the selected option before proceeding.

### Step 2 — Fetch latest from origin

Update the remote tracking branches:

```bash
git fetch origin
```

This ensures the branch will be based on the latest upstream code.

### Step 3 — Determine branch name

If `branch_name` was not provided as input, ask the user for the branch name.

Suggest patterns based on common use cases:

**Issue-based:**

- `issue/<number>` - For issue-specific work (e.g., `issue/12345`)

**Feature/fix types:**

- `<module>/<feature>` - For module enhancements (e.g., `ec2_instance/new_parameter`)
- `feature/<name>` - For new features
- `bugfix/<name>` - For bug fixes
- `fix/<name>` - For fixes

**Code quality:**

- `deprecation/<name>` - For deprecation removal (e.g., `deprecation/old_param`)
- `sonarcloud/<category>` - For SonarCloud fixes (e.g., `sonarcloud/security`)
- `security/<category>` - For security fixes (e.g., `security/weak-cryptography`)
- `reliability/<category>` - For reliability fixes (e.g., `reliability/duplicate-branches`)
- `maintainability/<module>` - For maintainability fixes (e.g., `maintainability/module_name`)

**Infrastructure:**

- `requirements/<desc>` - For dependency updates (e.g., `requirements/python311`)
- `ci/<name>` - For CI/CD changes
- `docs/<topic>` - For documentation updates

**Keep branch names:**

- Short and descriptive
- Lowercase with hyphens or slashes
- Under 50 characters when possible

### Step 4 — Create and checkout new branch

Create the branch based on origin/main:

```bash
git checkout -b <branch-name> origin/main
```

This ensures the branch starts from the latest upstream main branch.

### Step 5 — Unset remote tracking

After creating a new local branch from origin/main, unset the remote tracking:

```bash
git branch --unset-upstream
```

**Why:** In fork-based workflows, new branches will be pushed to a personal fork (not origin).
The upstream tracking will be set when first pushing with `git push -u <remote> <branch-name>`.

### Step 6 — Confirm success

Display to the user:

```
Created new branch: <branch-name>
Based on: origin/main (<commit-sha>)

Next steps:
- Make your changes
- Commit using the 'commit' skill
- Push with: git push -u <your-remote> <branch-name>
```

## Important Notes

### Fork-based Workflows

- Always base new branches off `origin/main` to ensure they start from the latest upstream state
- The upstream is unset because new branches will be pushed to a fork remote (not origin)
- First push should use `-u` flag to set upstream tracking: `git push -u fork <branch-name>`
- Check user's CLAUDE.md for their preferred remote name (often `fork`, `upstream`, or their username)

### Branch Naming Conventions

Different projects may have different conventions. The patterns suggested here follow common practices:

- Use `/` to separate category from name (e.g., `feature/name`)
- Use `-` within names (e.g., `bugfix/ec2-instance-fix`)
- Avoid special characters, spaces, or uppercase letters
- Be descriptive but concise

### Handling Uncommitted Changes

When uncommitted changes exist:

- **Commit first** is usually the best option if changes are complete
- **Stash** if changes are work-in-progress that you want to keep
- **Discard** only if changes are experimental and no longer needed
- **Continue anyway** if changes are unrelated and you want to bring them to the new branch

## Integration with Other Skills

- **commit**: Used if user chooses to commit changes before creating branch
- **create-pr**: Used after branch work is complete to create pull request

## Example Usage

### Example 1: Creating branch for new feature

```
User: "Create a branch for adding a new parameter to ec2_instance"

Step 1: Check git status - clean
Step 2: Fetch from origin - success
Step 3: Suggest branch name - "ec2_instance/new_parameter"
Step 4: Create branch - git checkout -b ec2_instance/new_parameter origin/main
Step 5: Unset upstream - git branch --unset-upstream
Step 6: Confirm success

Created new branch: ec2_instance/new_parameter
Based on: origin/main (abc1234)

Next steps:
- Make your changes
- Commit using the 'commit' skill
- Push with: git push -u fork ec2_instance/new_parameter
```

### Example 2: Creating branch with uncommitted changes

```
User: "Create a branch for issue 12345"

Step 1: Check git status - uncommitted changes found
        Ask user: What to do with uncommitted changes?
        User selects: "Commit them first"
        Use commit skill to create commit
Step 2: Fetch from origin - success
Step 3: Use suggested name - "issue/12345"
Step 4: Create branch - git checkout -b issue/12345 origin/main
Step 5: Unset upstream - git branch --unset-upstream
Step 6: Confirm success

Created new branch: issue/12345
Based on: origin/main (def5678)
```

### Example 3: Creating branch for deprecation cleanup

```
User: "Create a branch to remove the old_param deprecation"

Step 1: Check git status - clean
Step 2: Fetch from origin - success
Step 3: Suggest branch name - "deprecation/old_param"
Step 4: Create branch - git checkout -b deprecation/old_param origin/main
Step 5: Unset upstream - git branch --unset-upstream
Step 6: Confirm success

Created new branch: deprecation/old_param
Based on: origin/main (ghi9012)

This branch is ready for use with the 'remove-deprecations' skill.
```
