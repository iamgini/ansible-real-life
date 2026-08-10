#!/usr/bin/env python3
"""
Update galaxy.yml version field.

Usage:
    ./update-galaxy-version.py <new_version> [galaxy_file]

Output format:
    CURRENT_VERSION|NEW_VERSION
"""

import os
import re
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output. Respects NO_COLOR environment variable."""

    def __init__(self):
        # Disable colors if NO_COLOR environment variable is set
        if os.environ.get('NO_COLOR'):
            self.RESET = ''
            self.RED = ''
        else:
            self.RESET = '\033[0m'
            self.RED = '\033[91m'


# Global Colors instance
colors = Colors()


def update_galaxy_version(new_version: str, galaxy_file: Path) -> tuple:
    """
    Update version in galaxy.yml file.

    Args:
        new_version: New version string
        galaxy_file: Path to galaxy.yml

    Returns:
        Tuple of (current_version, new_version)
    """
    if not galaxy_file.exists():
        print(f"{colors.RED}Error: {galaxy_file} not found{colors.RESET}", file=sys.stderr)
        sys.exit(1)

    # Read file
    content = galaxy_file.read_text()

    # Find current version
    match = re.search(r'^version:\s+(.+)$', content, re.MULTILINE)
    if not match:
        print(f"{colors.RED}Error: Could not find version in {galaxy_file}{colors.RESET}", file=sys.stderr)
        sys.exit(1)

    current_version = match.group(1)

    # Update version
    updated_content = re.sub(
        r'^version:\s+.+$',
        f'version: {new_version}',
        content,
        count=1,
        flags=re.MULTILINE
    )

    # Write back
    galaxy_file.write_text(updated_content)

    return current_version, new_version


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <new_version> [galaxy_file]", file=sys.stderr)
        return 1

    new_version = sys.argv[1]
    galaxy_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("galaxy.yml")

    try:
        current_version, new_version = update_galaxy_version(new_version, galaxy_file)
        print(f"{current_version}|{new_version}")
        return 0
    except Exception as e:
        print(f"{colors.RED}Error: {e}{colors.RESET}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
