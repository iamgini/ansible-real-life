---
name: configure-sonarcloud-collection
description: >-
  Adds SonarCloud (SonarQube Cloud) static analysis to an Ansible collection repo:
  sonar-project.properties, GitHub Actions scanner workflow, XML coverage for Sonar,
  and contributor-facing docs; includes fork/secret and assistant-safe patterns (see Security section).
  Use when onboarding SonarCloud, wiring CI secrets, producing coverage.xml, or mirroring
  ansible-collections setups like amazon.aws.
user-invocable: true
---

# Configure SonarCloud for an Ansible Collection

Guide repository changes so SonarCloud can analyze Python/plugins/tests and display coverage.
Complements `sonarcloud-remediation` (analyze and fix findings)—run that **after** the project exists on SonarCloud and CI uploads analysis.

## Purpose

Produce consistent, reviewable setup across collections:

- Root `sonar-project.properties` aligned with org project key and layout
- A workflow that runs the SonarScanner with the org token
- `coverage.xml` at the repository root for `sonar.python.coverage.reportPaths`
- Documentation (README section or dedicated doc) for Sonar/coverage expectations

## Canonical templates (ansible-collections)

Org policy: **keep GitHub Actions YAML identical across repos** (same pins, same secret name, same job layout) unless GitHub / Sonar maintainers roll out a coordinated change.

1. Open **`module/skills/sonarcloud-workflow-templates/README.md`** in this module (path may differ if the
   module is installed via Lola from another clone).
2. Copy **`sonar-project.properties.template`** to the collection repo root as **`sonar-project.properties`**.
   Replace every **`__PLACEHOLDER__`** using the legend in that file plus **`galaxy.yml`** and the SonarCloud
   project UI. **`sonar.projectKey`** must match the SonarCloud UI exactly.
3. Copy **one** workflow template to **`.github/workflows/sonarcloud.yml`** without structural edits. See the
   same **`README.md`** for **`workflow_run`** vs **`workflow_call`**.
   For **`workflow_call`**, also add the **`sonarcloud`** caller job from **`all_green-caller.sonarcloud-job.yml.template`**
   into **`all_green_check.yaml`** (or your aggregator file) after **`all_green`** and **`coverage`** succeed.
   - **`sonarcloud.workflow_run.yml.template`**: **amazon.aws** pattern — aggregator **`name: all_green`**,
     **`workflow_run`**, job **`finalize`**, **`dawidd6/action-download-artifact`**, **`pattern: coverage*`**,
     **`permissions.actions: read`**.
   - **`sonarcloud.workflow_call.yml.template`**: reusable Sonar — body matches merged **kubernetes.core**
     **`sonarcloud.yml`** (e.g. [PR #1124](https://github.com/ansible-collections/kubernetes.core/pull/1124)).
     Caller on **`pull_request`** / **`push`**; one upload with **`name: coverage`**; template uses
     **`actions/download-artifact@v4`** for that name.
   - **`all_green-caller.sonarcloud-job.yml.template`**: paste the **`sonarcloud`** job into
     **`all_green_check.yaml`** with **`uses: ./.github/workflows/sonarcloud.yml`** and explicit **`secrets:`**
     for **`ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT`** (not **`secrets: inherit`** if GitHub reports
     **"Only pass required secrets to this workflow"**).

Do **not** rename **`ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT`** for ansible-collections repos so CI works without per-repo secret lookup changes.

## When to Invoke

TRIGGER when the user asks to:

- Add, enable, or configure SonarCloud / SonarQube Cloud for a collection
- Create `sonar-project.properties` or Sonar CI workflow from scratch
- Wire pytest/tox output to Sonar coverage
- Document Sonar or coverage thresholds for contributors

DO NOT TRIGGER when:

- The user wants to **view** or **fix** Sonar issues on an already-configured project (use `sonarcloud-remediation`)

## Prerequisites (human / org)

Before CI can succeed end-to-end:

1. **SonarCloud project** exists and is linked to the GitHub repo (Analyze new project → pick repo). Project key on SonarCloud **must match** `sonar.projectKey` in `sonar-project.properties`.
2. **Org-level secret** available to workflows: for `ansible-collections`, GitHub Actions use
   `SONAR_TOKEN: ${{ secrets.ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT }}`
3. **Coordinate access** with collection/Sonar org admins if the project is missing or mis-keyed (internal Ansible channels/sponsor as applicable).

Use `get-upstream-info` to derive `UPSTREAM_ORG`, repo name, and the SonarCloud-style project key
(typically `ORG_COLLECTIONNAME` with dots in the collection name replaced—e.g.
`ansible-collections/amazon.aws` → `ansible-collections_amazon.aws`).

## Fork and secret limitation

GitHub **does not** expose secrets to workflows triggered by pull requests **from forks**. Plan accordingly:

- Sonar jobs that need `SONAR_TOKEN` should run on **push** to the default branch and on PRs **from the same repository** (internal contributors), not from forks.
- Alternatively, accept that fork PRs skip Sonar until merge.

Document this in the workflow comments or contributor docs.

## Security (assistants, CI, and secrets)

GitHub **does not expose secrets** to workflows triggered from **forked** pull requests the same way
as for PRs from branches on the same repository. Treat fork PR runs as **less trusted** when designing
jobs that need `SONAR_TOKEN` or other org secrets. See GitHub’s documentation on
[using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
and on [forks and permissions](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/approving-workflow-runs-from-public-forks).

Workflow files changed in a PR often run with **default-branch** definitions until merged; review
workflow edits carefully because the next **trusted** run on the default branch can execute new
steps with access to secrets.

When **fork PRs** must still get SonarCloud results **with coverage**, a common pattern is: (1) a
workflow triggered by the PR runs tests and **uploads coverage (and PR metadata) as artifacts**
without using the Sonar token in that job; (2) a **separate** workflow runs in a trusted context,
**downloads** those artifacts, and runs the official **SonarSource** scanner with secrets. That
follow-up job often uses GitHub’s
[`workflow_run` event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_run).

Your **GitHub and SonarCloud administrators** may document a concrete layout (job names, permissions,
variable names) in **internal** repos or handbooks; follow that guidance rather than inventing
org-specific wiring from this skill alone.

When this skill is applied by an assistant (Claude, Cursor, or similar):

- **Never** commit, generate, or paste real **Sonar tokens** or other credentials into repo files, PR
  bodies, commits, or transcripts. Workflows must reference existing GitHub **Actions secrets** only
  (e.g. `${{ secrets.… }}`). If your org uses a **Variable** to hold the secret *name*, use the
  indirection pattern your admins document (for example `secrets[format('{0}', vars.SOME_NAME)]`)
  **without** embedding secret values.
- **Human-review** every `.github/workflows/` change before merge; mistaken or malicious steps can
  exfiltrate secrets the next time a **trusted** job runs on the default branch.
- Prefer the **artifact + follow-up workflow** pattern when policy requires **fork PR** scanning **with**
  coverage while keeping org tokens out of untrusted fork contexts.
- **Do not** add `echo`, upload, or debug steps that print secret values; keep Sonar steps to official
  **SonarSource** actions and SonarCloud endpoints your org already approves.
- **Provisioning** (SonarCloud project, keys, which secret or variable names to use) stays with **org
  admins** and your internal support channels; assistants must not invent production keys or create org
  tokens on their own.

## Workflow for the agent

### 1. Inventory the repo

- Read `galaxy.yml` for collection name (namespace.name).
- Locate existing test workflows: `.github/workflows/tests.yml`, `units.yml`, `ansible-test`-based jobs, or `tox`.
- Confirm whether unit tests already emit XML coverage; many collections only emit HTML via tox/pytest.

### 2. Add `sonar-project.properties` at the repository root

Tune paths to match the tree (`plugins/`, `tests/unit`, `tests/integration`). Minimum pattern for collections (adjust names):

```properties
# SonarCloud project configuration for <collection.name>
# Complete documentation: https://docs.sonarqube.org/latest/analysis/analysis-parameters/

sonar.projectKey=<ORG>_<collection.name with dots as needed>
sonar.organization=<sonarcloud org slug, e.g. ansible-collections>
sonar.sources=.
sonar.projectName=<collection.name>

sonar.python.coverage.reportPaths=coverage.xml

sonar.tests=tests/unit,tests/integration
sonar.python.version=<match CI primary Python, e.g. 3.13>
sonar.newCode.referenceBranch=main

sonar.exclusions=tests/**,.tox/**
```

**Consistency rule:** `sonar.projectKey` must equal the SonarCloud project key exactly.

### 3. Add a SonarCloud GitHub Actions workflow

- **Prefer copying** from **`module/skills/sonarcloud-workflow-templates/`** (see **Canonical templates**
  above) so the file stays **identical** to other ansible-collections repos except optional commented guards.
- When the Sonar workflow is **`workflow_call`**-only, the caller (e.g. **`all_green_check.yaml`**) must pass
  **`secrets:`** explicitly for each secret declared under **`on.workflow_call.secrets`** (typically only
  **`ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT`**). Use **`all_green-caller.sonarcloud-job.yml.template`**
  as the canonical job block. Using **`secrets: inherit`** can fail validation with **"Only pass required
  secrets to this workflow."**
- Typical filename: `.github/workflows/sonarcloud.yml` (match sibling repos if an org convention exists).
- Job must checkout the repo, optionally **produce `coverage.xml`** (step 4), then run SonarScanner (official
  SonarCloud GitHub Action or **`sonar-scanner`** CLI) with:

```yaml
env:
  SONAR_TOKEN: ${{ secrets.ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT }}
```

Use the **same default branch** name in `sonar.newCode.referenceBranch` as in GitHub (`main` vs `devel`).

Reference implementations: **`sonarcloud-workflow-templates/`** in this module; **kubernetes.core**
**`workflow_call`** Sonar and **`all_green`** caller ([PR #1124](https://github.com/ansible-collections/kubernetes.core/pull/1124));
**amazon.aws** Sonar onboarding PRs for **`workflow_run`** + **`all_green`** naming and matrix parity.

### 4. Ensure `coverage.xml` exists at repo root before Sonar runs

`sonar-project.properties` expects **`coverage.xml` at the repository root** unless paths are changed.

**Option A — Workflow job:** Run unit tests with XML report directly, e.g. pytest with `--cov-report xml:coverage.xml` at repo root, then run Sonar in the same workflow
(or upload artifact between jobs).

**Option B — tox:** Add `--cov-report xml:coverage.xml` (or equivalent) to the relevant tox env; copy or configure output so the final file is **`coverage.xml` at repo root** before the Sonar step.

Until XML coverage is produced, SonarCloud still reports issues and duplication, but **coverage stays empty** in the UI.

For a **second PR** focused on coverage jobs, **`workflow_run`** wiring, aggregator gates, badges, and
path rewriting, use the companion skill **`configure-sonarcloud-coverage`**.

### 5. Integrate with existing test workflows

Update the primary unit-test workflow (may be named `tests.yml`, `units.yml`, etc.) so CI reliably
generates coverage used by Sonar **without** duplicating unnecessary work—often a **second focused PR**
after the minimal Sonar workflow merges (matches common staged rollout). Detailed steps for that phase
live in **`configure-sonarcloud-coverage`**.

### 6. Documentation

Add either:

- A **README** section covering SonarCloud, coverage expectation (~90% codebase target where policy applies), and fork secret behavior, or
- A dedicated **`sonarcloud.md`** (or similar) linked from the README.

### 7. Validate locally (optional but recommended)

See [reference.md](reference.md) for SonarScanner CLI install, `SONAR_TOKEN`, and `sonar-scanner` invocation from repo root to catch misconfiguration before CI.

## Quality expectations

Where org policy applies, collections should **aim for ~90%** coverage across the codebase; Sonar setup makes coverage visible—raising coverage is separate work.

## Integration with other skills

| Phase | Skill |
| ----- | ----- |
| Derive org/repo/Sonar key | `get-upstream-info` |
| Sonar coverage CI (`workflow_run`, artifacts, badges) | `configure-sonarcloud-coverage` |
| Analyze and fix findings | `sonarcloud-remediation` |

## Checklist (copy for PR description)

```
- [ ] sonar-project.properties at repo root; projectKey matches SonarCloud UI
- [ ] Sonar workflow uses org SONAR_TOKEN secret (and triggers documented for forks)
- [ ] If **sonarcloud.yml** is **workflow_call**-only: **all_green_check.yaml** (or aggregator) includes **sonarcloud** job with explicit **secrets:** (see **all_green-caller.sonarcloud-job.yml.template**)
- [ ] coverage.xml produced at repo root before Sonar step (or staged follow-up PR)
- [ ] Test workflow updated if needed for XML coverage
- [ ] README or sonarcloud.md explains Sonar + coverage for contributors
- [ ] No literal Sonar tokens in commits; workflows use secrets/vars only; fork/trust model documented
```
