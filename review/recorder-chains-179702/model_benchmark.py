import json, tempfile, time
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from homeassistant.components.recorder.db_schema import Base, States, StatesMeta

def run(count, batch, entities):
    with tempfile.TemporaryDirectory() as td:
        engine=create_engine('sqlite:///'+str(Path(td)/'test.db'))
        Base.metadata.create_all(engine)
        with Session(engine, expire_on_commit=False) as s:
            s.add_all(StatesMeta(entity_id=f'sensor.test_{i}', metadata_id=i+1) for i in range(entities)); s.commit()
            pending={}; committed={}
            start=time.perf_counter()
            for i in range(count):
                key=i%entities
                state=States(metadata_id=key+1,state=str(i),last_updated_ts=float(i))
                if key in pending: state.old_state=pending[key]
                elif key in committed: state.old_state_id=committed[key]
                s.add(state);pending[key]=state
                if batch and (i+1)%batch==0:
                    s.commit(); committed.update({k:v.state_id for k,v in pending.items()}); pending.clear()
            s.commit()
            elapsed=time.perf_counter()-start
            rows=list(s.execute(select(States.state_id,States.metadata_id,States.old_state_id).order_by(States.state_id)))
            previous={}
            assert len(rows)==count
            for row in rows:
                assert row.old_state_id==previous.get(row.metadata_id)
                previous[row.metadata_id]=row.state_id
        engine.dispose()
        return elapsed
for entities in (1,100):
    for count in (1000,4000,8000):
        for batch in (0,250,1000):
            print(json.dumps(dict(entities=entities,count=count,batch=batch,seconds=run(count,batch,entities))),flush=True)
