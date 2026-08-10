#!/usr/bin/env python3
"""
Setup or update an Ansible collection repository.
Clones if not exists, updates if exists, ensures upstream remote is configured.

Usage:
    ./setup-collection-repo.py <namespace.collection>

Environment variables:
    ANSIBLE_COLLECTIONS_PATH: Base path for collections (default: ~/dev/collections/ansible_collections)
    UPSTREAM_ORG: GitHub organization (default: ansible-collections)
    GITHUB_USERNAME: GitHub username for fork (optional)
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple


class Colors:
    """ANSI color codes for terminal output. Respects NO_COLOR environment variable."""

    def __init__(self):
        # Disable colors if NO_COLOR environment variable is set
        if os.environ.get('NO_COLOR'):
            self.RESET = ''
            self.GREEN = ''
            self.RED = ''
            self.YELLOW = ''
        else:
            self.RESET = '\033[0m'
            self.GREEN = '\033[92m'
            self.RED = '\033[91m'
            self.YELLOW = '\033[93m'


# Global Colors instance
colors = Colors()


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
            return result.returncode, result.stderr.strip()
    except Exception as e:
        return 1, str(e)


def setup_collection_repo(collection: str, collections_base: Path, upstream_org: str) -> Tuple[bool, Path]:
    """
    Setup or update collection repository.

    Args:
        collection: Collection name (e.g., "amazon.aws")
        collections_base: Base path for collections
        upstream_org: GitHub organization

    Returns:
        Tuple of (success, collection_path)
    """
    # Parse namespace and collection name
    if '.' not in collection:
        print(f"{colors.RED}Error: Invalid collection format. Use namespace.name{colors.RESET}", file=sys.stderr)
        print("Example: amazon.aws", file=sys.stderr)
        return False, Path()

    namespace, name = collection.split('.', 1)
    collection_path = collections_base / namespace / name
    upstream_url = f"https://github.com/{upstream_org}/{namespace}.{name}.git"

    # Check if repository exists
    if (collection_path / ".git").exists():
        print(f"Repository exists at {collection_path}", file=sys.stderr)

        # Ensure upstream remote exists
        exit_code, remote_url = run_command(
            ["git", "remote", "get-url", "upstream"],
            cwd=collection_path
        )

        if exit_code != 0:
            print(f"Adding upstream remote: {upstream_url}", file=sys.stderr)
            run_command(
                ["git", "remote", "add", "upstream", upstream_url],
                cwd=collection_path
            )

        # Fetch from upstream
        print("Fetching from upstream...", file=sys.stderr)
        exit_code, _ = run_command(
            ["git", "fetch", "upstream", "--tags"],
            cwd=collection_path,
            capture=False
        )

        if exit_code != 0:
            print(f"{colors.RED}Error: Failed to fetch from upstream{colors.RESET}", file=sys.stderr)
            return False, collection_path

        # Get main branch name
        exit_code, main_branch = run_command(
            ["git", "remote", "show", "upstream"],
            cwd=collection_path
        )

        if exit_code == 0:
            for line in main_branch.split('\n'):
                if 'HEAD branch' in line:
                    main_branch = line.split(':')[1].strip()
                    break
            else:
                main_branch = "main"
        else:
            main_branch = "main"

        # Update main branch
        print(f"Updating {main_branch} branch...", file=sys.stderr)

        # Checkout main branch (create if doesn't exist)
        exit_code, _ = run_command(
            ["git", "checkout", main_branch],
            cwd=collection_path
        )

        if exit_code != 0:
            # Try to create branch from upstream
            run_command(
                ["git", "checkout", "-b", main_branch, f"upstream/{main_branch}"],
                cwd=collection_path
            )

        # Pull latest
        exit_code, _ = run_command(
            ["git", "pull", "upstream", main_branch],
            cwd=collection_path,
            capture=False
        )

        if exit_code != 0:
            print(f"{colors.YELLOW}Warning: Could not pull from upstream/{main_branch}{colors.RESET}", file=sys.stderr)

        print(f"{colors.GREEN}✅ Repository updated{colors.RESET}", file=sys.stderr)

    else:
        print("Repository does not exist, cloning...", file=sys.stderr)

        # Create parent directory
        collection_path.parent.mkdir(parents=True, exist_ok=True)

        # Clone repository
        exit_code, error = run_command(
            ["git", "clone", upstream_url, str(collection_path)],
            capture=False
        )

        if exit_code != 0:
            print(f"{colors.RED}❌ Failed to clone {upstream_url}{colors.RESET}", file=sys.stderr)
            print(error, file=sys.stderr)
            return False, collection_path

        # Set upstream remote (should already exist from clone, but ensure it's correct)
        run_command(
            ["git", "remote", "add", "upstream", upstream_url],
            cwd=collection_path
        )

        # Check if user has a fork and add as origin
        github_username = os.environ.get('GITHUB_USERNAME')
        if not github_username:
            # Try to get from git config
            exit_code, username = run_command(["git", "config", "user.name"])
            if exit_code == 0:
                github_username = username

        if github_username:
            fork_url = f"https://github.com/{github_username}/{namespace}.{name}.git"
            # Try to add fork as origin (may fail if fork doesn't exist, that's ok)
            exit_code, _ = run_command(
                ["git", "remote", "set-url", "origin", fork_url],
                cwd=collection_path
            )
            if exit_code != 0:
                print(f"No fork found at {fork_url}", file=sys.stderr)

        print(f"{colors.GREEN}✅ Repository cloned{colors.RESET}", file=sys.stderr)

    return True, collection_path


def main() -> int:
    """Main entry point."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <namespace.collection>", file=sys.stderr)
        print("Example: ./setup-collection-repo.py amazon.aws", file=sys.stderr)
        return 1

    collection = sys.argv[1]
    collections_base = Path(os.environ.get(
        'ANSIBLE_COLLECTIONS_PATH',
        str(Path.home() / "dev/collections/ansible_collections")
    ))
    upstream_org = os.environ.get('UPSTREAM_ORG', 'ansible-collections')

    success, collection_path = setup_collection_repo(collection, collections_base, upstream_org)

    if success:
        # Output the collection path (for use in scripts)
        print(str(collection_path))
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
