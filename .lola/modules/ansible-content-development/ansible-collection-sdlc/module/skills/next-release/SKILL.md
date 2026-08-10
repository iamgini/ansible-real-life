---
name: next-release
description: >
  Calculates next patch, minor, and major release versions following SemVer.
  Use this skill when you need to determine version_added values or answer
  questions about the next collection release version.
user-invocable: true
---

# Skill: next-release

## Purpose

Calculate the next patch, minor, and major release versions following Semantic Versioning (SemVer).
This skill helps determine what version to use in `version_added` tags when documenting new features.

## When to Invoke

TRIGGER when:

- A user asks what version to use in a `version_added` tag
- A user asks about the next release version
- A user needs to know version numbers for documenting new features
- A user asks "what version should I use for version_added?"
- A user asks "I'm making a breaking change, what is the next major release?"

DO NOT TRIGGER when:

- Creating an actual release (use `release` skill instead)
- Managing changelog fragments (use `changelog-fragment` skill instead)

## Workflow

### Step 1 — Get current version

Use the `current-release` helper skill to fetch the current version.

This returns:

- Current version (baseline, with `-dev0` stripped if present)
- Source (git tag, stable branch + git tag, or galaxy.yml)
- Status (IN DEVELOPMENT or RELEASED)
- Stable branch version (if different from current, indicates git version vs galaxy.yml mismatch)

### Step 2 — Calculate next versions following SemVer

Use hierarchical decision logic:

**Note**: If current-release reports a rebase warning (git version > galaxy.yml version), skip version calculations and proceed directly to Step 3 Case 1 for rebase guidance.

#### Stable branch with lower major version (backport scenario)

When current-release reports:

- Current version: `A.B.C` (from galaxy.yml on main)
- Stable branch version: `X.Y.Z` (where X < A, major version jumped)

Calculate versions:

- Next patch: `X.Y.(Z+1)` (on stable branch X)
- Next minor: `X.(Y+1).0` (on stable branch X)
- Next major: `A.B.C` (current version on main, already in development)

**Example**: Current `10.0.0-dev0` on main, stable-9 at `9.2.0`

- Next patch: `9.2.1` (on stable-9)
- Next minor: `9.3.0` (on stable-9)
- Next major: `10.0.0` (on main)

#### Single-branch development

When no stable branch exists OR stable branch major version equals current major:

**If status is IN DEVELOPMENT** (`X.Y.Z-dev0`):

Current version IS the next release:

- If Y=0, Z=0: This is the next major
- If Z=0, Y≠0: This is the next minor
- If Z≠0: This is the next patch

After release, calculate:

- Next patch: `X.Y.(Z+1)`
- Next minor: `X.(Y+1).0`
- Next major: `(X+1).0.0`

**If status is RELEASED** (`X.Y.Z` tag exists):

Calculate from the released version:

- Next patch: `X.Y.(Z+1)`
- Next minor: `X.(Y+1).0`
- Next major: `(X+1).0.0`

### Step 3 — Provide version_added guidance

Use hierarchical decision logic with blocking conditions first:

#### Case 1: Branch out of date (rebase warning) - BLOCKING

When current-release reports a warning that git version > galaxy.yml version:

```text
Current version: X.Y.Z (from galaxy.yml)
Stable branch version: A.B.C (higher version exists)

⚠️  BRANCH OUT OF DATE WARNING ⚠️

Version A.B.C has been released since this branch was created.

If intentional (backport/older branch work):
→ New features: Use version_added: "X.Y.Z" (acceptable for intentional older branch work)
→ Next minor: "X.(Y+1).0" (but this version may already be released!)

If unintentional:
→ Rebase this branch on latest stable or main
→ Update galaxy.yml to match current development version after rebase
→ Most PRs should be based on latest code

Confirm your intent before proceeding.
```

**IMPORTANT**: Do not proceed to Cases 2-4 if rebase warning is present. User must fix branch first.

#### Case 2: Stable branch with lower major version (backport scenario)

When stable branch major < current major (and no rebase warning), check if current version is properly formatted:

**If current is A.0.0 (proper major release)**:

```text
Current version: A.0.0 (IN DEVELOPMENT on main - MAJOR RELEASE)
Stable branch version: X.Y.Z (stable-X)

For minor changes that will be backported:
→ Bugfixes: Use version_added: "X.Y.(Z+1)"
   Merge to main first, then backport to stable-X for release as X.Y.(Z+1)

→ New features: Use version_added: "X.(Y+1).0"
   Merge to main first, then backport to stable-X for release as X.(Y+1).0

→ Breaking changes: Use version_added: "A.0.0"
   Cannot be backported - merge to main for release as A.0.0

Workflow: Merge to main → Backport to stable-X → Release from stable-X

The version_added tag should reflect where the feature will actually be released
(the backport version), not the main branch version.
```

**If current is A.B.C where B>0 or C>0 (INCONSISTENCY)**:

```text
⚠️  VERSION INCONSISTENCY WARNING ⚠️

Current version: A.B.C on main
Stable branch version: X.Y.Z (stable-X where X < A)

Main has jumped major version (X → A) but current version is A.B.C (not A.0.0).
This is inconsistent - major version bumps should always result in A.0.0.

Expected: A.0.0-dev0 in galaxy.yml on main
Actual: A.B.C-dev0 in galaxy.yml on main

→ Check galaxy.yml - should it be A.0.0-dev0 instead?
→ If this is a mistake, update galaxy.yml to A.0.0-dev0

Please fix the version in galaxy.yml before proceeding.
```

#### Case 3: Single-branch development (IN DEVELOPMENT status)

When status is IN DEVELOPMENT and no special cases above apply:

**For major release (X.0.0-dev0)**:

```text
Current version: X.0.0 (IN DEVELOPMENT - MAJOR RELEASE)

→ New features: Use version_added: "X.0.0"
→ Breaking changes: Use version_added: "X.0.0" (allowed in major releases)
```

**For minor release (X.Y.0-dev0, Y≠0)**:

```text
Current version: X.Y.0 (IN DEVELOPMENT - MINOR RELEASE)

→ New features: Use version_added: "X.Y.0"
→ Breaking changes: NOT ALLOWED - next major is (X+1).0.0
   Coordinate with maintainers about when (X+1).0.0 development will begin.
```

**For patch release (X.Y.Z-dev0, Z≠0)**:

```text
Current version: X.Y.Z (IN DEVELOPMENT - PATCH RELEASE)

⚠️  SEMVER VIOLATION WARNING ⚠️

Patch releases can ONLY contain bugfixes per Semantic Versioning.

→ New features: NOT ALLOWED in patch releases
   Features require a minor release. Should galaxy.yml be X.(Y+1).0-dev0 instead?
   If you must add features now, use version_added: "X.(Y+1).0"

→ Breaking changes: NOT ALLOWED in patch releases
   Breaking changes require a major release (X+1).0.0
   Coordinate with maintainers about versioning strategy.
```

#### Case 4: Single-branch development (RELEASED status)

When status is RELEASED and no special cases apply:

```text
Current version: X.Y.Z (RELEASED)

→ New features: Use version_added: "X.(Y+1).0" (next minor)
→ Breaking changes: Use version_added: "(X+1).0.0" (next major)
   Coordinate with maintainers about when (X+1).0.0-dev0 development begins.
```

## Semantic Versioning Rules

- **Patch** (X.Y.Z+1): Bug fixes, security fixes - MUST NOT add new features
  - Rarely used in `version_added` tags
- **Minor** (X.Y+1.0): New features, enhancements - MUST be backwards-compatible
  - Most commonly used in `version_added` tags
- **Major** (X+1.0.0): Breaking changes - MAY break backwards compatibility
  - Used when features coincide with breaking changes
  - Requires coordination with maintainers

## Example Usage

Examples ordered by Step 3 case hierarchy:

### Example 1: Branch out of date (Case 1 - BLOCKING)

User: "I'm adding a new parameter, what version should I use?"

current-release returns:

```
Current version: 9.1.0 (IN DEVELOPMENT, from galaxy.yml: 9.1.0-dev0)
Stable branch version: 9.2.0 (stable-9)

⚠️  WARNING: Version 9.2.0 appears to have been released since this branch was created.
Consider rebasing unless working on backport/older branch intentionally.
```

Response:

```text
Current version: 9.1.0 (IN DEVELOPMENT - MINOR RELEASE)

⚠️  BRANCH OUT OF DATE WARNING ⚠️

Version 9.2.0 has been released since this branch was created.

If this is intentional (backport/older branch work):
→ New features: Use version_added: "9.1.0" (acceptable for intentional older branch work)
→ Next minor: "9.2.0" (but this version has already been released!)

If this is unintentional:
→ Consider rebasing this branch on the latest stable-9 or main
→ After rebase, galaxy.yml should be updated to match current development version

Most PRs should be based on the latest code. Confirm your intent before proceeding.
```

### Example 2: Major release with stable branch (Case 2a - backport scenario)

User: "I'm adding a new parameter, what version should I use?"

current-release returns: `10.0.0` (IN DEVELOPMENT, from galaxy.yml: 10.0.0-dev0 on main)
Stable branch: stable-9 at 9.2.0

Response:

```text
Current version: 10.0.0 (IN DEVELOPMENT on main - MAJOR RELEASE)
Stable branch version: 9.2.0 (stable-9)

For minor changes that will be backported:
→ Bugfixes: Use version_added: "9.2.1"
   Merge to main first, then backport to stable-9 for release as 9.2.1

→ New features: Use version_added: "9.3.0"
   Merge to main first, then backport to stable-9 for release as 9.3.0

→ Breaking changes: Use version_added: "10.0.0"
   Cannot be backported - merge to main for release as 10.0.0

For your new parameter (a minor feature), use version_added: "9.3.0".

Workflow: Merge to main → Backport to stable-9 → Release from stable-9
```

### Example 3: Version inconsistency (Case 2b - major jump but not X.0.0)

User: "I'm adding a new feature, what version should I use?"

current-release returns: `10.1.0` (IN DEVELOPMENT, from galaxy.yml: 10.1.0-dev0 on main)
Stable branch: stable-9 at 9.2.0

Response:

```text
⚠️  VERSION INCONSISTENCY WARNING ⚠️

Current version: 10.1.0 on main
Stable branch version: 9.2.0 (stable-9)

Main has jumped major version (9 → 10) but current version is 10.1.0 (not 10.0.0).
This is inconsistent - major version bumps should always result in 10.0.0.

Expected: 10.0.0-dev0 in galaxy.yml on main
Actual: 10.1.0-dev0 in galaxy.yml on main

→ Check galaxy.yml - should it be 10.0.0-dev0 instead?
→ If this is a mistake, update galaxy.yml to 10.0.0-dev0

Please fix the version in galaxy.yml before proceeding.
```

### Example 4: Major release in development (Case 3 - single-branch IN DEVELOPMENT)

User: "I'm adding a new parameter, what version should I use?"

current-release returns: `12.0.0` (IN DEVELOPMENT, from galaxy.yml: 12.0.0-dev0)

Response:

```text
Current version: 12.0.0 (IN DEVELOPMENT - MAJOR RELEASE)

→ New features: Use version_added: "12.0.0"
→ Breaking changes: Use version_added: "12.0.0" (allowed in major releases)
```

### Example 5: Patch release in development (Case 3 - SemVer violation)

User: "I'm adding a new parameter, what version should I use?"

current-release returns: `12.1.3` (IN DEVELOPMENT, from galaxy.yml: 12.1.3-dev0)

Response:

```text
Current version: 12.1.3 (IN DEVELOPMENT - PATCH RELEASE)

⚠️  SEMVER VIOLATION WARNING ⚠️

Patch releases can ONLY contain bugfixes per Semantic Versioning.

→ New features: NOT ALLOWED in patch releases
   Features require a minor release. Should galaxy.yml be 12.2.0-dev0 instead?
   If you must add features now, use version_added: "12.2.0"

→ Breaking changes: NOT ALLOWED in patch releases
   Breaking changes require a major release (13.0.0)
   Coordinate with maintainers about versioning strategy.
```

### Example 6: Released version (Case 4 - single-branch RELEASED)

User: "I'm adding a new module option, what version should I use?"

current-release returns: `9.2.0` (RELEASED, from stable-9 + git tag)

Response:

```text
Current version: 9.2.0 (RELEASED)

→ New features: Use version_added: "9.3.0" (next minor)
→ Breaking changes: Use version_added: "10.0.0" (next major)
   Coordinate with maintainers about when 10.0.0-dev0 development begins.
```

## Integration with Other Skills

- **current-release**: Used to fetch the current version
- **release**: Updates versions after releases
- **changelog-fragment**: Documents changes that include version_added tags
- **deprecation-cleanup**: May trigger major version bumps when removing deprecated features
