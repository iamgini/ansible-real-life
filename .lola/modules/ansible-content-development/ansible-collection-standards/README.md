# Ansible Collection Standards Module

A Lola module for standards and guidelines compliance, scaffolding, and code review against Red Hat Communities of Practice (CoP) automation good practices.
Provides tools to ensure your Ansible collections meet community standards and inclusion criteria.

## Installation

```bash
# Install Lola package manager
pip install lola-ai

# Register the module from GitHub
lola mod add https://github.com/ansible-community/ai-forge/ansible-collection-standards

# Or clone and register locally
git clone https://github.com/ansible-community/ai-forge.git
lola mod add ./ai-forge/ansible-collection-standards

# Install to Claude Code
lola install ansible-collection-standards -a claude-code

# Install to Cursor
lola install ansible-collection-standards -a cursor

# Install to other assistants
lola install ansible-collection-standards -a gemini-cli
lola install ansible-collection-standards -a opencode
```

## Components

### Skills

See **[SKILLS.md](../SKILLS.md#ansible-collection-standards)** for skills in this module.

### Commands

- **ansible-cop-review** - Review Ansible code against Red Hat CoP automation good practices with severity classification, diff-aware mode, and auto-fix capabilities
- **ansible-scaffold-collection** - Scaffold a new Ansible content collection with plugin generation, CI/CD pipelines, and full CoP compliance
- **ansible-collection-standards-inclusion-review** - Review an Ansible collection for inclusion in the Ansible community package

### Agents

None currently defined.

### MCP Servers

None currently defined.

## Development

This module follows the Lola module structure:

```
ansible-collection-standards/
├── README.md           # This file
└── module/             # Lola-importable content
    ├── AGENTS.md       # Module-level instructions
    ├── skills/         # Skill folders with SKILL.md
    ├── commands/       # Slash command .md files
    ├── agents/         # Subagent .md files
    └── mcps.json       # MCP server configuration
```

## Dependencies

- **ansible-creator** (optional) - Used by scaffold commands to generate base skeletons, with fallback to manual creation
- **ansible-lint** (optional) - Used by review command for cross-referencing
- **CoP rules** - Commands reference rules from CLAUDE.md and redhat-cop-automation-good-practices files, with fallback to https://github.com/redhat-cop/automation-good-practices

## License

GPL-3.0-or-later
