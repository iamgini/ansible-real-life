# SonarCloud setup reference

Supplementary detail for `configure-sonarcloud-collection`. Read when validating locally or explaining admin steps.

## SonarCloud web UI

1. Sign in at https://sonarcloud.io with GitHub.
2. **Analyze new project** → select the collection repository.
3. Set the **project key** to match `sonar.projectKey` in `sonar-project.properties` (must match exactly).

Org admins create projects and manage tokens; coordinate through your team’s usual channels if the project does not exist or keys conflict.

## ansible-collections org token in CI

```yaml
env:
  SONAR_TOKEN: ${{ secrets.ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT }}
```

Secret is configured at **organization** level; repository workflows reference it by name.

## Run SonarScanner locally

Useful to validate `sonar-project.properties` and layout before relying on CI.

<!-- markdownlint-disable MD029 -->

1. Install [SonarScanner CLI](https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/) and put `bin` on `PATH`.
2. Create a user token in SonarCloud (**My Account → Security**) and export:

```bash
export SONAR_TOKEN=<token>
```

3. From the **repository root** (where `sonar-project.properties` lives):

```bash
sonar-scanner -Dsonar.projectBaseDir=. -Dsonar.host.url=https://sonarcloud.io
```

4. Check the end of the log for errors. Results appear under the project on SonarCloud.

<!-- markdownlint-enable MD029 -->

## Staged PRs

Common rollout:

1. **First PR:** `sonar-project.properties` + minimal Sonar workflow (scanner runs; coverage may be absent initially).
2. **Second PR:** tox/pytest/workflow changes so `coverage.xml` is produced at repo root + README/doc updates.

This matches workflows where unit jobs historically only produced HTML coverage reports.

## Canonical workflow YAML in this module

For **ansible-collections** repos, copy templates from **`module/skills/sonarcloud-workflow-templates/`**.

Read **`sonarcloud-workflow-templates/README.md`** there first. Then copy one or more of:

- **`sonar-project.properties.template`**
- **`sonarcloud.workflow_run.yml.template`**
- **`sonarcloud.workflow_call.yml.template`**
- **`all_green-caller.sonarcloud-job.yml.template`** (paste **`sonarcloud`** job into **`all_green_check.yaml`**
  when using **`workflow_call`** Sonar; see [kubernetes.core#1124](https://github.com/ansible-collections/kubernetes.core/pull/1124))

Keep workflow YAML **identical** org-wide unless maintainers coordinate a pin or layout change.

## Example community reference

Concrete file-level examples appear in public collection PRs (e.g. amazon.aws SonarCloud onboarding). Use them as templates; adapt paths and Python versions to each collection.

## Security references (forks, secrets, trusted CI)

Use these alongside the **Security** section in [SKILL.md](SKILL.md). Prefer **public** sources here; upstream may also maintain **internal** runbooks—use those when available.

- [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Approving workflow runs from forks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/approving-workflow-runs-from-public-forks)
- [`workflow_run` event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_run)
- [SonarQube Cloud — CI-based analysis](https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/ci-based-analysis)

## Assistant / skill usage

Skills and coding assistants must **not** write real tokens into repositories or conversations. Prefer
human-reviewed workflow YAML, org-provided secret names, and the patterns above—especially when fork
PRs must receive Sonar results with coverage.

For the **second-phase** coverage rollout (artifacts, `workflow_run`, badges), see the sibling skill
`configure-sonarcloud-coverage` in this module.
