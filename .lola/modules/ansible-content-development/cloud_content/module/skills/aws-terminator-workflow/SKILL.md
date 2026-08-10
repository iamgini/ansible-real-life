---
name: aws-terminator-workflow
description: >-
  Use this skill when creating an end-to-end aws-terminator PR for new AWS
  modules in Ansible collections. Orchestrates analysis, implementation,
  validation, and PR submission, linking the companion PR back to the original
  collection PR. Invoke for "aws terminator workflow", "create aws-terminator
  pr", or "terminator pr for" a collection PR.
allowed-tools: Skill(skill:aws-terminator-analyze) Skill(skill:aws-terminator-implement) Read Write Bash(command:git *) Bash(command:gh *) Bash(command:python3 *)
argument-hint: "--pr <number> [--repo <owner/repo>] [--auto-pr] [--skip-tests] [--resume]"
triggers:
  - "aws terminator workflow"
  - "create aws-terminator pr"
  - "terminator pr for"
  - "aws-terminator workflow"
user-invocable: true
---

# AWS Terminator Workflow

Complete orchestrator for creating aws-terminator PRs when new AWS modules are added to Ansible collections. Coordinates analysis, implementation, testing, and PR submission.

## Purpose

When a PR adds new AWS modules to an Ansible collection (amazon.aws, community.aws, etc.), this workflow:

1. Analyzes what terminators and permissions are needed
2. Implements the terminator classes and IAM permissions
3. Runs validation tests
4. Creates a PR to mattclay/aws-terminator
5. Links it back to the original Ansible collection PR

## Quick Start

```bash
# Full automated workflow
/aws-terminator-workflow --pr 2353 --repo ansible-collections/community.aws

# Auto-mode (no prompts, fully automated)
/aws-terminator-workflow --pr 2353 --auto-pr
```

**What it does**: Analyzes the collection PR, implements terminators and IAM permissions in your fork, runs tests, creates a PR to mattclay/aws-terminator, and links it back to the original PR.

**Prerequisites**: Fork mattclay/aws-terminator on GitHub first. The skill handles cloning, branching, implementation, testing, and PR creation.

**See reference documentation** for PR templates, finalize steps, and error recovery.

## When to Use

- Complete automation: "Create aws-terminator PR for community.aws#2353"
- After seeing CI failures due to missing permissions
- When reviewing a PR that adds new AWS modules
- End-to-end from analysis to PR submission

## Usage

```bash
# Full automated workflow
/aws-terminator-workflow --pr 2353 --repo ansible-collections/community.aws

# Default to community.aws
/aws-terminator-workflow --pr 2353

# Auto-mode (no prompts, automatic decisions)
/aws-terminator-workflow --pr 2353 --auto-pr

# Skip tox tests (faster, use for drafts)
/aws-terminator-workflow --pr 2353 --skip-tests

# Check mode (analyze only, don't implement)
/aws-terminator-workflow --pr 2353 --check

# Resume from failed/interrupted workflow
/aws-terminator-workflow --pr 2353 --resume
```

## Workflow Steps

### Step 1: Analyze the Ansible Collection PR

**Run analysis skill**:

```bash
/aws-terminator-analyze --pr <PR_NUMBER> --repo <REPO>
```

**Output**: Analysis report with:

- Resources being added
- Terminator coverage status
- IAM permissions needed
- Implementation recommendations

**Checkpoint**: If `--check` mode, stop here and present analysis only.

**Prompt** (unless `--auto-pr`):

```
Analysis complete. Found:
- N resource types need terminators
- M IAM permissions need to be added

Proceed with implementation? [Y/n]:
```

### Step 2: Check for Existing Terminator PR

**Search for related PRs**:

```bash
# Check if PR description mentions existing terminator PR
gh pr view <PR_NUMBER> --repo <REPO> --json body | \
  grep -o "mattclay/aws-terminator/pull/[0-9]*"
```

**If existing terminator PR found**:

**Prompt** (unless `--auto-pr`):

```
Found existing terminator PR: #<TERMINATOR_PR_NUMBER>
Status: <open/merged/closed>

Options:
  [u] Update existing PR
  [n] Create new PR
  [s] Skip implementation

Choice [u/n/s]:
```

**If merged**: Exit with message "Terminator PR already merged"
**If closed**: Warn and offer to create new PR
**If open**: Offer to update the existing PR

### Step 3: Setup aws-terminator Repository

**Clone or update**:

```bash
if [ ! -d ~/dev/aws-terminator ]; then
  echo "Cloning aws-terminator fork..."
  # Clone from YOUR fork, not mattclay's repo
  FORK_USER=$(gh api user --jq .login)
  git clone https://github.com/$FORK_USER/aws-terminator.git ~/dev/aws-terminator

  cd ~/dev/aws-terminator
  # Set up upstream remote to mattclay's repo
  git remote add upstream https://github.com/mattclay/aws-terminator.git
  git fetch upstream
fi

cd ~/dev/aws-terminator
# Sync your fork's main with upstream
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**Create implementation branch**:

```bash
# Extract service name from analysis
SERVICE_NAME=$(echo "<first-resource-type>" | sed 's/[A-Z]/ &/g' | tr '[:upper:]' '[:lower:]' | awk '{print $1}')

# Branch naming: add-<service>-terminators
# Example: add-medialive-terminators
BRANCH_NAME="add-${SERVICE_NAME}-terminators"

git checkout -b "$BRANCH_NAME"
```

### Step 4: Implement Terminators and Permissions

**Run implementation skill**:

```bash
/aws-terminator-implement
```

This uses context from the analysis in Step 1.

**Implementation performs**:

- Creates terminator classes in appropriate `aws/terminator/*.py` files
- Adds IAM permissions to appropriate `aws/policy/*.yaml` files
- Follows aws-terminator code patterns
- Validates syntax

**Prompt** (unless `--auto-pr`) after each resource:

```
Implemented <ResourceType>Terminator in <file>.py
Added <N> IAM permissions to <policy-file>.yaml

Continue with next resource? [Y/n]:
```

### Step 5: Validation

**Python syntax check**:

```bash
cd ~/dev/aws-terminator

# Check all modified Python files
for file in $(git diff --name-only | grep '\.py$'); do
  python3 -m py_compile "$file" || echo "Syntax error in $file"
done
```

**YAML syntax check**:

```bash
# Check all modified YAML files
for file in $(git diff --name-only | grep '\.yaml$'); do
  python3 -c "import yaml; yaml.safe_load(open('$file'))" || echo "YAML error in $file"
done
```

**Run tox tests** (unless `--skip-tests`):

```bash
cd ~/dev/aws-terminator
tox
```

**Expected output**:

```
pycodestyle: OK
pylint: OK
yamllint: OK
policy: OK
congratulations :)
```

**On tox failure**:

**Prompt** (unless `--auto-pr`):

```
Tox validation failed:
<error output>

Options:
  [f] Fix and retry
  [s] Skip tox (continue anyway)
  [a] Abort workflow

Choice [f/s/a]:
```

### Step 6: Generate PR Description

Create comprehensive PR body using the template in `references/pr-description-template.md`.

### Step 7: Finalize (Conditional on `--auto-pr` Flag)

**Without `--auto-pr` (default)**: Stop after implementation and hand off git operations to the user.

**With `--auto-pr` flag**: Automate commit, push, and PR creation.

Read `references/finalize-steps.md` for manual handoff instructions, automated git steps, and deployment notes.

## Configuration

Optional environment variables:

```bash
# Fork username (defaults to gh config)
export AWS_TERMINATOR_FORK="your-username"

# Local aws-terminator path (defaults to ~/dev/aws-terminator)
export AWS_TERMINATOR_PATH="~/custom/path"

# Enable auto-PR mode (default: false, requires manual commit/push/PR)
export AWS_TERMINATOR_AUTO_PR="true"
```

**Fork Setup**:

Before using this workflow, you must:

1. Fork mattclay/aws-terminator on GitHub to your account
2. The skills will automatically clone from YOUR fork (detected via `gh api user`)
3. The upstream remote is set to mattclay/aws-terminator for syncing
4. Changes are pushed to origin (your fork)
5. PR is created from your-fork:branch → mattclay/aws-terminator:main

## Flags

| Flag | Description |
| ---- | ----------- |
| `--pr <number>` | **Required** - Ansible collection PR number |
| `--repo <owner/repo>` | Repository (default: ansible-collections/community.aws) |
| `--auto-pr` | Automate commit, push, and PR creation (default: manual) |
| `--skip-tests` | Skip tox validation (faster, for drafts) |
| `--check` | Analysis only, don't implement |
| `--interactive` | Prompt for each implementation decision |
| `--resume` | Resume from failed or interrupted workflow |

## Error Handling

Read `references/error-handling.md` for analysis, implementation, git/PR failure handling, and workflow recovery.

## Related Skills

- `/aws-terminator-analyze` - Just analyze (no implementation)
- `/aws-terminator-implement` - Just implement (analysis already done)

## References

- `references/pr-description-template.md` - PR description template
- `references/finalize-steps.md` - Manual and automated finalize steps
- `references/error-handling.md` - Error handling and recovery
- aws-terminator repository: https://github.com/mattclay/aws-terminator
- Ansible Cloud Content Handbook: https://github.com/ansible-collections/cloud-content-handbook
- Ansible Collections: amazon.aws, community.aws, amazon.ai, amazon.cloud
