#!/usr/bin/env python3
"""
Calculate next version based on changelog fragments using SemVer rules.

Usage:
    ./calculate-version.py <current_version> <fragments_dir>

Output format:
    IMPACT|NEXT_VERSION|FRAGMENT_COUNT
    Example: MINOR|1.1.0|3
"""

import re
import sys
from pathlib import Path
from typing import Tuple


def parse_version(version: str) -> Tuple[int, int, int]:
    """
    Parse version string into major, minor, patch components.

    Args:
        version: Version string (e.g., "1.0.0", "1.0.0-dev")

    Returns:
        Tuple of (major, minor, patch)
    """
    # Remove -dev suffix if present
    version_clean = version.split('-')[0]

    parts = version_clean.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")

    try:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2])
        return major, minor, patch
    except ValueError as e:
        raise ValueError(f"Invalid version format: {version}") from e


def analyze_fragments(fragments_dir: Path) -> Tuple[str, int, list]:
    """
    Analyze changelog fragments to determine SemVer impact.

    Args:
        fragments_dir: Directory containing fragment YAML files

    Returns:
        Tuple of (max_impact, fragment_count, fragment_details)
    """
    if not fragments_dir.exists() or not fragments_dir.is_dir():
        return "NONE", 0, []

    # Find all fragment files
    fragment_files = [
        f for f in fragments_dir.glob("*.yml")
        if f.name != ".keep"
    ] + [
        f for f in fragments_dir.glob("*.yaml")
        if f.name != ".keep"
    ]

    if not fragment_files:
        return "NONE", 0, []

    max_impact = "PATCH"
    fragment_details = []

    # SemVer impact keywords
    major_keywords = ['breaking_changes', 'removed_features']
    minor_keywords = ['major_changes', 'minor_changes', 'deprecated_features']

    for fragment_file in fragment_files:
        try:
            content = fragment_file.read_text()
            fragment_types = []

            # Check for MAJOR impact keywords
            for keyword in major_keywords:
                if re.search(rf'^{keyword}:', content, re.MULTILINE):
                    max_impact = "MAJOR"
                    fragment_types.append(keyword)

            # Check for MINOR impact keywords (if not already MAJOR)
            if max_impact != "MAJOR":
                for keyword in minor_keywords:
                    if re.search(rf'^{keyword}:', content, re.MULTILINE):
                        if max_impact != "MAJOR":
                            max_impact = "MINOR"
                        fragment_types.append(keyword)

            # If no major/minor, it's PATCH (bugfixes, trivial, etc)
            if not fragment_types:
                # Extract any fragment types present
                matches = re.findall(r'^([a-z_]+):', content, re.MULTILINE)
                fragment_types = list(set(matches))

            impact = max_impact if fragment_types else "PATCH"
            fragment_details.append({
                'file': fragment_file.name,
                'types': fragment_types,
                'impact': impact
            })

        except Exception as e:
            print(f"Warning: Could not read fragment {fragment_file.name}: {e}", file=sys.stderr)
            continue

    return max_impact, len(fragment_files), fragment_details


def calculate_next_version(current_version: str, impact: str) -> str:
    """
    Calculate next version based on SemVer impact.

    Args:
        current_version: Current version string
        impact: MAJOR, MINOR, or PATCH

    Returns:
        Next version string
    """
    major, minor, patch = parse_version(current_version)

    if impact == "MAJOR":
        return f"{major + 1}.0.0"
    elif impact == "MINOR":
        return f"{major}.{minor + 1}.0"
    else:  # PATCH
        return f"{major}.{minor}.{patch + 1}"


def main() -> int:
    """Main entry point."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <current_version> <fragments_dir>", file=sys.stderr)
        return 1

    current_version = sys.argv[1]
    fragments_dir = Path(sys.argv[2])

    try:
        # Analyze fragments
        impact, fragment_count, fragment_details = analyze_fragments(fragments_dir)

        # Print fragment details to stderr
        for detail in fragment_details:
            types_str = ', '.join(detail['types'])
            print(f"  {detail['file']}: {types_str} (impact: {detail['impact']})", file=sys.stderr)

        # Calculate next version
        if impact == "NONE":
            next_version = current_version
        else:
            next_version = calculate_next_version(current_version, impact)

        # Output format: IMPACT|NEXT_VERSION|FRAGMENT_COUNT
        print(f"{impact}|{next_version}|{fragment_count}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
