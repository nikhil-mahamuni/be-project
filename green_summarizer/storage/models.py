from dataclasses import dataclass
from typing import Optional, List

@dataclass
class SummaryResult:
    summary_text: str
    model_name: str
    input_word_count: int
    output_word_count: int
    compression_ratio: float
    sentence_count: int
    keywords: List[str]
    processing_time_seconds: float

@dataclass
class HistoryEntry:
    id: Optional[int]
    created_at: float
    input_type: str
    source_name: str
    model_name: str
    input_word_count: int
    output_word_count: int
    compression_ratio: float
    summary_text: str
    duration_seconds: float
    data_used_bytes: int
    battery_delta_percent: float
    energy_joules: float
    energy_wh: float
    carbon_gco2e: float
    efficiency_score: float
