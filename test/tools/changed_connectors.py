#!/usr/bin/env python
"""Emit the connectors a change set affects that also have a committed baseline.

Used by CI to scope the (slow) mutation-parity run to just the connectors a pull
request touches. A connector is *affected* if any changed file lives under its
source path or its test path. Only connectors with a baseline
(``test/baselines/<name>.json``) are emitted, since ``parity.py compare`` needs
one to compare against.

Usage::

    # connectors changed in this PR (relative to a base ref) that have a baseline
    python test/tools/changed_connectors.py --base origin/main

    # every connector that has a baseline (for the scheduled full sweep)
    python test/tools/changed_connectors.py --all

Prints one connector name per line (empty output = nothing to do).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import connector_map
from connector_map import REPO_ROOT

BASELINE_DIR = REPO_ROOT / "test" / "baselines"


def baselined_connectors() -> list[str]:
    """All connector names with a committed baseline."""
    return sorted(p.stem for p in BASELINE_DIR.glob("*.json"))


def changed_files(base: str) -> list[str]:
    """Repo-relative paths changed between ``base`` and HEAD."""
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [line.strip() for line in out.splitlines() if line.strip()]


def _under(path: str, base: str) -> bool:
    """True if ``path`` is ``base`` (a file) or lives under ``base`` (a dir)."""
    base = base.rstrip("/")
    return path == base or path.startswith(base + "/")


def affected(base: str) -> list[str]:
    files = changed_files(base)
    result = []
    for name in baselined_connectors():
        conn = connector_map.resolve(name)
        if any(_under(f, conn.source_path) or _under(f, conn.test_path) for f in files):
            result.append(name)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="every baselined connector")
    group.add_argument("--base", help="git ref to diff HEAD against (e.g. origin/main)")
    args = parser.parse_args(argv)

    names = baselined_connectors() if args.all else affected(args.base)
    print("\n".join(names))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
