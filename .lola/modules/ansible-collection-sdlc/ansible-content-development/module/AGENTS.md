# Ansible Content Development

Module provides skills for developing and testing Ansible content following official best practices. Covers Python-based module development, YAML-based content authoring, and testing for both.

## When to Use

- **write-module skill**: Use the `write-module` skill to scaffold new Ansible modules following official best practices or review existing modules for compliance.
  Invoke with `/write-module` or when discussing module development, module scaffolding, or module best practices.

- **write-content skill**: Use the `write-content` skill to write or improve Ansible content (playbooks, tasks, handlers, templates, variables, inventories,
  argument specs) following Red Hat CoP automation good practices.
  Invoke with `/write-content` or when discussing Ansible content authoring, task writing, playbook structure, template creation, or variable conventions.

- **write-module-tests skill**: Use the `write-module-tests` skill to write unit tests (pytest) and integration tests (ansible-test) for Ansible modules.
  Invoke with `/write-module-tests` or when discussing module testing, mocking AnsibleModule, or writing test cases for modules.

- **write-content-tests skill**: Use the `write-content-tests` skill to write functional tests for Ansible roles and playbooks using Molecule.
  Emphasizes functional verification (does the automation achieve its goal?) over structural verification (did it create the file?).
  Invoke with `/write-content-tests` or when discussing Molecule, role testing, or writing verify playbooks.

## Authoring Priorities

- Prefer existing Ansible content before creating custom automation.
- Selection order:
  1. `ansible.builtin`
  2. vendor-supported collections, modules, plugins, and roles
  3. content from verified authors
  4. general Galaxy content
  5. custom collections, modules, plugins, and roles only as a last resort
- Avoid `ansible.builtin.shell`, `ansible.builtin.raw`, and ad hoc bash unless there is a clear, explicit justification that no safer module or plugin approach will work.
- Prefer purpose-built modules first, then `ansible.builtin.command` when shell features are not required.
- When using anything below `ansible.builtin` or creating custom content, explain why higher-trust options were not suitable.

## Configuration

**Optional Dependencies:**

- `ansible-test` - Used to validate modules and run unit/integration tests
- `ansible-lint` - Used to validate generated Ansible content
- `ansible-creator` - Used for scaffolding project structures (collections, roles, playbooks)
- `molecule` - Used for functional testing of roles and playbooks
- `podman` or `docker` - Used as container backend for Molecule and ansible-test

**Required Context:**

- Best practices are embedded in the skill reference materials:
  - `write-module` / `write-module-tests`: sourced from docs.ansible.com
  - `write-content` / `write-content-tests`: sourced from Red Hat CoP automation good practices and docs.ansible.com
- Collection identity (namespace, name, version) is read from `galaxy.yml` when available

**Companion Modules (optional but commonly referenced):**

- `ansible-collection-sdlc` - provides companion skills such as `run-tests`, `next-release`,
  `changelog-fragment`, `pr-review`, and `sanity`
- `ansible-role` - provides the `/ansible-scaffold-role` command
- `ansible-collection-standards` - provides the `/ansible-scaffold-collection` and
  `/ansible-cop-review` commands plus the `ansible-zen` skill

## Notes

- The write-module skill focuses on Python module files under `plugins/modules/`. The write-module-tests skill generates unit (pytest) and integration (ansible-test) tests for those modules.
- The write-content skill focuses on YAML-based Ansible content. The write-content-tests skill generates Molecule scenarios with functional verification for roles and playbooks.
- The testing skills emphasize functional testing: verify that automation achieves its intended outcome, not that built-in modules created files correctly.
- The authoring priority order above applies across every skill in this module, including scaffolding, review, and testing guidance.
- This module defines skills only. When a skill redirects to another tool, preserve whether that
  tool is a companion skill or a slash command from another module.
