---
name: collection-backport-status-check
description: >-
  Use this skill when you need to check backport and patchback workflow blockers
  for Ansible collection stable branches. Detects open backport PRs and patchback
  failures that must be resolved before creating a release prep PR. Complements
  version analysis skills by focusing on process blockers. By default, checks the
  two most recent stable branches.
user-invocable: true
allowed-tools: Read Bash(command:git *) Bash(command:gh *) Bash(command:jq *) Bash(command:md5sum *) Bash(command:sed *) Bash(command:awk *) Bash(command:grep *) Bash(command:sort *) Bash(command:xargs *) Bash(command:cut *)
triggers:
  - check backport status
  - backport blockers
  - ready for prep PR
  - patchback failures
---

# Skill: collection-backport-status-check

## Purpose

Check if a collection's stable branch is **ready for a prep PR** from a workflow perspective:

- Are all backport PRs merged?
- Are all patchback failures resolved?
- Can I safely create a release prep PR now?

This skill focuses on **process blockers**, not version calculation. Use **`stable-release-analyze`** to determine if a release is needed and what version to use.

**Out of scope:** Version calculation, changelog analysis, actual release execution. For those use the **`stable-release-analyze`** and **`release`** skills.

## When to invoke

- "Are there any backport blockers for `stable-X`?"
- "Can I create a prep PR for `stable-X`?" (after version is already determined)
- "Check backport status before stable-release-prep"
- "Are there any patchback failures to resolve?"

**Note:** For "do I need a release?" or "what version?" questions, use **`stable-release-analyze`** instead.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| `collection_git_url` | **Yes** | Clone URL or absolute path to a local clone |
| `target_stable_branch` | No | e.g. `stable-11`. Defaults to checking the two most recent `stable-*` branches. |

## Prerequisites

- `git` in PATH; network if cloning
- Optional: `gh` + `jq` for backport PR checks

---

## Workflow

### Step 1 — Obtain checkout

**Local path:**

```bash
cd <collection_git_url> && git fetch --all --prune
```

**Remote URL:**

```bash
short_hash=$(echo "<collection_git_url>" | md5sum | cut -c1-8)
git clone --filter=blob:none <collection_git_url> /tmp/collection-release-readiness-${short_hash}
cd /tmp/collection-release-readiness-${short_hash}
git fetch origin 'refs/heads/stable-*:refs/remotes/origin/stable-*' 2>/dev/null || true
git fetch origin
```

Record default branch name:

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' \
  || git remote show origin | grep 'HEAD branch' | awk '{print $NF}'
```

### Step 2 — Resolve upstream remote and repo

Use **`get-upstream-info`** to determine:

- `UPSTREAM_REMOTE` — canonical remote name (`upstream` in fork workflows, `origin` in direct clones)
- `UPSTREAM_PATH` — `org/repo` for `gh` commands (e.g. `ansible-collections/amazon.aws`)

Use `UPSTREAM_REMOTE` in all `git` commands, `UPSTREAM_PATH` in all `gh` commands.

### Step 3 — Find target stable branch(es)

```bash
git branch -r \
  | grep -E "${UPSTREAM_REMOTE}/stable-[0-9]+$" \
  | sed "s|^[[:space:]]*${UPSTREAM_REMOTE}/||" \
  | sort -V
```

If `target_stable_branch` is given, use only that branch. Otherwise:

- Select the **two most recent** stable branches (e.g., `stable-11` and `stable-10`)
- Check both branches for release readiness
- Team policy expects patch fixes to be assessed for multiple supported stable lines

Extract major number `N` for each branch (e.g. `stable-11` → `N=11`).

If no `stable-*` branches exist, **STOP** — collection does not use stable branches.

---

### Backport Workflow Checks

**Prerequisites:** This skill assumes you've already determined a release is needed (use `stable-release-analyze` for that).

Run both checks below. Any blocker means **NOT READY** for prep PR.

#### Check A — Open backport PRs (requires `gh` + `jq`)

```bash
# Open patchback-created PRs targeting stable-N not yet merged → BLOCKER
gh pr list --repo UPSTREAM_PATH \
  --base <target_stable_branch> \
  --state open \
  --json number,title,url,labels \
  --limit 20 \
  | jq '[.[] | select(.labels | map(.name) | contains(["backport-N"]))]'
```

**Also check for PRs with backport labels that target other branches** (these may need to be merged to stable-N as well):

```bash
gh pr list --repo UPSTREAM_PATH \
  --state open \
  --json number,title,url,labels \
  --limit 50 \
  | jq '.[] | select(.labels | map(.name) | contains(["backport-N"]))'
```

**Note:** The jq filter `map(.name) | contains(["backport-N"])` correctly checks if the array of label names contains the backport label.
The simpler `.labels[].name == "backport-N"` syntax does not work reliably with jq's select function.

Open backport PRs → **BLOCKER** — merge them before creating the prep PR.

#### Check B — Patchback failures on main-branch PRs (requires `gh` + `jq`)

```bash
# Get the last tag on the stable branch
last_tag=$(git describe --tags --abbrev=0 ${UPSTREAM_REMOTE}/<target_stable_branch> 2>/dev/null)

# Get the actual tag creation date from GitHub API (not git commit date)
if [ -n "$last_tag" ]; then
  last_tag_date=$(gh api repos/${UPSTREAM_PATH}/git/refs/tags/${last_tag} 2>/dev/null \
    | jq -r '.object.url' \
    | xargs gh api 2>/dev/null \
    | jq -r '.tagger.date // .committer.date' \
    | cut -d'T' -f1)
else
  last_tag_date="2000-01-01"
fi
last_tag_date=${last_tag_date:-"2000-01-01"}

# Merged main PRs where patchback failed for stable-N since last tag → BLOCKER
gh pr list --repo UPSTREAM_PATH \
  --base <default_branch> \
  --label "backport-N" \
  --label "backport_failed" \
  --state closed \
  --json number,title,url,mergedAt \
  --limit 50 \
  | jq --arg since "$last_tag_date" '[.[] | select(.mergedAt != null and .mergedAt > $since)]'
```

**Important:** Use GitHub API to get the **actual tag creation date** (when the tag was pushed to GitHub), not the git commit date.
This ensures accurate scoping of the backport failure check to the current release cycle.
The Galaxy/Automation Hub publish date may lag by hours or days after the tag is created.

Patchback failures → **BLOCKER** — manually cherry-pick the change to `stable-N` before the prep PR:

```bash
git fetch upstream
git checkout -b <fix-branch> upstream/<target_stable_branch>
git cherry-pick -x <sha>          # use -m 1 if merge commit
```

If `gh` / `jq` unavailable: mark both checks as **SKIPPED** — recommend manually reviewing open PRs on `stable-N` and checking for `backport_failed` labels.

---

### Final output

When checking a single branch:

```text
## Backport Status: <target_stable_branch>

### Ready for prep PR?
READY | NOT READY | SKIPPED (gh/jq unavailable)

### Blockers (if NOT READY)
- Open backport PRs: <count> (<list PR numbers>)
- Patchback failures: <count> (<list PR numbers>)

### Context
- Last tag: <tag_name> (created <YYYY-MM-DD> from GitHub API, ~N weeks/months ago)
- Open backport PRs targeting this branch: <count>
- Backport-labeled PRs needing manual cherry-pick: <count>

### Next steps
If READY:
  - Proceed with release prep PR creation
  - Use `stable-release-analyze` if you need version calculation

If NOT READY:
  - Merge open backport PRs first
  - Manually cherry-pick patchback failures:
    git fetch upstream
    git checkout -b fix-backport upstream/<target_stable_branch>
    git cherry-pick -x <sha>  # use -m 1 for merge commits
  - Re-run this check after resolving blockers
```

When checking multiple branches (default behavior), repeat the above structure for each branch, ordered from newest to oldest (e.g., `stable-11` then `stable-10`).

**Important:** Always report tag dates using the actual GitHub tag creation date from the API, and include a human-readable time reference (e.g., "~2 weeks ago", "~3 months ago") to provide context.

---

## Integration

**Recommended workflow:**

1. **`stable-release-analyze`** — Determine if a release is needed and calculate the version
2. **`collection-backport-status-check`** (this skill) — Check for backport/patchback blockers
3. **`stable-release-prep`** — Create the prep PR (once blockers are cleared)
4. **`release`** — Execute the full release after prep PR is merged

**Dependencies:**

- **`get-upstream-info`** — Required for upstream remote resolution

## Notes

- **Scope**: This skill ONLY checks backport/patchback workflow blockers. It does NOT determine if a release is needed or calculate versions — use `stable-release-analyze` for that.
- **Complementary skills**: Run `stable-release-analyze` first to determine version, then use this skill to check for process blockers before creating the prep PR.
- `hashicorp.vault` canonical repo is `ansible-automation-platform/hashicorp.vault` — `get-upstream-info` resolves this.
- Release manager decisions override this skill's output; it **informs**, it does **not** approve.
- **Tag dates**: Always use GitHub API (`gh api repos/<org>/<repo>/git/refs/tags/<tag>`) to get actual tag creation dates, not `git log` which returns commit dates.
  Verify against GitHub tags page (`https://github.com/<org>/<repo>/tags`) if in doubt.
- **Backport PR checks**: Check both PRs targeting the stable branch AND PRs with backport labels across all open PRs (some may target main but need to be backported).
- **Multi-branch default**: By default, checks the two most recent stable branches (e.g., `stable-11` and `stable-10`). Override with `target_stable_branch` to check only one.
- **Graceful degradation**: If `gh` or `jq` are unavailable, the skill reports SKIPPED and recommends manual PR review.
