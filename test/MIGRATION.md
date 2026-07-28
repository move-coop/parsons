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

## The parallel-change bake (keep the old suite for now)

Migrate one connector at a time using expand → bake → contract:

1. **Expand.** Write the new `test_<connector>.py`. Keep the old suite in the same
   directory, renamed `test_<connector>_legacy.py`, with `pytestmark =
   pytest.mark.legacy` at the top. Restore its old data modules too if you moved
   them. Both suites run and pass:

   ```bash
   git show HEAD:test/test_<connector>/test_<connector>.py > \
       test/test_<connector>/test_<connector>_legacy.py   # then add the pytestmark
   uv run pytest test/test_<connector>          # new + legacy, both green
   uv run pytest test/test_<connector> -m "not legacy"    # new only
   ```

2. **Bake.** Both suites run in CI. Because the two suites exercise the same
   source, a source change that breaks exactly one of them exposes a gap in the
   other — that is the drift signal the frozen baseline cannot give. The parity
   gate always measures the **new suite alone** (`parity.py` runs it with
   `-m "not legacy"`), so the legacy tests never mask a regression in the new one.

3. **Contract.** Once the new suite has baked (parity green, no drift), delete
   `test_<connector>_legacy.py` and tick "Legacy removed" in the checklist.

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

**45 connector directories migrated** (each has a `_legacy` sibling running the
old suite through the bake), all validated against their pre-migration baselines
with **zero regressions**. Several improved: salesforce, ngpvan, targetsmart,
copper (coverage), and controlshift 23.53% → 100% / quickbase 50% → 100% /
**ssh 0% → 100%** / **geocode 0% → 75.76%** / **sftp 21.46% → 54.94%** /
**alchemer 25% → 88.46%** / **catalist 69.55% → 86.59%** / **twilio 80.52% → 90.91%**
(mutation). `action_kit` had
its boundary anti-pattern fixed (mocked `.conn` → `requests_mock`), now exercising the
real request/response code.

Remaining work (measured from the tree, not this checklist — regenerate with the
snippet below): **18 non-legacy files still use `unittest.TestCase`**, **3** are
top-level `test_*.py` files, and **8** directories lack `__init__.py`.

> **Caveat — dir-level "done" can hide sub-files.** A connector is checked here
> when its primary suite is migrated, but a few directories still have unmigrated
> `TestCase` *sub-files* (e.g. `test_google/test_utilities.py`, `test_databases/`
> (3), `test_utilities/` (2)). Trust the tree, not the box.

### Next up

The two P2 heavyweights (`copper`, `action_network`) are done, along with four P1
boundary reviews: `ssh` (0% → 100% mutation), `action_kit` (the flagged `.conn`
anti-pattern, now `requests_mock`), `geocode` (mocked tests were all class-marked
`@pytest.mark.live` so nothing ran; 0% → 75.76% mutation), `sftp` (added a
`FakeSFTP` fake so the operations run in CI, not just live; 21.46% → 54.94% mutation),
`alchemer` (weak assertions — a no-op `assert`, single-row checks, untested
pagination; 25% → 88.46% mutation), and `catalist` (already pytest; added `+init` and
tests for the untested `action`/`await_completion`/error paths; 69.55% → 86.59%
mutation), and `twilio` (`TC` → pytest + `+init`; added `_table_convert` column-drop
and `exclude_null` coverage; 80.52% → 90.91% mutation). Next are the remaining
**P1 · OBJECT** reviews (`bigquery`, `databases`, `dbt`, `utilities`) and the **P3** tier.

Regenerate these numbers any time:

```bash
echo "migrated dirs:   $(find test -name '*_legacy.py' -exec dirname {} \; | sort -u | wc -l)"
echo "TestCase left:   $(grep -rl 'unittest.TestCase' test/ --include='*.py' | grep -v _legacy | wc -l)"
echo "dirs w/o __init__: $(for d in test/test_*/; do [ -f "$d/__init__.py" ] || echo x; done | wc -l)"
```

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

- [x] `test_action_kit` — **boundary bug confirmed & fixed**: `setUp` replaced
  `self.conn` (a real `requests.Session`) with a `MagicMock`, so the tests only
  checked which URL each method was handed and never ran `_base_get`/`_base_post`
  response handling. Refactored all 57 tests to `requests_mock` (top→dir, +`__init__`
  /conftest), which now asserts request bodies/params *and* the parsed return values
  and pagination against real responses — this immediately surfaced that
  `get_user_fields` returns `list(resp["fields"].keys())`, previously unexercised.
  No baseline existed (top-level file); captured one pre-migration and the new suite
  meets/exceeds it (line 88.12 → 88.45, branch 63.24 → 64.71). Legacy bake kept.
- [x] `test_alchemer` — **boundary correct** (mocks the third-party `surveygizmo`
  client), but assertions were hollow: a **no-op `assert survey_id, table["survey_id"]`**,
  `for i in range(0, 1)` loops that checked only the first row, and no pagination
  coverage. Merged the two `TestCase` sub-files into `test_alchemer.py` (pytest +
  `mocker` client, +`__init__`/conftest), moved inline payloads to `data/*.json`, and
  added tests for multi-page fetching, the column transforms (drop `links`, unpack
  `statistics`, add `survey_id` at index 1), and the explicit-page path. Mutation
  25% → **88.46%**, line 84.44 → **93.33**, branch 50 → **78.57**. Legacy bake kept.
- [ ] `test_bigquery` — TC, boundary?
- [x] `test_catalist` — **boundary confirmed** (OAuth2 HTTP via `requests_mock` +
  a mocked SFTP client); the suite was already pytest with a conftest, just missing
  `__init__.py`. Coverage was low (62%) because whole methods were untested. Added
  `+init` and tests for `action` (with options + single vs list file ids), the
  `upload` input-subfolder path, `validate_table`'s non-default-template skip, the
  `load_matches` failed-status branches (Error/Stopped/Exception → RuntimeError), and
  `await_completion`'s poll-until-finished loop. No rewrite → no legacy bake. Coverage
  line 62.04 → **94.16**, branch 35 → **85**, mutation 69.55 → **86.59**. (Noted two
  trivial source nits: a no-op `else` string in `load_matches` and a deprecated
  `logger.warn`.)
- [ ] `test_databases` — TC, boundary? (already uses `fakes.py` — good model)
- [ ] `test_dbt` — boundary?
- [x] `test_geocode` — **boundary was correct but the whole suite was dead**: the
  mocked tests correctly mock the third-party `censusgeocode` client, but the class
  was marked `@pytest.mark.live`, so all 4 tests were skipped in CI (0% mutation,
  34% line). Converted to pytest + `mocker` (patch the client at its import site),
  dropped the bogus `live` marker, moved `test_responses.py` payloads to `data/*.json`.
  Added the missing branch/log assertions (column validation, empty-result logging,
  coordinates found/not-found) and fixed `test_coordinates`, which mocked the wrong
  client method. Mutation 0% → **75.76%**, line 34 → **100**, branch 0 → **100**.
  Flagged a real source bug: `geocode_address` ignores its `return_type` arg. Legacy
  bake kept.
- [x] `test_sftp` — **boundary confirmed** (paramiko SFTP protocol; every method
  already accepts a `connection` for injection). The suite was already pytest, but
  almost every test was `@pytest.mark.live`, so CI covered ~30%. Added a `FakeSFTP`
  fake (in `fakes.py`; subclasses `paramiko.SFTPClient` so the `@connect` decorator's
  `isinstance` check accepts it) and a `test_sftp_mocked.py` with 19 CI tests covering
  list/make/remove, get/put, size, list_files/subdirectories (+patterns, empty-dir),
  get_table, and get_files. Also added the missing `data/` CSV the live fixtures
  reference. No rewrite → no legacy bake. Coverage line 29.61 → **62.57**, branch
  7.81 → **56.25**, mutation 21.46 → **54.94**. Follow-up: `walk_tree` and chunked
  `get_file` remain live-only.
- [x] `test_ssh` — **boundary was already correct** (patched the `sshtunnel` /
  `psycopg2` third-party libs, not the connector's own code); modernized to pytest +
  conftest fixture, +`__init__`. `survivors` showed the assertions were hollow (0/3
  killed): added checks that cleanup runs (`con.close`/`server.stop`), that the error
  path logs and re-raises, and a tunnel-construction-failure case. Mutation 0% →
  **100%**, line 89.29 → **100**, branch 50 → **75**. Legacy bake kept.
- [x] `test_twilio` — **boundary confirmed** (mocks the third-party `twilio.rest.Client`);
  `TestCase` → pytest functions, +`__init__`/conftest (patch the client at its import
  site). The old suite only checked call routing (mock returns iterate empty), so
  `_table_convert`'s uri-column drop and `get_account_usage`'s `exclude_null` path were
  untested; added a `FakeRecord` and tests covering both, plus parametrized the
  time_period/group_by routing. Line 94.55 → **100**, branch 83.33 → **100**, mutation
  80.52 → **90.91** (remaining survivors are equivalent `==`→`is` string-literal
  mutants). Legacy bake kept.
- [ ] `test_utilities` — TC, boundary?

### P2 · HTTP (27) — mostly mechanical

- [x] `test_action_builder` — pytest + fixtures; setUp fakes extracted to `data/*.json`;
  callbacks/helpers as module functions. Legacy bake (mutation 59.88%).
- [x] `test_action_network` — pytest + fixtures; the 3.6k-line `setUp` of inline
  `fake_*` payloads extracted to 57 `data/*.json` files (loaded via `shared_datadir`),
  the 91 `TestCase` methods ported 1:1 to functions, +`__init__`. Faithful port
  (coverage exactly 80.26 line / 47.66 branch preserved — baseline is coverage-only,
  no mutation). Legacy bake kept. Follow-up: branch coverage is low (47.66%) — the
  per-method optional-param branches (per_page cap, limit, filter combos) are a
  strengthening opportunity.
- [x] `test_bill_com` — pytest + fixtures; 180-line setUp extracted to `data/*.json`; the
  bc fixture mocks the Login.json session handshake. Legacy bake (mutation 81.29%).
- [x] `test_braintree` — pytest + fixtures; XML fixtures → `data/`; SDK's HTTP calls
  mocked via requests_mock. Legacy bake kept (mutation 74.61%).
- [x] `test_capitol_canary` — top→dir; pytest + fixtures; `data/*.json`. Same fixes as p2a
  (no-op asserts, wrong-payload tests, empty test); split the two env-var tests to cover the
  CAPITOLCANARY_* > PHONE2ACTION_* precedence. Post-migration baseline (mutation 75.36%).
- [x] `test_community` — pytest + fixtures; added default-URI and the
  `outbound_message_type_usage` special-path tests via `survivors`
  (mutation 60% → **80%**).
- [x] `test_controlshift` — pytest + fixtures; `data/*.json`; added hostname-normalization
  and pagination tests found via `survivors` (mutation 23.53% → **100%**).
- [x] `test_copper` — pytest + fixtures; response payloads → `data/*.json`; +`__init__`.
  Dropped an exact-duplicate opportunities test; `survivors` drove new assertions on
  request paging/filters/auth headers and the pagination math (page_number pinning,
  non-divisor page_size). Coverage 92.56 → **98.35** line / 83.33 → **92.86** branch,
  mutation 75.13 → **83.07**. Legacy bake kept.
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
- [x] `test_gmail` — pytest + fixtures; gmail fixture uses tmp_path; the 6 attachment
  tests collapse into one parametrized test; assets/ kept. Legacy bake (mutation 75.0%).
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
