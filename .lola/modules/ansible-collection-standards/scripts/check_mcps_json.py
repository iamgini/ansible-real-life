#!/usr/bin/env python3
"""Validate that every mcps.json file has the required schema.

Checks all ``*/module/mcps.json`` files for:
- Valid JSON syntax
- A top-level ``mcpServers`` key
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    """Check all mcps.json files for valid JSON with a mcpServers key."""
    root = Path()
    mcps_files = sorted(root.glob("*/module/mcps.json"))

    if not mcps_files:
        print("No mcps.json files found")
        return 0

    errors: list[str] = []
    for mcps_file in mcps_files:
        try:
            data = json.loads(mcps_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{mcps_file}: invalid JSON — {exc}")
            continue

        if not isinstance(data, dict):
            errors.append(f"{mcps_file}: top-level value must be an object")
            continue

        if "mcpServers" not in data:
            errors.append(f"{mcps_file}: missing 'mcpServers' key")

    if errors:
        print("mcps.json schema errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"All {len(mcps_files)} mcps.json files have valid schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
