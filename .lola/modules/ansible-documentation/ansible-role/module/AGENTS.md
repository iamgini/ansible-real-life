# Ansible Role

Module provides commands for scaffolding Ansible roles following Red Hat CoP automation good practices.

## When to Use

- **ansible-scaffold-role command**: Use `/ansible-scaffold-role` to create a new Ansible role that fully complies with Red Hat CoP good practices. Features include:
  - Interactive variable builder that asks what the role manages (packages, services, configs, users, firewall, storage) and generates realistic defaults, tasks,
    handlers, and templates
  - Task componentization that splits complex roles into install.yml, configure.yml, service.yml with proper sub-task name prefixes
  - Smart handler generation that creates actual handlers (restart, reload, validate) based on role purpose
  - Collection-aware scaffolding using ansible-creator inside collections with fallback to manual creation
  - Standalone role creation for roles outside collections

## Configuration

**Optional Dependencies:**

- `ansible-creator` CLI - Used to generate role skeleton structure (falls back to manual creation if not installed)

**Required Context:**

- CoP rules from `CLAUDE.md` and `redhat-cop-automation-good-practices-*.md` files
- Fallback to https://github.com/redhat-cop/automation-good-practices when rules not available locally

## Notes

- The scaffold command follows an interactive pattern: gather user input about what the role manages, then generates appropriate variables, tasks, handlers,
  and templates pre-populated with realistic content
- All generated roles include proper meta/argument_specs.yml, README.md with examples, and CoP-compliant variable naming
- Roles are validated post-scaffold to ensure compliance with all CoP rules (no dashes in names, FQCN module usage, proper YAML formatting, etc.)
