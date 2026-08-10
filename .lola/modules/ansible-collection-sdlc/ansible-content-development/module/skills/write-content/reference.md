# Ansible Content Best Practices Reference

Supplementary detail for the `write-content` skill. Consult when writing or improving Ansible content. Primary source: Red Hat CoP automation good
practices (https://redhat-cop.github.io/automation-good-practices/). Secondary source: docs.ansible.com.

---

## 1. Content Structure and Hierarchy

### Four-tier hierarchy

Structure automation in four tiers:

- **Landscape**: The top level (e.g., a three-tier application). Represented by a Controller/AWX workflow or a master playbook.
- **Type**: Each managed host has exactly one type, deployed by a single playbook (e.g., web server, database server).
- **Function**: Represented by roles. Reusable units like "base Linux OS" or "web server." Write each function only once.
- **Component**: Subdivisions within a function-role for maintainability. Default representation is a task file within the role.

Functions exist for **reusability**; components exist for **maintainability and readability**.

### Role design principles

- Design roles around **functionality provided**, not the software implementing it (e.g., an NTP role, not a chrony role)
- Design for a "specific, guaranteed outcome" with limited scope
- Hide implementation details — present collections as low-code automation applications
- Author loosely coupled, hierarchical content — avoid hard dependencies on external roles or variables

### Task componentization

Split complex roles into component task files:

```yaml
# tasks/main.yml
- name: Include install tasks
  ansible.builtin.include_tasks:
    file: "{{ role_path }}/tasks/install.yml"

- name: Include configure tasks
  ansible.builtin.include_tasks:
    file: "{{ role_path }}/tasks/configure.yml"

- name: Include service tasks
  ansible.builtin.include_tasks:
    file: "{{ role_path }}/tasks/service.yml"
```

Prefix tasks in sub-task files with the filename:

```yaml
# tasks/install.yml
- name: install | Install required packages
  ansible.builtin.dnf:
    name: "{{ webserver_packages }}"
    state: present
  become: true
```

**Why:** Log output becomes `TASK [myrole : install | Install required packages]`, clearly indicating origin without needing verbosity level 2+.

---

## 2. YAML Style Rules

### Indentation

Always use two spaces. Never use tabs.

### File extension

Use `.yml`, not `.yaml`. This matches `ansible-galaxy init` convention and is the community standard.

### YAML-style module arguments

**Wrong:**

```yaml
- name: Copy file
  ansible.builtin.copy: src=foo.conf dest=/etc/foo.conf
```

**Right:**

```yaml
- name: Copy file
  ansible.builtin.copy:
    src: foo.conf
    dest: /etc/foo.conf
```

**Why:** YAML style is more readable, easier to diff, and avoids quoting ambiguity.

### Boolean values

**Wrong:** `yes`, `no`, `True`, `False`, `YES`, `NO`

**Right:** `true`, `false`

**Why:** YAML 1.2 only recognizes `true`/`false`. Other forms are YAML 1.1 legacy and can cause subtle parsing issues.

### String quoting

- Double quotes for YAML strings: `dest: "/etc/nginx/nginx.conf"`
- Single quotes only inside Jinja2 expressions: `"{{ my_dict['key'] }}"`
- No quotes for module keywords: `state: present` (not `state: "present"`)

### Folded scalars

**Wrong:** `>` (adds trailing newline)

**Right:** `>-` (no trailing newline)

**Why:** A trailing newline can cause subtle bugs in filenames, URLs, and values where whitespace matters.

```yaml
- name: Set a long message
  ansible.builtin.debug:
    msg: >-
      This is a very long message that spans
      multiple lines but will be joined into
      a single line without a trailing newline
```

### Line length

Keep lines under 120 characters (ansible-lint default). Use YAML folding or line continuation for long strings.

### Long when conditions

Break into a list — Ansible automatically ANDs list elements:

**Wrong:**

```yaml
when: ansible_facts['os_family'] == 'RedHat' and ansible_facts['distribution_major_version'] | int >= 8 and webserver_enabled
```

**Right:**

```yaml
when:
  - ansible_facts['os_family'] == 'RedHat'
  - ansible_facts['distribution_major_version'] | int >= 8
  - webserver_enabled
```

---

## 3. Task Writing Rules

### Name all tasks

Every task, play, and block must have a `name:` in imperative mood.

**Wrong:** `- ansible.builtin.dnf: name=nginx state=present`

**Right:**

```yaml
- name: Install nginx
  ansible.builtin.dnf:
    name: nginx
    state: present
```

**Why:** Named tasks produce readable output. Unnamed tasks show only the module name, making logs hard to follow.

### FQCN for all modules

Always use Fully Qualified Collection Names. See section 12 for a complete reference table.

**Wrong:** `copy:`, `template:`, `service:`

**Right:** `ansible.builtin.copy:`, `ansible.builtin.template:`, `ansible.builtin.service:`

**Why:** Avoids ambiguity when multiple collections provide modules with the same short name.

### Choose the highest-trust existing content first

Before adding a new role, task, plugin, or module to solve a problem, use the highest-trust existing content that fits:

1. `ansible.builtin`
2. vendor-supported collections, modules, plugins, and roles
3. content from verified authors
4. general Galaxy content
5. custom collections, modules, plugins, and roles only as a last resort

When using anything below `ansible.builtin` or creating custom content, explain why higher-trust options were not suitable.

**Why:** Reusing higher-trust content reduces maintenance burden, security risk, and support ambiguity while avoiding reinvention of already-solved automation problems.

### Explicit state

Always specify `state` explicitly — different modules have different defaults.

```yaml
- name: Install nginx
  ansible.builtin.dnf:
    name: nginx
    state: present  # explicit, not relying on module default
```

### Use loop, not with_*

**Wrong:**

```yaml
- name: Install packages
  ansible.builtin.dnf:
    name: "{{ item }}"
    state: present
  with_items: "{{ packages }}"
```

**Right:**

```yaml
- name: Install packages
  ansible.builtin.dnf:
    name: "{{ packages }}"
    state: present
```

Or when individual iteration is needed:

```yaml
- name: Create users
  ansible.builtin.user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
  loop: "{{ users }}"
```

**Why:** `with_*` constructs are deprecated. `loop:` is the modern replacement. Many modules also accept lists directly.

### Prefer modules over command/shell/raw

1. First choice: a purpose-built module or plugin from the highest-trust source available
2. Second choice: `ansible.builtin.command` (no shell features)
3. Last resort: `ansible.builtin.shell` (when shell features are required)
4. `ansible.builtin.raw` only for bootstrapping or environments where normal module execution cannot work yet

When using `command`, `shell`, or `raw`, add a comment explaining why no safer module or plugin exists. Always set `changed_when:` on `command` and `shell` tasks:

```yaml
- name: Check if application is running
  ansible.builtin.command:
    cmd: pgrep -f myapp
  register: app_check
  changed_when: false
  failed_when: false
```

### failed_when instead of ignore_errors

**Wrong:**

```yaml
- name: Check service status
  ansible.builtin.command:
    cmd: systemctl is-active myservice
  ignore_errors: true
```

**Right:**

```yaml
- name: Check service status
  ansible.builtin.command:
    cmd: systemctl is-active myservice
  register: service_status
  changed_when: false
  failed_when: service_status.rc not in [0, 3]
```

**Why:** `ignore_errors` silences ALL errors, including unexpected ones. `failed_when` lets you define exactly which exit codes are acceptable.

### changed_when on command/shell

`command` and `shell` always report `changed: true`. Override with `changed_when:`:

```yaml
- name: Run database migration
  ansible.builtin.command:
    cmd: /opt/app/migrate.sh
  register: migrate_result
  changed_when: "'Applied' in migrate_result.stdout"
```

### delegate_to, not local_action

**Wrong:** `local_action: ansible.builtin.command echo hello`

**Right:**

```yaml
- name: Run command locally
  ansible.builtin.command:
    cmd: echo hello
  delegate_to: localhost
```

### Debug verbosity

Always set `verbosity:` on debug tasks to avoid cluttering production output:

```yaml
- name: Show variable value
  ansible.builtin.debug:
    var: my_variable
    verbosity: 2
```

### Block for error handling

Use `block`/`rescue`/`always` for structured error handling:

```yaml
- name: Deploy application
  block:
    - name: Download application archive
      ansible.builtin.get_url:
        url: "{{ app_download_url }}"
        dest: /tmp/app.tar.gz

    - name: Extract application
      ansible.builtin.unarchive:
        src: /tmp/app.tar.gz
        dest: /opt/app
        remote_src: true

  rescue:
    - name: Log deployment failure
      ansible.builtin.debug:
        msg: "Deployment failed: {{ ansible_failed_result.msg }}"

  always:
    - name: Clean up temporary files
      ansible.builtin.file:
        path: /tmp/app.tar.gz
        state: absent
```

---

## 4. Handler Writing Rules

### Naming

Prefix handler names with the role name for clarity:

```yaml
- name: webserver | Restart nginx
  ansible.builtin.systemd_service:
    name: "{{ webserver_service_name }}"
    state: restarted
  become: true
  listen:
    - Restart nginx
```

### Use listen for decoupling

Use `listen:` so multiple handlers can respond to the same trigger, and tasks notify a logical name rather than a specific handler:

```yaml
# handlers/main.yml
- name: webserver | Restart nginx service
  ansible.builtin.systemd_service:
    name: nginx
    state: restarted
  listen:
    - Restart web stack

- name: webserver | Clear nginx cache
  ansible.builtin.file:
    path: /var/cache/nginx
    state: absent
  listen:
    - Restart web stack
```

### Validation before restart

When restarting a service after config changes, validate the config first:

```yaml
- name: Validate nginx configuration
  ansible.builtin.command:
    cmd: nginx -t
  changed_when: false
  listen:
    - Restart nginx

- name: webserver | Restart nginx
  ansible.builtin.systemd_service:
    name: nginx
    state: restarted
  listen:
    - Restart nginx
```

### Handlers are for change-triggered actions only

Do not use handlers for actions that should always run. Use `post_tasks` or regular tasks for that.

---

## 5. Playbook Writing Rules

### Keep playbooks simple

Playbooks should be a list of roles — put logic in roles, not playbooks.

**Wrong:**

```yaml
- hosts: webservers
  tasks:
    - name: Install nginx
      ansible.builtin.dnf:
        name: nginx
        state: present
    - name: Copy config
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
    - name: Start nginx
      ansible.builtin.service:
        name: nginx
        state: started
```

**Right:**

```yaml
- name: Configure web servers
  hosts: webservers
  become: true

  roles:
    - role: namespace.collection.webserver
      tags:
        - webserver
```

### Never mix roles and tasks sections

Do not use both `roles:` and `tasks:` in the same play. The execution order between them is not obvious and leads to confusion.

### gather_facts and gather_subset

Specify `gather_subset` when full facts are not needed — reduces execution time:

```yaml
- name: Configure network
  hosts: all
  gather_facts: true
  gather_subset:
    - "!all"
    - "!min"
    - network
```

### Play naming

Name plays in imperative mood: `"Configure web servers"`, not `"Web server configuration"`.

---

## 6. Template (Jinja2) Writing Rules

### ansible_managed header

Every template must start with `{{ ansible_managed | comment }}`:

```jinja2
{{ ansible_managed | comment }}

# nginx configuration
server {
    listen {{ webserver_port }};
}
```

**Why:** Marks the file as managed by Ansible, warning manual editors that their changes will be overwritten.

### backup: true

Always use `backup: true` on template tasks until users request otherwise:

```yaml
- name: Deploy nginx configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: "0644"
    backup: true
  notify:
    - Restart nginx
```

### No timestamps

Never include dynamic timestamps like `"Last modified: {{ date }}"`. This causes the template to report changes on every run, breaking idempotency.

### Jinja2 quoting

Use single quotes inside Jinja2 expressions:

```jinja2
{{ my_dict['key'] }}
{{ my_var | default('fallback_value') }}
```

### Whitespace control

Use `{%- -%}` for whitespace trimming when needed to avoid blank lines:

```jinja2
{% for vhost in webserver_vhosts %}
server {
    server_name {{ vhost.name }};
    listen {{ vhost.port | default(80) }};
}
{% endfor %}
```

---

## 7. Variable Conventions

### Naming

- `snake_case` for all variable names
- Role variable prefix: `<role_name>_variable_name`
- Internal variable double-underscore prefix: `__<role_name>_internal_var`
- No special characters other than underscores

**Why role prefixing matters:** All role variables, registered variables, and custom facts share one global namespace. Without prefixing, a common
name like `packages` in one role silently overwrites the same name from another role.

### Placement

| Where | What goes here | Precedence |
|-------|----------------|------------|
| `defaults/main.yml` | All user-facing variables with safe defaults | Lowest — easily overridden |
| `vars/main.yml` | Internal constants separating code from data | High — hard to override |
| `vars/<Platform>.yml` | Platform-specific constants (e.g., `vars/RedHat.yml`) | High |
| Inventory `group_vars/` | Desired-state variables for the environment | Medium |
| Inventory `host_vars/` | Host-specific overrides | Medium-high |

### defaults/main.yml rules

- Every user-facing variable must have an entry
- Variables without safe defaults: present but commented out with a description
- Serves as documentation of the role's interface
- Do not use the Jinja2 `default` filter in tasks as a substitute for `defaults/main.yml` (the filter is fine for optional dictionary keys)
- Do not give defaults when there is no meaningful default — let the role fail. Comment the variable out.

### vars/main.yml rules

- Internal constants only, prefixed with `__<role_name>_`
- Never put user-facing defaults here — high precedence makes them hard to override
- For required packages: `__<role_name>_packages` in `vars/main.yml`; for optional extras: `<role_name>_extra_packages` defaulting to `[]` in `defaults/main.yml`

### Variable precedence (simplified 8 levels)

1. **Role defaults** (`defaults/main.yml`) — lowest
2. **Inventory vars** (`group_vars/`, `host_vars/`) — desired state
3. **Host facts** (`ansible_facts`) — current state
4. **Role vars** (`vars/main.yml`) — constants
5. **Scoped vars** (block/task `vars:`) — local scope
6. **Runtime vars** (`register`/`set_fact`) — current automation state
7. **Scoped params** (role/include params) — avoid to limit surprises
8. **Extra vars** (`-e`) — overrides everything

### Facts vs variables

- **As-Is (facts)**: Discovered information from the current environment
- **To-Be (variables)**: Managed information expressing desired state

Never mix them. A fact tells you what IS; a variable tells you what SHOULD BE. Using facts for desired state means automation cannot correct drift.

### Vault layering

Keep variable names visible while values stay encrypted:

```
group_vars/
└── webservers/
    ├── vars.yml      # db_config: "{{ vault_db_config }}"
    └── vault.yml     # vault_db_config: <ansible-vault encrypted>
```

Reference `vault_`-prefixed variables from `vars.yml` so names remain searchable.

### Bracket notation for facts

**Wrong:** `ansible_os_family`, `ansible_distribution`

**Right:** `ansible_facts['os_family']`, `ansible_facts['distribution']`

**Why:** Dot notation (`ansible_facts.name`) can conflict with Python attribute access. Bracket notation is explicit and safe.

---

## 8. Inventory Structure

### Directory layout

```
inventory/
├── production/
│   ├── hosts.yml                    # Groups and hosts only — no variables
│   ├── group_vars/
│   │   ├── all/
│   │   │   ├── vars.yml             # Non-sensitive variables
│   │   │   └── vault.yml            # Encrypted sensitive variables
│   │   └── webservers/
│   │       └── vars.yml             # Role-specific variables for this group
│   └── host_vars/
│       └── web01.example.com/
│           └── vars.yml
├── staging/
│   └── ...
└── development/
    └── ...
```

### Rules

- No variable definitions in the hosts file — keep it to group membership only
- Name variable files after the role they configure; use `vars.yml` for general variables
- Separate environments into distinct inventory directories
- Group hosts by function (`webservers`, `dbservers`), not by hostname patterns
- Use dynamic inventory for cloud environments
- Do not create host lists to loop over — use inventory groups and the `hosts:` directive

---

## 9. Argument Specs

### Format

```yaml
# meta/argument_specs.yml
---
argument_specs:
  main:
    short_description: One-line description without trailing period
    description:
      - Full sentence description of the role.
    options:
      role_name_variable:
        description:
          - What this variable controls.
        type: str
        required: true
      role_name_optional:
        description:
          - Optional variable with a default.
        type: int
        default: 80
        choices:
          - 80
          - 443
          - 8080
```

### Rules

- `short_description` must be a string, not a list, and must not end with a period
- Every option needs `description` and `type`
- Must match `defaults/main.yml` — if a variable has a default there, it must be documented here
- Use `elements` when `type: list`
- Use `options` (suboptions) when `type: dict`
- Validation runs at role start — fails fast on incorrect input

---

## 10. Tags

### Naming strategy

- Tags named after roles: `webserver`, `database`, `monitoring`
- Tags for meaningful operations: `deploy`, `configure`, `backup`
- Never create tags that are destructive when used alone

### Rules

- Document all tags in the role's README
- Users should not need to learn tag sequences — one tag should achieve a meaningful result
- When using `include_role`, tags must be specified both on the task and via `apply:`
- Tag at the role inclusion level in playbooks, not on individual tasks within roles

---

## 11. Platform Support Patterns

### Variable loading

Load platform-specific variables from least specific to most specific:

```yaml
# tasks/main.yml
- name: Set platform-specific variables
  ansible.builtin.include_vars:
    file: "{{ item }}"
  loop: "{{ __platform_var_files }}"
  when: item is file
  vars:
    __platform_var_files:
      - "{{ role_path }}/vars/{{ ansible_facts['os_family'] }}.yml"
      - "{{ role_path }}/vars/{{ ansible_facts['distribution'] }}.yml"
      - >-
        {{ role_path }}/vars/{{ ansible_facts['distribution'] }}_
        {{- ansible_facts['distribution_major_version'] }}.yml
```

### Task loading

Use `lookup('first_found')` for platform-specific tasks:

```yaml
- name: Include platform-specific tasks
  ansible.builtin.include_tasks:
    file: "{{ lookup('first_found', params) }}"
  vars:
    params:
      files:
        - "{{ ansible_facts['distribution'] }}_{{ ansible_facts['distribution_major_version'] }}.yml"
        - "{{ ansible_facts['distribution'] }}.yml"
        - "{{ ansible_facts['os_family'] }}.yml"
        - default.yml
      paths:
        - "{{ role_path }}/tasks"
```

### Platform variable files

```yaml
# vars/RedHat.yml
---
__webserver_package_name: nginx
__webserver_config_path: /etc/nginx/nginx.conf

# vars/Debian.yml
---
__webserver_package_name: nginx-full
__webserver_config_path: /etc/nginx/nginx.conf
```

---

## 12. Common FQCN Reference

| Short Name | FQCN |
|------------|------|
| `copy` | `ansible.builtin.copy` |
| `template` | `ansible.builtin.template` |
| `file` | `ansible.builtin.file` |
| `service` | `ansible.builtin.service` |
| `systemd` / `systemd_service` | `ansible.builtin.systemd_service` |
| `package` | `ansible.builtin.package` |
| `yum` | `ansible.builtin.yum` |
| `apt` | `ansible.builtin.apt` |
| `dnf` | `ansible.builtin.dnf` |
| `pip` | `ansible.builtin.pip` |
| `user` | `ansible.builtin.user` |
| `group` | `ansible.builtin.group` |
| `command` | `ansible.builtin.command` |
| `shell` | `ansible.builtin.shell` |
| `raw` | `ansible.builtin.raw` |
| `script` | `ansible.builtin.script` |
| `debug` | `ansible.builtin.debug` |
| `assert` | `ansible.builtin.assert` |
| `fail` | `ansible.builtin.fail` |
| `set_fact` | `ansible.builtin.set_fact` |
| `include_tasks` | `ansible.builtin.include_tasks` |
| `import_tasks` | `ansible.builtin.import_tasks` |
| `include_role` | `ansible.builtin.include_role` |
| `import_role` | `ansible.builtin.import_role` |
| `include_vars` | `ansible.builtin.include_vars` |
| `lineinfile` | `ansible.builtin.lineinfile` |
| `blockinfile` | `ansible.builtin.blockinfile` |
| `uri` | `ansible.builtin.uri` |
| `get_url` | `ansible.builtin.get_url` |
| `unarchive` | `ansible.builtin.unarchive` |
| `cron` | `ansible.builtin.cron` |
| `stat` | `ansible.builtin.stat` |
| `wait_for` | `ansible.builtin.wait_for` |
| `setup` | `ansible.builtin.setup` |
| `gather_facts` | `ansible.builtin.gather_facts` |
| `group_by` | `ansible.builtin.group_by` |
| `hostname` | `ansible.builtin.hostname` |
| `firewalld` | `ansible.posix.firewalld` |
| `seboolean` | `ansible.posix.seboolean` |
| `sysctl` | `ansible.posix.sysctl` |
| `mount` | `ansible.posix.mount` |
| `authorized_key` | `ansible.posix.authorized_key` |

---

## 13. Anti-Patterns

### Using key=value style

**Wrong:**

```yaml
- name: Copy file
  ansible.builtin.copy: src=foo.conf dest=/etc/foo.conf owner=root mode=0644
```

**Right:**

```yaml
- name: Copy file
  ansible.builtin.copy:
    src: foo.conf
    dest: /etc/foo.conf
    owner: root
    mode: "0644"
```

**Why:** YAML style is more readable, easier to diff, and avoids quoting ambiguity. Mode values need quoting to prevent octal interpretation.

### Using yes/no instead of true/false

**Wrong:** `become: yes`, `enabled: no`

**Right:** `become: true`, `enabled: false`

**Why:** YAML 1.2 only defines `true`/`false`. Other boolean forms are YAML 1.1 legacy.

### Using short module names

**Wrong:** `copy:`, `service:`, `template:`

**Right:** `ansible.builtin.copy:`, `ansible.builtin.service:`, `ansible.builtin.template:`

**Why:** Short names are ambiguous when multiple collections are installed.

### Omitting state

**Wrong:**

```yaml
- name: Install nginx
  ansible.builtin.dnf:
    name: nginx
```

**Right:**

```yaml
- name: Install nginx
  ansible.builtin.dnf:
    name: nginx
    state: present
```

**Why:** Default `state` varies across modules. Being explicit removes ambiguity.

### Using with_items instead of loop

**Wrong:** `with_items: "{{ packages }}"`

**Right:** `loop: "{{ packages }}"` or pass the list directly to the module

**Why:** `with_*` constructs are deprecated in favor of `loop`.

### Using ignore_errors instead of failed_when

**Wrong:** `ignore_errors: true`

**Right:** `failed_when: result.rc not in [0, 1]`

**Why:** `ignore_errors` silences all errors. `failed_when` lets you define exactly which failures are acceptable.

### Mixing roles and tasks in a playbook

**Wrong:**

```yaml
- hosts: all
  roles:
    - common
  tasks:
    - name: Do something
      ansible.builtin.debug:
        msg: "Hello"
```

**Right:**

```yaml
- hosts: all
  roles:
    - common
    - my_other_role
```

**Why:** The execution order between `roles:` and `tasks:` is not obvious and leads to confusion.

### User-facing variables in vars/main.yml

**Wrong:** Putting `webserver_port: 80` in `vars/main.yml`

**Right:** Put it in `defaults/main.yml`

**Why:** `vars/main.yml` has high precedence and is hard for users to override. `defaults/main.yml` has the lowest role precedence and is designed to be overridden.

### Not prefixing role variables

**Wrong:** `packages`, `service_name`, `config_path`

**Right:** `webserver_packages`, `webserver_service_name`, `webserver_config_path`

**Why:** All role variables share one global namespace. Without prefixing, variable names from different roles silently overwrite each other.

### Missing ansible_managed in templates

**Wrong:** Template file without any managed-by header

**Right:** Start every template with `{{ ansible_managed | comment }}`

**Why:** Warns manual editors that the file is managed by automation and their changes will be overwritten.

### Using ansible_os_family instead of ansible_facts['os_family']

**Wrong:** `when: ansible_os_family == 'RedHat'`

**Right:** `when: ansible_facts['os_family'] == 'RedHat'`

**Why:** The `ansible_*` shorthand can conflict with other variable sources. Bracket notation on `ansible_facts` is explicit and safe.

### Using shell when command suffices

**Wrong:**

```yaml
- name: List files
  ansible.builtin.shell:
    cmd: ls /tmp
```

**Right:**

```yaml
- name: List files
  ansible.builtin.command:
    cmd: ls /tmp
```

**Why:** `shell` invokes a full shell interpreter and is vulnerable to injection. `command` runs the command directly without shell processing.

### Creating custom content before exhausting existing options

**Wrong:** Writing a custom module, plugin, or role before checking whether `ansible.builtin`, vendor-supported content, content from verified authors, or general Galaxy content already solves the problem.

**Right:** Reuse the highest-trust existing content first, and create custom content only when there is a clear gap that existing options do not cover safely or maintainably.

**Why:** Reinventing existing automation increases maintenance cost and risk without improving the user experience.

### Using .yaml extension

**Wrong:** `tasks/main.yaml`, `defaults/main.yaml`

**Right:** `tasks/main.yml`, `defaults/main.yml`

**Why:** `.yml` is the community convention established by `ansible-galaxy init` and used consistently across the Ansible ecosystem.

---

## 14. Tooling Integration

### ansible-lint

Validates Ansible content against best practices and style rules:

```bash
ansible-lint playbook.yml
ansible-lint roles/my_role/
```

Common rule IDs:

| Rule | What it checks |
|------|----------------|
| `yaml` | YAML syntax and style (indentation, line length, booleans) |
| `name` | Task and play naming (must be present, must be descriptive) |
| `fqcn` | Fully qualified collection names required |
| `no-changed-when` | `changed_when` required on command/shell tasks |
| `command-instead-of-module` | Prefer modules over command/shell |
| `command-instead-of-shell` | Prefer command over shell |
| `no-handler` | Tasks that should use handlers |
| `risky-shell-pipe` | Shell tasks with pipes should use `pipefail` |
| `no-jinja-when` | Don't use `{{ }}` in `when:` conditions |

### ansible-playbook --syntax-check

Quick validation that playbook YAML is parseable:

```bash
ansible-playbook --syntax-check playbook.yml
```

### ansible-creator

Use `ansible-creator` for scaffolding full project structures:

```bash
# Scaffold a new collection
ansible-creator init collection namespace.name /path

# Add a role to an existing collection
ansible-creator add resource role role_name /path/to/collection

# Scaffold a playbook project
ansible-creator init playbook namespace.name /path

# Add a plugin to a collection
ansible-creator add plugin filter my_filter /path/to/collection
```

Install with `pip install ansible-creator` or use the `ansible-dev-tools` devcontainer.

For full role scaffolding with interactive variable builders and task componentization, use the `ansible-scaffold-role` command instead.

### yamllint

Configure `.yamllint` for Ansible projects:

```yaml
---
extends: default
rules:
  line-length:
    max: 120
  truthy:
    allowed-values:
      - "true"
      - "false"
  comments:
    min-spaces-from-content: 1
  braces:
    max-spaces-inside: 1
  octal-values:
    forbid-implicit-octal: true
```
