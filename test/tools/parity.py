#!/usr/bin/env python
"""Per-connector test-quality parity: coverage + mutation score.

This is the measurement tool behind the test-refactor migration process
(see docs/write_tests.rst, "Migrating an existing connector"). It answers the
question that "all tests green" cannot: **is the new test suite at least as
strong as the old one?**

It measures two things, scoped to a single connector's source module:

* **coverage** — line % and branch % (does the test suite execute the code?)
* **mutation score** — % of injected faults the suite catches (does it actually
  *assert* on behavior?). Coverage can be 100% while assertions are gutted; a
  no-op assertion like ``assert len(x), len(y)`` covers the line but kills no
  mutants. Mutation score is what catches that.

Usage::

    # 1. Before migrating a connector, capture a baseline from the OLD suite:
    python test/tools/parity.py capture airtable

    # 2. After migrating, confirm the NEW suite has not regressed:
    python test/tools/parity.py compare airtable            # advisory (never fails)
    python test/tools/parity.py compare airtable --strict   # exit 1 on regression

Baselines are written to ``test/baselines/<connector>.json`` and committed, so
the comparison survives deletion of the old suite. Run everything through the
project venv (``uv run python test/tools/parity.py ...``).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

# Allow running as a script (python test/tools/parity.py) or as a module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import connector_map
from connector_map import REPO_ROOT, Connector

BASELINE_DIR = REPO_ROOT / "test" / "baselines"
EPS = 0.01  # float tolerance for the (deterministic) coverage metrics
# Mutation score is not perfectly deterministic: cosmic-ray classifies a mutant
# that hangs as "killed" via a timeout, and whether a slow mutant trips the
# timeout can vary a little run to run. Allow a small tolerance so that noise
# alone never reports a regression. Coverage stays strict.
MUTATION_EPS = 2.0

# The cosmic-ray console script sits next to the interpreter; resolve it directly
# so it is found regardless of whether the venv's bin dir is on PATH.
CR_BIN = str(Path(sys.executable).parent / "cosmic-ray")


class NoCoverageData(Exception):
    """A connector's suite ran no measurable code (all tests skipped or none collected).

    Nothing can be baselined in that case — it is a clean skip, not an error.
    """


@dataclass
class CoverageResult:
    line_pct: float
    branch_pct: float
    num_statements: int
    num_branches: int


@dataclass
class MutationResult:
    score_pct: float
    killed: int
    survived: int
    total: int


@dataclass
class Survivor:
    """A mutation no test caught — i.e. a behavior nothing asserts on."""

    path: str
    line: int
    operator: str
    source: str


# --------------------------------------------------------------------------- #
# Measurement
# --------------------------------------------------------------------------- #


def measure_coverage(conn: Connector) -> CoverageResult:
    """Run the connector's tests under coverage scoped to its source module."""
    with tempfile.TemporaryDirectory() as tmp:
        json_path = Path(tmp) / "coverage.json"
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            conn.test_path,
            f"--cov={conn.cov_module}",
            "--cov-branch",
            f"--cov-report=json:{json_path}",
            "--cov-report=",  # suppress the terminal coverage table
            "-n0",  # disable xdist distribution for a deterministic measurement
            "-q",
            "-p",
            "no:cacheprovider",
        ]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        if not json_path.exists():
            combined = proc.stdout + proc.stderr
            no_data_signals = ("No data was collected", "no tests ran", "no tests collected")
            if proc.returncode == 5 or any(s in combined for s in no_data_signals):
                raise NoCoverageData(
                    f"no measurable tests for '{conn.name}' "
                    f"(all skipped or none collected in {conn.test_path})"
                )
            raise RuntimeError(
                f"coverage run for '{conn.name}' produced no report.\n"
                f"command: {' '.join(cmd)}\n"
                f"stdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}"
            )
        totals = json.loads(json_path.read_text())["totals"]

    num_statements = totals.get("num_statements", 0)
    num_branches = totals.get("num_branches", 0)
    line_pct = 100.0 * totals.get("covered_lines", 0) / num_statements if num_statements else 100.0
    branch_pct = 100.0 * totals.get("covered_branches", 0) / num_branches if num_branches else 100.0
    return CoverageResult(
        line_pct=round(line_pct, 2),
        branch_pct=round(branch_pct, 2),
        num_statements=num_statements,
        num_branches=num_branches,
    )


def _cosmic_ray_dump(conn: Connector) -> str:
    """Run a cosmic-ray session over the connector's source and return its JSON dump.

    cosmic-ray reads its own per-session config (no coupling to pyproject.toml),
    which makes per-connector scoping clean and robust. Each mutation is applied
    to the source on disk, this connector's tests run, and the file is restored.
    """
    test_command = f"{sys.executable} -m pytest -x -q -n0 -p no:cacheprovider {conn.test_path}"
    with tempfile.TemporaryDirectory() as tmp:
        config = Path(tmp) / "session.toml"
        session = Path(tmp) / "session.sqlite"
        config.write_text(
            "[cosmic-ray]\n"
            f'module-path = "{conn.source_path}"\n'
            "timeout = 60.0\n"
            "excluded-modules = []\n"
            f'test-command = "{test_command}"\n'
            "\n[cosmic-ray.distributor]\n"
            'name = "local"\n'
        )

        # Confirm the unmutated suite passes before mutating; a clean baseline is
        # a precondition for a meaningful score.
        baseline = subprocess.run(
            [CR_BIN, "baseline", str(config)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if baseline.returncode != 0:
            raise RuntimeError(
                f"mutation baseline for '{conn.name}' failed (tests do not pass "
                f"cleanly).\nstdout:\n{baseline.stdout}\n\nstderr:\n{baseline.stderr}"
            )

        for cmd in (
            [CR_BIN, "init", str(config), str(session)],
            [CR_BIN, "exec", str(config), str(session)],
        ):
            subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True)

        return subprocess.run(
            [CR_BIN, "dump", str(session)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout


def _iter_results(dump: str):
    """Yield (work_item, result) pairs from a cosmic-ray dump, skipping empties."""
    for line in dump.splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        result = record[1] if isinstance(record, list) and len(record) > 1 else None
        if result:
            yield record[0], result


def measure_mutation(conn: Connector) -> MutationResult:
    """Score the connector's tests by how many injected faults they catch."""
    killed = survived = 0
    for _work_item, result in _iter_results(_cosmic_ray_dump(conn)):
        outcome = result.get("test_outcome")
        if outcome == "killed":
            killed += 1
        elif outcome == "survived":
            survived += 1
        # anything else (e.g. an "incompetent" mutant that didn't compile) is
        # excluded from the score entirely

    scored = killed + survived
    score = 100.0 * killed / scored if scored else 100.0
    return MutationResult(score_pct=round(score, 2), killed=killed, survived=survived, total=scored)


def _source_line(path: str, line: int) -> str:
    """The stripped text of a source line, for annotating a survivor."""
    try:
        lines = (REPO_ROOT / path).read_text().splitlines()
        return lines[line - 1].strip() if 0 < line <= len(lines) else ""
    except OSError:
        return ""


def find_survivors(conn: Connector) -> list[Survivor]:
    """List the mutants this connector's tests fail to catch.

    Each survivor is a behavior you could change without any test noticing —
    i.e. a concrete missing assertion.
    """
    survivors = []
    for work_item, result in _iter_results(_cosmic_ray_dump(conn)):
        if result.get("test_outcome") != "survived":
            continue
        for mutation in work_item.get("mutations", []):
            path = mutation.get("module_path") or conn.source_path
            start = mutation.get("start_pos") or [0]
            line = start[0] if isinstance(start, list) else 0
            survivors.append(
                Survivor(
                    path=path,
                    line=line,
                    operator=mutation.get("operator_name", "?"),
                    source=_source_line(path, line),
                )
            )
    return sorted(survivors, key=lambda s: (s.path, s.line))


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #


def _resolve_or_exit(name: str) -> Connector:
    conn = connector_map.resolve(name)
    problems = connector_map.validate(conn)
    if problems:
        print(f"error: cannot resolve connector '{name}':", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(2)
    return conn


def cmd_capture(name: str, mutation: bool) -> int:
    conn = _resolve_or_exit(name)
    print(f"Capturing baseline for '{name}' ({conn.cov_module})...")
    cov = measure_coverage(conn)
    print(f"  coverage: line {cov.line_pct}%  branch {cov.branch_pct}%")

    payload: dict = {
        "connector": name,
        "git_sha": git_sha(),
        "source_path": conn.source_path,
        "cov_module": conn.cov_module,
        "test_path": conn.test_path,
        "coverage": asdict(cov),
    }
    if mutation:
        print("  running mutation testing (this can take several minutes)...")
        mut = measure_mutation(conn)
        print(f"  mutation: {mut.score_pct}%  ({mut.killed}/{mut.total} killed)")
        payload["mutation"] = asdict(mut)

    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    out = BASELINE_DIR / f"{name}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {out.relative_to(REPO_ROOT)}")
    return 0


def _render_text(rows: list[tuple[str, float, float]], regressions: list[str]) -> None:
    print()
    print(f"  {'metric':20} {'baseline':>10} {'current':>10} {'delta':>10}")
    print(f"  {'-' * 20} {'-' * 10:>10} {'-' * 10:>10} {'-' * 10:>10}")
    for label, base, cur in rows:
        delta = round(cur - base, 2)
        flag = "  <-- REGRESSION" if label in regressions else ""
        print(f"  {label:20} {base:>10} {cur:>10} {delta:>+10} {flag}")
    print()


def _render_markdown(
    name: str, rows: list[tuple[str, float, float]], regressions: list[str]
) -> None:
    """Emit a GitHub-flavored markdown table (for $GITHUB_STEP_SUMMARY)."""
    status = "⚠️ REGRESSION" if regressions else "✅ PASS"
    print(f"### Parity — `{name}` — {status}")
    print()
    print("| metric | baseline | current | delta |")
    print("| --- | ---: | ---: | ---: |")
    for label, base, cur in rows:
        delta = round(cur - base, 2)
        mark = " ⚠️" if label in regressions else ""
        print(f"| {label} | {base} | {cur} | {delta:+}{mark} |")
    print()


def cmd_compare(name: str, mutation: bool, strict: bool, markdown: bool = False) -> int:
    conn = _resolve_or_exit(name)
    # In markdown mode, progress goes to stderr so stdout stays clean for the summary.
    log = sys.stderr if markdown else sys.stdout

    baseline_path = BASELINE_DIR / f"{name}.json"
    if not baseline_path.exists():
        print(
            f"error: no baseline at {baseline_path.relative_to(REPO_ROOT)}. "
            f"Run: python test/tools/parity.py capture {name}",
            file=sys.stderr,
        )
        return 2
    baseline = json.loads(baseline_path.read_text())

    print(
        f"Comparing '{name}' against baseline (captured at {baseline.get('git_sha')})...", file=log
    )
    cov = measure_coverage(conn)
    rows = [
        ("line coverage %", baseline["coverage"]["line_pct"], cov.line_pct),
        ("branch coverage %", baseline["coverage"]["branch_pct"], cov.branch_pct),
    ]

    has_mut_baseline = "mutation" in baseline
    if mutation and has_mut_baseline:
        print("  running mutation testing (this can take several minutes)...", file=log)
        mut = measure_mutation(conn)
        rows.append(("mutation score %", baseline["mutation"]["score_pct"], mut.score_pct))
    elif mutation and not has_mut_baseline:
        print("  (baseline has no mutation score; skipping mutation comparison)", file=log)

    # Coverage is compared strictly; mutation gets a small tolerance for its
    # run-to-run timeout noise (see MUTATION_EPS).
    tolerances = {"mutation score %": MUTATION_EPS}
    regressions = [label for label, base, cur in rows if cur < base - tolerances.get(label, EPS)]

    if markdown:
        _render_markdown(name, rows, regressions)
    else:
        _render_text(rows, regressions)

    if regressions:
        print(f"FAIL: {name} regressed on: {', '.join(regressions)}", file=log)
        return 1 if strict else 0
    print(f"PASS: {name} meets or exceeds baseline.", file=log)
    return 0


def cmd_survivors(name: str) -> int:
    """Print the mutants the current tests fail to catch (a missing-test to-do list)."""
    conn = _resolve_or_exit(name)
    print(f"Finding surviving mutants for '{name}' (this can take several minutes)...")
    survivors = find_survivors(conn)

    if not survivors:
        print(f"\nNone — every mutation in {conn.source_path} is caught by {conn.test_path}.")
        return 0

    print(f"\n{len(survivors)} surviving mutant(s) — behaviors no test currently checks:\n")
    current_path = None
    for s in survivors:
        if s.path != current_path:
            current_path = s.path
            print(f"  {s.path}")
        print(f"    line {s.line:>4}  {s.operator:<28}  {s.source}")
    print(
        "\nEach line above is a change that could be made to the source without any "
        "test failing.\nAdd an assertion covering it to close the gap."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_cap = sub.add_parser("capture", help="capture a baseline from the current tests")
    p_cap.add_argument("connector")
    p_cap.add_argument(
        "--no-mutation", action="store_true", help="coverage only (skip mutation testing)"
    )

    p_cmp = sub.add_parser("compare", help="compare current tests against the baseline")
    p_cmp.add_argument("connector")
    p_cmp.add_argument(
        "--no-mutation", action="store_true", help="coverage only (skip mutation testing)"
    )
    p_cmp.add_argument(
        "--strict", action="store_true", help="exit 1 on regression (the CI hard gate)"
    )
    p_cmp.add_argument(
        "--markdown",
        action="store_true",
        help="emit a markdown table on stdout (for $GITHUB_STEP_SUMMARY)",
    )

    p_surv = sub.add_parser(
        "survivors", help="list mutants the current tests do not catch (missing assertions)"
    )
    p_surv.add_argument("connector")

    args = parser.parse_args(argv)
    if args.command == "survivors":
        return cmd_survivors(args.connector)
    if args.command == "capture":
        return cmd_capture(args.connector, mutation=not args.no_mutation)
    if args.command == "compare":
        return cmd_compare(
            args.connector,
            mutation=not args.no_mutation,
            strict=args.strict,
            markdown=args.markdown,
        )
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
