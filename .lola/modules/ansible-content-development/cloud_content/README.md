# Cloud Content Module

A Lola module for cloud automation skills and workflows specific to Ansible cloud collections.
Contains community-facing skills for cloud provider integrations, infrastructure management, and cloud-native workflows.

## Installation

```bash
# Install Lola package manager
pip install lola-ai

# Register the module from GitHub
lola mod add https://github.com/ansible-community/ai-forge/cloud_content

# Or clone and register locally
git clone https://github.com/ansible-community/ai-forge.git
lola mod add ./ai-forge/cloud_content

# Install to Claude Code
lola install cloud_content -a claude-code

# Install to Cursor
lola install cloud_content -a cursor

# Install to other assistants
lola install cloud_content -a gemini-cli
lola install cloud_content -a opencode
```

## Components

### Skills

| Skill | Description |
|-------|-------------|
| `aws-terminator-analyze` | Analyze Ansible AWS collection PRs to determine required aws-terminator changes |
| `aws-terminator-implement` | Implement terminator classes and IAM permissions in aws-terminator repository |
| `aws-terminator-workflow` | End-to-end orchestrator: analyze → implement → test → PR creation |
| `collection-backport-status-check` | Check backport and patchback workflow blockers for Ansible collection stable branches. Detect open backport PRs and patchback failures that must be resolved before creating a release prep PR. Complements version analysis skills by focusing on process blockers. By default, checks the two most recent stable branches. |

Skills live under [`module/skills/`](module/skills/).

### Commands

None currently defined.

### Agents

None currently defined.

### MCP Servers

None currently defined.

## Scope

This module is for **public, community-facing** cloud automation skills.

### What is a Cloud Collection?

A **Cloud Collection** provides modules and plugins for managing cloud-based services via APIs.
This includes infrastructure services (compute, storage, networking), platform services (databases, AI/ML, secrets management, messaging), and more.

Examples: `amazon.aws`, `amazon.ai`, `community.aws`, `azure.azcollection`, `google.cloud`, `hashicorp.vault`, `openstack.cloud`

### What Makes Cloud Collections Different

Cloud collections share common development patterns:

- **Connection**: Standard Python using REST APIs or provider SDKs
- **State handling**: CRUD operations with eventual consistency and async provisioning
- **Authentication**: API keys, service accounts, IAM roles, environment variables
- **Idempotency**: Check resource existence via API before acting

### Planned Skills

| Skill | Description |
|-------|-------------|
| `cloud-module-scaffold` | Generate cloud module boilerplate with proper SDK integration, pagination handling, and waiter patterns |
| `cloud-inventory-plugin` | Scaffold dynamic inventory plugins for cloud providers with proper caching and filtering |
| `cloud-auth-patterns` | Guide for implementing credential chain patterns (env vars → config files → instance metadata) |
| `cloud-async-operations` | Patterns for handling long-running operations (polling, waiters, callbacks) |
| `cloud-pagination` | Implement pagination for list operations with configurable page sizes |
| `cloud-integration-tests` | Generate integration test structure using cloud provider test accounts |

### Example Use Cases

- Provisioning cloud resources with proper wait conditions
- Multi-cloud abstraction modules
- Cloud provider API interaction patterns
- Infrastructure-as-code validation
- Cost optimization helpers

Internal or business-specific cloud skills should be contributed to the private repository.

## Development

This module follows the Lola module structure:

```
cloud_content/
├── README.md           # This file
└── module/             # Lola-importable content
    ├── AGENTS.md       # Module-level instructions
    ├── mcps.json       # MCP server configuration
    └── skills/         # Skill folders with SKILL.md
        └── collection-backport-status-check/
            └── SKILL.md
```

## Contributing

See [SKILL_GUIDELINES.md](../SKILL_GUIDELINES.md) for criteria on writing new skills.
See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution process.

## License

GPL-3.0-or-later
