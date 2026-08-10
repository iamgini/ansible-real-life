# Ansible Role Module

A Lola module providing commands for scaffolding Ansible roles following Red Hat Communities of Practice (CoP) automation good practices.

## Installation

```bash
# Install Lola package manager
pip install lola-ai

# Register the module from GitHub
lola mod add https://github.com/ansible-community/ai-forge/ansible-role

# Or clone and register locally
git clone https://github.com/ansible-community/ai-forge.git
lola mod add ./ai-forge/ansible-role

# Install to Claude Code
lola install ansible-role -a claude-code

# Install to Cursor
lola install ansible-role -a cursor

# Install to other assistants
lola install ansible-role -a gemini-cli
lola install ansible-role -a opencode
```

## Components

### Skills

None currently defined.

### Commands

- **ansible-scaffold-role** - Scaffold a new Ansible role with interactive variable builder, task componentization, smart handler generation, and full CoP compliance

### Agents

None currently defined.

### MCP Servers

None currently defined.

## Development

This module follows the Lola module structure:

```
ansible-role/
├── README.md           # This file
└── module/             # Lola-importable content
    ├── AGENTS.md       # Module-level instructions
    ├── skills/         # Skill folders with SKILL.md
    ├── commands/       # Slash command .md files
    ├── agents/         # Subagent .md files
    └── mcps.json       # MCP server configuration
```

## Dependencies

- **ansible-creator** (optional) - Used by scaffold command to generate role skeleton, with fallback to manual creation
- **CoP rules** - Command references rules from CLAUDE.md and redhat-cop-automation-good-practices files, with fallback to https://github.com/redhat-cop/automation-good-practices

## License

GPL-3.0-or-later
