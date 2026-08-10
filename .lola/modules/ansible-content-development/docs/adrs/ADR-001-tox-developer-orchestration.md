# ADR-001: tox as Sole Developer Orchestration Tool

## Status

Accepted

## Date

2026-06-05

## Context

Developer tasks in ai-forge are spread across multiple tools with no single
entry point:

- **pre-commit** for lint hooks (`pre-commit run --all-files`)
- **npm** for markdown linting (`npm run lint:md`)
- **Individual tools** invoked directly (`yamllint`, `shellcheck`, `skillmark`)

A new contributor must discover multiple tools and commands, documented
inconsistently across `CONTRIBUTING.md` and `README.md`. There is no local/CI
parity — GitHub Actions runs dedicated actions (`markdownlint-cli2-action`,
`action-shellcheck`, `action-actionlint`) while developers run `pre-commit`
locally.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| tox + tox-uv | Ansible ecosystem standard, named environments, `allowlist_externals` wraps non-Python tasks, tox-uv integrates with `uv` | Additional tool to install |
| just / Makefile | Language-agnostic, no Python dependency | No virtualenv management, manual dependency handling |
| prek only | Already used for hooks, single binary | Not an orchestration tool — manages hooks, not arbitrary tasks |
| Status quo (pre-commit) | Already in place | Multiple tools, no single entry point, CI/local drift |

## Decision

**Adopt tox with the tox-uv plugin as the sole developer orchestration tool.**
Install via `uv tool install tox --with tox-uv`. Every developer-facing task is
a `tox -e <env>` command.

### Environment layout

| Environment | What it runs | Category |
|-------------|-------------|----------|
| `lint` | `prek run --all-files` | Quality gate |

### Relationship to existing tools

- **prek**: Remains the git hook runner and pre-commit replacement. `tox -e lint`
  delegates to `prek run --all-files`. The single source of truth for hook
  configuration stays in `.pre-commit-config.yaml`.
- **CI**: The lint workflow calls `uvx --with tox-uv tox -e lint` — the same
  command a developer runs locally.

## Rationale

- **Single entry point**: `tox -e lint` is the one command a developer needs.
  `tox l` shows all available environments.
- **Local/CI parity**: CI runs the same `tox -e lint` command as developers.
  No drift between local hooks and CI checks.
- **Ansible ecosystem alignment**: tox is the standard test runner for
  ansible-core, ansible collections, and most Ansible tooling projects.
  Contributors from the Ansible ecosystem will recognize it immediately.
- **Room to grow**: Additional environments (e.g., `tox -e test` for validation
  script tests) can be added later without changing the developer workflow.
- **Non-Python tasks**: `allowlist_externals` cleanly wraps prek without
  contorting it into a Python dependency.

## Consequences

### Positive

- One tool to learn, one command pattern for all tasks
- CI workflow simplified to a single step
- `tox l` serves as living documentation of available developer tasks

### Negative

- Additional tool to install (`uv tool install tox --with tox-uv`)
- prek and tox coexist — two tools, but with clear separation (hooks vs
  orchestration)

## Related Decisions

- This ADR is adapted from
  [apme ADR-047](https://github.com/ansible/apme) which established the
  same pattern for a larger Python project.
