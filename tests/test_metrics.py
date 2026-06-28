import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../green_summarizer')))

from metrics.battery import BatteryManager
from metrics.network import NetworkStats
from metrics.energy import EnergyEstimator
from metrics.carbon import CarbonCalculator
from metrics.efficiency import EfficiencyCalculator
from metrics.profiler import Profiler

def test_energy_fallback():
    # Test fallback estimation when no real hardware current is available
    res = EnergyEstimator.calculate_energy(
        duration_seconds=2.0,
        voltage_mv=3850,
        current_ua=0.0,
        battery_delta_percent=0.0,
        is_mock_battery=True,
        model_wh_per_second=0.0001
    )
    assert res['estimated'] is True
    assert res['wh'] > 0
    assert res['joules'] > 0

def test_carbon_calculator():
    wh = 1000.0 # 1 kWh
    grid_factor = 708.2 # India default
    gco2e = CarbonCalculator.calculate_carbon_footprint(wh, grid_factor)
    assert abs(gco2e - 708.2) < 0.01

def test_efficiency_score():
    score_good = EfficiencyCalculator.calculate_score(
        duration_seconds=0.1,
        energy_joules=0.1,
        data_used_bytes=0,
        compression_ratio=0.5,
        output_words=50
    )
    assert 0 < score_good <= 100

    score_empty = EfficiencyCalculator.calculate_score(
        duration_seconds=0.1,
        energy_joules=0.1,
        data_used_bytes=0,
        compression_ratio=0.5,
        output_words=0
    )
    assert score_empty == 0.0

    score_bad = EfficiencyCalculator.calculate_score(
        duration_seconds=50.0, # Massive latency
        energy_joules=100.0, # Massive energy
        data_used_bytes=1000000, # Massive data
        compression_ratio=0.99, # Bad compression
        output_words=50
    )
    assert score_bad == 0.0 # Clamped

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
