#!/usr/bin/env python3
"""
Check a single stable branch for unreleased commits and calculate next version.

Usage:
    ./check-branch.py <branch> [collection_path]

Output format:
    STATUS|CURRENT_VERSION|NEXT_VERSION|IMPACT|COMMIT_COUNT|FRAGMENT_COUNT
    Examples:
        UP_TO_DATE|1.0.0|0
        NEEDS_RELEASE|1.0.0|1.0.1|PATCH|5|1
        NO_FRAGMENTS|1.0.0|5
        ERROR|Could not checkout branch
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple


def run_command(cmd: list, cwd: Path = None, capture: bool = True) -> Tuple[int, str]:
    """Run a command and return exit code and output."""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode, result.stdout.strip()
        else:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode, ""
    except Exception as e:
        return 1, str(e)


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <branch> [collection_path]", file=sys.stderr)
        return 1

    branch = sys.argv[1]
    collection_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()

    if not collection_path.exists():
        print(f"ERROR|Collection path not found: {collection_path}")
        return 0

    # Checkout branch
    exit_code, _ = run_command(["git", "checkout", branch], cwd=collection_path)
    if exit_code != 0:
        print(f"ERROR|Could not checkout {branch}")
        return 0

    # Pull from upstream
    exit_code, _ = run_command(["git", "pull", "upstream", branch], cwd=collection_path)
    if exit_code != 0:
        print(f"ERROR|Could not pull from upstream/{branch}")
        return 0

    # Get last tag
    exit_code, last_tag = run_command(
        ["git", "describe", "--tags", "--abbrev=0"],
        cwd=collection_path
    )

    if exit_code != 0 or not last_tag:
        print(f"ERROR|No tags found on {branch}")
        return 0

    # Count commits since last tag
    exit_code, commit_log = run_command(
        ["git", "log", f"{last_tag}..HEAD", "--oneline"],
        cwd=collection_path
    )

    if exit_code != 0:
        print(f"ERROR|Could not get commit log")
        return 0

    commit_count = len([line for line in commit_log.split('\n') if line.strip()])

    if commit_count == 0:
        print(f"UP_TO_DATE|{last_tag}|0")
        return 0

    # Check for changelog fragments
    fragments_dir = collection_path / "changelogs/fragments"
    if not fragments_dir.exists():
        print(f"NO_FRAGMENTS|{last_tag}|{commit_count}")
        return 0

    # Count fragment files
    fragment_count = len([
        f for f in fragments_dir.glob("*.yml")
        if f.name != ".keep"
    ]) + len([
        f for f in fragments_dir.glob("*.yaml")
        if f.name != ".keep"
    ])

    if fragment_count == 0:
        print(f"NO_FRAGMENTS|{last_tag}|{commit_count}")
        return 0

    # Calculate next version using calculate-version.py
    script_dir = Path(__file__).parent
    calc_script = script_dir / "calculate-version.py"

    exit_code, version_info = run_command(
        [sys.executable, str(calc_script), last_tag, str(fragments_dir)],
        cwd=collection_path
    )

    if exit_code != 0:
        print(f"ERROR|Failed to calculate version")
        return 0

    # Parse version info: IMPACT|NEXT_VERSION|FRAGMENT_COUNT
    parts = version_info.split('|')
    if len(parts) != 3:
        print(f"ERROR|Invalid version calculation output")
        return 0

    impact = parts[0]
    next_version = parts[1]
    frag_count = parts[2]

    # Output format: STATUS|CURRENT_VERSION|NEXT_VERSION|IMPACT|COMMIT_COUNT|FRAGMENT_COUNT
    print(f"NEEDS_RELEASE|{last_tag}|{next_version}|{impact}|{commit_count}|{frag_count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
