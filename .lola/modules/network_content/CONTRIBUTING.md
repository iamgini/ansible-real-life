# Contributing to ai-forge

We want your successful workflows. Contributions are organized into three tiers:

| Tier | What You Do | Time | Git Skills |
| :--- | :---------- | :--- | :--------- |
| **1 — Request a skill** | Open a GitHub Issue describing the workflow you want | ~5 min | None |
| **2 — Author a skill** | Create a new skill file following the template | ~30 min | Basic |
| **3 — Improve an existing skill** | Fork, edit, test, open a PR | ~15 min | Basic |

**Not sure where to start?** Open a GitHub Issue describing what you're trying to accomplish. Maintainers will help guide you to the right approach.

## Quick Links

- [Development Workflow](#development-workflow) — Fork, branch, commit, PR process
- [Quality Checklist](#quality-checklist) — What to check before submitting
- [Testing Locally](#testing-locally) — How to test skills before pushing
- [Commit Messages](#commit-messages) — Format and attribution requirements
- [Adding a New Skill](#adding-a-new-skill) — Step-by-step skill creation guide
- [After PR Submission](#after-pr-submission) — What happens next

## Prerequisites

Before contributing, ensure you have:

- **Lola package manager** installed: `uv tool install lola-ai` (or `pip install lola-ai`)
- **At least one AI assistant** (Claude Code, Cursor, Gemini CLI, etc.)
- **tox** installed: `uv tool install tox --with tox-uv`
- **prek** installed: `brew install prek` (or `cargo install prek`, or `pip install prek`)
- **Git** with user name and email configured

### Git Hooks Setup

This project uses [prek](https://prek.j178.dev/) (a drop-in replacement for
pre-commit) to run git hooks. Install and activate them with:

```bash
# Install git hooks
prek install

# Run all checks
tox -e lint
```

### What Gets Checked

Hooks run automatically on `git commit` and via `tox -e lint`:

- **Markdown** — markdownlint-cli2 with .markdownlint.json config
- **YAML** — Frontmatter validation and syntax checking
- **Shell scripts** — shellcheck
- **GitHub Actions** — actionlint
- **Agent Skills spec** — [skillmark](https://github.com/michellepellon/skillmark) validates all SKILL.md files against the [agentskills.io specification](https://agentskills.io/specification)
- **JSON** — Syntax validation
- **File formatting** — Trailing whitespace, end-of-file, line endings
- **Module structure** — Lola module directory layout validation
- **Command frontmatter** — Command .md files have valid frontmatter
- **mcps.json schema** — Each mcps.json has a `mcpServers` key
- **Manifest completeness** — Every module with skills is in `lola-market.yml`

CI runs the same `tox -e lint` command, so fixing issues locally saves iteration time.

## Development Workflow

All contributions use the **fork-and-pull** model. You work on a personal fork and submit pull requests to the main repository.

### One-Time Setup

1. **Fork the repository** on GitHub: go to [ansible-community/ai-forge](https://github.com/ansible-community/ai-forge) and click **Fork**.

2. **Clone your fork** locally:

   ```bash
   git clone git@github.com:<your-username>/ai-forge.git
   cd ai-forge
   ```

3. **Add the upstream remote** (the main repository):

   ```bash
   git remote add upstream git@github.com:ansible-community/ai-forge.git
   ```

4. **Verify your remotes:**

   ```bash
   git remote -v
   # <your-username>  git@github.com:<your-username>/ai-forge.git (fetch)
   # <your-username>  git@github.com:<your-username>/ai-forge.git (push)
   # upstream         git@github.com:ansible-community/ai-forge.git (fetch)
   # upstream         git@github.com:ansible-community/ai-forge.git (push)
   ```

5. **Install git hooks** (see Prerequisites above).

### Making Changes

1. **Sync your fork** with the latest upstream changes:

   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch** from `main`:

   ```bash
   git checkout -b add-my-feature
   ```

   Use a descriptive branch name:
   - `add-release-notes-skill`
   - `fix-pr-review-formatting`
   - `update-contributing-docs`

3. **Make your changes.** Follow the [Quality Checklist](#quality-checklist) below.

4. **Test locally** (see [Testing Locally](#testing-locally) section).

5. **Commit your work:**

   ```bash
   git add <files>
   git commit -m "Add release-notes skill to ansible-collection-sdlc

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```

   **Important:**
   - Stage files by name — avoid `git add .` which can accidentally include sensitive files
   - Include Co-Authored-By if AI-assisted (see [AI Attribution](#ai-attribution))
   - Follow [commit message guidelines](#commit-messages)

6. **Push to your fork:**

   ```bash
   git push <your-username> add-my-feature
   ```

7. **Create a pull request** from your fork to the main repository:

   ```bash
   gh pr create --repo ansible-community/ai-forge
   ```

   Or use the GitHub web UI — you'll see a "Compare & pull request" banner after pushing.

### Keeping Your Branch Up to Date

If main has moved ahead while your PR is open:

```bash
git fetch upstream
git checkout add-my-feature
git merge upstream/main
git push <your-username> add-my-feature
```

## Testing Locally

**Before pushing**, test your skill or command in a live AI assistant session.

### For New Skills

1. **Load the skill** in your AI assistant:

   Ask Claude Code (or your assistant) to:
   > "Load and invoke the skill at `ansible-collection-sdlc/skills/my-new-skill/SKILL.md`"

2. **Test the happy path:**
   - Invoke the skill with typical inputs
   - Verify it produces the expected output
   - Check that all steps execute correctly

3. **Test edge cases:**
   - Try invalid inputs
   - Test error handling
   - Verify failure messages are clear

4. **Document the results** in your PR description:

   ```markdown
   ## Testing

   Tested with Claude Code 1.5.0:

   - ✅ Happy path: Skill correctly generated release notes from changelog fragments
   - ✅ Error handling: Clear error when no fragments found
   - ✅ Edge case: Handles collections with no previous releases
   ```

### For Skill Modifications

1. **Test the old behavior** first (before your changes)
2. **Apply your changes**
3. **Test the new behavior**
4. **Verify you didn't break existing functionality** (regression test)

### For Documentation Changes

1. **Render the markdown** to verify formatting
2. **Check all links** work and point to the correct locations
3. **Verify code examples** are syntactically correct

## Quality Checklist

Before submitting a PR, verify:

### For All Contributions

- [ ] `tox -e lint` passes
- [ ] No secrets or real credentials in examples (use placeholders like `<token>`, `user@example.com`)
- [ ] Professional and inclusive language (no offensive content)
- [ ] GPL-3.0-or-later license header in new code files (if applicable)

### For Skills and Commands

- [ ] **Frontmatter follows the [agentskills.io spec](https://agentskills.io/specification):**
  - `name` — Must match the skill folder name (lowercase, hyphens, no consecutive hyphens)
  - `description` — What the skill does **and** when to use it (include "Use when..." language)

- [ ] **Documentation includes examples:**
  - Show how to invoke the skill
  - Include example inputs and outputs
  - Explain what the skill does in each step

- [ ] **Tool usage is safe:**
  - No `rm -rf /` or other destructive patterns
  - Confirmation steps for destructive operations
  - No arbitrary user input executed without validation

- [ ] **Lola-compatible:**
  - Use standard frontmatter (YAML between `---` delimiters)
  - No assistant-specific features without fallbacks
  - Works with Lola package manager structure

- [ ] **Follows Ansible standards** (for Ansible-related skills):
  - Uses correct collection naming (namespace.name)
  - Follows galaxy.yml structure conventions
  - Respects semantic versioning rules

- [ ] **Tested locally** (see [Testing Locally](#testing-locally))

## Commit Messages

Follow these guidelines for commit messages:

### Format

```
Short summary in imperative mood (max 72 chars)

Longer explanation if needed. Wrap at 72 characters. Explain what
changed and why, not how (the code shows how).

If this commit was AI-assisted, include the trailer below.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Rules

- **Use imperative mood:** "Add feature" not "Added feature"
- **Keep first line under 72 characters**
- **Include blank line before body** (if you add a body)
- **Wrap body text at 72 characters**

### Examples

**Good:**

```
Add stable-release skill for Ansible collections

This skill orchestrates the complete release workflow for collections
with stable-X branches, including version analysis, changelog
generation, documentation updates, and quality checks.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Bad:**

```
added stuff
```

**Bad:**

```
Fixed the bug in the PR review skill that was causing it to fail when reviewing PRs with more than 100 files changed because it wasn't paginating the results
```

(First line too long, should be split)

## AI Attribution

### When AI Attribution is Required

You **must** include a `Co-Authored-By` trailer when:

- AI helped you write the skill/command/documentation
- AI generated code examples or test scenarios
- AI suggested the approach or structure
- You iterated on AI-generated content

### When AI Attribution is Optional

You **don't** need attribution when:

- You wrote everything yourself without AI assistance
- AI only helped with spelling/grammar (like a spell checker)
- You used AI to look up syntax but wrote the content yourself

### How to Add Attribution

Add to the end of your commit message:

```
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

Replace with the actual model you used:

- `Claude Opus 4.6 <noreply@anthropic.com>`
- `Claude Sonnet 4.5 <noreply@anthropic.com>`
- `GitHub Copilot <noreply@github.com>`
- `Cursor <noreply@cursor.sh>`

### Why This Matters

The Ansible community values transparency. When users see AI attribution, they know to apply appropriate scrutiny and understand the content's origin. It's not about liability — it's about honesty.

## After PR Submission

### What Happens Next

1. **CI checks run automatically** (`tox -e lint`):
   - Markdown, YAML, shell, and GitHub Actions linting
   - Agent Skills spec validation (skillmark)
   - Module structure, command frontmatter, and manifest completeness

2. **A maintainer will review your PR:**
   - Usually within 1-2 weeks
   - Faster for simple fixes
   - Slower for large new features

3. **Address review feedback:**
   - Push additional commits to your branch
   - Respond to reviewer comments
   - Make requested changes

4. **Once approved and CI passes:**
   - A maintainer will merge your PR
   - Your contribution becomes part of the next release

### Review Focus Areas

Maintainers will check:

- **Does this solve a real problem?** Is it useful to the Ansible community?
- **Does it follow Ansible standards?** Collections, roles, galaxy.yml conventions
- **Is it safe?** No credential exposure, destructive operations have confirmations
- **Is it documented?** Clear examples and usage instructions
- **Is it tested?** Evidence that it actually works

Maintainers are here to **help you get your contribution merged**, not block you. If feedback seems unclear, ask for clarification.

## Linting Commands

Run all checks (the primary command):

```bash
tox -e lint
```

Run a specific hook:

```bash
prek run <hook-id> --all-files
```

Auto-fix skillmark issues:

```bash
prek run skillmark-fix --all-files
```

## Adding a New Skill

Skills are AI assistant capabilities that can be invoked by users. Follow these steps to add a new skill:

### Step 1: Create the skill folder

Create a new folder under the appropriate module's skills directory:

```bash
mkdir -p <module>/module/skills/<skill-name>/
```

For example:

```bash
mkdir -p ansible-collection-sdlc/module/skills/my-new-skill/
```

### Step 2: Create the SKILL.md file

Create a `SKILL.md` file in the skill folder with the required frontmatter:

```markdown
---
name: my-new-skill
description: >-
  A brief description of what this skill does and when it should be invoked.
---

# Skill: my-new-skill

## Purpose

Describe the purpose of this skill.

## When to Invoke

TRIGGER when:
- User asks to...
- User wants to...

DO NOT TRIGGER when:
- ...

## Steps

1. First step...
2. Second step...
```

**Required frontmatter fields:**

- `name` - The skill identifier (should match the folder name)
- `description` - A concise description shown in skill listings

### Step 3: Add supporting files (optional)

Add any additional files the skill needs (templates, reference data, etc.) in the same folder.

### Step 4: Update AGENTS.md

Add an entry for your skill in the module's `AGENTS.md` file:

```markdown
- **my-new-skill skill**: Use the `my-new-skill` skill when you want to...
  Invoke when the user asks to...
```

### Step 5: Update the module README

Add your skill to the Components section in the module's `README.md`.

### Step 6: Verify the module is in the manifest

Ensure the module is listed in `lola-market.yml`. The `check-manifest-skills`
hook (run via `tox -e lint`) will catch missing entries. Run `tox -e lint` to
validate your skill against the [agentskills.io spec](https://agentskills.io/specification)
via skillmark.

### Making the Skill Available

After adding your skill, users can install it using [Lola](https://lobstertrap.org/lola/):

```bash
# Register or update the module
lola mod add https://github.com/ansible-community/ai-forge/<module>

# Install to an AI assistant (project-level)
lola install <module> -a claude-code

# Or install globally (available in all projects)
lola install <module> -a claude-code ~
```

## Creating New Modules

Want to add a new top-level Lola module? Open a GitHub Issue first to discuss:

- What domain does it cover? (e.g., ansible-collection-testing, ansible-playbook-standards)
- What skills/commands will it include?
- How does it fit with existing modules?
- Who will maintain it?

Maintainers will help you define the scope and structure before you start building.

## Questions?

- **General questions:** Open a GitHub Issue
- **Stuck on something:** Tag a maintainer in an Issue or PR
- **Want to discuss an idea:** Open a GitHub Issue with your proposal
- **Found a bug:** Open a GitHub Issue with reproduction steps

See [GOVERNANCE.md](GOVERNANCE.md) for project structure and decision-making.

## Additional Resources

- [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html)
- [Red Hat CoP Contributing Guidelines](https://redhat-cop.github.io/contrib/)
- [Lola Package Manager Documentation](https://lobstertrap.org/lola/)
- [SKILL_GUIDELINES.md](SKILL_GUIDELINES.md) — Detailed skill writing guide
- [AGENTS.md](AGENTS.md) — Agent guidelines and architectural invariants
- [GOVERNANCE.md](GOVERNANCE.md) — Project governance and decision-making
- [Agent Skills Specification](https://agentskills.io/specification) — SKILL.md format reference
