---
description: Check GitHub Actions/GitLab CI status and analyze failures
argument-hint: "[pr-number]"
---

Check the status of GitHub Actions/GitLab CI for the current pull request or branch.

Use the `get-pr-action-results` skill to:

1. Detect the PR number from the current branch (or check branch directly if no PR exists)
2. Get the upstream repository information
3. List recent workflow runs and identify failures
4. Analyze failed jobs by examining logs
5. Provide actionable error summaries with file paths and line numbers
6. Suggest specific fixes based on error patterns
7. Offer to apply straightforward fixes (formatting, linting, etc.)

The skill will present a clear summary of what's failing and why, helping you quickly troubleshoot CI/CD issues.
