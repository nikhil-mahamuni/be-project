import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../green_summarizer')))

from metrics.battery import BatteryManager
from metrics.network import NetworkStats
from metrics.profiler import Profiler

def test_profiler():
    battery = BatteryManager()
    network = NetworkStats()

    profiler = Profiler(battery, network)
    profiler.start()
    time.sleep(0.1)

    results = profiler.stop(compression_ratio=0.5, output_words=50)

    assert results['duration_seconds'] >= 0.1
    assert results['efficiency_score'] > 0
    assert 'energy_joules' in results
    assert 'carbon_gco2e' in results
