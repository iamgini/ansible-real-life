---
description: Review an Ansible collection for inclusion in the Ansible community package
argument-hint: "<collection-path>"
---

Review the Ansible collection at the specified path for inclusion in the Ansible community package.
Conduct a systematic checklist-based review following the official Ansible collection requirements and inclusion criteria.

## Arguments

Use `$ARGUMENTS` to access the local path to the collection's source code. If no path is provided, ask the user to specify the collection directory path.

## Workflow

1. **Validate collection path**
   - Verify that `$ARGUMENTS` contains a valid path to a collection directory
   - Confirm the path exists and contains a `galaxy.yml` file
   - If no path is provided, prompt the user for the collection location

2. **Parse collection metadata**
   - Locate and read the `galaxy.yml` file in the collection's root directory
   - Extract key metadata: `namespace`, `name`, `version`, `repository`, `authors`, `license`, and `tags`
   - Store this information for use in the report and verification steps

3. **Fetch the official collection checklist**
   - Retrieve the latest checklist from: https://github.com/ansible-collections/ansible-inclusion/blob/main/collection_checklist.md
   - Use this as the authoritative list of items to verify

4. **Conduct systematic review**
   - Go through each item in the fetched checklist systematically
   - For each item, follow the verification guidance detailed below
   - Refer to the documentation sources listed below for verification standards
   - Record findings for each checklist item: pass, fail, or needs manual review

5. **Generate review report**
   - Create a markdown report file named: `<namespace>_<collection_name>_review_report.md`
   - Follow the report structure specified in the Output section below
   - Include the full checklist with marks and detailed findings

## Verification Guidance

Use these sources and verification steps when reviewing checklist items:

### Documentation Sources

- **Collection Requirements**: https://docs.ansible.com/projects/ansible/devel/community/collection_contributors/collection_requirements.html
- **Collection Checklist**: https://github.com/ansible-collections/ansible-inclusion/blob/main/collection_checklist.md
- **Module Format and Documentation**: https://docs.ansible.com/projects/ansible/devel/dev_guide/developing_modules_documenting.html
- **Module Best Practices**: https://docs.ansible.com/projects/ansible/devel/dev_guide/developing_modules_best_practices.html
- **Release and Maintenance**: https://docs.ansible.com/projects/ansible/devel/reference_appendices/release_and_maintenance.html

### Specific Verification Steps

#### Published on Ansible Galaxy

- Construct the Galaxy URL: `https://galaxy.ansible.com/{namespace}/{name}` using values from `galaxy.yml`
- Verify the URL is reachable and the collection is present
- Use WebFetch if needed to check accessibility

#### Has a public git repository

- Use the `repository` URL from `galaxy.yml`
- Verify the URL is accessible and points to a valid git repository

#### Has README.md

- Check for the existence of a `README.md` file in the root of the collection directory
- Verify it contains meaningful content (not just a stub)

#### Repository should not contain unnecessary files

- Always report that this item needs manual review
- Note: This requires human judgment about what constitutes "unnecessary"

#### Documentation and return sections use version_added

- For each module, parse the `DOCUMENTATION` string
- Check that `version_added` is present for the module/plugin itself and for its options
- Exception: options added in the very first release may omit this
- Verify the version is the collection version, not the `ansible-core` version

#### Follows Ansible documentation standards

- Review module and plugin documentation against guidelines at the documentation URLs above
- Check for adherence to best practices
- Verify that `check_mode` support is specified in the `DOCUMENTATION` block of module files

#### Supports all Python versions

- Check `meta/runtime.yml` for the minimum supported `ansible-core` version
- Cross-reference with the Python support matrix at the release and maintenance URL
- If there are exceptions, verify they are documented in the collection's `README.md` and in documentation fragments/requirements module documentation sections

#### Follows development conventions

- **Idempotency**: Review module logic to ensure running multiple times with the same parameters results in the same state (often requires manual inspection)
- **`_info` modules**: Verify modules ending in `_info.py` only gather information and make no changes. Names should correspond to the information gathered (e.g., `user_info`)
- **`_facts` modules**: Verify modules ending in `_facts.py` return `ansible_facts` and do not return other data
- **No query state in modules**: Other modules should not have options like `state=get` or `state=query`. Such functionality should be in separate `_info` or `_facts` modules
- **`check_mode` support**: Ensure all `_info` and `_facts` modules support `check_mode`. Look for `supports_check_mode=True` in the `AnsibleModule` argument spec

## Output

Generate a markdown report file with the following structure:

### Report File Naming

- File name: `<namespace>_<collection_name>_review_report.md`
- Example: `cisco_ise_review_report.md`

### Report Structure

1. **Summary of Findings**
   - Brief summary of the review
   - Highlight critical issues
   - Overall recommendation (approve, reject, or needs fixes)

2. **Collection Metadata**
   - Display the key information from `galaxy.yml`
   - Include namespace, name, version, repository URL, license

3. **Completed Checklist**
   - Include the full checklist from the ansible-inclusion repository
   - Mark each item with `[x]` for pass or `[ ]` for fail/needs review
   - For any item that is not a clear pass, add a finding note directly below it

### Finding Formats

Use these three formats for findings:

**MUST FIX** - For requirements violations that block inclusion:

```markdown
- [ ] have a Code of Conduct (CoC) compatible with the Ansible Code of Conduct
  **MUST FIX:** The collection repository does not contain a `CODE_OF_CONDUCT.md` file.
```

**SHOULD FIX** - For strong recommendations (not blockers but highly recommended):

```markdown
- [ ] collection dependencies must have a lower bound on the version
  **SHOULD FIX:** The upper bound for the `ansible.utils` dependency is very restrictive (`<7.0`). Consider removing the upper bound for better future compatibility.
```

**NEEDS MANUAL REVIEW** - For items requiring human judgment:

```markdown
- [ ] modules satisfy the concept of idempotency
  **NEEDS MANUAL REVIEW:** Idempotency can only be partially checked automatically.
  A manual review of the module logic is required to confirm it is fully idempotent.
```

1. **Next Steps**
   - If there are MUST FIX items, list them clearly
   - Provide actionable guidance for the collection maintainer
   - Suggest priority order for addressing issues
