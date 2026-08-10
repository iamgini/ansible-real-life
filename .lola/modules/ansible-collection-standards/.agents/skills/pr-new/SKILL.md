---
name: pr-new
description: >
  Prepare and submit a pull request for the ai-forge project. Syncs with
  upstream, runs quality gates (tox -e lint), commits with proper attribution,
  then creates the PR via gh against the upstream repo. Use when the user asks
  to submit, create, or open a pull request, or says "make a PR", "open PR",
  "create PR", "new PR".
user-invocable: true
metadata:
  author: ai-forge
  version: "1.0"
---

# PR New

Create and submit a pull request for ai-forge.

## Workflow

### Step 1: Verify branch and sync with upstream

Ensure you are on a feature branch (not `main`). If changes are on `main`,
create a feature branch first:

```bash
git fetch upstream
git checkout -b <branch-name> upstream/main
```

Use a descriptive branch name (e.g., `add-release-notes-skill`,
`fix-pr-review-formatting`, `update-contributing-docs`).

If changes already exist on the current branch, cherry-pick or rebase them
onto the new branch based off `upstream/main`.

### Step 2: Run quality gates

```bash
tox -e lint
```

This **must pass cleanly on the full tree** — not just the files you changed.
If the branch has pre-existing violations from an old base, rebase onto
`upstream/main` first.

Do **not** run `prek`, `skillmark`, `markdownlint`, `yamllint`, `shellcheck`,
or `actionlint` directly — always use tox (ADR-001).

### Step 3: Squash into a single commit

Each PR must contain exactly **one commit** when pushed. If your branch
has multiple commits, squash them:

```bash
git rebase -i upstream/main
```

Mark all commits except the first as `squash` (or `fixup`). This keeps
the git history clean and makes reverts straightforward.

If the branch has already been pushed and you need to force-push after
squashing:

```bash
git push --force-with-lease
```

### Step 4: Write the commit message

Use the [Conventional Commits 1.0.0](https://www.conventionalcommits.org/)
format with imperative mood. Keep the first line under 72 characters:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types for this project:

| Type | When to use |
|------|-------------|
| `feat` | New skill, command, module, or capability |
| `fix` | Bug fix in a skill, hook, or workflow |
| `docs` | Documentation only (CONTRIBUTING, AGENTS, ADRs) |
| `ci` | CI/CD configuration (lint.yml, workflows) |
| `chore` | Maintenance tasks (manifest updates, dependency bumps) |
| `refactor` | Restructuring without changing behavior |
| `test` | Adding or updating validation scripts |

Scopes reflect project areas: `lint`, `skillmark`, `contributing`,
`manifest`, `pr-new`, `pr-review`, or a module name
(e.g., `ansible-collection-sdlc`).

Examples:

- `feat(cloud_content): add AWS resource module skill`
- `fix(manifest): add missing module to lola-market.yml`
- `ci(lint): install prek in GitHub Actions runner`
- `docs(contributing): update prerequisites for tox workflow`

Include `Co-Authored-By` in the commit footer if AI assisted with the
changes. See `CONTRIBUTING.md` for the full attribution guide.

### Step 5: Push and create the pull request

Push to your fork and create the PR against the **upstream** repository:

```bash
git push -u origin HEAD

gh pr create --repo ansible-community/ai-forge --title "conventional commit style title" --body "$(cat <<'EOF'
## Summary
- Concise description of what changed and why

## Changes
- List of notable functional changes

## Quality of life
- List any non-functional improvements bundled in this PR: skill updates,
  workflow fixes, AGENTS.md changes, ADR additions, documentation for
  contributor experience, etc.
- Omit this section entirely if there are none.

## Test plan
- [ ] `tox -e lint` passes
- [ ] Skills tested in AI assistant session (if applicable)
- [ ] Docs updated (if applicable)

Co-Authored-By: <model> <noreply@provider.com>
EOF
)"
```

The PR targets upstream's `main` branch from your fork. Return the PR URL
to the user.

**Do not hard-wrap lines** in the PR body. GitHub renders Markdown and
handles line length — hard wraps at 72 or 80 characters create ragged
paragraphs in the GitHub UI. Write each sentence or bullet as a single
long line and let the renderer wrap it.

### Including non-code changes (Quality of life)

PRs often include changes that are not directly part of the feature or fix
but improve the development workflow: skill updates, AGENTS.md tweaks,
ADR additions, documentation for contributor experience, or process fixes.

These changes belong in the **Quality of life** section of the PR body.
Use this section whenever the PR touches files like `.agents/skills/`,
`AGENTS.md`, `CONTRIBUTING.md`, `docs/adrs/`, or similar workflow
artifacts. This makes it easy for reviewers to separate functional changes
from process improvements.

If a PR contains **only** quality-of-life changes (no production code),
use `chore` or `docs` as the commit type.

### Step 6: Verify CI

After creating the PR, verify that CI runs `tox -e lint` and passes. If it
fails on issues not present locally, investigate and push fixes.

### Maintaining the PR

When updating an existing PR (adding scope, fixing review feedback, etc.),
follow this same skill — the commit format, quality gates, and PR body
template all apply equally to updates. The only differences are:

1. **Amend, don't add commits.** Squash new work into the existing single
   commit (`git commit --amend`) and force-push (`git push --force-with-lease`).
   The branch must always contain exactly one commit.
2. **Update the PR body** to reflect the full current scope — not just the
   delta. All sections (Summary, Changes, Quality of life, Test plan) must
   describe the branch as it stands now, not just the initial submission.

```bash
git commit --amend --no-edit   # or with -m to revise the message
git push --force-with-lease

gh pr edit <pr-number> --body "$(cat <<'EOF'
...updated body covering full scope...
EOF
)"
```

Do **not** create a separate skill invocation for PR updates — use `pr-new`
for both creation and maintenance.

## Checklist

Before creating the PR:

- [ ] On a feature branch (not `main`)
- [ ] Branch is based on latest `upstream/main`
- [ ] `tox -e lint` passes
- [ ] Branch squashed to a single commit
- [ ] Commit message uses Conventional Commits format (`CONTRIBUTING.md`)
- [ ] AI attribution included if applicable
- [ ] New skills are in `lola-market.yml` manifest
- [ ] PR targets `ansible-community/ai-forge` (upstream), not your fork
