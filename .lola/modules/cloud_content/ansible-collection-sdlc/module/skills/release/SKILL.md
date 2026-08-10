---
name: release
description: >-
  Guides the release of an Ansible collection following the
  upstream process (without release branches). Automatically
  determines the next version from changelog fragments. Outputs
  step-by-step instructions with commands for changelog generation,
  release PR, tagging, Galaxy publication, version bump, and GitHub
  release. Use when asked to release, publish, or tag a new
  collection version.
user-invocable: true
---

# Skill: release

## Purpose

Guide the release of an Ansible collection. This skill is collection-generic —
it derives namespace, name, and current version from `galaxy.yml`,
and automatically determines the next version from changelog fragment categories.

## When to Invoke

TRIGGER when:

- A user asks to release, publish, or tag a new collection version
- A user asks about the release process or release checklist

DO NOT TRIGGER when:

- Reviewing a PR (use `pr-review` skill instead)
- Running tests (use `run-tests` skill instead)
- General changelog or versioning questions unrelated to performing a release

## Inputs

- `version` (optional): the target release version, e.g. `2.1.0`. If not provided, the version is automatically determined from changelog fragments (see Step 2).

## Prerequisites

- `antsibull-changelog` installed (`pip install antsibull-changelog`)
- `gh` CLI installed and authenticated
- Push access to the upstream remote
- Git remote named `upstream` configured to point to the canonical repository

## Human Confirmation Gates

**Do not proceed past a confirmation gate without explicit human approval.**
Present the relevant information and wait for the human to confirm
before continuing to the next step. Gates are marked with **CONFIRM** below.

## Release Steps

### Step 1 — Determine repository information

Use the `get-upstream-info` helper skill to determine the upstream repository.

This returns:

- `UPSTREAM_ORG`: GitHub organisation (e.g., `ansible-collections`)
- `UPSTREAM_REPO`: Repository name (e.g., `amazon.aws`)
- `UPSTREAM_PATH`: Full path (e.g., `ansible-collections/amazon.aws`)

Cache these values for use in subsequent steps.

### Step 2 — Read collection context and determine version

Extract collection identity from `galaxy.yml`:

```bash
grep -E '^(namespace|name|version):' galaxy.yml
```

Use the extracted values as `NAMESPACE`, `COLLECTION`, and `CURRENT_VERSION` in all subsequent steps.

#### Determine next version

If the user did not provide a target version, determine it automatically:

1. Scan all YAML files in `changelogs/fragments/` and collect the top-level keys (category names) from each file.
2. Determine the version bump using the highest-severity category found:

| Bump  | Fragment categories                                      |
|-------|----------------------------------------------------------|
| Major | `breaking_changes`, `removed_features`, `major_changes`  |
| Minor | `minor_changes`, `deprecated_features`                   |
| Patch | `bugfixes`, `security_fixes`, `known_issues`, `trivial`  |

1. Apply the bump to `CURRENT_VERSION` (e.g. `2.0.0` + minor -> `2.1.0`).
   When bumping major, reset minor and patch to 0. When bumping minor, reset patch to 0.

Use the resulting version as `VERSION`.

**CONFIRM:** Present the extracted `NAMESPACE`, `COLLECTION`, `CURRENT_VERSION`,
the detected fragment categories, the determined bump type, and the resulting `VERSION`
to the human. Ask them to confirm these values are correct before proceeding.
The human may override the version at this point.

### Step 3 — Pre-flight checks

```bash
git status
git checkout main
git pull --rebase upstream main
```

Verify before continuing:

- Working tree is clean (no uncommitted changes)
- Changelog fragments exist: `ls changelogs/fragments/`

### Step 4 — Security scan

Run security scan before release to catch vulnerabilities:

Invoke the `security-scan` skill to check for:

- Vulnerable Python dependencies
- Compromised GitHub Actions versions
- Hardcoded secrets in code

**CONFIRM:** Review any security findings. Critical or high severity issues should block the release.
Resolve all critical issues before proceeding.

### Step 5 — Update galaxy.yml version

If `CURRENT_VERSION` in `galaxy.yml` does not match `VERSION`, update it:

```bash
sed -i "s/^version: .*/version: VERSION/" galaxy.yml
```

### Step 6 — Create release branch

```bash
git checkout -b release_VERSION
```

### Step 7 — Create release summary fragment (BEFORE antsibull-changelog)

**CRITICAL**: The release summary fragment MUST be created BEFORE running `antsibull-changelog release`.
This is the required order per the [cloud-content-handbook release process](https://github.com/ansible-collections/cloud-content-handbook/blob/main/Releases/release_collections.md):

1. Create `changelogs/fragments/<version>.yml` with `release_summary`
2. Then run `antsibull-changelog release`

If you run antsibull-changelog first, the release summary will be missing from the generated changelog.

#### Generate release summary content

Determine the release type from `VERSION` and generate a meaningful summary:

1. **Analyze the changelog fragments** in `changelogs/fragments/` to understand what's included
2. **Identify key modules/plugins affected** by checking which files were changed:

   ```bash
   git diff $(git describe --tags --abbrev=0)..HEAD --stat | grep "plugins/modules/"
   ```

3. **Draft a summary** that describes the actual changes, not just the release type

**Release summary templates** (starting point, customize based on actual changes):

- **Major** (`X.0.0`): `This major release of the ``NAMESPACE.COLLECTION`` collection includes breaking changes, new features, and improvements.`
- **Minor** (`X.Y.0`): `This minor release of the ``NAMESPACE.COLLECTION`` collection includes new features and improvements.`
- **Patch** (`X.Y.Z`): `This patch release of the ``NAMESPACE.COLLECTION`` collection includes bugfixes and minor improvements.`

**Formatting rules:**

- Use `>-` (folded block scalar) to avoid blank lines in the output
- Wrap all module/plugin names in double backticks: ``module_name``
- Be specific about what changed when possible

**CONFIRM:** Present the suggested release summary and the list of changelog fragments that will be included. Ask the human to approve or edit the text before writing the fragment.

#### Create the release summary fragment

```bash
cat > changelogs/fragments/VERSION.yml << 'EOF'
release_summary: >-
  This is a <major/minor/patch> release of the ``NAMESPACE.COLLECTION`` collection.
  <Add specific details about key changes, affected modules, or notable fixes.>
EOF
```

Verify the fragment was created:

```bash
cat changelogs/fragments/VERSION.yml
ls changelogs/fragments/
```

### Step 8 — Run antsibull-changelog release

**Only run this AFTER the release summary fragment exists.**

```bash
antsibull-changelog release --reload-plugins
```

This will:

- Process all fragment YAML files in `changelogs/fragments/`
- Include the release summary in the generated changelog
- Update `CHANGELOG.rst` and `changelogs/changelog.yaml`
- Delete processed fragment files

#### Verify version ordering in changelog.yaml

**CRITICAL**: Versions in `changelogs/changelog.yaml` must be ordered **semantically (numerically)**, NOT alphabetically.

Alphabetical sorting incorrectly places version `10.x` before `2.x` (since "1" < "2" as strings).
The correct order is: `1.0.0` → `2.0.0` → ... → `9.0.0` → `10.0.0` → `11.0.0`

After running `antsibull-changelog release`, check the `releases:` section in `changelogs/changelog.yaml`:

```yaml
# WRONG (alphabetical):
releases:
  1.0.0: ...
  10.0.0: ...   # ❌ Should come after 9.0.0
  2.0.0: ...

# CORRECT (semantic):
releases:
  1.0.0: ...
  2.0.0: ...
  ...
  9.0.0: ...
  10.0.0: ...  # ✅ Correctly after 9.0.0
```

If versions are misordered, edit `changelogs/changelog.yaml` to fix the order, then regenerate:

```bash
antsibull-changelog generate
```

**CONFIRM:** Show the human the generated `CHANGELOG.rst` diff and ask them to confirm the content is correct before continuing.

### Step 9 — Commit and push release branch

```bash
git add -A
git commit -m "Release VERSION"
git push origin release_VERSION
```

### Step 10 — Create pull request

```bash
gh pr create --repo UPSTREAM_PATH --title "Release VERSION" --body "Release VERSION of NAMESPACE.COLLECTION."
```

**CONFIRM:** Wait for the human to confirm that CI has passed and the PR has been reviewed and merged before continuing.

### Step 11 — Update local main

After the PR is merged:

```bash
git checkout main
git pull --rebase upstream main
```

### Step 12 — Tag and push

**CONFIRM:** Ask the human to confirm before creating and pushing the tag. This action is irreversible.

```bash
git tag -a VERSION -m "NAMESPACE.COLLECTION: VERSION"
git push upstream VERSION
```

### Step 13 — Create GitHub release

```bash
gh release create VERSION --repo UPSTREAM_PATH --title "VERSION" --notes "See [CHANGELOG.rst](https://github.com/UPSTREAM_PATH/blob/main/CHANGELOG.rst) for details."
```

### Step 14 — Bullhorn release announcement

Generate and present the following announcement text for the user to post
in the [Bullhorn newsletter](https://forum.ansible.com/c/news/bullhorn/17)
after the user ensures the release has appeared on Ansible Galaxy:

```
The [NAMESPACE.COLLECTION](https://galaxy.ansible.com/ui/repo/published/NAMESPACE/COLLECTION/) collection
version [VERSION](https://github.com/UPSTREAM_PATH/blob/main/CHANGELOG.rst#vVERSION) has been released!
```

Replace `NAMESPACE`, `COLLECTION`, `VERSION`, and `UPSTREAM_PATH` with the actual values. In the anchor fragment (`#vVERSION`), replace dots with hyphens (e.g. `#v2-1-0` for version `2.1.0`).

## Output Format

Present each step as a numbered section containing:

1. What the step does (one line)
2. The exact command(s) to run (with placeholders replaced by actual values)
3. What to verify before proceeding to the next step

## Integration with Other Skills

- **get-upstream-info**: Used in Step 1 to determine upstream repository path for gh CLI commands (`gh pr create`, `gh release create`)
- **security-scan**: Used in Step 4 to check for vulnerabilities before release
- **current-release**: Not currently used; release skill reads galaxy.yml directly to get namespace, name, and version together
- **next-release**: Not used; release skill has unique logic to scan changelog fragments and determine bump type for actual releases (next-release is for version_added tags)
