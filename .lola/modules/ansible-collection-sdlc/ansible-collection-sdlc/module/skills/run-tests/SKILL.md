---
name: run-tests
description: >-
  Runs and writes tests (sanity, unit, integration) for an Ansible
  collection using ansible-test. Use when asked to run, check, or
  write tests for a module or utility. Do not use for PR reviews
  or questions unrelated to testing.
user-invocable: true
---

# Skill: run-tests

## Purpose

Run and write tests for an Ansible collection. Covers sanity, unit, and integration tests using `ansible-test`.

## When to Invoke

TRIGGER when:

- A user asks to run tests, check tests, or verify changes with tests
- A user asks how to test a module or utility
- A user asks to write tests for new or modified code

DO NOT TRIGGER when:

- Reviewing a PR for overall quality (use the `pr-review` skill instead)
- The question is about module logic unrelated to testing

## Test Infrastructure

All tests run inside Docker/Podman via `ansible-test --docker`.
No local package installation is needed.
The collection must be installed at `ansible_collections/<namespace>/<name>/`
(relative to a directory on `ANSIBLE_COLLECTIONS_PATHS`) for imports to resolve correctly.
Determine the namespace and name from `galaxy.yml`.

---

## Test Commands

### Sanity

Checks style, documentation, and imports for a changed file:

```bash
ansible-test sanity plugins/modules/<module_name>.py --docker -vvv
```

### Unit

Runs unit tests for changed files:

```bash
ansible-test units tests/unit/plugins/modules/test_<module_name>.py --docker -vvv
ansible-test units tests/unit/plugins/module_utils/test_<util_name>.py --docker -vvv
```

Unit tests live under `tests/unit/plugins/` and use the **PyTest** framework. Every new function or class method MUST have a corresponding unit test.

### Integration

Runs integration tests against a live service instance (started by Docker):

```bash
ansible-test integration test_<module_name> --docker default -vvv
```

Integration tests live under `tests/integration/targets/<module_name>/`. Each target may declare setup dependencies in `tests/integration/targets/<name>/meta/main.yml`.

### Integration via Makefile

If the project provides a Makefile for integration tests
(check `TESTING.md` or `Makefile` in the project root),
prefer using it as it handles spinning up required services
and configuring the test environment.
Consult the project's testing documentation for available options.

---

## When Tests Are Required

| Change type | Sanity | Unit | Integration |
| --- | --- | --- | --- |
| New module | yes | yes | yes |
| New parameter | yes | if logic changed | yes |
| Bug fix | yes | yes | yes |
| Refactoring | yes | yes | no |
| Documentation only | yes | no | no |

---

## Integration Test Pattern

Every integration test target must follow this sequence:

1. Call the module under test -> `register: result`
2. Assert on `result` using `ansible.builtin.assert`
3. Verify the resulting state via a separate module or command -> `register: result` -> `ansible.builtin.assert`
4. This must be done in `check_mode: true` as well

```yaml
- name: Create resource in check mode
  check_mode: true
  <namespace>.<name>.<module_name>:
    name: test_resource
    state: present
  register: result

- name: Assert changed
  ansible.builtin.assert:
    that:
      - result is changed

- name: Verify resource does not exist yet
  <verify using an appropriate module or command>
  register: result

- name: Assert resource is not present
  ansible.builtin.assert:
    that:
      - <appropriate assertion>

- name: Create resource in real mode
  <namespace>.<name>.<module_name>:
    name: test_resource
    state: present
  register: result

- name: Assert changed
  ansible.builtin.assert:
    that:
      - result is changed

- name: Verify resource exists
  <verify using an appropriate module or command>
  register: result

- name: Assert resource is present
  ansible.builtin.assert:
    that:
      - <appropriate assertion>
```

Tests must also cover:

- **Idempotency**: run the same task a second time and assert `result is not changed`.
- **`state: absent`**: where applicable, remove the resource and assert it is gone.
