---
name: write-module
description: >-
  Scaffold new Ansible modules or review existing ones against official
  best practices from docs.ansible.com. Use when writing a new module
  from scratch, reviewing module code for compliance, or asking how to
  structure an Ansible module. Do NOT use for role scaffolding, playbook
  review, or PR-level review.
argument-hint: "[module-file-path or module-name]"
user-invocable: true
metadata:
  author: David Danielsson
  version: 1.0.0
---

# Skill: write-module

## Purpose

Scaffold new Ansible modules following official best practices, or review existing modules for compliance with the Ansible module development guidelines from docs.ansible.com.

## When to Invoke

TRIGGER when:

- A user asks to write, create, or scaffold a new Ansible module
- A user asks to review or check an existing module for best practices
- A user asks how to structure or format an Ansible module
- A user asks about module development conventions or requirements

DO NOT TRIGGER when:

- Reviewing a full PR (use `pr-review` instead)
- Scaffolding a role (use the `/ansible-scaffold-role` command instead)
- Reviewing playbooks or roles for CoP compliance (use the `/ansible-cop-review` command instead)
- Reviewing code philosophy/style (use `ansible-zen` instead)
- Running tests (use `run-tests` instead)
- General Ansible usage questions unrelated to module development

## Important

- This skill focuses on Python module files under `plugins/modules/`. It does not cover roles, playbooks, or non-Python modules.
- Always explain WHY a practice matters, not just WHAT to do. Users learn better when they understand the rationale.
- When reviewing, highlight what is done well — not every review needs to find problems. If the module is already well-written, say so.
- For scaffolding, always confirm what the module manages and its operational mode (state-based vs info/facts) before generating code.
- Before scaffolding a module, decide whether the problem is really a better fit for an
  action plugin. For controller-local orchestration, cloud/API-heavy workflows, or logic
  that always runs on the control node, prefer an action plugin over a remote module.
- Prefer existing Ansible content before creating a custom module. Selection order:
  `ansible.builtin` -> vendor-supported content -> content from verified authors -> general Galaxy content -> custom modules/plugins/roles only as a last resort.
- Avoid wrapping `ansible.builtin.shell`, `ansible.builtin.raw`, or ad hoc bash in a custom
  module unless there is a clear, explicit justification that no safer module or plugin approach
  will work.
- All guidance is sourced from the official Ansible documentation at docs.ansible.com. Keep the
  execution flow in this file, and use [reference.md](reference.md) for fuller scaffold variants,
  exact check-mode patterns, and the detailed review rules behind the checklist.

## Modes

Determine the mode based on the user's invocation and `$ARGUMENTS`:

- If `$ARGUMENTS` is a path to an existing Python file or an existing `plugins/modules/` directory → **Mode 2: Review**
- If `$ARGUMENTS` is a module name (no path separator, no `.py`) → **Mode 1: Scaffold**
- If `$ARGUMENTS` is empty → ask the user whether they want to scaffold or review
- If ambiguous → ask the user to clarify

---

### Mode 1: Scaffold a New Module

Generate a complete, best-practice-compliant Ansible module from scratch.

#### Step 1 — Confirm a New Module Is Necessary

Before scaffolding, check whether a new custom module is justified:

- First, check whether `ansible.builtin` already solves the problem
- If builtin content is not sufficient, prefer vendor-supported content, then content from verified authors, then general Galaxy content
- Only scaffold a custom module when no suitable existing content meets the need safely, idempotently, or maintainably
- Decide whether the use case should be a module or an action plugin:
  - Prefer a module when work must run on the managed host or return managed-host facts/state
  - Prefer an action plugin when the work always runs on the controller, primarily orchestrates APIs/cloud services, or would just proxy local logic before calling other modules
- If the user's request can be solved by combining existing modules/plugins cleanly, recommend that approach instead of generating a new module
- If a custom module is still needed, capture the gap it fills so the rationale is explicit in the generated guidance

#### Step 2 — Gather Inputs

Collect the following from the user (ask if not provided):

- **Module name**: Must use underscores, not hyphens. If the name ends in `_info` or `_facts`, switch to the info/facts variant.
- **Purpose**: What does the module manage? What actions does it perform?
- **State model**: Is this a state-based module (`present`/`absent`, `started`/`stopped`) or an action module?
- **Parameters**: What inputs does the module accept? Which are required? Which are sensitive?
- **Dependencies**: Does the module need third-party Python libraries?

If a `galaxy.yml` exists in the project, read it to determine the collection namespace and name for
FQCN examples.

If the companion `next-release` skill is available from the `ansible-collection-sdlc` module, use
it to determine the next unreleased collection version for `version_added`. Otherwise, ask the user
which release this module is targeting. Only fall back to the current `galaxy.yml` version when it
clearly represents the next unreleased collection version.

#### Step 3 — Validate Naming

- Module name MUST use underscores only (not hyphens or spaces)
- `_info` and `_facts` module names must use a singular noun before the suffix
- Reject reserved option names: `action`, `command`, `message`, `syslog_facility`

#### Step 4 — Derive Argument Spec

From the user's description, build the `argument_spec` dictionary:

- Set `type` on every parameter (`str`, `bool`, `int`, `list`, `dict`, `path`)
- Set `required=True` only for mandatory params — never combine with `default`
- Set `no_log=True` for passwords, tokens, secrets, API keys
- Add `choices` where a fixed set of values applies
- Add `elements` when `type='list'`
- Define `mutually_exclusive`, `required_together`, `required_one_of`, `required_if`, `required_by` where applicable
- Use `fallback=(env_fallback, ['ENV_VAR'])` for connection parameters

#### Step 5 — Generate the Module File

Use the template in the **Module Template** section below. Place the file at `plugins/modules/<module_name>.py`.

#### Step 6 — Generate Documentation Blocks

Follow these formatting rules precisely:

**DOCUMENTATION:**

- `module:` matches filename without `.py`
- `short_description:` — concise, NO trailing period
- `description:` — full sentences, each starting with capital letter and ending with period
- `version_added:` — string, quoted, collection version (not ansible-core version)
- `options:` — each option has `description` (full sentences, periods) and `type`; add
  `required: true` for required params and `default` only when the code sets a real default
- `author:` — `First Last (@GitHubID)` format

**EXAMPLES:**

- Multi-line plain-text YAML
- Each example has a `name:` line (capitalized, no trailing dot)
- Use FQCN for the module name
- Use `true`/`false` for booleans (not `yes`/`no`)
- Cover the primary use case and `state: absent` if applicable

**RETURN:**

- Every returned key has `description` (capitalized, trailing dot), `returned`, `type`, `sample`
- Add `elements` if `type: list`
- If no return values: `RETURN = r''' # '''`

#### Step 7 — Post-Scaffold

After generating the module:

1. Suggest running `ansible-test sanity --test validate-modules plugins/modules/<name>.py` to verify documentation and argument spec
2. Suggest using the `write-module-tests` skill to generate unit and integration tests
3. Suggest creating a changelog fragment manually or with the companion `changelog-fragment` skill if the `ansible-collection-sdlc` module is installed

#### Info/Facts Module Variant

When the module name ends in `_info` or `_facts`, apply these additional requirements:

- Set `supports_check_mode=True` — mandatory, not optional
- The module MUST NOT make any changes to the system
- `_info` modules return data in the result dictionary
- `_facts` modules return data in `module.exit_json(changed=False, ansible_facts=dict(...))`
- `changed` is always `False`
- RETURN block must document all returned fields

---

### Mode 2: Review an Existing Module

Audit an existing module file against the best practices checklist.

#### Step 1 — Discover Scope

- If `$ARGUMENTS` is a file path, review that file
- If `$ARGUMENTS` is a directory, find all `*.py` files under `plugins/modules/`
- If no arguments, review all modules in the current project's `plugins/modules/`

#### Step 2 — Read the Code

Read every file completely before forming any judgment. Do not make assessments from partial reads.

#### Step 3 — Evaluate Against Checklist

Run through every category in the **Review Checklist** below. Collect findings per category. For the full detailed rules behind each check, consult [reference.md](reference.md).

#### Step 4 — Score

Rate overall compliance on a 1-10 scale:

- **9-10**: Exemplary — follows all practices, well-documented, clean structure
- **7-8**: Good — follows most practices, minor issues only
- **5-6**: Acceptable — works but has notable gaps in documentation, structure, or safety
- **3-4**: Needs work — significant violations in multiple categories
- **1-2**: Non-compliant — fundamental structural or safety issues

#### Step 5 — Top Recommendations

List the 3 most impactful changes that would improve compliance. Focus on changes that affect correctness, safety, or maintainability — not style preferences.

---

## Module Template

Use this skeleton when scaffolding. Every section is required and must appear in this exact order.

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: module_name
short_description: One-line summary without trailing period
description:
  - First sentence of the detailed description.
  - Second sentence providing additional context.
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
author:
  - First Last (@GitHubID)
"""

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

RETURN = r"""
resource:
  description: The resource details.
  returned: success
  type: dict
  sample:
    name: my_resource
    state: present
"""

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

# Third-party imports with graceful degradation
some_library = None
LIB_IMP_ERR = None
try:
    import some_library

    HAS_LIB = True
except ImportError:
    HAS_LIB = False
    LIB_IMP_ERR = traceback.format_exc()


def get_client():
    """Build the client used to talk to the backing service."""
    return some_library.Client()


def get_resource(client, name):
    """Return the existing resource or None."""
    raise NotImplementedError()


def create_resource(module, client):
    """Create the resource and return serialized data."""
    raise NotImplementedError()


def delete_resource(client, name):
    """Delete the resource."""
    raise NotImplementedError()


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    if not HAS_LIB:
        module.fail_json(
            msg=missing_required_lib("some_library"),
            exception=LIB_IMP_ERR,
        )

    result = dict(
        changed=False,
    )

    name = module.params["name"]
    state = module.params["state"]

    try:
        client = get_client()
        existing = get_resource(client, name)

        if state == "present":
            if existing is None:
                if module.check_mode:
                    result["changed"] = True
                    result["msg"] = "Resource would be created"
                    module.exit_json(**result)

                result["resource"] = create_resource(module, client)
                result["changed"] = True
                result["msg"] = "Resource created successfully"
            else:
                result["resource"] = existing
                result["msg"] = "Resource already exists"
        else:
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
    except Exception as exc:
        module.fail_json(msg=to_native(exc), **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
```

When the module has no third-party dependencies, omit the `HAS_LIB` pattern, `traceback` import, and the `if not HAS_LIB` check.
This minimal scaffold keeps explicit helper seams so the default unit-test pattern can patch
resource lookup and mutation cleanly. For fuller variants such as nested argument specs, update
paths, and `_info`/`_facts` modules, use [reference.md](reference.md).

---

## Review Checklist

| Category | What to Check |
|----------|---------------|
| Reuse Strategy | Custom module is justified only when higher-trust existing content (`ansible.builtin` -> vendor-supported -> content from verified authors -> general Galaxy) does not already solve the problem; action plugins are considered for controller-local/API-heavy logic; wrappers around `shell`/`raw` are explicitly justified |
| File Structure | `#!/usr/bin/python` shebang (not `#!/usr/bin/env`), `# -*- coding: utf-8 -*-`, copyright header, `__future__` imports, sections in order: DOCUMENTATION → EXAMPLES → RETURN → imports → code |
| Naming | Underscores only (no hyphens), singular `_info`/`_facts` suffix, no reserved names (`action`, `command`, `message`, `syslog_facility`) |
| DOCUMENTATION | `module` matches filename, `short_description` (no trailing period), `description` (full sentences with periods), `version_added` (quoted string, collection version), `options` with `description` and `type`, `required: true` on required params, `default` only when code sets one, `author` |
| EXAMPLES | Valid YAML, each example has `name:` (capitalized, no trailing dot), uses FQCN, `true`/`false` booleans, covers primary use case |
| RETURN | Present (even if empty: `r''' # '''`), `description` (capitalized, trailing dot), `returned`, `type`, `sample`, `elements` if `type: list` |
| Argument Spec | `type` on every param, `no_log=True` for secrets, no `required=True` + `default` together, inter-option dependencies declared, `choices` types match param `type` |
| Error Handling | `module.fail_json(msg=...)` for errors (not `sys.exit()` or bare `raise`), `module.run_command()` for external commands (not `subprocess`), `fetch_url`/`open_url` for HTTP (not `urllib2`), clear error messages |
| Idempotency | `changed` is `False` when no real change occurs, repeated runs with same args produce same outcome |
| Check Mode | `supports_check_mode=True` declared in AnsibleModule constructor, `module.check_mode` checked before making changes, mandatory for `_info`/`_facts` modules |
| Security | `no_log=True` on passwords/tokens/secrets, no user input passed to shell unescaped, `shlex.quote()` used with `use_unsafe_shell=True`, example secrets start with `EXAMPLE` |
| Code Structure | `main()` function with `if __name__ == '__main__': main()` guard, no wildcard imports, `HAS_LIB` + `missing_required_lib()` pattern for optional deps, result dict seeded at start |
| Output | No `print()` calls, no output to stderr, top-level return is a dict, return values are JSON-serializable basic types, always returns useful data even when unchanged |

---

## Output Format

### Scaffold Mode

After generating the module file, output:

```
## Scaffolded: <namespace>.<collection>.<module_name>

### File
`plugins/modules/<module_name>.py`

### Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| ... | ... | ... | ... | ... |

### Next Steps
1. Run `ansible-test sanity --test validate-modules plugins/modules/<module_name>.py`
2. Replace the placeholder helper functions with the real client and resource operations
3. Use `write-module-tests` to generate unit and integration tests
4. Create a changelog fragment
```

### Review Mode

```
## Module Review: <file path>

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
| Reuse Strategy | PASS / FAIL / N/A | ... |
| File Structure | PASS / FAIL / N/A | ... |
| Naming | PASS / FAIL / N/A | ... |
| DOCUMENTATION | PASS / FAIL / N/A | ... |
| EXAMPLES | PASS / FAIL / N/A | ... |
| RETURN | PASS / FAIL / N/A | ... |
| Argument Spec | PASS / FAIL / N/A | ... |
| Error Handling | PASS / FAIL / N/A | ... |
| Idempotency | PASS / FAIL / N/A | ... |
| Check Mode | PASS / FAIL / N/A | ... |
| Security | PASS / FAIL / N/A | ... |
| Code Structure | PASS / FAIL / N/A | ... |
| Output | PASS / FAIL / N/A | ... |

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
| Write unit and integration tests for the module | `write-module-tests` |
| Determine `version_added` for scaffolded module | `next-release` |
| Run sanity checks after scaffold or review | `run-tests` |
| Review the module as part of a PR | `pr-review` |
| Review code for philosophical alignment | `ansible-zen` |
