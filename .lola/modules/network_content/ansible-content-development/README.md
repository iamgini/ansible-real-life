# Ansible Content Development Module

A Lola module for developing and testing Ansible content following official best practices.
Provides skills to write and review Python modules (write-module), YAML-based content (write-content),
and tests for both — module unit/integration tests (write-module-tests) and Molecule functional tests (write-content-tests).

## Authoring Principles

- Prefer existing Ansible content before creating custom automation.
- Selection order: `ansible.builtin` -> vendor-supported content -> content from verified authors -> general Galaxy content -> custom content only as a last resort.
- Avoid `ansible.builtin.shell`, `ansible.builtin.raw`, and ad hoc bash unless there is a clear, explicit justification that no safer module or plugin approach will work.
- Prefer purpose-built modules first, then `ansible.builtin.command` when shell features are not required.

## Installation

```bash
# Install Lola package manager
pip install lola-ai

# Register the module from GitHub
lola mod add https://github.com/ansible-community/ai-forge/ansible-content-development

# Or clone and register locally
git clone https://github.com/ansible-community/ai-forge.git
lola mod add ./ai-forge/ansible-content-development

# Install to Claude Code
lola install ansible-content-development -a claude-code

# Install to Cursor
lola install ansible-content-development -a cursor

# Install to other assistants
lola install ansible-content-development -a gemini-cli
lola install ansible-content-development -a opencode
```

## Components

### Skills

See **[SKILLS.md](../SKILLS.md#ansible-content-development)** for skills in this module.

### Commands

None currently defined.

### Agents

None currently defined.

### MCP Servers

None currently defined.

## Companion Modules

This module ships skills only. Some skill recommendations intentionally point to companion tools in
other Lola modules when the user needs scaffolding, compliance review, release/version guidance, or
broader test workflows.

- **`ansible-collection-sdlc`** - companion skills such as `run-tests`, `next-release`,
  `changelog-fragment`, `pr-review`, and `sanity`
- **`ansible-role`** - the `/ansible-scaffold-role` command
- **`ansible-collection-standards`** - the `/ansible-scaffold-collection` and
  `/ansible-cop-review` commands plus the `ansible-zen` skill

If those modules are not installed, the skills in this module should fall back to the direct CLI
commands they already mention, such as `ansible-test sanity`, `ansible-lint`, or `molecule test`.

## Development

This module follows the Lola module structure:

```
ansible-content-development/
├── README.md           # This file
└── module/             # Lola-importable content
    ├── AGENTS.md       # Module-level instructions
    ├── skills/         # Skill folders with SKILL.md
    ├── commands/       # Slash command .md files
    ├── agents/         # Subagent .md files
    └── mcps.json       # MCP server configuration
```

## Dependencies

- **ansible-test** (optional) - Used to validate modules and run unit/integration tests
- **ansible-lint** (optional) - Used to validate generated Ansible content
- **ansible-creator** (optional) - Used for scaffolding project structures (collections, roles, playbooks)
- **molecule** (optional) - Used for functional testing of roles and playbooks
- **podman** or **docker** (optional) - Container backend for Molecule and ansible-test

## License

GPL-3.0-or-later
