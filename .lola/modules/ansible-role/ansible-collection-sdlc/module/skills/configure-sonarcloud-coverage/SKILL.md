---
name: configure-sonarcloud-coverage
description: >
  Configures CI coverage reporting for SonarCloud on Ansible collections. Use
  this skill when Sonar already runs but coverage is missing and you need to
  wire XML reports, aggregator workflows, and scanner report paths.
user-invocable: true
---

# Configure SonarCloud coverage for an Ansible Collection

Wire **unit-test coverage into SonarCloud** so the UI shows coverage, not only issues and duplication.
This is typically a **follow-up PR** after minimal Sonar onboarding (`configure-sonarcloud-collection`).

## Purpose

- Produce **`coverage*.xml`** (or equivalent) in CI reliably
- Ensure the Sonar scan step receives **`sonar.python.coverage.reportPaths`** (properties file and/or
  scanner `-D` arguments)
- Optionally adopt an **aggregator workflow** plus **`workflow_run`** (or a reusable **`workflow_call`**
  Sonar workflow) so Sonar runs only after linters, sanity, units, and coverage succeed—matching patterns
  discussed in public collection PRs such as
  [amazon.aws#2871](https://github.com/ansible-collections/amazon.aws/pull/2871)

## Canonical templates (ansible-collections)

Use **`module/skills/sonarcloud-workflow-templates/`** in this module:

- **`sonarcloud.workflow_run.yml.template`** — Pattern B. Paste into **`.github/workflows/sonarcloud.yml`**.
  Listens for **`all_green`** via **`workflow_run`**. Uses **`dawidd6/action-download-artifact`** with
  **`pattern: coverage*`**. Needs **`permissions.actions: read`**. Optional **`if:`** on **`finalize`** (see
  template comments).
- **`sonarcloud.workflow_call.yml.template`** — Pattern B2 (reusable Sonar). Same destination filename.
  Body stays **line-for-line** with merged **kubernetes.core** **`.github/workflows/sonarcloud.yml`**
  (e.g. [PR #1124](https://github.com/ansible-collections/kubernetes.core/pull/1124)). Upload **one**
  artifact **`name: coverage`**; template uses **`actions/download-artifact@v4`**.
- **`all_green-caller.sonarcloud-job.yml.template`** — **`sonarcloud`** job block to paste into
  **`all_green_check.yaml`** (or equivalent): **`needs: [all_green, coverage]`**, fork-safe **`if:`**,
  **`uses: ./.github/workflows/sonarcloud.yml`**, explicit **`secrets:`** for
  **`ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT`** (not **`secrets: inherit`** when the callee lists only
  that secret; GitHub may report **"Only pass required secrets to this workflow."**). See template
  **`README.md`**.
- **`sonar-project.properties.template`** — only file that should differ per repo (placeholders).

Keep YAML **identical** across repos; do not change action SHAs or **`ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT`** without an org-wide rollout.

## When to Invoke

TRIGGER when the user asks to:

- Add or fix **SonarCloud coverage** after Sonar already analyzes the repo but coverage is empty
- Split Sonar out of a monolithic job into **artifact + workflow_run** flow
- Add a **coverage job** (tox, pytest-cov, or `ansible-test` coverage xml) for Sonar
- Document **coverage badges** or `docs/sonarcloud.md`-style contributor notes for Sonar coverage

DO NOT TRIGGER when:

- There is **no** Sonar project or `sonar-project.properties` yet (use `configure-sonarcloud-collection`
  first)
- The user only wants Sonar **issue** review or fixes (`sonarcloud-remediation`)

## Prerequisites

- `sonar-project.properties` exists with a sensible `sonar.python.coverage.reportPaths` **or** the team
  passes paths only via scanner `args` (some repos override paths dynamically).
- Org **`SONAR_TOKEN`** available to the workflow that runs the scanner (subject to fork/trusted-job
  rules—see **Security** in `configure-sonarcloud-collection`).

## Security

Follow **`configure-sonarcloud-collection`** Security section: no literal tokens in commits; human-review
workflow changes; use **`workflow_run` + artifacts** when fork PRs must not receive org secrets in the
same job as the scanner.

## Workflow for the agent

### 1. Inspect existing CI

- Locate the **Sonar** workflow and **unit test** workflow(s): tox env names, `ansible-test units`,
  reusable workflows (`uses:`), Python/Ansible versions.
- Confirm whether coverage is already produced **inline** before the Sonar step (single workflow) or
  missing entirely.

### 2. Pick an integration pattern

Start from **`module/skills/sonarcloud-workflow-templates/README.md`**.

Copy the matching **`sonarcloud.*.yml.template`** to **`.github/workflows/sonarcloud.yml`** without edits.
Then wire **`all_green`** and coverage jobs to match that template (artifact names, workflow **`name:`**).

#### Pattern A — Inline scan with coverage (simplest)

One job runs tests with coverage, writes XML (repo root or fixed path), then runs
`SonarSource/sonarqube-scan-action`. Suitable when the Sonar job already runs only on **trusted**
triggers (for example same-repo PRs and pushes).

Typical **`ansible-test`** sequence:

```bash
ansible-test units --venv --coverage --python X.Y --requirements
ansible-test coverage combine --venv --python X.Y --requirements
ansible-test coverage xml --venv --python X.Y --requirements
# Copy or reference XML under tests/output/reports/ as needed for sonar.python.coverage.reportPaths
```

#### Pattern B — Aggregator + `workflow_run` (amazon.aws-style)

1. A workflow such as **`all_green`** runs **linters** (often PR-only), **test jobs** (one **`ansible-test`**
   workflow or separate **sanity** / **unit** callable workflows), and a dedicated **coverage** job. The
   coverage job runs **tox** or **pytest** with **`--cov-report xml`** (amazon.aws), or **`ansible-test`**
   **`coverage xml`** (kubernetes.core-style); locate **`coverage.xml`**, often under **`.tox`** or
   **`tests/output/reports/`**, and optionally **rewrite paths** so sources are repo-relative.
2. Upload artifacts whose names match **`coverage*`** (`actions/upload-artifact`). Examples: **`coverage`**,
   **`coverage-unit.xml`**. Must align with **`sonarcloud.workflow_run.yml.template`** (`pattern: coverage*`).
3. A separate **`sonarcloud.yml`** triggers on **`workflow_run`** when that workflow completes successfully.
   The **`workflows:`** list must match the aggregator **`name:`** (for example **`all_green`**), not only the
   YAML filename (**`all_green_check.yaml`**). Check out **`head_sha`** of the triggering run. Download
   coverage artifacts. Build comma-separated **`sonar.python.coverage.reportPaths`**. For PRs, set
   **`sonar.pullrequest.*`** when needed. Run the scan action. Remove any **inline** Sonar job on
   **`push`/`pull_request`** that duplicated coverage so Sonar does not run twice.

Grant **`permissions: actions: read`** (and **`contents`**, **`pull-requests`** as required) on the Sonar
workflow so **`dawidd6/action-download-artifact`** can read the triggering run’s artifacts.

#### Pattern B2 — Aggregator + reusable **`workflow_call`** Sonar

Same **`all_green`** / coverage jobs as Pattern B. Sonar lives in **`sonarcloud.workflow_call.yml.template`**.

Copy the **`sonarcloud`** job from **`all_green-caller.sonarcloud-job.yml.template`** into
**`all_green_check.yaml`** (YAML only; drop the file’s leading **`#`** comment lines), or mirror the merged
**kubernetes.core** layout ([PR #1124](https://github.com/ansible-collections/kubernetes.core/pull/1124)).
Requires **`actions/upload-artifact`** with **`name: coverage`** (exact) before **`uses: ./.github/workflows/sonarcloud.yml`**
and explicit **`secrets:`** mapping for **`ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT`**.

Do **not** mix this with the **`workflow_run`** template in the same repo unless maintainers intentionally run
two scanners.

#### Pattern C — Fork-safe

Unit workflow uploads coverage **without** `SONAR_TOKEN`; Sonar workflow uses **`workflow_run`** on the
default-branch context (see GitHub docs linked from `configure-sonarcloud-collection`).

### 3. Align `sonar-project.properties` and scanner args

- If paths are fixed: `sonar.python.coverage.reportPaths=coverage.xml` at repo root.
- If multiple reports or dynamic discovery: pass **`-Dsonar.python.coverage.reportPaths=...`** on the scan
  step (comma-separated list), consistent with properties.

### 4. Dependencies and tooling

- **ansible-test**: use **`ansible-test units --coverage`**, then **`ansible-test coverage combine`** and
  **`ansible-test coverage xml`**; copy the generated XML to the repo root (often under
  **`tests/output/reports/`**) and upload as a **`coverage*`** artifact. Common for collections that use
  **`ansible-network`** reusable unit workflows and add **`workflow_call`** so an **`all_green`** job can
  **`uses:`** them.
- **pytest-cov / tox**: use when coverage is produced via **tox** or raw **pytest** (for example
  [amazon.aws#2871](https://github.com/ansible-collections/amazon.aws/pull/2871)); add **`pytest-cov`** to
  **`tests/unit/requirements.txt`** (or test extras) when pytest runs with **`--cov`**. Collections may
  still list **`pytest-cov`** for parity even when **`ansible-test`** supplies the XML Sonar consumes.
- **Path rewriting**: if Sonar shows **0%** coverage with XML present, strip **`GITHUB_WORKSPACE`** from
  paths in the file (**`sed`**, or **`coverage.toml` / `pyproject.toml`** with **`relative_files`**) so
  Sonar resolves sources.

### 4a. Example: `all_green` + `workflow_run` (kubernetes.core-style)

1. Add **`workflow_call:`** beside existing **`pull_request`** on **`linters.yaml`**, **`sanity-tests.yaml`**,
   **`unit-tests.yaml`** (or equivalent) so **`all_green`** can call them.
2. Add **`all_green_check.yaml`** with **`name: all_green`**, jobs **linters** (PR-only), **sanity**,
   **units**, **coverage** (XML + artifact **`coverage*`**), and a final **all_green** assert (skip
   **linters** on **push**), mirroring
   [amazon.aws all_green_check.yml](https://github.com/ansible-collections/amazon.aws/blob/main/.github/workflows/all_green_check.yml).
3. Copy **`sonarcloud.workflow_run.yml.template`** to **`.github/workflows/sonarcloud.yml`**. Optionally keep
   the org file identical to the template. **`workflow_run.workflows`** must list the aggregator **`name:`**
   (e.g. **`all_green`**), not only the YAML filename.
4. **README**: SonarCloud badges and a link to **`https://sonarcloud.io/project/overview?id=<projectKey>`**.

PRs may run linters/sanity/units **twice** (standalone plus **`all_green`**) until maintainers consolidate
checks.

### 5. Documentation and visibility

- Add **README** badges and a link to the **SonarCloud project overview** URL
  (`https://sonarcloud.io/project/overview?id=<sonar.projectKey>`).
- Optional **`docs/sonarcloud.md`** (or **`CI.md`**) describing when coverage runs and how forks interact
  with CI.

### 6. Validate

- Merge or run on default branch as required for trusted workflows.
- Confirm SonarCloud UI shows **coverage** for the branch or PR, not only **0%** or missing measures.
- Optionally require the **`all_green`** check (or equivalent) in branch protection so **`workflow_run`**
  Sonar always has a successful upstream run with artifacts.

## Integration with other skills

| Phase | Skill |
| ----- | ----- |
| Initial Sonar files and scanner workflow | `configure-sonarcloud-collection` |
| Coverage jobs, artifacts, `workflow_run`, badges | `configure-sonarcloud-coverage` |
| Analyze and fix Sonar findings | `sonarcloud-remediation` |

## Checklist (copy for PR description)

```
- [ ] CI emits XML coverage on every path Sonar should analyze (tox/pytest and/or ansible-test)
- [ ] Sonar scan receives sonar.python.coverage.reportPaths (file and/or -D args)
- [ ] If using **workflow_run**: aggregator **`name:`** matches **`workflow_run.workflows`**; uploads artifacts
  matching **`coverage*`**; Sonar workflow downloads for **`head_sha`**; old inline Sonar job removed if present
- [ ] If using **workflow_call** Sonar template: **`sonarcloud`** job from **all_green-caller.sonarcloud-job.yml.template**
  (or **kubernetes.core** [PR #1124](https://github.com/ansible-collections/kubernetes.core/pull/1124)); caller uploads **one**
  artifact named exactly **`coverage`** before **`uses: ./.github/workflows/sonarcloud.yml`**
- [ ] Path rewriting / relative_files addressed if Sonar shows 0% coverage with XML present
- [ ] README or docs updated (badges, contributor notes)
- [ ] No secrets in logs; workflows reviewed for fork/trust model
```

Further links: [reference.md](reference.md).
