---
description: Check SonarCloud analysis results for the current pull request
argument-hint: "[pr-number]"
---

Check the SonarCloud static analysis results for the current pull request.

Use the `get-pr-number` skill to detect the PR number from the current branch, then use the `sonarcloud-remediation` skill to:

1. Fetch SonarCloud issues specific to this pull request
2. Filter issues to show only those introduced or affected by PR changes
3. Categorize issues by type (security hotspots, bugs, code smells)
4. Group related issues by rule or file
5. Provide severity assessment and priority recommendations
6. Suggest whether issues should be fixed or marked as false positives

The skill will present a focused analysis of SonarCloud findings for this PR, helping you understand what static analysis issues need attention before the PR can be merged.
