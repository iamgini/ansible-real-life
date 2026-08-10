# Changelog Validation and Fixes

**CRITICAL**: Fix common antsibull-changelog bugs after running `antsibull-changelog release`.

## Issue 1: changelog.yaml indentation errors

antsibull-changelog has a known bug where it generates incorrect YAML indentation (4 spaces instead of 6/8 for list items). This causes ansible-lint to fail in CI even though tox linters pass locally.

**IMPORTANT**: You must check ALL list structures in the entire file, not just the new release section. The bug affects multiple release entries and different list types.

**Complete validation checklist:**

1. **Read the entire changelog.yaml file** (not just the new release section)
2. **Check ALL occurrences** of these list structures:
   - `fragments:` - list items must be 6 spaces
   - `modules:` - list items must be 6 spaces, with `name:`/`namespace:` at 8 spaces
   - `plugins:` - nested items (e.g., `connection:`) must be 8 spaces, with `name:`/`namespace:` at 10 spaces
   - `minor_changes:` / `bugfixes:` / `breaking_changes:` - list items must be 8 spaces (nested under `changes:`)
   - `major_changes:` / `deprecated_features:` / `removed_features:` - list items must be 8 spaces

3. **Validate with ansible-lint** after fixing:

   ```bash
   ansible-lint --offline changelogs/changelog.yaml
   ```

**Common indentation patterns to fix:**

```yaml
# WRONG Pattern 1: fragments list items at 4 spaces
    fragments:
    - 1.1.0.yml
    - other-fragment.yml

# CORRECT: fragments list items at 6 spaces
    fragments:
      - 1.1.0.yml
      - other-fragment.yml
```

```yaml
# WRONG Pattern 2: minor_changes list items at 6 spaces
      minor_changes:
      - Added new feature to module
      - Updated documentation

# CORRECT: minor_changes list items at 8 spaces
      minor_changes:
        - Added new feature to module
        - Updated documentation
```

```yaml
# WRONG Pattern 3: modules with name/namespace at 6 spaces
    modules:
      - description: Call a specific tool
      name: run_tool
      namespace: ''

# CORRECT: modules with name/namespace at 8 spaces (aligned with description)
    modules:
      - description: Call a specific tool
        name: run_tool
        namespace: ''
```

```yaml
# WRONG Pattern 4: plugins nested items at 6 spaces
    plugins:
      connection:
      - description: Persistent connection
      name: mcp
      namespace: null

# CORRECT: plugins nested items at 8 spaces, name/namespace at 10 spaces
    plugins:
      connection:
        - description: Persistent connection
          name: mcp
          namespace: null
```

**Pro tip:** After fixing indentation, always validate the entire file:

```bash
# Validate YAML syntax
ansible-lint --offline changelogs/changelog.yaml

# Should output: "Passed: 0 failure(s), 0 warning(s)"
```

**Why this happens:**
antsibull-changelog generates different list items inconsistently across releases. Even if you
fixed indentation during a previous release (e.g., 1.0.0), the next release (e.g., 1.1.0) will
have the same bug. You must check the entire file every time, not just the new release section.

**RECOMMENDATION**: Fix indentation as a **separate commit** before the release PR:

```bash
# 1. Fix indentation issues FIRST
ansible-lint --offline changelogs/changelog.yaml
# (Fix any indentation errors found)

# 2. Commit separately
git add changelogs/changelog.yaml
git commit -m "Fix changelog.yaml indentation (antsibull-changelog bug)"

# 3. THEN proceed with release
# Run antsibull-changelog release, and you'll only see new changes in the diff
```

This keeps your release PR focused on the actual release changes, not historical indentation fixes.

## Issue 1b: release_summary line too long

ansible-lint enforces a 160-character line length limit. If the release_summary exceeds this, break it into multiple lines using YAML's implicit string continuation:

```yaml
# WRONG (line too long):
      release_summary: This minor release adds new features and enhancements to the ansible.mcp collection, including enhanced ``tools_info`` action plugin with server metadata support, JQ query support for MCP server event auditing, and updates to the ``run_tool`` module for node count query support.

# CORRECT (broken into multiple lines):
      release_summary: This minor release adds new features and enhancements to the
        ansible.mcp collection, including enhanced ``tools_info`` action plugin with
        server metadata support, JQ query support for MCP server event auditing, and
        updates to the ``run_tool`` module for node count query support.
```

**Note:** When using YAML implicit continuation (no `>` or `|`), line breaks are collapsed into spaces, producing the same single-line output as the original.

## Issue 2: .plugin-cache.yaml committed

collection_prep (run by docs-generate) creates `changelogs/.plugin-cache.yaml`. This file should never be committed (it's in build_ignore).

Remove it if present:

```bash
if [ -f "changelogs/.plugin-cache.yaml" ]; then
  rm -f "changelogs/.plugin-cache.yaml"
  echo "Removed .plugin-cache.yaml (auto-generated, should not be committed)"
fi
```
