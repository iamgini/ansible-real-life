---
name: check-skill-spec
description: >
  Compare the agentskills.io specification against this project's extended
  frontmatter allowlist to determine whether the custom validation hook
  (scripts/check_skill_frontmatter.py) is still needed. Use this skill when
  checking if the upstream spec has adopted the extended fields, when planning
  to remove the custom hook, or when a new spec release is announced.
user-invocable: true
metadata:
  author: ai-forge
  version: "1.0"
---

# Check Skill Spec Alignment

Determine whether the custom frontmatter validation hook can be retired
in favor of skillmark's built-in E030 rule.

## Context

This project uses a custom pre-commit hook (`scripts/check_skill_frontmatter.py`)
that validates SKILL.md frontmatter against the agentskills.io spec **plus**
extended fields that Claude Code and VS Code support but the spec has not yet
adopted. Skillmark's E030 is disabled in `.skillmark.toml` because it rejects
these fields.

The extended fields are:

| Field | Purpose | Tracking |
|-------|---------|----------|
| `user-invocable` | Controls `/` menu visibility | [agentskills#105](https://github.com/agentskills/agentskills/issues/105) |
| `argument-hint` | Autocomplete hint for arguments | [agentskills#105](https://github.com/agentskills/agentskills/issues/105) |
| `disable-model-invocation` | Prevents agent auto-triggering | [agentskills#105](https://github.com/agentskills/agentskills/issues/105) |
| `triggers` | Invocation phrases for discovery | [agentskills#105](https://github.com/agentskills/agentskills/issues/105) |

## Workflow

### Step 1: Fetch the current spec

Read the upstream specification:

```bash
curl -sL https://raw.githubusercontent.com/agentskills/agentskills/main/docs/specification.mdx
```

Extract the frontmatter field table from the spec. Look for the `### Frontmatter`
section and the table listing `Field | Required | Constraints`.

### Step 2: Compare against our allowlist

Read `scripts/check_skill_frontmatter.py` and compare:

- `_SPEC_FIELDS` — should match what the upstream spec lists
- `_EXTENDED_FIELDS` — check if any of these now appear in the upstream spec

### Step 3: Check the tracking issue

```bash
gh issue view 105 --repo agentskills/agentskills --json state,title,comments
```

Check whether issue #105 has been closed/merged, or if there are updates
indicating the fields have been adopted.

### Step 4: Check skillmark releases

```bash
gh release list --repo michellepellon/skillmark --limit 5
```

Check whether a newer version of skillmark recognizes the extended fields
in its E030 rule. If so, test by temporarily re-enabling E030:

```bash
skillmark check --disable "" SKILL.md
```

### Step 5: Report findings

Produce a summary with one of these verdicts:

- **Still needed** — the spec has not adopted the extended fields; keep the
  custom hook and E030 disabled.
- **Partially resolved** — some fields are now in the spec; update
  `_SPEC_FIELDS` and `_EXTENDED_FIELDS` accordingly.
- **Can be retired** — all extended fields are in the spec and skillmark
  recognizes them. Follow the retirement steps below.

### Retirement steps (when verdict is "Can be retired")

1. Update `.skillmark.toml`: remove `E030` from the `disable` list
2. Remove `scripts/check_skill_frontmatter.py`
3. Remove the `check-skill-frontmatter` hook from `.pre-commit-config.yaml`
4. Remove this skill (`.agents/skills/check-skill-spec/`)
5. Run `tox -e lint` to verify everything passes with E030 re-enabled
6. Commit and create a PR
