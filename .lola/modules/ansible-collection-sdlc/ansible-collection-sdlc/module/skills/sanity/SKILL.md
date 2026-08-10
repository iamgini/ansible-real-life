---
name: sanity
description: >-
  Run Ansible sanity tests with smart change detection. Use when testing
  Ansible collections, validating module code, running pre-commit checks, or
  preparing releases. Supports smart mode (tests only changed files - fast),
  full mode (all files), and changed-only mode (custom range).
user-invocable: true
---

# Skill: sanity

## Purpose

Execute `ansible-test sanity` with smart modes to balance speed and comprehensiveness.
Detects changed files and targets tests appropriately.

## When to Invoke

TRIGGER when:

- User asks to "run sanity" or "test modules"
- Before committing code changes
- As part of release preparation workflow
- When contributing to Ansible collections
- To validate module documentation and arguments

DO NOT TRIGGER when:

- Performing full release (use `stable-release` skill instead)
- Running only linters (use `tox-lint` skill instead)

## Prerequisites

- Python 3.8+
- ansible-core (pip install ansible-core)
- Collection structure with meta/runtime.yml

## Modes

### Smart Mode (Default - Recommended)

- Detects files changed since last stable tag
- Runs sanity only on changed modules/plugins
- **Fast, targeted feedback** (typically <1 minute)

### Full Mode

- Runs complete `ansible-test sanity` on entire collection
- All tests on all files
- **Slower but comprehensive** (5-15 minutes)

### Changed-Only Mode

- Tests files changed since specified git ref
- Requires `--since` parameter

## Usage

### Smart Mode (Recommended)

```bash
cd /path/to/collection

# Find base reference (last tag on stable branch)
BASE_REF=$(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD~10")

# Detect changed plugin/module files
CHANGED_FILES=$(git diff --name-only ${BASE_REF}..HEAD | \
                grep -E '^plugins/(modules|module_utils|action|lookup|filter|test|inventory)/')

if [ -z "$CHANGED_FILES" ]; then
  echo "No plugin/module changes detected"
  echo "Running minimal sanity (validate-modules only)"
  ansible-test sanity --test validate-modules
else
  echo "Testing changed files:"
  echo "$CHANGED_FILES"

  # Count changed files
  FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')

  if [ "$FILE_COUNT" -gt 10 ]; then
    echo "Many files changed ($FILE_COUNT files)"
    echo "Running full sanity for efficiency..."
    ansible-test sanity
  else
    # Test specific files
    ansible-test sanity $CHANGED_FILES
  fi
fi
```

### Full Mode

```bash
cd /path/to/collection

# Run full sanity test suite
ansible-test sanity

echo "Tests run: validate-modules, pylint, import, compile, yamllint"
```

### Changed-Only Mode

```bash
cd /path/to/collection

# Specify base reference
SINCE_REF="origin/stable-11"

# Detect and test changed files
CHANGED_FILES=$(git diff --name-only ${SINCE_REF}..HEAD | \
                grep -E '^plugins/')

if [ -n "$CHANGED_FILES" ]; then
  ansible-test sanity $CHANGED_FILES
fi
```

## Virtual Environment Setup

**CRITICAL**: Use compatible ansible-core and Python versions.

Check ansible-core/Python support matrix:

- ansible-core 2.17: Python 3.10, 3.11, 3.12
- ansible-core 2.18: Python 3.10, 3.11, 3.12
- ansible-core 2.19: Python 3.10, 3.11, 3.12
- ansible-core 2.20: Python 3.11, 3.12, 3.13
- ansible-core 2.21: Python 3.11, 3.12, 3.13

```bash
# Determine minimum required ansible-core from meta/runtime.yml
MIN_ANSIBLE=$(grep "^requires_ansible:" meta/runtime.yml | grep -oE '[0-9]+\.[0-9]+')

# Install compatible version
python3.12 -m venv .venv
source .venv/bin/activate
pip install "ansible-core~=2.20.0"
```

## Expected Output

**On success:**

```
Running sanity tests (smart mode)...
Base: 11.2.0 (12 commits ago)
Changed files detected: 2
  - plugins/modules/ec2_instance.py
  - plugins/module_utils/ec2_utils.py

Running: ansible-test sanity plugins/modules/ec2_instance.py \
                              plugins/module_utils/ec2_utils.py

Tests run: validate-modules, pylint, import, compile, yamllint
✅ All sanity tests passed!
Files tested: 2
Time: 45.3 seconds
```

**On failures:**

```
❌ Sanity tests failed (2 errors):

validate-modules:
  plugins/modules/my_module.py:
    - Missing RETURN documentation
    - Missing examples

pylint:
  plugins/module_utils/helper.py:12:
    - Unused variable 'result'

Fix these issues and re-run
```

## Performance Comparison

Example: amazon.aws collection (389 modules)

| Mode                    | Files Tested | Tests Run       | Time  |
|-------------------------|--------------|-----------------|-------|
| smart (2 files changed) | 2            | 5 tests × 2     | 0:45  |
| full                    | 389          | 5 tests × 389   | 12:30 |

**Recommendation**: Use smart mode for 95% of cases, full mode before major releases.

## Testing with Multiple ansible-core Versions (Release Workflow)

**BEST PRACTICE for releases**: Test with BOTH minimum and latest compatible ansible-core versions.

```bash
# Extract minimum version from meta/runtime.yml
MIN_ANSIBLE=$(grep "^requires_ansible:" meta/runtime.yml | grep -oE '[0-9]+\.[0-9]+')

# Test 1: Minimum supported version
echo "Testing with MINIMUM version: $MIN_ANSIBLE"
python3.12 -m venv .venv_min
source .venv_min/bin/activate
pip install "ansible-core==$MIN_ANSIBLE.0"
ansible-test sanity $CHANGED_FILES

# Test 2: Latest compatible version
echo "Testing with LATEST compatible version"
python3.11 -m venv .venv_latest
source .venv_latest/bin/activate
pip install "ansible-core~=2.21.0"
ansible-test sanity $CHANGED_FILES
```

## Troubleshooting

### "Not an Ansible collection"

```bash
cd ~/dev/collections/ansible_collections/namespace/collection
[ -f "galaxy.yml" ] && echo "Collection found"
```

### "ansible-test command not found"

```bash
pip install ansible-core
```

### Takes too long

Use smart mode (default) instead of full mode.

### No changed files detected

```bash
# Run minimal validation
ansible-test sanity --test validate-modules

# Or specify base ref
git diff --name-only origin/main..HEAD | grep plugins/
```

## Integration

This skill integrates with:

- `tox-lint` - Run alongside linters
- `stable-release` - Part of release workflow (quality checks)
- `run-tests` - Sanity is one type of test

## When to Use Each Mode

| Mode | Use Case | Time | Coverage |
| --- | --- | --- | --- |
| **smart** | Daily development, PRs | ~1 min | Changed files only |
| **full** | Major releases, main branch | ~10 min | All files |
| **changed-only** | Backports, specific branches | ~2 min | Custom range |

## Reference

- [ansible-test sanity documentation](https://docs.ansible.com/ansible/latest/dev_guide/testing/sanity/index.html)
- [ansible-core support matrix](https://docs.ansible.com/projects/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix)
