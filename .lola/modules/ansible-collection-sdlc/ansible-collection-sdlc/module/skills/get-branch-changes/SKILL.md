---
name: get-branch-changes
description: >
  Determines merge-base and changed files for the current branch. Use this skill
  when you need to identify branch-scoped changes without unrelated commits from
  the target branch.
user-invocable: false
---

# Skill: get-branch-changes

## Purpose

Correctly identify what files have changed in the current branch by finding the merge-base with the target branch, avoiding inclusion of unrelated changes when branch is behind target.

This is a helper skill used internally by other skills.

## When to Invoke

This is primarily a helper skill used by:

- `changelog-fragment` - To analyze what files changed
- `create-pr` - To determine PR scope and suggest details
- Any skill that needs to know "what changed in this branch"

TRIGGER when:

- Another skill needs to know the merge-base
- Another skill needs the list of changed files in current branch
- Need to avoid including unrelated changes from target branch

## Workflow

### Step 1 — Determine target branch

**Default to main branch**:

- Use `origin/main` as the default target
- If `origin/main` doesn't exist, try `origin/master`

**Allow user override for stable branches**:

If the user is working on a backport or stable branch feature, they may specify a different target:

- Use `AskUserQuestion` if context suggests this might be a backport:
  - Branch name contains "stable" or "backport"
  - Multiple stable branches exist
- Question: "Target branch for comparison? (main is default)"
- Options: origin/main, origin/stable-9, origin/stable-10, etc.

**Store target branch** for later steps.

**Example scenarios**:

- Feature branch `add-new-param` → Assume target is `origin/main`
- Branch `backport-fix-to-stable9` → Ask user, suggest `origin/stable-9`
- Branch `fix-bug` but user knows it's for stable-9 → User can specify when asked

### Step 2 — Find merge-base

**Calculate common ancestor**:

```bash
MERGE_BASE=$(git merge-base HEAD <target-branch>)
```

This finds the commit where the current branch diverged from the target.

**Example**:

```
origin/main: A -- B -- C -- D -- E
                    \
current:             F -- G -- H
```

Merge-base is commit `B` (where branch diverged).

**Verify merge-base**:

- Ensure merge-base SHA is not empty
- If empty, branch may not have diverged - report current HEAD as merge-base

### Step 3 — Get changed files

**List all changed files since merge-base**:

```bash
git diff --name-only <merge-base>...HEAD
```

This shows only files changed in current branch, not changes from target.

**Categorize files** (optional, for skills that need it):

Group by type:

- **Code files**: `plugins/`, `*.py` (excluding tests)
- **Test files**: `tests/`
- **Documentation**: `docs/`, `*.md`, `*.rst`
- **Changelog fragments**: `changelogs/fragments/*.yml`, `changelogs/fragments/*.yaml`
- **CI/CD**: `.github/`, `.gitlab-ci.yml`, `*.cfg`, `tox.ini`
- **Other**: Everything else

### Step 4 — Get commit information

**List commits in branch**:

```bash
git log --oneline <merge-base>..HEAD
```

This shows commits made in current branch only.

**Count commits**:

```bash
git rev-list --count <merge-base>..HEAD
```

### Step 5 — Output

Return structured information:

```text
Target branch: <origin/main | origin/stable-X | origin/master>
Merge-base: <commit-sha>
Commits in branch: <count>

Changed files (<total-count>):
<list of files, one per line>

Categories:
- Code: <count> files
- Tests: <count> files
- Docs: <count> files
- Changelog: <count> files
- CI/CD: <count> files
- Other: <count> files
```

## Example Output

### Example 1: Feature branch on main

```text
Target branch: origin/main
Merge-base: a1b2c3d4
Commits in branch: 3

Changed files (5):
plugins/modules/ec2_instance.py
plugins/module_utils/ec2.py
tests/integration/targets/ec2_instance/tasks/main.yml
changelogs/fragments/123-ec2-instance-new-param.yml
docs/ec2_instance_module.rst

Categories:
- Code: 2 files
- Tests: 1 file
- Docs: 1 file
- Changelog: 1 file
- CI/CD: 0 files
- Other: 0 files
```

### Example 2: Backport to stable branch

```text
Target branch: origin/stable-9
Merge-base: e5f6g7h8
Commits in branch: 1

Changed files (2):
plugins/modules/s3_bucket.py
changelogs/fragments/456-s3-bucket-bugfix.yml

Categories:
- Code: 1 file
- Tests: 0 files
- Docs: 0 files
- Changelog: 1 file
- CI/CD: 0 files
- Other: 0 files
```

### Example 3: Branch behind main (demonstrates why merge-base matters)

```text
Scenario:
origin/main: A -- B -- C -- D -- E -- F
                    \
feature:             G -- H

User is on 'feature' branch at commit H.
origin/main has advanced to F since branch creation.

Using git diff origin/main...HEAD would include changes D, E, F (wrong!)
Using merge-base (B) then git diff B...HEAD shows only G, H (correct!)

Target branch: origin/main
Merge-base: b2c3d4e5 (commit B)
Commits in branch: 2

Changed files (3):
plugins/modules/new_module.py
tests/unit/plugins/modules/test_new_module.py
changelogs/fragments/789-new-module.yml

Categories:
- Code: 1 file
- Tests: 1 file
- Docs: 0 files
- Changelog: 1 file
- CI/CD: 0 files
- Other: 0 files
```

## Integration with Other Skills

- **changelog-fragment**: Uses this to determine what files changed for fragment creation
- **create-pr**: Uses this to analyze changes and suggest PR details
- **pr-review**: Could use this to focus review on actual branch changes
- **release**: Could use this to validate release branch changes

## Notes

- Always uses merge-base to avoid including unrelated changes
- Handles both main and stable branch targets
- Provides categorized file lists for skills that need it
- Works correctly even when branch is behind target
- Does not modify any files, read-only operation
