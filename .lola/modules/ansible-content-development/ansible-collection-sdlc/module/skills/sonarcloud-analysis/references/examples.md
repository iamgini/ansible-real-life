# Example Usage

## Example 1: PR Review

```
User: "Check sonar for this PR"

Skill:
1. Detects current branch: feature/add-caching
2. Finds PR #1234 for this branch
3. Fetches issues for PR #1234
4. Finds 3 new CODE_SMELL issues
5. Analyses each issue and suggests fixes
6. Reports: "3 new maintainability issues introduced. All are MINOR severity."
```

## Example 2: Technical Debt Audit

```
User: "Show me all security hotspots"

Skill:
1. Detects project key from git remote
2. Fetches all TO_REVIEW security hotspots
3. Groups by category (2 weak-cryptography, 5 encrypt-data, 1 dos)
4. Analyses each category
5. Identifies 3 false positives (AWS metadata HTTP calls)
6. Recommends addressing 2 weak-cryptography issues and 1 DOS issue
```

## Example 3: Comprehensive Analysis

```
User: "What's our SonarCloud status?"

Skill:
1. Fetches all issue types (security, reliability, maintainability)
2. Presents summary: 8 hotspots, 18 bugs, 156 code smells
3. Prioritises: 2 CRITICAL bugs, 8 MAJOR bugs
4. Recommends: "Focus on the 2 CRITICAL bugs first, then review security hotspots"
```

## Example 4: Large Codebase with Pagination

```
User: "Analyse SonarCloud issues for ansible-collections/amazon.aws"

Skill:
1. Determines project key: ansible-collections_amazon.aws
2. Fetches total counts:
   - 8 security hotspots
   - 5 bugs
   - 2,621 code smells
   Total: 2,626 issues
3. Recognises this exceeds 500 (page size limit)
4. Shows summary statistics and asks:
   "This project has 2,626 unresolved issues. Would you like to:
    - Analyse security hotspots (8 items)
    - Analyse bugs (5 items)
    - Analyse CRITICAL/BLOCKER code smells only
    - Analyse code smells by severity"
5. User selects "Analyse bugs"
6. Fetches and analyses all 5 bugs (no pagination needed)
7. Provides detailed analysis with fix suggestions
```
