---
name: write-module-tests
description: >-
  Use this skill when writing unit or integration tests for Ansible modules
  with ansible-test and pytest. Covers test structure, mocking AnsibleModule,
  argument validation, and integration test patterns. Do NOT use for Ansible
  content tests (use write-content-tests for Molecule).
argument-hint: "[module-file-path or test-description]"
user-invocable: true
metadata:
  author: David Danielsson
  version: 1.0.0
---

# Skill: write-module-tests

## Purpose

Write unit tests (pytest) and integration tests (ansible-test) for Ansible modules. Generate test files that validate argument processing, success and failure paths, check mode behavior, and idempotency.

## When to Invoke

TRIGGER when:

- A user asks to write, create, or generate tests for an Ansible module
- A user asks how to test a module's argument spec, logic, or return values
- A user asks to improve or review existing module tests
- A user asks about mocking AnsibleModule, exit_json, or fail_json in tests

DO NOT TRIGGER when:

- Writing Molecule tests for roles or playbooks (use `write-content-tests` instead)
- Running existing tests (use `run-tests` instead)
- Running sanity checks directly (use `ansible-test sanity`, or the companion `sanity` skill if the `ansible-collection-sdlc` module is installed)
- Writing the module itself (use `write-module` instead)

## Important

- Unit tests use **pytest** — not unittest. This is the Ansible Engineering standard.
- Integration tests use **ansible-test** and run in Docker/Podman containers.
- Test descriptive names that explain WHAT is tested and WHAT is expected: `test_state_present_creates_resource_when_missing`, not `test_create`.
- Tests must not make real external calls. Mock all API interactions, command executions, and network requests.
- The unit-test template below assumes the module follows the helper-based scaffold from
  `write-module` (`get_client`, `get_resource`, `create_resource`, `delete_resource`). If the
  module keeps logic inline, keep the same assertions but patch the narrowest boundary instead.
  Alternate patterns live in [reference.md](reference.md).
- Imports such as `from ansible_collections.<namespace>.<collection>...` assume the collection is
  available in a standard `ansible_collections/<namespace>/<name>/` layout so `ansible-test` can
  resolve it correctly.
- All guidance is sourced from docs.ansible.com. Use [reference.md](reference.md) for alternate mocking patterns, missing-dependency cases, and more complete ansible-test examples.

## Modes

Determine the mode based on the user's invocation and `$ARGUMENTS`:

- If `$ARGUMENTS` is a path to an existing unit/integration test file or test directory → **Mode 2: Improve**
- If `$ARGUMENTS` is a module path or module name and the user asks to improve/review tests, locate the existing tests for that module and use **Mode 2: Improve**
- If `$ARGUMENTS` is a path to a module file or a module name and the user wants new tests → **Mode 1: Write**
- If `$ARGUMENTS` is empty → ask the user what they want to test
- If ambiguous → ask the user to clarify

---

### Mode 1: Write New Tests

Generate unit and/or integration tests for an Ansible module.

#### Step 1 — Determine Test Types Needed

| Change Type | Sanity | Unit | Integration |
|-------------|--------|------|-------------|
| New module | yes | yes | yes |
| New parameter | yes | if logic changed | yes |
| Bug fix | yes | yes | yes |
| Refactoring | yes | yes | no |
| Documentation only | yes | no | no |

#### Step 2 — Read the Module

Read the module file to understand:

- `argument_spec`: all parameters, types, required, defaults, choices, mutual exclusions
- Module logic: what actions it performs, what can fail
- Return values: what `exit_json` returns on success
- Error conditions: what triggers `fail_json`
- Check mode: how it behaves in check mode
- Dependencies: any `HAS_LIB` patterns

#### Step 3 — Generate Tests

**Unit tests**: Place at `tests/unit/plugins/modules/test_<module_name>.py`. Use the template in the **Unit Test Template** section when the module follows the default helper-based scaffold from `write-module`.

**Integration tests**: Place at `tests/integration/targets/<module_name>/tasks/main.yml`. Use the template in the **Integration Test Template** section.

#### Step 4 — Post-Write Guidance

1. Run unit tests: `ansible-test units tests/unit/plugins/modules/test_<module_name>.py --docker -vvv`
2. Run integration tests: `ansible-test integration <module_name> --docker default -vvv`
3. Run sanity: `ansible-test sanity plugins/modules/<module_name>.py --docker -vvv`

---

### Mode 2: Improve Existing Tests

Audit existing module tests and suggest improvements.

#### Step 1 — Read Existing Tests

Read all test files for the module (unit and integration).

#### Step 2 — Evaluate Against Checklist

Run through every category in the **Test Checklist** below.

#### Step 3 — Score

Rate test quality on a 1-10 scale:

- **9-10**: Exemplary — all paths covered, descriptive names, proper mocking
- **7-8**: Good — most paths covered, minor gaps
- **5-6**: Acceptable — success path tested, some error/edge cases missing
- **3-4**: Needs work — minimal coverage, poor naming, missing check mode
- **1-2**: Non-compliant — no meaningful tests or fundamentally broken

#### Step 4 — Top Recommendations

List the 3 most impactful improvements.

---

## Unit Test Template

```python
"""Unit tests for <namespace>.<collection>.<module_name> module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

import pytest
from unittest.mock import MagicMock, patch

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


def set_module_args(args):
    """Prepare arguments for module invocation."""
    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception for capturing exit_json calls."""
    pass


class AnsibleFailJson(Exception):
    """Exception for capturing fail_json calls."""
    pass


def exit_json(*args, **kwargs):
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


@pytest.fixture(autouse=True)
def patch_module(monkeypatch):
    """Patch AnsibleModule exit/fail methods for all tests."""
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)


# Import the module under test after patching
from ansible_collections.namespace.collection.plugins.modules import module_name


@pytest.fixture
def mock_client():
    """Patch optional dependency checks and client creation."""
    with patch.object(module_name, "HAS_LIB", True):
        with patch.object(module_name, "get_client", return_value=MagicMock()) as mock_get_client:
            yield mock_get_client.return_value


class TestModuleName:
    """Tests for module_name module."""

    def test_missing_required_args_fails(self):
        """Module fails when required arguments are missing."""
        set_module_args({})
        with pytest.raises(AnsibleFailJson) as exc:
            module_name.main()
        assert "missing required arguments" in str(exc.value.args[0]["msg"]).lower()

    def test_state_present_creates_resource(self, mock_client):
        """Module creates resource when state=present and resource is missing."""
        set_module_args({
            "name": "test_resource",
            "state": "present",
        })
        with patch.object(module_name, "get_resource", return_value=None):
            with patch.object(module_name, "create_resource", return_value={"name": "test_resource"}) as mock_create:
                with pytest.raises(AnsibleExitJson) as exc:
                    module_name.main()
                result = exc.value.args[0]
                assert result["changed"] is True
                mock_create.assert_called_once()

    def test_state_present_no_change_when_exists(self, mock_client):
        """Module reports no change when resource already exists."""
        set_module_args({
            "name": "test_resource",
            "state": "present",
        })
        with patch.object(module_name, "get_resource", return_value={"name": "test_resource"}):
            with pytest.raises(AnsibleExitJson) as exc:
                module_name.main()
            result = exc.value.args[0]
            assert result["changed"] is False

    def test_state_absent_removes_resource(self, mock_client):
        """Module removes resource when state=absent and resource exists."""
        set_module_args({
            "name": "test_resource",
            "state": "absent",
        })
        with patch.object(module_name, "get_resource", return_value={"name": "test_resource"}):
            with patch.object(module_name, "delete_resource") as mock_delete:
                with pytest.raises(AnsibleExitJson) as exc:
                    module_name.main()
                result = exc.value.args[0]
                assert result["changed"] is True
                mock_delete.assert_called_once()

    def test_check_mode_does_not_modify(self, mock_client):
        """Module does not make changes in check mode."""
        set_module_args({
            "name": "test_resource",
            "state": "present",
            "_ansible_check_mode": True,
        })
        with patch.object(module_name, "get_resource", return_value=None):
            with patch.object(module_name, "create_resource") as mock_create:
                with pytest.raises(AnsibleExitJson) as exc:
                    module_name.main()
                result = exc.value.args[0]
                assert result["changed"] is True
                mock_create.assert_not_called()

    def test_api_error_fails_gracefully(self, mock_client):
        """Module fails with descriptive message on API error."""
        set_module_args({
            "name": "test_resource",
            "state": "present",
        })
        with patch.object(module_name, "get_resource", side_effect=Exception("Connection refused")):
            with pytest.raises(AnsibleFailJson) as exc:
                module_name.main()
            assert "Connection refused" in exc.value.args[0]["msg"]
```

Adapt the template based on the actual module structure. If the module follows the default
`write-module` scaffold, patch `get_client`, `get_resource`, `create_resource`, and
`delete_resource` directly. If the module is structured differently, keep the same coverage goals
but patch the narrowest boundary (API client, `module.run_command`, or `module_utils` helper)
instead; [reference.md](reference.md) has fuller variants.

---

## Integration Test Template

Place at `tests/integration/targets/<module_name>/tasks/main.yml`:

```yaml
---
- name: Test create in check mode
  <namespace>.<collection>.<module_name>:
    name: integration_test_resource
    state: present
  check_mode: true
  register: result

- name: Assert check mode reports changed
  ansible.builtin.assert:
    that:
      - result is changed

- name: Verify resource does not exist yet
  ansible.builtin.command:
    cmd: <command to check resource does not exist>
  register: verify_result

- name: Assert resource is not present
  ansible.builtin.assert:
    that:
      - <appropriate assertion on verify_result>

- name: Create resource
  <namespace>.<collection>.<module_name>:
    name: integration_test_resource
    state: present
  register: result

- name: Assert resource was created
  ansible.builtin.assert:
    that:
      - result is changed

- name: Verify resource exists
  ansible.builtin.command:
    cmd: <command to verify resource>
  register: verify_result

- name: Assert resource is present
  ansible.builtin.assert:
    that:
      - <appropriate assertion on verify_result>

- name: Create resource again (idempotency)
  <namespace>.<collection>.<module_name>:
    name: integration_test_resource
    state: present
  register: result

- name: Assert no change on second run
  ansible.builtin.assert:
    that:
      - result is not changed

- name: Remove resource
  <namespace>.<collection>.<module_name>:
    name: integration_test_resource
    state: absent
  register: result

- name: Assert resource was removed
  ansible.builtin.assert:
    that:
      - result is changed

- name: Verify resource is gone
  ansible.builtin.command:
    cmd: <command to verify resource is absent>
  register: verify_result

- name: Assert resource is absent
  ansible.builtin.assert:
    that:
      - <appropriate assertion on verify_result>
```

Also create `tests/integration/targets/<module_name>/meta/main.yml` for dependencies:

```yaml
---
dependencies: []
```

---

## Test Checklist

| Category | What to Check |
|----------|---------------|
| Test Coverage | Missing required args fails, success path (state present/absent), failure path (API errors), check mode, idempotency (second run unchanged) |
| Naming | Descriptive names: `test_state_present_creates_resource_when_missing`, not `test_create`. Names explain what is tested and expected outcome. |
| Mocking | `exit_json`/`fail_json` patched to raise exceptions. `run_command` mocked. API calls mocked. No real external calls or side effects. |
| Assertions | `changed` status verified on every test. Return values checked. Error messages validated. `assert_called_once` on mocked functions. |
| Integration Pattern | check_mode → real → idempotency → absent sequence. State verified independently via separate command (not just module return). |
| Independence | Tests don't depend on execution order or shared state. Each test sets its own module args and mocks. |
| Error Paths | Invalid input tested (wrong type, invalid choices). API errors tested. Missing dependency (`HAS_LIB`) tested. |
| Framework | pytest used (not unittest). `monkeypatch` or `patch` for mocking. `pytest.raises` for exception capture. Clear arrange/act/assert. |

---

## Output Format

### Write Mode

```
## Generated: Tests for <module_name>

### Unit Tests
`tests/unit/plugins/modules/test_<module_name>.py`

<generated test code>

### Integration Tests
`tests/integration/targets/<module_name>/tasks/main.yml`

<generated test YAML>

### Test Coverage
| Test | Type | What it Validates |
|------|------|-------------------|
| ... | unit | ... |
| ... | integration | ... |

### Next Steps
1. Run `ansible-test units tests/unit/plugins/modules/test_<module_name>.py --docker -vvv`
2. Run `ansible-test integration <module_name> --docker default -vvv`
```

### Improve Mode

```
## Test Review: <test file path>

### Summary
<One-paragraph assessment.>

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
| Test Coverage | PASS / FAIL | ... |
| Naming | PASS / FAIL | ... |
| Mocking | PASS / FAIL | ... |
| Assertions | PASS / FAIL | ... |
| Integration Pattern | PASS / FAIL / N/A | ... |
| Independence | PASS / FAIL | ... |
| Error Paths | PASS / FAIL | ... |
| Framework | PASS / FAIL | ... |

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
| Writing the module to be tested | `write-module` |
| Writing Molecule tests for roles/playbooks | `write-content-tests` |
| Running existing tests | `run-tests` |
| Running sanity checks | `ansible-test sanity` directly, or `sanity` if the SDLC module is installed |
| Reviewing a PR that includes tests | `pr-review` |
