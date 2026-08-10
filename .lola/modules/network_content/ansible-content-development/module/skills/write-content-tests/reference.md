# Ansible Content Testing Reference (Molecule)

Supplementary detail for the `write-content-tests` skill. Consult when writing or improving Molecule tests for Ansible roles and playbooks. Primary source: docs.ansible.com/projects/molecule/.

---

## 1. Functional vs Structural Testing

This is the most important concept in this reference. Every test decision should start here.

### The principle

Test the **intended outcome** of your automation, not the implementation details. Built-in Ansible modules (ansible.builtin.template,
ansible.builtin.copy, ansible.builtin.file, etc.) are already tested by the Ansible project. Your tests should verify that the *system behaves
correctly* after your automation runs.

### Examples by automation type

#### Package and service management

**Structural (avoid):**

```yaml
- name: Check nginx is installed
  ansible.builtin.package_facts:
    manager: auto
- name: Assert nginx installed
  ansible.builtin.assert:
    that: "'nginx' in ansible_facts.packages"
```

**Functional (correct):**

```yaml
- name: Verify nginx responds
  ansible.builtin.uri:
    url: "http://localhost:80"
    status_code: 200
  register: nginx_check
- name: Assert nginx is serving
  ansible.builtin.assert:
    that: nginx_check.status == 200
    fail_msg: "Nginx is not responding on port 80"
```

**Why:** If the role installs nginx and starts it, the meaningful question is "does nginx serve requests?" — not "is the package installed?"

#### User and permission management

**Structural (avoid):**

```yaml
- name: Check sudoers file exists
  ansible.builtin.stat:
    path: /etc/sudoers.d/deploy
  register: sudoers_file
- name: Assert file exists
  ansible.builtin.assert:
    that: sudoers_file.stat.exists
```

**Functional (correct):**

```yaml
- name: Check deploy user sudo permissions
  ansible.builtin.command:
    cmd: sudo -l -U deploy
  register: sudo_check
  changed_when: false
- name: Assert deploy user can restart the app
  ansible.builtin.assert:
    that:
      - "'NOPASSWD: /usr/bin/systemctl restart myapp' in sudo_check.stdout"
    fail_msg: "Deploy user missing expected sudo permissions"
- name: Assert deploy user cannot reboot
  ansible.builtin.assert:
    that:
      - "'/usr/sbin/reboot' not in sudo_check.stdout"
    fail_msg: "Deploy user has unexpected reboot permission"
```

**Why:** The goal is correct permissions, not file existence. A file can exist with wrong content.

#### Configuration management

**Structural (avoid):**

```yaml
- name: Check config file content
  ansible.builtin.slurp:
    src: /etc/myapp/config.yml
  register: config_content
- name: Assert config has expected key
  ansible.builtin.assert:
    that: "'database_host' in (config_content.content | b64decode)"
```

**Functional (correct):**

```yaml
- name: Verify application connects to database
  ansible.builtin.command:
    cmd: /opt/myapp/bin/healthcheck --check-db
  register: health
  changed_when: false
- name: Assert database connection works
  ansible.builtin.assert:
    that: health.rc == 0
    fail_msg: "Application cannot connect to database: {{ health.stderr }}"
```

**Why:** If the config is correct, the application works. If the application works, the config is correct. Test the thing that matters.

#### Firewall rules

**Structural (avoid):**

```yaml
- name: List firewall rules
  ansible.builtin.command:
    cmd: firewall-cmd --list-all
  register: fw_rules
- name: Assert port 443 is open
  ansible.builtin.assert:
    that: "'443/tcp' in fw_rules.stdout"
```

**Functional (correct):**

```yaml
- name: Verify HTTPS port is accessible
  ansible.builtin.wait_for:
    host: localhost
    port: 443
    timeout: 10
  register: port_check
- name: Assert port is open
  ansible.builtin.assert:
    that: port_check is not failed
    fail_msg: "HTTPS port 443 is not accessible"
```

---

## 2. Molecule Fundamentals

### What Molecule is

Molecule is an Ansible testing framework that leverages standard Ansible features (inventory, playbooks, collections) to provide flexible testing
workflows. It manages the entire test lifecycle: creating infrastructure, running automation, verifying results, and tearing everything down.

### Installation

```bash
pip install molecule
```

For container-based testing (recommended):

```bash
pip install molecule containers.podman
```

### CLI commands

| Command | Purpose |
|---------|---------|
| `molecule test` | Run the full test lifecycle |
| `molecule create` | Create test infrastructure only |
| `molecule converge` | Run the automation under test |
| `molecule verify` | Run verify playbook only |
| `molecule idempotence` | Re-run converge and check for zero changes |
| `molecule destroy` | Tear down test infrastructure |
| `molecule login` | SSH into a test instance for debugging |
| `molecule test --parallel` | Run all scenarios simultaneously |
| `molecule test -s <name>` | Run a specific scenario |

---

## 3. Scenario Structure

### Standalone role

```
molecule/
└── default/
    ├── molecule.yml      # Scenario configuration
    ├── create.yml        # Provision containers
    ├── prepare.yml       # Install prerequisites (optional)
    ├── converge.yml      # Run the role/playbook
    ├── verify.yml        # Functional assertions
    ├── cleanup.yml       # Remove test artifacts (optional)
    └── destroy.yml       # Tear down containers
```

### Collection (with shared state)

```
extensions/molecule/
├── config.yml            # Shared base configuration
├── inventory.yml         # Shared inventory
├── default/
│   ├── molecule.yml      # Overrides: create + destroy only
│   ├── create.yml
│   └── destroy.yml
├── role1/
│   ├── molecule.yml      # Empty — inherits config.yml
│   ├── converge.yml
│   └── verify.yml
└── role2/
    ├── molecule.yml
    ├── converge.yml
    └── verify.yml
```

---

## 4. Test Lifecycle

The full default sequence:

```
dependency → cleanup → destroy → syntax → create → prepare → converge → idempotence → side_effect → verify → cleanup → destroy
```

Recommended sequence for most roles:

```yaml
scenario:
  test_sequence:
    - dependency
    - create
    - prepare
    - converge
    - idempotence
    - verify
    - cleanup
    - destroy
```

Each phase maps to a playbook file in the scenario directory.

---

## 5. Writing verify.yml

### Structure

```yaml
---
- name: Verify
  hosts: all
  gather_facts: true
  become: true
  tasks:
    # Functional assertions here
```

### Assertion patterns

Always use `ansible.builtin.assert` with `fail_msg`:

```yaml
- name: Assert service is healthy
  ansible.builtin.assert:
    that:
      - service_check.status == 200
    fail_msg: >-
      Service health check failed.
      Expected status 200, got {{ service_check.status }}.
```

### Non-destructive checking

Use `check_mode: true` and `failed_when: false` for checks that should not modify state:

```yaml
- name: Check service state without modifying
  ansible.builtin.systemd_service:
    name: nginx
    state: started
  check_mode: true
  register: service_state
  failed_when: false

- name: Assert service is running
  ansible.builtin.assert:
    that: service_state is not changed
    fail_msg: "Nginx service is not running"
```

---

## 6. Converge Patterns

### For standalone roles

```yaml
---
- name: Converge
  hosts: all
  become: true
  roles:
    - role: role_name
```

### For collection roles

```yaml
---
- name: Converge
  hosts: all
  become: true
  tasks:
    - name: Include role under test
      ansible.builtin.include_role:
        name: namespace.collection.role_name
```

### For playbooks

```yaml
---
- name: Converge
  ansible.builtin.import_playbook: ../../playbook_name.yml
```

### With variables

```yaml
---
- name: Converge
  hosts: all
  become: true
  vars:
    webserver_port: 8080
    webserver_ssl_enabled: false
  tasks:
    - name: Include role under test
      ansible.builtin.include_role:
        name: namespace.collection.webserver
```

---

## 7. Idempotency Testing

### What it means

Running the automation twice with the same inputs must produce the same state. The second run must report zero changes.

### How Molecule checks it

The `idempotence` action re-runs the converge playbook and fails if any task reports `changed`.

### Common idempotency failures

- `command`/`shell` tasks without `changed_when: false`
- Template tasks with dynamic timestamps
- Package install tasks where the package manager reports changes on re-run
- Service restart handlers triggered unnecessarily

### Fixing idempotency issues

These are bugs in the role, not in the test. The test correctly identifies non-idempotent behavior.

---

## 8. Collection Testing with Shared State

### config.yml (shared configuration)

```yaml
---
ansible:
  executor:
    args:
      ansible_playbook:
        - --inventory=${MOLECULE_SCENARIO_DIRECTORY}/../inventory.yml

scenario:
  test_sequence:
    - prepare
    - converge
    - verify
    - idempotence
    - verify
    - cleanup

shared_state: true
```

### Default scenario (lifecycle manager)

```yaml
# default/molecule.yml — overrides test_sequence
---
scenario:
  test_sequence:
    - create
    - destroy
```

### Component scenarios

Leave `molecule.yml` empty to inherit everything from `config.yml`.

### Running

```bash
molecule test --all --command-borders --report
```

---

## 9. Platform Testing

### Multi-platform inventory

```yaml
all:
  children:
    redhat:
      hosts:
        centos9:
          container_image: quay.io/centos/centos:stream9
    debian:
      hosts:
        ubuntu2204:
          container_image: docker.io/ubuntu:22.04
```

### Common container images

| Platform | Image |
|----------|-------|
| CentOS Stream 9 | `quay.io/centos/centos:stream9` |
| Rocky Linux 9 | `quay.io/rockylinux/rockylinux:9` |
| Ubuntu 22.04 | `docker.io/ubuntu:22.04` |
| Debian 12 | `docker.io/debian:12` |
| Fedora | `registry.fedoraproject.org/fedora:latest` |

### Podman setup

Ensure Podman is installed and the user has permissions:

```bash
podman --version
podman run --rm quay.io/centos/centos:stream9 cat /etc/os-release
```

---

## 10. Functional Verification Patterns

### Service responds on port

```yaml
- name: Verify service responds on expected port
  ansible.builtin.uri:
    url: "http://localhost:{{ service_port }}"
    status_code: 200
    return_content: true
  register: response

- name: Assert response contains expected content
  ansible.builtin.assert:
    that:
      - response.status == 200
    fail_msg: "Service not responding on port {{ service_port }}"
```

### User has correct access

```yaml
- name: Verify user exists with correct groups
  ansible.builtin.command:
    cmd: id {{ test_user }}
  register: user_info
  changed_when: false

- name: Assert user is in expected groups
  ansible.builtin.assert:
    that:
      - "'wheel' in user_info.stdout"
    fail_msg: "User {{ test_user }} not in wheel group"
```

### DNS resolution works

```yaml
- name: Verify hostname resolves
  ansible.builtin.command:
    cmd: getent hosts {{ expected_hostname }}
  register: dns_check
  changed_when: false

- name: Assert hostname resolves to correct IP
  ansible.builtin.assert:
    that:
      - "'{{ expected_ip }}' in dns_check.stdout"
    fail_msg: "{{ expected_hostname }} does not resolve to {{ expected_ip }}"
```

### Sysctl parameter is active

```yaml
- name: Get sysctl value
  ansible.builtin.command:
    cmd: sysctl -n {{ sysctl_param }}
  register: sysctl_value
  changed_when: false

- name: Assert sysctl parameter is set correctly
  ansible.builtin.assert:
    that:
      - sysctl_value.stdout | trim == expected_value
    fail_msg: "{{ sysctl_param }} is {{ sysctl_value.stdout }}, expected {{ expected_value }}"
```

### Cron job exists

```yaml
- name: List crontab for user
  ansible.builtin.command:
    cmd: crontab -l -u {{ cron_user }}
  register: crontab
  changed_when: false

- name: Assert expected cron entry exists
  ansible.builtin.assert:
    that:
      - "'{{ expected_cron_command }}' in crontab.stdout"
    fail_msg: "Expected cron entry not found for user {{ cron_user }}"
```

---

## 11. When Structural Tests Are Appropriate

Structural tests verify file existence, content, or permissions directly. They are appropriate when:

1. **Custom modules/plugins**: No upstream tests exist for your custom module's output. You must verify it directly.
2. **Complex Jinja2 templates**: When the output must match an exact schema (XML, JSON, INI) that the consuming application will parse. A malformed template that "exists" can still break the application.
3. **Generated configs with computed values**: When the template contains complex arithmetic or conditional logic and the correctness of specific
   computed values matters independently of whether the application starts.
4. **Idempotency regression tests**: When a specific bug caused idempotency issues around file content, and a structural check is the most direct way to prevent regression.

Even in these cases, if you can also write a functional test, do both. The functional test catches more classes of bugs.

---

## 12. Anti-Patterns

### Testing file existence for built-in modules

**Wrong:** Using `ansible.builtin.stat` to check if a file created by `ansible.builtin.template` exists.

**Why:** You're retesting ansible.builtin.template. It works. Test what the file *enables*.

### Testing file content for built-in modules

**Wrong:** Using `ansible.builtin.slurp` + b64decode to read a config file and grep for lines.

**Why:** You're retesting template rendering. Test the application behavior the config controls.

### Missing idempotency in test sequence

**Wrong:** Test sequence without `idempotence` action.

**Why:** Idempotency is fundamental. A role that reports changes on every run cannot be trusted.

### No fail_msg on assertions

**Wrong:** `assert: that: - result.status == 200`

**Right:** Include `fail_msg` with context about what failed and the actual values.

### Forgetting changed_when on verify commands

**Wrong:** Running `ansible.builtin.command` in verify.yml without `changed_when: false`.

**Why:** Verify playbooks should never report changes. All commands are read-only checks.

### Testing in converge instead of verify

**Wrong:** Adding assertions directly in converge.yml.

**Why:** Converge applies automation. Verify validates outcomes. Mixing them makes it unclear which is which.

---

## 13. Tooling

### molecule CLI

```bash
# Full lifecycle
molecule test --scenario-name default --report --command-borders

# Development workflow
molecule create -s default
molecule converge -s default
molecule verify -s default
molecule login -s default  # debug interactively
molecule destroy -s default

# All scenarios
molecule test --all --parallel --report
```

### tox-ansible integration

Use `tox-ansible` to run Molecule scenarios via tox:

```ini
# tox.ini
[tox]
requires = tox-ansible>=24.9.0

[testenv]
commands = molecule test -s {envname}
```

### CI/CD

In GitHub Actions:

```yaml
- name: Run Molecule tests
  run: |
    pip install molecule containers.podman
    molecule test --all --report
```
