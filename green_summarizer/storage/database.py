import sqlite3
import os
from typing import List, Optional
from storage.models import HistoryEntry

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at REAL NOT NULL,
                    input_type TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    input_word_count INTEGER NOT NULL,
                    output_word_count INTEGER NOT NULL,
                    compression_ratio REAL NOT NULL,
                    summary_text TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    data_used_bytes INTEGER NOT NULL,
                    battery_delta_percent REAL NOT NULL,
                    energy_joules REAL NOT NULL,
                    energy_wh REAL NOT NULL,
                    carbon_gco2e REAL NOT NULL,
                    efficiency_score REAL NOT NULL
                )
            ''')
            conn.commit()

    def add_history(self, entry: HistoryEntry) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO history (
                    created_at, input_type, source_name, model_name,
                    input_word_count, output_word_count, compression_ratio,
                    summary_text, duration_seconds, data_used_bytes,
                    battery_delta_percent, energy_joules, energy_wh,
                    carbon_gco2e, efficiency_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.created_at, entry.input_type, entry.source_name, entry.model_name,
                entry.input_word_count, entry.output_word_count, entry.compression_ratio,
                entry.summary_text, entry.duration_seconds, entry.data_used_bytes,
                entry.battery_delta_percent, entry.energy_joules, entry.energy_wh,
                entry.carbon_gco2e, entry.efficiency_score
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_history(self) -> List[HistoryEntry]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM history ORDER BY created_at DESC')
            rows = cursor.fetchall()

            return [HistoryEntry(
                id=row[0], created_at=row[1], input_type=row[2], source_name=row[3],
                model_name=row[4], input_word_count=row[5], output_word_count=row[6],
                compression_ratio=row[7], summary_text=row[8], duration_seconds=row[9],
                data_used_bytes=row[10], battery_delta_percent=row[11], energy_joules=row[12],
                energy_wh=row[13], carbon_gco2e=row[14], efficiency_score=row[15]
            ) for row in rows]

    def delete_history(self, history_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM history WHERE id = ?', (history_id,))
            conn.commit()

    def clear_all_history(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM history')
            conn.commit()
