"""Temporary actual-recorder benchmark; not part of the contribution."""
import json
from unittest.mock import patch
from freezegun.api import real_perf_counter
import pytest
from pytest_homeassistant.components.recorder.common import async_wait_recording_done
from homeassistant.components.recorder.db_schema import States, StatesMeta
from homeassistant.components.recorder.util import session_scope

@pytest.fixture
async def mock_recorder_before_hass(async_test_recorder):
    pass

@pytest.mark.parametrize('limit', [1000000, 250])
@pytest.mark.parametrize('entity_count,count', [(1,4000),(1,8000),(100,4000)])
@pytest.mark.parametrize('repeat', range(3))
async def test_chain_benchmark(hass, async_setup_recorder_instance, limit, entity_count, count, repeat):
    await async_setup_recorder_instance(hass, {'commit_interval':3600})
    with patch('homeassistant.components.recorder.core.MAX_PENDING_STATE_CHAIN_LENGTH',limit):
        start=real_perf_counter()
        for value in range(count):
            hass.states.async_set(f'sensor.benchmark_{value % entity_count}',str(value))
        await async_wait_recording_done(hass)
        elapsed=real_perf_counter()-start
    with session_scope(hass=hass,read_only=True) as session:
        rows=session.query(States).order_by(States.state_id).all()
        assert len(rows)==count
        previous={}
        for row in rows:
            assert row.old_state_id==previous.get(row.metadata_id)
            previous[row.metadata_id]=row.state_id
    with open('/tmp/ha-chain-recorder-results.jsonl','a') as result:
        result.write(json.dumps(dict(limit=limit,entities=entity_count,count=count,repeat=repeat,seconds=elapsed))+'\n')
