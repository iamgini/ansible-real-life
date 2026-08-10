---
name: write-content
description: >-
  Write or improve Ansible content (playbooks, tasks, handlers, templates,
  variables, inventories, argument specs) following Red Hat CoP automation
  good practices. Use when writing new Ansible YAML content from a description,
  or improving existing content against best practices. Do NOT use for Python
  module development (use write-module), role/collection scaffolding (use the
  /ansible-scaffold-role or /ansible-scaffold-collection commands),
  compliance auditing (use the /ansible-cop-review command), or style review
  (use ansible-zen).
argument-hint: "[content-file-path or content-description]"
user-invocable: true
metadata:
  author: David Danielsson
  version: 1.0.0
---

# Skill: write-content

## Purpose

Write new Ansible YAML content or improve existing content following Red Hat CoP automation good practices and official Ansible documentation. This
is a hands-on writing assistant for individual pieces of content — tasks, handlers, playbooks, templates, variables, inventories, and argument specs.

## When to Invoke

TRIGGER when:

- A user asks to write, create, or generate a task, handler, playbook, template, variable definition, inventory structure, or argument spec
- A user asks to improve, fix, or update existing Ansible YAML content against best practices
- A user asks how to structure a specific piece of Ansible content correctly
- A user asks for help writing Jinja2 templates for Ansible
- A user asks about variable naming, placement, or precedence conventions
- A user asks to add proper tags, blocks, or error handling to existing content

DO NOT TRIGGER when:

- Writing Python modules (use `write-module` instead)
- Scaffolding an entire role (use the `/ansible-scaffold-role` command instead)
- Scaffolding an entire collection (use the `/ansible-scaffold-collection` command instead)
- Auditing code against CoP compliance rules (use the `/ansible-cop-review` command instead)
- Reviewing code for Zen/philosophy alignment (use `ansible-zen` instead)
- Reviewing a PR (use `pr-review` instead)
- Running tests (use `run-tests` instead)

## Important

- This skill focuses on YAML-based Ansible content, not Python files under `plugins/modules/`. If the user needs help with a Python module, redirect to the `write-module` skill.
- Always explain WHY a practice matters, not just WHAT to do. Users learn better when they understand the rationale.
- When improving, highlight what is already done well — not every review needs to find problems.
- For full project or role scaffolding, suggest the `/ansible-scaffold-collection` or
  `/ansible-scaffold-role` command from the companion modules. This skill writes
  individual content pieces, not entire directory structures.
- When generating content that belongs inside a role, always prefix variables with the role name.
- Prefer existing Ansible content before creating custom automation. Selection order:
  `ansible.builtin` -> vendor-supported content -> content from verified authors -> general Galaxy content -> custom collections/modules/plugins/roles only as a last resort.
- Avoid `ansible.builtin.shell`, `ansible.builtin.raw`, and ad hoc bash unless there is a clear,
  explicit justification that no safer module or plugin approach will work. Prefer purpose-built
  modules first, then `ansible.builtin.command` when shell features are not required.
- Primary source: Red Hat CoP automation good practices (https://redhat-cop.github.io/automation-good-practices/). Secondary source: docs.ansible.com. For the full set of rules and examples, see [reference.md](reference.md).

## Modes

Determine the mode based on the user's invocation and `$ARGUMENTS`:

- If `$ARGUMENTS` is a path to an existing `.yml`, `.yaml`, or `.j2` file, or an existing directory of Ansible content → **Mode 2: Improve**
- If `$ARGUMENTS` is a text description (no path separator or file does not exist) → **Mode 1: Write**
- If `$ARGUMENTS` is empty → ask the user whether they want to write new content or improve existing content
- If ambiguous → ask the user to clarify

---

### Mode 1: Write New Content

Generate best-practice-compliant Ansible content from a user description.

#### Step 1 — Determine Content Type

Identify what the user wants from their description:

| Content Type | Detection Signals | Primary Output |
|--------------|-------------------|----------------|
| Task / Task file | "task", "install", "configure", "ensure", action verbs | One or more YAML tasks |
| Handler | "handler", "restart", "reload", "notify" | Handler YAML block |
| Playbook | "playbook", "play", multiple hosts/roles | Full playbook YAML |
| Template (Jinja2) | "template", ".conf", ".cfg", config file names | `.j2` file content |
| Variable definitions | "variables", "defaults", "vars", "inventory vars" | YAML variable block |
| Inventory structure | "inventory", "hosts", "groups" | Inventory directory/file layout |
| Argument spec | "argument_specs", "meta/argument_specs", "validate role args" | `meta/argument_specs.yml` content |

If the type is unclear, ask the user.

#### Step 2 — Gather Context

Collect from the user (ask if not provided):

- **For tasks/handlers**: What action? Which service/package/resource? Target state? Role context (for variable naming)?
- **For playbooks**: Target hosts? What roles/tasks? Become needed? Tags?
- **For templates**: What application/service? Configuration parameters? File path on target?
- **For variables**: Role name (for prefixing)? Defaults vs vars? Platform-specific?
- **For inventory**: Environments? Group hierarchy? Static or dynamic?
- **For argument specs**: Role name? Which variables to validate?

If in a project directory, detect context automatically:

- Read `galaxy.yml` for namespace/collection info
- Read existing `defaults/main.yml` for variable naming patterns
- Read existing role structure to determine role name prefix

#### Step 3 — Select the Highest-Trust Existing Content

Before generating content, choose the safest suitable implementation source:

- First, check whether `ansible.builtin` already provides a suitable module, plugin, or role interface
- If builtin content is not sufficient, prefer vendor-supported content, then content from verified authors, then general Galaxy content
- Create custom collections, modules, plugins, or roles only when no suitable existing option meets the need
- Avoid `ansible.builtin.shell`, `ansible.builtin.raw`, and ad hoc bash unless there is a clear, explicit justification that no safer module or plugin approach will work
- Prefer purpose-built modules first, then `ansible.builtin.command` when shell features are not required
- When using anything below `ansible.builtin` or creating custom content, explain why higher-trust options were not suitable

#### Step 4 — Generate Content

Apply the content-type-specific template from the **Content Templates** section below. All generated content must follow every applicable rule from the **Style Rules** section.

#### Step 5 — Post-Write Guidance

After generating content:

1. Suggest running `ansible-lint <file>` to validate
2. Suggest running `ansible-playbook --syntax-check <playbook>` for playbooks
3. Suggest using the `write-content-tests` skill to generate Molecule functional tests
4. If the content is part of a role and no `meta/argument_specs.yml` exists, suggest creating one
5. If the user needs a full role, suggest the `/ansible-scaffold-role` command instead
6. If the user needs a full collection, suggest the `/ansible-scaffold-collection` command instead

---

### Mode 2: Improve Existing Content

Audit existing Ansible YAML content against best practices and suggest improvements.

#### Step 1 — Discover Scope

- If `$ARGUMENTS` is a file path, improve that file
- If `$ARGUMENTS` is a directory, focus on Ansible content roots such as `tasks/`, `handlers/`,
  `templates/`, `defaults/`, `vars/`, `meta/`, `playbooks/`, and inventory directories instead of
  every YAML or Jinja2 file in the repository
- If no arguments, ask which role, playbook, or content path the user wants reviewed instead of
  scanning the entire project by default

#### Step 2 — Read the Content

Read every file completely before forming any judgment. Determine the content type of each file (task file, handler, playbook, template, variable file, inventory, argument spec) from its path and structure.

#### Step 3 — Evaluate Against Checklist

Run through every category in the **Improvement Checklist** below. Collect findings per category. For the full detailed rules behind each check, consult [reference.md](reference.md).

#### Step 4 — Score

Rate overall compliance on a 1-10 scale:

- **9-10**: Exemplary — follows all practices, well-structured, clean style
- **7-8**: Good — follows most practices, minor issues only
- **5-6**: Acceptable — works but has notable gaps in naming, style, or structure
- **3-4**: Needs work — significant violations in multiple categories
- **1-2**: Non-compliant — fundamental structural or style issues

#### Step 5 — Top Recommendations

List the 3 most impactful changes that would improve compliance. Focus on changes that affect correctness, idempotency, or maintainability — not style preferences.

---

## Content Templates

### Task

```yaml
- name: Ensure nginx is installed
  ansible.builtin.dnf:
    name: "{{ webserver_packages }}"
    state: present
  become: true
  notify:
    - Restart nginx
  tags:
    - webserver
    - install
```

### Handler

```yaml
- name: webserver | Restart nginx
  ansible.builtin.systemd_service:
    name: "{{ webserver_service_name }}"
    state: restarted
  become: true
  listen:
    - Restart nginx
```

### Playbook

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: true
  gather_facts: true

  roles:
    - role: namespace.collection.webserver
      tags:
        - webserver
```

### Template (Jinja2)

```jinja2
{{ ansible_managed | comment }}

# Application configuration
server {
    listen {{ webserver_port | default(80) }};
    server_name {{ webserver_hostname }};

{% for location in webserver_locations %}
    location {{ location.path }} {
        proxy_pass {{ location.backend }};
    }
{% endfor %}
}
```

### Variable Definitions — defaults/main.yml

```yaml
---
# webserver - Web server configuration

# Packages to install.
webserver_packages:
  - nginx

# Service name for the web server.
webserver_service_name: nginx

# Whether the service should be enabled at boot.
webserver_service_enabled: true

# Port the web server listens on.
webserver_port: 80

# Variables without safe defaults (uncomment and set):
# webserver_ssl_certificate: /path/to/cert.pem
# webserver_ssl_key: /path/to/key.pem
```

### Variable Definitions — vars/main.yml

```yaml
---
# Internal constants - do not override
__webserver_config_path: /etc/nginx/nginx.conf
__webserver_config_owner: root
__webserver_config_group: root
__webserver_config_mode: "0644"
```

### Inventory Structure

```
inventory/
├── production/
│   ├── hosts.yml
│   ├── group_vars/
│   │   ├── all/
│   │   │   ├── vars.yml
│   │   │   └── vault.yml
│   │   └── webservers/
│   │       └── vars.yml
│   └── host_vars/
│       └── web01.example.com/
│           └── vars.yml
└── staging/
    ├── hosts.yml
    ├── group_vars/
    │   └── all/
    │       ├── vars.yml
    │       └── vault.yml
    └── host_vars/
```

### Argument Spec — meta/argument_specs.yml

```yaml
---
argument_specs:
  main:
    short_description: Configure web server
    description:
      - Install and configure a web server with reverse proxy support.
    options:
      webserver_packages:
        description:
          - List of packages to install for the web server.
        type: list
        elements: str
        default:
          - nginx
      webserver_service_name:
        description:
          - Name of the web server service.
        type: str
        default: nginx
      webserver_port:
        description:
          - Port the web server listens on.
        type: int
        default: 80
      webserver_ssl_certificate:
        description:
          - Path to the SSL certificate file.
          - Required when enabling HTTPS.
        type: path
```

---

## Style Rules

Keep the highest-signal authoring rules inline here. Use [reference.md](reference.md) for the
full rule set, rationale, and edge cases.

1. Two-space indentation
2. `.yml` extension (not `.yaml`)
3. YAML style for module arguments (not `key=value` inline)
4. `true`/`false` booleans
5. FQCN for all modules
6. Name all tasks, plays, and blocks in imperative mood
7. Always specify `state` explicitly when the module supports it
8. Use `loop:` rather than deprecated `with_*`
9. Prefer highest-trust existing content and prefer modules over `command`/`shell`/`raw`
10. Use `failed_when:` with specific conditions, not `ignore_errors: true`
11. Prefix sub-task names and role variables consistently (`<role_name>_...`, `__<role_name>_...`)
12. Put `{{ ansible_managed | comment }}` at the top of generated templates
13. Use `snake_case` for file names, variable names, and role names
14. Use `ansible_facts['...']` bracket notation, not legacy top-level fact variables

---

## Improvement Checklist

Use these categories as report headings. The detailed checks and examples for each category live in
[reference.md](reference.md).

| Category | What to Check |
|----------|---------------|
| YAML Style | Indentation, booleans, `.yml`, quoting, folding, line length |
| Naming | `snake_case`, imperative names, task prefixes, variable prefixes |
| Module Usage | FQCN, trust order, explicit `state`, `loop`, modules over `command`/`shell`/`raw` |
| Task Structure | Names, `become` scope, handlers, meaningful `tags` |
| Handlers | Role-prefixed names, `listen:` aliases, change-triggered actions |
| Templates | `ansible_managed` header, deterministic rendering, safe overwrite behavior |
| Variables | Defaults vs vars, safe defaults, role/internal prefixes |
| Playbook Structure | Role-centric logic, clean play structure, fact scoping |
| Inventory | Structured layout, var layering, functional group naming |
| Error Handling | `block`/`rescue`, `failed_when`, `changed_when`, justified `raw` use |
| Idempotency | No spurious changes on re-run |
| Argument Specs | `meta/argument_specs.yml` coverage and alignment with defaults |
| Tags | Meaningful, documented tags |
| Platform Support | `first_found`, platform var files, bracket fact notation |

---

## Output Format

### Write Mode

After generating content, output:

```
## Generated: <content type>

### Content
<the generated YAML or Jinja2 content>

### File Placement
`<suggested file path relative to role or project root>`

### Rules Applied
- <numbered list of key style rules applied from the Style Rules section>

### Next Steps
1. Run `ansible-lint <file>` to validate
2. <additional contextual suggestions>
```

### Improve Mode

```
## Content Review: <file path>

### Summary
<One-paragraph assessment: scope, quality, primary concerns.>

### Findings

#### Blockers (must fix)
- [CATEGORY] <file>:<line> — <description>

#### Warnings (should fix)
- [CATEGORY] <file>:<line> — <description>

#### Suggestions (optional improvements)
- [CATEGORY] <file>:<line> — <description>

### Checklist Status
| Category | Status | Notes |
|----------|--------|-------|
| YAML Style | PASS / FAIL / N/A | ... |
| Naming | PASS / FAIL / N/A | ... |
| Module Usage | PASS / FAIL / N/A | ... |
| Task Structure | PASS / FAIL / N/A | ... |
| Handlers | PASS / FAIL / N/A | ... |
| Templates | PASS / FAIL / N/A | ... |
| Variables | PASS / FAIL / N/A | ... |
| Playbook Structure | PASS / FAIL / N/A | ... |
| Inventory | PASS / FAIL / N/A | ... |
| Error Handling | PASS / FAIL / N/A | ... |
| Idempotency | PASS / FAIL / N/A | ... |
| Argument Specs | PASS / FAIL / N/A | ... |
| Tags | PASS / FAIL / N/A | ... |
| Platform Support | PASS / FAIL / N/A | ... |

### Score: X/10
<One sentence justification.>

### Top 3 Recommendations
1. ...
2. ...
3. ...
```

---

## Integration with Other Skills

Some integrations below come from companion Lola modules rather than this module alone.

| When | Tool |
|------|------|
| Write functional tests (Molecule) for the content | `write-content-tests` |
| Writing a Python module, not YAML content | `write-module` |
| Scaffolding an entire role structure | `/ansible-scaffold-role` |
| Scaffolding an entire collection | `/ansible-scaffold-collection` |
| Full CoP compliance audit across a project | `/ansible-cop-review` |
| Philosophical/style review | `ansible-zen` |
| Running tests after writing content | `run-tests` |
| Determining version for argument specs | `next-release` |
| Creating a changelog after content changes | `changelog-fragment` |
