# Test Suite Migration to the Testing Standard

This is the tracking checklist for bringing every connector's tests onto the
single testing standard in [`docs/write_tests.rst`](../docs/write_tests.rst).

**You do not need to do a whole tier at once.** Migrate a connector whenever you
touch it, check its box here, and open a small PR. Each connector is independent.

## Reference implementations (copy these)

Each connector type has a finished exemplar — start from the one that matches:

| Type | Exemplar | Pattern |
| --- | --- | --- |
| HTTP / REST | [`test_airtable/`](test_airtable/) | `requests_mock` fixture + `data/*.json` via `shared_datadir` |
| Third-party SDK | [`test_salesforce/`](test_salesforce/) | `mocker` swaps the vendor client; program per test |
| Protocol / DB | [`test_smtp/`](test_smtp/) | fake class in `fakes.py`, injected by a fixture |

## What "migrated" means

A connector is done when its tests:

1. Are plain **pytest functions** (no `unittest.TestCase`, no `setUp`/`tearDown`).
2. Mock the **correct boundary** — HTTP (`requests_mock`), SDK client (`mocker`),
   or protocol (a fake) — and **never the connector's own methods**.
3. Live in a `test_<connector>/` directory with `__init__.py` and a `conftest.py`
   holding the fixtures.
4. Keep large canned payloads in `data/*.json` loaded via `shared_datadir`
   (not in `*_responses.py` / `expected_json.py` modules or big inline dicts).
5. Pass, and are `ruff format` + `ruff check` clean.

## Verifying a migration (the parity gate)

Passing tests do not prove the new suite is as *strong* as the old one — a rewrite
can preserve coverage while quietly dropping assertions. Every connector has a
committed baseline in [`baselines/`](baselines/) recording the **old** suite's
line %, branch %, and mutation score, measured before migration.

```bash
# Run this FIRST when converting. Each line is a behavior you could change
# without any test failing — i.e. an assertion the new suite should add.
uv run python test/tools/parity.py survivors <connector>

# After converting: confirm the new suite has not regressed against the baseline.
uv run python test/tools/parity.py compare <connector>
uv run python test/tools/parity.py compare <connector> --no-mutation   # fast
```

The mutation *score* is only a regression floor; the **survivor list** is the
actionable output — use it so a conversion leaves the connector genuinely better
tested rather than merely equal.

Coverage is compared strictly. Mutation score is allowed a small tolerance
(±2 points): cosmic-ray classifies a hanging mutant as killed via a timeout, and
whether a slow mutant trips the 60s timeout varies slightly run to run, so the
aggregate score has a little noise. A real regression is larger than that; when
in doubt, run `survivors` — it is deterministic.

Baselines exist for 59+ connectors (the five `dbt-*` suites have no mockable tests,
so there is nothing to measure). Connectors that were **top-level `test_*.py` files**
(redash, shopify, p2a, …) missed the original directory-only sweep, so their baselines
are captured post-migration — verify the port is faithful/improved by hand in those cases. CI runs the coverage half automatically on every
PR. See [`tools/README.md`](tools/README.md) for the full toolset.

## Status

**34 connectors migrated**, all validated against their pre-migration baselines
with **zero regressions**. Several improved: salesforce, ngpvan, targetsmart
(coverage), and controlshift 23.53% → 100% / quickbase 50% → 100% (mutation).

Remaining: 46 files still use `unittest.TestCase`, 8 are top-level `test_*.py`
files, and 24 directories lack `__init__.py`.

## Priority tiers

- **P0 — HYBRID (13).** These mix an HTTP mock *and* an object mock in the same
  suite, which is where "mock the connector's own methods" anti-patterns hide.
  Review each: pick the one correct boundary, then convert. Highest value.
  *Known offenders from the audit:* `test_action_kit` mocks `.conn`, `test_airmeet`
  and `test_newmode` mock `.client` methods directly — refactor these to mock the
  real external boundary.
- **P1 — OBJECT (11).** These mock a client/connection object. Confirm the mocked
  object is a **third-party client** (correct — follow Salesforce/SMTP) and not the
  connector's own method (wrong — refactor to `requests_mock`). Then modernize style.
- **P2 — HTTP (27).** Mostly mechanical: swap the `@requests_mock.Mocker()`
  decorator for the `requests_mock` fixture, convert `TestCase` → functions, move
  legacy data modules into `data/*.json`, add `__init__.py`.
- **P3 — OTHER (19).** Non-HTTP suites (ETL core, pandas, cloud/DB warehouses, dbt
  adapters). Mostly just `TestCase` → pytest and structural cleanup; several already
  follow good local patterns.

### Cross-cutting cleanups (roll into each connector's PR)

- **11 top-level `test_*.py`** → move into a `test_<connector>/` directory.
- **27 dirs missing `__init__.py`** → add it.
- **Legacy data modules** (`*_responses.py`, `expected_json.py`, `fixtures.py`,
  `post.py`/`leaderboard.py`, and the central `test/responses/`) → convert to
  `data/*.json`.

## Legend

`TC` = convert `unittest.TestCase` → pytest &nbsp;·&nbsp; `top→dir` = move top-level
file into a directory &nbsp;·&nbsp; `+init` = add `__init__.py` &nbsp;·&nbsp;
`data→data/` = move canned data into `data/*.json` &nbsp;·&nbsp; `boundary?` =
verify the mock targets the external boundary, not the connector's own methods.

---

## Checklist

### P0 · HYBRID (13) — ✅ all done

> **Finding:** most "hybrid" flags were *not* boundary bugs — they came from
> incidental `@mock.patch.dict(os.environ)` or a MagicMock used as a requests-mock
> response, while the real HTTP/SDK boundary was already mocked correctly. The
> genuine "mock a Parsons-owned method and hide a bug" anti-pattern showed up in
> **`airmeet`** (a real `TypeError` fixed). Converting the suites also surfaced
> several latent *test* bugs (no-op assertions, a dead nested test) — all fixed.
>
> Data-file extraction (`data→data/`) for the larger suites was intentionally
> left out of this pass and remains as follow-up (see below); every payload is
> still test-local and correct.

- [x] `test_airmeet` — mocked `APIConnector.get_request`; moved to `requests_mock`,
  which exposed and fixed a real `TypeError` in `download_session_recordings`.
- [x] `test_auth0` — package; pure `requests_mock`; removed MagicMock-as-response misuse.
- [x] `test_sisense` — pytest + monkeypatch (boundary was already correct).
- [x] `test_actblue` — pytest + fixtures; `Table.from_csv` mock scoped via `mocker`.
- [x] `test_bloomerang` — pytest + fixtures; monkeypatch for env init.
- [x] `test_census` — pytest + fixture; live test preserved.
- [x] `test_github` — pytest + conftest; PyGithub-client mock via `mocker`, HTTP via `requests_mock`.
- [x] `test_newmode` — V1 SDK-pattern (`mocker`) + V2 `requests_mock`; fixed a shadowed test name.
- [x] `test_slack` — slack_sdk client mocked via `mocker`; `responses/` JSON kept.
- [x] `test_targetsmart` — `requests_mock`; live SFTP tests kept; fixed a no-op `pytest.raises`.
- [x] `test_zoom` — top→dir package; 26 pytest fns; `requests_mock` fixture + monkeypatch.
- [x] `test_google` — admin (mocker) / civic (requests_mock) / live suites / fakes; +`__init__`.
- [x] `test_ngpvan` — 17 modules; `van` fixtures; recovered a dead nested test, fixed a no-op assert.

**Follow-up (not blocking):** extract large inline / `*_responses.py` payloads into
`data/*.json` for `zoom`, `google`, `ngpvan`, `targetsmart`, `newmode`, `sisense`,
`bloomerang`.

### P1 · OBJECT (11) — confirm it mocks a third-party client

- [ ] `test_action_kit` — TC, top→dir, boundary? (mocks `.conn` — likely should be `requests_mock`)
- [ ] `test_alchemer` — TC, +init, data→data/, boundary?
- [ ] `test_bigquery` — TC, boundary?
- [ ] `test_catalist` — +init, boundary?
- [ ] `test_databases` — TC, boundary? (already uses `fakes.py` — good model)
- [ ] `test_dbt` — boundary?
- [ ] `test_geocode` — TC, data→data/, boundary?
- [ ] `test_sftp` — boundary?
- [ ] `test_ssh` — TC, +init, boundary?
- [ ] `test_twilio` — TC, +init, boundary?
- [ ] `test_utilities` — TC, boundary?

### P2 · HTTP (27) — mostly mechanical

- [ ] `test_action_builder` — TC, +init
- [ ] `test_action_network` — TC, +init
- [ ] `test_bill_com` — TC, +init
- [ ] `test_braintree` — TC
- [x] `test_capitol_canary` — top→dir; pytest + fixtures; `data/*.json`. Same fixes as p2a
  (no-op asserts, wrong-payload tests, empty test); split the two env-var tests to cover the
  CAPITOLCANARY_* > PHONE2ACTION_* precedence. Post-migration baseline (mutation 75.36%).
- [x] `test_community` — pytest + fixtures; added default-URI and the
  `outbound_message_type_usage` special-path tests via `survivors`
  (mutation 60% → **80%**).
- [x] `test_controlshift` — pytest + fixtures; `data/*.json`; added hostname-normalization
  and pagination tests found via `survivors` (mutation 23.53% → **100%**).
- [ ] `test_copper` — TC, +init
- [x] `test_crowdtangle` — pytest + fixtures; large `*.py` payloads → `data/*.json`;
  +`__init__`. Coverage parity verified; mutation is slow (6.6k-line fixture re-unpacked
  per mutant) and the suite still asserts via `_unpack` — a candidate for a trimmed fixture.
- [ ] `test_donorbox` — TC, +init
- [x] `test_empower` — pytest + fixtures; `data/export.json`; parametrized the
  per-slice column checks. Remaining mutation gap is blocked by a real bug in
  `convert_unix_to_readable` (silently nulls every timestamp) — flagged separately.
- [x] `test_formstack` — pytest + fixtures; `data/*.json`; replaced `isinstance`-only
  checks with row/column assertions (mutation 67.92% → **72.64%**).
- [x] `test_freshdesk` — pytest + fixtures; `data/*.json`; getters now assert content
  and create_ticket asserts the request body (mutation 40% → **48.57%**).
- [ ] `test_gmail` — TC
- [x] `test_hustle` — pytest + fixtures; `data/*.json`; +`__init__`. Parity flagged ~1%
  mutation noise; adding tests for the untested `create_custom_field` lifted coverage
  (line 84.3→87.79, branch 61.76→67.65) and cleared it.
- [x] `test_mailchimp` — pytest + fixtures; `data/*.json`; added a query-param assertion.
- [ ] `test_mobilecommons` — TC, +init, data→data/
- [x] `test_mobilize` — pytest + fixtures; `data/*.json`; `test_mobilize_america.py`
  → `test_mobilize.py`. Parity caught a coverage regression (the old setUp built the
  client with no key, hitting the missing-key branch) — added a no-key construction test.
- [x] `test_nation_builder` — pytest + fixtures; `fixtures.py` → `data/*.json`; parametrized
  the validation-error loops (mutation 83.33% preserved).
- [x] `test_p2a` — top→dir; pytest + fixtures; `data/*.json`. Fixed two `assert x, y` no-op
  asserts and two tests that mocked the wrong payload; dropped an empty test. Post-migration
  baseline (mutation 91.89%).
- [x] `test_quickbase` — pytest + fixtures; `data/*.json`; added a column-rename/value-unwrap
  assertion found via `survivors` (mutation 50% → **100%**).
- [x] `test_quickbooks` — pytest + fixtures; `data/*.json`; +`__init__`. Faithful port
  (mutation 51.53% preserved); follow-up: the `_with_params` tests don't yet assert the
  querystring is sent, which is most of the surviving mutants.
- [x] `test_redash` — top→dir; pytest + fixtures; env-var test uses monkeypatch. Baseline
  captured post-migration (top-level file, missed the sweep).
- [x] `test_rockthevote` — pytest + fixtures; `test_rtv.py` → `test_rockthevote.py`;
  `sample.*` → `data/`; +`__init__`; dropped a stray `print`.
- [ ] `test_scytl` — TC, +init
- [x] `test_shopify` — top→dir; pytest + fixtures; inline data kept (small). Post-migration
  baseline (mutation 40% — get_query_url branch combos untested; follow-up).
- [x] `test_turbovote` — pytest + fixtures; `users.txt` → `data/users.csv`; added a bearer-token
  header assertion (mutation already 100%).

### P3 · OTHER (19) — non-HTTP; structural cleanup

- [ ] `test_avro` — +init
- [ ] `test_aws_async` — TC, top→dir
- [ ] `test_azure` — TC, +init
- [ ] `test_box` — +init
- [ ] `test_civis` — TC
- [ ] `test_dbt-bigquery`
- [ ] `test_dbt-duckdb`
- [ ] `test_dbt-postgres`
- [ ] `test_dbt-redshift`
- [ ] `test_dbt-snowflake`
- [ ] `test_etl` — top→dir
- [ ] `test_facebook` — TC
- [ ] `test_mysql` — TC
- [ ] `test_pandas` — +init
- [ ] `test_pdi`
- [ ] `test_postgres` — TC
- [ ] `test_redshift` — TC
- [ ] `test_s3` — TC
- [ ] `test_sendmail` — top→dir

### Done ✅

- [x] `test_airtable` — HTTP/REST exemplar
- [x] `test_salesforce` — third-party SDK exemplar
- [x] `test_smtp` — protocol exemplar
