# Implementation Notes

## Parallel Execution

Run lint and sanity concurrently for speed:

```python
# Use Claude Code's ability to run agents in parallel
Agent(skill="tox-lint", args="--path=${COLLECTION_PATH}", run_in_background=True)
Agent(skill="sanity", args="--mode=${SANITY_MODE} --path=${COLLECTION_PATH}", run_in_background=True)

# Claude Code will notify when both complete
# Then proceed to next step
```

## State Management

```python
import json
from pathlib import Path
from datetime import datetime

STATE_FILE = Path.cwd() / ".ansible-release-state.json"

def save_state(step: str, data: dict):
    state = {
        "last_completed_step": step,
        "timestamp": datetime.now().isoformat(),
        **data
    }
    STATE_FILE.write_text(json.dumps(state, indent=2))

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return None

def clear_state():
    if STATE_FILE.exists():
        STATE_FILE.unlink()
```

## User Interaction

Provide clear prompts and progress:

- Show step numbers [1/6], [2/6], etc.
- Use status indicators: ✅ ❌ ⚠️
- Provide actionable error messages
- Offer resume capability on failure
- Display total time at completion

## Cloud Content Handbook Compliance

Follow handbook guidelines:

- Use double backticks for module names
- Standard commit message format
- Co-Authored-By: Claude attribution
- PR template with checklist
- Quality checks before commit
