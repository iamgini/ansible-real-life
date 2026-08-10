---
name: pr-contributor-review
description: >
  Review and help prepare a contributor's pull request for merge. Checks that
  the branch is up to date, quality gates pass, PR description follows the
  template, and skills conform to the agentskills.io spec. Use when the user
  asks to review a PR, check a contributor's PR, or get a PR ready for merge.
user-invocable: true
metadata:
  author: ai-forge
  version: "1.0"
---

# Review Contributor PR

Review and assist with a contributor's pull request to make it merge-ready.
Use this when reviewing someone else's PR, not when submitting your own
(use `pr-new` for that).

## Goals

- PR is **up to date with upstream main** (no merge conflicts).
- **Quality gates pass**: `tox -e lint` on the full tree.
- **PR description** follows the project template (Summary, Changes, Test plan).
- Skills conform to the [agentskills.io specification](https://agentskills.io/specification).
- New skills are in `lola-market.yml`.

## Workflow

### 1. Fetch PR metadata and diff

Use `gh pr view` to get:

- PR number, title, body, base/head refs, author.
- List of changed files and diff.

```bash
gh pr view <N> --repo ansible-community/ai-forge
gh pr diff <N> --repo ansible-community/ai-forge
```

Confirm the **base** branch (typically `main`) and which remote/branch you
would push to if making changes.

### 2. Check if the branch is up to date

- Fetch `upstream main`.
- Compare the PR's base to current `upstream/main`. If upstream has newer
  commits, the contributor's branch should be rebased before merge.

### 3. Run quality gates

Run tox on the **entire** tree, not only the changed files:

```bash
tox -e lint
```

Fix any failures before pushing to the contributor's branch. Do **not** run
`prek`, `skillmark`, or other tools directly — always use tox (ADR-001).

Do **not** push to the contributor's branch if tox fails; fix in a new
commit first.

### 4. Review skill quality

For PRs that add or modify skills, verify:

- **Frontmatter** follows the [agentskills.io spec](https://agentskills.io/specification):
  `name` matches directory, `description` includes trigger language
- **Content** is under 500 lines (move detail to `references/`)
- **No non-standard frontmatter fields** unless documented as platform
  extensions in `metadata`
- **Module is in manifest** — check `lola-market.yml`
- **Module AGENTS.md updated** with the new skill entry
- **Module README updated** with the new skill in Components section

### 5. PR description quality

If the PR body is minimal or missing structure, suggest the template from
`pr-new`:

- **Summary** — what changed and why
- **Changes** — list of notable changes
- **Test plan** — checklist of verification steps
- **Attribution** — Co-Authored-By if AI-assisted

Update the PR body if you have permission:

```bash
gh pr edit <N> --repo ansible-community/ai-forge --body-file body.md
```

### 6. Pushing to the contributor's branch

Only push if you have permission and the user has asked you to:

1. Rebase onto `upstream/main` so the PR is current.
2. Ensure `tox -e lint` passes.
3. Use `--force-with-lease` for rebased branches:
   `git push <remote> <local>:<their-branch> --force-with-lease`

### 7. Track deferred work

Any suggestion to handle something in a follow-up PR **must** be captured
as a GitHub issue immediately:

```bash
gh issue create --repo ansible-community/ai-forge \
  --title "<description from review>" \
  --body "Flagged during review of PR #N"
```

## Checklist

- [ ] Fetched PR and know base/head and remotes
- [ ] Branch is up to date with upstream main
- [ ] `tox -e lint` passes
- [ ] Skills follow agentskills.io spec (if applicable)
- [ ] New skills are in `lola-market.yml` (if applicable)
- [ ] PR description has Summary, Changes, and Test plan
- [ ] Attribution included if AI-assisted

## References

- **pr-new** skill: PR body template and commit conventions
- **CONTRIBUTING.md**: Full contribution workflow
- **AGENTS.md**: Architectural invariants and quality assurance
- **SKILL_GUIDELINES.md**: Skill authoring standards
- [agentskills.io specification](https://agentskills.io/specification)
