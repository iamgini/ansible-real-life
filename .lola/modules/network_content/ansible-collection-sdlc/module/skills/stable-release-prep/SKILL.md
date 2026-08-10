---
name: stable-release-prep
description: >
  Prepares an Ansible collection release on a stable branch. Use this skill when
  stable-release-analyze has identified a version and you need to create a prep
  branch, update galaxy.yml, generate changelog entries, and run
  antsibull-changelog release.
user-invocable: false
---

# Skill: stable-release-prep

## Purpose

Prepare a release branch for an Ansible collection on a stable branch workflow.
Creates `prep_vX.Y.Z` branch, updates galaxy.yml, generates release summary fragment,
and runs antsibull-changelog to produce CHANGELOG.rst.

## When to Invoke

TRIGGER when:

- User asks to "prepare release" after analyzing stable branches
- After `/release-analyze` identifies a pending release
- User requests to "create release branch" or "update version"
- Before running quality checks (lint/sanity) for a release

DO NOT TRIGGER when:

- Performing full release (use `release` skill instead)
- Just analyzing (use `release-analyze` skill instead)
- Reviewing a PR (use `pr-review` skill instead)

## Inputs

- `collection`: collection name (e.g., `amazon.aws`) or path. Defaults to current directory.
- `version`: target release version (e.g., `1.0.1`). Required.
- `branch`: stable branch to release from (e.g., `stable-1`). Required.
- `summary` (optional): custom release summary text
- `release-date` (optional): custom release date in YYYY-MM-DD format. Defaults to today's date.

## Release Date Parameter

The `--release-date` parameter allows you to set a custom date in `changelogs/changelog.yaml`:

**Use cases:**

- **Future-dated releases**: Preparing today but scheduling for a specific future date
- **Backdating**: Recreating/fixing a release and preserving the original date
- **Coordinated releases**: Multiple collections releasing on the same date
- **Release freeze scenarios**: Preparing before a freeze but dating for after

**Examples:**

```bash
# Use today's date (default)
/stable-release-prep --version 1.0.1 --branch stable-1

# Future release (prepare today, release June 15)
/stable-release-prep --version 1.0.1 --branch stable-1 --release-date 2026-06-15

# Preserve original date when recreating a release
/stable-release-prep --version 1.0.1 --branch stable-1 --release-date 2026-04-22

# Coordinated release across collections
/stable-release-prep --version 2.0.0 --branch stable-2 --release-date 2026-07-01
```

## Prerequisites

- Python 3.8+
- antsibull-changelog (auto-installed in virtual environment)
- ansible-core (auto-installed in virtual environment)
- Git repository with configured `upstream` remote
- Clean working tree on stable branch

## Virtual Environment Management

**CRITICAL**: This skill ALWAYS creates and uses a virtual environment.

The virtual environment setup is automatic and includes:

- antsibull-changelog (for changelog generation)
- ansible-core (provides ansible-doc for changelog)
- PyYAML (for fragment parsing)

## Release Preparation Steps

### Step 1 — Setup virtual environment and install dependencies

```bash
cd SKILL_DIR && \
python3 -m venv .venv 2>/dev/null || true && \
source .venv/bin/activate && \
if command -v uv &> /dev/null; then
  uv pip install antsibull-changelog ansible-core pyyaml
else
  pip install --quiet --upgrade pip && \
  pip install --quiet antsibull-changelog ansible-core pyyaml
fi
```

Replace `SKILL_DIR` with the directory containing this skill's scripts folder.

### Step 2 — Determine collection path and sync base branch

If collection name provided (e.g., `amazon.aws`):

```bash
NAMESPACE=$(echo "COLLECTION" | cut -d. -f1)
NAME=$(echo "COLLECTION" | cut -d. -f2)
COLLECTION_PATH="${ANSIBLE_COLLECTIONS_PATH:-$HOME/dev/collections/ansible_collections}/$NAMESPACE/$NAME"
```

If in collection directory:

```bash
COLLECTION_PATH=$(pwd)
[ -f "galaxy.yml" ] || { echo "Error: Not an Ansible collection"; exit 2; }
```

Sync with upstream:

```bash
cd "$COLLECTION_PATH" && \
git checkout BRANCH && \
git pull upstream BRANCH
```

### Step 3 — Validate parameters

Extract current version from galaxy.yml:

```bash
CURRENT_VERSION=$(grep '^version:' galaxy.yml | awk '{print $2}' | tr -d '"')
```

Verify new version is higher than current:

```bash
# Compare versions - VERSION must be > CURRENT_VERSION
# If not, exit with error
```

### Step 4 — Create prep branch

```bash
git checkout -b prep_vVERSION
```

Example: `prep_v1.0.1`

### Step 5 — Update galaxy.yml version

Use the Edit tool or sed to update the version field:

```bash
sed -i.bak "s/^version: .*/version: VERSION/" galaxy.yml
```

Or use the update-galaxy-version.py script:

```bash
cd SKILL_DIR && source .venv/bin/activate && \
./scripts/update-galaxy-version.py COLLECTION_PATH VERSION
```

### Step 6 — Create release summary fragment

**CRITICAL**: Module and plugin names MUST be wrapped in double backticks (\`\`name\`\`).

**CRITICAL**: Use `>` (folded block scalar), NOT `|` (literal block scalar) for release_summary to avoid blank lines in changelog.yaml.

Create `changelogs/fragments/VERSION.yml`:

```yaml
release_summary: >-
  This patch release includes bugfixes for the ``module_name`` module
  and improvements to the ``other_module`` module for better error handling.
```

Auto-generation logic:

1. Parse existing fragments to understand changes
2. Run `git diff LAST_TAG..HEAD --stat` to detect modified files
3. Extract module names from `plugins/modules/` changes
4. Generate appropriate summary based on fragment types:
   - Only bugfixes → "This patch release includes bugfixes for..."
   - Minor changes → "This minor release adds new features to..."
   - Breaking changes → "This major release includes breaking changes to..."

Use the generate-release-summary.py script:

```bash
cd SKILL_DIR && source .venv/bin/activate && \
./scripts/generate-release-summary.py COLLECTION_PATH VERSION
```

### Step 7 — Run antsibull-changelog release

```bash
cd COLLECTION_PATH && \
source SKILL_DIR/.venv/bin/activate && \
if [ -n "$RELEASE_DATE" ]; then
  antsibull-changelog release --version VERSION --date "$RELEASE_DATE"
else
  antsibull-changelog release --version VERSION
fi
```

**Parameters:**

- `--version VERSION`: Required - the version to release
- `--date YYYY-MM-DD`: Optional - custom release date (defaults to today)

This will:

- Process all fragment YAML files in `changelogs/fragments/`
- Generate/update `CHANGELOG.rst`
- Update `changelogs/changelog.yaml` (with custom date if provided)
- Delete processed fragment files (except VERSION.yml release summary)

### Step 8 — Verify and fix changelog generation

Check that CHANGELOG.rst was updated:

```bash
grep -q "vVERSION" CHANGELOG.rst || {
  echo "Error: CHANGELOG.rst not updated";
  exit 1;
}
```

Check that changelog.yaml has new release entry:

```bash
grep -q "VERSION:" changelogs/changelog.yaml || {
  echo "Error: changelog.yaml not updated";
  exit 1;
}
```

**CRITICAL**: Fix common antsibull-changelog bugs. See
[references/changelog-validation.md](references/changelog-validation.md) for indentation
fixes, line-length limits, and `.plugin-cache.yaml` cleanup.

### Step 9 — Display changes and next steps

Show what was changed:

```bash
git status --short
git diff --stat
```

**CONFIRM:** Present the changes to the user:

- galaxy.yml version update
- New release summary fragment
- Updated CHANGELOG.rst
- Updated changelog.yaml
- Deleted fragment files

Ask the user to confirm the changes look correct before proceeding.

Provide next steps:

1. Review changes: `git diff`
2. Generate docs: `/docs-generate`
3. Run quality checks: `/lint` and `/sanity`
4. Commit and push: `git add -A && git commit -m "Release vVERSION"`

## Release Summary Formatting Rules

See [references/release-summary-formatting.md](references/release-summary-formatting.md) for
backtick formatting, block scalar guidance, and module name detection.

## Configuration

Optional environment variables (read from `~/.ansible-release.conf` if present):

```bash
export ANSIBLE_COLLECTIONS_PATH="~/dev/collections/ansible_collections"

# Remote name for canonical repository (default: "upstream")
# Set to "origin" if you use different remote naming convention
export REMOTE_UPSTREAM="upstream"
```

**Note on remote naming**: This skill assumes the standard fork-and-pull workflow where:

- `upstream` = canonical repository (e.g., ansible-collections/amazon.aws)
- `origin` = your fork

If you use a different convention (e.g., `origin` for canonical, your fork as a different remote), set `REMOTE_UPSTREAM="origin"`.

## Troubleshooting

### "antsibull-changelog command not found"

The venv setup should prevent this. If it occurs:

```bash
cd SKILL_DIR && source .venv/bin/activate && \
pip install antsibull-changelog ansible-core
```

### "Version must be higher than current version"

Check current version:

```bash
grep version galaxy.yml
```

Ensure target version is higher: 1.0.1 > 1.0.0 ✓

### "No changelog fragments found"

Ensure fragments exist:

```bash
ls changelogs/fragments/*.yml
```

At least one non-.keep fragment must exist.

### "antsibull-changelog fails"

Verify changelogs/config.yaml exists:

```bash
cat changelogs/config.yaml
```

Validate fragment YAML syntax:

```bash
yamllint changelogs/fragments/*.yml
```

## Script Files

This skill includes Python scripts in `scripts/`:

- `generate-release-summary.py` - Auto-generate release summary with proper backticks
- `update-galaxy-version.py` - Update galaxy.yml version field

Both scripts support virtual environment activation and include dependency checks.

## Integration

This skill integrates with:

- `release-analyze` - Analyzes pending releases (run before this)
- `docs-generate` - Generates documentation (run after this)
- `lint` - Runs linters (run after this)
- `sanity` - Runs sanity tests (run after this)

## Exit Codes

- `0`: Release prep successful
- `1`: Preparation failed (git errors, validation failures)
- `2`: Invalid parameters or configuration

## Output Format

Present each step as a numbered section:

1. What the step does
2. The command(s) to run
3. What to verify before proceeding

Show final status with:

- ✅ Branch created: `prep_vVERSION`
- ✅ galaxy.yml updated: `CURRENT_VERSION` → `VERSION`
- ✅ Release summary created
- ✅ CHANGELOG generated

List changed files and provide clear next steps.
