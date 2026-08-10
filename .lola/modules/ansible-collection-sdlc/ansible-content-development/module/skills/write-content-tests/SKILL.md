---
name: write-content-tests
description: >-
  Write functional tests for Ansible content (roles, playbooks) using
  Molecule. Focuses on verifying intended outcomes — does the automation
  achieve its goal? — not retesting built-in modules. Use when writing
  new Molecule scenarios, verify playbooks, or improving existing tests.
  Do NOT use for Python module unit/integration tests (use write-module-tests).
argument-hint: "[role-path or scenario-description]"
user-invocable: true
metadata:
  author: David Danielsson
  version: 1.0.0
---

# Skill: write-content-tests

## Purpose

Write functional tests for Ansible roles and playbooks using Molecule. Generate Molecule scenarios with verify playbooks that test whether automation
achieves its intended outcome, not whether individual modules did their job.

## When to Invoke

TRIGGER when:

- A user asks to write, create, or generate tests for a role or playbook
- A user asks to set up Molecule for a role or collection
- A user asks how to test Ansible content
- A user asks to improve or review existing Molecule tests
- A user asks to write a verify.yml for a Molecule scenario

DO NOT TRIGGER when:

- Writing unit or integration tests for Python modules (use `write-module-tests` instead)
- Running existing tests (use `run-tests` instead)
- Running sanity checks directly (use `ansible-test sanity`, or the companion `sanity` skill if the `ansible-collection-sdlc` module is installed)
- Reviewing a PR (use `pr-review` instead)

## Important

- **CRITICAL: Tests must be FUNCTIONAL, not structural.** Do not write tests that verify a file exists or contains expected content when a built-in
  module (ansible.builtin.template, ansible.builtin.copy, etc.) created it. Those modules are already tested by Ansible upstream. Instead, test the
  *intended outcome* — does the system behave correctly?
- Trust built-in modules. If your role uses `ansible.builtin.template` to deploy a sudoers file, don't test that the file exists. Test that the user has the correct sudo permissions.
- When improving existing tests, actively identify structural tests that should be replaced with functional tests. This is the highest-impact improvement you can suggest.
- Keep this file to one minimal standalone scenario pattern. For collection shared-state layouts,
  custom lifecycle playbooks, and multi-platform inventory design, use [reference.md](reference.md)
  sections 3, 8, and 9.
- All guidance follows Molecule's testing philosophy from docs.ansible.com. For the full set of
  patterns and examples, see [reference.md](reference.md).

## Modes

Determine the mode based on the user's invocation and `$ARGUMENTS`:

- If `$ARGUMENTS` is a path to an existing Molecule scenario, `molecule/` directory, `extensions/molecule/` directory, or test file such as `verify.yml`/`converge.yml` → **Mode 2: Improve**
- If `$ARGUMENTS` is a role path, playbook path, or text description → **Mode 1: Write**
- If `$ARGUMENTS` is empty → ask the user what they want to test
- If ambiguous → ask the user to clarify

---

### Mode 1: Write New Tests

Generate a Molecule scenario with functional verification for Ansible content.

#### Step 1 — Determine What to Test

Identify the target:

- **Role**: Read the role's `tasks/`, `defaults/`, `handlers/`, and `meta/` to understand what it does
- **Playbook**: Read the playbook to identify its roles and tasks
- **Collection**: Determine which components need scenarios

If a `galaxy.yml` exists, read it for namespace and collection context.

#### Step 2 — Identify Functional Outcomes

For each function the role/playbook performs, determine the functional outcome to verify:

| What the Automation Does | Functional Outcome to Verify | How to Verify |
|--------------------------|------------------------------|---------------|
| Installs packages and starts a service | Service responds on its port | `ansible.builtin.uri` or `ansible.builtin.wait_for` |
| Manages service state | Service is in correct state | `ansible.builtin.command: systemctl is-active <service>` |
| Deploys application config | Application behaves correctly | `ansible.builtin.uri` to app endpoint, or run app command |
| Manages user accounts | User has correct access | `ansible.builtin.command: id <user>`, `sudo -l -U <user>` |
| Configures sudoers | User has correct permissions | `ansible.builtin.command: sudo -l -U <user>` and assert allowed/denied commands |
| Manages firewall rules | Correct ports are accessible | `ansible.builtin.wait_for: port=<port>`, `ansible.builtin.uri` |
| Deploys SSL certificates | HTTPS endpoint works | `ansible.builtin.uri: url=https://... validate_certs=true` |
| Configures DNS/hosts | Name resolution works | `ansible.builtin.command: getent hosts <hostname>` |
| Manages cron jobs | Scheduled task exists and runs | `ansible.builtin.command: crontab -l -u <user>` |
| Sets system parameters (sysctl) | Parameter is active | `ansible.builtin.command: sysctl <param>` and assert value |

#### Step 3 — Generate Molecule Scenario

Create the scenario directory structure using the templates in the **Scenario Templates** section below.

For a **standalone role**, create under `molecule/<scenario_name>/` using the minimal runnable
pattern below.
For a **collection role**, create under `extensions/molecule/<role_name>/`, but do not reuse the
standalone template verbatim. Use the shared-state layout in [reference.md](reference.md) sections
3 and 8 so `config.yml`, `inventory.yml`, and the lifecycle scenario are present.

#### Step 4 — Generate verify.yml

Write functional assertions based on Step 2. Use the patterns from the **Functional Verification Patterns** section.

#### Step 5 — Post-Write Guidance

1. Suggest running `molecule test --scenario-name <name>` to validate
2. Suggest `pip install molecule containers.podman` if container-based testing is not installed
3. Suggest ensuring Podman or Docker is available
4. If testing a collection role, point the user to the shared-state layout in [reference.md](reference.md) instead of trying to infer it from the standalone template

---

### Mode 2: Improve Existing Tests

Audit existing Molecule tests and suggest improvements.

#### Step 1 — Read Existing Tests

Read the full Molecule scenario: `molecule.yml`, `converge.yml`, `verify.yml`, and all supporting playbooks.

#### Step 2 — Evaluate Against Checklist

Run through every category in the **Improvement Checklist** below.

**Most important check:** Identify any structural tests in verify.yml that test file existence, file content, or file permissions for files created by
built-in modules. These should be replaced with functional tests.

#### Step 3 — Score

Rate overall test quality on a 1-10 scale:

- **9-10**: Exemplary — all functional, good coverage, idempotency tested
- **7-8**: Good — mostly functional, minor structural tests remain
- **5-6**: Acceptable — mix of functional and structural, idempotency present
- **3-4**: Needs work — mostly structural tests, missing idempotency
- **1-2**: Non-compliant — only structural tests, no idempotency, broken scenario

#### Step 4 — Top Recommendations

List the 3 most impactful changes. Prioritize converting structural tests to functional tests.

---

## Scenario Templates

Keep the inline templates in this file limited to one minimal standalone scenario. For collection
roles with `shared_state: true`, custom `create.yml` / `destroy.yml`, or multi-platform test
inventories, use [reference.md](reference.md) sections 3, 8, and 9.

### Directory Structure (Standalone Role)

```text
molecule/
└── default/
    ├── molecule.yml
    ├── converge.yml
    └── verify.yml
```

### molecule.yml (Standalone Role)

```yaml
---
dependency:
  name: galaxy

driver:
  name: podman

platforms:
  - name: instance
    image: quay.io/centos/centos:stream9
    pre_build_image: true
    command: /sbin/init
    privileged: true

provisioner:
  name: ansible

scenario:
  test_sequence:
    - dependency
    - create
    - converge
    - idempotence
    - verify
    - destroy
```

### converge.yml (Standalone Role)

```yaml
---
- name: Converge
  hosts: all
  become: true
  roles:
    - role: role_name
```

### converge.yml (Playbook)

```yaml
---
- name: Converge
  ansible.builtin.import_playbook: ../../playbook_name.yml
```

### verify.yml (Functional)

```yaml
---
- name: Verify
  hosts: all
  gather_facts: true
  become: true
  tasks:
    - name: Verify service is running and responding
      ansible.builtin.uri:
        url: "http://localhost:{{ service_port }}"
        status_code: 200
      register: service_check

    - name: Assert service responds correctly
      ansible.builtin.assert:
        that:
          - service_check.status == 200
        fail_msg: "Service is not responding on port {{ service_port }}"
```

---

## When Structural Tests ARE Appropriate

Not all structural tests are wrong. Use them when:

- **Custom modules/plugins**: No upstream tests exist, so you must verify the output directly
- **Complex Jinja2 templates**: When the output format must match an exact schema that the application parses (e.g., XML configs, INI files with strict formatting)
- **Generated configs with computed values**: When the template logic itself is complex and the correctness of computed values matters
- **Idempotency regression**: When a structural check is the only way to verify a specific idempotency bug was fixed

Even in these cases, prefer a functional test when one is feasible. A structural test is the fallback, not the default.

---

## Improvement Checklist

| Category | What to Check |
|----------|---------------|
| Functional Focus | Tests verify outcomes (service responds, user has access, app works) not implementation (file exists, content matches). Flag any `ansible.builtin.stat` + assert-exists patterns for built-in module outputs. |
| Scenario Structure | `molecule.yml`, `create.yml`, `converge.yml`, `verify.yml`, `destroy.yml` all present. `test_sequence` includes `idempotence`. |
| Idempotency | The `idempotence` action is in the test sequence. Converge runs twice and the second run reports zero changes. |
| Verify Quality | Assertions are specific with `fail_msg` for clear diagnostics. `check_mode: true` + `failed_when: false` pattern used for non-destructive checks. |
| Coverage | All role functions tested (install, configure, service, user, security). Both `present` and `absent` states tested where applicable. |
| Platform Support | Tests cover all declared supported platforms, or document which are tested. Multi-platform inventory if role supports multiple OS families. |
| Isolation | Tests don't depend on external state or pre-existing resources. `create`/`destroy` handle the full lifecycle. `failed_when: false` on destroy tasks. |
| Tooling | `molecule test` succeeds end-to-end. `ansible-lint` passes on all scenario playbooks. |

---

## Output Format

### Write Mode

```
## Generated: Molecule Scenario for <role/playbook name>

### Scenario Structure
<directory tree of generated files>

### Functional Tests
| What is Tested | Verification Method | Expected Outcome |
|----------------|--------------------|--------------------|
| ... | ... | ... |

### Files
<generated file contents>

### Next Steps
1. Run `molecule test --scenario-name <name>` to validate
2. Ensure Podman is installed: `podman --version`
3. Install Molecule if needed: `pip install molecule`
```

### Improve Mode

```
## Test Review: <scenario path>

### Summary
<One-paragraph assessment.>

### Structural Tests to Convert
- <file>:<line> — Tests <structural thing>. Replace with: <functional alternative>

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
| Functional Focus | PASS / FAIL | ... |
| Scenario Structure | PASS / FAIL | ... |
| Idempotency | PASS / FAIL | ... |
| Verify Quality | PASS / FAIL | ... |
| Coverage | PASS / FAIL | ... |
| Platform Support | PASS / FAIL / N/A | ... |
| Isolation | PASS / FAIL | ... |
| Tooling | PASS / FAIL | ... |

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
| Writing the Ansible content to be tested | `write-content` |
| Writing Python module tests, not content tests | `write-module-tests` |
| Running existing ansible-test (sanity/unit/integration) | `run-tests` |
| Reviewing the content for best practices before testing | `write-content` (improve mode) |
| Scaffolding a full role before writing tests | `/ansible-scaffold-role` |
