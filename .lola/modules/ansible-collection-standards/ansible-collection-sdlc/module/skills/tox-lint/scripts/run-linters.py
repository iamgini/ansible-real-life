#!/usr/bin/env python3
"""Run all configured tox linters for Ansible collections."""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple


class Colors:
    """ANSI color codes for terminal output. Respects NO_COLOR environment variable."""

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


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{colors.BOLD}{'━' * 60}{colors.RESET}")
    print(f"{colors.BOLD}{text}{colors.RESET}")
    print(f"{colors.BOLD}{'━' * 60}{colors.RESET}\n")


def print_step(step: str, total: int, current: int, message: str) -> None:
    """Print a step in the workflow."""
    print(f"{colors.CYAN}[{current}/{total}]{colors.RESET} {message}...")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"  {colors.GREEN}✅{colors.RESET} {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{colors.RED}❌ Error: {message}{colors.RESET}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{colors.YELLOW}⚠️  {message}{colors.RESET}")


def setup_venv(collection_path: Path) -> bool:
    """Set up Python virtual environment with tox."""
    # Create venv if it doesn't exist
    venv_path = collection_path / ".venv"
    if not venv_path.exists():
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            pass  # May already exist

    # Activate venv and install tox
    if sys.platform == "win32":
        pip_cmd = str(venv_path / "Scripts" / "pip")
        python_cmd = str(venv_path / "Scripts" / "python")
    else:
        pip_cmd = str(venv_path / "bin" / "pip")
        python_cmd = str(venv_path / "bin" / "python")

    # Check if uv is available for faster installation
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        has_uv = True
        print("  Using uv for fast installation...", file=sys.stderr)
    except (subprocess.CalledProcessError, FileNotFoundError):
        has_uv = False
        print("  Using pip...", file=sys.stderr)

    if has_uv:
        cmd = ["uv", "pip", "install", "--python", python_cmd, "tox"]
    else:
        # Upgrade pip first
        subprocess.run([pip_cmd, "install", "--quiet", "--upgrade", "pip"],
                      check=True, capture_output=True)
        cmd = [pip_cmd, "install", "--quiet", "tox"]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install tox: {e}")
        return False


def determine_tox_command(collection_path: Path) -> str:
    """Determine which tox command to run based on tox.ini."""
    tox_ini = collection_path / "tox.ini"

    try:
        content = tox_ini.read_text()

        # Try label-based first (tox -m lint)
        if "labels" in content and "lint" in content:
            return "tox -m lint"
        # Then check for linters environment
        elif "[testenv:linters]" in content:
            return "tox -e linters"
        else:
            # Use default envlist
            return "tox"
    except Exception:
        return "tox"


def run_linters(collection_path: Path) -> Tuple[bool, float, str]:
    """Run tox linters and return success status, duration, and output."""
    venv_path = collection_path / ".venv"

    if sys.platform == "win32":
        tox_cmd = str(venv_path / "Scripts" / "tox")
    else:
        tox_cmd = str(venv_path / "bin" / "tox")

    # Determine tox command
    tox_args = determine_tox_command(collection_path).split()[1:]  # Remove 'tox' prefix
    cmd = [tox_cmd] + tox_args

    print(f"  Running: {' '.join(cmd)}", file=sys.stderr)

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=collection_path,
            capture_output=True,
            text=True
        )
        duration = time.time() - start_time

        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        return result.returncode == 0, duration, result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        return False, duration, str(e)


def detect_auto_fixable(output: str) -> bool:
    """Detect if linter failures can be auto-fixed."""
    auto_fixable_linters = ["black", "isort", "flynt", "ruff"]

    for linter in auto_fixable_linters:
        if linter in output.lower() and "fail" in output.lower():
            return True

    return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run tox linters for Ansible collections"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to collection directory (default: current directory)"
    )

    args = parser.parse_args()
    collection_path = Path(args.path).resolve()

    # Verify we're in a collection
    tox_ini = collection_path / "tox.ini"
    if not tox_ini.exists():
        print_error(f"tox.ini not found in {collection_path}")
        return 2

    print_header("Running Linters")

    # Step 1: Setup venv
    print_step("Setting up virtual environment", 2, 1, "Setting up virtual environment")
    if not setup_venv(collection_path):
        return 1
    print_success("Virtual environment ready")

    # Step 2: Run linters
    print()
    print_step("Running tox linters", 2, 2, "Running tox linters")

    success, duration, output = run_linters(collection_path)

    print()
    print(f"{colors.BOLD}{'━' * 60}{colors.RESET}")

    if success:
        print(f"{colors.GREEN}{colors.BOLD}All linters passed! ✨{colors.RESET}")
        print(f"{colors.BOLD}{'━' * 60}{colors.RESET}")
        print(f"Total time: {duration:.1f}s")
        return 0
    else:
        print(f"{colors.RED}{colors.BOLD}Linters failed!{colors.RESET}")
        print(f"{colors.BOLD}{'━' * 60}{colors.RESET}\n")

        # Check if auto-fixable
        if detect_auto_fixable(output):
            print("Some failures can be auto-fixed:")
            print(f"  {colors.CYAN}➤{colors.RESET} Run: {colors.BOLD}/lint-fix{colors.RESET}")
            print(f"  {colors.CYAN}➤{colors.RESET} Then re-run: {colors.BOLD}/lint{colors.RESET}")
        else:
            print("Manual fixes required:")
            print(f"  {colors.CYAN}➤{colors.RESET} Review output above")
            print(f"  {colors.CYAN}➤{colors.RESET} Fix issues and re-run: {colors.BOLD}/lint{colors.RESET}")

        print(f"\nTotal time: {duration:.1f}s")
        return 1


if __name__ == "__main__":
    sys.exit(main())
