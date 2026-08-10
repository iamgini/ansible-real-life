---
name: docs-generate
description: >-
  Generate or update Ansible collection documentation using collection_prep.
  Use when module documentation needs updating, after changing module arguments
  or return values, before releases, or when README needs regeneration.
  Automatically updates module RST files and README.md with current module
  information.
user-invocable: false
---

# Skill: docs-generate

## Purpose

Generate or update Ansible collection documentation using the collection_prep tool.
Runs `tox -e add_docs` to automatically generate module/plugin documentation RST files
and update README.md with current module information from DOCUMENTATION strings.

## When to Use

- After changing module documentation, arguments, or return values
- Before creating a release
- When adding new modules to a collection
- After updating doc fragments
- When README.md needs regeneration with current module list

## Prerequisites

- Python 3.8+
- tox (pip install tox)
- collection_prep (installed via tox or pip install git+https://github.com/ansible-network/collection_prep)
- tox.ini with `add_docs` environment

## Usage

```bash
# Navigate to collection
cd /path/to/collection

# Verify tox.ini has add_docs environment
grep -q "\[testenv:add_docs\]" tox.ini || echo "Missing add_docs environment"

# Run documentation generation
tox -e add_docs

# Verify documentation was generated
ls -la docs/*.rst
git diff README.md
```

## Required tox.ini Configuration

```ini
[testenv:add_docs]
deps = git+https://github.com/ansible-network/collection_prep
commands = collection_prep_add_docs -p .
```

## What Gets Generated

### Module RST Files (docs/*.rst)

One file per module with:

- Module synopsis
- Parameters documentation
- Return values
- Examples
- Author information
- Links to GitHub

Example: `docs/amazon.aws.ec2_instance.rst`

### Updated README.md

- List of all modules with descriptions
- Ansible version compatibility matrix
- Installation instructions
- Links to documentation

## Post-Generation Fixes for Stable Branch Releases

**CRITICAL**: collection_prep always generates README.md links pointing to the `main` branch.

For stable-branch releases, manually correct links:

```bash
# Wrong (generated):
/blob/main/docs/

# Correct (for stable-11 release):
/blob/stable-11/docs/
```

**Fix command**:

```bash
# For stable-11 release (portable across macOS and Linux)
sed -i.bak 's|/blob/main/docs/|/blob/stable-11/docs/|g' README.md && rm README.md.bak
```

## Troubleshooting

### "tox.ini missing [testenv:add_docs]"

Add to your `tox.ini`:

```ini
[testenv:add_docs]
deps = git+https://github.com/ansible-network/collection_prep
commands = collection_prep_add_docs -p .
```

### "collection_prep fails to install"

```bash
pip install git+https://github.com/ansible-network/collection_prep
collection_prep_add_docs -p .
```

### "No modules found"

Check your collection structure:

```
plugins/
  modules/
    *.py  # Module files must be here
```

## Post-Generation Validation

After running, verify:

- ✅ `docs/` directory exists
- ✅ One RST file per module (*.rst)
- ✅ README.md has module list
- ✅ No errors in collection_prep output
- ✅ Galaxy.yml repository URL is set (required by collection_prep)

## Integration

This skill is used by:

- `stable-release` - Release orchestrator (generates docs before commit)
- `release` - Standard release workflow

## Reference

- [collection_prep GitHub](https://github.com/ansible-network/collection_prep)
