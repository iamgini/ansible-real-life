#!/usr/bin/env python3
"""Analyze Ansible collection stable branches for pending releases."""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Check for required dependencies before importing
try:
    import yaml
except ImportError:
    print("\n" + "=" * 70, file=sys.stderr)
    print("ERROR: PyYAML is required but not installed", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("\nThis script requires PyYAML to parse changelog fragments.", file=sys.stderr)
    print("\nTo install PyYAML:", file=sys.stderr)
    print("\n  Option 1 (with uv - faster):", file=sys.stderr)
    print("    uv pip install pyyaml", file=sys.stderr)
    print("\n  Option 2 (with pip):", file=sys.stderr)
    print("    pip install pyyaml", file=sys.stderr)
    print("\n  Option 3 (in a virtual environment - recommended):", file=sys.stderr)
    print("    python3 -m venv .venv", file=sys.stderr)
    print("    source .venv/bin/activate", file=sys.stderr)
    print("    pip install pyyaml", file=sys.stderr)
    print("\n" + "=" * 70 + "\n", file=sys.stderr)
    sys.exit(2)


class Colors:
    """ANSI color codes. Respects NO_COLOR environment variable."""

    def __init__(self):
        # Disable colors if NO_COLOR environment variable is set
        if os.environ.get('NO_COLOR'):
            self.RESET = ''
            self.BOLD = ''
            self.GREEN = ''
            self.RED = ''
            self.YELLOW = ''
            self.BLUE = ''
            self.CYAN = ''
        else:
            self.RESET = '\033[0m'
            self.BOLD = '\033[1m'
            self.GREEN = '\033[92m'
            self.RED = '\033[91m'
            self.YELLOW = '\033[93m'
            self.BLUE = '\033[94m'
            self.CYAN = '\033[96m'


# Global Colors instance
colors = Colors()


def setup_collection_repo(collection_name: str) -> Path:
    """Setup collection repository (clone or update)."""
    # Parse namespace.name
    match = re.match(r'^([a-z]+)\.([a-z_]+)$', collection_name)
    if not match:
        print(f"{colors.RED}Error: Invalid collection name format{colors.RESET}", file=sys.stderr)
        sys.exit(2)

    namespace, name = match.groups()
    collections_path = Path.home() / "dev" / "collections" / "ansible_collections"
    collection_path = collections_path / namespace / name

    if not collection_path.exists():
        print(f"Cloning {collection_name}...", file=sys.stderr)
        repo_url = f"https://github.com/ansible-collections/{collection_name}.git"

        collection_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run(
                ["git", "clone", repo_url, str(collection_path)],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"{colors.RED}Error cloning: {e.stderr.decode()}{colors.RESET}", file=sys.stderr)
            sys.exit(1)

    # Update repository
    print(f"Repository exists at {collection_path}", file=sys.stderr)
    print("Fetching from upstream...", file=sys.stderr)

    try:
        subprocess.run(
            ["git", "fetch", "upstream", "--tags"],
            cwd=collection_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=collection_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "pull", "upstream", "main"],
            cwd=collection_path,
            check=True,
            capture_output=True
        )
        print(f"{colors.GREEN}✅{colors.RESET} Repository updated", file=sys.stderr)
    except subprocess.CalledProcessError:
        pass  # Continue anyway

    return collection_path


def get_collection_info(collection_path: Path) -> Dict[str, str]:
    """Extract collection metadata from galaxy.yml."""
    galaxy_yml = collection_path / "galaxy.yml"

    if not galaxy_yml.exists():
        print(f"{colors.RED}Error: Not an Ansible collection (galaxy.yml not found){colors.RESET}", file=sys.stderr)
        sys.exit(1)

    with open(galaxy_yml, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return {
        "namespace": data.get("namespace", ""),
        "name": data.get("name", ""),
        "version": data.get("version", ""),
    }


def get_stable_branches(collection_path: Path, upstream: str = "upstream") -> List[str]:
    """Get list of stable branches from upstream."""
    try:
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=collection_path,
            check=True,
            capture_output=True,
            text=True
        )

        branches = []
        pattern = re.compile(rf'remotes/{upstream}/stable-(\d+)$')

        for line in result.stdout.splitlines():
            match = pattern.search(line.strip())
            if match:
                branches.append(f"stable-{match.group(1)}")

        # Sort by version number
        return sorted(branches, key=lambda x: int(x.split('-')[1]))
    except subprocess.CalledProcessError:
        return []


def check_branch(branch: str, collection_path: Path) -> Tuple[str, Dict[str, Any]]:
    """Check a single branch for release needs."""
    try:
        # Checkout branch
        subprocess.run(
            ["git", "checkout", branch],
            cwd=collection_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "pull", "upstream", branch],
            cwd=collection_path,
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        return "ERROR", {"message": f"Failed to checkout {branch}: {e}"}

    # Get last tag
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=collection_path,
            check=True,
            capture_output=True,
            text=True
        )
        last_tag = result.stdout.strip()
    except subprocess.CalledProcessError:
        return "ERROR", {"message": "No tags found"}

    # Count commits since tag
    try:
        result = subprocess.run(
            ["git", "log", f"{last_tag}..HEAD", "--oneline"],
            cwd=collection_path,
            check=True,
            capture_output=True,
            text=True
        )
        commit_count = len([l for l in result.stdout.splitlines() if l.strip()])
    except subprocess.CalledProcessError:
        commit_count = 0

    if commit_count == 0:
        return "UP_TO_DATE", {"current_version": last_tag}

    # Check for changelog fragments
    fragments_dir = collection_path / "changelogs" / "fragments"
    if not fragments_dir.exists():
        return "NO_FRAGMENTS", {"current_version": last_tag, "commit_count": commit_count}

    fragments = list(fragments_dir.glob("*.yml"))
    # Exclude .keep files
    fragments = [f for f in fragments if f.name != ".keep"]

    if not fragments:
        return "NO_FRAGMENTS", {"current_version": last_tag, "commit_count": commit_count}

    # Analyze fragment impact
    max_impact = "PATCH"
    fragment_details = []

    for fragment in fragments:
        try:
            with open(fragment, encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data:
                continue

            # Determine impact
            if "breaking_changes" in data or "removed_features" in data:
                max_impact = "MAJOR"
                impact = "MAJOR"
            elif any(k in data for k in ["major_changes", "minor_changes", "deprecated_features"]):
                if max_impact != "MAJOR":
                    max_impact = "MINOR"
                impact = "MINOR"
            else:
                impact = "PATCH"

            # Get fragment type
            frag_type = next((k for k in data.keys() if k != "release_summary"), None)
            fragment_details.append(f"{fragment.name}: {frag_type} (impact: {impact})")

        except Exception as e:
            print(f"{colors.YELLOW}Warning: Could not parse {fragment.name}: {e}{colors.RESET}", file=sys.stderr)

    # Calculate next version (handle optional 'v' prefix like v1.0.0)
    version_match = re.match(r'v?(\d+)\.(\d+)\.(\d+)', last_tag)
    if not version_match:
        return "ERROR", {"message": f"Invalid version format: {last_tag}"}

    major, minor, patch = map(int, version_match.groups())

    if max_impact == "MAJOR":
        next_version = f"{major + 1}.0.0"
    elif max_impact == "MINOR":
        next_version = f"{major}.{minor + 1}.0"
    else:  # PATCH
        next_version = f"{major}.{minor}.{patch + 1}"

    return "NEEDS_RELEASE", {
        "current_version": last_tag,
        "next_version": next_version,
        "impact": max_impact,
        "commit_count": commit_count,
        "fragment_count": len(fragments),
        "fragment_details": fragment_details
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Analyze collection for pending releases")
    parser.add_argument("collection", nargs="?", default=".", help="Collection name (namespace.name) or path")
    args = parser.parse_args()

    # Determine collection path
    if re.match(r'^[a-z]+\.[a-z_]+$', args.collection):
        collection_path = setup_collection_repo(args.collection)
    else:
        collection_path = Path(args.collection).resolve()

    # Get collection info
    info = get_collection_info(collection_path)
    print(f"Collection: {info['namespace']}.{info['name']}")
    print(f"Current version: {info['version']}")
    print()

    # Get stable branches
    branches = get_stable_branches(collection_path)

    if not branches:
        print("No stable branches found")
        return 0

    print(f"Stable branches found: {len(branches)}")
    print()

    # Check each branch
    release_count = 0

    for branch in branches:
        print(f"Checking {branch}...", file=sys.stderr)

        status, details = check_branch(branch, collection_path)

        if status == "NEEDS_RELEASE":
            print(f"{colors.GREEN}✅{colors.RESET} {branch}: {details['current_version']} → {details['next_version']} ({details['impact']})")
            print(f"   Commits: {details['commit_count']}, Fragments: {details['fragment_count']}")
            for frag in details['fragment_details']:
                print(f"   {frag}")
            print()
            release_count += 1

        elif status == "UP_TO_DATE":
            print(f"{colors.BLUE}✓{colors.RESET} {branch}: Up to date ({details['current_version']})")
            print()

        elif status == "NO_FRAGMENTS":
            print(f"{colors.YELLOW}⚠️{colors.RESET}  {branch}: {details['commit_count']} commits but no changelog fragments")
            print()

        elif status == "ERROR":
            print(f"{colors.RED}❌{colors.RESET} {branch}: {details['message']}")
            print()

    print(f"{colors.BOLD}{'━' * 50}{colors.RESET}")
    print(f"Summary: {release_count} release(s) needed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
