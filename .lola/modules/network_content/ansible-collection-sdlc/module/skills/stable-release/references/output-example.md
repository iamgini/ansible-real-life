# Complete Output Example

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ansible Collection Release Orchestrator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Collection: amazon.ai
Working directory: /Users/alinabuzachis/dev/collections/ansible_collections/amazon/ai
Reference: https://github.com/ansible-collections/cloud-content-handbook

[1/6] Analyzing pending releases...
      Running: /stable-release-analyze

      ✅ Analysis complete
      Branch: stable-1
      Current: 1.0.0 → Proposed: 1.0.1 (PATCH)
      Reason: 1 bugfix fragment

      Proceed with release v1.0.1? [Y/n]: y

[2/6] Preparing release branch...
      Running: /stable-release-prep --version 1.0.1 --branch stable-1

      ✅ Branch created: prep_v1.0.1
      ✅ galaxy.yml updated
      ✅ Changelog generated

[3/6] Generating documentation...
      Running: /docs-generate

      ✅ Documentation updated (12 files)

[4/6] Running quality checks...
      Running: /tox-lint --path=${COLLECTION_PATH} (parallel)
      Running: /sanity --mode=smart --path=${COLLECTION_PATH} (parallel)

      ✅ tox-lint: All checks passed (84.7s)
      ✅ sanity: All tests passed (45.3s)

[5/6] Committing and pushing...
      Running: git commit and git push

      ✅ Committed: 46a848a
      ✅ Pushed to origin/prep_v1.0.1

[6/6] Creating pull request...
      Auto-create PR: prompt

      Create PR now? [Y/n]: y

      ✅ PR created: https://github.com/ansible-collections/amazon.ai/pull/42

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Release workflow complete! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
  Collection: amazon.ai
  Version: 1.0.0 → 1.0.1
  Branch: prep_v1.0.1
  Commit: 46a848ad98855647d56e00bcbb5b5fd4b8ce67f7
  PR: https://github.com/ansible-collections/amazon.ai/pull/42

Next steps:
  1. Monitor PR: https://github.com/ansible-collections/amazon.ai/pull/42
  2. After merge, tag release: git tag v1.0.1 && git push upstream v1.0.1
  3. GitHub Actions will publish to Galaxy

Total time: 2m 34s
```
