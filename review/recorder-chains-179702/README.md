# Recorder pending state chains — review package

Related issue: https://github.com/home-assistant/core/issues/179702

Base: `08920ecb3ae1d96049f3ca03b7e14601c33aadb4`.
Code commit: `9f96dd9a90aa0883740b8bb7cc7c31b288e0395d`.

## Behavior

The writer keeps `old_state` ORM relationships between uncommitted states of
one entity. Very long chains make SQLAlchemy dependency ordering expensive.
The change tracks each pending chain and commits through the existing recorder
commit/retry/cache-update path at 250 states. After a commit, the next state
uses the committed predecessor ID. Commit and session reset clear chain counts.
Independent entities keep the normal commit interval.

This is a partial mitigation for the writer slowdown discussed in the issue.
It does not modify `max_backlog`, memory checks, queue admission, or address the
reported SIGSEGV. More transactions during floods is the tradeoff. No device,
upstream library release, schema migration, or user configuration is required.

## Actual recorder benchmark

Python 3.14.10, SQLAlchemy 2.1.8, SQLite, Home Assistant test fixtures.
Three repetitions per case, median wall time from `freezegun.api.real_perf_counter`.
Timing includes publishing state changes and draining/committing the recorder;
it excludes setup and subsequent DB validation. All recorded rows and predecessor
links are checked. A large chain limit (1,000,000) disables early commits for the
comparison while retaining the new counting code. This is a controlled mechanism
comparison, not a full original-code throughput benchmark. The fixture database
is in memory; the separate model benchmark uses an on-disk temporary SQLite DB.
One lint process ran during part of the benchmark; timings are illustrative,
not a CI threshold or a production performance guarantee.

| Entities | Total changes | Early commit disabled | Limit 250 |
| --- | ---: | ---: | ---: |
| 1 | 4,000 | 7.192 s | 1.662 s |
| 1 | 8,000 | 36.420 s | 3.322 s |
| 100 | 4,000 | 1.293 s | 1.230 s |

The 100-entity case never reaches 250 pending states for any entity; its small
timing difference is noise, not evidence of a speedup.

To reproduce, copy `test_recorder_chain_benchmark.py` to
`tests/components/recorder/test_chain_benchmark_tmp.py` on the code branch and run
`uv run --no-sync pytest -q tests/components/recorder/test_chain_benchmark_tmp.py`.
Remove the temporary test afterward. It appends measurements to
`/tmp/ha-chain-recorder-results.jsonl`; remove any old output before rerunning.

The standalone `model_benchmark.py` compares global batch sizes using real HA
models on disk. It supports the dependency-chain hypothesis but does not run
the recorder and should not be mistaken for the final per-entity algorithm.

## Regression evidence

On the untouched base production files, the new long-chain tests fail with
flushes of 501 and 1,002 states (limits 250 and 500 respectively).
With the fix, both pass and verify every stored state and predecessor ID.
A third regression verifies that 501 independent entities flush together.

## Review before submission

`PR_DESCRIPTION.md` preserves the upstream template. Its human-understanding
checkbox deliberately remains unchecked. The repository requires human review
and understanding before a pull request is submitted. This branch contains
review material only; the code branch contains only production changes/tests.

## Validation results

- Full recorder suite: **1,095 passed, 17 skipped**, 247 warnings, 119.11 s.
  Command: `uv run --no-sync pytest -q tests/components/recorder`.
- New tests against original production code: **2 expected failures**.
- Actual recorder benchmark: **18 passed** (three repeats of six cases).
- Targeted prek: Ruff check/format, codespell, branch check and Prettier passed.
  The mypy/pylint hooks could not create worker sockets in this environment.
  Equivalent sequential runs passed:
  `mypy --num-workers 0 --no-native-parser` on both production files;
  `pylint --jobs=1 --ignore-missing-annotations=y` on all three changed files.
- `git diff --check` passed.
- Required `script/setup` was attempted; PyPI returned HTTP 429 for pyflic.
  The editable core, pytest plugin, hassfest package, requirements_test.txt and
  pinned aiohasupervisor dependency were installed separately for validation.
- SQLite was exercised; no live MariaDB/PostgreSQL server or production
  1.5-million-event backlog was tested.
