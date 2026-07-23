#!/usr/bin/env python
"""Capture parity baselines for many connectors in one sweep (Phase B).

Iterates the connectors that have a ``test/test_<name>`` directory, resolves each
to its source module, and writes ``test/baselines/<name>.json``. Connectors whose
mapping does not resolve are skipped and reported (add an override to
``connector_map.py``). Failures during measurement are caught so one bad
connector does not abort the sweep.

Usage::

    # fast: coverage-only baselines for every connector
    python test/tools/capture_all.py --no-mutation

    # full (slow): coverage + mutation for every connector
    python test/tools/capture_all.py

    # limit to specific connectors
    python test/tools/capture_all.py --no-mutation airtable google ngpvan

Existing baselines are skipped unless ``--overwrite`` is given.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import connector_map
import parity
from connector_map import REPO_ROOT

BASELINE_DIR = REPO_ROOT / "test" / "baselines"


def all_connectors() -> list[str]:
    return sorted(p.name[len("test_") :] for p in (REPO_ROOT / "test").glob("test_*") if p.is_dir())


def capture_one(name: str, mutation: bool) -> dict:
    conn = connector_map.resolve(name)
    payload: dict = {
        "connector": name,
        "git_sha": parity.git_sha(),
        "source_path": conn.source_path,
        "cov_module": conn.cov_module,
        "test_path": conn.test_path,
        "coverage": asdict(parity.measure_coverage(conn)),
    }
    if mutation:
        payload["mutation"] = asdict(parity.measure_mutation(conn))
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    (BASELINE_DIR / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("connectors", nargs="*", help="limit to these (default: all)")
    parser.add_argument("--no-mutation", action="store_true", help="coverage only (fast)")
    parser.add_argument("--overwrite", action="store_true", help="recapture existing baselines")
    args = parser.parse_args(argv)

    names = args.connectors or all_connectors()
    mutation = not args.no_mutation

    captured, skipped, failed = [], [], []
    for name in names:
        conn = connector_map.resolve(name)
        problems = connector_map.validate(conn)
        if problems:
            skipped.append((name, problems[0]))
            print(f"SKIP  {name}: {problems[0]}")
            continue
        if not args.overwrite and (BASELINE_DIR / f"{name}.json").exists():
            skipped.append((name, "baseline exists (use --overwrite)"))
            print(f"SKIP  {name}: baseline exists")
            continue
        try:
            print(f"...   {name}", flush=True)
            payload = capture_one(name, mutation)
            cov = payload["coverage"]
            summary = f"line {cov['line_pct']}% branch {cov['branch_pct']}%"
            if "mutation" in payload:
                summary += f" mutation {payload['mutation']['score_pct']}%"
            captured.append(name)
            print(f"OK    {name}: {summary}")
        except parity.NoCoverageData as exc:
            skipped.append((name, str(exc)))
            print(f"SKIP  {name}: {exc}")
        except Exception as exc:  # report and continue the sweep
            failed.append((name, str(exc).splitlines()[0] if str(exc) else repr(exc)))
            print(f"FAIL  {name}: {exc}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    print("\n" + "=" * 60)
    print(f"captured: {len(captured)}  skipped: {len(skipped)}  failed: {len(failed)}")
    if failed:
        print("\nfailed:")
        for name, why in failed:
            print(f"  {name}: {why}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
