# Ansible Collection SDLC Module

A Lola module for the full software development lifecycle of Ansible collections: conventional commits, changelog
fragments, PR reviews, releases, and testing.  Streamlines day-to-day development workflows from code commit to
production release.

## Installation

```bash
# Install Lola package manager
pip install lola-ai

# Register the module from GitHub
lola mod add https://github.com/ansible-community/ai-forge/ansible-collection-sdlc

# Or clone and register locally
git clone https://github.com/ansible-community/ai-forge.git
lola mod add ./ai-forge/ansible-collection-sdlc

# Install to Claude Code
lola install ansible-collection-sdlc -a claude-code

# Install to Cursor
lola install ansible-collection-sdlc -a cursor

# Install to other assistants
lola install ansible-collection-sdlc -a gemini-cli
lola install ansible-collection-sdlc -a opencode
```

## Configuration (Optional)

Skills work with sensible defaults. For customization, create a configuration file:

```bash
# Copy the template
cp ansible-release.conf.template ~/.ansible-release.conf

# Edit with your preferences
vim ~/.ansible-release.conf

# Source before using skills (or add to your shell profile)
source ~/.ansible-release.conf
```

Available configuration options:

- `ANSIBLE_COLLECTIONS_PATH` - Where collections are stored
- `GITHUB_USERNAME` - Your GitHub username for PRs
- `SANITY_MODE` - Default sanity test mode (smart/full/changed-only)
- `AUTO_CREATE_PR` - Automatically create PRs (true/false/prompt)
- Collection-specific overrides (e.g., `amazon_aws_SANITY_MODE`)

See `ansible-release.conf.template` for all options and documentation.

## Components

### Skills

See **[SKILLS.md](../SKILLS.md#ansible-collection-sdlc)** for the complete list of skills in this module.

Key skills include: changelog-fragment, commit, create-branch, create-pr, pr-review, release, run-tests, and SonarCloud integration (configure-sonarcloud-collection, configure-sonarcloud-coverage, sonarcloud-remediation).

### Commands

- **/check-pr-actions** - Check GitHub Actions/GitLab CI status and analyze failures
- **/check-pr-sonarcloud** - Check SonarCloud analysis results for the current pull request
- **/setup-python-venv** - Set up or validate a project-local Python virtual environment

### Agents

None currently defined.

### MCP Servers

None currently defined.

## Development

This module follows the Lola module structure:

```
ansible-collection-sdlc/
├── README.md           # This file
└── module/             # Lola-importable content
    ├── AGENTS.md       # Module-level instructions
    ├── skills/         # Skill folders with SKILL.md (includes sonarcloud-workflow-templates/ for canonical CI YAML)
    ├── commands/       # Slash command .md files
    ├── agents/         # Subagent .md files
    └── mcps.json       # MCP server configuration
```

## Dependencies

- **antsibull-changelog** (optional) - Used for changelog generation
- **gh CLI** (optional) - Used for GitHub/GitLab operations (PRs, releases, upstream detection)
- **ansible-test** - Used for running sanity, unit, and integration tests
- **curl** (optional) - Used for fetching SonarCloud analysis results

## License

GPL-3.0-or-later
