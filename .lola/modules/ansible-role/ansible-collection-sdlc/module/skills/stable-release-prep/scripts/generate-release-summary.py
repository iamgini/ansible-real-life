#!/usr/bin/env python3
"""
Generate release summary fragment from existing changelog fragments.

Usage:
    ./generate-release-summary.py <collection_path> <version>
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Set


class Colors:
    """ANSI color codes for terminal output. Respects NO_COLOR environment variable."""

    def __init__(self):
        # Disable colors if NO_COLOR environment variable is set
        if os.environ.get('NO_COLOR'):
            self.RESET = ''
            self.YELLOW = ''
        else:
            self.RESET = '\033[0m'
            self.YELLOW = '\033[93m'


# Global Colors instance
colors = Colors()


def get_modules_from_fragments(fragments_dir: Path) -> List[str]:
    """
    Extract module names mentioned in changelog fragments.

    Args:
        fragments_dir: Path to fragments directory

    Returns:
        List of module names mentioned in fragments
    """
    fragment_files = [
        f for f in fragments_dir.glob("*.yml")
        if f.name != ".keep"
    ] + [
        f for f in fragments_dir.glob("*.yaml")
        if f.name != ".keep"
    ]

    modules = set()

    for fragment_file in fragment_files:
        try:
            content = fragment_file.read_text(encoding='utf-8')

            # Extract module names from fragment entries
            # Pattern: "module_name - description" or "module_name-description"
            # Look for lines under bugfixes, minor_changes, etc.
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    # Remove leading "- "
                    line = line[2:].strip()
                    # Extract module name (everything before first space or dash)
                    match = re.match(r'^([a-z][a-z0-9_]*)\s*-', line)
                    if match:
                        module_name = match.group(1)
                        modules.add(module_name)
        except Exception:
            continue

    return sorted(modules)


def analyze_fragment_types(fragments_dir: Path) -> dict:
    """
    Analyze fragment types to determine release characteristics.

    Args:
        fragments_dir: Path to fragments directory

    Returns:
        Dict with boolean flags for each fragment type
    """
    fragment_files = [
        f for f in fragments_dir.glob("*.yml")
        if f.name != ".keep"
    ] + [
        f for f in fragments_dir.glob("*.yaml")
        if f.name != ".keep"
    ]

    types = {
        'breaking': False,
        'major': False,
        'minor': False,
        'bugfixes': False,
        'trivial': False
    }

    for fragment_file in fragment_files:
        try:
            content = fragment_file.read_text(encoding='utf-8')

            if re.search(r'^(breaking_changes|removed_features):', content, re.MULTILINE):
                types['breaking'] = True

            if re.search(r'^major_changes:', content, re.MULTILINE):
                types['major'] = True

            if re.search(r'^(minor_changes|deprecated_features):', content, re.MULTILINE):
                types['minor'] = True

            if re.search(r'^bugfixes:', content, re.MULTILINE):
                types['bugfixes'] = True

            if re.search(r'^trivial:', content, re.MULTILINE):
                types['trivial'] = True

        except Exception:
            continue

    return types


def generate_summary(types: dict, modules: List[str]) -> str:
    """
    Generate release summary text based on fragment types and modules.

    Args:
        types: Dict of fragment type flags
        modules: List of changed module names

    Returns:
        Release summary text
    """
    # Format module list with backticks
    if modules:
        module_list = ', '.join([f'``{m}``' for m in modules])
        module_text = f"the {module_list} module(s)"
    else:
        module_text = ""

    # Generate summary based on types
    if types['breaking']:
        if module_text:
            summary = f"This major release includes breaking changes affecting {module_text}. Please review the changelog for migration guidance."
        else:
            summary = "This major release includes breaking changes. Please review the changelog for migration guidance."

    elif types['major'] or types['minor']:
        if module_text:
            summary = f"This minor release adds new features and improvements to {module_text}."
        else:
            summary = "This minor release adds new features and improvements."

    elif types['bugfixes']:
        if module_text:
            summary = f"This patch release includes bugfixes for {module_text}."
        else:
            summary = "This patch release includes bugfixes."

    else:
        summary = "This release includes maintenance updates and improvements."

    return summary


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <collection_path> <version>", file=sys.stderr)
        return 1

    collection_path = Path(sys.argv[1])
    version = sys.argv[2]

    # Derive fragments directory from collection path
    fragments_dir = collection_path / "changelogs" / "fragments"
    output_file = fragments_dir / f"{version}.yml"

    if not fragments_dir.exists():
        print(f"{colors.YELLOW}Warning: Fragments directory not found: {fragments_dir}{colors.RESET}", file=sys.stderr)
        # Create minimal summary
        summary = "This release includes maintenance updates and improvements."
    else:
        # Analyze fragments
        types = analyze_fragment_types(fragments_dir)

        # Get modules mentioned in fragments
        modules = get_modules_from_fragments(fragments_dir)

        # Generate summary
        summary = generate_summary(types, modules)

    # Create release summary fragment
    # Use folded block scalar with strip (>-) to avoid blank lines and quotes in changelog.yaml
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(f"release_summary: >-\n  {summary}\n", encoding='utf-8')

    print(summary)
    print(f"Created: {output_file}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
