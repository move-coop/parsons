#!/usr/bin/env python
"""Verify that every ``*_legacy.py`` suite still matches the upstream original.

During the test-refactor migration each connector's pre-migration suite is kept
as ``test_<connector>_legacy.py`` and runs alongside the new suite through the
"bake" (see docs/contrib_docs/write_tests.rst). That only has value if the legacy
file is the *frozen original*. But because each ``*_legacy.py`` is a **new path**,
git shows it as an addition, so ordinary ``git diff`` can't tell you whether it
still matches the test it was copied from — or was quietly edited.

This tool reconstructs that comparison. For every ``*_legacy.py`` it finds the
corresponding original on a baseline ref (default ``upstream/main`` — the real
"before" this PR merges into), and checks that the two differ **only** by the
sanctioned bake edits:

* the ``pytestmark = pytest.mark.legacy`` marker (and an ``import pytest`` for it),
* import-path changes (bare data-module imports become package-qualified, and the
  reordering that implies),
* an added module docstring / comment header noting the file is legacy.

Anything else — a changed assertion, a dropped test, a tweaked mock — is real
drift and is reported. Comparison is logic-only: docstrings, comments, imports,
blank lines, and the marker are normalized away before diffing, so only the test
code itself has to match.

Usage::

    uv run python test/tools/verify_legacy.py                 # check all, vs upstream/main
    uv run python test/tools/verify_legacy.py --base 1aac3ee  # against a specific ref
    uv run python test/tools/verify_legacy.py --verbose       # show the drift diff

Exit code is 1 if any legacy file has drift (or no original was found), else 0 —
so it can gate CI during the bake. It becomes obsolete at the "contract" step,
when the legacy files are deleted.
"""

import argparse
import ast
import difflib
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = "pytestmark = pytest.mark.legacy"


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def _show(ref_path: str) -> str | None:
    r = _git("show", ref_path)
    return r.stdout if r.returncode == 0 else None


def legacy_files() -> list[str]:
    out = _git("ls-files", "test/**/*_legacy.py", "test/*_legacy.py").stdout
    return sorted(line for line in out.splitlines() if line.endswith("_legacy.py"))


def find_original(legacy_path: str, base: str) -> str | None:
    """Map a ``*_legacy.py`` path to its original on ``base``.

    Tries the dir-sibling (``test_<area>.py``) first, then a flat
    ``test/test_<connector>.py`` for connectors that had no directory.
    """
    candidates = [legacy_path[: -len("_legacy.py")] + ".py"]
    parts = legacy_path.split("/")
    if len(parts) >= 3:  # test/test_<connector>/...
        candidates.append(f"test/{parts[1]}.py")
    for cand in candidates:
        if _git("cat-file", "-e", f"{base}:{cand}").returncode == 0:
            return cand
    return None


def normalize(src: str) -> list[str]:
    """Reduce source to comparable test logic: drop the leading module docstring,
    all imports, the legacy marker, comments, and blank lines.
    """
    doc_lines: set[int] = set()
    try:
        tree = ast.parse(src)
        first = tree.body[0] if tree.body else None
        if (
            isinstance(first, ast.Expr)
            and isinstance(getattr(first, "value", None), ast.Constant)
            and isinstance(first.value.value, str)
        ):
            doc_lines = set(range(first.lineno, (first.end_lineno or first.lineno) + 1))
    except SyntaxError:
        pass

    kept: list[str] = []
    for lineno, line in enumerate(src.split("\n"), start=1):
        if lineno in doc_lines:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith(("import ", "from ")):
            continue
        if stripped == MARKER:
            continue
        kept.append(stripped)
    return kept


def check(base: str, verbose: bool) -> int:
    files = legacy_files()
    faithful, drifted, missing = [], [], []

    for legacy in files:
        original = find_original(legacy, base)
        if original is None:
            missing.append(legacy)
            continue
        orig_src = _show(f"{base}:{original}")
        legacy_src = (REPO / legacy).read_text()
        if normalize(orig_src) == normalize(legacy_src):
            faithful.append(legacy)
        else:
            drifted.append((legacy, original))

    print(f"Checked {len(files)} legacy files against {base}")
    print(f"  faithful (sanctioned edits only): {len(faithful)}")
    print(f"  DRIFTED (real changes):           {len(drifted)}")
    print(f"  NO ORIGINAL on base:              {len(missing)}")

    for legacy in missing:
        print(f"\n[no original] {legacy}\n  no matching test found on {base}")

    for legacy, original in drifted:
        print(f"\n[drift] {legacy}\n  vs {base}:{original}")
        if verbose:
            diff = difflib.unified_diff(
                normalize(_show(f"{base}:{original}")),
                normalize((REPO / legacy).read_text()),
                fromfile=f"{base}:{original} (logic)",
                tofile=f"{legacy} (logic)",
                lineterm="",
            )
            for line in diff:
                print("    " + line)

    return 1 if (drifted or missing) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--base",
        default="upstream/main",
        help="git ref holding the original tests (default: upstream/main)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print the normalized-logic diff for each drifted file",
    )
    args = parser.parse_args(argv)
    return check(args.base, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
