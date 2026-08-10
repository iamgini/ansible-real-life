
<!-- lola:instructions:start -->
<!-- lola:module:ai-forge:start -->
# Ansible Collection Development

Module provides skills and commands for Ansible collection development workflows including commits, PRs, releases, and testing.

## When to Use

### Commands

- **/check-pr-actions command**: Use the `/check-pr-actions` command to check GitHub Actions or GitLab CI status for the current pull request or branch.
  Analyzes failures by examining logs, identifying patterns across matrix tests, and suggesting specific fixes.
  Invoke when asked to check PR status, CI status, "why is the PR failing?", or to troubleshoot GitHub Actions/GitLab CI failures.

- **/check-pr-sonarcloud command**: Use the `/check-pr-sonarcloud` command to check SonarCloud static analysis results for the current pull request.
  Uses get-pr-number to detect the PR and sonarcloud-remediation to fetch and analyze PR-specific issues.
  Invoke when asked to check SonarCloud for the PR, review static analysis results, or see what code quality issues affect the current PR.

### Skills

- **commit skill**: Use the `commit` skill when you want to create a conventional commit
  with FQCN scopes for Ansible collection content.
  Invoke when the user asks to "commit", "create a commit", or "git commit".

- **changelog-fragment skill**: Use the `changelog-fragment` skill to create or update changelog fragments for documenting changes.
  Supports automatic change analysis and PR URL updates.
  Invoke when asked to create a changelog fragment, add a fragment, or update fragments with PR URLs.

- **create-branch skill**: Use the `create-branch` skill to create a new feature branch following project conventions.
  Fetches latest from origin, bases branch off origin/main, and unsets upstream for fork workflows.
  Invoke when asked to create a branch, start new work, or "create a branch for...".

- **create-pr skill**: Use the `create-pr` skill to create a draft pull request with pre-flight checks, changelog validation, and automated formatting.
  Performs branch validation, checks for changelog fragments, optionally runs tests, analyzes changes to suggest PR details, and updates fragments with PR number.
  Invoke when asked to "create a PR", "make a pull request", or "open a PR".

- **pr-review skill**: Use the `pr-review` skill to review pull requests and code changes
  against project standards and the Ansible Collection Review Checklist.
  Invoke when asked to review a PR, patch, diff, or set of code changes.

- **remove-deprecations skill**: Use the `remove-deprecations` skill to find and remediate overdue deprecation warnings.
  Identifies deprecated code past removal date/version, categorizes by priority, and guides implementation of removal changes.
  Invoke when preparing for releases, cleaning up technical debt, or when asked to remove deprecations.

- **release skill**: Use the `release` skill to guide the release of an Ansible collection.
  Automatically determines the next version from changelog fragments
  and outputs step-by-step instructions.
  Invoke when asked to release, publish, or tag a new collection version.

- **run-tests skill**: Use the `run-tests` skill to run or write sanity, unit, and integration tests using `ansible-test`. Invoke when asked to run, check, or write tests for a module or utility.

- **sonarcloud-remediation skill**: Use the `sonarcloud-remediation` skill to fetch, analyze, and fix SonarCloud issues with end-to-end automation.
  Supports both project-wide debt reduction and PR-specific quality gates. Phase A analyzes and groups issues by rule and module with priority sorting.
  Phase B applies fixes with validation gates, batching, and strategic approval checkpoints.
  Invoke when asked to check, review, analyze, or fix SonarCloud results, code smells, security hotspots, or static analysis findings.

- **next-release skill**: Use the `next-release` skill to calculate next patch/minor/major release versions following SemVer.
  Invoke when asked what version to use for version_added tags or about next release versions.

### Utility Skills

- **current-release skill**: Helper skill that fetches the current release version from git tags/branches or galaxy.yml. Used internally by other skills.

- **get-branch-changes skill**: Helper skill that determines merge-base and changed files for the current branch, avoiding inclusion of unrelated changes when branch is behind target.
  Used internally by changelog-fragment and create-pr skills.

- **get-pr-action-results skill**: Helper skill that gets GitHub Actions/GitLab CI results for a pull request or branch, analyzes failures, and suggests fixes.
  Used internally by check-pr-actions command and other workflows.

- **get-pr-number skill**: Helper skill that determines the pull request number for a branch. Used internally by other skills.

- **get-upstream-info skill**: Helper skill that determines upstream repository information and service identifiers (GitHub/GitLab). Used internally by other skills.

## Configuration

**Optional Dependencies:**

- `antsibull-changelog` - Used for changelog generation
- `gh` CLI - Used for GitHub/GitLab operations (PRs, releases, upstream detection)
- `ansible-test` - Used for running sanity, unit, and integration tests
- `curl` - Used for fetching SonarCloud analysis results

**Required Context:**

- The collection must reside at `ansible_collections/<namespace>/<name>/` (relative to a directory on `ANSIBLE_COLLECTIONS_PATHS`) for imports to resolve correctly
- Collection identity (namespace, name, version) is read from `galaxy.yml`

## Notes

- All skills follow Ansible collection conventions and best practices
- The commit skill uses Conventional Commits 1.0.0 standard
- The changelog-fragment skill supports two modes: creating new fragments and updating existing fragments with PR URLs
- The release skill includes human confirmation gates at critical steps
- The pr-review skill produces structured reports with blockers/warnings/suggestions and a verdict
<!-- lola:module:ai-forge:end -->

<!-- lola:module:ansible-documentation:start -->
# Ansible Documentation

Module provides skills and commands for fetching official Ansible documentation
directly from docs.ansible.com as Markdown.

## When to Use

### Skills

- **ansible-markdown-docs skill**: Use the `ansible-markdown-docs` skill to fetch and render Ansible
  documentation from docs.ansible.com using the `Accept: text/markdown` header.
  Invoke when the user asks to "Get Ansible documentation", provides a `docs.ansible.com`
  URL, or asks to "fetch", "show", or "look up" Ansible docs.

## Configuration

**Required Dependencies:**

- `curl` — Used to fetch documentation pages from docs.ansible.com

## Notes

- Documentation is fetched using the `Accept: text/markdown` header, which instructs
  Read the Docs to return page content as Markdown instead of HTML.
- Only pages on `docs.ansible.com` are supported; the skill validates the URL before fetching.
<!-- lola:module:ansible-documentation:end -->
<!-- lola:instructions:end -->
