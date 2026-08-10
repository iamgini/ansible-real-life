#!/usr/bin/env python3
"""Validate that every Lola module has the required directory structure.

Auto-discovers modules by finding top-level directories that contain
a ``module/`` subdirectory.

Required layout per module::

    <module-name>/
    └── module/
        ├── AGENTS.md
        ├── mcps.json
        ├── skills/          (required)
        ├── commands/        (optional)
        └── agents/          (optional)
"""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_FILES = ["AGENTS.md", "mcps.json"]
REQUIRED_DIRS = ["skills"]


def discover_modules(root: Path) -> list[Path]:
    """Return top-level directories that contain a ``module/`` subdirectory."""
    return sorted(
        d
        for d in root.iterdir()
        if d.is_dir() and not d.name.startswith(".") and (d / "module").is_dir()
    )


def check_module(module_dir: Path) -> list[str]:
    """Return error messages for missing required files and directories."""
    module_path = module_dir / "module"
    errors = [
        f"{module_dir.name}/module/{f} missing"
        for f in REQUIRED_FILES
        if not (module_path / f).is_file()
    ]
    errors.extend(
        f"{module_dir.name}/module/{d}/ missing"
        for d in REQUIRED_DIRS
        if not (module_path / d).is_dir()
    )
    return errors


def main() -> int:
    """Discover all Lola modules and validate their structure."""
    root = Path()
    modules = discover_modules(root)

    if not modules:
        print("No Lola modules found (no */module/ directories)")
        return 1

    all_errors: list[str] = []
    for module_dir in modules:
        all_errors.extend(check_module(module_dir))

    if all_errors:
        print("Module structure errors:")
        for error in all_errors:
            print(f"  - {error}")
        return 1

    print(f"All {len(modules)} modules have valid structure")
    return 0


if __name__ == "__main__":
    sys.exit(main())
