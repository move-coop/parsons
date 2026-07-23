# Test-suite migration tracker

Parsons is standardizing its connector tests onto a single convention (see
[docs/write_tests.rst](../docs/write_tests.rst)). This file is the **process guide
and the source of truth** for that incremental migration: how each connector moves
from its old tests to the new standard safely, and where every connector currently
stands.

Refactoring *tests* is uniquely risky: the tests are the thing changing, so "all
green" proves nothing about whether the new suite is as **strong** as the old one.
We guard against silent quality loss two ways: a **per-connector legacy bake**
(old and new tests run side by side for a while) and an objective **coverage +
mutation parity gate**.

## The per-connector lifecycle: expand → bake → contract

Migrate one connector at a time. Each moves through four states, tracked in the
table below.

### 0. Baseline — *before* changing anything

Capture the old suite's quality, scoped to the connector's source module, and
commit it. The old suite is deleted at the end, so the baseline must be frozen now:

```bash
uv run python test/tools/parity.py capture <connector>
```

This writes `test/baselines/<connector>.json` (line %, branch %, and mutation
score). Commit it. (Add `--no-mutation` for a fast coverage-only baseline while
iterating; capture the full baseline before you finish.)

### 1. Expand — add the new tests beside the old

- Write the new-style tests per [docs/write_tests.rst](../docs/write_tests.rst).
- **Keep the old tests**, renamed `test_<connector>_legacy.py`, and mark every
  test in that file `@pytest.mark.legacy`.
- Add an `__init__.py` to the connector's test dir if it lacks one, so the
  `_legacy` file and the new file don't collide under pytest's `prepend` import
  mode (they must not share a basename without a package).
- Both suites should now pass: `uv run pytest test/test_<connector>`.

### 2. Bake — run both for a while and watch for drift

Both suites run on every PR and on the weekly scheduled CI run. **Drift** is the
two suites disagreeing as the connector's source changes during this window — a
source edit that breaks exactly one suite exposes a gap in the other. Exit the
bake when all of these hold:

- `uv run python test/tools/parity.py compare <connector>` → **PASS** (coverage and
  mutation ≥ baseline), and
- no drift incident during the window (~2 weeks or one release cycle).

### 3. Contract — delete the old suite

- Delete `test_<connector>_legacy.py`.
- Tick the row below (Legacy removed).

## The parity gate

`test/tools/parity.py` measures two things, scoped to one connector's source:

- **coverage** — line % and branch % (is the code executed?)
- **mutation score** — % of injected faults the tests catch (do the tests actually
  *assert* behavior?). Coverage can be 100% while assertions are gutted; mutation
  score is what catches that.

```bash
uv run python test/tools/parity.py compare <connector>            # advisory
uv run python test/tools/parity.py compare <connector> --strict   # exit 1 on regression (CI gate)
```

Connector→source mapping lives in [test/tools/connector_map.py](tools/connector_map.py);
add an override there if a connector's source is not `parsons/<connector>/`.

## Status

Legend: ⬜ not started · 🟡 in progress · ✅ done · — n/a

`CI job` = where the connector's tests run today: the per-connector **extras job**
(`pytest test/test_<extra>`) or the combined **main job**. Extras-job connectors
get per-connector parity in CI for free; main-job connectors are validated by
changed-path scoping (see the workflow plan).

| Connector | CI job | Baseline | Migrated | Cov parity | Mut parity | Bake start | Legacy removed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| actblue | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| action_builder | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| action_network | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| airmeet | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| airtable | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| alchemer | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| auth0 | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| avro | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| azure | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| bigquery | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| bill_com | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| bloomerang | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| box | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| braintree | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| catalist | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| census | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| civis | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| community | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| controlshift | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| copper | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| crowdtangle | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| databases | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| dbt-bigquery | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| dbt-duckdb | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| dbt-postgres | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| dbt-redshift | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| dbt-snowflake | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| donorbox | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| empower | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| facebook | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| formstack | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| freshdesk | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| geocode | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| github | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| gmail | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| google | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| hustle | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| mailchimp | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| mobilecommons | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| mobilize | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| mysql | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| nation_builder | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| newmode | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| ngpvan | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| pandas | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| pdi | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| postgres | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| quickbase | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| quickbooks | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| redshift | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| rockthevote | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| s3 | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| salesforce | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| scytl | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| sftp | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| sisense | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| slack | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| smtp | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| ssh | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| targetsmart | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| turbovote | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| twilio | extras job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| utilities | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| zoom | main job | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

> Note: exemplar migrations for **airtable**, **google**, **ngpvan**, and **zoom**
> currently live on the `test-refactor` branch. When that branch and this tooling
> converge, capture their baselines from `main` (old suite) first, then mark their
> rows.
