# test/tools — migration parity tooling

Tooling that supports the incremental test-suite migration (see
[test/MIGRATION.md](../MIGRATION.md)). It answers the question "all tests green"
cannot: **is the new test suite at least as strong as the old one?**

## `parity.py`

Measures two things for one connector, scoped to its source module:

- **coverage** — line % and branch % (does the suite execute the code?)
- **mutation score** — % of injected faults the suite catches (does it actually
  *assert* behavior?). Coverage can be 100% while assertions are gutted; mutation
  score is what catches a no-op assertion like `assert len(x), len(y)`.

```bash
# Capture a baseline from the current tests (do this on the OLD suite, before
# migrating), writing test/baselines/<connector>.json — commit that file.
uv run python test/tools/parity.py capture <connector>

# After migrating, confirm the new suite hasn't regressed.
uv run python test/tools/parity.py compare <connector>            # advisory (never fails)
uv run python test/tools/parity.py compare <connector> --strict   # exit 1 on regression (CI gate)

# Coverage only (fast; skips mutation testing) while iterating.
uv run python test/tools/parity.py capture <connector> --no-mutation
```

Requires the `mutation` dependency group (coverage tooling + cosmic-ray):

```bash
uv sync --no-default-groups --group mutation --extra <connector>
```

Notes:

- Coverage uses `coverage.py` (already configured with `branch = true`), scoped
  with `--cov=parsons.<module>`.
- Mutation uses [cosmic-ray](https://cosmic-ray.readthedocs.io/), which reads its
  own per-session config (no coupling to `pyproject.toml`). It mutates the source
  on disk, runs the connector's tests, and restores the file. Runs can take
  minutes; scope stays per-connector.
- Example: the pre-refactor `airtable` suite scores **97% line coverage but only
  ~56% mutation** — a concrete illustration of why coverage alone is not enough.

## `connector_map.py`

Maps a connector name to its source module (`--cov` target / mutation path) and
its test path. Most connectors resolve by the default rule `parsons/<name>` +
`test/test_<name>`; exceptions (e.g. `s3` → `parsons/aws/s3.py`, `facebook` →
`parsons/facebook_ads`) are listed in `_OVERRIDES`. Add an entry there if a
connector's source is not `parsons/<name>/`.

## `changed_connectors.py`

Emits the connectors a change set affects that also have a committed baseline —
used by CI to scope the slow mutation run to just what a PR touches.

```bash
python test/tools/changed_connectors.py --base origin/main   # affected by this PR
python test/tools/changed_connectors.py --all                # every baselined connector
```

## CI integration

`.github/workflows/python-checks.yml` wires these in, advisory-only during the
migration (results render to the GitHub **job summary**; the build is never
failed on a regression yet):

- **`pytest-extras`** — after each connector's tests, if a baseline exists, runs
  `parity.py compare <connector> --no-mutation` (fast, coverage only).
- **`parity-mutation`** — on PRs, runs mutation parity for the baselined
  connectors the PR changed (`changed_connectors.py --base`); on the weekly
  schedule and manual dispatch, sweeps all baselined connectors (`--all`),
  doubling as the drift monitor.

To turn the gate hard (Phase E), add `--strict` to the `compare` calls so a
regression fails the job.
