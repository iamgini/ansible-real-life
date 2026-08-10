---
name: tox-lint
description: >
  Runs configured tox linters on an Ansible collection or Python project.
  Use this skill when you need to validate code quality with ansible-lint,
  black, isort, flake8, pylint, flynt, or ruff before commits or releases.
user-invocable: true
---

# Skill: tox-lint

## Purpose

Execute tox linting environments to ensure code quality and style consistency.
Runs multiple linters in parallel including black, isort, flake8, pylint,
ansible-lint, flynt, and ruff. The `scripts/run-linters.py` helper can detect
and run the appropriate tox lint command when a standard tox.ini layout is present.

## When to Invoke

TRIGGER when:

- User asks to "run lint" or "check code quality"
- Before committing code changes
- As part of release preparation workflow (after `stable-release-prep`)
- When contributing to Ansible collections
- To validate code meets team standards

DO NOT TRIGGER when:

- Performing full release (use `stable-release` skill instead)
- Running only tests (use `run-tests` skill instead)

## Prerequisites

- Python 3.8+
- tox (pip install tox)
- tox.ini with lint environments configured

## Linting Steps

### Step 1: Verify tox.ini Configuration

```bash
cd /path/to/collection

# Method 1: Check for lint label using tox itself (most robust)
if tox -l -m lint 2>/dev/null | grep -q -E '[^[:space:]]+'; then
    echo "Found lint label"
    TOX_CMD="tox -m lint"
# Method 2: Check for linters environment (older pattern)
elif tox -l 2>/dev/null | grep -qE "^linters$"; then
    echo "Found linters environment"
    TOX_CMD="tox -e linters"
# Method 3: Check for individual lint environments
elif tox -l 2>/dev/null | grep -qE "^(black-lint|flake8-lint|pylint)$"; then
    echo "Found individual lint environments"
    # Build command from available environments
    LINT_ENVS=$(tox -l | grep -E "(black|flake8|pylint|isort|ansible)-lint$" | tr '\n' ',' | sed 's/,$//')
    TOX_CMD="tox -e $LINT_ENVS"
else
    echo "Warning: No standard lint configuration found"
    echo "Please configure tox.ini with a lint label or linters environment"
fi
```

**Note**: Method 1 uses `tox -l -m lint` which asks tox itself to list lint-labeled environments. This is more robust than parsing tox.ini because it works regardless of:

- Whether labels are on one line or multiple lines
- Whether labels are in [tox] section or individual [testenv] sections
- How the tox.ini is formatted

Expected tox.ini configuration:

```ini
[tox]
labels =
    lint = ansible-lint, black-lint, isort-lint, flynt-lint, flake8-lint, pylint-lint

[testenv:ansible-lint]
...

[testenv:black-lint]
...
```

### Step 2: Run Linters

Execute the command determined in Step 1:

```bash
# Run the detected tox command
$TOX_CMD

# This will be one of:
# - tox -m lint           (if labels are configured)
# - tox -e linters        (if linters environment exists)
# - tox -e black-lint,... (if individual lint envs found)
```

This runs:

- **ansible-lint**: Ansible best practices
- **black-lint**: Python code formatting check
- **isort-lint**: Import sorting check
- **flynt-lint**: f-string usage check
- **flake8-lint**: Python style guide (PEP 8)
- **pylint-lint**: Python code analysis
- **ruff-lint**: Fast Python linter (if configured)

### Step 3: Run ansible-lint Separately (CRITICAL)

**ALWAYS run ansible-lint separately** if it's not included in tox configuration:

```bash
# Check if ansible-lint was run by tox
if ! (tox -l | grep -q "ansible-lint" || grep -q "ansible-lint" tox.ini); then
  echo "Running ansible-lint separately..."
  ansible-lint
fi
```

**Why this is critical:**

- Many Ansible collections only configure Python linters in tox
- ansible-lint checks Ansible-specific issues like YAML indentation
- CI often runs ansible-lint separately
- Prevents "ansible-lint passed locally but failed in CI"

### Step 4: Review Results

**On success:**

```
✅ ansible-lint: PASSED (0 failures, 0 warnings in 32 files)
✅ black-lint: PASSED (21 files unchanged)
✅ isort-lint: PASSED
✅ flynt-lint: PASSED
✅ flake8-lint: PASSED
✅ pylint-lint: PASSED (10.00/10)

All linters passed! ✨
```

**On failures:**

```
❌ black-lint: FAILED (3 files would be reformatted)
   plugins/modules/my_module.py

   ➤ Auto-fix: tox -e black

❌ pylint: FAILED (score: 8.45/10)
   plugins/modules/my_module.py:45: unused-variable 'result'

   ⚠️  Manual fix required
```

## Linter Categories

### Auto-Fixable

- **black**: Code formatting → `tox -e black`
- **isort**: Import sorting → `tox -e isort`
- **flynt**: f-string conversions → `tox -e flynt`
- **ruff format**: Fast formatting → `tox -e ruff-format`

Quick fix command:

```bash
tox -e black,isort,flynt
```

### Manual Fix Required

- **pylint**: Code quality, complexity, unused variables
- **flake8**: Logic errors, undefined variables, style
- **ansible-lint**: Best practice violations
- **mypy**: Type checking errors

## Troubleshooting

### "tox.ini not found"

Ensure you're in the collection root:

```bash
cd /path/to/collection
ls tox.ini
```

### "No lint environments configured"

Add lint label to tox.ini:

```ini
[tox]
labels =
    lint = black-lint, flake8-lint, pylint-lint
```

### Slow execution

Run specific linter only:

```bash
tox -e ansible-lint
```

## Integration

This skill integrates with:

- `stable-release-prep` - Run after prep before commit
- `sanity` - Run alongside sanity tests
- `stable-release` - Part of full release workflow (quality checks)
