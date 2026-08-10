---
name: changelog-fragment
description: >-
  Creates or updates changelog fragments for documenting changes in Ansible
  collections. Use when asked to create a changelog fragment, add a fragment,
  or update fragments with PR URLs. Automatically detects repository context
  from git.
user-invocable: true
---

# Skill: changelog-fragment

## Purpose

Manage changelog fragments for Ansible collections. This skill creates new fragments
to document changes and updates existing fragments with PR URLs after pull request creation.

## When to Invoke

TRIGGER when:

- A user asks to create a changelog fragment or add a changelog entry
- A user asks what changelog fragment they need for their changes
- A user needs to update changelog fragments with a PR number after PR creation
- Working in a repository with `changelogs/fragments/` directory

DO NOT TRIGGER when:

- Generating the full changelog for a release (use `release` skill instead)
- General questions about changelog format unrelated to creating fragments

## Modes

This skill has two modes: **create** (default) and **update-pr-url**.

---

## Mode: Create Fragment

Create a new changelog fragment to document changes.

### Step 1 — Determine repository context

Use the `get-upstream-info` helper skill to extract repository information for generating proper PR URLs.

This provides the base repository path (e.g., `ansible-collections/amazon.aws`) to construct
GitHub PR URLs: `https://github.com/<repo>/pull/<number>`.

If working in a collection, optionally extract namespace and name from `galaxy.yml`:

```bash
grep -E '^(namespace|name):' galaxy.yml 2>/dev/null
```

### Step 2 — Analyze current changes (optional but recommended)

Automatically analyze what has changed to suggest fragment content.

**Use `get-branch-changes` helper skill** to determine:

- Target branch (origin/main, origin/stable-X, etc.)
- Merge-base commit
- Changed files since merge-base
- Commits in branch

This ensures we only analyze changes in the current branch, avoiding unrelated changes when branch is behind target.

Based on this analysis, suggest:

- **Change type**: Infer from file paths and commit messages
- **Affected components**: Extract from modified file paths (e.g., `plugins/modules/ec2_instance.py` → `ec2_instance`)
- **Description**: Synthesize from commit messages

Present suggestions to the user for confirmation/editing.

**Note**: Using `git merge-base` ensures we only analyze changes made on the current branch,
regardless of whether the branch has been rebased or not.

### Step 3 — Determine the change type

If not auto-detected, ask the user to select the change type:

- `bugfixes`: Bug fixes and corrections
- `minor_changes`: New features, enhancements, or improvements
- `major_changes`: Significant new functionality or major updates
- `breaking_changes`: Changes that break backwards compatibility
- `deprecated_features`: Features marked as deprecated
- `removed_features`: Features that have been removed
- `security_fixes`: Security vulnerability fixes
- `trivial`: Trivial changes like typos, test additions, or refactoring (not user-facing)

### Step 4 — Gather details from user

Use `AskUserQuestion` to confirm or edit:

- The suggested change type
- The affected component/module (e.g., `ec2_instance`, `s3_bucket`, `aws_ssm connection plugin`)
- The description (1-2 sentences, user-facing perspective)
- Issue/PR number if applicable

### Step 5 — Generate filename

Create a filename following these rules:

- If PR/issue number provided: `<number>-<brief-slug>.yml` (e.g., `2869-ssm-connection-fix.yml`)
- Otherwise: `<brief-slug>.yml` (e.g., `plugin-utils-inventory-unittests.yml`)
- Use lowercase, hyphens for spaces, keep it concise (2-5 words)

### Step 6 — Create the fragment file

Create the fragment file in `changelogs/fragments/`:

```yaml
<change_type>:
  - <component> - <description> (https://github.com/<repo>/pull/XXXX).
```

**Single section example**:

```yaml
bugfixes:
  - ec2_instance - Fixed issue where tags were not properly applied during instance creation (https://github.com/ansible-collections/amazon.aws/pull/1234).
```

**Multiple entries, same section**:

```yaml
minor_changes:
  - s3_bucket - Add support for intelligent tiering configuration (https://github.com/ansible-collections/amazon.aws/pull/5678).
  - s3_bucket - Add validation for bucket name format (https://github.com/ansible-collections/amazon.aws/pull/5678).
```

**Multiple sections example**:

```yaml
minor_changes:
  - plugin_utils/inventory - Extract role session name generation into separate method (https://github.com/ansible-collections/amazon.aws/pull/2902).
trivial:
  - plugin_utils/inventory - Add unit tests for region handling (https://github.com/ansible-collections/amazon.aws/pull/2902).
```

**Important formatting rules**:

- Each entry should be from a user's perspective (what changed, not how it was implemented)
- End each entry with a full stop before the PR link
- The PR URL is required even for trivial changes
- If PR number is unknown, use `XXXX` as placeholder - use the **update-pr-url** mode after PR creation
- For changes affecting multiple components, create separate entries under the same section

### Step 7 — Confirm with the user

**CONFIRM:** Show the filename and content to the user. Ask if they want to proceed with creating the file.
Only create the file after confirmation.

---

## Mode: Update PR URL

Update existing changelog fragments with the PR URL after pull request creation.

**Usage**: Invoke with a PR number (e.g., "update changelog fragments with PR 1234") or let the skill auto-detect.

### Step 1 — Determine PR number

If not provided as input, use the `get-pr-number` helper skill to detect the PR number for the current branch.

If no PR found, inform the user and stop.

### Step 2 — Determine repository context

Use the `get-upstream-info` helper skill to extract repository information.

### Step 3 — Find changelog fragments to update

List all fragment files that are part of current changes.

First, determine the merge base with the main branch:

**Use `get-branch-changes` helper skill** to get the merge-base and changed files for this branch.

Then filter for changelog fragments:

```bash
# Filter changed files for changelog fragments only
grep 'changelogs/fragments/' | grep -E '\.(yml|yaml)$'
```

### Step 4 — Check and update each fragment

For each fragment found:

1. Read the fragment file
2. Check if it contains `XXXX` or is missing a github.com URL
3. If it needs updating:
   - Replace `XXXX` with the actual PR number
   - If no URL exists, add it: `(https://github.com/<repo>/pull/<pr-number>).`
   - Preserve the existing YAML structure and formatting
   - Write the updated content back to the file

### Step 5 — Commit and push updates

If any fragments were updated, use standard git commands to commit and push:

```bash
git add changelogs/fragments/
git commit -m "Update changelog fragments with PR URL"
git push
```

Report which fragments were updated.

**Important**:

- Only update fragments that contain `XXXX` or are missing github.com URLs
- Don't update fragments that already have a valid PR URL
- Preserve the original YAML structure and formatting
- Use simple git commands rather than the `commit` skill for this automated update

---

## Integration with Other Skills

- **get-branch-changes**: Used to determine merge-base and changed files for fragment analysis
- **get-upstream-info**: Used to determine repository context and construct PR URLs
- **get-pr-number**: Used to auto-detect PR numbers in update-pr-url mode
- **commit skill**: May create commits that need changelog fragments
- **pr-review skill**: May remind users to create changelog fragments
- **release skill**: Consumes changelog fragments to generate the full CHANGELOG

## Output Format

When creating fragments, present:

1. The suggested filename
2. The complete fragment content
3. A confirmation prompt before writing the file

When updating fragments, present:

1. Which fragments were found
2. Which fragments were updated
3. The commit message used
