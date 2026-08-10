---
name: python-virtual-env
description: >-
  Creates or validates a project-local Python virtual environment (.venv by default)
  for isolated pip installs and local tooling. Typically invoked by setup-python-venv command.
  Use when setting up local Python dev, installing Python dependencies with pip, or before
  running non-Docker Python commands. Do not use when the user requests system Python,
  containers only, or ansible-test --docker.
user-invocable: true
---

# Skill: python-virtual-env

## Purpose

Set up a re-usable Python virtual environment for the AI agent and user. This is ideal for creating clean, isolated environments that can be used for multiple Python commands.

## When to Invoke

TRIGGER when:

- Invoked by the `setup-python-venv` command
- A user asks to set up a virtual environment or local Python development environment
- A user asks to use a specific virtual environment by name or path
- Local `pip install` or Python CLI tooling is needed (for example `antsibull-changelog`, linters, or project scripts)

DO NOT TRIGGER when:

- The user tells you to use the host system's Python environment or a container environment
- Work only requires `ansible-test --docker` (see the `run-tests` skill; no local venv is needed)

## Rules

When performing this skill:

- NEVER install packages to the host system (yum, dnf, apt, etc.) nor the system Python environment without asking the user and getting explicit permission.
- NEVER remove or uninstall versions of Python or packages from the host system.
- NEVER delete, modify, or re-create virtual environments at paths other than the **managed environment** (the name or path from Inputs).
- MAY create, delete, and re-create **only** the managed environment at its configured path—for example
  when creating it for the first time, when re-creating for a different Python version or tool, or when
  the user asks to remove that environment.
- For package installation in this skill, **always** use `<managed-env>/bin/pip`—never `pip`, `pip3`, or another environment's pip.

## Inputs and Setup

There are no required inputs from the user. However, inputs may be provided:

- The user may specify a virtual environment **name** or **path**:
  - If unspecified, default to `.venv` at the project root.
  - A bare **name** (for example `myenv` or `.venv`) is a directory at the **project root** with that basename (for example `./myenv`).
  - A **path** (relative or absolute) is used as given (for example `tools/.venv` or `/opt/myproject/venv`).
  - Resolve the result to a single path; that path is the **managed environment** for this invocation.

- The user may specify the tool they want to use for creating the virtual environment.
  - If the user does not specify, fall back to the `venv` module that comes with modern versions of Python. For example, `python -m venv .venv` creates a virtual environment at `.venv`.

- The user may specify the version of Python they want to use.
  - If the user does not specify, fall back to the `python3` command on their host system.

- The user may specify **packages** and/or **requirements files** to install into the managed environment (optional).
  - **Packages**: one or more PyPI package names or specifiers (for example `antsibull-changelog`, `pytest>=7.0`).
  - **Requirements files**: paths to files such as `requirements.txt` or `tests/unit/requirements.txt`.
  - If neither is specified, skip package installation (Step 5).

### Version matching

When comparing the user's requested version to `<managed-env>/bin/python --version` output:

- Request **X.Y** (for example `3.11`) → match **major.minor** only (`3.11.4` satisfies `3.11`).
- Request **X.Y.Z** (for example `3.11.8`) → match the full **major.minor.patch** triple.
- Parse the version from `python --version` output (for example `Python 3.11.4` → `3.11.4`).

## Reusing the environment

For subsequent Python commands in the same task:

- Prefer `<managed-env>/bin/python` and `<managed-env>/bin/pip` for one-off commands (works across separate shell invocations).
- Or run `source <managed-env>/bin/activate` and keep follow-up commands in the **same** shell session.

Tell the user both options in the report.

## Approach

### Step 1 — Check for an existing managed environment

If the user asked to **remove** the managed environment only (no re-create), go to Step 2 (delete only), then Step 6.

Otherwise, determine whether the managed environment path exists and whether its Python version matches
the requested version (if any). When the path exists, run `<managed-env>/bin/python --version` and apply
**Version matching** rules.

| State | Action |
| --- | --- |
| User asked to remove managed environment only | Go to Step 2 (delete only), then Step 6 |
| Does not exist | Go to Step 2 (create) |
| Exists, version matches (or no version requested) | Go to Step 3 (validate), then Steps 4–6 |
| Exists, version does not match user request | Go to Step 2 (re-create) |

Do not use or alter any other virtual environment directory on the system.

### Step 2 — Create, re-create, or delete the managed environment

**Delete only** (user asked to remove the managed environment):

- Delete **only** the managed environment path.
- Skip create. Go to Step 6 (report).

**Create or re-create**:

- If the managed environment does not exist, create it at the configured path.
- If it exists but must change (wrong Python version, different tool explicitly requested by the user,
  or user asked to refresh it), **re-create** it: delete **only** the managed environment path, then
  create it again. Do not change Python inside an existing `venv` in place.
- Re-create for a different tool **only** when the user explicitly requests that tool—not by inferring the tool from an existing directory.

When choosing the Python interpreter or tool:

- Some virtual environment tools may install a Python version that is not on the host. If the selected tool supports that, use it.
- If the tool does not support installing Python versions, search for other tools such as `uv`, `pyenv`,
  or `conda`. If one is available, ask the user before switching tools. For example:

  `I attempted to create a virtual environment with the 'venv' module, but I was unable to find Python
  version X on the host system. However, I found that 'uv' is available. Would you like me to create the
  virtual environment with 'uv' instead, or look for other options to install Python version X for the
  'venv' module?`

- If the user wants other options for the `venv` module, list Python versions found on the host. For
  example:

  `I was unable to find the version of Python you specified on the host system. I found versions X, Y
  and Z. Would you like me to install the missing version on your host system, or would you like to use
  one of the existing versions?`

After create or re-create, go to Step 3.

### Step 3 — Validate

Run:

```bash
<managed-env>/bin/python --version
```

- If a Python version was requested, confirm the output satisfies **Version matching**. If it does not, report the mismatch in Step 6 and do not claim the environment is ready.
- If no version was requested, record the reported version for Step 6.
- If `bin/python` is missing or the command fails, treat the environment as invalid; re-create if appropriate, or report the failure.

Then go to Step 4.

### Step 4 — Update ignore statements

- Ensure the managed environment is listed in `.gitignore`. Use the pattern `.venv/` when the default name applies; otherwise ignore the managed directory name (for example `my-env/`).
  - If `.gitignore` exists, **append** the ignore entry only when it is missing. Do not remove or replace other entries.
  - If `.gitignore` does not exist and the repository has no ignore file, create `.gitignore` containing only that ignore entry.

- If the project has a `galaxy.yml`, ensure `build_ignore` includes the managed environment directory
  name (for example `.venv`). If it does not, add it under the existing `build_ignore` list. Do not
  create `galaxy.yml` if it does not exist.

  Example addition when using the default path:

  ```yaml
  build_ignore:
    - .venv
  ```

Then go to Step 5.

### Step 5 — Install packages (optional)

Run this step **only** when the user specified packages and/or requirements files, the managed environment still exists, and Step 3 validation passed.

Use **only** the managed environment's pip:

```bash
<managed-env>/bin/pip install -r <requirements-file>
<managed-env>/bin/pip install <package> [<package> ...]
```

- Install each requirements file with `pip install -r` (one command per file).
- Install named packages in as few `pip install` commands as practical (a single command with multiple package arguments is fine).
- Do not use `pip` from the host, `pip3`, or any path outside the managed environment.
- Record every requirements file path and package specifier installed for the report.
- If an install fails, report the error in Step 6 and do not claim those packages are available.

If the user specified no packages or requirements files, skip this step.

Then go to Step 6.

### Step 6 — Report

Produce the structured report described in the **Output Format** section.

---

## Output Format

Structure the report as follows:

```
## Python Virtual Environment: <name or path>

### Summary
<One sentence describing what happened: created, re-created, validated, removed, packages installed, or no changes. If Step 5 ran on an existing environment, mention package installation even when the environment itself was unchanged.>

### Environment
- **Name:** ...
- **Path:** ... (relative to project root or absolute)
- **Python version:** ... (from `bin/python --version` validation in Step 3, if applicable)
- **Validation:** PASS | FAIL — <raw `python --version` output or error>
- **Tool used:** venv | uv | ... (if created or re-created)

### Activation
<source only if environment still exists>
source <path>/bin/activate

Or use <path>/bin/python and <path>/bin/pip for individual commands.

### Changes
<If removed: state the managed path was deleted.>

<If the environment was neither created, re-created, nor removed, and Step 5 did not run: write "No changes were made to the existing environment.">

<If only packages were installed (Step 5) on an existing environment: list package changes below; do not claim "no changes".>

Otherwise list:
- Whether the environment was created, re-created, or removed, and which tool was used (if applicable)
- Python version and validation result
- Any lines added to `.gitignore` and `galaxy.yml` `build_ignore`
- **Packages installed** (if Step 5 ran): list each requirements file (`pip install -r ...`) and each package or specifier installed (`pip install ...`). If Step 5 was skipped, omit this bullet.
```
