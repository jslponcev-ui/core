# MariaDB purge query benchmark — issue #188413

Measured on MariaDB 10.11.14 (Ubuntu build), InnoDB, 256 MiB buffer pool, default in_predicate_conversion_threshold=1000. Home Assistant source base: 331f18f0f1d2b7bd11bfd0850d88c6e34201fe5e.

The scripts compile the actual four Home Assistant SQLAlchemy query builders with the MySQL dialect. The synthetic schema includes the referenced columns and relevant indexes, not every Recorder column. The first dataset has two million states and two million events, each sharing 2,000 IDs (1,000 rows per ID). Parent tables contain 2,652 IDs, including 652 unreferenced IDs. The second dataset adds 100,000 single-use IDs and rows to each pair of tables, then updates optimizer statistics. Candidate IDs remain 1..999 or 1..2652.

One warmup per variant precedes three timed repetitions, with order alternating between variants. Timings use MariaDB SYSDATE(6) around each SELECT INTO OUTFILE. They include result writing, not Home Assistant service overhead. All 64 result sets match exactly the expected IDs. These are synthetic query timings, not full purge benchmarks or reproductions of the reporter's 43-million-row database.

Median seconds (warmups excluded):

| Distribution | Query | IDs | DISTINCT | LIMIT 1 |
| --- | --- | ---: | ---: | ---: |
| Uniform | Attributes | 999 | 0.005613 | 0.036693 |
| Uniform | Attributes | 2652 | 0.678745 | 0.074084 |
| Uniform | Events | 999 | 0.006652 | 0.029386 |
| Uniform | Events | 2652 | 0.552058 | 0.061632 |
| Skewed | Attributes | 999 | 0.004952 | 0.032539 |
| Skewed | Attributes | 2652 | 0.586776 | 0.064960 |
| Skewed | Events | 999 | 0.405587 | 0.067992 |
| Skewed | Events | 2652 | 0.623242 | 0.070740 |

The alternative is about 9x faster for large lists in these datasets. DISTINCT remains faster for small lists in three of four scenarios. The change favors avoiding large purge stalls; it does not claim every query becomes faster.

## Reproduction

Use an isolated MariaDB data directory; the scripts create a database named purge_benchmark. Run from a Home Assistant checkout with its test environment active:

```sh
mkdir -p /tmp/ha-purge-benchmark
PYTHONPATH=. python /path/to/generate.py
mariadb < /tmp/ha-purge-benchmark/benchmark.sql
python /path/to/generate_skew.py
mariadb < /tmp/ha-purge-benchmark-skew/benchmark.sql
```

The MariaDB server must be able to write to the output directories. Every output file must be absent before rerunning; use a fresh isolated directory/database for each complete repetition.

In this environment normal server startup was blocked by unavailable Unix sockets. The real MariaDB binary instead processed the SQL with `mariadbd --no-defaults --bootstrap --user=root --basedir=... --datadir=... --innodb-buffer-pool-size=256M < benchmark.sql`. This executes the storage engine and SQL queries without a network listener. Full Home Assistant tests against a live MariaDB server were not run locally.

## Correctness validation

- 145 tests pass: tests/components/recorder/test_util.py and tests/components/recorder/test_purge.py (SQLite).
- Nine version-selection cases fail before the fix and pass after it.
- Existing purge tests run both query strategies and verify retained states, attributes and events.
- Raw timed repetitions are preserved in uniform.tsv and skew.tsv.
- Ruff and single-process targeted Pylint pass. Full prek cannot complete parallel mypy/pylint workers due to socket restrictions, and hassfest lacks the unrelated infrared_protocols package. Full script/setup failed on dtlssocket compilation (missing autoconf); targeted test dependencies were installed successfully.
