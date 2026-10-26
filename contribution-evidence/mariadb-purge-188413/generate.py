from pathlib import Path
from sqlalchemy.dialects.mysql import dialect
from homeassistant.components.recorder import queries
root=Path('/tmp/ha-purge-benchmark')
lines=['CREATE DATABASE purge_benchmark;', 'USE purge_benchmark;', 'CREATE TABLE state_attributes (attributes_id BIGINT PRIMARY KEY) ENGINE=InnoDB;', 'CREATE TABLE states (state_id BIGINT PRIMARY KEY, attributes_id BIGINT, last_updated_ts DOUBLE, INDEX ix_states_attributes_id(attributes_id), INDEX ix_states_last_updated_ts(last_updated_ts)) ENGINE=InnoDB;', 'INSERT INTO state_attributes SELECT seq FROM seq_1_to_2652;', 'INSERT INTO states SELECT seq, MOD(seq-1,2000)+1, seq FROM seq_1_to_2000000;', 'CREATE TABLE event_data (data_id BIGINT PRIMARY KEY) ENGINE=InnoDB;', 'CREATE TABLE events (event_id BIGINT PRIMARY KEY, data_id BIGINT, time_fired_ts DOUBLE, INDEX ix_events_data_id(data_id), INDEX ix_events_time_fired_ts(time_fired_ts)) ENGINE=InnoDB;', 'INSERT INTO event_data SELECT attributes_id FROM state_attributes;', 'INSERT INTO events SELECT state_id, attributes_id, last_updated_ts FROM states;', 'ANALYZE TABLE states, events;', 'CREATE TABLE measurements (kind VARCHAR(30), candidate_count INT, variant VARCHAR(20), repetition INT, seconds DOUBLE);']
for kind, funcs in [('attributes',(queries.attributes_ids_exist_in_states_with_fast_in_distinct,queries.attributes_ids_exist_in_states)),('events',(queries.data_ids_exist_in_events_with_fast_in_distinct,queries.data_ids_exist_in_events))]:
 for count in (999,2652):
  for rep in range(4):
   for idx in ([0,1] if rep%2==0 else [1,0]):
    variant=('distinct','limit_one')[idx]
    sql=str(funcs[idx](list(range(1,count+1))).compile(dialect=dialect(),compile_kwargs={'literal_binds':True}))
    output=root/f'{kind}_{count}_{variant}_{rep}.tsv'
    sql=sql.replace('FROM ',f"INTO OUTFILE '{output}' FROM ",1)
    lines+=['SET @started = SYSDATE(6);',sql+';',f"INSERT INTO measurements VALUES ('{kind}',{count},'{variant}',{rep},TIMESTAMPDIFF(MICROSECOND,@started,SYSDATE(6))/1000000);"]
lines+=[f"SELECT * INTO OUTFILE '{root}/measurements.tsv' FROM measurements;",f"SELECT VERSION(), @@in_predicate_conversion_threshold INTO OUTFILE '{root}/version.tsv';"]
(root/'benchmark.sql').write_text('\n'.join(s.replace('\n',' ') for s in lines)+'\n')
