---
description: Scaffold a new Ansible content collection following Red Hat CoP good practices
argument-hint: "[namespace.name]"
---

Create a new Ansible content collection that fully complies with every rule in CLAUDE.md.
Leverage ansible-creator when available, falling back to manual creation if needed.

## Arguments

Use `$ARGUMENTS` to access the optional namespace.name parameter (e.g., `mycompany.mycollection`). If not provided, ask the user for namespace and collection name separately.

## Workflow

1. **Gather inputs**

   Ask the user for (unless already provided in `$ARGUMENTS`):
   - **Namespace** — the collection namespace (snake_case) — required
   - **Collection name** — the collection name (snake_case, no dashes) — required
   - **Target path** — where to create the collection (default: current directory)
   - **Description** — brief description of the collection's purpose
   - **Author** — author name and email
   - **License** — license type (default: GPL-3.0-or-later)
   - **Initial roles** — list of role names to include (optional).
     For each role, follow the full ansible-scaffold-role command process (interactive variable builder, task componentization, smart handlers, etc.)
   - **Repository URL** — source repository URL (optional)
   - **Plugins** — does the collection need custom plugins? (optional)
     - **Modules** — custom modules to manage specific resources
     - **Filters** — custom Jinja2 filters
     - **Lookup plugins** — custom lookup plugins
     - **Action plugins** — custom action plugins

     For each requested plugin, ask for a name and brief description.
   - **CI/CD platform** — which CI platform to generate a pipeline for (optional). Supported: GitHub Actions, GitLab CI. Default: GitHub Actions

2. **Execute scaffolding strategy**

   - Run `ansible-creator init collection <namespace>.<name> <path>` to generate the base skeleton
   - If `ansible-creator` is not installed, fall back to creating the directory structure manually and inform the user
     they can install it with `pip install ansible-creator` or use the `ansible-dev-tools` devcontainer for future use
   - Customize the generated files for full compliance with CLAUDE.md rules
   - If initial roles were requested, use `ansible-creator add resource role <role_name> <collection_path>` for each role
     (or create manually if ansible-creator is unavailable), then apply the full ansible-scaffold-role command process to each role —
     including the interactive variable builder, task componentization, smart handler generation, and all CoP compliance rules

3. **Customize galaxy.yml**

   - Verify namespace and name are snake_case with no dashes
   - Set version to `1.0.0` (semantic versioning)
   - Fill in description, authors, license, repository
   - Add any required dependencies

4. **Create README.md**

   Include:
   - Collection overview and purpose
   - Installation instructions (`ansible-galaxy collection install`)
   - List of included roles with brief descriptions
   - List of included plugins (if any)
   - Requirements (Ansible version, Python version, dependencies)
   - License and author info
   - Link to full documentation

5. **Ensure LICENSE file**

   Ensure the license file matches the license specified in galaxy.yml

6. **Configure meta/runtime.yml**

   Set `requires_ansible` to a sensible minimum version (e.g., `>=2.15.0`)

7. **Set up collection-wide variables**

   If roles share common configuration, create implicit collection-wide variables referenced in each role's `defaults/main.yml`. Document these in the collection README.

8. **Scaffold roles**

   For each role, follow the full ansible-scaffold-role command process.
   This includes the interactive variable builder, task componentization, smart handler generation, argument_specs,
   platform support patterns, and all CoP compliance rules. Do not just create empty role skeletons.

9. **Generate plugins**

   If the user requested custom plugins, generate proper skeletons:

   - **Modules** — create in `plugins/modules/<name>.py` with:
     - Full `DOCUMENTATION`, `EXAMPLES`, and `RETURN` docstrings
     - `AnsibleModule` boilerplate with `argument_spec`
     - FQCN reference in the examples: `<namespace>.<collection>.<module>`
   - **Filters** — create in `plugins/filter/<name>.py` with:
     - `FilterModule` class with `filters()` method
     - Docstring with usage examples
   - **Lookup plugins** — create in `plugins/lookup/<name>.py` with:
     - `LookupModule` class extending `LookupBase`
     - Full `DOCUMENTATION`, `EXAMPLES`, and `RETURN` docstrings
   - **Action plugins** — create in `plugins/action/<name>.py` with:
     - `ActionModule` class extending `ActionBase`
     - Docstring explaining the action's purpose

   Keep `__init__.py` files in all plugin directories.

10. **Cleanup sample content**

    - Remove or replace the sample plugins (`sample_action.py`, `sample_filter.py`, `sample_lookup.py`, `sample_module.py`, `sample_test.py`) —
      keep only the `__init__.py` files in plugin directories unless the user requested specific plugins
    - Remove the sample `run` role if the user specified their own initial roles
    - Update molecule scenarios to reference actual roles
    - Update integration test targets to match actual roles

11. **Set up changelogs**

    Create `changelogs/config.yaml` for `antsibull-changelog`:

    ```yaml
    ---
    changelog_filename_template: CHANGELOG.rst
    changelog_filename_version_depth: 0
    changes_file: changelog.yaml
    changes_format: combined
    keep_fragments: false
    mention_ancestor: true
    new_plugins_after_name: removed_features
    sanitize_changelog: true
    sections:
      - - major_changes
        - Major Changes
      - - minor_changes
        - Minor Changes
      - - breaking_changes
        - Breaking Changes / Porting Guide
      - - deprecated_features
        - Deprecated Features
      - - removed_features
        - Removed Features (previously deprecated)
      - - security_fixes
        - Security Fixes
      - - bugfixes
        - Bugfixes
      - - known_issues
        - Known Issues
    title: <namespace>.<collection>
    trivial_section_name: trivial
    ```

    Create `changelogs/fragments/.gitkeep` so the fragments directory is tracked.

12. **Generate CI/CD pipeline**

    Generate a working CI pipeline based on the user's chosen platform.

    **GitHub Actions** (`.github/workflows/ci.yml`):
    - Lint job: `ansible-lint` and `yamllint`
    - Sanity job: `ansible-test sanity`
    - Unit test job: `ansible-test units` (if unit tests exist)
    - Integration test job: `ansible-test integration` or molecule
    - Build job: `ansible-galaxy collection build`
    - Publish job (on tag): `ansible-galaxy collection publish` with `ANSIBLE_GALAXY_API_KEY` secret

    **GitLab CI** (`.gitlab-ci.yml`):
    - Same stages adapted to GitLab CI syntax

    Only generate the pipeline for the platform the user chose. Include comments explaining required secrets and manual setup steps.

13. **Create collection-level CLAUDE.md**

    Generate a `CLAUDE.md` at the collection root so future Claude Code sessions understand the collection:
    - Collection namespace and name
    - List of roles with brief descriptions
    - List of plugins with brief descriptions
    - Build command: `ansible-galaxy collection build`
    - Test command: `ansible-test sanity` and molecule commands
    - Changelog workflow: `antsibull-changelog release`
    - Reference to CoP rules

14. **Configure testing infrastructure**

    - Keep the generated molecule, tox, and CI workflows
    - Update test references to match the actual collection content
    - Ensure `.pre-commit-config.yaml` is configured appropriately

15. **Validate post-scaffold**

    After creating all files, verify:
    - `galaxy.yml` has valid semantic version
    - All role names are snake_case with no dashes
    - All roles have `meta/argument_specs.yml`
    - All roles have compliant `defaults/main.yml` and `vars/main.yml`
    - README and LICENSE exist at collection root
    - No sample/placeholder content remains unless intentional
    - YAML uses 2-space indent and `true`/`false` booleans throughout
    - All plugins have proper docstrings with FQCN examples
    - `changelogs/config.yaml` exists and is valid
    - CI pipeline references actual collection content
    - Collection-level `CLAUDE.md` exists and is accurate

## Rules Source

If the rules are not available locally (no CLAUDE.md with Ansible rules or `redhat-cop-automation-good-practices-*.md`),
fetch them from https://github.com/redhat-cop/automation-good-practices as a fallback.

## Output

Report what was created:

- Collection path
- List of generated files (grouped by category: roles, plugins, tests, CI, changelogs, documentation)
- Build command: `ansible-galaxy collection build`
- Any manual steps the user should take next (e.g., adding Galaxy API key secret, authenticating to Automation Hub, writing integration tests)
