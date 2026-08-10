# ai-forge Agent Guidelines

Read this file before making changes. It defines the rules and workflow that
all agents must follow when working in this repository.

## Architectural Invariants

These are non-negotiable. If you think one needs to change, write an ADR first
(see `docs/adrs/`).

1. **ADRs before structural changes.** Read `docs/adrs/` before making
   decisions that affect module structure, CI, or tooling. If no ADR covers
   your change, write one.

2. **tox is the sole orchestration tool** (ADR-001). `tox -e lint` for all
   linting. Never invoke `prek`, `markdownlint`, `yamllint`, `shellcheck`, or
   `skillmark` directly. In CI, use `uvx --with tox-uv tox -e lint`.

3. **Skills follow the agentskills.io spec.** All `SKILL.md` files must conform
   to the [Agent Skills specification](https://agentskills.io/specification).
   Validated by skillmark via `tox -e lint`.

4. **All skills must be in the manifest.** Every module that contains skills
   must be listed in `lola-market.yml`. Validated by the `check-manifest-skills`
   hook via `tox -e lint`.

## Prohibited Direct Invocations

**Do not run any of these directly. Use the corresponding tox environment.**

| Prohibited | Use instead |
|------------|-------------|
| `prek run ...` | `tox -e lint` |
| `skillmark check ...` | `tox -e lint` |
| `markdownlint ...` | `tox -e lint` |
| `yamllint ...` | `tox -e lint` |
| `shellcheck ...` | `tox -e lint` |
| `actionlint ...` | `tox -e lint` |

## Quality Assurance

All agents must:

1. Run `tox -e lint` before committing
2. Review ADRs in `docs/adrs/` before making structural decisions
3. Follow skill authoring guidelines in `SKILL_GUIDELINES.md`
4. Ensure new skills are added to the module's `AGENTS.md`, README, and
   `lola-market.yml`
5. Commit with proper message format (see `CONTRIBUTING.md`)
6. Verify no architectural invariants (above) were violated

## Key File Locations

| Path | Purpose |
|------|---------|
| `SKILL_GUIDELINES.md` | How to author skills |
| `CONTRIBUTING.md` | Development workflow and PR process |
| `lola-market.yml` | Lola marketplace manifest |
| `.pre-commit-config.yaml` | Hook configuration (source of truth for lint) |
| `pyproject.toml` | tox environment definitions |
| `docs/adrs/` | Architectural decision records |
| `scripts/` | Validation hook scripts |

## Project Skills

This project defines agent skills in `.agents/skills/`. When the user asks
to perform one of these tasks, read the corresponding `SKILL.md` **before
doing anything else** and follow its instructions.

| Command | Purpose |
|---------|---------|
| `/pr-new` | Create and submit a pull request |
| `/pr-contributor-review` | Review a contributor's pull request |

## Design Thinking

### When in doubt, read the ADR

Every major design choice has an ADR in `docs/adrs/`. If you are about to make
a decision that affects module structure, CI pipeline, tooling, or developer
workflow, check the ADR index first. If no ADR covers it, write one before
implementing.

### Skills are the product

This repository does not ship Ansible modules, plugins, or roles. It ships
AI agent skills that teach assistants how to build and maintain Ansible content.
Every change should be evaluated through the lens of "does this make the skills
better for developers using them?"
