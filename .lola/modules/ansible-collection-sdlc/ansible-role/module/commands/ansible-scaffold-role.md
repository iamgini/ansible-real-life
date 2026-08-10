---
description: Scaffold a new Ansible role following Red Hat CoP good practices
argument-hint: "[role-name]"
---

Create a new Ansible role that fully complies with every rule in CLAUDE.md. Leverage ansible-creator when available, falling back to manual creation if needed.

## Arguments

Use `$ARGUMENTS` to access the optional role name. If not provided, ask the user for the role name.

## Workflow

1. **Gather inputs**

   If `$ARGUMENTS` is provided, use it as the role name. Otherwise ask the user.

   Ask the user for:
   - **Role name** (snake_case, no dashes) — required (may come from `$ARGUMENTS`)
   - **Target path** — where to create the role (default: `./roles/<role_name>`)
   - **Collection context** — is this role inside an existing collection? If a `galaxy.yml` exists in the project root or a parent directory, assume yes
   - **Brief description** — what the role does (for README and argument_specs)
   - **Platform support needed** — which OS families/distributions (optional)
   - **Provider support** — does the role need a provider pattern? (optional)
   - **What does the role manage?** — Ask what the role actually does to drive variable and task generation. Common patterns:
     - **Packages** — installs/removes packages → generates `<role_name>_packages` list variable, install tasks
     - **Services** — manages systemd/init services → generates `<role_name>_service_name`, `<role_name>_service_state`, `<role_name>_service_enabled` variables, service tasks, restart/reload handlers
     - **Configuration files** — manages config via templates → generates `<role_name>_config_*` variables, template tasks with `backup: true` and `notify:`
       handler, config file templates with `{{ ansible_managed | comment }}`
     - **Users/groups** — manages system users → generates `<role_name>_users` list variable, user/group tasks
     - **Firewall rules** — manages firewall ports → generates `<role_name>_firewall_ports` list variable, firewall tasks
     - **Storage/mounts** — manages filesystems or mounts → generates appropriate variables and tasks
     - **Custom** — let the user describe freely, then derive variables and tasks from their description

     The user can select multiple patterns. Use their answers to pre-populate `defaults/main.yml`, `meta/argument_specs.yml`, `tasks/`, `handlers/`,
     and `templates/` with realistic, role-specific content instead of empty placeholders.

2. **Execute scaffolding strategy**

   **If inside a collection:**
   - Use `ansible-creator add resource role <role_name> <collection_path>` to generate the skeleton, then modify the generated files to comply with all rules
   - If `ansible-creator` is not installed, fall back to creating the directory structure manually and inform the user they can install it with
     `pip install ansible-creator` or use the `ansible-dev-tools` devcontainer for future use

   **If standalone:**
   - Create the role directory structure manually with all required files

3. **Create defaults/main.yml**

   - All user-facing variables with sensible defaults, prefixed with the role name: `<role_name>_variable_name`
   - Variables without safe defaults: present but commented out with a description
   - If provider pattern is used: `<role_name>_provider` variable

4. **Create vars/main.yml**

   - Internal constants and magic values only, prefixed with `__<role_name>_`
   - NEVER user-facing defaults here
   - Platform-specific variable files if requested (`RedHat.yml`, `Debian.yml`, etc.)

5. **Create tasks/main.yml**

   - Include the platform-specific variable loading pattern from CLAUDE.md
   - Include the platform-specific task loading pattern if platform tasks needed
   - Use `{{ role_path }}/vars/` and `{{ role_path }}/tasks/` absolute paths
   - All tasks named in imperative form
   - All modules use FQCN
   - Use `loop:` not `with_*`

6. **Implement task componentization**

   If the role manages multiple concerns (e.g., packages + config + service), split tasks into separate component files under `tasks/`:
   - `tasks/main.yml` — includes component files using `ansible.builtin.include_tasks` with `{{ role_path }}/tasks/` paths
   - `tasks/install.yml` — package installation tasks
   - `tasks/configure.yml` — configuration/template tasks
   - `tasks/service.yml` — service management tasks
   - Other component files as needed based on what the role manages

   Name tasks in component files with a prefix matching the file name: `install | Install required packages`, `configure | Deploy configuration file`, `service | Ensure service is running`.

   Only create component files that are relevant to what the role manages — do not generate empty component files. If the role is simple enough for a single task file, keep everything in `tasks/main.yml`.

7. **Create meta/argument_specs.yml**

   - Define all role arguments with types, descriptions, required flags, and choices where applicable
   - Match the variables defined in `defaults/main.yml`

8. **Create meta/main.yml**

   - Role metadata: author, description, license, min_ansible_version, platforms

9. **Create handlers/main.yml**

   Generate actual handlers based on what the role manages, not just placeholders. Common patterns:
   - **Service roles** — create `Restart <role_name>` and `Reload <role_name>` handlers using `ansible.builtin.systemd_service` or `ansible.builtin.service`
   - **Configuration roles** — create handlers that validate config before restarting (e.g., `Validate <role_name> configuration` followed by
     `Restart <role_name>`)
   - **Roles with no handlers needed** — leave `handlers/main.yml` with a comment explaining no handlers are required

   All handler names MUST be prefixed with the role name. Wire up `notify:` in the corresponding tasks (e.g., template tasks notify restart handler).

10. **Create templates/**

    If any templates are created, include `{{ ansible_managed | comment }}` header and use `backup: true` in the corresponding task.

11. **Create README.md**

    Include:
    - Role description
    - Requirements
    - Role variables (all from defaults/main.yml, documented)
    - Example playbook
    - Idempotency designation
    - Check mode support statement
    - Rollback capabilities
    - License and author

12. **Validate post-scaffold**

    After creating all files, verify:
    - No dashes in the role name
    - All variables are role-name prefixed
    - Internal variables use `__` prefix
    - `argument_specs.yml` matches `defaults/main.yml`
    - All task names are imperative
    - All modules use FQCN
    - YAML uses 2-space indent and `true`/`false` booleans
    - `ansible_facts['...']` bracket notation is used everywhere

## Rules Source

If the rules are not available locally (no CLAUDE.md with Ansible rules or `redhat-cop-automation-good-practices-*.md`), fetch them from https://github.com/redhat-cop/automation-good-practices as a fallback.

## Output

Report what was created:

- Role path
- List of generated files
- Description of the role's purpose
- Variables available for customization
- Example usage in a playbook
