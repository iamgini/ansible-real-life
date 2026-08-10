---
name: remove-deprecations
description: >-
  Find and remediate overdue deprecation warnings in Ansible collection code.
  Identifies deprecated code past removal date/version and helps implement
  necessary changes. Use when preparing releases or cleaning up technical debt.
user-invocable: true
---

# Skill: remove-deprecations

## Purpose

Find and remediate overdue deprecation warnings in the codebase.
This skill helps identify deprecated code that should have been removed or changed based on the deprecation date or version,
then guides implementation of the necessary changes.

## When to Invoke

TRIGGER when:

- Preparing for a major release (to remove version-based deprecations)
- User asks to clean up deprecations
- User asks what deprecations are overdue
- Conducting technical debt cleanup

DO NOT TRIGGER when:

- Adding new deprecation warnings (that's part of regular development)
- Reviewing deprecation policy (that's documentation)

## Inputs

- `priority` (optional): Filter to specific priority level (CRITICAL, HIGH, MEDIUM, LOW)
- `version` (optional): Target specific version (e.g., "12.0.0" to find all deprecations blocking that version)

## Workflow

### Step 1 — Determine version context

Use the `current-release` helper skill to get version information.

Use the `next-release` helper skill to get next major/minor/patch versions.

This provides context for:

- Current version (e.g., `11.2.0`)
- Next minor (e.g., `11.3.0`)
- Next major (e.g., `12.0.0`)

### Step 2 — Find all deprecation warnings

Search for deprecations in the codebase using multiple patterns:

#### Pattern A: module.deprecate() calls

```bash
# Find deprecate() calls in plugins
grep -rn "\.deprecate(" plugins/ --include="*.py"

# Find deprecate_attribute() calls
grep -rn "deprecate_attribute" plugins/ --include="*.py"
```

#### Pattern B: argument_spec deprecations

```bash
# Find removed_in_version in argument_spec
grep -rn "removed_in_version" plugins/ --include="*.py"

# Find removed_at_date in argument_spec
grep -rn "removed_at_date" plugins/ --include="*.py"

# Find deprecated_aliases
grep -rn "deprecated_aliases" plugins/ --include="*.py"
```

#### Pattern C: runtime.yml redirects

```bash
# Find deprecated module redirects
grep -A 5 "redirect:" meta/runtime.yml
grep "deprecation:" meta/runtime.yml
```

For each deprecation found, extract:

- File and line number
- Deprecation type (module call, argument_spec, alias, redirect)
- Date parameter (e.g., `date="2024-12-01"` or `removed_at_date='2024-12-01'`)
- Version parameter (e.g., `version="12.0.0"` or `removed_in_version='12.0.0'`)
- Collection name parameter (e.g., `collection_name="community.general"`)
- Deprecation message or context
- What is being deprecated (parameter, alias, module, feature)

### Step 3 — Compare deprecations against current date and version

**Today's date:** Use current system date

**Date-based deprecations:**

- Parse the `date` parameter (format: `YYYY-MM-DD`)
- Compare to today's date
- Identify if overdue (date < today)
- Calculate how many days/months overdue

**Version-based deprecations:**

- Parse the `version` parameter
- Compare to current and next versions:
  - **Overdue**: version <= current version (should already be removed)
  - **Blocks next major**: version == next major
  - **Blocks next minor**: version == next minor
  - **Future**: version > next major

### Step 4 — Categorize deprecations

**Priority order:**

1. **CRITICAL** - Overdue (date or version), should be removed immediately
2. **HIGH** - Blocks next major release
3. **MEDIUM** - Blocks next minor release OR upcoming date-based (0-3 months)
4. **LOW** - Future deprecations (>3 months or version > next major)

**Type categories:**

- Parameter deprecations
- Parameter value/choice deprecations
- Module deprecations (redirect_is_deprecated)
- Return value deprecations
- Functionality deprecations
- Behaviour changes

### Step 5 — Present summary to user

Display a summary table with version context:

```
Current Version: 11.2.0
Next Minor: 11.3.0
Next Major: 12.0.0

Deprecation Status Summary
==========================

Total deprecations found: X

By Priority:
  CRITICAL (overdue - action required now): Y
  HIGH (blocks next major 12.0.0): A
  MEDIUM (blocks next minor 11.3.0 or upcoming): B
  LOW (future): C

CRITICAL - Overdue Deprecations
================================

File                          | Line | Overdue By        | Type      | Description
------------------------------|------|-------------------|-----------|------------------
plugins/modules/example.py    | 1375 | 115 days          | Parameter | old_param deprecated
plugins/modules/other.py      | 234  | since 11.0.0      | Choice    | mode=legacy
```

For each deprecation, show:

- Full context (file, line, code snippet)
- What needs to be removed/changed
- Suggested implementation approach
- Potential breaking change impact
- For version-based: which release it blocks

### Step 6 — Get user selection

Use `AskUserQuestion` to ask which deprecation(s) to address:

Options:

- "Fix all CRITICAL (overdue) deprecations"
- "Fix all HIGH (blocks next major) deprecations"
- "Fix all MEDIUM (blocks next minor) deprecations"
- "Fix selected deprecation" (then ask which one)
- "Show details only" (no changes)

### Step 7 — Implement deprecation removal

Follow the appropriate pattern based on deprecation type:

**Note:** Patterns A-C cover common removal scenarios (parameter, choice, behaviour).
Patterns D-F cover removal based on deprecation mechanism (argument_spec, alias, redirect).

#### Pattern A: Remove Deprecated Parameter (module.deprecate() call)

1. Read module documentation (DOCUMENTATION block)
2. Remove parameter from:
   - DOCUMENTATION string
   - EXAMPLES (if used)
   - RETURN (if affects return values)
   - `argument_spec` dictionary
   - Validation logic
3. Remove deprecation warning call
4. Remove any code paths specific to that parameter
5. Search for usages in tests: `grep -r "old_param" tests/`
6. Remove or update test cases

#### Pattern B: Remove Deprecated Choice/Mode

1. Remove choice from valid choices in argument_spec
2. Remove all code paths handling that choice
3. Remove deprecation warning
4. Update documentation (remove from choices list)
5. Remove integration tests for that choice

#### Pattern C: Change Default Behaviour

1. Remove old behaviour code path
2. Remove compatibility shim
3. Remove deprecation warning
4. Update parameter default value in argument_spec
5. Update documentation to reflect new default
6. Update or remove tests verifying old default

#### Pattern D: Remove argument_spec Deprecated Parameter

1. Find the parameter in `argument_spec` with `removed_in_version` or `removed_at_date`
2. Remove the entire parameter definition from argument_spec
3. Remove from DOCUMENTATION block
4. Remove from EXAMPLES (if used)
5. Remove any code that references `module.params['old_param']`
6. Search for usages in tests and remove

Example argument_spec before:

```python
argument_spec = dict(
    old_param=dict(
        type='str',
        removed_in_version='12.0.0',
        removed_from_collection='namespace.collection'
    ),
    new_param=dict(type='str')
)
```

After removal:

```python
argument_spec = dict(
    new_param=dict(type='str')
)
```

#### Pattern E: Remove Deprecated Alias

1. Find the parameter with `deprecated_aliases`
2. Remove the deprecated alias from the `aliases` list
3. Remove the corresponding entry from `deprecated_aliases`
4. Update DOCUMENTATION to remove the alias
5. Update tests using the old alias name

Example argument_spec before:

```python
argument_spec = dict(
    new_name=dict(
        type='str',
        aliases=['old_name'],
        deprecated_aliases=[dict(
            name='old_name',
            version='12.0.0',
            collection_name='namespace.collection'
        )]
    )
)
```

After removal:

```python
argument_spec = dict(
    new_name=dict(type='str')
)
```

#### Pattern F: Remove Entire Deprecated Module (runtime.yml redirect)

1. For redirect deprecations in `meta/runtime.yml`:
   - Remove entry from `meta/runtime.yml`
   - Remove the deprecated module file if it exists
   - Keep the target module (where it redirects to)
2. Update documentation
3. Remove integration tests for deprecated module name
4. Add note to changelog about removal

### Step 8 — Run tests

Use the `run-tests` skill to verify changes:

- Run sanity tests on changed files
- Run unit tests if module_utils were changed
- Run integration tests if module behaviour changed

Fix any failures before proceeding.

**Check for remaining references:**

```bash
# Search for references to removed functionality
grep -r "old_param" plugins/ tests/ docs/
grep -r "deprecated_feature" .
```

Update or remove as needed.

### Step 9 — Create changelog fragment

Use the `changelog-fragment` skill to create an appropriate fragment:

**For major breaking changes:**

```yaml
breaking_changes:
  - >-
    module_name - removed support for deprecated_feature.
    The deprecated_feature was deprecated in version X.Y.Z and the deprecation
    period has now ended (https://github.com/ORG/REPO/pull/XXXX).
```

**For parameter removals:**

```yaml
breaking_changes:
  - >-
    module_name - removed deprecated parameter ``old_param``.
    Use ``new_param`` instead. The parameter was deprecated in version X.Y.Z
    (https://github.com/ORG/REPO/pull/XXXX).
```

**For minor changes (removed obscure parameter):**

```yaml
minor_changes:
  - >-
    module_name - removed deprecated parameter ``old_param``
    (https://github.com/ORG/REPO/pull/XXXX).
```

### Step 10 — Commit changes

Use the `commit` skill to create a conventional commit:

**For date-based:**

```
feat!: remove overdue deprecation in module_name

Remove support for deprecated_feature (deprecated since X.Y.Z, removal date YYYY-MM-DD).

The deprecation period ended on YYYY-MM-DD. Users should migrate to new_feature.

BREAKING CHANGE: deprecated_feature is no longer supported in module_name.
```

**For version-based:**

```
feat!: remove deprecation scheduled for X.Y.Z in module_name

Remove support for deprecated_feature (deprecated in A.B.C, removal in X.Y.Z).

This removal was scheduled for version X.Y.Z. Users should migrate to new_feature.

BREAKING CHANGE: deprecated_feature is no longer supported in module_name.
```

### Step 11 — Create pull request (optional)

Ask user if they want to create a PR now.

If yes, use the `create-pr` skill with:

- Title: "Remove deprecation scheduled for X.Y.Z: [description]"
- Include: what was deprecated, when, why removing now, migration guide
- Suggested labels: `breaking-change`, `major`

## Important Notes

### Breaking Changes

- Deprecation removals are **breaking changes**
- Always use `breaking_changes` section in changelog for major removals
- Consider creating a migration guide if widely used
- Ensure PRs are properly labeled

### Version-based Deprecations for Major Releases

- Deprecations marked with `version="12.0.0"` must be removed BEFORE releasing 12.0.0
- Consider creating dedicated PR for all major-blocking deprecations
- Review and batch all `version="12.0.0"` deprecations together

### Edge Cases

**Deprecations in module_utils:**

- May affect multiple modules
- Check all modules that import the utility:

  ```bash
  grep -r "from.*module_utils.*import.*deprecated_function" plugins/
  ```

- More complex impact analysis required

**Deprecations with both date AND version:**

- Use whichever comes first as the removal trigger
- Example: `date="2024-12-01", version="12.0.0"` - if date is overdue, it's overdue

**Collection-namespaced deprecations:**

- Check `collection_name` parameter - may be deprecating in favour of another collection
- Ensure target collection has the replacement feature

**Parameter naming differences:**

- `module.deprecate()` calls use `collection_name='namespace.collection'`
- `argument_spec` deprecations use `removed_from_collection='namespace.collection'`
- Both serve the same purpose - identifying which collection the deprecation belongs to

## Integration with Other Skills

- **current-release**: Used to get current version for comparison
- **next-release**: Used to get next major/minor versions for categorization
- **run-tests**: Used to verify changes don't break existing functionality
- **changelog-fragment**: Used to document breaking changes
- **commit**: Used to create conventional commits
- **create-pr**: Used to create pull request for review

## Example Output

### Example 1: Preparing for major release

```
Current Version: 11.2.0 (IN DEVELOPMENT)
Next Minor: 11.2.0
Next Major: 12.0.0

Found 8 deprecations:
- CRITICAL (overdue): 0
- HIGH (blocks 12.0.0): 5
- MEDIUM (blocks 11.2.0 or soon): 2
- LOW (future): 1

HIGH Priority - Blocks Next Major (12.0.0)
===========================================

1. plugins/modules/ec2_instance.py:450
   Parameter: vpc_subnet_id
   Version: 12.0.0
   Message: "Use subnets.subnet_id instead"
   Impact: Users must update playbooks to use new parameter structure

2. plugins/modules/s3_bucket.py:890
   Choice: mode=legacy
   Version: 12.0.0
   Message: "Legacy mode will be removed in 12.0.0"
   Impact: Users relying on legacy behaviour must update

[...]

What would you like to do?
> Fix all HIGH (blocks next major) deprecations
```

### Example 2: Overdue deprecations

```
Current Version: 9.2.0 (RELEASED)
Next Minor: 9.3.0
Next Major: 10.0.0

Found 3 deprecations:
- CRITICAL (overdue): 2
- HIGH (blocks 10.0.0): 0
- MEDIUM: 1
- LOW: 0

CRITICAL - Overdue Deprecations
================================

1. plugins/modules/rds_instance.py:234
   Parameter: master_username
   Date: 2025-12-01
   Overdue by: 104 days
   Message: "Renamed to db_username"
   Impact: Breaking change, users must update parameter name

2. plugins/module_utils/core.py:67
   Function: get_aws_connection_info
   Date: 2026-01-15
   Overdue by: 90 days
   Message: "Use get_aws_connection_params instead"
   Impact: May affect multiple modules importing this function

These deprecations are OVERDUE and should be removed immediately.
```
