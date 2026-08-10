---
name: stable-release-analyze
description: >-
  Analyzes Ansible collection stable branches to determine pending releases
  and calculate appropriate SemVer versions. Checks for unreleased commits,
  analyzes changelog fragments, and recommends next version. Use when asked
  to check which collections need releases or what version to release.
user-invocable: false
---

# Skill: stable-release-analyze

## Purpose

Analyze Ansible collection stable branches for pending releases. This skill:

- Detects all stable-X branches
- Counts unreleased commits since last tag
- Analyzes changelog fragments to determine SemVer impact (MAJOR/MINOR/PATCH)
- Calculates the next appropriate version number
- Generates release recommendations

## When to Invoke

TRIGGER when:

- A user asks to analyze pending releases
- A user asks "which collections need releases?"
- A user asks "what version should I release?"
- Beginning a release workflow (before release-prep)
- Planning release schedules

DO NOT TRIGGER when:

- Actually performing a release (use `release-prep` skill instead)
- Reviewing a PR (use `pr-review` skill instead)
- Running tests (use `run-tests` skill instead)

## Inputs

- `collection` (optional): collection name (e.g., `amazon.aws`) or path. Defaults to current directory.
- `--all` (optional): analyze all collections in ANSIBLE_COLLECTIONS_PATH

## Prerequisites

- Python 3.8+
- PyYAML library (auto-installed in virtual environment)
- Git repository with configured `upstream` remote
- Stable branches following `stable-X` naming convention

## Virtual Environment Management

**CRITICAL**: This skill ALWAYS creates and uses a virtual environment to ensure:

- ✅ Consistent dependency versions (PyYAML)
- ✅ No global package pollution
- ✅ Cross-platform compatibility
- ✅ Isolation from system Python

The virtual environment is automatically created in the skill directory and reused across invocations.

## Release Analysis Steps

### Step 1 — Setup virtual environment and install dependencies

**ALWAYS run this first** to ensure PyYAML is available:

```bash
cd SKILL_DIR && \
python3 -m venv .venv 2>/dev/null || true && \
source .venv/bin/activate && \
if command -v uv &> /dev/null; then
  uv pip install pyyaml
else
  pip install --quiet --upgrade pip && pip install --quiet pyyaml
fi
```

Replace `SKILL_DIR` with the directory containing this skill's scripts folder.

**Verification**: Confirm Python packages are installed:

```bash
source .venv/bin/activate && python3 -c "import yaml; print('PyYAML OK')"
```

### Step 2 — Determine collection path

If collection name provided (e.g., `amazon.aws`):

```bash
NAMESPACE=$(echo "COLLECTION" | cut -d. -f1)
NAME=$(echo "COLLECTION" | cut -d. -f2)
COLLECTION_PATH="${ANSIBLE_COLLECTIONS_PATH:-$HOME/dev/collections/ansible_collections}/$NAMESPACE/$NAME"
```

If in collection directory:

```bash
COLLECTION_PATH=$(pwd)
# Verify it's a collection
[ -f "galaxy.yml" ] || { echo "Error: Not an Ansible collection"; exit 2; }
```

### Step 3 — Run analysis script

Execute the Python analysis script with venv activated:

```bash
cd SKILL_DIR && \
source .venv/bin/activate && \
./scripts/analyze-collection.py COLLECTION_PATH
```

The script will:

1. Read `galaxy.yml` to extract collection metadata
2. Fetch and sync with upstream remote
3. Detect all `stable-X` branches
4. For each stable branch:
   - Checkout and sync
   - Find last release tag
   - Count commits since tag
   - Analyze changelog fragments in `changelogs/fragments/`
   - Determine SemVer impact (MAJOR/MINOR/PATCH)
   - Calculate next version number
5. Generate summary report

### Step 4 — Interpret results

The script outputs color-coded results:

#### ✅ Green: RELEASE NEEDED

```
✅ stable-1: 1.0.0 → 1.0.1 (PATCH)
   Commits: 14, Fragments: 1
   20260122-devopsguru-notification_channel.yml
```

Action: Proceed with `/release-prep --version 1.0.1 --branch stable-1`

#### ✓ Blue: UP TO DATE

```
✓ stable-3: Up to date (3.5.0)
```

Action: No release needed

#### ⚠️ Yellow: COMMITS WITHOUT FRAGMENTS

```
⚠️ stable-6: 8 commits but no changelog fragments
```

Action: Add changelog fragments before releasing

#### ❌ Red: ERROR

```
❌ stable-5: Failed to checkout branch
```

Action: Investigate git/branch issues

### Step 5 — Analyze all collections (optional)

If `--all` flag provided, iterate through collections:

```bash
cd SKILL_DIR && source .venv/bin/activate

for NAMESPACE_DIR in ${ANSIBLE_COLLECTIONS_PATH}/*/*; do
  if [ -f "$NAMESPACE_DIR/galaxy.yml" ]; then
    COLLECTION=$(basename $(dirname $NAMESPACE_DIR)).$(basename $NAMESPACE_DIR)
    echo "Analyzing $COLLECTION..."
    ./scripts/analyze-collection.py "$NAMESPACE_DIR"
  fi
done
```

## SemVer Calculation Rules

Based on Ansible changelog fragment types:

| Fragment Type         | Impact     | Version Bump | Example           |
|-----------------------|------------|--------------|-------------------|
| `breaking_changes`    | **MAJOR**  | X.0.0        | 1.2.3 → 2.0.0     |
| `removed_features`    | **MAJOR**  | X.0.0        | 1.2.3 → 2.0.0     |
| `major_changes`       | **MINOR**  | x.Y.0        | 1.2.3 → 1.3.0     |
| `minor_changes`       | **MINOR**  | x.Y.0        | 1.2.3 → 1.3.0     |
| `deprecated_features` | **MINOR**  | x.Y.0        | 1.2.3 → 1.3.0     |
| `bugfixes`            | **PATCH**  | x.y.Z        | 1.2.3 → 1.2.4     |
| `security_fixes`      | **PATCH**  | x.y.Z        | 1.2.3 → 1.2.4     |
| `trivial`             | **PATCH**  | x.y.Z        | 1.2.3 → 1.2.4     |

**Rule**: The highest impact across all fragments determines the bump.

## Output Example

```
Collection: amazon.ai
Current version: 1.0.0

Stable branches found: 1

Checking stable-1...
✅ stable-1: 1.0.0 → 1.0.1 (PATCH)
   Commits: 14, Fragments: 1
   20260122-devopsguru-notification_channel.yml: bugfixes (impact: PATCH)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary: 1 release(s) needed
```

## Configuration

Optional environment variables (read from `~/.ansible-release.conf` if present):

```bash
export ANSIBLE_COLLECTIONS_PATH="~/dev/collections/ansible_collections"
export UPSTREAM_ORG="ansible-collections"

# Remote name for canonical repository (default: "upstream")
# Set to "origin" if you use different remote naming convention
export REMOTE_UPSTREAM="upstream"
```

**Note on remote naming**: This skill assumes the standard fork-and-pull workflow where:

- `upstream` = canonical repository (e.g., ansible-collections/amazon.aws)
- `origin` = your fork

If you use a different convention (e.g., `origin` for canonical, your fork as a different remote), set `REMOTE_UPSTREAM="origin"`.

## Troubleshooting

### "PyYAML is required but not installed"

The venv setup should prevent this, but if it occurs:

```bash
cd SKILL_DIR && source .venv/bin/activate && pip install pyyaml
```

### "Remote 'upstream' not found"

```bash
cd COLLECTION_PATH
git remote add upstream https://github.com/ansible-collections/COLLECTION.git
git fetch upstream --tags
```

### "No stable branches found"

Verify the collection uses `stable-X` branch naming:

```bash
git branch -a | grep stable
```

### "Cannot determine collection path"

Ensure you're either:

1. In a collection directory with `galaxy.yml`, OR
2. Providing a valid collection name like `amazon.aws`

## Script Files

This skill includes the following Python scripts in `scripts/`:

- `analyze-collection.py` - Main analysis script (entry point)
- `calculate-version.py` - SemVer calculation logic
- `check-branch.py` - Branch analysis logic
- `setup-collection-repo.py` - Repository setup and cloning

All scripts include built-in dependency checks with helpful error messages.

## Integration

This skill integrates with:

- `release-prep` - Prepares release after analysis determines version
- `release` - Full release orchestrator (uses this for analysis step)

## Exit Codes

- `0`: Analysis complete, results displayed
- `1`: Analysis failed (git errors, missing dependencies)
- `2`: Invalid collection or configuration

## Implementation Notes

- Always activate venv before running scripts
- Use `uv pip install` for speed when available (fallback to pip)
- Scripts handle git operations internally
- Color output uses ANSI codes (disable with `NO_COLOR=1`)
- Safe to run multiple times (read-only operations)
