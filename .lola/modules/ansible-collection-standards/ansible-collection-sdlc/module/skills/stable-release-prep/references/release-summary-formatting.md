# Release Summary Formatting Rules

Per cloud-content-handbook guidelines, wrap all module/plugin/collection names in double backticks:

**✅ Correct:**

```yaml
release_summary: >-
  This release includes updates to the ``my_module`` and ``other_module``
  modules for better ``aws_service`` integration.
```

**❌ Incorrect (missing backticks):**

```yaml
release_summary: >-
  This release includes updates to the my_module and other_module
  modules for better aws_service integration.
```

**❌ Incorrect (using `|` instead of `>`):**

```yaml
release_summary: |
  This release includes updates to the ``my_module`` and ``other_module``
  modules for better ``aws_service`` integration.
```

**Why use `>` (folded block scalar)?**

- `>` collapses line breaks into spaces, producing clean single-line output in changelog.yaml
- `|` (literal block scalar) preserves blank lines exactly, causing awkward formatting in changelog.yaml
- Both are valid YAML, but `>` produces cleaner antsibull-changelog output

**Example output comparison:**

```yaml
# Using `>` (correct):
release_summary: This release includes updates to the ``my_module`` and ``other_module`` modules for better ``aws_service`` integration.

# Using `|` (produces blank lines):
release_summary: 'This release includes updates to the ``my_module`` and ``other_module``

  modules for better ``aws_service`` integration.

  '
```

## Module Name Detection

The generate-release-summary.py script extracts module names from git diff:

- Pattern: `plugins/modules/MODULE_NAME.py`
- Automatically wraps in backticks: ``MODULE_NAME``
- Generates appropriate summary based on fragment categories
