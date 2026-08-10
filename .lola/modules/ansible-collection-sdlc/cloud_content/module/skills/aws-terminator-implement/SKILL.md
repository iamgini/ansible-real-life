---
name: aws-terminator-implement
description: >-
  Use this skill when implementing terminator classes and IAM permissions in
  the mattclay/aws-terminator repository after analysis. Creates terminator
  class code following Terminator/DbTerminator patterns, generates IAM
  permission blocks, and validates changes for PR submission. Invoke for
  "implement terminator", "create terminator classes", or "add terminator
  permissions".
allowed-tools: Read Edit Write Bash(command:git *) Bash(command:gh *) Bash(command:grep *)
argument-hint: "[--analysis <file>] [--interactive]"
triggers:
  - "implement terminator"
  - "aws-terminator implement"
  - "create terminator classes"
  - "add terminator permissions"
user-invocable: true
---

# AWS Terminator Implement

Implements terminator classes and IAM permissions in the mattclay/aws-terminator repository based on analysis from `/aws-terminator-analyze` or manual specification.

## Purpose

After analyzing an Ansible collection PR with `/aws-terminator-analyze`, this skill:

1. Creates terminator class implementations in the appropriate file
2. Adds IAM permissions to the appropriate policy file
3. Follows aws-terminator patterns and conventions
4. Creates properly formatted code ready for PR submission

## Quick Start

```bash
# Implement based on prior analysis (from /aws-terminator-analyze)
/aws-terminator-implement

# Interactive mode (prompts for each decision)
/aws-terminator-implement --interactive
```

**What it does**: Creates terminator class implementations, adds IAM permissions to policy files, runs validation tests, and prepares code for PR submission.

**Prerequisites**: Fork mattclay/aws-terminator, clone your fork, and run `/aws-terminator-analyze` first.

**See reference documentation** for terminator class patterns, IAM permission structure, and validation steps.

## When to Use

- After running `/aws-terminator-analyze` and reviewing the report
- When you know what terminators and permissions are needed
- To implement recommendations from analysis
- Before submitting a PR to mattclay/aws-terminator

## Usage

```bash
# Implement based on prior analysis
/aws-terminator-implement

# Implement with saved analysis file
/aws-terminator-implement --analysis terminator-analysis.md

# Interactive mode (prompt for each implementation)
/aws-terminator-implement --interactive
```

## Prerequisites

- **Fork** of mattclay/aws-terminator repository (fork it on GitHub first)
- aws-terminator fork cloned at `~/dev/aws-terminator`
- Analysis completed (from `/aws-terminator-analyze` or manual)
- Git configured with user credentials
- `gh` CLI authenticated (for PR creation)

## Step 1: Setup and Validation

**Check aws-terminator repository**:

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
git fetch origin
git checkout main
git pull origin main
```

**Create implementation branch**:

```bash
# Branch name format: add-<service>-terminators
# Example: add-medialive-terminators
git checkout -b add-<SERVICE>-terminators
```

## Step 2: Load Analysis Context

If `--analysis <file>` provided, read the analysis file.

Otherwise, use context from previous `/aws-terminator-analyze` invocation in this conversation.

**Required information**:

- Resource types to add terminators for
- AWS service boto3 client name
- Resource properties (id, name, created_time fields)
- Terminator file to modify (compute.py, application_services.py, etc.)
- IAM permissions to add
- Policy file to modify (compute.yaml, application-services.yaml, etc.)

**If missing context**, prompt user for:

```
I need the following information to implement terminators:

1. AWS Service: (e.g., medialive, rds, ec2)
2. Resource Types: (e.g., Cluster, Input, Network)
3. Terminator File: (e.g., application_services.py)
4. Policy File: (e.g., application-services.yaml)

You can provide this by:
- Running /aws-terminator-analyze first
- Providing an analysis file with --analysis
- Entering the details manually
```

## Step 3: Implement Terminator Classes

For each resource type, generate and add the terminator class.

Read `references/terminator-classes.md` for:

- Base class selection (`Terminator` vs `DbTerminator`)
- Class code templates
- Insertion point guidance
- Special cases (pagination, pre-delete, ignore terminated)

## Step 4: Implement IAM Permissions

Add permission blocks to the appropriate policy file.

Read `references/iam-permissions.md` for:

- Resource-scoped and global permission block templates
- Policy file insertion guidance
- Least-privilege best practices

## Step 5: Update Imports (if needed)

**Check if new imports are needed**:

```bash
cd ~/dev/aws-terminator
grep -n "^from " aws/terminator/<terminator-file>.py | head -10
grep -n "^import " aws/terminator/<terminator-file>.py | head -10
```

**Common imports**:

```python
import datetime
from aws.terminator import Terminator, DbTerminator
from aws.terminator.util import get_account_id
```

**Add imports if missing** (use Edit tool at top of file).

## Step 6: Validation

### Syntax Check

**Python syntax**:

```bash
cd ~/dev/aws-terminator
python3 -m py_compile aws/terminator/<terminator-file>.py
```

**YAML syntax**:

```bash
cd ~/dev/aws-terminator
python3 -c "import yaml; yaml.safe_load(open('aws/policy/<policy-file>.yaml'))"
```

### Run Tox Tests

```bash
cd ~/dev/aws-terminator
tox
```

Expected checks:

- pycodestyle - Python style
- pylint - Code quality
- yamllint - YAML style
- policy - Policy validation

### Check for Duplicates

**Duplicate terminators**:

```bash
grep -r "class <ResourceType>" aws/terminator/
# Should only find the new one
```

**Duplicate permissions**:

```bash
grep -r "<service>:<action>" aws/policy/
# Check if permission already exists elsewhere
```

## Step 7: Generate Implementation Summary

Create a summary of what was implemented using the template in `references/implementation-summary.md`.

## Interactive Mode

If `--interactive` flag is provided, prompt before each change:

```
Ready to implement <ResourceType>Terminator in <terminator-file>.py

Properties:
- id: <IdField>
- name: <NameField>
- created_time: <TimestampField>

Terminate operation: client.<delete_operation>(<IdParam>=self.id)

Proceed with implementation? [Y/n]:
```

## Configuration

Optional environment variables:

```bash
# Local aws-terminator path (defaults to ~/dev/aws-terminator)
export AWS_TERMINATOR_PATH="~/custom/path"
```

If not set, the skill uses `~/dev/aws-terminator` as the default location.

**Fork Setup**:

This skill requires a fork of mattclay/aws-terminator:

1. Fork mattclay/aws-terminator on GitHub to your account
2. Clone from YOUR fork (detected via `gh api user`)
3. Upstream remote set to mattclay/aws-terminator
4. Push changes to origin (your fork)
5. Create PR from your fork to mattclay/aws-terminator

## Error Handling

**aws-terminator not found**:

```
Error: aws-terminator repository not found at ~/dev/aws-terminator

Clone it with:
  git clone https://github.com/mattclay/aws-terminator.git ~/dev/aws-terminator

Then re-run this skill.
```

**Dirty working tree**:

```
Error: aws-terminator repository has uncommitted changes

Commit or stash changes first:
  cd ~/dev/aws-terminator
  git status
  git stash  # or git commit
```

**Missing analysis context**:

```
Error: No analysis context found

Run /aws-terminator-analyze first, or provide:
  --analysis <file> pointing to analysis output
```

## Related Skills

- `/aws-terminator-analyze` - Analyze Ansible collection PR to determine what's needed
- `/aws-terminator-workflow` - Orchestrator that runs analyze + implement + PR creation

## References

- `references/terminator-classes.md` - Terminator class templates and special cases
- `references/iam-permissions.md` - IAM permission block templates
- `references/implementation-summary.md` - Implementation summary template
- aws-terminator repository: https://github.com/mattclay/aws-terminator
- Terminator base classes: `aws/terminator/__init__.py`
- Existing terminators: `aws/terminator/*.py`
- Policy structure: `aws/policy/*.yaml`
