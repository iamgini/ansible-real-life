# Error Handling & Recovery

## Recoverable Errors

**Lint/Sanity Failures**:

```
Options:
  [r] Retry after fixing issues
  [s] Skip this step (--force)
  [a] Abort workflow

Choice [r/s/a]:
```

**Merge Conflicts**:

```
⚠️ Merge conflict detected while syncing stable-1

Actions:
  1. Resolve conflicts manually
  2. Run: git add <files>
  3. Re-run: /stable-release --resume

Abort workflow? [y/N]:
```

**Network Errors**:

```
⚠️ Failed to push to origin (network error)

Retrying in 5 seconds... (attempt 2/3)
```

## Non-Recoverable Errors

**Missing Configuration**:

```
❌ Error: GITHUB_USERNAME not set

Setup required:
  1. Create config: cp ansible-release.conf.template ~/.ansible-release.conf
  2. Edit config: vim ~/.ansible-release.conf
  3. Set GITHUB_USERNAME="your-username"
  4. Re-run: /stable-release
```

**Not a Git Repository**:

```
❌ Error: Not a git repository

Ensure you're in a collection directory:
  cd ~/dev/collections/ansible_collections/namespace/collection
```

## Resume Capability

State is tracked in `.ansible-release-state.json`:

```json
{
  "collection": "amazon.ai",
  "version": "1.0.1",
  "branch": "prep_v1.0.1",
  "last_completed_step": "docs-generate",
  "timestamp": "2026-04-01T14:45:00Z"
}
```

Resume workflow:

```bash
/stable-release --resume
```

Output:

```
Resuming from last checkpoint...
Last completed: docs-generate
Continuing with: quality checks
```
