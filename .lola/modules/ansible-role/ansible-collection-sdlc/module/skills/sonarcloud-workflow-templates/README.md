# SonarCloud workflow templates (ansible-collections org)

These files are **canonical copies** for Ansible collections under the **ansible-collections** GitHub org.

Live **`workflow_call`** reference:
[ansible-collections/kubernetes.core](https://github.com/ansible-collections/kubernetes.core) — repo
**`sonarcloud.yml`** (path `.github/workflows/`) and the **`sonarcloud`** job in **`all_green_check.yaml`**
(e.g. [PR #1124](https://github.com/ansible-collections/kubernetes.core/pull/1124)). Template
**`sonarcloud.workflow_call.yml.template`** matches that **`sonarcloud.yml`** line-for-line when org policy
changes.

| File | Role |
| ---- | ---- |
| [sonar-project.properties.template](sonar-project.properties.template) | Per-repo Sonar keys, paths, Python version |
| [sonarcloud.workflow_run.yml.template](sonarcloud.workflow_run.yml.template) | Sonar after **`workflow_run`** on workflow **`all_green`** completes |
| [sonarcloud.workflow_call.yml.template](sonarcloud.workflow_call.yml.template) | Reusable Sonar job; caller runs on **`pull_request`** / **`push`** |
| [all_green-caller.sonarcloud-job.yml.template](all_green-caller.sonarcloud-job.yml.template) | **`sonarcloud`** job block for **`all_green_check.yaml`** (explicit **`secrets:`**, fork guard) |

**Do not edit structure, action SHAs, job names, or secret names** in the workflow YAML when applying
them to a collection unless **GitHub / Sonar org maintainers** approve a coordinated change across repos.

## Choosing `workflow_run` vs `workflow_call`

Compare [workflow_run](sonarcloud.workflow_run.yml.template) and
[workflow_call](sonarcloud.workflow_call.yml.template):

- **Trigger** — **`workflow_run`**: separate workflow runs when **`all_green`** finishes. **`workflow_call`**:
  invoked from caller with `uses: ./.github/workflows/sonarcloud.yml`.
- **Checkout** — **`workflow_run`**: `ref: ${{ github.event.workflow_run.head_sha }}`. **`workflow_call`**: PR
  head SHA or `github.sha` from caller event.
- **Coverage download** — **`workflow_run`**: third-party download action (see
  **`sonarcloud.workflow_run.yml.template`**) with **`pattern: coverage*`** on the triggering run.
  **`workflow_call`**: **`actions/download-artifact@v4`** with **`name: coverage`** (one artifact). Pin and
  repo names match the template YAML.
- **Extra permissions** — **`workflow_run`**: `actions: read` (cross-workflow artifact read). **`workflow_call`**:
  not required for that download pattern.
- **PR metadata** — **`workflow_run`**: shell + **`gh`** when `workflow_run.event == pull_request`. **`workflow_call`**:
  native `github.event.pull_request.*` on PR callers.
- **Secrets** — **`workflow_run`**: repo/org secret in job `env`. **`workflow_call`**: pass only the secrets
  the callee declares (e.g.
  **`ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT: ${{ secrets.ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT }}`**).
  Avoid **`secrets: inherit`** when the reusable workflow lists explicit **`workflow_call.secrets`**; GitHub may
  reject inherit with **"Only pass required secrets to this workflow."**

Use **`workflow_call`** when org policy avoids **`workflow_run`** + **`head_sha`** checkout (e.g. Sonar security
hotspot / quality gate). Otherwise **`workflow_run`** matches the common **amazon.aws**-style aggregator pattern.

## What to copy where

| Template | Destination |
| -------- | ----------- |
| [sonar-project.properties.template](sonar-project.properties.template) | Repo root `sonar-project.properties` |
| [sonarcloud.workflow_run.yml.template](sonarcloud.workflow_run.yml.template) | `.github/workflows/sonarcloud.yml` |
| [sonarcloud.workflow_call.yml.template](sonarcloud.workflow_call.yml.template) | `.github/workflows/sonarcloud.yml` (alternative) |
| [all_green-caller.sonarcloud-job.yml.template](all_green-caller.sonarcloud-job.yml.template) | Paste **`jobs:`** fragment into **`all_green_check.yaml`** (with **`all_green`** + **`coverage`**) |

**Allowed edits** (otherwise keep YAML structure, pins, and secret names unchanged):

- **sonar-project.properties.template** — Replace every `__PLACEHOLDER__` per legend in that file. Paths
  (`sonar.tests`, `sonar.exclusions`) may be tuned for tree layout **only** if SonarCloud project settings agree.
- **sonarcloud.workflow_run.yml.template** — **None** in YAML structure or pins. Optional: uncomment the `if:`
  guard on the **`finalize`** job for same-repo-only finalize (see comments in file). Upstream **`all_green`**
  must upload artifacts matching **`coverage*`** (e.g. `coverage.xml`, `coverage-unit.xml`).
- **sonarcloud.workflow_call.yml.template** — **None** in YAML structure or pins. Body matches merged
  **kubernetes.core** `sonarcloud.yml`; refresh from that repo when coordinated org changes land.
- **all_green-caller.sonarcloud-job.yml.template** — **None** in structure or secret names. Copy the
  **`sonarcloud`** job (YAML only, drop leading `#` comment lines) into **`all_green_check.yaml`** after
  **`all_green`** and **`coverage`** jobs. Caller uploads **one** artifact **`name: coverage`**; use explicit
  **`secrets:`** (not **`secrets: inherit`**) when the callee declares **`workflow_call.secrets`** only for the
  Sonar token (see **Secrets** above).

## Aggregator workflow name (`workflow_run` template)

The **`workflow_run`** template listens for a workflow whose **`name:`** field is exactly **`all_green`**.
Your aggregator file (often `all_green_check.yaml`) must set:

```yaml
name: all_green
```

The **`workflows:`** list in `sonarcloud.yml` uses that **display name**, not the YAML filename.

## Org secret (lookup)

For **ansible-collections** repositories, workflows should reference:

```yaml
secrets.ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT
```

CI is expected to work **without** renaming that secret. Other orgs must replace the secret name in a
**single coordinated** change approved by their admins (do not fork the template with a different
secret name per repo unless required).

## Related skills

- **`configure-sonarcloud-collection`** — when to use templates, `sonar-project.properties`, first-phase docs.
- **`configure-sonarcloud-coverage`** — `all_green`, coverage jobs, `workflow_call` vs `workflow_run`, badges.
