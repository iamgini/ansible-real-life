---
name: sonarcloud-remediation
description: >-
  Fetch, analyze, and fix SonarCloud issues with end-to-end automation.
  Supports both project-wide debt reduction and PR-specific quality gates.
  Phase A analyzes and groups issues by rule and module with priority sorting.
  Phase B applies fixes with validation gates, batching, and strategic approval checkpoints.
user-invocable: true
---

# Claude Skill: SonarCloud Issue Remediation

Fetch SonarCloud issues, analyze and group them, suggest fixes, and create focused PRs with human-in-the-loop review.

---

## Setup

### Prerequisites

- **`gh`** (GitHub CLI) or **`glab`** (GitLab CLI) — one must be installed and authenticated, matching the repo's hosting platform.
Used by `/sonarcloud-fix` to create PRs/MRs and post comments. The skill auto-detects the platform from the git remote URL.
- **`python3`** (3.8+) — used by the fetch script (`scripts/sonarcloud-fetch.py`). Uses only Python stdlib (no external dependencies).

### Environment Variables

All variables can be set as environment variables beforehand **or** provided interactively when the skill starts. Interactive prompting avoids requiring engineers to exit the session to configure the environment.

| Variable | When needed | Purpose |
|----------|-------------|---------|
| `SONAR_BASE_URL` | Phase A, B (optional) | Base URL of the Sonar API. Defaults to `https://sonarcloud.io/api`. Set this to target a self-hosted SonarQube instance (e.g. `https://sonarqube.corp.redhat.com/api`). |
| `SONAR_ORGANIZATION` | Phase A, B | SonarCloud organization slug. **Required for SonarCloud; optional for self-hosted SonarQube.** |
| `SONAR_PROJECT_KEY` | Phase A, B | Sonar project key |
| `SONARCLOUD_TOKEN` | Private projects only | API authentication token. **Must be set as an environment variable before starting Claude** — the skill will never prompt for or handle this value directly. Works with both SonarCloud and SonarQube tokens. |
| `SONAR_DEFAULT_BRANCH` | Phase B | Base branch for fix PRs (e.g. `main`, `devel`) |
| `SONAR_VALIDATE_COMMANDS` | Phase B | Validation commands that must pass before PR creation (e.g. `npm run tsc && npm run vitest`) |
| `SONAR_PR_COMMENT` | Phase B (optional) | Comment to post automatically on each newly created PR/MR. Commonly used to trigger CI workflows (e.g. `/run-playwright`). If not provided, no comment is posted. Set to `none`, `skip`, `false`, or empty string `""` to explicitly disable. |

---

## Phase A — Analyze

Invoked via `/sonarcloud-analyze`. Fetches all open issues and presents a prioritized, grouped report.

### Step 0: Collect Configuration

Before fetching data, detect the hosting platform and collect required variables.

#### Step 0a: Detect hosting platform

Read the git remote URL to determine whether this is a GitHub or GitLab repository:

```bash
git remote get-url origin

```

- If the URL contains `github.com` → **GitHub** (use `gh` CLI)
- If the URL contains `gitlab` → **GitLab** (use `glab` CLI)
- If unclear, ask the engineer: "Is this repo hosted on GitHub or GitLab?"

Store the detected platform for use in Phase B.

#### Step 0b: Collect SonarCloud variables

Check whether the required variables are available as environment variables. For any that are missing, prompt the engineer interactively using AskUserQuestion.

1. If `SONAR_ORGANIZATION` is not set and the target is SonarCloud (no `SONAR_BASE_URL` override), ask: "What is your SonarCloud organization slug?" For self-hosted SonarQube instances,
`SONAR_ORGANIZATION` is optional — skip this prompt.
2. If `SONAR_PROJECT_KEY` is not set, ask: "What is your Sonar project key?"
3. If `SONARCLOUD_TOKEN` is not set and the project is private, **do not prompt for the token**. Instead, guide the engineer to set it up themselves and restart Claude:

   > "This project requires a `SONARCLOUD_TOKEN` for API access. Please set it as an environment variable and restart Claude:
   >
   > ```bash
   > export SONARCLOUD_TOKEN=<your-token>
   > ```
   >
   > You can generate a token at your Sonar instance's account security page (e.g. https://sonarcloud.io/account/security for SonarCloud). Once the variable is set, restart Claude and re-run the command."

   Then **stop the workflow** — do not proceed without the token in the environment.

**IMPORTANT - Ansible Collections Integration:**

For Ansible collections repos, attempt to auto-detect configuration using the `get-upstream-info` skill:

```
Invoke get-upstream-info skill to get:

- UPSTREAM_PATH (e.g., ansible-collections/amazon.aws)
- SONARCLOUD_KEY (e.g., ansible-collections_amazon.aws)
- UPSTREAM_ORG (e.g., ansible-collections)
- UPSTREAM_REPO (e.g., amazon.aws)

```

**Cache these values** for use throughout the skill execution. If `get-upstream-info` succeeds, use `SONARCLOUD_KEY` as `SONAR_PROJECT_KEY` and `UPSTREAM_ORG` as `SONAR_ORGANIZATION`.

After collecting the required values, also remind the engineer: "If you plan to fix issues after analysis, I'll need a few more values later —
the base branch name and your validation commands. You can provide them now or when we get to the fix phase."

If the engineer provides Phase B values at this point (`SONAR_DEFAULT_BRANCH`, `SONAR_VALIDATE_COMMANDS`, `SONAR_PR_COMMENT`), store them for later use and skip re-prompting in Phase B Step 0.

Use the collected values for the remainder of the session.

#### Step 0c: Determine analysis mode

**Auto-detect mode from context:**

- If user mentions "PR", "pull request", or provides a PR number → **PR-specific mode**
- If current branch has an open PR and user asks to "check sonar" → **PR-specific mode**
- Otherwise → **Project-wide mode**

**For PR-specific mode, get PR number:**

- If user provided a number as argument, use it
- Otherwise, for Ansible collections, use the `get-pr-number` skill to detect PR for current branch:

  ```
  Invoke get-pr-number skill to get:

  - PR_NUMBER
  - PR_FOUND (boolean)
  - PR_STATE

  ```

- If `PR_FOUND` is false, inform user and ask if they want project-wide analysis instead

**Determine issue type filter (optional):**

Ask the user which types to analyze (or analyze all if not specified):

- **Security hotspots** - Security vulnerabilities and potential security issues
- **Reliability issues** - Bugs and potential runtime errors
- **Maintainability issues** - Code smells and technical debt
- **All issues** - Everything combined

### Step 1: Fetch and Categorize Issues

Run the fetch script to retrieve all SonarCloud data. If `SONAR_ORGANIZATION` or `SONAR_PROJECT_KEY` were provided interactively (not via environment variables), pass them as inline environment
variables. **Never pass `SONARCLOUD_TOKEN` on the command line** — it must already be in the environment.

```bash
SONAR_PROJECT_KEY=<value> SONAR_ORGANIZATION=<value> python3 ansible-collection-sdlc/module/skills/sonarcloud-remediation/scripts/sonarcloud-fetch.py

```

If all values are already set as environment variables, run the script directly:

```bash
python3 ansible-collection-sdlc/module/skills/sonarcloud-remediation/scripts/sonarcloud-fetch.py

```

**For PR-specific mode, pass the PR number:**

```bash
SONAR_PR_NUMBER=<PR_NUMBER> python3 ansible-collection-sdlc/module/skills/sonarcloud-remediation/scripts/sonarcloud-fetch.py

```

The script handles pagination, authentication, and categorization automatically. It outputs JSON to stdout with this structure:

- `project_key` — the project key used
- `fetched_at` — ISO timestamp of when data was fetched
- `pr_number` — PR number if in PR-specific mode
- `issues.total` — total issue count
- `issues.items[]` — array of issues, each with: `key`, `component` (relative file path), `type` (BUG/VULNERABILITY/CODE_SMELL), `severity`, `line`, `message`, `rule`
- `hotspots.total` — total hotspot count
- `hotspots.items[]` — array of hotspots, each with: `key`, `component`, `securityCategory`, `vulnerabilityProbability`, `line`, `message`, `rule`, `status`
- `duplication` — object with `duplicated_lines_density`, `duplicated_blocks`, `duplicated_files`
- `categories` — pre-grouped object with keys: `Security`, `Reliability`, `Maintainability`, `Security Hotspots`, `Duplication`

If the script exits with code 1, read the `error` field from its JSON output and display the error message to the user. Common errors:

- Missing env vars → prompt the user to set them
- HTTP 401 → invalid token
- HTTP 404 → wrong project key
- `"hint": "missing_organization"` → the Sonar instance requires an organization. Prompt the user: "This Sonar instance requires an organization.
What is your Sonar organization slug?" Then re-run the fetch script with `SONAR_ORGANIZATION` set to the provided value.

Parse the JSON output. Use the `categories` object as the starting point for Step 2.

### Step 2: Group by Rule + Module

Within each category, group issues by **SonarCloud rule key** and **module** (workspace, package, or top-level directory depending on the repo structure).

**Special handling for Security Hotspots:**

Security hotspots should be grouped by **securityCategory** and module (not by rule key), as the category provides more actionable context than individual rules.
The fetch script provides a `securityCategory` field for each hotspot. Use these standardized category names:

- `weak-cryptography` - Cryptographic issues (often `random` module usage, weak hashing algorithms)
- `encrypt-data` - Data encryption issues (HTTP vs HTTPS, unencrypted storage)
- `dos` - Denial of Service vulnerabilities (regex backtracking, resource exhaustion)
- `permission` - Permission and access control issues
- `injection` - Injection vulnerabilities (SQL, command, XSS)
- `auth` - Authentication issues
- `insecure-conf` - Insecure configuration
- `others` - Uncategorized security issues

Group identifier format for hotspots: `<securityCategory> — <module>` (e.g., `weak-cryptography — plugins/module_utils`, `encrypt-data — frontend/awx`).

For all other issue types (Reliability, Maintainability, Security), use the standard grouping: `<rule key> — <module>`.

#### Detecting Modules

Determine the repo's module structure **once at the start of analysis**, then apply it consistently to all issues.

#### Step 2a: Check for monorepo workspace definitions

Look for workspace/package definitions in this order:

1. **`package.json` `workspaces`** — NPM/Yarn workspaces (array of glob patterns like `["frontend/*", "framework"]`)
2. **`pnpm-workspace.yaml`** — pnpm workspaces (`packages:` list)
3. **`nx.json`** or `workspace.json` — Nx monorepo
4. **`lerna.json`** — Lerna monorepo (`packages` list)

If any of these exist, resolve the workspace patterns to actual directories. Map each issue's `component` file path to the workspace whose path prefix matches.
Use the workspace directory name (or a human-friendly label derived from it) as the module name.

Example: if `package.json` has `"workspaces": ["frontend/*", "framework"]`, then:

- `frontend/awx/src/Foo.tsx` → module `frontend/awx`
- `framework/PageTable.tsx` → module `framework`
- `scripts/build.js` → module `root`

#### Step 2b: No workspace definitions found (non-monorepo)

Group issues by their **top-level directory** from the `component` field (the first path segment after the project key). Files in the repo root go into a `root` group.

Example:

- `src/api/handler.ts` → module `src`
- `lib/utils.ts` → module `lib`
- `tests/unit/foo.test.ts` → module `tests`
- `README.md` → module `root`

#### Step 2c: Ansible collection module detection

For Ansible collections (detected by presence of `galaxy.yml` or `plugins/` directory), use Ansible-specific module grouping:

- `plugins/modules/` → module `modules`
- `plugins/module_utils/` → module `module_utils`
- `plugins/inventory/` → module `inventory`
- `tests/unit/` → module `tests/unit`
- `tests/integration/` → module `tests/integration`
- Root files → module `root`

#### Group Identifier

Each group is identified as: `<rule key> — <module>` (e.g., `typescript:S1854 — frontend/awx`, `python:S1481 — modules`).

### Step 3: Sort by Remediation Priority

Within each category, sort groups by this priority order. Match by rule ID suffix (the numeric part is language-agnostic in SonarCloud —
e.g., `S1128` appears as `typescript:S1128`, `python:S1128`, `java:S1128`, etc.):

1. Unused imports and variables (`S1128`, `S1481`, `S1144`)
2. Dead code / dead stores (`S1854`, `S1186`, `S1068`)
3. Duplicate string literals (`S1192`)
4. Unused function parameters (`S1172`)
5. Commented-out code (`S125`)
6. Simple type safety improvements (`S4325`, `S4204`, `S1874`)
7. Cognitive complexity (`S3776`)
8. Security hotspot rules
9. Reliability / bug rules
10. All other rules

Rules not matching any priority bucket sort to the end, ordered by issue count descending.

### Step 4: Estimate LOC Impact

For each group, estimate the lines of code that will change:

- Unused imports: ~1 LOC per issue (removal)
- Dead stores: ~1-2 LOC per issue
- Duplicate strings: ~2-3 LOC per issue (extract to const + references)
- Unused parameters: ~1 LOC per issue
- Commented-out code: variable, count the commented lines from issue details
- Type safety: ~1-3 LOC per issue
- Cognitive complexity: ~10-20 LOC per issue (refactoring)

### Step 5: Present Summary Table

Display one table per category. Include total issue count in the heading.

**CRITICAL: Use a single continuous numbering sequence across all categories.** The group `#` is the ID that `/sonarcloud-fix` uses to select groups.
It must be globally unique, not reset per category. All rows — including security hotspots — must use the same table format with the rule or category identifier in parentheses.

**Include mode context at the top:**

```
SonarCloud Analysis
===================
Project: <project-key>
Mode: <Project-wide | Pull Request #<PR_NUMBER>>
Issue Types: <All | Security | Reliability | Maintainability>
Link: https://sonarcloud.io/project/<issues or pull_requests>?id=<PROJECT_KEY><&pullRequest=<PR_NUMBER>>

```

**Example output:**

```
## Maintainability (847 issues)

| # | Group                              | Module          | Count | Severity | Est. LOC | Note      |
|---|------------------------------------|-----------------|-------|----------|----------|-----------|
| 1 | Unused imports (typescript:S1128)   | frontend/awx    |   45  | Minor    |   ~45    |           |
| 2 | Dead stores (typescript:S1854)      | frontend/awx    |   23  | Major    |   ~35    |           |
| 3 | Duplicate strings (typescript:S1192)| framework       |   12  | Minor    |   ~36    |           |
| 4 | Cognitive complexity (typescript:S3776) | frontend/hub|   8   | Critical |  ~120    | Will split |
...

## Reliability (42 issues)

| # | Group                              | Module          | Count | Severity | Est. LOC | Note      |
|---|------------------------------------|-----------------|-------|----------|----------|-----------|
| 5 | Constant nullishness (typescript:S6638) | frontend/awx|   2   | Major    |    ~4    |           |
...

## Security (5 issues)

| # | Group                              | Module          | Count | Severity | Est. LOC | Note      |
|---|------------------------------------|-----------------|-------|----------|----------|-----------|
| 8 | SQL injection (typescript:S2077)    | frontend/hub   |   1   | Blocker  |    ~5    |           |
...

## Security Hotspots (18 issues)

| # | Group                              | Module          | Count | Severity | Est. LOC | Note      |
|---|------------------------------------|-----------------|-------|----------|----------|-----------|
|11 | Weak cryptography (weak-cryptography) | frontend/awx |   3   | Medium   |    ~6    |           |
|12 | Data encryption (encrypt-data)     | frontend/awx    |   1   | Low      |    ~2    |           |
...

## Duplication
Duplicated lines density: 3.2%  |  Duplicated blocks: 47  |  Duplicated files: 12
(Duplicate string literal issues are listed under Maintainability above.)

```

Flag any group where Est. LOC > 200 with "Will split" in the Note column.

At the end of the report, suggest low-risk starting groups for `/sonarcloud-fix` using their group numbers:

```
Good starting groups for /sonarcloud-fix:
  /sonarcloud-fix 1   — Unused imports (45 issues, ~45 LOC, Low risk)
  /sonarcloud-fix 2   — Dead stores (23 issues, ~35 LOC, Low risk)

```

**Tip:** If you plan to fix issues after analysis, it's best to have `SONAR_DEFAULT_BRANCH` and `SONAR_VALIDATE_COMMANDS` ready.
You can set them as environment variables beforehand, or provide them interactively when Phase B starts.

### Optional Filters

If the user provides flags, apply them before grouping:

- `--severity <BLOCKER|CRITICAL|MAJOR|MINOR|INFO>` — only show issues at or above this severity
- `--module <name>` — only show issues in the specified module

### Step 6: Detailed Issue Analysis (Optional)

For high-priority groups or when requested by the user, provide detailed analysis:

**a) List each issue with context:**

```
File: plugins/modules/ec2_instance.py:234
Rule: python:S3776 (Cognitive Complexity)
Severity: CRITICAL
Message: Refactor this function to reduce its Cognitive Complexity from 45 to the 15 allowed.

Context: The `ensure_present()` function has deeply nested conditionals and loops
that make it difficult to understand and maintain.

```

**b) Read the affected code:**
Use the Read tool to show the relevant lines with context.

**c) Explain the issue:**

- What is the rule checking for?
- Why is this a problem?
- What are the potential impacts (security, reliability, maintainability)?

**d) Suggest fixes:**

- Specific, actionable recommendations
- Example code where applicable
- Note if this appears to be a false positive

**e) Link to rule documentation:**

```
Rule details: https://rules.sonarsource.com/python/RSPEC-<number>

```

### Step 7: Prioritization and Recommendations

**Prioritize issues by:**

1. **BLOCKER/CRITICAL severity** - Address immediately
2. **Security hotspots** - Review and address based on risk
3. **High-severity bugs** - Address in next iteration
4. **Maintainability issues** - Plan for incremental improvement

**Provide actionable recommendations:**

- "Fix the 2 BLOCKER issues before merging this PR"
- "Review the 5 weak-cryptography hotspots - 3 appear to be false positives (UUID generation)"
- "Consider refactoring ec2_instance.py to address the 8 MAJOR complexity issues"
- "The 15 code smell issues are low priority and can be addressed incrementally"

### Step 8: Next Steps

**For PR-specific analysis:**

- If issues are found: "These issues were introduced in this PR. Would you like to fix them before merging?"
- If no issues: "No new issues introduced by this PR ✓"

**For project-wide analysis:**

- Ask if the user wants to focus on a specific category
- Suggest creating issues/tickets for tracking
- Recommend periodic reviews to track progress

---

## Phase B — Fix

Invoked via `/sonarcloud-fix`. The engineer selects groups from the analyze output and the skill applies fixes with approval.

### Step 0: Configuration Pre-Check

**Before doing any work**, check all required Phase B configuration. If any variables are missing and were not already provided during Phase A Step 0, prompt the engineer interactively using AskUserQuestion.

#### Step 0a: Collect missing Phase B variables

If `SONAR_DEFAULT_BRANCH` is not set (env var or earlier prompt), ask:
> "What is the base branch for fix PRs? (e.g. `main`, `devel`)"

If `SONAR_VALIDATE_COMMANDS` is not set (env var or earlier prompt), ask:
> "What validation commands must pass before a PR can be created? (e.g. `npm run tsc && npm run vitest`, `make lint && make test`)"

If `SONAR_PR_COMMENT` is not set (env var or earlier prompt), ask:
> "Do you want a comment posted automatically on each PR/MR? This is commonly used to trigger CI workflows (e.g. `/run-playwright`). Provide the comment text, or type 'skip' to disable."

Use the values provided for the remainder of the session.

#### Step 0b: Display configuration summary

Display all non-sensitive configuration values so the engineer can verify them:

```
## Configuration

| Variable                  | Value                          | Source      | Description                                        |
|---------------------------|--------------------------------|-------------|----------------------------------------------------|
| SONAR_ORGANIZATION        | your-org                       | env         | SonarCloud organization slug                       |
| SONAR_PROJECT_KEY         | your-project-key               | env         | SonarCloud project key                             |
| SONARCLOUD_TOKEN          | (set)                          | env         | API token for private projects                     |
| SONAR_DEFAULT_BRANCH      | main                           | interactive | Branch that fix PRs will target                    |
| SONAR_VALIDATE_COMMANDS   | make lint && make test         | interactive | Commands that must pass before a PR can be created |
| SONAR_PR_COMMENT          | /run-playwright                | env         | Comment posted automatically on each PR/MR         |

```

- Show `(set)` or `(not set)` for `SONARCLOUD_TOKEN` — never display the actual value. This variable is always sourced from the environment (never interactive).
- In the Source column, show `env` if from an environment variable or `interactive` if provided via prompt
- If `SONAR_PR_COMMENT` was skipped or not provided, show `(not set — no comment will be posted)` in the Value column
- If `SONAR_PR_COMMENT` is set to `none`, `skip`, `false`, or an empty string, show `(disabled)` in the Value column

Then ask: "Do these settings look correct? If any need updating, let me know."

- If the engineer confirms → proceed to Step 1
- If the engineer wants to change a value → prompt for the new value and update the session configuration

**Skip this pre-check** if it was already confirmed earlier in the same session.

### Step 1: Select Groups

If the user provided a group number or name as an argument, use that.

If no group was specified, prompt interactively:

1. If no `/sonarcloud-analyze` was run in this session, run it first to generate the group table
2. Display the available groups (or remind the user of the table)
3. Ask which group(s) to fix — accept by number from the analyze table, by rule key, or by name
4. Multiple groups can be selected at once

### Step 2: Read Affected Files

For each issue in the selected group(s):

1. Read the affected file using the Read tool
2. Focus on the specific line number and surrounding context (~10 lines above/below)
3. Identify whether the issue is a true positive or false positive

### Step 3: Present Fixes as a Group

**CRITICAL: Present fixes at the group level, not individually.** With thousands of open issues, per-fix approval is not efficient.

Display:

```
## Group: Unused imports (typescript:S1128) — frontend/awx (45 issues)

**Severity:** Minor  |  **Risk:** Low  |  **Est. LOC changed:** ~45

| # | File                                          | Line | Issue                        | Proposed Fix          |
|---|-----------------------------------------------|------|------------------------------|-----------------------|
| 1 | frontend/awx/views/jobs/JobsList.tsx           |   3  | Remove unused import `Foo`   | Delete import line    |
| 2 | frontend/awx/views/jobs/JobsList.tsx           |   7  | Remove unused import `Bar`   | Delete import line    |
| 3 | frontend/awx/components/ResourceCard.tsx       |  12  | Remove unused import `Baz`   | Delete import line    |
...

**Risk Assessment:** Low — removing unused imports has no runtime effect.

```

### Step 4: Get Fix Approval

Ask the engineer to:

- **Approve all** — apply every fix in the group
- **Exclude specific files** — list file numbers to skip
- **Reject** — skip this group entirely

### Fix Strategies by Rule Pattern

These strategies apply across languages. Adapt to the project's language and conventions.

| Rule Pattern | Fix Strategy | Caution |
|---|---|---|
| Unused imports | Remove the import/include/require line | Check for side-effect imports (e.g., CSS imports, polyfills, module-level init) — do not remove those |
| Dead stores | Remove the unused assignment | Check for intentional destructuring or unpacking patterns |
| Duplicate strings | Extract to a named constant at the top of the file or a shared constants module | Use descriptive names; check if a shared constant already exists in the project |
| Unused function parameters | Remove if internal function; prefix with `_` if required by an interface, override, or callback signature | Verify the function isn't part of a public API or framework contract |
| Commented-out code | Delete entirely | Git history preserves it; no need to keep |
| Type safety (e.g., `any` in TypeScript, raw types in Java) | Replace with proper types using existing project type definitions | Check for existing types/interfaces in the project before creating new ones |
| Cognitive complexity | Extract nested logic into helper functions | Ensure extracted functions are testable and well-named |

### Step 5: Apply Fixes and Validate

Apply all approved fixes using the Edit tool.

**CRITICAL: Cap at ~200 LOC per PR.** If the group exceeds 200 LOC of changes:

- Split into batches by file or logical grouping
- Each batch becomes its own branch
- Inform the engineer: "This group will produce N branches of ~X LOC each."

**Add Unit Tests for Refactoring Changes:**

When extracting complex logic into helper functions (especially for cognitive complexity fixes):

1. **Identify extraction opportunities** - New helper functions extracted from complex code
2. **Write unit tests** for the extracted functions:
   - Test happy path with typical inputs
   - Test edge cases and boundary conditions
   - Test error handling if applicable
3. **Place tests appropriately**:
   - For Ansible collections: `tests/unit/plugins/module_utils/` or `tests/unit/plugins/modules/`
   - For other projects: Follow the project's test directory structure
4. **Document expected behavior** - Unit tests serve as documentation for future maintainers

**Why unit tests for extractions:**

- Extracted functions are smaller and more focused than the original code
- They're ideal candidates for unit testing
- Tests prevent regression when code is modified later
- Tests document the intended behavior

**Validation — Hard Gate:**

After applying fixes (and adding any necessary unit tests), run the validation commands using the value from the environment variable or the value provided interactively in Step 0.

```bash
eval "$SONAR_VALIDATE_COMMANDS"

```

**For Ansible collections**, if validation commands are not set, run:

```bash
# Run sanity tests on changed files
ansible-test sanity --changed

# Run unit tests (including newly added tests)
ansible-test units --coverage

# Run integration tests if behavior changed
# (optional, ask engineer first as integration tests can be time-consuming)
ansible-test integration <target>

```

If validation fails:

1. Read the error output
2. Diagnose whether the fix introduced the failure
3. Correct the fix
4. Re-run validation
5. Do not proceed to branch creation until validation passes

### Step 6: Create Branch and Commit (Approval 1)

**Branch** off the configured default branch, using the value from the environment variable or the value provided interactively in Step 0.

**Branch naming strategy:**

**For Ansible collections** - Use type-specific naming to align with collection development conventions:

```bash
# Security issues
git checkout -b "security/<category>" "origin/$SONAR_DEFAULT_BRANCH"
# Examples: security/weak-cryptography, security/encrypt-data

# Reliability issues
git checkout -b "reliability/<category>" "origin/$SONAR_DEFAULT_BRANCH"
# Examples: reliability/duplicate-branches, reliability/cognitive-complexity

# Maintainability issues
git checkout -b "maintainability/<module-name>" "origin/$SONAR_DEFAULT_BRANCH"
# Examples: maintainability/ec2_instance, maintainability/botocore

# Mixed types
git checkout -b "sonarcloud/<description>" "origin/$SONAR_DEFAULT_BRANCH"
# Examples: sonarcloud/critical-issues, sonarcloud/pr-blockers

```

**For other projects** - Use rule-specific naming:

```bash
git checkout -b "sonar/<rule-key>-<module-slug>" "origin/$SONAR_DEFAULT_BRANCH"

```

Where `<module-slug>` is the module name with `/` replaced by `-` (e.g., `sonar/S1854-frontend-awx`, `sonar/S1128-framework`, `sonar/S1481-src`)

**Commit** with a descriptive message:

```
fix: remove dead stores in frontend/awx (SonarCloud S1854)

Addresses 23 typescript:S1854 violations in frontend/awx/.
SonarCloud issue keys: AZxx1, AZxx2, ...

```

**For Ansible collections, use conventional commits:**

```
fix(security): address weak-cryptography issues

- plugins/module_utils/aws_ssm.py:45 - Use secrets module for token generation
- plugins/modules/core.py:123 - Use secrets module for random IDs

Addresses 2 security issue(s) identified by SonarCloud.
Rule: python:S2245 - Pseudorandom number generators (PRNGs) must not be used for security-critical purposes

SonarCloud issue keys: AZxx1, AZxx2

```

**CRITICAL: Pause here.** Inform the engineer:

```
Branch `sonar/S1854-frontend-awx` is ready with N commits.

You can now:

  - Review the diff: git diff origin/<SONAR_DEFAULT_BRANCH>...HEAD
  - Run additional tests locally
  - Make manual adjustments and commit them to this branch

When you're satisfied, let me know and I'll create the PR.

```

**Wait for the engineer's explicit go-ahead before proceeding to PR creation.** Do NOT create the PR automatically.

### Step 7: Create PR/MR (Approval 2)

Before creating any PRs/MRs, present a summary:

```
Ready to create PR(s)/MR(s):

| # | Branch                          | Files | LOC changed | Target              |
|---|-------------------------------|-------|-------------|---------------------|
| 1 | sonar/S1854-frontend-awx        |   12  |    ~46      | <SONAR_DEFAULT_BRANCH> |
| 2 | sonar/S1854-frontend-awx-batch2 |    8  |    ~38      | <SONAR_DEFAULT_BRANCH> |

Total: 2 PR(s)/MR(s) targeting `<SONAR_DEFAULT_BRANCH>`.

Proceed?

```

**Wait for explicit approval.** Then for each PR/MR:

**Title — REQUIRED format:**

All titles **must** start with the prefix `SonarCloud Fix:` followed by a short description of the issue area being addressed. Use this pattern:

```
SonarCloud Fix: <brief description of fix> (<rule key>, <module>)

```

Examples:

- `SonarCloud Fix: Remove unused imports (S1128, frontend/awx)`
- `SonarCloud Fix: Remove dead stores (S1854, framework)`
- `SonarCloud Fix: Extract duplicate string literals (S1192, frontend/hub)`
- `SonarCloud Fix: Reduce cognitive complexity (S3776, frontend/eda)`
- `SonarCloud Fix: Remove commented-out code (S125, src)`

For batched PRs/MRs, append the batch number:

- `SonarCloud Fix: Remove dead stores (S1854, frontend/awx) [batch 1/2]`

**Creating the PR/MR:**

Use the platform detected in Phase A Step 0:

- **GitHub**: `gh pr create --title "<title>" --body "<body>" --base <SONAR_DEFAULT_BRANCH>`
- **GitLab**: `glab mr create --title "<title>" --description "<body>" --target-branch <SONAR_DEFAULT_BRANCH>`

**Body/description:** If the repo has a PR/MR template (`.github/pull_request_template.md` or `.gitlab/merge_request_templates/`), follow its structure. Otherwise, use this default format:

```markdown
## Summary

Remove N unused imports across M files in the <module> module.
Addresses SonarCloud rule `<language>:S1128` (<count> violations).

SonarCloud dashboard: https://sonarcloud.io/project/issues?id=<PROJECT_KEY>&rules=<rule>

## Type of Change

- [x] Enhancement

## Risk Analysis

- [x] **Low** — Narrowly scoped (removing unused imports has no runtime effect).

## Testing

Validation passed: `<SONAR_VALIDATE_COMMANDS>`.

```

Adjust **Type of Change** and **Risk Analysis** based on the fix category:

- Dead code, unused imports, commented-out code → **Low**
- Duplicate strings, unused params, type safety → **Low** to **Medium** (depending on scope)
- Cognitive complexity refactoring → **Medium**
- Security/reliability fixes → **Medium** to **High**

### Step 8: Add Changelog Fragment (Ansible Collections Only)

**For Ansible collections only**, use the `changelog-fragment` skill to document the changes.

Fragment type based on issue category:

- Security hotspots → `trivial` (or `security_fixes` if actual vulnerability)
- Reliability issues → `bugfixes`
- Maintainability issues → `trivial`

Example fragment content:

```yaml
bugfixes:

  - >-

    Fixed reliability issues identified by SonarCloud static analysis
    (https://github.com/ORG/REPO/pull/XXXX).

```

or

```yaml
trivial:

  - >-

    Improved code quality by addressing maintainability issues in module_name
    (https://github.com/ORG/REPO/pull/XXXX).

```

### Step 9: Post PR/MR Comment and Continue

1. Check `SONAR_PR_COMMENT`. If the variable is **not set**, **skip** this step entirely. If set to `none`, `skip`, `false`, or an empty string `""`, also **skip**.
Otherwise, post the comment on each newly created PR/MR using the detected platform:
   - **GitHub**: `gh pr comment <PR_NUMBER> --body "$SONAR_PR_COMMENT"`
   - **GitLab**: `glab mr note <MR_NUMBER> --message "$SONAR_PR_COMMENT"`
2. Offer to continue — return to group selection for the next batch

---

## Common Issue Patterns and Guidance

### Weak Cryptography (python:S2245, typescript:S2245)

**Pattern:** Using `random` module (Python) or `Math.random()` (JavaScript) for security-sensitive operations

**Fix:**

- If cryptographic randomness is needed: Use `secrets` module (Python) or `crypto.getRandomValues()` (JavaScript)
- If randomness is for hashing but not cryptographic purposes: Add `usedforsecurity=False` parameter (Python only - SonarCloud recognizes this)
- If not security-sensitive (e.g., generating unique IDs): Mark as SAFE with justification

**Example with usedforsecurity=False:**

```python
# For MD5 hash used for non-cryptographic purposes (e.g., checksums, cache keys)
hashlib.md5(data, usedforsecurity=False).hexdigest()

```

This parameter explicitly indicates to both Python and SonarCloud that the hash is not being used for security purposes.

### HTTP URLs (encrypt-data)

**Pattern:** Using HTTP instead of HTTPS

**Fix:**

- If HTTP is required (e.g., AWS metadata endpoint `http://169.254.169.254`): Mark as SAFE
- Otherwise: Change to HTTPS

### Cognitive Complexity (S3776)

**Pattern:** Functions with deeply nested logic

**Fix:**

- Extract nested logic into helper functions
- Simplify conditional statements
- Prioritize extracting logic that can be unit tested

**For refactoring changes (especially cognitive complexity fixes):**

When extracting complex logic into helper functions, write unit tests for the new functions:

- New helper functions are ideal candidates for unit testing
- They're typically smaller and more focused than the original code
- Unit tests document the expected behavior
- Tests prevent regression when the code is modified later
- Place tests in `tests/unit/plugins/module_utils/` or `tests/unit/plugins/modules/` (Ansible collections)

### Duplicate Strings (S1192)

**Pattern:** Magic strings repeated multiple times

**Fix:**

- Extract into named constants
- Use descriptive constant names
- Group related constants

### Generic Exceptions (python:S112)

**Pattern:** Raising or catching generic `Exception`

**Fix:**

- Use specific exception types
- Create custom exception classes for domain-specific errors

### Duplicate Branches (S1862)

**Pattern:** Identical code in different conditional branches

**Fix:**

- Refactor to eliminate duplication
- Verify whether different conditions should have different logic

---

## When Not to Fix

Don't fix issues that are:

- **False positives** - Legitimate patterns flagged incorrectly by static analysis
- **Required by external constraints** - Example: HTTP calls to AWS metadata endpoint `http://169.254.169.254`
- **Intentional technical debt** - Documented and accepted trade-offs

### Identifying False Positives

Use domain knowledge to distinguish between real issues and false positives:

- **AWS metadata endpoint** - HTTP to `169.254.169.254` is required, not a security issue
- **UUID generation** - Using `random` for UUIDs is not cryptographically sensitive
- **Test fixtures** - Deliberately simplified code in tests may trigger complexity warnings
- **Framework requirements** - Some patterns are dictated by the framework (unused parameters in callback signatures)

### Handling False Positives

For false positives identified during Phase A or B:

1. **Document the rationale** - Add a code comment explaining why this is safe
2. **Mark in SonarCloud UI** - Use the web interface to mark as "Won't Fix" or "False Positive"
3. **Skip the fix** - Exclude from the approved fixes list

Example code comment:

```python
# SonarCloud S2245: Random is used for non-cryptographic UUID generation
import random
uuid = random.randint(100000, 999999)

```

---

## False Positives Section

Static analysis tools like SonarCloud may flag legitimate code patterns as issues. Understanding how to identify and handle these is critical for efficient remediation.

### Common False Positive Patterns

| Pattern | Why Flagged | When It's Actually Safe |
|---------|-------------|------------------------|
| HTTP URLs | encrypt-data category flags all HTTP | AWS metadata (`169.254.169.254`), local dev servers, internal non-sensitive APIs |
| `random` module | weak-cryptography flags all uses | UUID generation, test data, non-cryptographic hashing with `usedforsecurity=False` |
| Unused parameters | Dead code detection | Framework callbacks, interface implementations, future extensibility points |
| Cognitive complexity | Function is too complex | Intentional state machines, parser logic, configuration builders |
| Duplicate strings | String literals repeated | Short literals (":", "/"), protocol constants, format strings |

### False Positive Decision Tree

When reviewing an issue:

1. **Read the surrounding context** - Is this code part of a larger pattern?
2. **Check external requirements** - Does a framework, API, or spec mandate this pattern?
3. **Assess the risk** - If this were actually a bug/vulnerability, what would be the impact?
4. **Look for documentation** - Is there a comment explaining why this pattern is necessary?

If the answer to any of these suggests "false positive," document and skip the fix.

### Documenting False Positives

For issues you determine are false positives:

**In code comments:**

```python
# SonarCloud false positive - HTTP to AWS metadata endpoint is required
response = requests.get("http://169.254.169.254/latest/meta-data/")

```

**In SonarCloud UI:**

1. Navigate to the issue in SonarCloud
2. Click "Resolve" → "Won't Fix" or "False Positive"
3. Add justification: "AWS metadata endpoint requires HTTP"

**In PR descriptions:**

When creating fix PRs, note any issues that were intentionally skipped:

```
## Issues Skipped (False Positives)

- AZxx3: HTTP call to AWS metadata endpoint (required by AWS SDK)
- AZxx7: random.randint for UUID generation (not cryptographic use)

```

---

## Rate Limiting and API Notes

### SonarCloud API Rate Limits

- **Public projects** - No authentication required, subject to public rate limits
- **Private projects** - Require `SONARCLOUD_TOKEN`, higher rate limits
- **Unauthenticated limit** - ~20-40 requests per minute per IP
- **Authenticated limit** - Higher, but not publicly documented

### Pagination

The fetch script handles pagination automatically:

- Default page size: 500 issues per request
- Maximum results: 10,000 issues per query type
- If a project has >10,000 issues, filter by severity or type

### sonar-project.properties

This skill reads SonarCloud data but doesn't modify `sonar-project.properties`. For project configuration:

- Exclusions: Add to `sonar.exclusions` (files to skip)
- Coverage paths: Set `sonar.python.coverage.reportPaths`
- Custom quality gates: Configure in SonarCloud UI

### Custom Quality Gates

If your project has custom quality gates:

- The skill shows all unresolved issues regardless of gate status
- Quality gate failures are visible in the SonarCloud UI
- PR-specific mode shows issues that would fail the gate for that PR

---

## Issue Resolution Guidance

### How Issues Auto-Resolve

SonarCloud issues resolve automatically when:

1. **Fix is merged** - The code change reaches the default branch (e.g., `main`)
2. **SonarCloud re-analyzes** - Triggered automatically after merge
3. **Issue no longer detected** - The rule no longer flags that location

**Timeline:** Issues typically resolve within 5-10 minutes after merge.

### Handling False Positives in SonarCloud UI

For false positives that can't be fixed in code:

#### Step 1: Navigate to the issue

1. Go to SonarCloud project: `https://sonarcloud.io/project/issues?id=<PROJECT_KEY>`
2. Filter to find the specific issue (by file, rule, or issue key)

#### Step 2: Mark as Won't Fix or False Positive

1. Click on the issue
2. Click "Resolve" button
3. Select resolution type:
   - **Won't Fix** - Valid finding but intentionally not addressing
   - **False Positive** - Not actually an issue

#### Step 3: Add justification

Provide a clear explanation:

- "AWS metadata endpoint requires HTTP (169.254.169.254)"
- "Random module used for non-cryptographic UUID generation"
- "Framework callback signature requires unused parameter"

**Impact:** Resolved issues are removed from:

- Issue count metrics
- Quality gate calculations
- PR decoration (for PR-specific issues)

### Tracking Resolution Progress

After merging fix PRs:

1. **Wait 5-10 minutes** for SonarCloud to re-analyze
2. **Refresh the project page** in SonarCloud UI
3. **Verify issue count decreased** in the affected category
4. **Check quality gate status** if it was failing before

If issues don't resolve after 15 minutes:

- Check the SonarCloud analysis log for errors
- Verify the fix actually changed the flagged code
- Confirm the scanner ran on the correct branch

---

## Example Usage Scenarios

### Example 1: PR Review

**User:** "Check sonar for this PR"

**Skill workflow:**

1. Detects current branch: `feature/add-caching`
2. Uses `get-pr-number` skill to find PR #1234
3. Runs fetch script with `SONAR_PR_NUMBER=1234`
4. Finds 3 new CODE_SMELL issues
5. Groups by rule and module
6. Presents table with 3 issues
7. Reports: "3 new maintainability issues introduced. All are MINOR severity. Group #1: Duplicate strings in plugins/cache_utils.py"

**Engineer response:** "Let me review before merging"

### Example 2: Technical Debt Audit

**User:** "Show me all security hotspots"

**Skill workflow:**

1. Detects project key from `get-upstream-info`
2. Runs fetch script in project-wide mode
3. Fetches all TO_REVIEW security hotspots
4. Groups by `securityCategory`:
   - 2 weak-cryptography
   - 5 encrypt-data
   - 1 dos
5. Analyzes each category
6. Reads affected code
7. Identifies 3 false positives (AWS metadata HTTP calls)
8. Recommends:
   - "Fix 2 weak-cryptography issues (use `secrets` module)"
   - "Mark 3 HTTP calls as false positives (AWS metadata)"
   - "Review 1 DOS issue (regex backtracking)"

**Engineer response:** "Fix the weak-cryptography group"

### Example 3: Comprehensive Analysis

**User:** "What's our SonarCloud status?"

**Skill workflow:**

1. Fetches all issue types (security, reliability, maintainability)
2. Runs fetch script without PR filter
3. Categorizes results:
   - 8 security hotspots
   - 18 bugs
   - 156 code smells
4. Presents summary table
5. Sorts groups by priority (security first, then critical bugs)
6. Recommends: "Focus on the 2 CRITICAL bugs first (Group #3), then review the 8 security hotspots (Groups #1-2)"

**Engineer response:** "Show me the CRITICAL bugs"

### Example 4: Large Codebase with Pagination

**User:** "Analyze SonarCloud issues for ansible-collections/amazon.aws"

**Skill workflow:**

1. Uses `get-upstream-info` to determine project key: `ansible-collections_amazon.aws`
2. Runs fetch script, which paginates automatically
3. Fetch script retrieves:
   - Page 1: issues 1-500
   - Page 2: issues 501-1000
   - ...
   - Page 6: issues 2501-2626
   - Total: 2,626 issues
4. Categorizes all 2,626 issues
5. Groups by rule and module
6. Presents summary table with 47 groups
7. Recommends starting with high-priority groups:
   - Group #1: 2 CRITICAL bugs (S1862, plugins/modules/)
   - Group #2: 8 security hotspots (weak-cryptography)
   - Group #3: 23 MAJOR bugs (S3776, plugins/modules/ec2_instance.py)

**Engineer response:** "Fix Group #1 and Group #2"

---

## Portability

This skill is designed for adoption across repositories:

1. **No hardcoded values** — all project-specific config via environment variables or interactive prompts
2. **SonarCloud and SonarQube** — works with SonarCloud (default) and self-hosted SonarQube instances via `SONAR_BASE_URL`.
Organization parameter is automatically omitted for self-hosted instances where it is not required.
3. **Configurable base branch** — `SONAR_DEFAULT_BRANCH` set via env var or provided interactively
4. **Automatic module detection** — detects monorepo workspaces from `package.json`, `pnpm-workspace.yaml`, `nx.json`, or `lerna.json`.
For non-monorepo projects, groups issues by top-level directory. For Ansible collections, uses Ansible-specific module grouping. No repo-specific configuration required.
5. **Fetch script** — `scripts/sonarcloud-fetch.py` uses only Python stdlib (no external dependencies). Handles pagination, authentication, and categorization deterministically.
6. **Validation commands** — `SONAR_VALIDATE_COMMANDS` set via env var or provided interactively
7. **GitHub and GitLab** — auto-detects hosting platform from git remote URL; uses `gh` or `glab` accordingly
8. **PR/MR template** — automatically adapts to the target repo's `.github/pull_request_template.md` or `.gitlab/merge_request_templates/`
9. **Ansible collections integration** — auto-detects Ansible collections repos and integrates with `get-upstream-info`, `get-pr-number`, `changelog-fragment`, and other collection-specific skills

### Quick Start for Other Teams

```bash
export SONAR_ORGANIZATION=your-org
export SONAR_PROJECT_KEY=your-project-key
export SONARCLOUD_TOKEN=your-token        # only for private projects
export SONAR_BASE_URL=https://sonarqube.corp.example.com/api  # only for self-hosted SonarQube
export SONAR_DEFAULT_BRANCH=main                          # if not devel
export SONAR_VALIDATE_COMMANDS="make lint && make test"    # your validation pipeline
export SONAR_PR_COMMENT="/run-e2e"                         # your PR comment, or "none" to disable

```

Then use `/sonarcloud-analyze` and `/sonarcloud-fix`.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Prompted for organization/project key | Not set as env vars | Set env vars beforehand, or provide values when prompted interactively |
| Empty results from API | Wrong project key or org | Verify the project exists on your Sonar instance (e.g. `https://sonarcloud.io/project/overview?id=<PROJECT_KEY>` for SonarCloud, or `<SONAR_BASE_URL>/dashboard?id=<PROJECT_KEY>` for self-hosted) |
| 401 from API | Private project without token | Set `SONARCLOUD_TOKEN` as an environment variable (`export SONARCLOUD_TOKEN=<your-token>`), then restart Claude. Generate a token from your Sonar instance's account security page |
| Connection error to self-hosted instance | Wrong URL or TLS issue | Verify `SONAR_BASE_URL` is correct (include `/api` suffix). For self-signed certificates, set `SONAR_INSECURE=1` |
| Prompted for Phase B config | Not set as env vars | Set env vars beforehand, or provide values when prompted. You can also provide Phase B values during Phase A to avoid a second prompt. |
| Validation command fails after fix | Fix introduced a build/lint/type error | Review the error, adjust the fix, re-run `SONAR_VALIDATE_COMMANDS` |
| Tests fail after fix | Fix broke a test | Check if the test relied on removed code; update the test and re-run validation |
| Pagination missed issues | More than 500 issues per query | The skill paginates automatically; if issues are still missing, try filtering by severity or type |
