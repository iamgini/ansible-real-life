#!/usr/bin/env python3
"""Validate network-collection-triage JSON output against the shared schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from jsonschema.exceptions import ValidationError
except ImportError as exc:  # pragma: no cover - runtime guard for missing dep
    print(
        "error: jsonschema is required. Install with: pip install jsonschema",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


DEFAULT_SCHEMA = (
    Path(__file__).resolve().parent.parent / "schema" / "triage-report.schema.json"
)


def load_json(path: Path | None, label: str) -> Any:
    """Load JSON from a file path, or from stdin when path is None."""
    try:
        if path is None:
            return json.load(sys.stdin)
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {label}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except OSError as exc:
        print(f"error: cannot read {label}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def load_schema(schema_path: Path) -> dict[str, Any]:
    """Load the JSON Schema document."""
    schema = load_json(schema_path, str(schema_path))
    if not isinstance(schema, dict):
        print("error: schema root must be a JSON object", file=sys.stderr)
        raise SystemExit(1)
    return schema


def check_statistics_consistency(document: dict[str, Any]) -> list[str]:
    """Apply completeness checks described in the skill beyond JSON Schema."""
    errors: list[str] = []

    statistics = document.get("statistics", {})
    repositories = document.get("repositories", [])

    issue_count = sum(len(repo.get("issues", [])) for repo in repositories)
    pr_count = sum(len(repo.get("pullRequests", [])) for repo in repositories)

    expected_issues = statistics.get("totalIssues")
    if isinstance(expected_issues, int) and issue_count != expected_issues:
        errors.append(
            "statistics.totalIssues "
            f"({expected_issues}) does not match sum of repositories[].issues "
            f"({issue_count})"
        )

    expected_prs = statistics.get("totalPrs")
    if isinstance(expected_prs, int) and pr_count != expected_prs:
        errors.append(
            "statistics.totalPrs "
            f"({expected_prs}) does not match sum of repositories[].pullRequests "
            f"({pr_count})"
        )

    for repo in repositories:
        name = repo.get("name", "<unknown>")
        ci_status = repo.get("ci-status")
        if ci_status is None or not isinstance(ci_status, dict):
            continue

        pass_count = ci_status.get("passCount")
        runs = ci_status.get("runs", [])
        if isinstance(pass_count, int) and isinstance(runs, list):
            success_count = sum(
                1 for run in runs if isinstance(run, dict) and run.get("conclusion") == "success"
            )
            if pass_count != success_count:
                errors.append(
                    f"repositories[{name}].ci-status.passCount "
                    f"({pass_count}) does not match successful runs ({success_count})"
                )

        health = ci_status.get("health")
        if isinstance(pass_count, int) and isinstance(health, str):
            expected_health = (
                "green"
                if pass_count == 5
                else "yellow"
                if 3 <= pass_count <= 4
                else "red"
            )
            if health != expected_health:
                errors.append(
                    f"repositories[{name}].ci-status.health "
                    f"({health}) does not match passCount ({pass_count}); "
                    f"expected {expected_health}"
                )

    return errors


def format_validation_error(error: ValidationError) -> str:
    """Render a jsonschema ValidationError as a concise message."""
    path = ".".join(str(part) for part in error.absolute_path) or "<root>"
    return f"{path}: {error.message}"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a network-collection-triage JSON report against "
            "schema/triage-report.schema.json."
        )
    )
    parser.add_argument(
        "report",
        nargs="?",
        default="-",
        help="Path to the triage report JSON file (default: read from stdin)",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help=f"Path to JSON Schema file (default: {DEFAULT_SCHEMA})",
    )
    parser.add_argument(
        "--skip-consistency-checks",
        action="store_true",
        help="Skip post-schema completeness checks (issue/PR counts, CI health).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    schema = load_schema(args.schema)
    report_path = None if args.report == "-" else Path(args.report)
    report_label = "stdin" if report_path is None else str(report_path)
    document = load_json(report_path, report_label)

    if not isinstance(document, dict):
        print("error: report root must be a JSON object", file=sys.stderr)
        return 1

    validator = jsonschema.Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(document), key=lambda err: list(err.path))

    if schema_errors:
        print("Schema validation failed:", file=sys.stderr)
        for error in schema_errors:
            print(f"  - {format_validation_error(error)}", file=sys.stderr)
        return 1

    if not args.skip_consistency_checks:
        consistency_errors = check_statistics_consistency(document)
        if consistency_errors:
            print("Consistency validation failed:", file=sys.stderr)
            for message in consistency_errors:
                print(f"  - {message}", file=sys.stderr)
            return 1

    print(f"Valid triage report ({report_label}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
