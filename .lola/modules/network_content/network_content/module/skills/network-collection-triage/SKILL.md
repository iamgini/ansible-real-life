---
name: network-collection-triage
description: >-
  Triage bug reports, CI failures, and GitHub issues across Ansible network
  collections (cisco.ios, cisco.iosxr, cisco.nxos, arista.eos,
  ansible.netcommon, ansible.utils, etc.). Two modes: scan mode for bulk weekly
  triage across all repos, and direct mode for deep triage of a single
  issue. Network-specific: uses cross-collection cascade detection for
  shared dependencies (netcommon, utils) and known network CI failure
  patterns. Outputs structured JSON and markdown. Use when asked to triage
  network issues, scan network issues, weekly triage, triage CI failure,
  or triage collection issue. Do not use for non-network collections or
  general Ansible questions.
triggers:
  - triage network issues
  - triage network
  - scan network issues
  - weekly triage
  - triage CI failure
  - triage collection issue
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
argument-hint: "[<github-issue-url>] [--scan]"
---

# Skill: network-collection-triage

## Purpose

Triage bug reports, CI failures, and GitHub issues across Ansible network
collections. Categorize items, check known network CI failure patterns,
assess severity with cross-collection cascade detection for shared
dependencies (`ansible.netcommon`, `ansible.utils`, `ansible.pylibssh`), and produce structured
JSON and markdown output suitable for downstream dashboards or reports.

### Why network-specific

This skill exists in `network_content` rather than `ansible-collection-sdlc`
because the triage logic depends on network-specific domain knowledge:

- **Cross-collection cascade detection** tied to the `ansible.netcommon` and
  `ansible.utils` and `ansible.pylibssh` dependency chain shared by all network collections
- **Known CI failure patterns** specific to network collection CI (Galaxy
  version lag for netcommon, persistent connection timeout leaks, etc.)
- **Scoped repo list** — queries a fixed set of network collection repositories
  under the `ansible-collections` GitHub org

A generic collection triage skill would not have this domain knowledge.

## When to Invoke

TRIGGER when:

- A user asks to triage network collection issues or CI failures
- A user asks to scan repos for unassigned bugs/PRs (scan mode)
- A user pastes a GitHub issue URL or CI failure link for a network collection
- A user asks for a weekly triage report
- A user says "triage network", "scan network issues", or "weekly triage"

DO NOT TRIGGER when:

- The issue is in a non-network collection (use generic triage instead)
- The user is asking general Ansible questions unrelated to triage
- The user wants to fix a bug (use a bugfix workflow instead)

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- Push access not required — this skill only reads GitHub data

---

## Mode Detection

This skill has TWO modes. Detect the mode from the user's trigger and
act accordingly. **Do NOT ask clarifying questions in scan mode.**

### Scan mode (no specific issue provided)

Any trigger that does NOT include a specific GitHub URL or issue number
runs scan mode. This includes: "triage network issues", "triage network",
"scan network issues", "weekly triage", "generate triage report".

**When scan mode is triggered: immediately run the full pipeline end-to-end
without asking the user for any input.** Do NOT stop to ask "What would you
like me to triage?" — the whole point of scan mode is zero-input bulk triage.

### Direct mode (specific issue provided)

A user pastes a GitHub issue URL, CI failure link, error log, or describes
a specific bug symptom. In this mode (and ONLY this mode), ask the user
for additional context if needed (collection, platform, Ansible version).

---

## Collections in Scope

| Collection | Platform | Connection |
|---|---|---|
| `ansible.netcommon` | Shared (connection plugins, base classes) | N/A |
| `ansible.utils` | Shared (utility filters, cli_parse) | N/A |
| `ansible.pylibssh` | SSH Client for Ansible Network Collections | N/A |
| `cisco.ios` | Cisco IOS / IOS-XE | network_cli |
| `cisco.iosxr` | Cisco IOS-XR | network_cli, netconf |
| `cisco.nxos` | Cisco NX-OS | network_cli, httpapi |
| `arista.eos` | Arista EOS | network_cli, httpapi |
| `cisco.asa` | Cisco ASA | network_cli |
| `vyos.vyos` | VyOS | network_cli |
| `ansible.scm` | Manage Git repositories with Ansible | git |

**GitHub org**: `ansible-collections`

---

## Scan Mode Pipeline

**Execute all steps automatically without stopping for user input.**

### Step 1 — Fetch open issues and PRs across all repos

Use `gh` to query each repo in scope. Fetch open issues
and open pull requests from the last 14 days (configurable).

**For bugs (issues):**

```bash
gh issue list --repo ansible-collections/cisco.ios --state open \
  --search "updated:>=YYYY-MM-DD" --json number,title,url,labels,createdAt,author,assignees --limit 50 --search "-label:stale"
```

**For pull requests:**

```bash
gh pr list --repo ansible-collections/cisco.ios --state open \
  --search "updated:>=YYYY-MM-DD draft:false" \
  --json number,title,url,labels,createdAt,author,isDraft,reviewDecision \
  --limit 50 --search "-label:stale"
```

Run these for every repo in the Collections in Scope table:

```
ansible-collections/ansible.netcommon
ansible/pylibssh
ansible-collections/ansible.utils
ansible-collections/cisco.ios
ansible-collections/cisco.iosxr
ansible-collections/cisco.nxos
ansible-collections/arista.eos
ansible-collections/cisco.asa
ansible-collections/vyos.vyos
ansible-collections/ansible.scm
```

### Filter and record results based on the timeline (default: T-14 days)

- **Ignore** PRs where isDraft is True
- **Ignore** closed issues
- **Ignore** closed/merged PRs
- **Ignore** any issue or PR that is labelled as 'stale'
- Group by repository and type (issue vs PR)
- **Store ALL items** for the complete listing section (no filtering at this stage)

Combine all results into a single list for processing.

### Step 2 — Check CI status for each repo

For each repo, check the latest CI workflow run status:

```bash
gh run list --repo ansible-collections/cisco.ios --workflow tests.yml \
  --json status,conclusion,headBranch,createdAt,url --limit 5 --branch main
```

Note any repos where the main branch CI is currently failing — this feeds
into cross-collection signal detection step.

Use the five most recent runs from the query (`--limit 5`). Count a run as passing only when
`conclusion` is `success`; any other conclusion or a missing run slot counts
as non-passing for health (`green` 5/5, `yellow` 3–4/5, `red` 0–2/5).

### Step 3 — Categorize every item

Examine each issue/PR title, labels, and body to assign a category:

| Category | Base Severity | Rationale |
|---|---|---|
| Bug report | **Major** | User-facing issue, needs investigation |
| Downstream fix | **Major** | Upstream breakage actively affecting this collection |
| New feature PR | **Minor** | No urgency unless tied to release deadline |
| Test infrastructure | **Minor** | Strategic work enabling CI reliability |
| Chore / CI / Modernization | **Trivial** | No functional change, auto-merge candidate if CI green |

**Heuristics for categorization:**

- Label `bug` or title contains "fix", "broken", "error" → Bug report
- Title references another collection's PR/issue or "bump dependency" → Downstream fix
- Label `enhancement` or `feature` or title contains "add support" → New feature PR
- Title mentions "test", "molecule", "mock", "integration target" → Test infrastructure
- Title mentions "dependabot", "bump", "ci:", "chore:", "linting" → Chore

**Key distinction:** A Molecule/CISSHGO PR building mock-device test
scenarios is test INFRASTRUCTURE (Minor). A Dependabot bump or
pyproject.toml cleanup is a Chore (Trivial).

### Step 4 — Check for known CI failure patterns

Check whether any failing CI or reported issue matches a known pattern.
If a known pattern matches, note it in the triage output and use the
documented resolution rather than investigating from scratch.

**Pattern 1 — Galaxy version lag:**
Unit CI (`unit-galaxy` job) fails with an error already fixed in
`ansible.netcommon` or `ansible.utils` main but not yet released to Galaxy.
The `unit-galaxy` job installs the last Galaxy release, so fixes in main
don't reach it until a new release is cut.
*Resolution*: Cut a netcommon/utils release, or temporarily pin to git source.

**Pattern 2 — devel/milestone only failure:**
CI fails only on `devel` or `milestone` ansible-core versions due to an
API change or deprecation not yet adapted. Check ansible-core changelog.
*Resolution*: May be `needs_revision`; adapt to new API.

**Pattern 3 — Cross-PR dependency:**
PR passes CI independently but fails when merged due to an unmerged
dependency (e.g. a netcommon fix that this PR depends on).
*Resolution*: Merge dependencies in correct order.

**Pattern 4 — Persistent connection state leak:**
A test task sets connection options (e.g. `ansible_command_timeout`) via
`include_tasks vars:`. The persistent connection daemon caches the value
and does not reset it when the task scope ends, causing subsequent tasks
to fail with stale values.
*Resolution*: Add `ansible.builtin.meta: reset_connection` after the test.

### Step 5 — Apply severity escalators

Escalators can only raise severity, never lower it.

| Condition | Action |
|---|---|
| Bug in `ansible.netcommon`, `ansible.utils` or `ansible.pylibssh` | **Critical** — Potential cascade risk, assign based on the severity of the bug |
| Data loss or security issue | **Critical** |
| Multiple collections failing with same root cause | **Critical** — cascade event |

### Step 6 — Detect cross-collection signals

If a bug or failing CI is in `ansible.netcommon`, `ansible.utils` or `ansible.pylibssh`:

- List all downstream collections importing the affected code
- Check if their CI is currently failing (from Step 2 data)
- If multiple collections failing → cascade event
- Priority action: fix in netcommon/utils → cut release → re-trigger downstream CI

Dependency chain:

```
ansible.pylibssh ──→ ansible.netcommon
ansible.netcommon ──→ cisco.ios, cisco.iosxr, cisco.nxos,
                      arista.eos, cisco.asa, vyos.vyos
ansible.utils ────→ (same downstream consumers), ansible.scm
```

### Step 7 — Generate structured output

Save two files:

1. **`triage-report-YYYY-MM-DD.json`** — structured triage data (see JSON Output Schema)
2. **`triage-report-YYYY-MM-DD.md`** — human-readable markdown summary

The JSON file is the primary output — it can be loaded by a separate
dashboard frontend or consumed by other tools. The markdown file is for
quick human review.

**Validate the JSON before finishing:**

```bash
python network-collection-triage/scripts/validate_triage_report.py triage-report-YYYY-MM-DD.json
```

Fix any schema or consistency errors reported by the validator.

### Step 7.1 — Present results

Share both file links and a brief summary: total items, breakdown by
severity, any critical items or cross-collection signals that need
immediate attention.

### Step 7.2 — Generate the markdown

Create a detailed markdown report of the triage results, ensuring all the issues and PRs are listed in the report. It should be written in the user's current working directory.

### Step 7.3 — Generate the JSON

Generate a JSON file of the triage results, ensuring all the issues and PRs are listed in the JSON file.
It should be written in the user's current working directory.
**Do not** use any summary data from the markdown, utilize the data generated from relevant commands and generate the json.
The format of the JSON file should be as mentioned below:

## Output — JSON schema

The canonical JSON Schema lives at
**`schema/triage-report.schema.json`** (relative to this skill directory).
The agent **must** emit valid JSON (UTF-8) that passes
`scripts/validate_triage_report.py`. Top-level shape:

| Field | Type | Description |
|--------|------|-------------|
| `schemaVersion` | string | e.g. `"1.1"` |
| `meta` | object | `generatedAt` (ISO 8601), `timelineStart`, `timelineEnd`, `repos` (short names `owner/repo`) |
| `statistics` | object | Required: `totalIssues`, `totalPrs`, `criticalCount`. Optional: `staleCount`, `majorCount`, `minorCount`, `trivialCount`, `issuesOpen`, `prsOpen`, `issuesWithAssignees`, `prsApproved`, `averagePrAgeDays`, etc. |
| `priorityMatrix` | object | Keys `critical`/`high`/`medium`/`low`, each with `immediate`, `thisWeek`, `thisMonth`, `backlog` counts (numbers). |
| `criticalItems` | array | Objects with at least `url`, `title`, `repo`, `severity` (`critical`/`major`/`minor`/`trivial`), `impact`, `recommendedOwner`, `nextAction`, `component`. |
| `highPriorityItems` | array | Same style as critical, subset for highlighting. |
| `prReviewHighlights` | array | PR-focused objects (`url`, `title`, `reviewStatus`, `recommendedAction`, …). |
| `recommendedActions` | array of string | Short imperative lines (assign, escalate, merge-ready, …). |
| `repositories` | array | One object per repo scanned (see below). |
| `executiveSummaryMarkdown` | string (optional) | Bullet-style markdown for chat if useful. |

**`repositories[]` entry**

| Field | Type | Description |
|--------|------|-------------|
| `name` | string | `owner/repo` |
| `url` | string | GitHub repo URL |
| `issues` | array | All issues in window (see **Issue row**). |
| `pullRequests` | array | All PRs in window (see **Pull request row**). |
| `ci-status` | object \| null | Latest main-branch CI from Step 2 (`gh run list --limit 5`), or `null` when CI could not be fetched. |

**`ci-status` object** (per repo; set to `null` when `gh run list` failed for that repo)

| Field | Type | Description |
|--------|------|-------------|
| `workflow` | string | Workflow file queried (e.g. `tests.yml`). |
| `branch` | string | Branch filter used (e.g. `main`). |
| `checkedAt` | string | ISO 8601 when CI was fetched. |
| `passCount` | number | Runs with `conclusion: success` among the five slots (0–5). |
| `totalCount` | number | Always `5` (fewer returned runs count as non-passing). |
| `health` | string | `green` (5/5) \| `yellow` (3–4/5) \| `red` (0–2/5). |
| `runs` | array | Up to five run objects (newest first), same order as `gh run list`. |

**`ci-status.runs[]` entry**

| Field | Type | Description |
|--------|------|-------------|
| `conclusion` | string \| null | `success`, `failure`, `cancelled`, `skipped`, etc. |
| `status` | string | e.g. `completed`, `in_progress`. |
| `createdAt` | string | ISO 8601 from `gh`. |
| `headBranch` | string | Branch for the run. |
| `url` | string (optional) | GitHub Actions run URL. |

**Issue row** (`repositories[].issues[]`)

| Field | Type | Notes |
|--------|------|------|
| `number` | number | Issue number. |
| `title` | string | Plain text title. |
| `url` | string | Canonical GitHub issue URL. |
| `state` | string | `open` \| `closed`. |
| `severity` | string | Triage severity: `critical` \| `major` \| `minor` \| `trivial`. |
| `summary` | string | Detailed summary in ~five lines; rationale for severity. |
| `labels` | array | Strings or `{ "name": "..." }`. |
| `assignees` | array | Prefer `[{ "login": "octocat" }, ...]` or string[] for broad consumer compatibility. |
| `author` | string (optional) | Issue author login. |
| `createdAt` / `updatedAt` | string (optional) | ISO dates from `gh --json`. |
| `component` | string | Best SME/component guess. |
| `recommendedOwner` | string | SME or team contact label. |
| `nextAction` | string | Recommended action. Under five lines. |

**Pull request row** (`repositories[].pullRequests[]`)

Same fields as **Issue row**, plus:

| Field | Type | Notes |
|--------|------|------|
| `state` | string | `open` \| `closed` \| `merged`. |
| `reviewStatus` | string | Required. e.g. `APPROVED`, `CHANGES_REQUESTED`, `REVIEW_REQUIRED`. |

`priorityMatrix` buckets (`critical`/`high`/`medium`/`low`) are separate from per-item
triage severity (`critical`/`major`/`minor`/`trivial` above).

**Completeness**: `sum(repositories[].issues.length)` must equal the open issues you analyzed for the listing (per workflow rules); same for PRs. Nothing omitted for brevity.

---

---

## Direct Mode Steps

### Step 1 — Identify collection and component

Determine which collection, which module/plugin, and what connection type.
If a GitHub URL is provided, fetch the issue or PR details:

```bash
gh issue view <number> --repo ansible-collections/<collection> --json title,body,labels,comments
```

or:

```bash
gh pr view <number> --repo ansible-collections/<collection> --json title,body,labels,files,statusCheckRollup
```

### Step 2 — Check for known CI failure patterns

Check whether the failure matches a known pattern (see Step 4 in scan
mode). If a known pattern matches, document it and skip to resolution.

### Step 3 — Cross-collection dependency check

If the bug is in `ansible.netcommon`, `ansible.utils` or `ansible.pylibssh`, check the
dependency chain (same as scan mode Step 6).

### Step 4 — Apply severity escalators

Same table as scan mode Step 5.

### Step 5 — Produce triage report

Use the Output Format below.

---

## Output Format

Every triage produces this structured report:

```markdown
## Network Collection Triage Report

**Date**: [date]
**Mode**: [Scan / Direct]

### Issue
[GitHub issue URL or CI failure link]

### Collection: [e.g. cisco.ios]
### Component: [module name, plugin, or CI infrastructure]
### Ansible Version: [e.g. stable-2.19 / devel]
### Connection Type: [network_cli / netconf / httpapi]

### Category
[Downstream fix / New feature / Bug report / Chore-CI / Test improvement]

### Severity: [Critical / Major / Minor / Trivial]
[Justification, including any escalators applied]

### Known Pattern Match
[Matched pattern name, OR "No known pattern — new issue"]

### Cross-Collection Impact
[None / List of affected collections / Cascade event detected]

### Root Cause
[Technical explanation if identified]

### Recommended Resolution
[Specific action: cut release, fix in PR #N, add meta: reset_connection, etc.]
```

---

## Error Handling

- **`gh` not authenticated**: Run `gh auth status`. If not logged in, inform
  user to run `gh auth login` and stop.
- **Rate limiting**: GitHub API has rate limits. If hitting limits during scan
  mode, space out requests or reduce the repo list to critical collections first
  (netcommon, utils, pylibssh, ios, iosxr, nxos, eos, scm).
- **Empty results**: If no open bugs or PRs are found for a repo, skip it
  silently. If ALL repos return empty, report "No open items found across
  network collections" and confirm the time window.
- **Repo not found**: If `gh` returns a 404 for a repo, skip it and note
  the skip in the output. The repo may have been renamed or archived.
