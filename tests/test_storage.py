import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../green_summarizer')))

from storage.database import Database
from storage.settings_store import SettingsStore
from storage.models import HistoryEntry

def test_database_operations(tmp_path):
    db_path = str(tmp_path / "test.db")
    db = Database(db_path)

    entry = HistoryEntry(
        id=None,
        created_at=time.time(),
        input_type='text',
        source_name='test',
        model_name='Frequency Rank',
        input_word_count=100,
        output_word_count=20,
        compression_ratio=0.2,
        summary_text='This is a summary.',
        duration_seconds=0.5,
        data_used_bytes=0,
        battery_delta_percent=0.01,
        energy_joules=1.5,
        energy_wh=0.0004,
        carbon_gco2e=0.0001,
        efficiency_score=95.0
    )

    entry_id = db.add_history(entry)
    assert entry_id > 0

    entries = db.get_all_history()
    assert len(entries) == 1
    assert entries[0].model_name == 'Frequency Rank'

    db.delete_history(entry_id)
    entries = db.get_all_history()
    assert len(entries) == 0

def test_settings_store(tmp_path):
    db_path = str(tmp_path / "settings.db")
    settings = SettingsStore(db_path)

    settings.set('test_key', 'test_val')
    val = settings.get('test_key')
    assert val == 'test_val'
