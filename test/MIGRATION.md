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

## Status

73 connector test groups: **3 done**, 70 remaining. 55 still use
`unittest.TestCase`, 11 are top-level `test_*.py` files, 27 directories lack
`__init__.py`.

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

### P0 · HYBRID (13) — review the boundary first

> **Finding (in progress):** most "hybrid" flags are *not* boundary bugs — they
> come from incidental `@mock.patch.dict(os.environ)` or a MagicMock used as a
> requests-mock response, while the real HTTP/SDK boundary is already mocked
> correctly. These need only style conversion. The genuine anti-pattern (mocking
> a Parsons-owned method and hiding a bug) has so far shown up **once**: `airmeet`.

- [x] `test_airmeet` — **done.** Was mocking `APIConnector.get_request`; moved to
  `requests_mock`, which exposed and fixed a real `TypeError` bug in
  `download_session_recordings`.
- [x] `test_auth0` — **done.** Moved to a package; pure `requests_mock`; replaced
  MagicMock-as-response misuse.
- [x] `test_sisense` — **done.** Boundary was already correct (`requests_mock`);
  converted to pytest + monkeypatch.
- [ ] `test_actblue` — TC, +init (style only — boundary looks correct)
- [ ] `test_bloomerang` — TC (style only)
- [ ] `test_census` — TC, +init (style only)
- [ ] `test_github` — (style only)
- [ ] `test_newmode` — TC (legitimate: V1 is SDK-pattern, V2 is `requests_mock`; style only)
- [ ] `test_slack` — TC (style only)
- [ ] `test_targetsmart` — TC (style only)
- [ ] `test_zoom` — TC, top→dir, data→data/ — **deferred (large):** ~28 tests, big
  inline payloads; boundary already correct. Dedicated PR.
- [ ] `test_google` — TC, +init, data→data/ — **deferred (large):** multi-file dir
  with legacy response modules. Dedicated PR.
- [ ] `test_ngpvan` — TC, data→data/ — **deferred (large):** multi-file dir with
  legacy response modules. Dedicated PR.

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
- [ ] `test_capitol_canary` — TC, top→dir
- [ ] `test_community` — TC, +init
- [ ] `test_controlshift` — TC, +init
- [ ] `test_copper` — TC, +init
- [ ] `test_crowdtangle` — TC, +init, data→data/
- [ ] `test_donorbox` — TC, +init
- [ ] `test_empower` — TC, +init
- [ ] `test_formstack` — TC
- [ ] `test_freshdesk` — TC, data→data/
- [ ] `test_gmail` — TC
- [ ] `test_hustle` — TC, +init, data→data/
- [ ] `test_mailchimp` — TC, data→data/
- [ ] `test_mobilecommons` — TC, +init, data→data/
- [ ] `test_mobilize` — TC
- [ ] `test_nation_builder` — TC, data→data/
- [ ] `test_p2a` — TC, top→dir
- [ ] `test_quickbase` — TC, +init
- [ ] `test_quickbooks` — TC, +init
- [ ] `test_redash` — TC, top→dir
- [ ] `test_rockthevote` — TC, +init
- [ ] `test_scytl` — TC, +init
- [ ] `test_shopify` — TC, top→dir
- [ ] `test_turbovote` — TC, +init

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
