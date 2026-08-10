---
name: stable-release
description: >
  Orchestrates end-to-end stable-branch collection releases. Use this skill
  when you want to release a collection with stable-X branches by coordinating
  stable-release-analyze, stable-release-prep, docs-generate, tox-lint, and
  sanity in sequence.
user-invocable: true
---

# Stable Branch Release Orchestrator

Complete end-to-end release workflow for collections with stable-X branches.

## Author

**Alina Buzachis (alinabuzachis)** - Ansible Cloud Content Team

## Reference Documentation

- Ansible Cloud Content Handbook: https://github.com/ansible-collections/cloud-content-handbook
- Release Process: https://github.com/ansible-collections/cloud-content-handbook/blob/main/stable-release.md

## Purpose

Orchestrates all release steps from analysis to PR creation for stable-branch workflows. Imports
and coordinates individual skills (stable-release-analyze, stable-release-prep, docs-generate,
tox-lint, sanity) in the correct order with proper error handling and user interaction.

## File Operations - Batch Processing

**CRITICAL**: This orchestrator must minimize permission prompts by batching operations.

**Key principles**:

1. **Virtual environment first**: Set up .venv with all required dependencies (antsibull-changelog, ansible-core, tox)
2. **Batch all file reads**: Read galaxy.yml, changelog fragments, and other files in ONE message with parallel tool calls
3. **Parallel quality checks**: Run `/tox-lint` and `/sanity` in parallel using background agents
4. **Sequential git operations**: Git operations via Bash tool are naturally batched in commands

**Example flow**:

```
Message 1: Setup venv with uv/pip (antsibull-changelog, ansible-core, tox)
Message 2: Read galaxy.yml + all changelog fragments (parallel)
Message 3: Run git operations (single bash command with &&)
Message 4: Invoke /tox-lint and /sanity (parallel, run_in_background)
Message 5: Write/Edit files after analysis complete
```

**Virtual environment setup** (use uv for speed):

```bash
python3 -m venv .venv && source .venv/bin/activate && \
(command -v uv &> /dev/null && \
  uv pip install antsibull-changelog ansible-core tox || \
  pip install --quiet antsibull-changelog ansible-core tox)
```

## Configuration

Reads from `~/.ansible-release.conf`:

```bash
export GITHUB_USERNAME="alinabuzachis"
export ANSIBLE_COLLECTIONS_PATH="~/dev/collections/ansible_collections"
export SANITY_MODE="smart"
export AUTO_CREATE_PR="prompt"  # true | false | prompt
export LINT_ON_COMMIT="true"
export SANITY_ON_COMMIT="true"
```

## When to Use This Skill

- Performing a complete collection release
- Automating the release process from start to finish
- After changelog fragments have been created
- When asked to release, publish, or ship a new version
- To follow the cloud-content-handbook release process

## Usage Examples

```bash
# Full automated release (interactive prompts)
/stable-release

# Analyze only (no changes)
/stable-release --analyze-only

# Prepare specific version
/stable-release --collection amazon.ai --version 1.0.1 --branch stable-1

# Custom release date (future-dated or backdated)
/stable-release --collection amazon.ai --version 1.0.1 --branch stable-1 --release-date 2026-06-15

# Skip specific steps
/stable-release --skip-lint --skip-sanity

# Full automation (no prompts)
/stable-release --auto --create-pr

# Dry run (show what would happen)
/stable-release --dry-run
```

## Workflow Steps

See [references/workflow-steps.md](references/workflow-steps.md) for the full six-step
orchestration sequence from analysis through pull request creation.

## Complete Output Example

See [references/output-example.md](references/output-example.md) for a full end-to-end run.

## Error Handling & Recovery

See [references/error-handling.md](references/error-handling.md) for recoverable and
non-recoverable errors and resume capability.

## Flags & Options

| Flag | Description |
| ----- | ----------- |
| `--analyze-only` | Run analysis and stop |
| `--release-date YYYY-MM-DD` | Custom release date (default: today) |
| `--skip-lint` | Skip linting step |
| `--skip-sanity` | Skip sanity testing |
| `--skip-docs` | Skip documentation generation |
| `--force` | Continue even if quality checks fail |
| `--auto` | No interactive prompts (use config defaults) |
| `--create-pr` | Automatically create PR |
| `--dry-run` | Show what would happen without making changes |
| `--resume` | Resume from last successful step |

## Integration Points

This orchestrator imports:

- `/stable-release-analyze` - Determine version needed
- `/stable-release-prep` - Create branch and changelog
- `/docs-generate` - Update documentation
- `/tox-lint` - Run linters
- `/sanity` - Run sanity tests
- `git commit and git push` - Commit and push

## Requirements

### System Requirements

- `git` with configured remotes
- `tox` with lint and add_docs environments
- `antsibull-changelog` installed
- `gh` CLI (for PR creation)

### Repository Requirements

- Git remotes: `origin` (fork), `upstream` (canonical)
- `galaxy.yml` with valid version
- `tox.ini` with lint and add_docs envs
- `changelogs/fragments/` with at least one fragment

### Configuration Requirements

- `~/.ansible-release.conf` with GITHUB_USERNAME
- SSH keys or HTTPS credentials for GitHub

## Exit Codes

- `0`: Release workflow completed successfully
- `1`: Workflow failed at any step
- `2`: Configuration error or missing requirements
- `130`: User aborted (Ctrl+C)

## Implementation Notes

See [references/implementation-notes.md](references/implementation-notes.md) for parallel
execution, state management, user interaction, and handbook compliance guidance.
