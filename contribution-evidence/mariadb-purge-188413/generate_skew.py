from pathlib import Path

root = Path('/tmp/ha-purge-benchmark-skew')
root.mkdir(exist_ok=True)
sql = Path('/tmp/ha-purge-benchmark/benchmark.sql').read_text()
sql = sql[sql.index('CREATE TABLE measurements'):]
sql = sql.replace('/tmp/ha-purge-benchmark/', str(root) + '/')
sql = sql.replace('measurements', 'measurements_skew')
prefix = '''USE purge_benchmark;
INSERT INTO state_attributes SELECT seq+10000 FROM seq_1_to_100000;
INSERT INTO states SELECT seq+2000000, seq+10000, seq+2000000 FROM seq_1_to_100000;
INSERT INTO event_data SELECT seq+10000 FROM seq_1_to_100000;
INSERT INTO events SELECT seq+2000000, seq+10000, seq+2000000 FROM seq_1_to_100000;
ANALYZE TABLE states, events;
'''
(root / 'benchmark.sql').write_text(prefix + sql)
