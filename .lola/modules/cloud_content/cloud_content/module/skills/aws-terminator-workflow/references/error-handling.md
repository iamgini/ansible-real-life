# Error Handling

## Analysis Failures

**No modules found**:

```
Analysis complete: No new modules found in PR
No aws-terminator changes needed.
```

**Action**: Exit gracefully, no work to do.

**Analysis errors**:

```
Error during analysis: <error message>
```

**Action**: Display error, offer to retry or abort.

## Implementation Failures

**Syntax errors**:

```
Python syntax error in aws/terminator/application_services.py:
  File "...", line 123
    def terminate(self)
                      ^
SyntaxError: invalid syntax
```

**Action**: Show error, offer to fix and retry.

**Tox failures**:

```
pylint failed:
  E1101: Module 'client' has no 'delete_foo' member
```

**Action**: Show error, offer options (fix/skip/abort).

## Git/PR Failures

**Push failures**:

```
Error: failed to push branch
Permission denied (publickey)
```

**Action**: Show error, suggest checking gh auth status.

**PR creation failures**:

```
Error creating PR: GraphQL error
```

**Action**: Show error, provide manual PR creation instructions.

## Recovery

### Resume from Failure

If workflow fails mid-execution, it can be resumed:

```bash
# Check current state
cd ~/dev/aws-terminator
git status

# Resume workflow from where it left off
/aws-terminator-workflow --pr <PR_NUMBER> --resume
```

State is tracked in `.aws-terminator-workflow-state.json`:

```json
{
  "pr_number": 2353,
  "repo": "ansible-collections/community.aws",
  "last_completed_step": "implement",
  "branch_name": "add-medialive-terminators",
  "analysis_file": "/tmp/terminator-analysis-2353.md"
}
```
