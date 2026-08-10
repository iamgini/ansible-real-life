# Ansible Documentation Module

A Lola module providing skills and workflows for working with Ansible documentation at docs.ansible.com.

## Installation

```bash
# Install Lola package manager
pip install lola-ai

# Register the module from GitHub
lola mod add https://github.com/ansible-community/ai-forge.git --module-content ansible-documentation/module -n ansible-documentation

# Or clone and register locally
git clone https://github.com/ansible-community/ai-forge.git
lola mod add ./ai-forge/ansible-documentation

# Install to Claude Code
lola install ansible-documentation -a claude-code

# Install to Cursor
lola install ansible-documentation -a cursor

# Install to other assistants
lola install ansible-documentation -a gemini-cli
lola install ansible-documentation -a opencode
```

## Components

### Skills

- **`ansible-markdown-docs`** — Fetches Ansible documentation using `curl` with the
  `Accept: text/markdown` header, which instructs Read the Docs to return clean Markdown
  content rather than HTML.

## Usage

```
# Fetch a specific page by URL
Get Ansible documentation https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html

# Ask the agent to look up docs by topic
Get Ansible documentation for roles

# Provide a link directly
Check https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html
```

## How It Works

The skill uses the Read the Docs Markdown-for-agents feature: sending `Accept: text/markdown`
in the HTTP request header causes docs.ansible.com to return the raw Markdown source of the
page instead of rendered HTML. This produces clean, structured content suitable for display
inline in an AI assistant conversation.

Reference: [Read the Docs — Markdown for Agents](https://docs.readthedocs.com/platform/latest/reference/markdown-for-agents.html)

## Requirements

- `curl` available in PATH

## Development

This module follows the Lola module structure:

```
ansible-documentation/
├── README.md           # This file
└── module/             # Lola-importable content
    ├── AGENTS.md       # Module-level instructions
    ├── agents/         # Agent definitions
    ├── commands/       # Command definitions
    ├── skills/         # Skill folders with SKILL.md
    │   └── ansible-markdown-docs/
    │       └── SKILL.md
    └── mcps.json       # MCP server configuration
```

## Contributing

See [SKILL_GUIDELINES.md](../SKILL_GUIDELINES.md) for criteria on writing new skills.
See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution process.

## License

GPL-3.0-or-later
