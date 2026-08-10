---
name: current-release
description: >
  Fetches the current release version from git tags, stable branches, or
  galaxy.yml. Use this skill when you need to determine the latest published
  collection version for version_added tags, changelog entries, or release
  planning.
user-invocable: false
---

# Skill: current-release

## Purpose

Fetch the current release version using git tags and stable branches, with fallback to `galaxy.yml`.
This is a helper skill that provides version information to other skills.

## When to Invoke

This is primarily a helper skill used by other skills (like `next-release`).

TRIGGER when:

- Another skill needs to know the current version
- A user explicitly asks "what is the current version?"
- A user asks "what version are we on?"

## Workflow

### Step 1 — Gather version information from all sources

**Find stable branch version (if exists)**:

```bash
MAJOR=$(git branch -r | grep -o 'stable-[0-9]\+' | grep -o '[0-9]\+' | sort -n | tail -1)
```

If a stable branch was found, find the latest tag for that major version:

```bash
STABLE_VERSION=$(git tag --list --sort=-version:refname | grep "^${MAJOR}\." | head -1)
```

Example: If `MAJOR=9`, this finds the highest 9.x.y tag (e.g., `9.2.0`).

**Always read galaxy.yml version**:

```bash
GALAXY_VERSION=$(grep '^version:' galaxy.yml | awk '{print $2}')
```

This may include `-dev0` suffix.

### Step 2 — Determine which version to use

**Version comparison algorithm**:

To compare two versions (e.g., `9.2.0` vs `10.0.0-dev0`):

1. Strip `-dev0` suffix from both versions
2. Split both versions on `.` to get [major, minor, patch]
3. Compare numerically:
   - If major differs: higher major wins
   - If major same, compare minor: higher minor wins
   - If major and minor same, compare patch: higher patch wins
   - If all equal: versions are equal

Example comparisons:

- `9.2.0` vs `10.0.0-dev0` → strip dev → `9.2.0` vs `10.0.0` → 10 > 9 → `10.0.0` is higher
- `9.2.0` vs `9.3.0-dev0` → strip dev → `9.2.0` vs `9.3.0` → 3 > 2 → `9.3.0` is higher
- `9.2.0` vs `9.2.1-dev0` → strip dev → `9.2.0` vs `9.2.1` → 1 > 0 → `9.2.1` is higher

**Decision logic**:

**If both stable branch and galaxy.yml exist**:

Compare the versions using algorithm above:

- If galaxy.yml version is higher: Use galaxy.yml (main is developing a new major/minor/patch)
- If git version is higher: FLAG as potential rebase needed
  - Report galaxy.yml version but warn that a newer version appears to have been released
  - Ask user if they need to rebase or if this is intentional (backport/older branch work)
  - For intentional older branch work with minor changes: galaxy.yml version can be used
- If versions are equal: Use either (prefer stable branch for consistency)

Example scenarios:

- stable-9 has `9.2.0`, galaxy.yml has `10.0.0-dev0` → Use galaxy.yml (main developing next major)
- stable-9 has `9.2.0`, galaxy.yml has `9.3.0-dev0` → Use galaxy.yml (main developing next minor)
- stable-9 has `9.2.0`, galaxy.yml has `9.2.1-dev0` → Use galaxy.yml (main developing next patch)
- stable-9 has `9.2.0`, galaxy.yml has `9.1.0-dev0` → FLAG: Report galaxy.yml 9.1.0 but warn that 9.2.0 appears to have been released - check if rebase needed
- stable-9 has `9.2.0`, galaxy.yml has `9.2.0` → Use stable (versions match)

**If only stable branch exists**: Use stable branch version

**If only galaxy.yml exists**: Use galaxy.yml version

### Step 3 — Parse and report

**Determine baseline version**:

Strip any `-dev0` suffix to get the baseline version.

Examples:

- `12.0.0-dev0` → baseline: `12.0.0`
- `12.1.3-dev0` → baseline: `12.1.3`
- `9.2.0` → baseline: `9.2.0`

**Determine status**:

- If version ended with `-dev0`: Status is "IN DEVELOPMENT"
- Otherwise: Status is "RELEASED"

**Determine source**:

- If found from git tags: Source is "git tag"
- If found from stable branch logic: Source is "stable branch + git tag"
- If from galaxy.yml: Source is "galaxy.yml"

### Step 4 — Output

Return the version information:

```text
Current version: <baseline version>
Source: <git tag | stable branch + git tag | galaxy.yml | galaxy.yml (main branch)>
Status: <IN DEVELOPMENT | RELEASED>
Stable branch version: <version> (if exists and different from current)

⚠️  WARNING: Version <git-version> appears to have been released since this branch was created.
Consider rebasing unless working on backport/older branch intentionally.
(only shown when git version > galaxy.yml version)
```

## Example Output

### Example 1: From stable branch and git tag (no main development)

```text
Current version: 9.2.0
Source: stable branch (stable-9) + git tag
Status: RELEASED
```

### Example 2: From galaxy.yml only (no stable branches)

```text
Current version: 12.0.0
Source: galaxy.yml (12.0.0-dev0)
Status: IN DEVELOPMENT
```

### Example 3: Main developing next major (stable branch exists)

```text
Current version: 10.0.0
Source: galaxy.yml (10.0.0-dev0 on main)
Status: IN DEVELOPMENT
Stable branch version: 9.2.0 (stable-9)
```

### Example 4: Main developing next minor (stable branch exists)

```text
Current version: 9.3.0
Source: galaxy.yml (9.3.0-dev0 on main)
Status: IN DEVELOPMENT
Stable branch version: 9.2.0 (stable-9)
```

### Example 5: Old branch (galaxy.yml behind released version)

```text
Current version: 9.1.0
Source: galaxy.yml (9.1.0-dev0)
Status: IN DEVELOPMENT
Stable branch version: 9.2.0 (stable-9)

⚠️  WARNING: Version 9.2.0 appears to have been released since this branch was created.
Consider rebasing unless working on backport/older branch intentionally.
```

## Integration with Other Skills

- **next-release**: Uses this skill to get the current version before calculating next versions
- **release**: Updates git tags and galaxy.yml version
- **changelog-fragment**: May reference current version when creating fragments
