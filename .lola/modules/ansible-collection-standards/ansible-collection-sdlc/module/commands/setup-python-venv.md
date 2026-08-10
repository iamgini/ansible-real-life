---
description: Set up or validate a project-local Python virtual environment
argument-hint: "[env-path|name] [python-version] [packages...]"
---

Set up or validate a project-local Python virtual environment for isolated pip installs and local tooling.

Use the `python-virtual-env` skill to:

1. Resolve the managed environment path (default `.venv` at the project root, or use command arguments for name/path)
2. Check whether the environment exists and whether its Python version matches the request
3. Create, re-create, or remove **only** the managed environment (never other venvs on the system)
4. Validate with `<managed-env>/bin/python --version`
5. Update `.gitignore` and `galaxy.yml` `build_ignore` when applicable
6. Optionally install packages or requirements files with `<managed-env>/bin/pip` when the user specifies them
7. Report path, Python version, validation result, activation instructions, and any packages installed

Optional arguments: environment name or path; requested Python version (for example `3.11` or `3.11.8`);
package names or paths to requirements files (for example `requirements.txt`).
If the user asks to remove the environment, delete only the managed path and do not re-create.

The skill will present a structured report so you and the agent can reuse the same environment for subsequent Python commands in this project.
