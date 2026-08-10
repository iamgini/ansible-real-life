# Ansible Module Testing Reference (ansible-test / pytest)

Supplementary detail for the `write-module-tests` skill. Consult when writing or improving unit and integration tests for Ansible modules. Primary source: docs.ansible.com.

---

## 1. Test Types Overview

Ansible uses three test types, all run via `ansible-test`:

| Type | What it Tests | Framework | Location |
|------|---------------|-----------|----------|
| Sanity | Style, documentation, imports | Built-in rules | Automatic (no files to write) |
| Unit | Individual functions and classes | pytest | `tests/unit/plugins/modules/` |
| Integration | Module behavior against live services | Ansible playbooks | `tests/integration/targets/<module>/` |

### When each is required

| Change Type | Sanity | Unit | Integration |
|-------------|--------|------|-------------|
| New module | yes | yes | yes |
| New parameter | yes | if logic changed | yes |
| Bug fix | yes | yes | yes |
| Refactoring | yes | yes | no |
| Documentation only | yes | no | no |

---

## 2. Unit Test Setup

### Directory structure

```
tests/
└── unit/
    └── plugins/
        ├── modules/
        │   ├── __init__.py
        │   └── test_my_module.py
        └── module_utils/
            ├── __init__.py
            └── test_my_util.py
```

Mirror the plugin directory structure. Every `__init__.py` can be empty.

### Running unit tests

```bash
ansible-test units tests/unit/plugins/modules/test_my_module.py --docker -vvv
ansible-test units --docker -vvv  # run all unit tests
```

---

## 3. Module Test Skeleton

A complete, annotated pytest test file:

```python
"""Unit tests for namespace.collection.my_module module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

import pytest
from unittest.mock import MagicMock, patch, call

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


# --- Test infrastructure ---

def set_module_args(args):
    """Prepare arguments so they will be picked up during module creation.

    Must be called BEFORE the module's main() function.
    """
    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Raised instead of exit_json to capture the result."""
    pass


class AnsibleFailJson(Exception):
    """Raised instead of fail_json to capture the error."""
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
    """Patch AnsibleModule exit/fail for every test automatically."""
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)


# Import the module under test AFTER patching
from ansible_collections.namespace.collection.plugins.modules import my_module


# --- Tests ---

class TestMyModule:
    """Tests for the my_module module."""

    # Argument validation tests

    def test_missing_required_name_fails(self):
        """Fails when the required 'name' argument is not provided."""
        set_module_args({"state": "present"})
        with pytest.raises(AnsibleFailJson) as exc:
            my_module.main()
        assert "missing required arguments: name" in str(exc.value.args[0]["msg"]).lower()

    def test_invalid_state_choice_fails(self):
        """Fails when state is not a valid choice."""
        set_module_args({"name": "test", "state": "invalid"})
        with pytest.raises(AnsibleFailJson) as exc:
            my_module.main()
        assert "invalid" in str(exc.value.args[0]["msg"]).lower()

    # Success path tests

    def test_state_present_creates_when_missing(self):
        """Creates resource when state=present and it does not exist."""
        set_module_args({"name": "test", "state": "present"})
        with patch.object(my_module, "get_resource", return_value=None):
            with patch.object(my_module, "create_resource", return_value={"name": "test", "id": "123"}) as mock_create:
                with pytest.raises(AnsibleExitJson) as exc:
                    my_module.main()
        result = exc.value.args[0]
        assert result["changed"] is True
        assert result["resource"]["id"] == "123"
        mock_create.assert_called_once()

    def test_state_present_unchanged_when_exists(self):
        """Reports no change when resource already exists."""
        set_module_args({"name": "test", "state": "present"})
        with patch.object(my_module, "get_resource", return_value={"name": "test", "id": "123"}):
            with pytest.raises(AnsibleExitJson) as exc:
                my_module.main()
        result = exc.value.args[0]
        assert result["changed"] is False

    def test_state_absent_removes_when_exists(self):
        """Removes resource when state=absent and it exists."""
        set_module_args({"name": "test", "state": "absent"})
        with patch.object(my_module, "get_resource", return_value={"name": "test"}):
            with patch.object(my_module, "delete_resource") as mock_delete:
                with pytest.raises(AnsibleExitJson) as exc:
                    my_module.main()
        result = exc.value.args[0]
        assert result["changed"] is True
        mock_delete.assert_called_once()

    def test_state_absent_unchanged_when_missing(self):
        """Reports no change when resource does not exist."""
        set_module_args({"name": "test", "state": "absent"})
        with patch.object(my_module, "get_resource", return_value=None):
            with pytest.raises(AnsibleExitJson) as exc:
                my_module.main()
        result = exc.value.args[0]
        assert result["changed"] is False

    # Check mode tests

    def test_check_mode_present_reports_changed_without_creating(self):
        """Check mode reports changed=True but does not create."""
        set_module_args({"name": "test", "state": "present", "_ansible_check_mode": True})
        with patch.object(my_module, "get_resource", return_value=None):
            with patch.object(my_module, "create_resource") as mock_create:
                with pytest.raises(AnsibleExitJson) as exc:
                    my_module.main()
        result = exc.value.args[0]
        assert result["changed"] is True
        mock_create.assert_not_called()

    # Error path tests

    def test_api_error_fails_with_message(self):
        """Fails gracefully with descriptive message on API error."""
        set_module_args({"name": "test", "state": "present"})
        with patch.object(my_module, "get_resource", side_effect=Exception("Connection refused")):
            with pytest.raises(AnsibleFailJson) as exc:
                my_module.main()
        assert "Connection refused" in exc.value.args[0]["msg"]

    def test_missing_dependency_fails(self):
        """Fails with install instructions when required library is missing."""
        set_module_args({"name": "test", "state": "present"})
        with patch.object(my_module, "HAS_SDK", False):
            with pytest.raises(AnsibleFailJson) as exc:
                my_module.main()
        assert "some_sdk" in exc.value.args[0]["msg"].lower()
```

---

## 4. Testing Argument Validation

### Missing required arguments

```python
def test_missing_required_args(self):
    set_module_args({})
    with pytest.raises(AnsibleFailJson):
        my_module.main()
```

### Invalid choices

```python
def test_invalid_choice(self):
    set_module_args({"name": "test", "state": "bogus"})
    with pytest.raises(AnsibleFailJson) as exc:
        my_module.main()
    assert "bogus" in str(exc.value.args[0]["msg"])
```

### Mutually exclusive options

```python
def test_mutually_exclusive_fails(self):
    set_module_args({"name": "test", "force": True, "update": True})
    with pytest.raises(AnsibleFailJson) as exc:
        my_module.main()
    assert "mutually exclusive" in str(exc.value.args[0]["msg"]).lower()
```

---

## 5. Testing Success Paths

### Verify changed status

Always check `changed` on every success path:

```python
result = exc.value.args[0]
assert result["changed"] is True   # when something was created/modified
assert result["changed"] is False  # when nothing changed
```

### Verify return values

```python
assert result["resource"]["name"] == "test"
assert "id" in result["resource"]
```

### Verify function calls

```python
mock_create.assert_called_once()
mock_create.assert_called_once_with("test", {"param": "value"})
```

---

## 6. Testing Failure Paths

### API errors

```python
with patch.object(my_module, "api_call", side_effect=APIError("Not found")):
    with pytest.raises(AnsibleFailJson) as exc:
        my_module.main()
assert "Not found" in exc.value.args[0]["msg"]
```

### Missing dependencies

```python
with patch.object(my_module, "HAS_LIB", False):
    with pytest.raises(AnsibleFailJson) as exc:
        my_module.main()
```

### Command failures

```python
with patch.object(basic.AnsibleModule, "run_command", return_value=(1, "", "command not found")):
    with pytest.raises(AnsibleFailJson) as exc:
        my_module.main()
```

---

## 7. Mocking Patterns

### Mocking run_command

```python
with patch.object(basic.AnsibleModule, "run_command") as mock_cmd:
    mock_cmd.return_value = (0, "output", "")
    with pytest.raises(AnsibleExitJson):
        my_module.main()
    mock_cmd.assert_called_once_with(["/usr/bin/tool", "arg1"])
```

### Mocking API sequences (state transitions)

```python
with patch.object(my_module, "api_call") as mock_api:
    mock_api.side_effect = [
        None,                          # First call: resource not found
        {"name": "test", "id": "123"}, # Second call: resource created
    ]
    with pytest.raises(AnsibleExitJson):
        my_module.main()
    assert mock_api.call_count == 2
```

### Mocking HTTP requests

```python
with patch("ansible_collections.namespace.collection.plugins.modules.my_module.fetch_url") as mock_fetch:
    mock_fetch.return_value = (MagicMock(read=lambda: b'{"status": "ok"}'), {"status": 200})
    with pytest.raises(AnsibleExitJson):
        my_module.main()
```

---

## 8. Integration Test Directory

### Structure

```
tests/integration/targets/<module_name>/
├── tasks/
│   └── main.yml           # Test playbook
├── meta/
│   └── main.yml           # Dependencies
├── defaults/
│   └── main.yml           # Test variables (optional)
└── aliases                # Test categorization (optional)
```

### meta/main.yml

```yaml
---
dependencies: []
```

### aliases file

```
cloud/aws
unsupported
```

Use `unsupported` when tests cannot run in CI (e.g., require external services).

---

## 9. Integration Test Pattern

The canonical integration test follows this sequence:

```yaml
---
# 1. Check mode — should report changed but make no changes
- name: Create resource (check mode)
  namespace.collection.my_module:
    name: test_resource
    state: present
  check_mode: true
  register: check_result

- name: Assert check mode reports changed
  ansible.builtin.assert:
    that: check_result is changed

- name: Verify resource was NOT created
  ansible.builtin.command:
    cmd: <verify resource does not exist>
  register: verify
  changed_when: false

- name: Assert resource absent after check mode
  ansible.builtin.assert:
    that: <resource is absent in verify output>

# 2. Real creation
- name: Create resource
  namespace.collection.my_module:
    name: test_resource
    state: present
  register: create_result

- name: Assert creation succeeded
  ansible.builtin.assert:
    that:
      - create_result is changed
      - create_result.resource.name == 'test_resource'

- name: Verify resource exists
  ansible.builtin.command:
    cmd: <verify resource exists>
  register: verify
  changed_when: false

- name: Assert resource is present
  ansible.builtin.assert:
    that: <resource is present in verify output>

# 3. Idempotency — second run should not change
- name: Create resource again (idempotency)
  namespace.collection.my_module:
    name: test_resource
    state: present
  register: idem_result

- name: Assert no change on second run
  ansible.builtin.assert:
    that: idem_result is not changed

# 4. Removal
- name: Remove resource
  namespace.collection.my_module:
    name: test_resource
    state: absent
  register: remove_result

- name: Assert removal succeeded
  ansible.builtin.assert:
    that: remove_result is changed

- name: Verify resource is gone
  ansible.builtin.command:
    cmd: <verify resource does not exist>
  register: verify
  changed_when: false

- name: Assert resource is absent
  ansible.builtin.assert:
    that: <resource is absent in verify output>

# 5. Removal idempotency
- name: Remove resource again (idempotency)
  namespace.collection.my_module:
    name: test_resource
    state: absent
  register: idem_remove

- name: Assert no change on second removal
  ansible.builtin.assert:
    that: idem_remove is not changed
```

---

## 10. Test Naming

### Unit tests

Use descriptive names that encode what is tested and what is expected:

| Good | Bad |
|------|-----|
| `test_state_present_creates_resource_when_missing` | `test_create` |
| `test_missing_required_name_fails` | `test_args` |
| `test_check_mode_reports_changed_without_creating` | `test_check_mode` |
| `test_api_timeout_fails_with_descriptive_message` | `test_error` |
| `test_state_absent_unchanged_when_already_missing` | `test_absent` |

### Integration tests

Use descriptive `name:` fields on every task:

```yaml
- name: Create resource with all optional parameters
- name: Assert all return values are populated
- name: Verify resource has correct configuration via API
```

---

## 11. Anti-Patterns

### Testing implementation details

**Wrong:** Assert that an internal dictionary has a specific structure.

**Right:** Assert observable behavior: `changed`, return values, error messages.

**Why:** Implementation can be refactored. Observable behavior is the contract.

### Overly complex mocks

**Wrong:** Mock chains that are harder to read than the module code.

**Right:** Extract module logic into testable functions. Mock at the boundary (API calls, commands).

**Why:** If the mock is complex, the module's structure needs improvement.

### Missing error path tests

**Wrong:** Only testing the happy path.

**Right:** Test every `fail_json` path: missing args, API errors, missing dependencies, invalid input.

**Why:** Error handling is where most bugs hide in production.

### Not checking changed status

**Wrong:** Only asserting that the test doesn't raise an exception.

**Right:** Always assert `result["changed"]` is the expected value.

**Why:** `changed` drives handler execution and idempotency. Getting it wrong breaks playbooks.

### Tests that depend on execution order

**Wrong:** Tests that pass only when run in a specific sequence.

**Right:** Each test sets its own `set_module_args` and mocks independently.

**Why:** pytest can run tests in any order or in parallel.

---

## 12. Running Tests

### Unit tests

```bash
# Single test file
ansible-test units tests/unit/plugins/modules/test_my_module.py --docker -vvv

# All unit tests
ansible-test units --docker -vvv

# With specific Python version
ansible-test units --docker -vvv --python 3.11
```

### Integration tests

```bash
# Single target
ansible-test integration my_module --docker default -vvv

# With specific container image
ansible-test integration my_module --docker ubuntu -vvv

# List available targets
ansible-test integration --list-targets
```

### Sanity tests

```bash
# Single file
ansible-test sanity plugins/modules/my_module.py --docker -vvv

# Specific test
ansible-test sanity --test validate-modules plugins/modules/my_module.py --docker

# All sanity
ansible-test sanity --docker -vvv
```
