# Ansible Module Best Practices Reference

Supplementary detail for the `write-module` skill. Consult when scaffolding or reviewing modules. All guidance is sourced from the official Ansible documentation at docs.ansible.com.

---

## 1. File Layout and Structure

Every Python-based Ansible module must contain these sections in this exact order:

1. **Shebang and encoding**
2. **Copyright and license**
3. **`DOCUMENTATION` block**
4. **`EXAMPLES` block**
5. **`RETURN` block**
6. **Python imports**
7. **Module code**

### Shebang

Use `#!/usr/bin/python` — never `#!/usr/bin/env python`. The `env` form bypasses `ansible_python_interpreter` logic.

### Encoding

Always include `# -*- coding: utf-8 -*-` on the second line.

### Copyright

Use the standard single-line form without a year:

```python
# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
```

### Future imports

Always include immediately after copyright:

```python
from __future__ import absolute_import, division, print_function
__metaclass__ = type
```

### Self-contained

Each module must be self-contained in a single file. Ansible auto-transfers modules to remote hosts — multi-file modules break this mechanism. Shared code belongs in `module_utils/`.

### Module naming

- MUST use underscores: `my_module_name.py` (not `my-module-name.py`)
- Hyphens prevent Python importing
- The `module:` field in DOCUMENTATION must match the filename without `.py`

---

## 2. Module Design Principles

### Single responsibility

Follow the UNIX philosophy — one module should do one thing well. Do not build a lightweight wrapper around a complex API that forces users to write
logic in playbooks. Instead, create multiple smaller modules addressing distinct API pieces.

### Module vs action plugin

Choose the execution model before writing code:

- Prefer a **module** when the logic must execute on the managed host, manipulate remote state directly, or gather host-local facts
- Prefer an **action plugin** when the logic always runs on the controller, primarily orchestrates APIs or cloud services, or mostly prepares local work before delegating to existing modules
- Do not create a module just to bounce controller-local API calls through remote execution when an action plugin would be simpler and cheaper

**Why:** Modules pay the cost of packaging and remote execution. Action plugins avoid that overhead for controller-local logic and usually model cloud/API orchestration more naturally.

### Prefer existing content before a new module

Before authoring a custom module, use the highest-trust existing content that fits:

1. `ansible.builtin`
2. vendor-supported collections, modules, plugins, and roles
3. content from verified authors
4. general Galaxy content
5. custom modules, plugins, and roles only as a last resort

Do not write a new module just to lightly wrap behavior already available elsewhere, especially when the result would mostly proxy `command`, `shell`, or `raw` execution.

A new custom module is justified when existing content cannot provide a safe, idempotent, maintainable interface for the use case. When that happens, document the gap the module is filling.

### Separate info and facts modules

Do not add `get`, `list`, or `info` state options to an existing module. Create separate `_info` or `_facts` modules.

### Declarative operations

Use declarative state names:

- `present` / `absent` for resource existence
- `started` / `stopped` for service state

Avoid imperative names like `create`, `delete`, `action`, `command`.

### Idempotency

Running the module twice with the same arguments against the same system must produce the same state. The `changed` return value must be `False` on
the second run. If idempotency is impossible, document the behavior.

### Minimize dependencies

Document required dependencies at the top of the module. Use the `HAS_LIB` pattern to handle missing libraries gracefully.

---

## 3. Argument Specification

### Type declarations

Set `type` on every parameter. Supported types: `str`, `list`, `dict`, `bool`, `int`, `float`, `path`, `raw`, `jsonarg`, `json`, `bytes`, `bits`.

### Naming conventions

- Object-targeting options should be named `name` or accept `name` as an alias
- Boolean parameters must use `type='bool'` (accepts `yes`, `no`, `true`, `false`)
- Do not use these reserved names: `action`, `command`, `message`, `syslog_facility`
- Use module-specific environment variables: `API_<MODULENAME>_USERNAME`

### Required vs default

Never combine `required=True` with `default` — they are contradictory.

### Sensitive values

Set `no_log=True` for passwords, tokens, secrets, and API keys. For non-sensitive params whose names resemble passwords (e.g., `password_length`), set `no_log=False` to suppress the warning.

### Lists and dicts

When `type='list'`, always specify `elements` (e.g., `elements='str'`). When `type='dict'`, use `options` to define sub-arguments for nested validation.

### Inter-option dependencies

```python
module = AnsibleModule(
    argument_spec=argument_spec,
    mutually_exclusive=[
        ('path', 'content'),
    ],
    required_together=[
        ('username', 'password'),
    ],
    required_one_of=[
        ('path', 'content'),
    ],
    required_if=[
        ('state', 'present', ('name',)),
    ],
    required_by={
        'force': 'force_reason',
    },
)
```

### Environment variable fallback

```python
username=dict(
    type='str',
    fallback=(env_fallback, ['ANSIBLE_NET_USERNAME']),
)
```

### Deprecating options

Pair `removed_in_version` or `removed_at_date` with `removed_from_collection`:

```python
old_param=dict(
    type='str',
    removed_in_version='3.0.0',
    removed_from_collection='namespace.collection',
)
```

Prefer `deprecated_aliases` over permanent `aliases` when renaming.

---

## 4. DOCUMENTATION Block

Must be valid YAML assigned to a module-level `DOCUMENTATION` variable. All fields are lowercase.

### Required fields

| Field | Rules |
|-------|-------|
| `module` | Must match filename without `.py` |
| `short_description` | Concise summary, NO trailing period |
| `description` | List of full sentences, each capitalized and ending with a period. Do not mention the module name. |
| `version_added` | Quoted string. In collections, use the collection version (not ansible-core version). |
| `options` | Dict of options, each with `description` and `type`, plus `required: true` or `default` when they apply |
| `author` | `First Last (@GitHubID)` format. Use a list for multiple authors. |

### Option documentation

- `description`: Full sentences with periods. Do not list possible values (use `choices` for that). Document mutual exclusivity as the final sentence.
- `required`: Only specify when `true`. Omission implies not required.
- `default`: Do not list in description text. Ensure docs default matches code default.
- `choices`: List of valid values. Do not use if empty. Types must match param `type`.
- `type`: Must match `argument_spec`. For `type='bool'`, do not also specify `choices`.
- `version_added`: Only for options added after the module's initial release. Quoted string, collection version.
- `suboptions`: For `type='dict'` or `type='list'`/`elements='dict'` — recursively documents nested structure.

### Optional fields

- `requirements`: List prerequisites with minimum versions
- `notes`: Important info that doesn't fit elsewhere (not check_mode or diff — use `attributes`)
- `seealso`: References to other modules (FQCN), plugins, docs anchors, or URLs
- `deprecated`: For modules slated for removal
- `extends_documentation_fragment`: Shared docs from `plugins/doc_fragments/`

---

## 5. EXAMPLES Block

```python
EXAMPLES = r"""
- name: Create a resource
  namespace.collection.module_name:
    name: my_resource
    state: present

- name: Remove a resource
  namespace.collection.module_name:
    name: my_resource
    state: absent
"""
```

Rules:

- Multi-line plain-text YAML
- Each example has a `name:` field, capitalized, no trailing dot
- Use FQCN (`namespace.collection.module_name`)
- Use `true`/`false` for booleans (not `yes`/`no`)
- Cover the primary use case
- Example passwords/secrets must start with `EXAMPLE`
- Examples should be copy-paste ready

---

## 6. RETURN Block

```python
RETURN = r"""
resource:
  description: Details of the managed resource.
  returned: success
  type: dict
  sample:
    name: my_resource
    state: present
msg:
  description: Human-readable status message.
  returned: always
  type: str
  sample: "Resource created successfully"
"""
```

Rules:

- Every key needs: `description` (capitalized, trailing dot), `returned`, `type`, `sample`
- Add `elements` when `type: list`
- Use `contains` for nested dict/list structures
- If the module returns nothing: `RETURN = r''' # '''`
- `returned` is a human-readable string: `always`, `success`, `changed`, `when state is present`

---

## 7. Error Handling and Security

### Error reporting

- Always use `module.fail_json(msg='descriptive message')` — never `sys.exit()` or bare `raise`
- Fail fast: validate upfront with clear, actionable error messages
- Do not use catchall exceptions unless the underlying API provides detailed error messages
- Provide context about what was being attempted, appending exception details

### External commands

- Always use `module.run_command()` — never `subprocess`, `Popen`, or `os.system`
- Avoid the shell unless absolutely necessary
- When shell is required: set `use_unsafe_shell=True` and wrap user input with `shlex.quote(x)`
- Always check return codes

### HTTP requests

- Use `fetch_url` or `open_url` from `ansible.module_utils.urls`
- Never use `urllib2` — it does not natively verify TLS certificates

### Third-party library imports

```python
import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib

LIB_IMP_ERR = None
try:
    import some_library
    HAS_LIB = True
except ImportError:
    HAS_LIB = False
    LIB_IMP_ERR = traceback.format_exc()

def run_module():
    module = AnsibleModule(...)

    if not HAS_LIB:
        module.fail_json(
            msg=missing_required_lib('some_library'),
            exception=LIB_IMP_ERR,
        )
```

Document the dependency in the `requirements` section of DOCUMENTATION.

---

## 8. Module Output

- Modules must output valid JSON only to stdout
- Return data must be strict UTF-8 (use `errors='replace'` or base64 for non-UTF-8)
- Top-level return type must be a dictionary
- Never use `print()` — it breaks JSON output
- Never send output to stderr — it merges with stdout
- Always return useful data, even when `changed=False`
- Return values must be JSON-serializable basic types (str, int, dict, list, bool, float)
- Do not return raw Python objects — convert to dict fields
- Return diff when in diff mode (`module._diff`)
- Do not return entire log files or excessive data

### The changed key

`result['changed']` must accurately reflect whether the module made a real change. It must be `False` when no change occurred. This is fundamental to idempotency.

---

## 9. Code Structure

### Entry point

```python
def run_module():
    # All module logic here
    ...

def main():
    run_module()

if __name__ == '__main__':
    main()
```

The `if __name__` guard enables importing the module for unit testing without executing it.

### Imports

- Place imports after the RETURN block, not at the top of the file
- Use explicit imports: `from ansible.module_utils.basic import AnsibleModule`
- Never use wildcard imports: `from module_utils.basic import *`
- Import third-party packages inside `try`/`except` blocks (see section 7)

### Result dictionary

Seed the result dict at the start of `run_module()`:

```python
result = dict(
    changed=False,
)
```

Add return data to this dict throughout execution, then pass it to `module.exit_json(**result)` or `module.fail_json(msg=..., **result)`.

### Functions

- Keep functions concise — each should describe a meaningful amount of work
- Use underscore naming: `get_resource_state`
- Follow DRY — don't repeat yourself
- Add docstrings to functions
- Extract loop bodies into functions when nesting gets deep

---

## 10. Check Mode

### Declaration

```python
module = AnsibleModule(
    argument_spec=argument_spec,
    supports_check_mode=True,
)
```

Without this declaration, the module skips in check mode with a warning.

### Implementation

Guard each state-changing branch and report what *would* change:

```python
if existing is None and module.check_mode:
    result["changed"] = True
    result["msg"] = "Resource would be created"
    module.exit_json(**result)

# Proceed with actual changes below
```

Check mode should return what *would* change without making changes.

### Mandatory for info/facts

All `_info` and `_facts` modules MUST declare `supports_check_mode=True`. Since they make no changes, check mode behavior is identical to normal execution.

---

## 11. Info and Facts Modules

### Naming

- `_info` modules return general/non-host-specific information
- `_facts` modules return host-specific data (network interfaces, OS details, installed software)
- The `<something>` portion must be singular: `user_info`, not `users_info`
- Do not name modules `_facts` unless they return `ansible_facts`

### Mandatory requirements

1. Named `<something>_info` or `<something>_facts` (singular)
2. `_info` modules return in the result dictionary
3. `_facts` modules return in the `ansible_facts` field
4. Must support check mode (`supports_check_mode=True`)
5. Must NOT make any changes to the system
6. Must document all return fields in the RETURN block

### Facts return pattern

```python
module.exit_json(changed=False, ansible_facts=dict(
    my_resource=resource_data,
))
```

---

## 12. File Operations

Never write files directly. Use a temporary file and `atomic_move` from `ansible.module_utils.basic`:

```python
from ansible.module_utils.basic import AnsibleModule

# In module logic:
tmpfile = module.tmpdir + '/myfile.tmp'
# Write to tmpfile...
module.atomic_move(tmpfile, dest_path)
```

This prevents file corruption and preserves file context (permissions, SELinux context).

When using common file options, enable them with `add_file_common_args=True` and use `module.load_file_common_arguments()` / `module.set_fs_attributes_if_different()`.

---

## 13. Testing Requirements

### Integration tests

Every module should have integration tests at `tests/integration/targets/<module_name>/`.

Standard test pattern:

1. Call the module → `register: result`
2. Assert on `result` with `ansible.builtin.assert`
3. Verify actual state via a separate module or command → `register: verify` → assert

Cover:

- Happy path (create/configure)
- Idempotency (run same task twice, assert `changed: false`)
- Removal (`state: absent`)
- Edge cases and error conditions

Each test target needs `tests/integration/targets/<name>/meta/main.yml` for dependency declaration.

### Unit tests

Place under `tests/unit/plugins/modules/` mirroring the code structure.

Use for:

- Testing `module_utils` functions
- Forcing rare error conditions
- Testing against multiple API versions
- Quick feedback during development

### Sanity tests

Run `ansible-test sanity` to validate:

- Documentation format and completeness
- Import correctness
- PEP 8 compliance
- Python 2/3 compatibility

---

## 14. Deprecation and Backwards Compatibility

### Deprecating modules

Use the `deprecated` field in DOCUMENTATION with `removed_in`, `removed_from_collection`, `why`, and `alternative`.

### Deprecating options

Use `removed_in_version` or `removed_at_date` paired with `removed_from_collection` in the argument spec.

### Deprecating aliases

```python
deprecated_aliases=[
    dict(name='old_name', version='3.0.0', collection_name='ns.col'),
]
```

### Rules

- Never remove or rename parameters without a deprecation notice
- Never remove return values or change their types without deprecation
- Use `module.deprecate(msg, version=..., collection_name=...)` for runtime warnings
- Breaking changes must be flagged and justified

---

## 15. Complete State Module Template

A full, annotated template for a state-based module managing a resource with `present`/`absent`:

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: my_resource
short_description: Manage my_resource instances
description:
  - Create, update, or delete my_resource instances.
  - Supports check mode for dry-run operations.
version_added: "1.0.0"
options:
  name:
    description:
      - Name of the resource to manage.
    type: str
    required: true
  state:
    description:
      - Desired state of the resource.
    type: str
    choices:
      - present
      - absent
    default: present
  description:
    description:
      - Optional description for the resource.
    type: str
  force:
    description:
      - Force recreation of the resource if it already exists.
      - Mutually exclusive with O(update).
    type: bool
    default: false
  update:
    description:
      - Update the resource in place if it already exists.
      - Mutually exclusive with O(force).
    type: bool
    default: false
requirements:
  - some_sdk >= 1.0.0
author:
  - Your Name (@YourGitHub)
"""

EXAMPLES = r"""
- name: Create a resource
  namespace.collection.my_resource:
    name: example_resource
    state: present
    description: An example resource

- name: Force recreate a resource
  namespace.collection.my_resource:
    name: example_resource
    state: present
    force: true

- name: Remove a resource
  namespace.collection.my_resource:
    name: example_resource
    state: absent
"""

RETURN = r"""
resource:
  description: The resource object details.
  returned: when state is present
  type: dict
  contains:
    name:
      description: The resource name.
      type: str
      returned: always
      sample: example_resource
    id:
      description: The unique identifier of the resource.
      type: str
      returned: always
      sample: "abc-123"
msg:
  description: Human-readable result message.
  returned: always
  type: str
  sample: "Resource created successfully"
"""

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

LIB_IMP_ERR = None
try:
    import some_sdk

    HAS_SDK = True
except ImportError:
    HAS_SDK = False
    LIB_IMP_ERR = traceback.format_exc()


def get_resource(client, name):
    """Retrieve an existing resource by name, or None if not found."""
    try:
        return client.get(name)
    except some_sdk.NotFoundError:
        return None


def create_resource(module, client):
    """Create a new resource and return the result."""
    params = {
        "name": module.params["name"],
        "description": module.params.get("description", ""),
    }
    return client.create(**params)


def delete_resource(client, name):
    """Delete a resource by name."""
    client.delete(name)


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        description=dict(type="str"),
        force=dict(type="bool", default=False),
        update=dict(type="bool", default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ("force", "update"),
        ],
    )

    if not HAS_SDK:
        module.fail_json(
            msg=missing_required_lib("some_sdk"),
            exception=LIB_IMP_ERR,
        )

    result = dict(
        changed=False,
        msg="",
    )

    name = module.params["name"]
    state = module.params["state"]

    try:
        client = some_sdk.Client()
        existing = get_resource(client, name)

        if state == "present":
            if existing is None:
                if module.check_mode:
                    result["changed"] = True
                    result["msg"] = "Resource would be created"
                    module.exit_json(**result)

                resource = create_resource(module, client)
                result["changed"] = True
                result["resource"] = resource
                result["msg"] = "Resource created successfully"
            else:
                result["resource"] = existing
                result["msg"] = "Resource already exists"

        elif state == "absent":
            if existing is not None:
                if module.check_mode:
                    result["changed"] = True
                    result["msg"] = "Resource would be deleted"
                    module.exit_json(**result)

                delete_resource(client, name)
                result["changed"] = True
                result["msg"] = "Resource deleted successfully"
            else:
                result["msg"] = "Resource does not exist"

    except some_sdk.APIError as e:
        module.fail_json(
            msg="Failed to manage resource '{0}': {1}".format(name, str(e)),
            **result
        )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
```

---

## 16. Complete Info Module Template

A full template for an `_info` module:

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: my_resource_info
short_description: Retrieve information about my_resource instances
description:
  - Retrieve details of one or all my_resource instances.
  - This module does not make any changes to the system.
version_added: "1.0.0"
options:
  name:
    description:
      - Name of a specific resource to retrieve.
      - If omitted, all resources are returned.
    type: str
author:
  - Your Name (@YourGitHub)
"""

EXAMPLES = r"""
- name: Get all resources
  namespace.collection.my_resource_info:
  register: all_resources

- name: Get a specific resource
  namespace.collection.my_resource_info:
    name: example_resource
  register: resource_details
"""

RETURN = r"""
resources:
  description: List of resource objects.
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: The resource name.
      type: str
      returned: always
      sample: example_resource
    id:
      description: The unique identifier.
      type: str
      returned: always
      sample: "abc-123"
"""

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

LIB_IMP_ERR = None
try:
    import some_sdk

    HAS_SDK = True
except ImportError:
    HAS_SDK = False
    LIB_IMP_ERR = traceback.format_exc()


def run_module():
    argument_spec = dict(
        name=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    if not HAS_SDK:
        module.fail_json(
            msg=missing_required_lib("some_sdk"),
            exception=LIB_IMP_ERR,
        )

    result = dict(
        changed=False,
        resources=[],
    )

    try:
        client = some_sdk.Client()
        name = module.params.get("name")

        if name:
            resource = client.get(name)
            result["resources"] = [resource] if resource else []
        else:
            result["resources"] = client.list_all()

    except some_sdk.APIError as e:
        module.fail_json(
            msg="Failed to retrieve resource information: {0}".format(str(e)),
            **result
        )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
```

---

## 17. Anti-Patterns

Common mistakes and why they are wrong.

### Using `sys.exit()` instead of `fail_json`

**Wrong:**

```python
if error:
    sys.exit(1)
```

**Right:**

```python
if error:
    module.fail_json(msg="Descriptive error message")
```

**Why:** `sys.exit()` provides no structured output. `fail_json` returns valid JSON with the error message, allowing Ansible to handle the failure properly.

### Using `subprocess` instead of `run_command`

**Wrong:**

```python
import subprocess
result = subprocess.run(['ls', path], capture_output=True)
```

**Right:**

```python
rc, stdout, stderr = module.run_command(['ls', path])
```

**Why:** `module.run_command` respects Ansible's `become` settings, handles `check_mode`, and provides consistent error handling.

### Writing a custom module for an existing solution

**Wrong:** Creating a new module for behavior already handled by `ansible.builtin` or other higher-trust existing content.

**Right:** Reuse the highest-trust existing content first, and only author a custom module when existing options cannot solve the problem safely or maintainably.

**Why:** Duplicating existing automation increases maintenance cost, support burden, and security risk without improving the user experience.

### Using a module when an action plugin is the better fit

**Wrong:** Writing a remote module for controller-local API orchestration that never needs managed-host execution.

**Right:** Use an action plugin when the logic always runs locally on the controller and mainly coordinates APIs, cloud services, or other local-side work.

**Why:** Running a remote module for controller-local behavior adds unnecessary packaging and transport overhead while obscuring the real execution model.

### Using `print()` for output

**Wrong:**

```python
print("Processing resource...")
result = do_work()
module.exit_json(**result)
```

**Right:**

```python
result = do_work()
module.exit_json(**result)
```

**Why:** `print()` sends text to stdout before the JSON output, breaking JSON parsing. All output must go through `module.exit_json` or `module.fail_json`.

### Combining `required=True` with `default`

**Wrong:**

```python
name=dict(type='str', required=True, default='my_name')
```

**Right:**

```python
name=dict(type='str', required=True)
# OR
name=dict(type='str', default='my_name')
```

**Why:** If a parameter is required, the user must provide it — a default is contradictory.

### Wildcard imports

**Wrong:**

```python
from ansible.module_utils.basic import *
```

**Right:**

```python
from ansible.module_utils.basic import AnsibleModule
```

**Why:** Wildcard imports pollute the namespace, make dependencies unclear, and can mask naming conflicts.

### Missing `HAS_LIB` pattern

**Wrong:**

```python
import boto3

def run_module():
    module = AnsibleModule(...)
    client = boto3.client('ec2')
```

**Right:**

```python
import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib

LIB_IMP_ERR = None
try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    LIB_IMP_ERR = traceback.format_exc()

def run_module():
    module = AnsibleModule(...)
    if not HAS_BOTO3:
        module.fail_json(msg=missing_required_lib('boto3'), exception=LIB_IMP_ERR)
```

**Why:** Without graceful handling, a missing library causes an unstructured traceback instead of a helpful error message telling the user what to install.

### Not seeding the result dict

**Wrong:**

```python
def run_module():
    module = AnsibleModule(...)
    # ... do work ...
    module.exit_json(changed=True, data=result_data)
```

**Right:**

```python
def run_module():
    module = AnsibleModule(...)
    result = dict(changed=False)
    # ... do work, update result ...
    module.exit_json(**result)
```

**Why:** Seeding the result dict ensures consistent return structure. If the module fails mid-execution, `fail_json(**result)` still returns partial
data. It also prevents accidentally omitting the `changed` key.

### Using `urllib2` for HTTP requests

**Wrong:**

```python
import urllib2
response = urllib2.urlopen(url)
```

**Right:**

```python
from ansible.module_utils.urls import fetch_url
response, info = fetch_url(module, url)
```

**Why:** `urllib2` does not natively verify TLS certificates, creating security vulnerabilities. `fetch_url` handles TLS, proxies, and authentication correctly.

### Hyphens in module names

**Wrong:** `my-module.py`

**Right:** `my_module.py`

**Why:** Hyphens prevent Python from importing the module, breaking `ansible-doc` and test infrastructure.

### Writing files directly

**Wrong:**

```python
with open(dest_path, 'w') as f:
    f.write(content)
```

**Right:**

```python
tmpfile = os.path.join(module.tmpdir, 'myfile.tmp')
with open(tmpfile, 'w') as f:
    f.write(content)
module.atomic_move(tmpfile, dest_path)
```

**Why:** Direct writes risk file corruption on interruption and don't preserve file attributes (permissions, SELinux context). `atomic_move` writes to a temp file first, then moves it atomically.
