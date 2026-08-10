#!/usr/bin/env python3
"""Validate that every module with skills is listed in lola-market.yml.

Auto-discovers modules by finding directories that match
``*/module/skills/*/SKILL.md``, then verifies each is present
in the manifest with the correct path.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

MANIFEST = "lola-market.yml"

# YAML manifests are untyped at parse time; we narrow within each function.
_YAMLDict = dict[str, object]
_ModuleEntry = dict[str, str]


def discover_skill_modules(root: Path) -> set[str]:
    """Return module directory names that contain at least one skill."""
    modules: set[str] = set()
    for skill_file in root.glob("*/module/skills/*/SKILL.md"):
        module_name = skill_file.parts[0]
        modules.add(module_name)
    return modules


def load_manifest(root: Path) -> _YAMLDict:
    """Load and return the parsed lola-market.yml manifest."""
    manifest_path = root / MANIFEST
    if not manifest_path.is_file():
        return {}
    result: _YAMLDict = (
        yaml.safe_load(
            manifest_path.read_text(encoding="utf-8"),
        )
        or {}
    )
    return result


def main() -> int:
    """Check that every module with skills appears in the manifest."""
    root = Path()
    skill_modules = discover_skill_modules(root)

    if not skill_modules:
        print("No modules with skills found")
        return 0

    manifest = load_manifest(root)
    modules_list: list[_ModuleEntry] = manifest.get("modules", [])  # type: ignore[assignment]
    manifest_modules: dict[str, _ModuleEntry] = {m["name"]: m for m in modules_list}

    errors: list[str] = []
    for module_name in sorted(skill_modules):
        if module_name not in manifest_modules:
            errors.append(f"'{module_name}' has skills but is not listed in {MANIFEST}")
            continue

        expected_path = f"{module_name}/module"
        actual_path = manifest_modules[module_name].get("path", "")
        if actual_path != expected_path:
            errors.append(
                f"'{module_name}' path in {MANIFEST} is '{actual_path}', "
                f"expected '{expected_path}'"
            )

    if errors:
        print("Manifest completeness errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"All {len(skill_modules)} modules with skills are in {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
