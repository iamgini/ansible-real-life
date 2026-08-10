# Ansible Collection

Module provides skills and commands for Ansible collection development, review, and scaffolding following Red Hat CoP automation good practices.

## When to Use

- **ansible-zen skill**: Use the `ansible-zen` skill when you want to see the Zen of Ansible principles, get philosophical guidance on automation approach,
  or review code for simplicity, readability, and clarity. Invoke with `/ansible-zen` or when discussing code complexity and readability.

- **ansible-cop-review command**: Use `/ansible-cop-review` to audit Ansible code against all Red Hat CoP automation good practices.
  Supports severity classification (ERROR/WARNING/INFO), diff-aware reviews of changed files, category filtering for specific rule types,
  ansible-lint integration, parallel review with subagents for large projects, and auto-fix offer.

- **ansible-scaffold-collection command**: Use `/ansible-scaffold-collection` to create a new Ansible content collection with plugin scaffolding
  (modules, filters, lookup, action), CI/CD pipeline generation (GitHub Actions or GitLab CI), antsibull-changelog setup,
  and collection-level CLAUDE.md generation. Delegates role creation to ansible-scaffold-role process.

- **ansible-collection-inclusion-review command**: Use `/ansible-collection-inclusion-review` to review an Ansible collection for inclusion
  in the Ansible community package. Performs systematic checklist-based review following official Ansible collection requirements and inclusion criteria.

## Configuration

**Optional Dependencies:**

- `ansible-creator` CLI - Used by scaffold commands to generate base skeletons (falls back to manual creation if not installed)
- `ansible-lint` - Used by review command for cross-referencing CoP rules with ansible-lint findings

**Required Context:**

- CoP rules from `CLAUDE.md` and `redhat-cop-automation-good-practices-*.md` files
- Fallback to https://github.com/redhat-cop/automation-good-practices when rules not available locally

## Notes

- All scaffold commands follow a gather-inputs → generate → customize → validate pattern
- Review commands focus on helping users improve their code, not gatekeeping
- Skills reference and follow Red Hat Communities of Practice automation good practices
- ansible-zen provides philosophical/style guidance, while ansible-cop-review provides strict rule compliance checking
